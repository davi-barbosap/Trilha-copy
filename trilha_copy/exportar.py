"""Saída das peças aprovadas, prontas para subir nas plataformas e para o editor de vídeo.

Só sai o que está aprovado e não mudou depois da aprovação. O código da célula vai junto em cada linha:
é o `utm_content` do anúncio e o mesmo código que a Trilha-LP põe na mensagem do WhatsApp. O raio-x do
Trilha-ads agrupa leads, qualificados e vendas por ele (`por_criativo`).

- `anuncios.csv`: os textos, um por linha (campo e ordem), para colar na plataforma.
- `subida.csv`: um anúncio por linha: em que campanha e conjunto ele entra, com que nome e com que parâmetros
  de URL. Vem do plano de campanhas do briefing (`veiculacao` no contrato); a mesma peça pode entrar em mais de
  um conjunto, com `utm_campaign` diferente, por isso não cabe no CSV dos textos.
- `roteiros/<peca>.md`: o roteiro de cada vídeo, para quem grava e edita.
"""

from __future__ import annotations

import csv
from pathlib import Path

from trilha_copy.contrato import Contrato
from trilha_copy.peca import Google, Meta, Peca, Roteiro, carregar_peca, pecas_da_pasta, plataforma_da

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


def roteiro_md(p: Peca, contrato: Contrato) -> str:
    r: Roteiro = p.roteiro
    linhas = [f"# Roteiro {p.id} ({p.codigo}) — {contrato.cliente.nome}", "",
              f"Duração: {r.duracao_s or '—'}s · Ideia: {p.ideia}", "",
              "| Tempo | Fala | Visual | Texto na tela |", "|---|---|---|---|"]
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
    return escritos, recusadas, avisos
