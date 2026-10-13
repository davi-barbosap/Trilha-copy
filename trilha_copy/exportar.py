"""Saída das peças aprovadas, prontas para subir nas plataformas e para o editor de vídeo.

Só sai o que está aprovado e não mudou depois da aprovação. O código da célula vai junto em cada linha:
é o `utm_content` do anúncio e o mesmo código que a Trilha-LP põe na mensagem do WhatsApp. O raio-x do
Trilha-ads agrupa leads, qualificados e vendas por ele (`por_criativo`).

- `anuncios.csv`: os textos, um por linha (campo e ordem), para colar na plataforma.
- `subida.csv`: um anúncio por linha: em que campanha e conjunto ele entra, com que nome e com que parâmetros
  de URL. Vem do plano de campanhas do briefing (`veiculacao` no contrato); a mesma peça pode entrar em mais de
  um conjunto, com `utm_campaign` diferente, por isso não cabe no CSV dos textos.
- `criativos/<peca>.md`: o briefing do criativo de cada anúncio do Meta, para a equipe de criação: para que serve,
  para quem, a ideia, o que a arte mostra, o texto na arte, as provas, o que não pode e as medidas. Não é design.
- `roteiros/<peca>.md`: o roteiro de cada vídeo, com o mesmo cabeçalho e a parte do modelo de cada cena.
"""

from __future__ import annotations

import csv
from pathlib import Path

from trilha_copy.contrato import Contrato
from trilha_copy.formatos import FORMATOS
from trilha_copy.peca import Google, Meta, Peca, Roteiro, carregar_peca, pecas_da_pasta, plataforma_da
from trilha_copy.roteiros import modelos

CAMPOS_SUBIDA = ["plataforma", "campanha", "conjunto", "nome_anuncio", "parametros_url", "codigo", "peca", "formato"]


def aprovadas(pasta: str | Path, codigo: str | None = None) -> tuple[list[Peca], list[str]]:
    ok, recusadas = [], []
    for caminho in pecas_da_pasta(pasta):
        p = carregar_peca(caminho)
        if codigo and p.codigo != codigo:
            continue
        if p.estado != "aprovado":
            continue
        if not p.aprovacao_valida():
            recusadas.append(f"{p.id}: o texto mudou depois da aprovação")
            continue
        ok.append(p)
    return ok, recusadas


def _linhas(p: Peca) -> list[dict]:
    c = p.conteudo()
    base = {"codigo": p.codigo, "utm_content": p.codigo, "peca": p.id, "formato": p.formato}
    linhas = []
    if isinstance(c, Meta):
        campos = [("texto_principal", c.textos_principais), ("titulo", c.titulos), ("descricao", c.descricoes),
                  ("botao", [c.cta_botao] if c.cta_botao else [])]
    elif isinstance(c, Google):
        campos = [("titulo", c.titulos), ("descricao", c.descricoes), ("caminho", c.caminhos)]
    else:
        return []
    for campo, itens in campos:
        for i, texto in enumerate(itens, start=1):
            linhas.append({**base, "campo": campo, "ordem": i, "texto": texto, "caracteres": len(texto)})
    return linhas


def subida(pecas: list[Peca], contrato: Contrato) -> tuple[list[dict], list[str]]:
    """Uma linha por anúncio a criar e os avisos das peças que o plano não diz onde rodam."""
    linhas, avisos = [], []
    for p in pecas:
        plataforma = plataforma_da(p)
        if plataforma == "video":
            continue  # o roteiro vira anúncio pela peça meta_reels que usa o vídeo
        locais = contrato.locais_de(p.codigo, plataforma)
        if not locais:
            avisos.append(f"{p.id}: a célula {p.codigo} não está em nenhum conjunto de {plataforma} no plano de campanhas; "
                          "fica fora da subida.csv (ponha no plano do briefing e exporte de novo)")
        for l in locais:
            linhas.append({"plataforma": plataforma, "campanha": l.campanha, "conjunto": l.conjunto,
                           "nome_anuncio": l.preencher(l.anuncio, p.codigo, p.versao),
                           "parametros_url": l.preencher(l.parametros_url, p.codigo, p.versao),
                           "codigo": p.codigo, "peca": p.id, "formato": p.formato})
    return linhas, avisos


EMOCAO = {"novo": "novo", "facil": "fácil", "seguro": "seguro", "grande": "grande"}


def _item(rotulo: str, texto: str) -> str:
    """Item de lista que aguenta texto com parágrafos (as linhas seguintes ficam dentro do item)."""
    return f"- {rotulo}: " + texto.replace("\n", "\n  ")


def _cabecalho(p: Peca, c: Contrato) -> list[str]:
    """O que a equipe de criação precisa saber antes de produzir: para que serve, para quem, a ideia e o que não pode."""
    persona = c.persona(p.persona)
    hipotese = next((h for h in c.hipoteses if h.id == p.hipotese), None)
    locais = c.locais_de(p.codigo, plataforma_da(p))
    linhas = [f"Cliente: {c.cliente.nome} · {FORMATOS[p.formato].descricao} · versão {p.versao}"]
    for l in locais:
        linhas.append(f"Anúncio: **{l.preencher(l.anuncio, p.codigo, p.versao)}** (campanha {l.campanha}, conjunto {l.conjunto})")
    linhas += ["", "## Para que serve", "",
               f"- Esta peça precisa fazer a pessoa: {p.micro_acao or '—'}",
               f"- O que o sistema precisa no fim: {p.macro_acao or '—'}"]
    if hipotese:
        linhas.append(f"- Teste: {hipotese.hipotese or hipotese.id}"
                      + (f". O que varia entre as versões é **{hipotese.variavel}**: mantenha o resto igual, senão o "
                         "teste não diz nada." if hipotese.variavel else ""))
    linhas += ["", "## Para quem", ""]
    if persona:
        linhas.append(f"- {persona.nome}" + (f": {persona.quem_e}" if persona.quem_e else ""))
        frases = [f.texto for f in persona.frases[:3]]
        if frases:
            linhas.append("- Do jeito que essa pessoa fala: " + " · ".join(f"\"{x}\"" for x in frases))
    else:
        linhas.append(f"- {p.persona or '—'}")
    linhas += ["", "## A ideia", "", f"- {p.ideia or '—'}"]
    tom = [x for x in (f"emoção: {EMOCAO.get(p.emocao, p.emocao)}" if p.emocao else "", f"ângulo: {p.angulo}" if p.angulo else "",
                       f"intensidade {p.intensidade} de 5" if p.intensidade else "") if x]
    if tom:
        linhas.append(f"- {' · '.join(tom)}")
    if c.voz.tom:
        linhas.append(f"- Tom da marca: {', '.join(c.voz.tom)}")
    provas = [c.prova(x) for x in p.provas]
    if any(provas):
        linhas += ["", "## Provas que podem aparecer", ""]
        linhas += [f"- {x.rotulo()}" + (f" ({x.fonte})" if x.fonte else "") for x in provas if x]
    nao = list(dict.fromkeys([*c.compliance.nao_pode, *c.compliance.promessas_proibidas]))
    proibidos = sorted({*c.compliance.termos_proibidos, *c.voz.termos_proibidos})
    obrigatorio = [*c.compliance.avisos_legais, *c.compliance.registros_profissionais]
    if nao or proibidos or obrigatorio:
        linhas += ["", "## O que não pode e o que é obrigatório", ""]
        linhas += [f"- Não: {x}" for x in nao]
        if proibidos:
            linhas.append(f"- Palavras proibidas, inclusive na arte: {', '.join(proibidos)}")
        linhas += [f"- Obrigatório quando a regra pedir: {x}" for x in obrigatorio]
    return linhas


def _identidade(c: Contrato) -> list[str]:
    iv = c.identidade_visual
    if iv.vazia():
        return ["", "## Identidade da marca", "", "- Não preenchida no briefing (plataforma.yaml, identidade_visual): "
                "peça o manual de marca ao cliente antes de produzir."]
    linhas = ["", "## Identidade da marca", ""]
    if iv.cores:
        linhas.append("- Cores: " + ", ".join(f"{k} {', '.join(v) if isinstance(v, list) else v}" for k, v in iv.cores.items()))
    if iv.tipografia:
        linhas.append("- Tipografia: " + ", ".join(f"{k} {v}" for k, v in iv.tipografia.items()))
    if iv.logo:
        linhas.append(f"- Logo: {iv.logo}")
    if iv.estilo_imagem:
        linhas.append(f"- Estilo de imagem: {iv.estilo_imagem}")
    return linhas


def briefing_md(p: Peca, contrato: Contrato) -> str:
    """Briefing do criativo de um anúncio do Meta, para a equipe de criação. Diz o que comunicar, não como desenhar."""
    m: Meta = p.meta
    arte = m.arte
    linhas = [f"# Briefing do criativo — {p.codigo} v{p.versao} ({p.id})", "", *_cabecalho(p, contrato),
              "", "## O que a arte precisa mostrar", "", arte.mostrar if arte and arte.mostrar else "— (não preenchido)"]
    if arte and arte.texto_na_arte:
        linhas += ["", "Texto na arte, exatamente assim (já revisado):", ""] + [f"- {t}" for t in arte.texto_na_arte]
    if arte and arte.evitar:
        linhas += ["", f"Evitar: {arte.evitar}"]
    if arte and arte.referencias:
        linhas += ["", "Referências:", ""] + [f"- {r}" for r in arte.referencias]
    linhas += _identidade(contrato)
    linhas += ["", "## Especificações", "", f"- {(arte.tipo if arte else 'imagem').capitalize()}: {FORMATOS[p.formato].arte}",
               "- Medidas mudam: confira a documentação da plataforma antes de exportar.",
               "", "## O texto que acompanha a arte", "",
               "A arte não precisa repetir o texto: ela prende o olho, o texto explica.", ""]
    linhas += [_item("Texto principal", t) for t in m.textos_principais]
    linhas += [_item("Título", t) for t in m.titulos]
    linhas += [_item("Descrição", t) for t in m.descricoes]
    if m.cta_botao:
        linhas.append(f"- Botão: {m.cta_botao}")
    linhas += ["", f"Código para a UTM e a mensagem do WhatsApp: `{p.codigo}`"]
    return "\n".join(linhas) + "\n"


def roteiro_md(p: Peca, contrato: Contrato) -> str:
    r: Roteiro = p.roteiro
    modelo = modelos().get(r.modelo) if r.modelo else None
    linhas = [f"# Roteiro {p.id} ({p.codigo}) — {contrato.cliente.nome}", "", *_cabecalho(p, contrato),
              *_identidade(contrato), "",
              "## Roteiro", "",
              f"Duração: {r.duracao_s or '—'}s · Modelo: {modelo.nome if modelo else '—'} · "
              f"{FORMATOS[p.formato].arte}", ""]
    if modelo:
        nomes = {x.id: x.faz for x in modelo.partes} | {"cta": "a chamada"}
        linhas += ["| Tempo | Parte | Fala | Visual | Texto na tela |", "|---|---|---|---|---|"]
        linhas += [f"| {c.tempo} | {c.parte or '—'} | {c.fala} | {c.visual} | {c.texto_tela} |" for c in r.cenas]
        usadas = [x for x in dict.fromkeys(c.parte for c in r.cenas) if x in nomes]
        linhas += ["", "O que cada parte faz:", ""] + [f"- **{x}**: {nomes[x]}" for x in usadas]
    else:
        linhas += ["| Tempo | Fala | Visual | Texto na tela |", "|---|---|---|---|"]
        linhas += [f"| {c.tempo} | {c.fala} | {c.visual} | {c.texto_tela} |" for c in r.cenas]
    linhas += ["", f"**Chamada:** {r.cta}", "", f"Código para a UTM e a mensagem do WhatsApp: `{p.codigo}`"]
    return "\n".join(linhas) + "\n"


def exportar(pasta: str | Path, contrato: Contrato, saida: str | Path,
             codigo: str | None = None) -> tuple[list[Path], list[str], list[str]]:
    """(arquivos escritos, peças recusadas, avisos)."""
    pecas, recusadas = aprovadas(pasta, codigo)
    avisos: list[str] = []
    destino = Path(saida) / contrato.cliente.id
    destino.mkdir(parents=True, exist_ok=True)
    escritos: list[Path] = []
    linhas = [linha for p in pecas for linha in _linhas(p)]
    if linhas:
        arquivo = destino / "anuncios.csv"
        with open(arquivo, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["codigo", "utm_content", "peca", "formato", "campo", "ordem", "texto", "caracteres"])
            w.writeheader()
            w.writerows(linhas)
        escritos.append(arquivo)
    if contrato.veiculacao:
        anuncios, avisos = subida(pecas, contrato)
        if anuncios:
            arquivo = destino / "subida.csv"
            with open(arquivo, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=CAMPOS_SUBIDA)
                w.writeheader()
                w.writerows(anuncios)
            escritos.append(arquivo)
    elif linhas:
        avisos.append("o contrato não tem plano de campanhas (veiculacao): subida.csv não foi gerado, e o nome e os "
                      "parâmetros de URL de cada anúncio ficam por conta de quem sobe")
    for p in pecas:
        if p.formato == "roteiro_video":
            arquivo = destino / "roteiros" / f"{p.id}.md"
            arquivo.parent.mkdir(exist_ok=True)
            arquivo.write_text(roteiro_md(p, contrato), encoding="utf-8")
            escritos.append(arquivo)
        elif isinstance(p.conteudo(), Meta):
            arquivo = destino / "criativos" / f"{p.id}.md"
            arquivo.parent.mkdir(exist_ok=True)
            arquivo.write_text(briefing_md(p, contrato), encoding="utf-8")
            escritos.append(arquivo)
    return escritos, recusadas, avisos
