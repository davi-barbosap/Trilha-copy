"""O pacote da célula: tudo o que você precisa saber antes de escrever, organizado nos 6 Ps.

Pessoas · Posicionamento · Promessa · Prova · Prioridade · Processo. Com os seis preenchidos, a peça
"quase se escreve sozinha"; o P vazio aparece como lacuna, e é melhor voltar ao briefing do que inventar.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from trilha_copy.contrato import Celula, Contrato, Oferta, Persona
from trilha_copy.formatos import FORMATOS

TIPO_CRENCA = {"metodo": "sobre o método", "interna": "sobre si", "externa": "sobre o ambiente"}


@dataclass
class Pacote:
    codigo: str
    celula: Celula
    persona: Persona | None
    oferta: Oferta | None
    secoes: dict[str, list[str]] = field(default_factory=dict)
    lacunas: dict[str, list[str]] = field(default_factory=dict)

    def tem_lacuna_critica(self) -> list[str]:
        """O mínimo para começar a escrever: quem, o que promete, uma prova."""
        criticas = []
        if self.persona is None or not self.persona.dores:
            criticas.append("persona com dores")
        if not self.secoes.get("Promessa"):
            criticas.append("promessa")
        if not self.secoes.get("Prova"):
            criticas.append("ao menos uma prova utilizável")
        return criticas


def _ordenar(itens):
    """Mais mencionado primeiro: a copy mira a dor mais forte entre as mais comuns."""
    return sorted(itens, key=lambda i: -(getattr(i, "mencoes", None) or 0))


def _itens(itens) -> list[str]:
    return [f"{i.texto}" + (f" ({i.mencoes}×)" if getattr(i, "mencoes", None) else "") for i in _ordenar(itens)]


def montar(c: Contrato, codigo: str) -> Pacote:
    celula = c.celula(codigo)
    if celula is None:
        raise ValueError(f"célula {codigo} não existe na grade do briefing")
    persona = c.persona(celula.persona) if celula.persona else None
    oferta = c.oferta(celula.oferta) if celula.oferta else None
    pk = Pacote(codigo, celula, persona, oferta)
    s, lac = pk.secoes, pk.lacunas

    # Pessoas
    pessoas: list[str] = []
    if persona:
        pessoas.append(f"**{persona.nome}**: {persona.quem_e}")
        pessoas.append(f"Consciência: {celula.nivel_consciencia or persona.nivel_consciencia or '—'} · "
                       f"Sofisticação: {persona.sofisticacao or '—'}")
        pessoas += [f"Dor: {t}" for t in _itens(persona.dores)]
        pessoas += [f"Desejo: {t}" for t in _itens(persona.desejos)]
        pessoas += [f"Medo: {t}" for t in _itens(persona.medos)]
        pessoas += [f"Palavras dele ({f.origem}): \"{f.texto}\"" for f in persona.frases]
        pessoas += [f"Crença {TIPO_CRENCA[cr.tipo]}: {cr.texto}" + (f" → derrubar com: {cr.quebra}" if cr.quebra else "")
                    for cr in _ordenar(persona.crencas)]
        pessoas += [f"Objeção: {t}" for t in _itens(persona.objecoes)]
        if persona.gatilho_compra:
            pessoas.append(f"Gatilho de compra: {persona.gatilho_compra}")
    pessoas += [f"Não é para: {n.perfil}" + (f" (filtro: {n.como_filtrar})" if n.como_filtrar else "") for n in c.nao_atender]
    s["Pessoas"] = pessoas
    lac["Pessoas"] = [] if persona else ["a célula não tem persona"]
    if persona:
        lac["Pessoas"] += [nome for nome, v in (("frases literais", persona.frases), ("medos", persona.medos),
                                                ("crenças", persona.crencas)) if not v]
        if persona.sofisticacao is None:
            lac["Pessoas"].append("sofisticação")

    # Posicionamento
    pos = c.posicionamento
    posicao = [f"Para {pos.get('para_quem')}: {pos.get('categoria', '')} que {pos.get('diferenca', '')}"] if pos.get("para_quem") else []
    if c.unicidade:
        posicao.append(f"Só este cliente tem: {c.unicidade}")
    if oferta:
        if oferta.raridade:
            posicao.append(f"Raridade: {oferta.raridade}")
        posicao += [f"Bastidores: {b.texto}" for b in oferta.bastidores]
        for d in oferta.diferenciais:
            posicao.append(f"Diferencial: {d.texto}" + (f" → e daí? {' → '.join(d.e_dai)}" if d.e_dai else " (sem a escada do \"e daí?\")"))
    s["Posicionamento"] = posicao
    lac["Posicionamento"] = [] if (oferta and oferta.bastidores) else ["bastidores"]

    # Promessa
    promessa = []
    if celula.promessa:
        promessa.append(f"Desta célula: {celula.promessa}")
    if oferta and oferta.promessa:
        pr = oferta.promessa
        promessa.append(f"Da oferta: {pr.texto}" + (f" (resultado: {pr.resultado}; prazo: {pr.prazo}; para: {pr.condicao})"
                                                    if pr.resultado else ""))
    if oferta:
        promessa += [f"{ad.dimensao}: {ad.antes} → {ad.depois}" for ad in oferta.antes_depois]
        if celula.argumento:
            promessa.append(f"Argumento da célula: {celula.argumento}")
    s["Promessa"] = promessa
    lac["Promessa"] = [] if promessa else ["promessa"]

    # Prova
    provas = c.provas_para(persona.id) if persona else list(c.provas)
    s["Prova"] = [f"[{p.id or 'sem id'}] {p.rotulo()}" + (f" — perfil: {p.perfil}" if p.perfil else "") for p in provas]
    s["Prova"] += [f"História: {h.titulo} ({h.antes} → {h.resultado})" for h in c.historias
                   if not persona or not h.personas or persona.id in h.personas]
    lac["Prova"] = [] if provas else ["nenhuma prova utilizável"]
    if persona and not any(persona.id in p.personas for p in c.provas):
        lac["Prova"].append("nenhum depoimento de alguém parecido com esta persona")

    # Prioridade
    prioridade = []
    if oferta:
        if oferta.urgencia_valida():
            u = oferta.urgencia
            prioridade.append(f"Urgência real: {u.texto}" + (f" (motivo: {u.motivo})" if u.motivo else ""))
        if oferta.escassez_valida():
            prioridade.append(f"Escassez real: {oferta.escassez.texto}")
        if oferta.custo_inacao:
            prioridade.append(f"Custo de não agir: {oferta.custo_inacao}")
        if oferta.inversao_risco:
            prioridade.append(f"Risco que a pessoa não corre: {oferta.inversao_risco}")
    s["Prioridade"] = prioridade
    lac["Prioridade"] = [] if prioridade else ["urgência real, escassez real ou custo de não agir"]

    # Processo
    processo = []
    if oferta:
        b = oferta.big_idea
        if b.crenca_comum:
            processo.append(f"Todos acham: {b.crenca_comum}")
        if b.por_que_falha:
            processo.append(f"Está errado porque: {b.por_que_falha}")
        if b.mecanismo_unico:
            processo.append(f"O certo é: {b.mecanismo_unico}")
        processo += [f"Alternativa: {a.alternativa} — não resolve porque {a.por_que_nao}" for a in oferta.alternativas]
        processo += [f"Passo: {p.titulo}" + (f" — {p.texto}" if p.texto else "") for p in oferta.como_funciona]
    s["Processo"] = processo
    lac["Processo"] = [] if (oferta and oferta.big_idea.mecanismo_unico) else ["mecanismo"]
    return pk


def em_markdown(pk: Pacote, c: Contrato, formato: str | None = None) -> str:
    linhas = [f"# Pacote {pk.codigo} — {c.cliente.nome}", ""]
    linhas.append(f"Público: {pk.celula.publico or '—'} · Oferta: {pk.oferta.nome if pk.oferta else '—'} · "
                  f"Argumento: {pk.celula.argumento or '—'}")
    hip = c.hipoteses_da(pk.codigo)
    if hip:
        linhas.append("Hipóteses: " + "; ".join(f"{h.id} ({h.criterio_sucesso})" for h in hip))
    linhas.append("")
    for p in ("Pessoas", "Posicionamento", "Promessa", "Prova", "Prioridade", "Processo"):
        linhas += [f"## {p}", ""]
        linhas += [f"- {x}" for x in pk.secoes.get(p, [])] or ["- —"]
        if pk.lacunas.get(p):
            linhas.append(f"- **Falta no briefing:** {', '.join(pk.lacunas[p])}")
        linhas.append("")
    v = c.voz
    linhas += ["## Voz e limites", ""]
    linhas.append(f"- Tom: {', '.join(v.tom) or '—'} · Intensidade: {v.intensidade or '—'} de 5")
    linhas += [f"- Assim sim: {t}" for t in v.assim_sim] + [f"- Assim não: {t}" for t in v.assim_nao]
    proibidos = c.termos_proibidos() + c.compliance.promessas_proibidas
    if proibidos:
        linhas.append(f"- Nunca: {', '.join(dict.fromkeys(proibidos))}")
    linhas += [f"- Não pode: {t}" for t in c.compliance.nao_pode]
    linhas += [f"- Aviso legal: {t}" for t in c.compliance.avisos_legais]
    if formato:
        f = FORMATOS[formato]
        linhas += ["", f"## Formato: {f.descricao}", ""]
        for campo in f.campos:
            limite = f"{campo.rigido} caracteres (rígido)" if campo.rigido else (
                f"{campo.recomendado} caracteres antes do corte" if campo.recomendado else "")
            linhas.append(f"- {campo.nome}: {campo.minimo} a {campo.maximo}" + (f", até {limite}" if limite else ""))
    return "\n".join(linhas) + "\n"
