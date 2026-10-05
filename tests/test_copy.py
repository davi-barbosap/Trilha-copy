import contextlib
import csv
import io
import shutil
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml
from pydantic import ValidationError

from trilha_copy import texto as tx
from trilha_copy.__main__ import main
from trilha_copy.contrato import Contrato, carregar_contrato
from trilha_copy.exportar import aprovadas, exportar
from trilha_copy.fluxo import MINIMO_RASCUNHOS, avancar, pendencias, preparar_aprovacao
from trilha_copy.ganchos import GANCHOS
from trilha_copy.pacote import em_markdown, montar
from trilha_copy.peca import ErroPeca, Peca, carregar_peca, registrar_estado
from trilha_copy.referencias import carregar_referencias
from trilha_copy.revisao import revisar

RAIZ = Path(__file__).parent.parent
EXEMPLO = RAIZ / "clientes" / "_exemplo"
PT01 = EXEMPLO / "pecas" / "PT01" / "pt01-meta-feed.yaml"
PT02 = EXEMPLO / "pecas" / "PT02" / "pt02-roteiro-video.yaml"
GB01 = EXEMPLO / "pecas" / "GB01" / "gb01-google-rsa.yaml"


def ler(caminho):
    return yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))


def contrato(mudar=None) -> Contrato:
    dados = ler(EXEMPLO / "copy.yaml")
    if mudar:
        mudar(dados)
    return Contrato.model_validate(dados)


def peca(caminho=PT01, mudar=None) -> Peca:
    dados = ler(caminho)
    if mudar:
        mudar(dados)
    return Peca.model_validate(dados)


def meta(*textos, estado="refinado", **campos) -> Peca:
    """PT01 com outros textos principais, fora de 'aprovado' para a aprovação não interferir."""
    def mudar(d):
        d["estado"] = estado
        d.pop("aprovacao")
        d["meta"]["textos_principais"] = list(textos)
        d.update(campos)
    return peca(PT01, mudar)


def avisos(p, c=None, nivel=None) -> list[str]:
    return [a.texto for a in revisar(p, c or contrato()) if nivel is None or a.nivel == nivel]


def rodar(*args) -> tuple[int, str]:
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        try:
            rc = main([str(a) for a in args])
        except SystemExit as e:  # sem contrato ou peça inválida: sys.exit(mensagem)
            print(e.code)
            rc = 1
    return rc, saida.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pasta = self.tmp / "_exemplo"
        shutil.copytree(EXEMPLO, self.pasta)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def arquivo(self, codigo, pid):
        return self.pasta / "pecas" / codigo / f"{pid}.yaml"


def contem(lista, trecho) -> bool:
    return any(trecho in t for t in lista)


class TestContrato(unittest.TestCase):
    def test_exemplo_carrega(self):
        c = carregar_contrato(EXEMPLO / "copy.yaml")
        self.assertEqual((c.contrato, c.cliente.id), (1, "_exemplo"))
        self.assertEqual([x.codigo for x in c.grade], ["PT01", "PT02", "PT03", "GB01", "VA01"])

    def test_versao_desconhecida_e_recusada(self):
        with self.assertRaises(ValidationError) as e:
            contrato(lambda d: d.update(contrato=2))
        self.assertIn("atualize o trilha-copy", str(e.exception))

    def test_campo_novo_do_briefing_e_ignorado(self):
        c = contrato(lambda d: d["personas"][0].update(campo_que_ainda_nao_existe="x"))
        self.assertEqual(c.personas[0].id, "profissional-travado")

    def test_provas_da_persona_vem_antes_das_neutras(self):
        c = contrato()
        self.assertEqual([p.id for p in c.provas_para("profissional-travado")],
                         ["renata", "carlos", "nota-google", "turma-6", "formados"])
        self.assertEqual([p.id for p in c.provas_para("viajante")], ["nota-google", "turma-6", "formados"])

    def test_urgencia_so_vale_se_real_e_no_prazo(self):
        def com(**u):
            return contrato(lambda d: d["ofertas"][1]["urgencia"].update(u)).oferta("conversacao-adultos")
        amanha, ontem = date.today() + timedelta(days=1), date.today() - timedelta(days=1)
        self.assertTrue(com(data=amanha.isoformat()).urgencia_valida())
        self.assertFalse(com(data=ontem.isoformat()).urgencia_valida())
        self.assertFalse(com(data=amanha.isoformat(), real=False).urgencia_valida())

    def test_escassez_precisa_de_evidencia(self):
        c = contrato(lambda d: d["ofertas"][1]["escassez"].update(evidencia=""))
        self.assertFalse(c.oferta("conversacao-adultos").escassez_valida())
        self.assertTrue(contrato().oferta("conversacao-adultos").escassez_valida())


class TestTexto(unittest.TestCase):
    def test_numeros_relevantes(self):
        self.assertEqual(tx.numeros_relevantes("Turma de até 6"), set())
        self.assertEqual(tx.numeros_relevantes("Nota 4,9 com 87 avaliações"), {"49", "87"})
        self.assertEqual(tx.numeros_relevantes("R$ 5 de desconto e 3% de taxa"), {"5", "3"})
        self.assertEqual(tx.numeros_relevantes("+1.200 formados"), {"1200"})

    def test_termo_inteiro_sem_acento(self):
        self.assertTrue(tx.contem_termo("Aula IMPERDÍVEL!", "imperdível"))
        self.assertTrue(tx.contem_termo("fluencia garantida em 3 meses", "Fluência garantida"))
        self.assertFalse(tx.contem_termo("Temos garantias", "garantia"))

    def test_silabas(self):
        self.assertEqual([tx.silabas(p) for p in ("casa", "que", "guerra", "aula", "inglês")], [2, 1, 2, 2, 2])

    def test_legibilidade_separa_facil_de_dificil(self):
        facil = "Você entende tudo. A frase não sai. Na aula você fala. Fala desde o início. A turma é pequena. " * 2
        dificil = ("A metodologia comunicacional internacionalizada proporciona desenvolvimento profissional "
                   "extraordinariamente significativo aos participantes interessados, considerando necessidades "
                   "corporativas contemporâneas, especificidades organizacionais e características individuais "
                   "relacionadas à comunicação interpessoal multilíngue.")
        self.assertIsNone(tx.legibilidade("Curto demais."))
        self.assertGreater(tx.legibilidade(facil), 75)
        self.assertLess(tx.legibilidade(dificil * 2), 50)

    def test_ritmo(self):
        self.assertIsNone(tx.variacao_ritmo("Uma. Duas frases. Três."))
        self.assertLess(tx.variacao_ritmo("Eu falo bem. Ela fala bem. Nós falamos bem. Eles falam bem."), 0.25)
        self.assertGreater(tx.variacao_ritmo("Pare. A frase não sai na reunião de segunda. Treine. "
                                             "Na turma de até seis adultos você fala a maior parte da aula."), 0.25)


class TestPacote(unittest.TestCase):
    def test_seis_ps_da_celula(self):
        pk = montar(contrato(), "PT01")
        self.assertEqual(list(pk.secoes), ["Pessoas", "Posicionamento", "Promessa", "Prova", "Prioridade", "Processo"])
        self.assertEqual(pk.tem_lacuna_critica(), [])
        self.assertTrue(contem(pk.secoes["Pessoas"], "Palavras dele"))
        self.assertTrue(contem(pk.secoes["Promessa"], "Desta célula: Na primeira aula"))
        self.assertTrue(pk.secoes["Prova"][0].startswith("[renata]"))  # a prova da persona vem primeiro

    def test_lacunas_mostram_o_que_falta_no_briefing(self):
        pk = montar(contrato(), "PT01")
        self.assertEqual(pk.lacunas["Posicionamento"], ["bastidores"])
        self.assertTrue(contem(pk.secoes["Posicionamento"], "sem a escada do \"e daí?\""))

    def test_persona_sem_dores_e_lacuna_critica(self):
        pk = montar(contrato(lambda d: d["personas"][0].update(dores=[])), "PT01")
        self.assertIn("persona com dores", pk.tem_lacuna_critica())

    def test_celula_inexistente(self):
        with self.assertRaises(ValueError):
            montar(contrato(), "XX99")

    def test_markdown_com_formato(self):
        c = contrato()
        md = em_markdown(montar(c, "GB01"), c, "google_rsa")
        for trecho in ("## Pessoas", "## Processo", "Intensidade: 2 de 5", "Nunca: imperdível",
                       "titulos: 3 a 15, até 30 caracteres (rígido)"):
            self.assertIn(trecho, md)


class TestRevisao(unittest.TestCase):
    def test_exemplos_sem_aviso(self):
        for caminho in (PT01, PT02, GB01):
            self.assertEqual(avisos(carregar_peca(caminho)), [], caminho.name)

    def test_termo_e_promessa_proibidos_bloqueiam(self):
        b = avisos(meta("Aula imperdível. Aprenda em 30 dias. Agende hoje."), nivel="bloqueia")
        self.assertTrue(contem(b, "termo proibido — \"imperdível\""))
        self.assertTrue(contem(b, "promessa proibida — \"aprenda em 30 dias\""))

    def test_atributo_pessoal_bloqueia_no_meta_e_alerta_no_google(self):
        frase = "Você está endividado e travado no inglês?"
        self.assertTrue(contem(avisos(meta(frase), nivel="bloqueia"), "atributo pessoal"))
        g = peca(GB01, lambda d: d["google"]["descricoes"].__setitem__(0, frase))
        self.assertTrue(contem(avisos(g, nivel="atencao"), "atributo pessoal"))

    def test_urgencia_sem_lastro_bloqueia(self):
        self.assertTrue(contem(avisos(meta("Últimas vagas na aula experimental. Agende hoje."), nivel="bloqueia"),
                               "publicidade enganosa"))

    def test_urgencia_com_lastro_passa(self):
        def oferta_com_prazo(d):
            d["ofertas"][1]["urgencia"]["data"] = (date.today() + timedelta(days=20)).isoformat()
        p = meta("Últimas vagas na turma noturna. Agende hoje.", oferta="conversacao-adultos")
        self.assertFalse(contem(avisos(p, contrato(oferta_com_prazo)), "publicidade enganosa"))

    def test_numero_sem_lastro(self):
        self.assertTrue(contem(avisos(meta("Mais de 5000 alunos falando. Agende hoje."), nivel="atencao"),
                               "sem lastro no briefing (5000)"))
        self.assertFalse(contem(avisos(meta("Nota 4,9 com 87 avaliações. Agende hoje.")), "sem lastro"))

    def test_prova_inexistente_bloqueia_e_de_outra_persona_alerta(self):
        self.assertTrue(contem(avisos(meta("Agende hoje.", provas=["inventada"]), nivel="bloqueia"),
                               "prova 'inventada' não está no contrato"))
        c = contrato(lambda d: d["provas"][3].update(personas=["viajante"]))
        self.assertTrue(contem(avisos(meta("Agende hoje.", provas=["renata"]), c, nivel="atencao"), "de outra persona"))

    def test_fala_de_si(self):
        a = avisos(meta("Nossa escola tem nossos professores e nossa sede. Somos líderes de mercado. Agende hoje."))
        self.assertTrue(contem(a, "fala mais de si"))
        self.assertTrue(contem(a, "autoelogio"))

    def test_intensidade_acima_da_combinada(self):
        self.assertTrue(contem(avisos(meta("INCRÍVEL! Corra para agendar hoje!")), "intensidade acima"))
        self.assertFalse(contem(avisos(meta("INCRÍVEL! Corra para agendar hoje!", intensidade=5)), "intensidade acima"))

    def test_concorrente_e_promessa_de_ganho(self):
        a = avisos(meta("Diferente da Rede Nacional A. Ganhe R$ 5.000 a mais com inglês. Agende hoje."), nivel="atencao")
        self.assertTrue(contem(a, "concorrente \"Rede Nacional A\""))
        self.assertTrue(contem(a, "promessa de ganho"))

    def test_sugestoes(self):
        p = meta("A melhor escola com qualidade de verdade. Venha conhecer.")
        s = avisos(p, nivel="sugestao")
        self.assertTrue(contem(s, "adjetivo sem fato"))
        self.assertTrue(contem(s, "chamada sem 'quando'"))
        self.assertTrue(contem(s, "frases literais da persona"))

    def test_leitura_dificil_e_ritmo(self):
        dificil = ("A metodologia comunicacional internacionalizada proporciona desenvolvimento profissional "
                   "extraordinariamente significativo aos participantes interessados, considerando necessidades "
                   "corporativas contemporâneas e especificidades organizacionais relacionadas à comunicação.")
        self.assertTrue(contem(avisos(meta(dificil + " " + dificil)), "leitura difícil"))
        monotono = " ".join(["Você fala na aula toda semana."] * 6)
        self.assertTrue(contem(avisos(meta(monotono)), "mesmo tamanho"))

    def test_limites_do_meta(self):
        gancho = "Você entende a reunião inteira, prepara a frase com calma, espera a sua vez de falar, o assunto muda " \
                 "e a frase fica guardada de novo."
        p = meta(gancho + " Agende hoje.")
        a = avisos(p, nivel="atencao")
        self.assertTrue(contem(a, "a primeira frase tem"))
        p = peca(PT01, lambda d: (d.pop("aprovacao"), d.update(estado="refinado"),
                                  d["meta"].update(titulos=["Um título longo demais para caber inteiro no feed"],
                                                   cta_botao="")))
        a = avisos(p, nivel="atencao")
        self.assertTrue(contem(a, "titulos[0] com 49 caracteres"))
        self.assertTrue(contem(a, "cta_botao vazio"))

    def test_limites_do_google(self):
        def mudar(d):
            d["google"]["titulos"] = ["Inglês para Adultos", "inglês para adultos", "Um título que passa de trinta"
                                      " caracteres"]
            d["google"]["palavras_chave"] = ["curso de espanhol"]
        g = peca(GB01, mudar)
        self.assertTrue(contem(avisos(g, nivel="bloqueia"), "titulos[2] com 40 caracteres; o limite é 30"))
        self.assertTrue(contem(avisos(g, nivel="atencao"), "titulos repetidos"))
        s = avisos(g, nivel="sugestao")
        self.assertTrue(contem(s, "com 10 ou mais"))
        self.assertTrue(contem(s, "nenhum título repete uma palavra-chave"))
        poucos = peca(GB01, lambda d: d["google"].update(titulos=["Inglês para Adultos"]))
        self.assertTrue(contem(avisos(poucos, nivel="bloqueia"), "o mínimo é 3"))

    def test_roteiro(self):
        def mudar(d):
            d["roteiro"]["cenas"][0]["tempo"] = "0-5"
            d["roteiro"]["cenas"][1]["fala"] = " ".join(["palavra"] * 40)
            d["roteiro"]["duracao_s"] = 45
            d["roteiro"]["cta"] = ""
            for cena in d["roteiro"]["cenas"]:
                cena["texto_tela"] = ""
        a = avisos(peca(PT02, mudar))
        for trecho in ("o gancho precisa resolver nos primeiros 3s", "as cenas somam 30s, mas a duração diz 45s",
                       "a fala da cena 3-12 tem 40 palavras", "roteiro sem chamada", "roteiro sem texto na tela"):
            self.assertTrue(contem(a, trecho), trecho)
        torto = peca(PT02, lambda d: d["roteiro"]["cenas"][0].update(tempo="início"))
        self.assertTrue(contem(avisos(torto), "use o tempo das cenas"))

    def test_integridade(self):
        mudou = peca(PT01, lambda d: d["meta"]["titulos"].append("Agende hoje"))
        self.assertTrue(contem(avisos(mudou, nivel="bloqueia"), "o texto mudou depois da aprovação"))
        outra = meta("Agende hoje.", codigo="ZZ99", persona="viajante", hipotese="h99")
        a = avisos(outra)
        self.assertTrue(contem(a, "célula ZZ99 não existe"))
        self.assertTrue(contem(avisos(meta("Agende hoje.", persona="viajante")), "diferente da célula"))
        self.assertTrue(contem(a, "hipótese 'h99' não existe"))


class TestPeca(Base):
    def test_bloco_do_formato(self):
        with self.assertRaises(ValidationError):
            peca(PT01, lambda d: d.update(google={"titulos": []}))
        p = Peca.model_validate({"id": "x", "codigo": "PT01", "formato": "google_rsa"})
        self.assertEqual(p.google.titulos, [])
        self.assertIsNone(p.meta)

    def test_aprovado_exige_aprovacao(self):
        with self.assertRaises(ValidationError):
            peca(PT01, lambda d: d.pop("aprovacao"))

    def test_assinatura_muda_com_o_texto(self):
        p = carregar_peca(PT01)
        self.assertTrue(p.aprovacao_valida())
        p.meta.descricoes[0] += "."
        self.assertFalse(p.aprovacao_valida())

    def test_arquivo_no_lugar_certo(self):
        errado = self.pasta / "pecas" / "PT02" / "pt01-meta-feed.yaml"
        shutil.copyfile(PT01, errado)
        with self.assertRaisesRegex(ErroPeca, "pecas/PT01/"):
            carregar_peca(errado)
        outro_nome = self.pasta / "pecas" / "PT01" / "outro.yaml"
        shutil.copyfile(PT01, outro_nome)
        with self.assertRaisesRegex(ErroPeca, "diferente do nome do arquivo"):
            carregar_peca(outro_nome)

    def test_registrar_estado_preserva_comentarios(self):
        caminho = self.arquivo("GB01", "gb01-google-rsa")
        p = carregar_peca(caminho)
        ap, _ = preparar_aprovacao(p, contrato(), "assessor", True, hoje=date(2026, 10, 6))
        registrar_estado(caminho, "aprovado", "revisado com o cliente", hoje=date(2026, 10, 6), aprovacao=ap)
        texto = caminho.read_text(encoding="utf-8")
        self.assertIn("# Peça gb01-google-rsa da célula GB01", texto)
        self.assertIn("# títulos e ganchos em volume", texto)
        self.assertIn("estado: aprovado\n", texto)
        self.assertLess(texto.index("aprovacao:"), texto.index("# 'historico'"))
        p = carregar_peca(caminho)
        self.assertTrue(p.aprovacao_valida())
        self.assertEqual((p.historico[-1].estado, p.historico[-1].nota), ("aprovado", "revisado com o cliente"))

    def test_registrar_estado_em_historico_vazio(self):
        caminho = self.arquivo("PT01", "pt01-meta-feed")
        texto = caminho.read_text(encoding="utf-8")
        texto = texto[:texto.index("aprovacao:")].replace("estado: aprovado", "estado: final") + "historico: []\n"
        caminho.write_text(texto, encoding="utf-8")
        registrar_estado(caminho, "final", hoje=date(2026, 10, 6))
        self.assertEqual([r.estado for r in carregar_peca(caminho).historico], ["final"])

    def test_registrar_estado_desfaz_se_historico_nao_for_a_ultima_chave(self):
        caminho = self.arquivo("PT02", "pt02-roteiro-video")
        texto = caminho.read_text(encoding="utf-8") + "ideia: \"outra\"\n"
        caminho.write_text(texto, encoding="utf-8")
        with self.assertRaisesRegex(ErroPeca, "última chave"):
            registrar_estado(caminho, "final")
        self.assertEqual(caminho.read_text(encoding="utf-8"), texto)


class TestFluxo(unittest.TestCase):
    def test_fundacao_pede_ideia_e_briefing_minimo(self):
        p = peca(PT01, lambda d: (d.pop("aprovacao"), d.update(estado="fundacao", ideia="")))
        self.assertTrue(contem(pendencias(p, contrato()), "a ideia grande"))
        c = contrato(lambda d: d["personas"][0].update(dores=[]))
        self.assertIn("briefing: persona com dores", pendencias(p, c))

    def test_rascunho_pede_volume(self):
        p = peca(PT01, lambda d: (d.pop("aprovacao"), d.update(estado="rascunho", rascunhos=["um", "dois"],
                                                                 gancho_tipo="inexistente")))
        falta = pendencias(p, contrato())
        self.assertTrue(contem(falta, f"{MINIMO_RASCUNHOS} rascunhos"))
        self.assertTrue(contem(falta, "fora do catálogo"))

    def test_refinado_pede_subtexto_prova_e_revisao_limpa(self):
        p = meta("Aula imperdível. Agende hoje.", provas=[], subtexto=[])
        falta = pendencias(p, contrato())
        self.assertTrue(contem(falta, "subtexto"))
        self.assertTrue(contem(falta, "prova usada na peça"))
        self.assertTrue(contem(falta, "revisão: meta.textos_principais[0]: termo proibido"))
        novo, _ = avancar(p, contrato())
        self.assertIsNone(novo)

    def test_avancar(self):
        self.assertEqual(avancar(carregar_peca(PT02), contrato()), ("final", []))
        self.assertEqual(avancar(carregar_peca(GB01), contrato()), (None, ["use o comando aprovar"]))
        self.assertEqual(avancar(carregar_peca(PT01), contrato()), (None, ["a peça já está aprovada"]))

    def test_aprovacao(self):
        p, c = carregar_peca(GB01), contrato()
        dia_final = p.data_do_estado("final")
        ap, problemas = preparar_aprovacao(p, c, "assessor", True, hoje=dia_final)
        self.assertIsNone(ap)
        self.assertTrue(contem(problemas, "durma sobre ela"))
        self.assertIsNotNone(preparar_aprovacao(p, c, "assessor", True, mesmo_dia=True, hoje=dia_final)[0])
        ap, _ = preparar_aprovacao(p, c, "assessor", True, hoje=dia_final + timedelta(days=1))
        self.assertEqual(ap.assinatura, p.assinatura_conteudo())
        ap, problemas = preparar_aprovacao(p, c, "assessor", False, hoje=dia_final + timedelta(days=1))
        self.assertTrue(contem(problemas, "teste do vendedor"))
        ap, problemas = preparar_aprovacao(carregar_peca(PT02), c, "assessor", True)
        self.assertTrue(contem(problemas, "só peça final pode ser aprovada"))


class TestExportar(Base):
    def test_so_aprovadas(self):
        escritos, recusadas = exportar(self.pasta, contrato(), self.tmp / "dist")
        self.assertEqual(recusadas, [])
        self.assertEqual([e.name for e in escritos], ["anuncios.csv"])
        with open(escritos[0], encoding="utf-8") as f:
            linhas = list(csv.DictReader(f))
        self.assertEqual({(x["peca"], x["utm_content"]) for x in linhas}, {("pt01-meta-feed", "PT01")})
        self.assertEqual([x["campo"] for x in linhas].count("texto_principal"), 2)
        self.assertTrue(all(int(x["caracteres"]) == len(x["texto"]) for x in linhas))
        self.assertEqual(linhas[-1]["campo"], "botao")

    def test_texto_alterado_depois_da_aprovacao_nao_sai(self):
        caminho = self.arquivo("PT01", "pt01-meta-feed")
        caminho.write_text(caminho.read_text(encoding="utf-8").replace("60 minutos, no seu nível", "60 minutos"),
                           encoding="utf-8")
        ok, recusadas = aprovadas(self.pasta)
        self.assertEqual(ok, [])
        self.assertEqual(recusadas, ["pt01-meta-feed: o texto mudou depois da aprovação"])

    def test_roteiro_aprovado_vira_markdown(self):
        caminho = self.arquivo("PT02", "pt02-roteiro-video")
        c = contrato()
        registrar_estado(caminho, "final", hoje=date(2026, 10, 5))
        ap, problemas = preparar_aprovacao(carregar_peca(caminho), c, "assessor", True, hoje=date(2026, 10, 6))
        self.assertEqual(problemas, [])
        registrar_estado(caminho, "aprovado", hoje=date(2026, 10, 6), aprovacao=ap)
        escritos, _ = exportar(self.pasta, c, self.tmp / "dist", codigo="PT02")
        self.assertEqual([e.name for e in escritos], ["pt02-roteiro-video.md"])
        md = escritos[0].read_text(encoding="utf-8")
        self.assertIn("| 0-3 | Entende tudo, mas a frase não sai?", md)
        self.assertIn("`PT02`", md)


class TestCLI(Base):
    def test_importar(self):
        rc, saida = rodar("importar", EXEMPLO / "copy.yaml", "--pasta", self.tmp / "clientes")
        self.assertEqual(rc, 0, saida)
        self.assertTrue((self.tmp / "clientes" / "_exemplo" / "copy.yaml").exists())
        ruim = self.tmp / "ruim.yaml"
        ruim.write_text((EXEMPLO / "copy.yaml").read_text(encoding="utf-8").replace("contrato: 1", "contrato: 9"),
                        encoding="utf-8")
        self.assertEqual(rodar("importar", ruim, "--pasta", self.tmp / "clientes")[0], 1)

    def test_nova_cria_peca_valida_com_dados_da_celula(self):
        rc, saida = rodar("nova", self.pasta, "VA01", "--formato", "meta_reels")
        self.assertEqual(rc, 0, saida)
        caminho = self.arquivo("VA01", "va01-meta-reels")
        p = carregar_peca(caminho)
        self.assertEqual((p.estado, p.persona, p.oferta, p.intensidade), ("fundacao", "viajante", "aula-experimental", 2))
        self.assertIn("# 'historico' é a última chave", caminho.read_text(encoding="utf-8"))
        self.assertEqual(rodar("nova", self.pasta, "VA01", "--formato", "meta_reels")[0], 1)  # já existe
        self.assertEqual(rodar("nova", self.pasta, "XX01", "--formato", "meta_feed")[0], 1)
        rc, saida = rodar("checklist", caminho)
        self.assertEqual(rc, 1)
        self.assertIn("a ideia grande em uma frase", saida)
        registrar_estado(caminho, "rascunho")  # o arquivo gerado aceita registro de estado
        self.assertEqual(carregar_peca(caminho).historico[-1].estado, "rascunho")

    def test_revisar_aprovar_exportar(self):
        rc, saida = rodar("revisar", self.pasta)
        self.assertEqual(rc, 0, saida)
        gb01 = self.arquivo("GB01", "gb01-google-rsa")
        rc, saida = rodar("aprovar", gb01, "--por", "assessor", "--mesmo-dia")
        self.assertEqual(rc, 1)
        self.assertIn("teste do vendedor", saida)
        self.assertEqual(rodar("aprovar", gb01, "--por", "assessor", "--teste-do-vendedor", "--mesmo-dia")[0], 0)
        rc, saida = rodar("exportar", self.pasta, "--saida", self.tmp / "dist")
        self.assertEqual(rc, 0, saida)
        with open(self.tmp / "dist" / "_exemplo" / "anuncios.csv", encoding="utf-8") as f:
            self.assertEqual({x["codigo"] for x in csv.DictReader(f)}, {"PT01", "GB01"})

    def test_revisar_sai_com_erro_se_algo_bloqueia(self):
        caminho = self.arquivo("PT02", "pt02-roteiro-video")
        caminho.write_text(caminho.read_text(encoding="utf-8").replace("É gratuita.", "É imperdível."), encoding="utf-8")
        rc, saida = rodar("revisar", caminho)
        self.assertEqual(rc, 1)
        self.assertIn("✗", saida)

    def test_avancar(self):
        caminho = self.arquivo("PT02", "pt02-roteiro-video")
        self.assertEqual(rodar("avancar", caminho, "--nota", "lido em voz alta")[0], 0)
        p = carregar_peca(caminho)
        self.assertEqual((p.estado, p.historico[-1].nota), ("final", "lido em voz alta"))
        self.assertEqual(rodar("avancar", caminho)[0], 1)  # de final só o aprovar sai

    def test_pacote_e_catalogos(self):
        rc, saida = rodar("pacote", self.pasta, "PT01", "--formato", "meta_feed")
        self.assertEqual(rc, 0)
        self.assertIn("# Pacote PT01", saida)
        rc, saida = rodar("ganchos")
        self.assertEqual(rc, 0)
        self.assertEqual(sum(1 for nome in GANCHOS if nome in saida), len(GANCHOS))

    def test_sem_contrato(self):
        (self.pasta / "copy.yaml").unlink()
        rc, saida = rodar("revisar", self.pasta)
        self.assertEqual(rc, 1)
        self.assertIn("importar", saida)


class TestReferencias(Base):
    def test_banco_do_repositorio_carrega(self):
        refs, erros = carregar_referencias(RAIZ / "referencias")
        self.assertEqual(erros, {})
        self.assertGreaterEqual(len(refs), 3)
        self.assertTrue(all(r.decupagem and r.por_que_funciona for r in refs))

    def test_erros(self):
        pasta = self.tmp / "refs"
        pasta.mkdir()
        base = {"id": "x", "titulo": "t", "fonte": "f", "formato": "meta", "texto": "t"}
        (pasta / "y.yaml").write_text(yaml.safe_dump(base), encoding="utf-8")
        (pasta / "z.yaml").write_text(yaml.safe_dump({**base, "id": "z", "gancho_tipo": "nenhum"}), encoding="utf-8")
        refs, erros = carregar_referencias(pasta)
        self.assertEqual(refs, [])
        self.assertIn("diferente do nome", erros["y.yaml"])
        self.assertIn("fora do catálogo", erros["z.yaml"])


if __name__ == "__main__":
    unittest.main()
