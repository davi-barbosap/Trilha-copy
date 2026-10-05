"""Uma peça de copy: um anúncio ou um roteiro, ligado a uma célula da grade.

A peça passa por estados (fundação → rascunho → refinado → final → aprovado). Quem escreve é o
assessor; a ferramenta guarda a estrutura, confere e registra as mudanças de estado.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from trilha_copy.formatos import FORMATOS

Estado = Literal["fundacao", "rascunho", "refinado", "final", "aprovado"]
ESTADOS: tuple[Estado, ...] = ("fundacao", "rascunho", "refinado", "final", "aprovado")
Emocao = Literal["novo", "facil", "seguro", "grande"]
Id = Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Meta(_Base):
    textos_principais: list[str] = Field(default_factory=list)
    titulos: list[str] = Field(default_factory=list)
    descricoes: list[str] = Field(default_factory=list)
    cta_botao: str = ""


class Google(_Base):
    titulos: list[str] = Field(default_factory=list)
    descricoes: list[str] = Field(default_factory=list)
    caminhos: list[str] = Field(default_factory=list)
    palavras_chave: list[str] = Field(default_factory=list)  # as buscas do grupo, para conferir a relevância


class Cena(_Base):
    tempo: str  # "0-3", "3-12" (segundos)
    fala: str = ""
    visual: str = ""
    texto_tela: str = ""

    def intervalo(self) -> tuple[float, float] | None:
        m = re.fullmatch(r"\s*(\d+(?:[.,]\d+)?)\s*-\s*(\d+(?:[.,]\d+)?)\s*s?\s*", self.tempo)
        if not m:
            return None
        return float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))


class Roteiro(_Base):
    duracao_s: int | None = Field(default=None, ge=5, le=600)
    cenas: list[Cena] = Field(default_factory=list)
    cta: str = ""


class Subtexto(_Base):
    """O que cada trecho deve fazer a pessoa sentir ou pensar. Torna a revisão objetiva."""

    trecho: str
    funcao: str  # "novo", "seguro", "derruba crença interna", "prova", "urgência"…


class Aprovacao(_Base):
    por: str
    data: date
    teste_do_vendedor: bool  # "um bom vendedor diria isso com o cliente na frente dele?"
    assinatura: str  # resumo do conteúdo aprovado; se o texto mudar, a aprovação cai


class Registro(_Base):
    estado: Estado
    data: date
    nota: str = ""


class Peca(_Base):
    id: Id
    codigo: Annotated[str, Field(pattern=r"^[A-Z0-9]{2,8}$")]
    formato: Literal["meta_feed", "meta_reels", "google_rsa", "roteiro_video"]
    versao: int = Field(default=1, ge=1)  # 1, 2, 3… entre as peças da mesma célula na mesma plataforma; vai no nome do anúncio
    estado: Estado = "fundacao"
    # fundação
    persona: str = ""
    oferta: str = ""
    nivel_consciencia: str | None = None
    micro_acao: str = ""  # o que esta peça precisa provocar: parar de rolar, clicar, chamar no WhatsApp
    macro_acao: str = ""  # o que o sistema inteiro precisa: lead qualificado, agendamento, venda
    hipotese: str = ""
    ideia: str = ""  # a ideia grande em uma frase
    # rascunho
    rascunhos: list[str] = Field(default_factory=list)  # títulos e ganchos em volume: escreva muitos, descarte a maioria
    emocao: Emocao | None = None
    angulo: Literal["positivo", "negativo"] | None = None
    gancho_tipo: str = ""
    intensidade: int | None = Field(default=None, ge=1, le=5)
    provas: list[str] = Field(default_factory=list)  # ids das provas do contrato usadas na peça
    # conteúdo
    meta: Meta | None = None
    google: Google | None = None
    roteiro: Roteiro | None = None
    subtexto: list[Subtexto] = Field(default_factory=list)
    aprovacao: Aprovacao | None = None
    historico: list[Registro] = Field(default_factory=list)

    @model_validator(mode="after")
    def _bloco_do_formato(self) -> Peca:
        plataforma = FORMATOS[self.formato].plataforma
        esperado = {"meta": "meta", "google": "google", "video": "roteiro"}[plataforma]
        for bloco in ("meta", "google", "roteiro"):
            if bloco != esperado and getattr(self, bloco) is not None:
                raise ValueError(f"formato {self.formato} usa o bloco '{esperado}', não '{bloco}'")
        if getattr(self, esperado) is None:
            setattr(self, esperado, {"meta": Meta, "google": Google, "roteiro": Roteiro}[esperado]())
        if self.estado == "aprovado" and self.aprovacao is None:
            raise ValueError("estado aprovado sem o bloco 'aprovacao': use o comando aprovar")
        return self

    def conteudo(self) -> Meta | Google | Roteiro:
        return self.meta or self.google or self.roteiro

    def textos(self) -> list[tuple[str, str]]:
        """(onde, texto) de tudo o que o público lê ou ouve."""
        c = self.conteudo()
        saida: list[tuple[str, str]] = []
        if isinstance(c, Meta):
            saida += [(f"meta.textos_principais[{i}]", t) for i, t in enumerate(c.textos_principais)]
            saida += [(f"meta.titulos[{i}]", t) for i, t in enumerate(c.titulos)]
            saida += [(f"meta.descricoes[{i}]", t) for i, t in enumerate(c.descricoes)]
        elif isinstance(c, Google):
            saida += [(f"google.titulos[{i}]", t) for i, t in enumerate(c.titulos)]
            saida += [(f"google.descricoes[{i}]", t) for i, t in enumerate(c.descricoes)]
            saida += [(f"google.caminhos[{i}]", t) for i, t in enumerate(c.caminhos)]
        else:
            for i, cena in enumerate(c.cenas):
                saida += [(f"roteiro.cenas[{i}].fala", cena.fala), (f"roteiro.cenas[{i}].texto_tela", cena.texto_tela)]
            saida.append(("roteiro.cta", c.cta))
        return [(onde, t) for onde, t in saida if t and t.strip()]

    def assinatura_conteudo(self) -> str:
        dados = self.conteudo().model_dump(mode="json")
        return hashlib.sha256(json.dumps(dados, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

    def aprovacao_valida(self) -> bool:
        return self.aprovacao is not None and self.aprovacao.assinatura == self.assinatura_conteudo()

    def data_do_estado(self, estado: Estado) -> date | None:
        datas = [r.data for r in self.historico if r.estado == estado]
        return datas[-1] if datas else None


class ErroPeca(Exception):
    pass


def carregar_peca(caminho: str | Path) -> Peca:
    caminho = Path(caminho)
    try:
        with open(caminho, encoding="utf-8") as f:
            peca = Peca.model_validate(yaml.safe_load(f) or {})
    except (ValidationError, yaml.YAMLError) as e:
        raise ErroPeca(f"{caminho}: {e}") from e
    if peca.id != caminho.stem:
        raise ErroPeca(f"{caminho}: id '{peca.id}' diferente do nome do arquivo")
    if caminho.parent.name != peca.codigo:
        raise ErroPeca(f"{caminho}: a peça {peca.codigo} precisa ficar na pasta pecas/{peca.codigo}/")
    return peca


def pecas_da_pasta(pasta: str | Path) -> list[Path]:
    return sorted(Path(pasta).glob("pecas/*/*.yaml"))


def plataforma_da(p: Peca) -> str:
    return FORMATOS[p.formato].plataforma


def versoes_repetidas(pecas: list[Peca]) -> list[str]:
    """Peças da mesma célula e plataforma com a mesma versão: os anúncios teriam o mesmo nome."""
    vistas: dict[tuple[str, str, int], str] = {}
    problemas = []
    for p in pecas:
        chave = (p.codigo, plataforma_da(p), p.versao)
        if plataforma_da(p) != "video" and chave in vistas:
            problemas.append(f"{vistas[chave]} e {p.id}: mesma célula ({p.codigo}), mesma plataforma ({chave[1]}) e mesma "
                             f"versão ({p.versao}); os anúncios teriam o mesmo nome. Mude `versao` de uma delas.")
        vistas.setdefault(chave, p.id)
    return problemas


def proxima_versao(pasta: str | Path, codigo: str, formato: str) -> int:
    plataforma = FORMATOS[formato].plataforma
    usadas = []
    for caminho in sorted(Path(pasta).glob(f"pecas/{codigo}/*.yaml")):
        try:
            p = carregar_peca(caminho)
        except ErroPeca:
            continue
        if plataforma_da(p) == plataforma:
            usadas.append(p.versao)
    return max(usadas, default=0) + 1


# ---------- escrita que preserva os comentários do arquivo ----------


def _yaml_linha(valor: dict) -> str:
    return yaml.safe_dump(valor, default_flow_style=True, allow_unicode=True, width=1000).strip()


def registrar_estado(caminho: str | Path, novo: Estado, nota: str = "", hoje: date | None = None,
                     aprovacao: Aprovacao | None = None) -> None:
    """Troca a linha `estado:` e acrescenta ao `historico:` (a última chave do arquivo), sem reescrever o resto."""
    caminho = Path(caminho)
    texto = caminho.read_text(encoding="utf-8")
    texto, n = re.subn(r"(?m)^estado:\s*\S+", f"estado: {novo}", texto, count=1)
    if n == 0:
        raise ErroPeca(f"{caminho}: linha 'estado:' não encontrada")
    registro = {"estado": novo, "data": (hoje or date.today()).isoformat()}
    if nota:
        registro["nota"] = nota
    linha = f"  - {_yaml_linha(registro)}\n"
    if aprovacao is not None:
        bloco = "aprovacao: " + _yaml_linha(aprovacao.model_dump(mode="json")) + "\n"
        if re.search(r"(?m)^aprovacao:", texto):
            texto = re.sub(r"(?m)^aprovacao:.*\n", bloco, texto, count=1)
        else:
            # antes do comentário que acompanha 'historico', se houver, para o comentário ficar junto dele
            alvo = r"(?m)^(# 'historico'.*\n)?historico:"
            texto = re.sub(alvo, lambda m: bloco + m.group(0), texto, count=1)
    if re.search(r"(?m)^historico:\s*\[\]\s*$", texto):
        texto = re.sub(r"(?m)^historico:\s*\[\]\s*$", "historico:", texto, count=1)
    if not re.search(r"(?m)^historico:", texto):
        texto = texto.rstrip("\n") + "\nhistorico:\n"
    original = caminho.read_text(encoding="utf-8")
    caminho.write_text(texto.rstrip("\n") + "\n" + linha, encoding="utf-8")
    try:
        carregar_peca(caminho)
    except ErroPeca:
        caminho.write_text(original, encoding="utf-8")  # 'historico' precisa ser a última chave do arquivo
        raise ErroPeca(f"{caminho}: não deu para registrar o estado; deixe 'historico:' como a última chave do arquivo")
