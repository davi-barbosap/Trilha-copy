"""Medidas de texto em português: frases, palavras, sílabas, legibilidade, ritmo e números.

São aproximações para apontar onde olhar, não notas absolutas. A contagem de sílabas agrupa vogais
(ditongos contam como uma, hiatos às vezes também), o que basta para comparar textos entre si.
"""

from __future__ import annotations

import re
import statistics
import unicodedata

PALAVRA = re.compile(r"[A-Za-zÀ-ÿ0-9]+(?:[-'][A-Za-zÀ-ÿ0-9]+)*")
FIM_DE_FRASE = re.compile(r"(?<=[.!?…])\s+|\n+")
NUMERO = re.compile(r"(R\$\s*)?(\d+(?:[.,]\d+)*)(\s*%)?")

STOPWORDS = set("""
a o as os um uma uns umas de do da dos das em no na nos nas por para pra pelo pela pelos pelas com sem sob sobre
e ou mas que se nao sim ja mais menos muito muita muitos muitas pouco tudo nada isso isto aquilo esse essa este esta
eu tu ele ela nos vos eles elas voce voces seu sua seus suas meu minha meus minhas te me lhe ao aos a as quando onde
como porque porquê qual quais quem ate entre depois antes agora ainda so tambem bem ser estar ter fazer vai vou foi
era sao esta estao tem tinha fica ficar todo toda todos todas cada outro outra outros outras mesmo mesma aqui ali la
""".split())


def normalizar(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def frases(texto: str) -> list[str]:
    return [f.strip() for f in FIM_DE_FRASE.split(texto) if PALAVRA.search(f)]


def palavras(texto: str) -> list[str]:
    return PALAVRA.findall(texto)


def silabas(palavra: str) -> int:
    p = normalizar(palavra)
    p = re.sub(r"(?<=[qg])u(?=[ei])", "", p)  # "que", "gui": o u não soa
    return max(1, len(re.findall(r"[aeiouy]+", p)))


def legibilidade(texto: str) -> float | None:
    """Índice de Flesch adaptado ao português (Martins et al., 1996). Acima de 75 é fácil; abaixo de 50, difícil."""
    fs, ps = frases(texto), palavras(texto)
    if not fs or len(ps) < 30:
        return None
    total_silabas = sum(silabas(p) for p in ps)
    return 248.835 - 1.015 * (len(ps) / len(fs)) - 84.6 * (total_silabas / len(ps))


def variacao_ritmo(texto: str) -> float | None:
    """Coeficiente de variação do tamanho das frases. Perto de zero = todas iguais (texto monótono)."""
    tamanhos = [len(palavras(f)) for f in frases(texto)]
    if len(tamanhos) < 4 or statistics.mean(tamanhos) == 0:
        return None
    return statistics.pstdev(tamanhos) / statistics.mean(tamanhos)


def numeros_relevantes(texto: str) -> set[str]:
    """Números que afirmam algo: com dois dígitos ou mais, em reais ou em porcentagem. Só os dígitos."""
    achados = set()
    for m in NUMERO.finditer(texto):
        digitos = re.sub(r"\D", "", m.group(2))
        if len(digitos) >= 2 or m.group(1) or m.group(3):
            achados.add(digitos)
    return achados


def contem_termo(texto: str, termo: str) -> bool:
    """Termo inteiro, sem acento e sem diferença de maiúsculas."""
    t = normalizar(termo).strip()
    return bool(t) and re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", normalizar(texto)) is not None


def palavras_de_conteudo(texto: str) -> set[str]:
    return {normalizar(p) for p in palavras(texto) if len(p) >= 5 and normalizar(p) not in STOPWORDS}


def nomes_proprios(texto: str, ignorar: set[str] = frozenset()) -> list[str]:
    """Palavras com inicial maiúscula fora do começo da frase: nome de lugar, pessoa, marca, método.

    CAIXA ALTA de 4 letras ou mais não conta (é ênfase, não nome). `ignorar`: palavras normalizadas que não contam,
    como o nome do próprio cliente e da oferta.
    """
    achados = []
    for f in frases(texto):
        for i, p in enumerate(palavras(f)):
            if i == 0 or not p[0].isupper() or (len(p) >= 4 and p.isupper()):
                continue
            if normalizar(p) not in ignorar:
                achados.append(p)
    return achados
