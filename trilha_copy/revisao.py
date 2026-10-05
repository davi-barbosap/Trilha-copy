"""Revisão de uma peça contra o contrato do cliente, o formato e os princípios de copy.

Gravidades:
    bloqueia   não vai ao ar assim: termo proibido, limite que a plataforma recusa, urgência sem lastro,
               prova que não existe ou não pode ser usada, afirmação sobre atributo pessoal no Meta
    atencao    vai custar caro ou ser reprovado: número sem lastro, texto cortado, autoelogio, intensidade
               acima da combinada, prova de outro perfil, fala que não cabe no vídeo
    sugestao   melhora a peça: ritmo, palavras do cliente, chamada sem prazo, adjetivo sem fato

Quem decide é o assessor. A revisão aponta, não reescreve.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from trilha_copy import texto as tx
from trilha_copy.contrato import Contrato
from trilha_copy.formatos import FORMATOS, GANCHO_SEGUNDOS, PALAVRAS_POR_SEGUNDO, TITULOS_GOOGLE_RECOMENDADOS
from trilha_copy.peca import Google, Meta, Peca, Roteiro
from trilha_copy.roteiros import modelos

Nivel = Literal["bloqueia", "atencao", "sugestao"]
NIVEIS: tuple[Nivel, ...] = ("bloqueia", "atencao", "sugestao")


@dataclass(frozen=True)
class Aviso:
    nivel: Nivel
    texto: str

    def __str__(self) -> str:
        return self.texto


SEGUNDA_PESSOA = re.compile(r"\b(voce|voces|vc|seu|sua|seus|suas|te|ti|contigo)\b")
PRIMEIRA_PLURAL = re.compile(r"\b(nosso|nossa|nossos|nossas|somos|conosco|a gente)\b")  # "nós" fica de fora: "nos" também é em+os

# Afirmar algo sobre quem lê (saúde, finanças, religião, orientação…) é reprovado pelo Meta.
ATRIBUTOS_PESSOAIS = (
    "acima do peso", "obes", "gordo", "gorda", "gordura", "diabet", "depress", "ansiedade", "ansios", "doenca",
    "cancer", "calvicie", "careca", "acne", "divida", "endividad", "nome sujo", "negativad", "falid",
    "desempregad", "pobre", "gay", "lesbica", "bissexual", "transgener", "evangelic", "catolic", "religiao",
    "deficien", "gravida", "infertil", "solteir", "divorciad",
)
FRASES_EGOISTAS = (
    "exija", "nao aceite imitacoes", "evite imitacoes", "cuidado com imitacoes", "somos lideres", "lider de mercado",
    "lideres de mercado", "a melhor empresa", "os melhores do mercado", "nossa missao", "temos orgulho", "orgulho em",
)
EXAGERO = (
    "incrivel", "inacreditavel", "revolucionari", "explosiv", "chocante", "insano", "absurd", "segredo", "nunca visto",
    "garantid", "imperdivel", "ultima chance", "corra", "urgente", "milagr", "magic", "definitiv", "extraordinari",
    "surreal", "sem esforco", "ficar rico", "enriquec", "bomba",
)
URGENCIA_NO_TEXTO = (
    "ultimas vagas", "ultimas unidades", "ultimos dias", "so hoje", "so ate", "acaba hoje", "termina hoje",
    "vagas limitadas", "por tempo limitado", "ultima chance", "corra", "encerra", "nao perca",
)
PROMESSA_DE_GANHO = re.compile(r"(ganh\w*|fatur\w*|lucr\w*|renda extra|ficar rico|enriquec\w*)")
ADJETIVO_VAGO = re.compile(r"\b(melhor(es)?|qualidade|excelencia|excelente|incrivel|lider|unico no mercado|top)\b")
QUANDO = re.compile(r"\b(hoje|agora|amanha|ate|esta semana|essa semana|neste mes|nesse mes|dia \d+|\d+ de \w+|ainda)\b")
LIMITE_EXAGERO = {1: 0, 2: 1, 3: 2, 4: 4, 5: 99}


def _juntar(pares: list[tuple[str, str]]) -> str:
    return "\n".join(t for _, t in pares)


def _numeros_do_contrato(c: Contrato, oferta_id: str) -> set[str]:
    partes: list[str] = [f"{p.numero} {p.texto}" for p in c.provas]
    partes += [f"{h.titulo} {h.resultado}" for h in c.historias]
    o = c.oferta(oferta_id)
    if o:
        partes += [o.promessa.texto, o.promessa.resultado, o.promessa.prazo, o.promessa.condicao] if o.promessa else []
        partes += [d.texto for d in o.diferenciais] + [b.texto for b in o.bastidores] + [o.raridade, o.custo_inacao]
        partes += [f"{p.titulo} {p.texto}" for p in o.como_funciona] + [str(v) for v in o.condicoes.values() if v]
        if o.urgencia:
            partes += [o.urgencia.texto, o.urgencia.data.strftime("%d/%m/%Y") if o.urgencia.data else ""]
        if o.escassez:
            partes.append(o.escassez.texto)
        partes += [ad.antes + " " + ad.depois for ad in o.antes_depois]
    partes += [cel.promessa for cel in c.grade]
    numeros: set[str] = set()
    for parte in partes:
        numeros |= tx.numeros_relevantes(parte or "")
    return numeros


def _compliance(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    proibidos = [(t, "termo proibido") for t in c.termos_proibidos()]
    ja = {tx.normalizar(t) for t in c.termos_proibidos()}
    proibidos += [(t, "promessa proibida") for t in c.compliance.promessas_proibidas if tx.normalizar(t) not in ja]
    for onde, t in textos:
        for termo, motivo in proibidos:
            if tx.contem_termo(t, termo):
                avisos.append(Aviso("bloqueia", f"{onde}: {motivo} — \"{termo}\""))
    meta = FORMATOS[p.formato].plataforma == "meta"
    for onde, t in textos:
        for frase in tx.frases(t):
            n = tx.normalizar(frase)
            if SEGUNDA_PESSOA.search(n) and any(a in n for a in ATRIBUTOS_PESSOAIS):
                avisos.append(Aviso("bloqueia" if meta else "atencao",
                                    f"{onde}: possível afirmação sobre atributo pessoal de quem lê (\"{frase[:60]}\"): "
                                    "o Meta reprova; fale do desejo ou da situação, não de quem a pessoa é"))
            if PROMESSA_DE_GANHO.search(n) and tx.numeros_relevantes(frase):
                avisos.append(Aviso("atencao", f"{onde}: promessa de ganho com número (\"{frase[:60]}\"): deixe claro que "
                                               "não é resultado típico (CDC e políticas do Meta)"))
    for nome in c.concorrentes:
        if len(nome) >= 4 and any(tx.contem_termo(t, nome) for _, t in textos):
            avisos.append(Aviso("atencao", f"cita o concorrente \"{nome}\": publicidade comparativa tem regras (CONAR); "
                                           "confirme com o cliente"))


def _lastro(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    oferta = c.oferta(p.oferta)
    tudo = tx.normalizar(_juntar(textos))
    if any(u in tudo for u in URGENCIA_NO_TEXTO) and not (oferta and (oferta.urgencia_valida() or oferta.escassez_valida())):
        avisos.append(Aviso("bloqueia", "a peça fala em prazo ou vagas acabando, mas a oferta não tem urgência nem escassez "
                                        "reais no briefing: isso é publicidade enganosa (CDC)"))
    conhecidos = _numeros_do_contrato(c, p.oferta)
    soltos = sorted(n for onde, t in textos for n in tx.numeros_relevantes(t) if n not in conhecidos)
    if soltos:
        avisos.append(Aviso("atencao", f"número(s) sem lastro no briefing ({', '.join(dict.fromkeys(soltos))}): "
                                       "todo número precisa vir de uma prova, da oferta ou da promessa aprovada"))
    for pid in p.provas:
        prova = c.prova(pid)
        if prova is None:
            avisos.append(Aviso("bloqueia", f"prova '{pid}' não está no contrato: ou não existe, ou não é utilizável "
                                            "(sem fonte ou sem autorização)"))
        elif prova.personas and p.persona and p.persona not in prova.personas:
            avisos.append(Aviso("atencao", f"prova '{pid}' ({prova.perfil or 'outro perfil'}) é de outra persona: "
                                           "prova parecida com quem lê convence mais"))


def _hopkins(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    tudo = tx.normalizar(_juntar(textos))
    nos, voce = len(PRIMEIRA_PLURAL.findall(tudo)), len(SEGUNDA_PESSOA.findall(tudo))
    if nos >= 2 and nos > voce:
        avisos.append(Aviso("atencao", f"fala mais de si ({nos}× nós/nosso) do que de quem lê ({voce}× você/seu): "
                                       "quem lê quer saber o que ganha"))
    egoistas = [f for f in FRASES_EGOISTAS if f in tudo]
    if egoistas:
        avisos.append(Aviso("atencao", f"autoelogio ou pedido egoísta (\"{egoistas[0]}\"): um bom vendedor não diria isso "
                                       "com o cliente na frente dele"))
    for onde, t in textos:
        if ADJETIVO_VAGO.search(tx.normalizar(t)) and not re.search(r"\d", t):
            avisos.append(Aviso("sugestao", f"{onde}: adjetivo sem fato (\"{t[:60]}\"): troque por número, nome ou detalhe"))
    exagero = sum(1 for e in EXAGERO if e in tudo) + _juntar(textos).count("!")
    exagero += sum(1 for w in tx.palavras(_juntar(textos)) if len(w) >= 4 and w.isupper() and not w.isdigit())
    intensidade = p.intensidade or c.voz.intensidade
    if intensidade and exagero > LIMITE_EXAGERO[intensidade]:
        avisos.append(Aviso("atencao", f"intensidade acima da combinada: {exagero} marca(s) de exagero (palavras de euforia, "
                                       f"exclamações, CAIXA ALTA) para intensidade {intensidade}"))


def _leitura(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    corrido = _juntar([(o, t) for o, t in textos if "textos_principais" in o or ".fala" in o or "descricoes" in o])
    nota = tx.legibilidade(corrido)
    if nota is not None and nota < 50:
        avisos.append(Aviso("atencao", f"leitura difícil (índice {nota:.0f}; abaixo de 50 é difícil): frases mais curtas, "
                                       "palavras mais simples"))
    ritmo = tx.variacao_ritmo(corrido)
    if ritmo is not None and ritmo < 0.25:
        avisos.append(Aviso("sugestao", "frases todas do mesmo tamanho: misture curtas, médias e longas"))
    persona = c.persona(p.persona)
    if persona and persona.frases:
        do_cliente = set().union(*(tx.palavras_de_conteudo(f.texto) for f in persona.frases))
        if not (do_cliente & tx.palavras_de_conteudo(_juntar(textos))):
            avisos.append(Aviso("sugestao", "não usa nenhuma palavra das frases literais da persona: devolva ao leitor "
                                            "as palavras dele"))


def _formato(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    conteudo = p.conteudo()
    for campo in FORMATOS[p.formato].campos:
        itens = getattr(conteudo, campo.nome)
        if p.estado not in ("fundacao", "rascunho"):
            if len(itens) < campo.minimo:
                avisos.append(Aviso("bloqueia", f"{campo.nome}: {len(itens)} item(ns); o mínimo é {campo.minimo}"))
        if len(itens) > campo.maximo:
            avisos.append(Aviso("bloqueia", f"{campo.nome}: {len(itens)} itens; a plataforma aceita até {campo.maximo}"))
        for i, t in enumerate(itens):
            if campo.rigido and len(t) > campo.rigido:
                avisos.append(Aviso("bloqueia", f"{campo.nome}[{i}] com {len(t)} caracteres; o limite é {campo.rigido}"))
            elif campo.recomendado and campo.so_gancho:
                gancho = (tx.frases(t) or [t])[0]
                if len(gancho) > campo.recomendado:
                    avisos.append(Aviso("atencao", f"{campo.nome}[{i}]: a primeira frase tem {len(gancho)} caracteres; depois "
                                                   f"de {campo.recomendado} o texto é cortado no feed e o gancho some"))
            elif campo.recomendado and len(t) > campo.recomendado:
                avisos.append(Aviso("atencao", f"{campo.nome}[{i}] com {len(t)} caracteres: depois de {campo.recomendado} "
                                               "o texto é cortado na tela"))
    if isinstance(conteudo, Meta):
        if p.estado not in ("fundacao", "rascunho") and not conteudo.cta_botao:
            avisos.append(Aviso("atencao", "meta.cta_botao vazio: escolha o botão que leva à micro-ação"))
    if isinstance(conteudo, Google):
        normalizados = [tx.normalizar(t) for t in conteudo.titulos]
        if len(set(normalizados)) != len(normalizados):
            avisos.append(Aviso("atencao", "google.titulos repetidos: o Google combina títulos e repetição desperdiça espaço"))
        if p.estado not in ("fundacao", "rascunho") and len(conteudo.titulos) < TITULOS_GOOGLE_RECOMENDADOS:
            avisos.append(Aviso("sugestao", f"google.titulos: {len(conteudo.titulos)}; com {TITULOS_GOOGLE_RECOMENDADOS} ou mais "
                                            "o Google tem o que combinar"))
        if conteudo.palavras_chave and not any(
                tx.contem_termo(t, k) for t in conteudo.titulos for k in conteudo.palavras_chave):
            avisos.append(Aviso("sugestao", "nenhum título repete uma palavra-chave do grupo: quem busca quer ver o que buscou"))
    if isinstance(conteudo, Roteiro):
        _roteiro(p, conteudo, avisos)
    if p.estado not in ("fundacao", "rascunho"):
        chamada = conteudo.cta if isinstance(conteudo, Roteiro) else " ".join(
            (conteudo.textos_principais[-1:] if isinstance(conteudo, Meta) else conteudo.descricoes[-1:]))
        if chamada and not QUANDO.search(tx.normalizar(chamada)):
            avisos.append(Aviso("sugestao", "chamada sem 'quando' (hoje, até tal dia, esta semana): diga quem, o quê, até "
                                            "quando e como"))


def _roteiro(p: Peca, r: Roteiro, avisos: list[Aviso]) -> None:
    if not r.cenas:
        return
    intervalos = [cena.intervalo() for cena in r.cenas]
    if any(i is None for i in intervalos):
        avisos.append(Aviso("atencao", "roteiro: use o tempo das cenas no formato '0-3', '3-12' (segundos)"))
        return
    if intervalos[0][1] > GANCHO_SEGUNDOS:
        avisos.append(Aviso("atencao", f"roteiro: a primeira cena vai até {intervalos[0][1]:g}s; o gancho precisa resolver "
                                       f"nos primeiros {GANCHO_SEGUNDOS}s"))
    fim = intervalos[-1][1]
    if r.duracao_s and abs(fim - r.duracao_s) > 1:
        avisos.append(Aviso("atencao", f"roteiro: as cenas somam {fim:g}s, mas a duração diz {r.duracao_s}s"))
    for cena, (ini, fim_cena) in zip(r.cenas, intervalos):
        cabe = (fim_cena - ini) * PALAVRAS_POR_SEGUNDO
        n = len(tx.palavras(cena.fala))
        if n > cabe + 2:
            avisos.append(Aviso("atencao", f"roteiro: a fala da cena {cena.tempo} tem {n} palavras; cabem cerca de {cabe:.0f}"))
    if r.modelo:
        modelo = modelos()[r.modelo]
        for problema in modelo.conferir([cena.parte for cena in r.cenas]):
            avisos.append(Aviso("atencao", f"roteiro ({modelo.nome}): {problema}"))
    elif p.estado not in ("fundacao", "rascunho"):
        avisos.append(Aviso("sugestao", "roteiro sem modelo de corpo: escolha um (python -m trilha_copy roteiros) para a "
                                        "revisão conferir se cada parte está lá e na ordem"))
    if p.estado not in ("fundacao", "rascunho"):
        if not r.cta:
            avisos.append(Aviso("atencao", "roteiro sem chamada (cta): diga o que fazer depois de assistir"))
        if not any(cena.texto_tela for cena in r.cenas):
            avisos.append(Aviso("sugestao", "roteiro sem texto na tela: muita gente assiste sem som"))


def _integridade(p: Peca, c: Contrato, textos, avisos: list[Aviso]) -> None:
    if p.estado == "aprovado" and not p.aprovacao_valida():
        avisos.append(Aviso("bloqueia", "o texto mudou depois da aprovação: aprove de novo antes de exportar"))
    celula = c.celula(p.codigo)
    if celula is None:
        avisos.append(Aviso("bloqueia", f"célula {p.codigo} não existe na grade do briefing"))
    else:
        if p.persona and celula.persona and p.persona != celula.persona:
            avisos.append(Aviso("atencao", f"persona da peça ({p.persona}) diferente da célula ({celula.persona})"))
        if p.oferta and celula.oferta and p.oferta != celula.oferta:
            avisos.append(Aviso("atencao", f"oferta da peça ({p.oferta}) diferente da célula ({celula.oferta})"))
    if p.hipotese and p.hipotese not in {h.id for h in c.hipoteses}:
        avisos.append(Aviso("atencao", f"hipótese '{p.hipotese}' não existe no briefing"))


REGRAS = [_compliance, _lastro, _hopkins, _leitura, _formato, _integridade]


def revisar(p: Peca, c: Contrato) -> list[Aviso]:
    textos = p.textos()
    avisos: list[Aviso] = []
    for regra in REGRAS:
        regra(p, c, textos, avisos)
    vistos, unicos = set(), []
    for a in avisos:
        if a.texto not in vistos:
            vistos.add(a.texto)
            unicos.append(a)
    return sorted(unicos, key=lambda a: NIVEIS.index(a.nivel))


def bloqueantes(p: Peca, c: Contrato) -> list[Aviso]:
    return [a for a in revisar(p, c) if a.nivel == "bloqueia"]
