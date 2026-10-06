"""O padrão de texto da Trilha (regras/padrao.yaml): vocabulários, parâmetros e regras com gravidade e mensagem.

Como um item de vocabulário casa com o texto (os dois sem acento e em minúsculas):
- `termo` ou `duas palavras`: termo inteiro ("corra" casa com "Corra!", não com "ocorra");
- `radical*`: começo de palavra ("garantid*" pega garantido e garantida, não garantia);
- `re:expressão`: expressão regular com borda de palavra no começo; no fim, só não pode emendar em letra
  (assim "r\\$ ?\\d" casa com "R$ 450", e "\\d+ ?x" não casa com "20 xícaras").

A gravidade de cada regra pode mudar por contexto (`gravidade_por_contexto`: formato, superfície ou marca da
revisão, como `pagina` ou `meta_categoria_especial`) e pode ser `desligada`.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from trilha_copy.texto import normalizar

ARQUIVO = Path(__file__).parent / "regras" / "padrao.yaml"
Nivel = Literal["bloqueia", "atencao", "sugestao"]
NIVEIS: tuple[Nivel, ...] = ("bloqueia", "atencao", "sugestao")
Gravidade = Literal["bloqueia", "atencao", "sugestao", "desligada"]
Superficie = Literal["briefing", "anuncio", "roteiro", "pagina"]
BORDA = "(?<![a-z0-9])"
PALAVRA_NORMALIZADA = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Aviso:
    nivel: Nivel
    texto: str
    regra: str = ""

    def __str__(self) -> str:
        return self.texto


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Principio(_Base):
    id: str
    principio: str
    explicacao: str = ""
    fonte: str = ""
    regras: list[str] = Field(default_factory=list)


class Regra(_Base):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    grupo: str = ""
    o_que: str
    como_detectar: str = ""
    gravidade: Gravidade
    gravidade_por_contexto: dict[str, Gravidade] = Field(default_factory=dict)
    aplica_a: list[Superficie]
    segmento: str | list[str] = "geral"
    usa: list[str] = Field(default_factory=list)
    fonte: str
    mensagem: str
    exemplo_ruim: str = ""
    exemplo_bom: str = ""

    def gravidade_em(self, contexto: set[str]) -> Gravidade:
        for chave, g in self.gravidade_por_contexto.items():
            if chave in contexto:
                return g
        return self.gravidade


class Padrao(_Base):
    versao: str
    gravidades: dict[str, str] = Field(default_factory=dict)
    notacao: dict[str, str] = Field(default_factory=dict)
    principios: list[Principio]
    parametros: dict[str, Any]
    vocabularios: dict[str, list[str]]
    regras: list[Regra]

    @model_validator(mode="after")
    def _coerente(self) -> Padrao:
        ids = [r.id for r in self.regras]
        repetidas = sorted({i for i in ids if ids.count(i) > 1})
        if repetidas:
            raise ValueError(f"regras repetidas: {repetidas}")
        for r in self.regras:
            faltam = [v for v in r.usa if v not in self.vocabularios and v not in self.parametros]
            if faltam:
                raise ValueError(f"{r.id} usa vocabulários que não existem: {faltam}")
        for nome, itens in self.vocabularios.items():
            for item in itens:
                if not item.startswith("re:") and item != normalizar(item):
                    raise ValueError(f"vocabulário {nome}: '{item}' precisa estar sem acento e em minúsculas")
                try:
                    _padrao_do_item(item)
                except re.error as e:
                    raise ValueError(f"vocabulário {nome}: '{item}' não é uma expressão válida ({e})") from e
        for p in self.principios:
            fora = [x for x in p.regras if x not in ids]
            if fora:
                raise ValueError(f"princípio {p.id} cita regras que não existem: {fora}")
        return self

    def regra(self, rid: str) -> Regra:
        return next(r for r in self.regras if r.id == rid)


@lru_cache(maxsize=512)
def _padrao_do_item(item: str) -> re.Pattern:
    if item.startswith("re:"):
        return re.compile(BORDA + "(?:" + item[3:] + ")(?![a-z])")
    if item.endswith("*"):
        return re.compile(BORDA + re.escape(item[:-1]) + "[a-z0-9]*")
    return re.compile(BORDA + re.escape(item) + "(?![a-z0-9])")


@lru_cache(maxsize=1)
def carregar(caminho: str | Path = ARQUIVO) -> Padrao:
    return Padrao.model_validate(yaml.safe_load(Path(caminho).read_text(encoding="utf-8")))


def vocabulario(nome: str) -> list[str]:
    return carregar().vocabularios[nome]


def parametro(nome: str) -> Any:
    return carregar().parametros[nome]


def achar(nome: str, texto: str) -> list[str]:
    """Os trechos do texto (normalizado) que casam com itens do vocabulário, na ordem dos itens."""
    t = normalizar(texto)
    achados = []
    for item in vocabulario(nome):
        m = _padrao_do_item(item).search(t)
        if m:
            achados.append(m.group(0))
    return achados


def posicoes(nome: str, texto: str) -> list[tuple[int, str]]:
    """(posição em palavras, trecho) de cada ocorrência dos itens do vocabulário."""
    return _posicoes(vocabulario(nome), texto)


def posicoes_do_item(item: str, texto: str) -> list[tuple[int, str]]:
    """O mesmo, para um item avulso na mesma notação (termo, radical* ou re:) — ex.: um termo proibido do cliente."""
    return _posicoes([item if item.startswith("re:") else normalizar(item)], texto)


def _posicoes(itens: list[str], texto: str) -> list[tuple[int, str]]:
    t = normalizar(texto)
    achados = []
    for item in itens:
        for m in _padrao_do_item(item).finditer(t):
            achados.append((len(PALAVRA_NORMALIZADA.findall(t[:m.start()])), m.group(0)))
    return sorted(achados)


def contar(nome: str, texto: str) -> int:
    """Quantas vezes os itens do vocabulário aparecem no texto (ocorrências, não itens distintos)."""
    return len(posicoes(nome, texto))


def tem(nome: str, texto: str) -> bool:
    return bool(achar(nome, texto))


def quantos(nome: str, texto: str) -> int:
    """Quantos itens distintos do vocabulário aparecem no texto."""
    return len(achar(nome, texto))


class _Campos(dict):
    def __missing__(self, chave: str) -> str:
        return "{" + chave + "}"


def aviso(rid: str, contexto: set[str] = frozenset(), /, **campos: Any) -> Aviso | None:
    """O aviso da regra com a mensagem preenchida, ou None quando a regra está desligada nesse contexto."""
    r = carregar().regra(rid)
    nivel = r.gravidade_em(set(contexto))
    if nivel == "desligada":
        return None
    texto = string.Formatter().vformat(r.mensagem, (), _Campos(campos))
    return Aviso(nivel, texto.strip(), rid)
