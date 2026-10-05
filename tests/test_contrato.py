"""Contrato com o Trilha-briefing: o que ele exporta carrega aqui, e o exemplo versionado está em dia.

Os repositórios não dependem um do outro, então este teste só roda com o Trilha-briefing ao lado:

    PYTHONPATH=../Trilha-briefing python -m unittest tests.test_contrato -v

Sem ele, os testes são pulados (a CI deste repositório não tem acesso ao outro).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from trilha_copy.contrato import VERSOES_SUPORTADAS, carregar_contrato
from trilha_copy.pacote import montar
from trilha_copy.peca import carregar_peca, pecas_da_pasta
from trilha_copy.revisao import bloqueantes

try:
    import trilha_briefing
    from trilha_briefing.esquema import carregar_cliente
    from trilha_briefing.exportar import VERSAO_CONTRATO_COPY, exportar_copy
    TEM_BRIEFING = True
except ImportError:
    TEM_BRIEFING = False

EXEMPLO = Path(__file__).parent.parent / "clientes" / "_exemplo"


@unittest.skipUnless(TEM_BRIEFING, "Trilha-briefing fora do PYTHONPATH")
class TestContrato(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        exemplo_briefing = Path(trilha_briefing.__file__).parent.parent / "clientes" / "_exemplo"
        self.arquivo = exportar_copy(carregar_cliente(exemplo_briefing), self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_versao_do_briefing_e_suportada(self):
        self.assertIn(VERSAO_CONTRATO_COPY, VERSOES_SUPORTADAS)

    def test_exportacao_do_briefing_carrega_e_monta_todas_as_celulas(self):
        c = carregar_contrato(self.arquivo)
        for celula in c.grade:
            montar(c, celula.codigo)

    def test_exemplo_versionado_esta_em_dia(self):
        """Se falhar: exporte de novo no briefing e copie para clientes/_exemplo/copy.yaml."""
        deles = yaml.safe_load(self.arquivo.read_text(encoding="utf-8"))
        nosso = yaml.safe_load((EXEMPLO / "copy.yaml").read_text(encoding="utf-8"))
        deles.pop("gerado_em"), nosso.pop("gerado_em")
        self.assertEqual(deles, nosso)

    def test_pecas_do_exemplo_passam_com_o_contrato_novo(self):
        c = carregar_contrato(self.arquivo)
        for caminho in pecas_da_pasta(EXEMPLO):
            self.assertEqual(bloqueantes(carregar_peca(caminho), c), [], caminho.name)
