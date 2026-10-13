"""Banco de referências decupadas (swipe file): peças boas de qualquer segmento, com o porquê.

Cada referência marca, trecho a trecho, o que ele faz o leitor sentir ou pensar. Estudar assim é a
etapa "estudar" do ciclo de aprendizado; guardar assim deixa o estudo reaproveitável.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from trilha_copy.ganchos import GANCHOS


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Trecho(_Base):
    trecho: str
    funcao: str  # novo, fácil, seguro, grande, prova, derruba crença, urgência…


class Referencia(_Base):
    id: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]
    titulo: str
    fonte: str  # de onde veio: anunciante, ano, link
    formato: Literal["meta", "google", "video", "impresso", "email", "pagina", "outro"]
    segmento: str = ""
    gancho_tipo: str = ""
    texto: str
    decupagem: list[Trecho] = Field(default_factory=list)
    por_que_funciona: str = ""
    resultado_conhecido: str = ""  # só com fonte; sem fonte, deixe vazio


def carregar_referencias(pasta: str | Path) -> tuple[list[Referencia], dict[str, str]]:
    refs, erros = [], {}
    for caminho in sorted(Path(pasta).glob("*.yaml")):
        try:
            r = Referencia.model_validate(yaml.safe_load(caminho.read_text(encoding="utf-8")) or {})
        except (ValidationError, yaml.YAMLError) as e:
            erros[caminho.name] = str(e)
            continue
        if r.id != caminho.stem:
            erros[caminho.name] = f"id '{r.id}' diferente do nome do arquivo"
        elif r.gancho_tipo and r.gancho_tipo not in GANCHOS:
            erros[caminho.name] = f"gancho_tipo '{r.gancho_tipo}' fora do catálogo"
        else:
            refs.append(r)
    return refs, erros


FORMATO_DA_PLATAFORMA = {"meta": "meta", "google": "google", "video": "video"}


def de_peca_vencedora(p, contrato, hipotese) -> Referencia:
    """A peça aprovada que venceu um teste vira referência decupada do próprio cliente.

    A decupagem vem do subtexto da peça (o que cada trecho deveria fazer sentir); o porquê, do aprendizado registrado
    no briefing; o resultado, da hipótese, com a fonte (o retorno do Trilha-ads). É o estudo que vale mais: o que
    funcionou com este público.
    """
    from trilha_copy.peca import plataforma_da

    textos = [t for _, t in p.textos()]
    return Referencia(
        id=p.id,
        titulo=f"{contrato.cliente.nome}, {p.codigo}: {p.ideia or (textos[0] if textos else p.id)}"[:120],
        fonte=f"{contrato.cliente.nome}, peça {p.id}; hipótese {hipotese.id} {hipotese.resultado}"
              + (f" em {hipotese.fim:%d/%m/%Y}" if hipotese.fim else "") + " (retorno do Trilha-ads)",
        formato=FORMATO_DA_PLATAFORMA.get(plataforma_da(p), "outro"),
        segmento=contrato.cliente.segmento,
        gancho_tipo=p.gancho_tipo if p.gancho_tipo in GANCHOS else "",
        texto="\n\n".join(textos),
        decupagem=[Trecho(trecho=x.trecho, funcao=x.funcao) for x in p.subtexto],
        por_que_funciona=hipotese.aprendizado,
        resultado_conhecido=f"{hipotese.hipotese} Critério: {hipotese.criterio_sucesso}."
                            + (f" Conversões por variação: {hipotese.conversoes_obtidas}." if hipotese.conversoes_obtidas else ""),
    )

