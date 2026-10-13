"""Modelos de corpo para roteiro de vídeo (regras/roteiros.yaml, editável).

Cada cena declara a parte do modelo que cumpre. A revisão confere se nenhuma parte obrigatória falta, se a ordem
segue o modelo (com as repetições do `ciclo`) e se toda cena diz a que veio. A cena da chamada falada (`parte: cta`)
vale em qualquer modelo, sempre no fim; o texto da chamada fica no campo `cta` do roteiro.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

ARQUIVO = Path(__file__).parent / "regras" / "roteiros.yaml"


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Parte(_Base):
    id: str = Field(pattern=r"^[a-z_]+$")
    faz: str
    opcional: bool = False


class Modelo(_Base):
    nome: str
    fonte: str = ""
    quando: str = ""
    ciclo: list[str] = Field(default_factory=list)
    partes: list[Parte]

    @model_validator(mode="after")
    def _coerente(self) -> Modelo:
        ids = [p.id for p in self.partes]
        if len(set(ids)) != len(ids):
            raise ValueError(f"{self.nome}: partes repetidas")
        if "cta" in ids:
            raise ValueError(f"{self.nome}: a chamada fica no campo cta do roteiro, não é parte do corpo")
        fora = [c for c in self.ciclo if c not in ids]
        if fora:
            raise ValueError(f"{self.nome}: ciclo cita partes que não existem: {fora}")
        return self

    def parte(self, pid: str) -> Parte | None:
        return next((p for p in self.partes if p.id == pid), None)

    def conferir(self, partes_das_cenas: list[str]) -> list[str]:
        """Problemas da sequência de partes das cenas, em texto para o assessor."""
        ids = [p.id for p in self.partes]
        problemas = []
        if "cta" in partes_das_cenas[:-1]:
            problemas.append("a cena da chamada (cta) fica no fim")
        partes_das_cenas = [x for x in partes_das_cenas if x != "cta"]  # a chamada falada vale em qualquer modelo
        sem = [i for i, x in enumerate(partes_das_cenas, start=1) if not x]
        if sem:
            problemas.append(f"cena(s) {', '.join(map(str, sem))} sem `parte`: diga o que cada cena faz no modelo")
        desconhecidas = sorted({x for x in partes_das_cenas if x and x not in ids})
        if desconhecidas:
            problemas.append(f"partes que o modelo não tem: {', '.join(desconhecidas)} (o modelo tem: {', '.join(ids)})")
        validas = [x for x in partes_das_cenas if x in ids]
        faltam = [p.id for p in self.partes if not p.opcional and p.id not in validas]
        if faltam:
            problemas.append(f"faltam as partes: {', '.join(faltam)}")
        for a, b in zip(validas, validas[1:]):
            if ids.index(b) < ids.index(a) and not (a in self.ciclo and b in self.ciclo):
                problemas.append(f"'{b}' vem depois de '{a}', mas no modelo vem antes ({' → '.join(ids)})")
                break
        return problemas


class Modelos(_Base):
    modelos: dict[str, Modelo]


@lru_cache(maxsize=1)
def modelos() -> dict[str, Modelo]:
    return Modelos.model_validate(yaml.safe_load(ARQUIVO.read_text(encoding="utf-8"))).modelos


def esqueleto(modelo: str, duracao_s: int) -> list[dict]:
    """Cenas vazias com a parte e um tempo sugerido: gancho nos 3 primeiros segundos, o resto dividido por igual,
    e a cena da chamada no fim."""
    partes = [p.id for p in modelos()[modelo].partes if not p.opcional] + ["cta"]
    if duracao_s <= 3 * len(partes):
        passo = duracao_s / len(partes)
        return [{"tempo": f"{round(passo * i)}-{round(passo * (i + 1))}", "parte": x} for i, x in enumerate(partes)]
    resto = partes[1:]
    passo = (duracao_s - 3) / len(resto)
    cenas = [{"tempo": "0-3", "parte": partes[0]}]
    for i, x in enumerate(resto):
        cenas.append({"tempo": f"{3 + round(passo * i)}-{3 + round(passo * (i + 1))}", "parte": x})
    return cenas
