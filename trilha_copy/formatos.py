"""Regras de cada formato de peça.

Limites `rigido` a plataforma recusa; limites `recomendado` cortam o texto na tela ("ver mais") ou
perdem força. Os números vêm da documentação pública das plataformas, que muda de tempos em tempos:
se uma peça for recusada ou cortada de um jeito que a revisão não previu, confira a documentação vigente.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Campo:
    nome: str
    minimo: int
    maximo: int
    rigido: int | None = None  # caracteres que a plataforma não aceita passar
    recomendado: int | None = None  # caracteres a partir dos quais o texto é cortado na tela
    so_gancho: bool = False  # o corte vale para a primeira frase (o gancho); o resto pode ser longo


@dataclass(frozen=True)
class Formato:
    id: str
    plataforma: str
    descricao: str
    campos: tuple[Campo, ...] = field(default_factory=tuple)
    arte: str = ""  # medidas da arte para a equipe de criação (confira na documentação vigente da plataforma)


CTA_META = (
    "Saiba mais", "Cadastre-se", "Inscreva-se", "Enviar mensagem", "Enviar mensagem pelo WhatsApp",
    "Agendar", "Fale conosco", "Pedir orçamento", "Obter oferta", "Comprar agora", "Ver mais",
)

META_CAMPOS = (
    Campo("textos_principais", 1, 5, recomendado=125, so_gancho=True),
    Campo("titulos", 1, 5, recomendado=40),
    Campo("descricoes", 0, 5, recomendado=30),
)

FORMATOS: dict[str, Formato] = {
    "meta_feed": Formato("meta_feed", "meta", "Anúncio de feed (imagem ou carrossel) no Facebook e Instagram", META_CAMPOS,
                         arte="1080×1350 (4:5) ou 1080×1080 (1:1); carrossel com a mesma proporção em todos os cartões"),
    "meta_reels": Formato("meta_reels", "meta", "Anúncio em Reels e Stories (o texto aparece por cima do vídeo)", META_CAMPOS,
                          arte="1080×1920 (9:16); nada importante nas faixas de cima e de baixo, que a interface cobre"),
    "google_rsa": Formato("google_rsa", "google", "Anúncio responsivo de pesquisa do Google", (
        Campo("titulos", 3, 15, rigido=30),
        Campo("descricoes", 2, 4, rigido=90),
        Campo("caminhos", 0, 2, rigido=15),
    )),
    "roteiro_video": Formato("roteiro_video", "video", "Roteiro de vídeo curto (Reels, Shorts, anúncio em vídeo)",
                             arte="vertical 9:16 (1080×1920); legenda ou texto na tela, porque muita gente assiste sem som"),
}

PALAVRAS_POR_SEGUNDO = 2.5  # fala natural em português, cerca de 150 palavras por minuto
GANCHO_SEGUNDOS = 3  # o vídeo precisa prender nos primeiros 3 segundos
TITULOS_GOOGLE_RECOMENDADOS = 10  # com menos títulos, o Google tem pouco o que combinar
