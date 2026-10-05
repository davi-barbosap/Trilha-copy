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
