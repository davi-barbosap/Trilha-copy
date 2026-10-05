"""Leitura do `copy.yaml`, o contrato gerado pelo Trilha-briefing (`exportar --para copy`).

A copy não inventa nada sobre o cliente: tudo o que ela pode usar vem daqui. O briefing é o dono dos
dados; por isso os modelos ignoram campos que ainda não conhecem, mas recusam versões de contrato novas.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

VERSOES_SUPORTADAS = {1}


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Item(_Base):
    texto: str
    fonte: str = "nao_informada"
    status: str = "hipotese"
    mencoes: int | None = None

    @model_validator(mode="before")
    @classmethod
    def _de_texto(cls, v: Any) -> Any:
        return {"texto": v} if isinstance(v, str) else v


class Crenca(_Base):
    texto: str
    tipo: Literal["metodo", "interna", "externa"]
    quebra: str = ""
    mencoes: int | None = None


class Frase(_Base):
    texto: str
    origem: str = ""
    sobre: str = "outro"


class Persona(_Base):
    id: str
    nome: str
    quem_e: str = ""
    dores: list[Item] = Field(default_factory=list)
    desejos: list[Item] = Field(default_factory=list)
    objecoes: list[Item] = Field(default_factory=list)
    ganchos: list[Item] = Field(default_factory=list)
    medos: list[Item] = Field(default_factory=list)
    crencas: list[Crenca] = Field(default_factory=list)
    micro_problemas: list[Item] = Field(default_factory=list)
    frases: list[Frase] = Field(default_factory=list)
    nivel_consciencia: str | None = None
    sofisticacao: str | None = None
    gatilho_compra: str = ""


class NaoAtender(_Base):
    perfil: str
    motivo: str = ""
    como_filtrar: str = ""


class Voz(_Base):
    assinatura: str | None = None
    nome_pessoa: str = ""
    tom: list[str] = Field(default_factory=list)
    assim_sim: list[str] = Field(default_factory=list)
    assim_nao: list[str] = Field(default_factory=list)
    termos_obrigatorios: list[str] = Field(default_factory=list)
    termos_proibidos: list[str] = Field(default_factory=list)
    intensidade: int | None = None


class Compliance(_Base):
    termos_proibidos: list[str] = Field(default_factory=list)
    promessas_proibidas: list[str] = Field(default_factory=list)
    registros_profissionais: list[str] = Field(default_factory=list)
    avisos_legais: list[str] = Field(default_factory=list)
    regras_legais: list[str] = Field(default_factory=list)
    nao_pode: list[str] = Field(default_factory=list)


class BigIdea(_Base):
    oportunidade: str = ""
    inimigo: str = ""
    mecanismo_unico: str = ""
    crenca_comum: str = ""
    por_que_falha: str = ""


class Promessa(_Base):
    texto: str
    resultado: str = ""
    prazo: str = ""
    condicao: str = ""


class Diferencial(Item):
    e_dai: list[str] = Field(default_factory=list)


class Alternativa(_Base):
    alternativa: str
    por_que_nao: str = ""


class Urgencia(_Base):
    tipo: str
    texto: str
    motivo: str = ""
    data: date | None = None
    real: bool = False


class Escassez(_Base):
    texto: str
    real: bool = False
    evidencia: str = ""


class Passo(_Base):
    titulo: str
    texto: str = ""


class Objecao(_Base):
    eixo: str = ""
    objecao: str
    resposta: str = ""


class AntesDepois(_Base):
    dimensao: str
    antes: str
    depois: str


class Oferta(_Base):
    id: str
    nome: str
    degrau: str = ""
    personas: list[str] = Field(default_factory=list)
    problema: str = ""
    big_idea: BigIdea = Field(default_factory=BigIdea)
    promessa: Promessa | None = None
    antes_depois: list[AntesDepois] = Field(default_factory=list)
    diferenciais: list[Diferencial] = Field(default_factory=list)
    raridade: str = ""
    bastidores: list[Item] = Field(default_factory=list)
    alternativas: list[Alternativa] = Field(default_factory=list)
    como_funciona: list[Passo] = Field(default_factory=list)
    objecoes: list[Objecao] = Field(default_factory=list)
    inversao_risco: str = ""
    escassez: Escassez | None = None
    urgencia: Urgencia | None = None
    custo_inacao: str = ""
    condicoes: dict[str, Any] = Field(default_factory=dict)
    cta: str = ""

    def urgencia_valida(self) -> bool:
        u = self.urgencia
        return bool(u and u.real and (u.data is None or u.data >= date.today()))

    def escassez_valida(self) -> bool:
        return bool(self.escassez and self.escassez.real and self.escassez.evidencia)


class Prova(_Base):
    id: str | None = None
    tipo: str
    texto: str
    numero: str = ""
    autor: str = ""
    fonte: str = ""
    personas: list[str] = Field(default_factory=list)
    perfil: str = ""

    def rotulo(self) -> str:
        base = f"{self.numero} {self.texto}".strip()
        return f"{base} — {self.autor}" if self.autor else base


class Historia(_Base):
    titulo: str
    antes: str = ""
    virada: str = ""
    resultado: str = ""
    personas: list[str] = Field(default_factory=list)
    perfil: str = ""


class Celula(_Base):
    codigo: str
    publico: str = ""
    argumento: str = ""
    persona: str = ""
    oferta: str = ""
    nivel_consciencia: str | None = None
    formato: str = ""
    prioridade: int = 2
    promessa: str = ""


class Hipotese(_Base):
    id: str
    hipotese: str = ""
    variavel: str = ""
    codigos: list[str] = Field(default_factory=list)
    criterio_sucesso: str = ""
    resultado: str = "planejada"


class Cliente(_Base):
    id: str
    nome: str
    segmento: str = ""
    whatsapp: str = ""
    area: str = ""


class Contrato(_Base):
    contrato: int
    gerado_em: date | None = None
    cliente: Cliente
    voz: Voz = Field(default_factory=Voz)
    posicionamento: dict[str, Any] = Field(default_factory=dict)
    compliance: Compliance = Field(default_factory=Compliance)
    unicidade: str = ""
    concorrentes: list[str] = Field(default_factory=list)
    personas: list[Persona] = Field(default_factory=list)
    nao_atender: list[NaoAtender] = Field(default_factory=list)
    ofertas: list[Oferta] = Field(default_factory=list)
    provas: list[Prova] = Field(default_factory=list)
    historias: list[Historia] = Field(default_factory=list)
    grade: list[Celula] = Field(default_factory=list)
    hipoteses: list[Hipotese] = Field(default_factory=list)
    metrica_principal: str = ""
    evento_otimizacao: str = ""

    @model_validator(mode="after")
    def _versao(self) -> Contrato:
        if self.contrato not in VERSOES_SUPORTADAS:
            raise ValueError(f"contrato versão {self.contrato} não suportada (suportadas: {sorted(VERSOES_SUPORTADAS)}); "
                             "atualize o trilha-copy")
        return self

    def persona(self, pid: str) -> Persona | None:
        return next((p for p in self.personas if p.id == pid), None)

    def oferta(self, oid: str) -> Oferta | None:
        return next((o for o in self.ofertas if o.id == oid), None)

    def celula(self, codigo: str) -> Celula | None:
        return next((c for c in self.grade if c.codigo == codigo), None)

    def prova(self, pid: str) -> Prova | None:
        return next((p for p in self.provas if p.id == pid), None)

    def hipoteses_da(self, codigo: str) -> list[Hipotese]:
        return [h for h in self.hipoteses if codigo in h.codigos]

    def provas_para(self, persona: str) -> list[Prova]:
        """Provas que convencem esta persona primeiro; depois as sem persona (números, autoridade)."""
        dela = [p for p in self.provas if persona in p.personas]
        neutras = [p for p in self.provas if not p.personas]
        return dela + neutras

    def termos_proibidos(self) -> list[str]:
        return list(dict.fromkeys([*self.voz.termos_proibidos, *self.compliance.termos_proibidos]))


def carregar_contrato(caminho: str | Path) -> Contrato:
    with open(caminho, encoding="utf-8") as f:
        return Contrato.model_validate(yaml.safe_load(f) or {})
