"""Revisão de texto público contra o padrão de texto da Trilha (regras/padrao.yaml) e o contrato do cliente.

Vale para a peça (anúncio e roteiro) e para a página da Trilha-LP (`revisar_pagina`). Cada aviso nasce de uma regra
do padrão, com a gravidade e a mensagem de lá:

    bloqueia   não vai ao ar assim: risco jurídico, recusa da plataforma, afirmação sem lastro, o que o cliente proibiu
    atencao    vai custar caro ou sair fraco: reprovação provável, texto cortado, promessa que não convence
    sugestao   melhora a peça: ritmo, palavras do cliente, adjetivo trocado por fato

Quem decide é o assessor. A revisão aponta, não reescreve.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from trilha_copy import padrao as pd
from trilha_copy import texto as tx
from trilha_copy.contrato import Contrato
from trilha_copy.formatos import FORMATOS
from trilha_copy.padrao import NIVEIS, Aviso, Nivel  # noqa: F401  (reexportados: quem importa daqui continua igual)
from trilha_copy.peca import Google, Meta, Peca, Roteiro
from trilha_copy.roteiros import modelos

ESTADOS_SEM_MINIMO = ("fundacao", "rascunho")


@dataclass
class Alvo:
    """O que está sendo revisado, do jeito que as regras precisam: uma peça ou uma página."""

    superficie: str  # anuncio, roteiro, pagina
    contexto: set[str]  # chaves de gravidade_por_contexto: superfície, formato, plataforma
    textos: list[tuple[str, str]]  # (onde, texto) de tudo o que o público lê
    corridos: list[tuple[str, str]]  # texto corrido: legibilidade e ritmo
    oferta: str = ""
    personas: list[str] = field(default_factory=list)
    provas: list[str] = field(default_factory=list)  # ids de prova citados (peça)
    intensidade: int | None = None
    pronto: bool = True  # fora de fundação e rascunho: valem os mínimos
    canal_preco: str = "anuncio"  # anuncio ou landing (regra comercial de preço)
    registro_declarado: bool = False  # registro na arte (peça) ou no rodapé (página)
    concretos: list[tuple[str, str]] | None = None  # onde procurar fato concreto (padrão: textos)


def _juntar(pares: list[tuple[str, str]]) -> str:
    return "\n".join(t for _, t in pares)


def _avisar(avisos: list[Aviso], alvo: Alvo, rid: str, **campos) -> None:
    a = pd.aviso(rid, alvo.contexto | {alvo.superficie}, **campos)
    if a is not None:
        avisos.append(a)


def _curto(t: str, n: int = 60) -> str:
    t = " ".join(t.split())
    return t if len(t) <= n else t[:n - 1] + "…"


# ---------- segmento ----------


def segmentos(c: Contrato) -> set[str]:
    """Segmentos com regra própria: o playbook do cliente e o que os registros profissionais revelam (CRO → saúde)."""
    saida = {c.cliente.playbook} - {"", "padrao"}
    registros = " ".join(c.compliance.registros_profissionais).upper()
    for seg, siglas in pd.parametro("registro_por_segmento").items():
        if any(s in registros for s in siglas):
            saida.add(seg)
    return saida


# ---------- compliance ----------


def _proibidos(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    lista = [(t, "termo proibido") for t in c.termos_proibidos()]
    lista += [(t, "promessa proibida") for t in c.compliance.promessas_proibidas]
    for seg in segmentos(c):
        lista += [(t, "proibido no segmento") for t in pd.carregar().vocabularios.get(f"promessa_proibida_{seg}", [])]
    vistos: set[str] = set()
    unicos = []
    for termo, motivo in lista:
        if tx.normalizar(termo) not in vistos:
            vistos.add(tx.normalizar(termo))
            unicos.append((termo, motivo))
    for onde, t in alvo.textos:
        for termo, motivo in unicos:
            if pd.posicoes_do_item(termo, t):
                _avisar(avisos, alvo, "termo_ou_promessa_proibida", onde=onde, motivo=motivo, termo=termo)


def _garantia(frase: str, oferta) -> bool:
    if pd.tem("garantia_de_resultado", frase):
        return True
    janela = pd.parametro("janela_garantia_palavras")
    garantias = [i for i, _ in pd.posicoes_do_item("garant*", frase)]
    resultados = [i for i, _ in pd.posicoes("resultado_garantivel", frase)]
    perto = any(abs(g - r) <= janela for g in garantias for r in resultados)
    if perto and pd.tem("inversao_de_risco", frase) and oferta and oferta.inversao_risco:
        return False  # garantia do que a empresa controla (devolução, teste), registrada no briefing
    return perto


def _frases(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    oferta = c.oferta(alvo.oferta)
    texto_todo = _juntar(alvo.textos)
    com_ressalva = pd.tem("ressalva_de_resultado", texto_todo) or any(
        tx.contem_termo(texto_todo, a) for a in c.compliance.avisos_legais)
    saude = "saude" in segmentos(c)
    for onde, t in alvo.textos:
        for frase in tx.frases(t):
            garante = _garantia(frase, oferta)
            if garante:
                _avisar(avisos, alvo, "garantia_de_resultado", onde=onde, trecho=_curto(frase))
            if pd.tem("pronomes_leitor", frase) and pd.tem("atributo_pessoal", frase):
                _avisar(avisos, alvo, "atributo_pessoal", onde=onde, frase=_curto(frase))
            exclusao = pd.achar("exclusao_de_publico", frase)
            if exclusao:
                _avisar(avisos, alvo, "exclusao_de_publico", onde=onde, trecho=exclusao[0])
            if not garante and not com_ressalva and _ganho_com_numero(frase):
                _avisar(avisos, alvo, "promessa_de_ganho", onde=onde, frase=_curto(frase))
            if saude:
                antes_depois = pd.achar("antes_e_depois", frase)
                if antes_depois:
                    _avisar(avisos, alvo, "antes_e_depois_em_saude", onde=onde, trecho=antes_depois[0],
                            regras_legais="; ".join(c.compliance.regras_legais) or "nenhuma registrada no briefing")
    for nome in c.concorrentes:
        if len(nome) >= pd.parametro("concorrente_minimo_letras") and any(tx.contem_termo(t, nome) for _, t in alvo.textos):
            _avisar(avisos, alvo, "concorrente_citado", nome=nome)


def _ganho_com_numero(frase: str) -> bool:
    ganhos = pd.achar("promessa_de_ganho", frase)
    if not ganhos:
        return False
    numeros = tx.numeros_relevantes(frase)
    if not numeros:
        return False
    so_ganh = all(tx.normalizar(g).startswith("ganh") for g in ganhos)
    if so_ganh:  # "ganhe 2 aulas" não é promessa de renda: só conta dinheiro, porcentagem ou milhar
        n = tx.normalizar(frase)
        return "r$" in n or "%" in n or " mil" in n
    return True


# ---------- lastro ----------


def _numeros_do_contrato(c: Contrato, oferta_id: str) -> set[str]:
    partes: list[str] = [f"{p.numero} {p.texto}" for p in c.provas]
    partes += [f"{h.titulo} {h.resultado}" for h in c.historias]
    o = c.oferta(oferta_id)
    if o:
        partes += [o.promessa.texto, o.promessa.resultado, o.promessa.prazo, o.promessa.condicao] if o.promessa else []
        partes += [d.texto for d in o.diferenciais] + [b.texto for b in o.bastidores] + [o.raridade, o.custo_inacao]
        partes += [f"{p.titulo} {p.texto}" for p in o.como_funciona] + [str(v) for v in o.condicoes.values() if v]
        if o.urgencia:
            partes += [o.urgencia.texto, o.urgencia.data.strftime("%d/%m/%Y") if o.urgencia.data else ""]
        if o.escassez:
            partes.append(o.escassez.texto)
        partes += [ad.antes + " " + ad.depois for ad in o.antes_depois]
    partes += [cel.promessa for cel in c.grade]
    numeros: set[str] = set()
    for parte in partes:
        numeros |= tx.numeros_relevantes(parte or "")
    return numeros


def _lastro(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    oferta = c.oferta(alvo.oferta)
    urgencia = pd.achar("urgencia", _juntar(alvo.textos))
    if urgencia and not (oferta and (oferta.urgencia_valida() or oferta.escassez_valida())):
        onde = next(o for o, t in alvo.textos if pd.tem("urgencia", t))
        _avisar(avisos, alvo, "urgencia_ou_escassez_sem_lastro", onde=onde, termo=urgencia[0])
    conhecidos = _numeros_do_contrato(c, alvo.oferta)
    soltos = [n for _, t in alvo.textos for n in sorted(tx.numeros_relevantes(t)) if n not in conhecidos]
    if soltos:
        _avisar(avisos, alvo, "numero_sem_lastro", numeros=", ".join(dict.fromkeys(soltos)))
    for pid in alvo.provas:
        prova = c.prova(pid)
        if prova is None:
            _avisar(avisos, alvo, "prova_nao_utilizavel", onde="provas", prova=pid,
                    motivo="não está no contrato (não existe, ou está sem fonte ou sem autorização no briefing)")
        elif prova.personas and alvo.personas and not set(alvo.personas) & set(prova.personas):
            _avisar(avisos, alvo, "prova_de_outra_persona", prova=pid, perfil=prova.perfil or "outro perfil")


# ---------- voz e concretude ----------


def _ignorar_nomes(c: Contrato, oferta_id: str) -> set[str]:
    oferta = c.oferta(oferta_id)
    nomes = f"{c.cliente.nome} {oferta.nome if oferta else ''}"
    return {tx.normalizar(p) for p in tx.palavras(nomes)}


def _voz(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    tudo = _juntar(alvo.textos)
    nos, voce = pd.contar("pronomes_marca", tudo), pd.contar("pronomes_leitor", tudo)
    if c.voz.assinatura in ("pessoa", "marca_pessoa"):
        nos += pd.contar("pronomes_pessoa", tudo)
    if nos >= pd.parametro("fala_de_si_minimo_nos") and nos > voce:
        _avisar(avisos, alvo, "fala_de_si", nos=nos, voce=voce)
    egoistas = pd.achar("frase_egoista", tudo)
    if egoistas:
        _avisar(avisos, alvo, "frase_egoista", trecho=egoistas[0])
    ignorar = _ignorar_nomes(c, alvo.oferta)
    for onde, t in alvo.textos:
        vagos = pd.achar("adjetivo_vago", t) + pd.achar("prova_vaga", t)
        if vagos and not any(ch.isdigit() for ch in t) and not tx.nomes_proprios(t, ignorar):
            _avisar(avisos, alvo, "vago_sem_fato", onde=onde, trecho=_curto(t))
    concretos = alvo.concretos if alvo.concretos is not None else alvo.textos
    if alvo.pronto and concretos and not alvo.provas and not any(
            any(ch.isdigit() for ch in t) or tx.nomes_proprios(t, ignorar) for _, t in concretos):
        _avisar(avisos, alvo, "peca_sem_concretude")
    exagero = pd.quantos("exagero", tudo) + tudo.count("!")
    exagero += sum(1 for w in tx.palavras(tudo) if len(w) >= 4 and w.isupper() and not w.isdigit())
    if alvo.intensidade and exagero > pd.parametro("limite_exagero_por_intensidade")[alvo.intensidade]:
        _avisar(avisos, alvo, "intensidade_acima_da_combinada", n=exagero, intensidade=alvo.intensidade)
    frases = [f.texto for pid in alvo.personas if (p := c.persona(pid)) for f in p.frases]
    if frases:
        do_cliente = set().union(*(tx.palavras_de_conteudo(f) for f in frases))
        if not (do_cliente & tx.palavras_de_conteudo(tudo)):
            _avisar(avisos, alvo, "sem_palavras_da_persona")


def _leitura(alvo: Alvo, avisos: list[Aviso]) -> None:
    corrido = _juntar(alvo.corridos)
    leg = pd.parametro("legibilidade")
    nota = tx.legibilidade(corrido)
    if nota is not None and nota < leg["dificil_abaixo_de"]:
        _avisar(avisos, alvo, "leitura_dificil", nota=f"{nota:.0f}")
    ritmo = tx.variacao_ritmo(corrido)
    if ritmo is not None and ritmo < pd.parametro("ritmo")["coeficiente_de_variacao_minimo"]:
        _avisar(avisos, alvo, "ritmo_monotono")


# ---------- preço e registro ----------


def regra_de_preco(c: Contrato, canal: str) -> str:
    """nunca, a_partir_de, parcela ou valor_cheio; o que a marca combinou ou o padrão do segmento ('' = livre)."""
    if c.preco.get(canal):
        return c.preco[canal]
    for seg in segmentos(c):
        padrao = pd.parametro("preco_padrao_por_segmento").get(seg, {})
        if padrao.get(canal):
            return padrao[canal]
    return ""


def _precos(frase: str) -> list[tuple[int, str]]:
    """Valores em reais que são preço (têm "por", "a partir de", "x"… a até 3 palavras), não número de prova."""
    janela = pd.parametro("janela_preco_palavras")
    contexto = [i for i, _ in pd.posicoes("preco_contexto", frase)]
    return [(i, v) for i, v in pd.posicoes("preco_valor", frase) if any(abs(i - j) <= janela for j in contexto)]


def _preco(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    regra = regra_de_preco(c, alvo.canal_preco)
    if regra in ("", "valor_cheio"):
        return
    for onde, t in alvo.textos:
        for frase in tx.frases(t):
            precos = _precos(frase)
            if not precos:
                continue
            if regra == "nunca":
                _avisar(avisos, alvo, "preco_proibido_no_canal", onde=onde, trecho=_curto(frase), canal=alvo.canal_preco)
                continue
            formas = [i for i, _ in pd.posicoes("forma_a_partir_de", frase)]
            ok = (all(any(0 <= i - j <= 4 for j in formas) for i, _ in precos) if regra == "a_partir_de"
                  else pd.tem("forma_parcela", frase))
            if not ok:
                _avisar(avisos, alvo, "preco_sem_forma_combinada", onde=onde, trecho=_curto(frase),
                        canal=alvo.canal_preco, regra=regra.replace("_", " "))


def _registro(alvo: Alvo, c: Contrato, avisos: list[Aviso]) -> None:
    registros = c.compliance.registros_profissionais
    exigidos = [s for seg in segmentos(c) for s in pd.parametro("registro_por_segmento").get(seg, [])]
    if not registros and not exigidos:
        return
    if alvo.registro_declarado:
        return
    tudo = tx.normalizar(_juntar(alvo.textos))
    sem_pontos = tudo.replace(".", "")

    def citado(registro: str) -> bool:  # o registro inteiro ou o número dele em algum texto
        numero = "".join(ch for ch in registro if ch.isdigit())
        return tx.normalizar(registro) in tudo or bool(numero) and numero in sem_pontos

    if alvo.pronto and not any(citado(r) for r in registros):
        _avisar(avisos, alvo, "registro_profissional_ausente", onde="peça" if alvo.superficie != "pagina" else "marca",
                registro=", ".join(registros) or "/".join(dict.fromkeys(exigidos)))


# ---------- formato da peça ----------


def _formato(p: Peca, alvo: Alvo, avisos: list[Aviso]) -> None:
    conteudo = p.conteudo()
    for campo in FORMATOS[p.formato].campos:
        itens = getattr(conteudo, campo.nome)
        if (alvo.pronto and len(itens) < campo.minimo) or len(itens) > campo.maximo:
            _avisar(avisos, alvo, "quantidade_de_textos", campo=campo.nome, n=len(itens), minimo=campo.minimo,
                    maximo=campo.maximo)
        for i, t in enumerate(itens):
            if campo.rigido and len(t) > campo.rigido:
                _avisar(avisos, alvo, "limite_rigido_da_plataforma", campo=campo.nome, i=i, n=len(t), limite=campo.rigido)
            elif campo.recomendado and campo.so_gancho:
                gancho = (tx.frases(t) or [t])[0]
                if len(gancho) > campo.recomendado:
                    _avisar(avisos, alvo, "texto_longo_para_a_tela", onde=f"{campo.nome}[{i}] (primeira frase)",
                            n=len(gancho), limite=campo.recomendado, efeito="o texto é cortado no feed e o gancho some")
            elif campo.recomendado and len(t) > campo.recomendado:
                _avisar(avisos, alvo, "texto_longo_para_a_tela", onde=f"{campo.nome}[{i}]", n=len(t),
                        limite=campo.recomendado, efeito="o texto é cortado na tela")
    if isinstance(conteudo, Meta) and alvo.pronto and not conteudo.cta_botao:
        _avisar(avisos, alvo, "meta_sem_botao")
    if isinstance(conteudo, Google):
        normalizados = [tx.normalizar(t) for t in conteudo.titulos]
        if len(set(normalizados)) != len(normalizados):
            _avisar(avisos, alvo, "titulos_google_repetidos")
        recomendados = pd.parametro("google_rsa")["titulos_recomendados"]
        if alvo.pronto and len(conteudo.titulos) < recomendados:
            _avisar(avisos, alvo, "poucos_titulos_google", n=len(conteudo.titulos))
        if conteudo.palavras_chave and not any(
                tx.contem_termo(t, k) for t in conteudo.titulos for k in conteudo.palavras_chave):
            _avisar(avisos, alvo, "titulo_sem_palavra_chave")
    if isinstance(conteudo, Roteiro):
        _roteiro(p, conteudo, alvo, avisos)
    if alvo.pronto:
        chamada = conteudo.cta if isinstance(conteudo, Roteiro) else " ".join(
            (conteudo.textos_principais[-1:] if isinstance(conteudo, Meta) else conteudo.descricoes[-1:]))
        if chamada and not pd.tem("quando_da_chamada", chamada):
            _avisar(avisos, alvo, "chamada_sem_quando")


def _roteiro(p: Peca, r: Roteiro, alvo: Alvo, avisos: list[Aviso]) -> None:
    if r.cenas:
        par = pd.parametro("roteiro")
        intervalos = [cena.intervalo() for cena in r.cenas]
        if any(i is None for i in intervalos):
            _avisar(avisos, alvo, "roteiro_tempo_ilegivel")
        else:
            if intervalos[0][1] > par["gancho_segundos"]:
                _avisar(avisos, alvo, "gancho_depois_de_3s", fim=f"{intervalos[0][1]:g}")
            fim = intervalos[-1][1]
            if r.duracao_s and abs(fim - r.duracao_s) > par["folga_duracao_segundos"]:
                _avisar(avisos, alvo, "duracao_nao_bate", fim=f"{fim:g}", duracao=r.duracao_s)
            for cena, (ini, fim_cena) in zip(r.cenas, intervalos):
                cabe = (fim_cena - ini) * par["palavras_por_segundo"]
                n = len(tx.palavras(cena.fala))
                if n > cabe + par["folga_palavras"]:
                    _avisar(avisos, alvo, "fala_nao_cabe_na_cena", tempo=cena.tempo, n=n, cabe=f"{cabe:.0f}")
        # O modelo de corpo é processo da copy (regras/roteiros.yaml), não regra de texto do padrão.
        if r.modelo:
            modelo = modelos()[r.modelo]
            for problema in modelo.conferir([cena.parte for cena in r.cenas]):
                avisos.append(Aviso("atencao", f"roteiro ({modelo.nome}): {problema}", "modelo_de_roteiro"))
        elif alvo.pronto:
            avisos.append(Aviso("sugestao", "roteiro sem modelo de corpo: escolha um (python -m trilha_copy roteiros) para "
                                            "a revisão conferir se cada parte está lá e na ordem", "modelo_de_roteiro"))
    if alvo.pronto:
        if not r.cta:
            _avisar(avisos, alvo, "roteiro_sem_chamada")
        if r.cenas and not any(cena.texto_tela for cena in r.cenas):
            _avisar(avisos, alvo, "roteiro_sem_texto_na_tela")


def _integridade(p: Peca, c: Contrato, alvo: Alvo, avisos: list[Aviso]) -> None:
    if p.estado == "aprovado" and not p.aprovacao_valida():
        _avisar(avisos, alvo, "aprovacao_invalidada")
    celula = c.celula(p.codigo)
    if celula is None:
        _avisar(avisos, alvo, "celula_inexistente", codigo=p.codigo)
    else:
        for campo, valor, esperado in (("persona", p.persona, celula.persona), ("oferta", p.oferta, celula.oferta)):
            if valor and esperado and valor != esperado:
                _avisar(avisos, alvo, "peca_diferente_da_celula", campo=campo, valor=valor, esperado=esperado)
    if p.hipotese and p.hipotese not in {h.id for h in c.hipoteses}:
        _avisar(avisos, alvo, "hipotese_inexistente", hipotese=p.hipotese)


# ---------- entrada ----------


def _texto_comum(alvo: Alvo, c: Contrato) -> list[Aviso]:
    avisos: list[Aviso] = []
    _proibidos(alvo, c, avisos)
    _frases(alvo, c, avisos)
    _lastro(alvo, c, avisos)
    _voz(alvo, c, avisos)
    _leitura(alvo, avisos)
    _preco(alvo, c, avisos)
    _registro(alvo, c, avisos)
    return avisos


def _ordenar(avisos: list[Aviso]) -> list[Aviso]:
    vistos, unicos = set(), []
    for a in avisos:
        if a.texto not in vistos:
            vistos.add(a.texto)
            unicos.append(a)
    return sorted(unicos, key=lambda a: NIVEIS.index(a.nivel))


def alvo_da_peca(p: Peca, c: Contrato) -> Alvo:
    plataforma = FORMATOS[p.formato].plataforma
    textos = p.textos()
    arte = p.meta.arte if p.meta else None
    return Alvo(
        superficie="roteiro" if plataforma == "video" else "anuncio",
        contexto={p.formato, plataforma},
        textos=textos,
        corridos=[(o, t) for o, t in textos if "textos_principais" in o or ".fala" in o or "descricoes" in o],
        oferta=p.oferta, personas=[p.persona] if p.persona else [], provas=list(p.provas),
        intensidade=p.intensidade or c.voz.intensidade, pronto=p.estado not in ESTADOS_SEM_MINIMO,
        canal_preco="anuncio", registro_declarado=bool(arte and arte.registro_na_arte),
    )


def revisar(p: Peca, c: Contrato) -> list[Aviso]:
    alvo = alvo_da_peca(p, c)
    avisos = _texto_comum(alvo, c)
    _formato(p, alvo, avisos)
    _integridade(p, c, alvo, avisos)
    return _ordenar(avisos)


def bloqueantes(p: Peca, c: Contrato) -> list[Aviso]:
    return [a for a in revisar(p, c) if a.nivel == "bloqueia"]


# ---------- página da Trilha-LP ----------


def _g(dados: dict, *chaves, padrao=""):
    for k in chaves:
        if not isinstance(dados, dict):
            return padrao
        dados = dados.get(k)
    return padrao if dados is None else dados


def textos_da_pagina(d: dict) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    """(textos públicos, corridos, onde procurar fato concreto) de um pagina.yaml, sem depender do código da LP."""
    t: list[tuple[str, str]] = [("pagina.titulo_seo", _g(d, "pagina", "titulo_seo")),
                                ("pagina.descricao_seo", _g(d, "pagina", "descricao_seo")),
                                ("topo.titulo", _g(d, "topo", "titulo")), ("topo.subtitulo", _g(d, "topo", "subtitulo")),
                                ("topo.cta", _g(d, "topo", "cta", "texto"))]
    t += [(f"topo.provas[{i}]", x) for i, x in enumerate(_g(d, "topo", "provas", padrao=[]))]
    t += [(f"topo.reducao_medo[{i}]", x) for i, x in enumerate(_g(d, "topo", "reducao_medo", padrao=[]))]
    for c in ("titulo", "problema", "agravamento", "solucao"):
        t.append((f"dor.{c}", _g(d, "dor", c)))
    t.append(("prova_social.titulo", _g(d, "prova_social", "titulo")))
    t += [(f"prova_social.depoimentos[{i}]", _g(x, "texto")) for i, x in enumerate(_g(d, "prova_social", "depoimentos", padrao=[]))]
    t += [(f"prova_social.numeros[{i}]", f"{_g(x, 'numero')} {_g(x, 'texto')}")
          for i, x in enumerate(_g(d, "prova_social", "numeros", padrao=[]))]
    t.append(("beneficios.titulo", _g(d, "beneficios", "titulo")))
    beneficios = _g(d, "beneficios", "itens", padrao=[])
    for i, b in enumerate(beneficios):
        t += [(f"beneficios.itens[{i}].titulo", _g(b, "titulo")), (f"beneficios.itens[{i}].texto", _g(b, "texto"))]
    t.append(("como_funciona.titulo", _g(d, "como_funciona", "titulo")))
    t += [(f"como_funciona.passos[{i}]", f"{_g(x, 'titulo')} {_g(x, 'texto')}")
          for i, x in enumerate(_g(d, "como_funciona", "passos", padrao=[]))]
    t.append(("objecoes.titulo", _g(d, "objecoes", "titulo")))
    objecoes = _g(d, "objecoes", "itens", padrao=[])
    t += [(f"objecoes.itens[{i}]", f"{_g(x, 'pergunta')} {_g(x, 'resposta')}") for i, x in enumerate(objecoes)]
    t += [(f"objecoes.garantias[{i}]", x) for i, x in enumerate(_g(d, "objecoes", "garantias", padrao=[]))]
    t += [("fechamento.titulo", _g(d, "fechamento", "titulo")), ("fechamento.subtitulo", _g(d, "fechamento", "subtitulo"))]
    t += [(f"fechamento.lista[{i}]", x) for i, x in enumerate(_g(d, "fechamento", "lista", padrao=[]))]
    t += [("formulario.botao", _g(d, "formulario", "botao")), ("contato.mensagem_whatsapp", _g(d, "contato", "mensagem_whatsapp"))]
    t = [(o, x) for o, x in t if isinstance(x, str) and x.strip()]
    corridos = [(o, x) for o, x in t if o in ("topo.subtitulo", "fechamento.subtitulo") or o.startswith("dor.")
                or (o.startswith("beneficios.itens") and o.endswith(".texto")) or o.startswith("objecoes.itens")]
    concretos = [(o, x) for o, x in t if o.startswith(("topo.", "beneficios."))]
    return t, corridos, concretos


def revisar_pagina(d: dict, c: Contrato) -> list[Aviso]:
    """A página com as mesmas regras de texto da peça, mais as próprias de página. A estrutura (blocos, ordem,
    rastreamento) continua com a Trilha-LP (`python -m trilha_lp validar`)."""
    textos, corridos, concretos = textos_da_pagina(d)
    oferta_id = _g(d, "pagina", "oferta")
    oferta = c.oferta(oferta_id)
    alvo = Alvo(superficie="pagina", contexto={"pagina"}, textos=textos, corridos=corridos, oferta=oferta_id,
                personas=list(oferta.personas) if oferta else [], intensidade=c.voz.intensidade, canal_preco="landing",
                registro_declarado=bool(_g(d, "marca", "registro_profissional")), concretos=concretos)
    avisos = _texto_comum(alvo, c)
    topo = _g(d, "topo", "titulo")
    for onde, valor, limite, efeito in (
            ("topo.titulo", topo, pd.parametro("pagina")["topo_titulo_maximo"],
             "no celular passa de 3 linhas e empurra o botão para baixo"),
            ("pagina.descricao_seo", _g(d, "pagina", "descricao_seo"), pd.parametro("pagina")["descricao_seo_maximo"],
             "o Google corta a descrição no resultado da busca")):
        if len(valor) > limite:
            _avisar(avisos, alvo, "texto_longo_para_a_tela", onde=onde, n=len(valor), limite=limite, efeito=efeito)
    genericos = {tx.normalizar(x) for x in pd.vocabulario("titulo_generico")}
    for bloco in ("prova_social", "beneficios", "como_funciona", "objecoes", "fechamento"):
        titulo = _g(d, bloco, "titulo")
        if titulo and _sem_pontuacao(titulo) in genericos:
            _avisar(avisos, alvo, "titulo_de_bloco_generico", onde=f"{bloco}.titulo", titulo=titulo)
    ctas = {tx.normalizar(x) for x in pd.vocabulario("cta_generico")}
    for onde, valor in (("topo.cta", _g(d, "topo", "cta", "texto")), ("formulario.botao", _g(d, "formulario", "botao"))):
        if valor and _sem_pontuacao(valor) in ctas:
            _avisar(avisos, alvo, "cta_generico", onde=onde, texto=valor)
    for i, item in enumerate(_g(d, "objecoes", "itens", padrao=[])):
        resposta = _g(item, "resposta")
        so_manda_falar = pd.tem("cta_generico", resposta) and not any(ch.isdigit() for ch in resposta)
        if not resposta.strip() or so_manda_falar:
            _avisar(avisos, alvo, "objecao_sem_resposta", onde=f"objecoes.itens[{i}]", objecao=_g(item, "pergunta"))
    return _ordenar(avisos)


def _sem_pontuacao(t: str) -> str:
    return " ".join("".join(ch if ch.isalnum() or ch == " " else " " for ch in tx.normalizar(t)).split())
