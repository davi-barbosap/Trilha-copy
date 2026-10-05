"""Linha de comando do trilha-copy.

    python -m trilha_copy importar <copy.yaml> [--pasta clientes]     traz o contrato do Trilha-briefing
    python -m trilha_copy validar <pasta>                             contrato e peças no formato certo (não julga o texto)
    python -m trilha_copy pacote <pasta> <codigo> [--formato F]       os 6 Ps da célula, antes de escrever
    python -m trilha_copy nova <pasta> <codigo> --formato F [--id X]  cria a peça a partir da célula
    python -m trilha_copy checklist <peca.yaml>                       o que falta para sair do estado atual
    python -m trilha_copy avancar <peca.yaml>                         passa ao próximo estado, se nada faltar
    python -m trilha_copy revisar <peca.yaml | pasta>                 avisos por gravidade; sai com erro se algo bloqueia
    python -m trilha_copy aprovar <peca.yaml> --por NOME --teste-do-vendedor [--mesmo-dia]
    python -m trilha_copy exportar <pasta> [--codigo X] [--saida dist]   anuncios.csv, subida.csv e roteiros das aprovadas
    python -m trilha_copy ganchos                                     catálogo de tipos de gancho
    python -m trilha_copy referencias [pasta]                         banco de referências decupadas

Formatos: meta_feed, meta_reels, google_rsa, roteiro_video.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from pydantic import ValidationError

from trilha_copy.contrato import Contrato, carregar_contrato
from trilha_copy.exportar import exportar
from trilha_copy.fluxo import avancar, pendencias, preparar_aprovacao
from trilha_copy.formatos import CTA_META, FORMATOS
from trilha_copy.ganchos import GANCHOS
from trilha_copy.pacote import em_markdown, montar
from trilha_copy.peca import (ErroPeca, carregar_peca, pecas_da_pasta, proxima_versao, registrar_estado,
                             versoes_repetidas)
from trilha_copy.referencias import carregar_referencias
from trilha_copy.revisao import NIVEIS, revisar

ICONE = {"bloqueia": "✗", "atencao": "⚠", "sugestao": "·"}
ROTULO = {"bloqueia": "Bloqueia", "atencao": "Atenção", "sugestao": "Sugestão"}
MICRO = {
    "meta_feed": "parar de rolar e clicar no botão",
    "meta_reels": "assistir até o fim e clicar no botão",
    "google_rsa": "clicar, entre os anúncios da busca, quem procura exatamente isso",
    "roteiro_video": "assistir até a chamada e agir",
}


def _contrato_da_pasta(pasta: Path) -> Contrato:
    arquivo = pasta / "copy.yaml"
    if not arquivo.exists():
        sys.exit(f"✗ {arquivo} não existe: rode 'python -m trilha_copy importar <copy.yaml>' antes")
    try:
        return carregar_contrato(arquivo)
    except (ValidationError, ValueError) as e:
        sys.exit(f"✗ {arquivo}: {e}")


def _pasta_da_peca(caminho: Path) -> Path:
    # clientes/<id>/pecas/<codigo>/<peca>.yaml → clientes/<id>
    return caminho.resolve().parent.parent.parent


def _peca(caminho: str):
    try:
        return carregar_peca(caminho)
    except ErroPeca as e:
        sys.exit(f"✗ {e}")


def _mostrar(avisos) -> None:
    for nivel in NIVEIS:
        do_nivel = [a for a in avisos if a.nivel == nivel]
        if do_nivel:
            print(f"  {ROTULO[nivel]} ({len(do_nivel)})")
            for a in do_nivel:
                print(f"    {ICONE[nivel]} {a.texto}")


def cmd_importar(a) -> int:
    origem = Path(a.arquivo)
    try:
        c = carregar_contrato(origem)
    except (ValidationError, ValueError) as e:
        print(f"✗ {origem}: {e}")
        return 1
    destino = Path(a.pasta) / c.cliente.id / "copy.yaml"
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origem, destino)
    print(f"✓ {destino} (contrato {c.contrato}, gerado em {c.gerado_em}); {len(c.grade)} célula(s) na grade")
    return 0


def cmd_pacote(a) -> int:
    pasta = Path(a.pasta)
    c = _contrato_da_pasta(pasta)
    try:
        pk = montar(c, a.codigo)
    except ValueError as e:
        print(f"✗ {e}")
        return 1
    print(em_markdown(pk, c, a.formato))
    return 0


def cmd_nova(a) -> int:
    pasta = Path(a.pasta)
    c = _contrato_da_pasta(pasta)
    celula = c.celula(a.codigo)
    if celula is None:
        print(f"✗ célula {a.codigo} não existe na grade do briefing")
        return 1
    versao = proxima_versao(pasta, a.codigo, a.formato)
    pid = a.id or f"{a.codigo.lower()}-{a.formato.replace('_', '-')}" + (f"-v{versao}" if versao > 1 else "")
    destino = pasta / "pecas" / a.codigo / f"{pid}.yaml"
    if destino.exists():
        print(f"✗ {destino} já existe")
        return 1
    persona = c.persona(celula.persona)
    hip = c.hipoteses_da(a.codigo)
    bloco = {"meta_feed": "meta", "meta_reels": "meta", "google_rsa": "google", "roteiro_video": "roteiro"}[a.formato]
    conteudo = {
        "meta": ("meta:\n  textos_principais: []        # até 5; o gancho antes de 125 caracteres\n"
                 "  titulos: []                  # até 5; até 40 caracteres aparecem inteiros\n"
                 "  descricoes: []\n"
                 f"  cta_botao: \"\"                # {', '.join(CTA_META[:5])}…\n"),
        "google": ("google:\n  titulos: []                  # 3 a 15, até 30 caracteres; 10 ou mais dão o que combinar\n"
                   "  descricoes: []               # 2 a 4, até 90 caracteres\n"
                   "  caminhos: []                 # até 2, até 15 caracteres\n"
                   "  palavras_chave: []           # as buscas do grupo, para conferir a relevância\n"),
        "roteiro": ("roteiro:\n  duracao_s: 30\n  cenas: []                    # { tempo: \"0-3\", fala, visual, texto_tela }; gancho nos 3 primeiros segundos\n"
                    "  cta: \"\"\n"),
    }[bloco]
    texto = (
        f"# Peça {pid} da célula {a.codigo} ({celula.publico} — \"{celula.argumento}\").\n"
        f"# Antes de escrever: python -m trilha_copy pacote {pasta} {a.codigo} --formato {a.formato}\n"
        f"id: {pid}\ncodigo: {a.codigo}\nformato: {a.formato}\n"
        f"versao: {versao}                       # 1, 2, 3… por célula e plataforma; vai no nome do anúncio\n"
        "estado: fundacao\n\n"
        f"persona: {celula.persona}\noferta: {celula.oferta}\n"
        f"nivel_consciencia: {celula.nivel_consciencia or (persona.nivel_consciencia if persona else '') or 'null'}\n"
        f"micro_acao: \"{MICRO[a.formato]}\"\n"
        f"macro_acao: \"{c.evento_otimizacao or c.metrica_principal}\"\n"
        f"hipotese: \"{hip[0].id if hip else ''}\"\n"
        "ideia: \"\"                       # a ideia grande em uma frase\n\n"
        "rascunhos: []                   # títulos e ganchos em volume: escreva muitos (10+), descarte a maioria\n"
        "emocao: null                    # novo | facil | seguro | grande\n"
        "angulo: null                    # positivo | negativo (é variável de teste, não regra)\n"
        "gancho_tipo: \"\"                 # python -m trilha_copy ganchos\n"
        f"intensidade: {c.voz.intensidade or 'null'}\n"
        "provas: []                      # ids das provas do contrato usadas na peça\n\n"
        f"{conteudo}\n"
        "subtexto: []                    # { trecho, funcao }: o que cada trecho deve fazer sentir ou pensar\n\n"
        "# 'historico' é a última chave: a ferramenta acrescenta os estados aqui.\n"
        "historico: []\n"
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    carregar_peca(destino)
    print(f"✓ {destino}\n  Próximo: python -m trilha_copy pacote {pasta} {a.codigo} --formato {a.formato}")
    return 0


def cmd_checklist(a) -> int:
    p = _peca(a.peca)
    c = _contrato_da_pasta(_pasta_da_peca(Path(a.peca)))
    falta = pendencias(p, c)
    print(f"{p.id} — estado: {p.estado}")
    if not falta:
        print("  ✓ nada faltando: python -m trilha_copy " + ("aprovar" if p.estado == "final" else "avancar") + f" {a.peca}")
        return 0
    for f in falta:
        print(f"  … {f}")
    return 1


def cmd_avancar(a) -> int:
    p = _peca(a.peca)
    c = _contrato_da_pasta(_pasta_da_peca(Path(a.peca)))
    novo, falta = avancar(p, c)
    if novo is None:
        print(f"✗ {p.id} continua em {p.estado}:")
        for f in falta:
            print(f"  … {f}")
        return 1
    try:
        registrar_estado(a.peca, novo, a.nota)
    except ErroPeca as e:
        print(f"✗ {e}")
        return 1
    print(f"✓ {p.id}: {p.estado} → {novo}")
    return 0


def cmd_validar(a) -> int:
    pasta = Path(a.pasta)
    c = _contrato_da_pasta(pasta)
    erros, pecas = 0, []
    for caminho in pecas_da_pasta(pasta):
        try:
            pecas.append(carregar_peca(caminho))
        except ErroPeca as e:
            print(f"✗ {e}")
            erros += 1
    for problema in versoes_repetidas(pecas):
        print(f"✗ {problema}")
        erros += 1
    n = len(pecas_da_pasta(pasta))
    print(f"{'✓' if not erros else '✗'} {pasta}: contrato {c.contrato} de {c.cliente.id}; {n - erros} de {n} peça(s) válidas")
    return 1 if erros else 0


def cmd_revisar(a) -> int:
    alvo = Path(a.alvo)
    caminhos = pecas_da_pasta(alvo) if alvo.is_dir() else [alvo]
    pasta = alvo if alvo.is_dir() else _pasta_da_peca(alvo)
    c = _contrato_da_pasta(pasta)
    bloqueou = False
    for caminho in caminhos:
        p = _peca(caminho)
        avisos = revisar(p, c)
        bloqueou |= any(x.nivel == "bloqueia" for x in avisos)
        print(f"{p.id} ({p.formato}, {p.estado}): {len(avisos)} aviso(s)")
        _mostrar(avisos)
    if not caminhos:
        print("nenhuma peça em pecas/")
    return 1 if bloqueou else 0


def cmd_aprovar(a) -> int:
    p = _peca(a.peca)
    c = _contrato_da_pasta(_pasta_da_peca(Path(a.peca)))
    aprovacao, problemas = preparar_aprovacao(p, c, a.por, a.teste_do_vendedor, a.mesmo_dia)
    if aprovacao is None:
        print(f"✗ {p.id} não aprovada:")
        for x in problemas:
            print(f"  … {x}")
        return 1
    try:
        registrar_estado(a.peca, "aprovado", a.nota, aprovacao=aprovacao)
    except ErroPeca as e:
        print(f"✗ {e}")
        return 1
    print(f"✓ {p.id} aprovada por {a.por}. Exportar: python -m trilha_copy exportar {_pasta_da_peca(Path(a.peca))}")
    return 0


def cmd_exportar(a) -> int:
    pasta = Path(a.pasta)
    c = _contrato_da_pasta(pasta)
    escritos, recusadas, avisos = exportar(pasta, c, a.saida, a.codigo)
    for r in recusadas:
        print(f"✗ {r}")
    for e in escritos:
        print(f"✓ {e}")
    for x in avisos:
        print(f"⚠ {x}")
    if not escritos:
        print("nenhuma peça aprovada para exportar")
    return 1 if recusadas else 0


def cmd_ganchos(a) -> int:
    for nome, (descricao, exemplo) in GANCHOS.items():
        print(f"{nome:<22} {descricao}\n{'':<22} ex.: {exemplo}")
    return 0


def cmd_referencias(a) -> int:
    refs, erros = carregar_referencias(a.pasta)
    for nome, erro in erros.items():
        print(f"✗ {nome}: {erro}")
    for r in refs:
        print(f"{r.id:<24} [{r.formato}] {r.titulo} — gancho: {r.gancho_tipo or '—'} · {len(r.decupagem)} trecho(s) decupado(s)")
    return 1 if erros else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="trilha_copy", description="Estrutura e revisão de copy a partir do briefing")
    sub = ap.add_subparsers(dest="comando", required=True)
    s = sub.add_parser("importar"); s.add_argument("arquivo"); s.add_argument("--pasta", default="clientes"); s.set_defaults(f=cmd_importar)
    s = sub.add_parser("pacote"); s.add_argument("pasta"); s.add_argument("codigo"); s.add_argument("--formato", choices=list(FORMATOS))
    s.set_defaults(f=cmd_pacote)
    s = sub.add_parser("nova"); s.add_argument("pasta"); s.add_argument("codigo"); s.add_argument("--formato", choices=list(FORMATOS), required=True)
    s.add_argument("--id"); s.set_defaults(f=cmd_nova)
    s = sub.add_parser("checklist"); s.add_argument("peca"); s.set_defaults(f=cmd_checklist)
    s = sub.add_parser("avancar"); s.add_argument("peca"); s.add_argument("--nota", default=""); s.set_defaults(f=cmd_avancar)
    s = sub.add_parser("validar"); s.add_argument("pasta"); s.set_defaults(f=cmd_validar)
    s = sub.add_parser("revisar"); s.add_argument("alvo"); s.set_defaults(f=cmd_revisar)
    s = sub.add_parser("aprovar"); s.add_argument("peca"); s.add_argument("--por", required=True)
    s.add_argument("--teste-do-vendedor", action="store_true", help="um bom vendedor diria isso com o cliente na frente dele?")
    s.add_argument("--mesmo-dia", action="store_true", help="aprovar no mesmo dia em que a peça virou final")
    s.add_argument("--nota", default=""); s.set_defaults(f=cmd_aprovar)
    s = sub.add_parser("exportar"); s.add_argument("pasta"); s.add_argument("--codigo"); s.add_argument("--saida", default="dist")
    s.set_defaults(f=cmd_exportar)
    s = sub.add_parser("ganchos"); s.set_defaults(f=cmd_ganchos)
    s = sub.add_parser("referencias"); s.add_argument("pasta", nargs="?", default="referencias"); s.set_defaults(f=cmd_referencias)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
