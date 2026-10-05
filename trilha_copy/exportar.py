"""Saída das peças aprovadas, prontas para subir nas plataformas e para o editor de vídeo.

Só sai o que está aprovado e não mudou depois da aprovação. O código da célula vai junto em cada linha:
é o `utm_content` do anúncio e o mesmo código que a Trilha-LP põe na mensagem do WhatsApp. O Trilha-ads
ainda não agrupa o raio-x por ele (está no roadmap de lá).
"""

from __future__ import annotations

import csv
from pathlib import Path

from trilha_copy.contrato import Contrato
from trilha_copy.peca import Google, Meta, Peca, Roteiro, carregar_peca, pecas_da_pasta


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


def roteiro_md(p: Peca, contrato: Contrato) -> str:
    r: Roteiro = p.roteiro
    linhas = [f"# Roteiro {p.id} ({p.codigo}) — {contrato.cliente.nome}", "",
              f"Duração: {r.duracao_s or '—'}s · Ideia: {p.ideia}", "",
              "| Tempo | Fala | Visual | Texto na tela |", "|---|---|---|---|"]
    linhas += [f"| {c.tempo} | {c.fala} | {c.visual} | {c.texto_tela} |" for c in r.cenas]
    linhas += ["", f"**Chamada:** {r.cta}", "", f"Código para a UTM e a mensagem do WhatsApp: `{p.codigo}`"]
    return "\n".join(linhas) + "\n"


def exportar(pasta: str | Path, contrato: Contrato, saida: str | Path, codigo: str | None = None) -> tuple[list[Path], list[str]]:
    pecas, recusadas = aprovadas(pasta, codigo)
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
    for p in pecas:
        if p.formato == "roteiro_video":
            arquivo = destino / "roteiros" / f"{p.id}.md"
            arquivo.parent.mkdir(exist_ok=True)
            arquivo.write_text(roteiro_md(p, contrato), encoding="utf-8")
            escritos.append(arquivo)
    return escritos, recusadas
