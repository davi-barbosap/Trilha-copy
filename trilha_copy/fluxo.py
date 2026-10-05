"""Os estados da peça e o que cada passagem exige.

    fundação → rascunho   para quem, o que a peça e o sistema precisam provocar, a ideia grande, um pacote sem buraco
    rascunho → refinado   volume (escreva muitos títulos e ganchos, descarte a maioria), emoção, ângulo, gancho,
                          conteúdo do formato no mínimo da plataforma; roteiro com modelo de corpo
    refinado → final      subtexto anotado, prova escolhida, briefing do criativo (Meta), nada que bloqueie na revisão
    final → aprovado      só pelo comando aprovar: sem bloqueio, teste do vendedor e um dia depois do final
"""

from __future__ import annotations

from datetime import date

from trilha_copy.contrato import Contrato
from trilha_copy.formatos import FORMATOS
from trilha_copy.ganchos import GANCHOS
from trilha_copy.pacote import montar
from trilha_copy.peca import ESTADOS, Aprovacao, Estado, Meta, Peca, Roteiro
from trilha_copy.revisao import bloqueantes

MINIMO_RASCUNHOS = 10


def proximo(estado: Estado) -> Estado | None:
    i = ESTADOS.index(estado)
    return ESTADOS[i + 1] if i + 1 < len(ESTADOS) else None


def pendencias(p: Peca, c: Contrato) -> list[str]:
    """O que falta para a peça sair do estado atual."""
    falta: list[str] = []
    if p.estado == "fundacao":
        if not p.persona:
            falta.append("persona")
        elif c.persona(p.persona) is None:
            falta.append(f"persona '{p.persona}' não existe no briefing")
        for campo, nome in (("micro_acao", "micro-ação (o que esta peça precisa provocar)"),
                            ("macro_acao", "macro-ação (o que o sistema inteiro precisa)"),
                            ("ideia", "a ideia grande em uma frase")):
            if not getattr(p, campo):
                falta.append(nome)
        if c.celula(p.codigo):
            criticas = montar(c, p.codigo).tem_lacuna_critica()
            falta += [f"briefing: {x}" for x in criticas]
    elif p.estado == "rascunho":
        if len(p.rascunhos) < MINIMO_RASCUNHOS:
            falta.append(f"{MINIMO_RASCUNHOS} rascunhos de título ou gancho (tem {len(p.rascunhos)}): "
                         "escreva muitos, descarte a maioria")
        if p.emocao is None:
            falta.append("emoção principal (novo, fácil, seguro ou grande)")
        if p.angulo is None:
            falta.append("ângulo (positivo ou negativo)")
        if not p.gancho_tipo:
            falta.append("tipo de gancho")
        elif p.gancho_tipo not in GANCHOS:
            falta.append(f"tipo de gancho '{p.gancho_tipo}' fora do catálogo (veja: python -m trilha_copy ganchos)")
        conteudo = p.conteudo()
        for campo in FORMATOS[p.formato].campos:
            if len(getattr(conteudo, campo.nome)) < campo.minimo:
                falta.append(f"{campo.nome}: ao menos {campo.minimo}")
        if isinstance(conteudo, Roteiro) and not conteudo.cenas:
            falta.append("cenas do roteiro")
        if isinstance(conteudo, Roteiro) and not conteudo.modelo:
            falta.append("modelo de corpo do roteiro (python -m trilha_copy roteiros): diz o que cada cena precisa fazer")
    elif p.estado == "refinado":
        if len(p.subtexto) < 3:
            falta.append("subtexto: anote ao menos 3 trechos com o que cada um deve fazer sentir ou pensar")
        if not p.provas:
            falta.append("prova usada na peça (ids do contrato)")
        if isinstance(p.conteudo(), Meta) and not (p.meta.arte and p.meta.arte.mostrar):
            falta.append("briefing do criativo (meta.arte.mostrar): o que a arte precisa mostrar, para a equipe de criação")
        falta += [f"revisão: {a.texto}" for a in bloqueantes(p, c)]
    elif p.estado == "final":
        falta.append("só o comando aprovar leva a peça a aprovado")
    return falta


def avancar(p: Peca, c: Contrato) -> tuple[Estado | None, list[str]]:
    novo = proximo(p.estado)
    if novo is None:
        return None, ["a peça já está aprovada"]
    if novo == "aprovado":
        return None, ["use o comando aprovar"]
    falta = pendencias(p, c)
    return (None, falta) if falta else (novo, [])


def preparar_aprovacao(p: Peca, c: Contrato, por: str, teste_do_vendedor: bool, mesmo_dia: bool = False,
                       hoje: date | None = None) -> tuple[Aprovacao | None, list[str]]:
    hoje = hoje or date.today()
    problemas: list[str] = []
    if p.estado != "final":
        problemas.append(f"a peça está em '{p.estado}'; só peça final pode ser aprovada")
    problemas += [f"revisão: {a.texto}" for a in bloqueantes(p, c)]
    if not teste_do_vendedor:
        problemas.append("confirme o teste do vendedor (--teste-do-vendedor): um bom vendedor diria isso com o cliente "
                         "na frente dele?")
    if p.data_do_estado("final") == hoje and not mesmo_dia:
        problemas.append("a peça virou final hoje: durma sobre ela e aprove amanhã (ou use --mesmo-dia)")
    if problemas:
        return None, problemas
    return Aprovacao(por=por, data=hoje, teste_do_vendedor=True, assinatura=p.assinatura_conteudo()), []
