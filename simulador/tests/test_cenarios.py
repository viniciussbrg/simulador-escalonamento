"""Cenarios de validacao da secao 4 do enunciado.

Os valores aqui sao normativos: reproduzi-los, com as convencoes da secao 3, e
o que demonstra que o simulador funciona.
"""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from control import gerador, politicas  # noqa: E402
from control.motor import (  # noqa: E402
    HERANCA,
    SEM_PROTOCOLO,
    TETO,
    ErroDeConfiguracao,
    Escalonador,
)
from model.tarefa import EntradaInvalida, Tarefa  # noqa: E402


def simular(tarefas, sigla, **parametros):
    return Escalonador(
        [t.clonar() for t in tarefas], politicas.criar(sigla), **parametros
    ).executar()


# ---------------------------------------------------------------------- #
CENARIO_AULA_5 = [
    Tarefa(1, 0, 5, 2),
    Tarefa(2, 0, 2, 3),
    Tarefa(3, 1, 4, 1),
    Tarefa(4, 3, 1, 4),
    Tarefa(5, 5, 2, 5),
]

CENARIO_AULA_6 = [
    Tarefa(1, 0, 6, 1, sc_inicio=1, sc_duracao=4),
    Tarefa(2, 4, 4, 2),
    Tarefa(3, 6, 3, 3),
    Tarefa(4, 2, 3, 4, sc_inicio=1, sc_duracao=1),
]

CENARIO_PRECO_DO_TETO = [
    Tarefa(1, 0, 6, 1, sc_inicio=1, sc_duracao=4),
    Tarefa(2, 2, 3, 2),
    Tarefa(4, 12, 2, 4, sc_inicio=0, sc_duracao=1),
]

CENARIO_INANICAO = [
    Tarefa(1, 0, 4, 1),
    Tarefa(2, 0, 2, 5),
    Tarefa(3, 2, 2, 5),
    Tarefa(4, 4, 2, 5),
    Tarefa(5, 6, 2, 5),
    Tarefa(6, 8, 2, 5),
]


class CenarioAula5(unittest.TestCase):
    """4.1 -- os seis algoritmos sem custo de troca."""

    ESPERADO = {
        "FCFS": (8.0, 5.2, 5.2, 5),
        "RR": (8.4, 5.6, 2.8, 8),
        "SJF": (5.8, 3.0, 3.0, 5),
        "SRTF": (5.4, 2.6, 2.4, 6),
        "PRIOc": (6.6, 3.8, 3.8, 5),
        "PRIOp": (5.6, 2.8, 2.2, 7),
    }

    def test_seis_algoritmos(self):
        for sigla, (tt, tw, primeira, trocas) in self.ESPERADO.items():
            with self.subTest(algoritmo=sigla):
                resultado = simular(CENARIO_AULA_5, sigla, quantum=2, custo_troca=0)
                self.assertAlmostEqual(resultado.tt_medio, tt, places=6)
                self.assertAlmostEqual(resultado.tw_medio, tw, places=6)
                self.assertAlmostEqual(resultado.primeira_execucao_media, primeira, places=6)
                self.assertEqual(resultado.trocas, trocas)

    def test_tw_e_tt_menos_tp(self):
        """C8 -- o tempo de espera engloba fila, suspensao e troca de contexto."""
        resultado = simular(CENARIO_AULA_5, "RR", quantum=2, custo_troca=0)
        for estado in resultado.estados:
            self.assertEqual(estado.tw, estado.tt - estado.tp)


class CenarioAula5ComCustoDeTroca(unittest.TestCase):
    """4.2 -- as mesmas cinco tarefas com ttc = 1 e tq = 4."""

    def test_fcfs(self):
        resultado = simular(CENARIO_AULA_5, "FCFS", custo_troca=1)
        self.assertAlmostEqual(resultado.tt_medio, 11.0, places=6)
        self.assertAlmostEqual(resultado.tw_medio, 8.2, places=6)

    def test_round_robin(self):
        resultado = simular(CENARIO_AULA_5, "RR", quantum=4, custo_troca=1)
        self.assertAlmostEqual(resultado.tt_medio, 13.4, places=6)
        self.assertAlmostEqual(resultado.tw_medio, 10.6, places=6)

    def test_eficiencia_so_existe_com_quantum(self):
        """R4 -- nos cinco algoritmos sem quantum E nao esta definida."""
        self.assertIsNone(simular(CENARIO_AULA_5, "FCFS", custo_troca=1).eficiencia)
        rr = simular(CENARIO_AULA_5, "RR", quantum=4, custo_troca=1)
        self.assertAlmostEqual(rr.eficiencia, 4 / 5, places=6)

    def test_eficiencia_independe_do_conjunto_de_tarefas(self):
        outro = [Tarefa(1, 0, 9, 1), Tarefa(2, 3, 2, 4)]
        um = simular(CENARIO_AULA_5, "RR", quantum=4, custo_troca=1).eficiencia
        dois = simular(outro, "RR", quantum=4, custo_troca=1).eficiencia
        self.assertEqual(um, dois)


class InversaoDePrioridades(unittest.TestCase):
    """4.3 -- quatro tarefas sob PRIOp, sem protocolo de correcao."""

    def setUp(self):
        self.resultado = simular(CENARIO_AULA_6, "PRIOp", protocolo=SEM_PROTOCOLO)

    def test_conclusoes(self):
        esperado = {1: 16, 2: 11, 3: 9, 4: 15}
        obtido = {e.identificador: e.conclusao for e in self.resultado.estados}
        self.assertEqual(obtido, esperado)

    def test_medias(self):
        self.assertAlmostEqual(self.resultado.tt_medio, 9.75, places=6)
        self.assertAlmostEqual(self.resultado.tw_medio, 5.75, places=6)

    def test_distingue_bloqueio_direto_de_inversao(self):
        """R5 -- o bloqueio direto e limitado pela secao critica; a inversao nao."""
        t4 = self.resultado.por_identificador(4)
        self.assertEqual(t4.bloqueio_direto, 3)
        self.assertEqual(t4.bloqueio_inversao, 7)
        # t2 e t3 sao as de prioridade intermediaria que sequer usam R
        self.assertEqual(t4.culpados_inversao, {2, 3})
        self.assertTrue(self.resultado.houve_inversao)


class HerancaDePrioridade(unittest.TestCase):
    """4.4 -- as mesmas quatro tarefas com o protocolo habilitado."""

    def setUp(self):
        self.resultado = simular(CENARIO_AULA_6, "PRIOp", protocolo=HERANCA)

    def test_conclusoes(self):
        esperado = {1: 16, 2: 15, 3: 11, 4: 8}
        obtido = {e.identificador: e.conclusao for e in self.resultado.estados}
        self.assertEqual(obtido, esperado)

    def test_medias(self):
        self.assertAlmostEqual(self.resultado.tt_medio, 9.50, places=6)
        self.assertAlmostEqual(self.resultado.tw_medio, 5.50, places=6)

    def test_bloqueio_de_t4_cai_de_10_para_3(self):
        t4 = self.resultado.por_identificador(4)
        self.assertEqual(t4.bloqueio_direto, 3)
        self.assertEqual(t4.bloqueio_inversao, 0)

    def test_heranca_e_revertida_na_liberacao(self):
        """R6 -- uma heranca que nao e desfeita quebra o resto da execucao."""
        for estado in self.resultado.estados:
            self.assertEqual(
                estado.prioridade_atual,
                estado.prioridade_base,
                f"t{estado.identificador} terminou com prioridade herdada",
            )


class TetoDePrioridade(unittest.TestCase):
    """4.5 -- mesmo cenario sob o protocolo de teto."""

    def setUp(self):
        self.resultado = simular(CENARIO_AULA_6, "PRIOp", protocolo=TETO)

    def test_teto_calculado_sobre_quem_declara_secao_critica(self):
        self.assertEqual(self.resultado.teto_recurso, 4)  # C9

    def test_medias_coincidem_com_a_heranca(self):
        self.assertAlmostEqual(self.resultado.tt_medio, 9.50, places=6)
        self.assertAlmostEqual(self.resultado.tw_medio, 5.50, places=6)

    def test_o_caminho_e_outro(self):
        self.assertEqual(
            self.resultado.sequencia(),
            "t1[0,5) t4[5,8) t3[8,11) t2[11,15) t1[15,16)",
        )

    def test_o_bloqueio_foi_prevenido_e_nao_encurtado(self):
        """A diferenca entre um protocolo reativo e um preventivo."""
        t4_teto = self.resultado.por_identificador(4)
        t4_heranca = simular(CENARIO_AULA_6, "PRIOp", protocolo=HERANCA).por_identificador(4)
        self.assertEqual(t4_teto.bloqueio_direto + t4_teto.bloqueio_inversao, 0)
        self.assertEqual(t4_heranca.bloqueio_direto, 3)


class PrecoDoTeto(unittest.TestCase):
    """4.5 (final) -- o custo do teto quando a disputa nunca chega a ocorrer.

    Verifica tambem o salto do relogio no intervalo ocioso entre 9 e 12.
    """

    def test_heranca(self):
        resultado = simular(CENARIO_PRECO_DO_TETO, "PRIOp", protocolo=HERANCA)
        self.assertEqual(
            resultado.sequencia(), "t1[0,2) t2[2,5) t1[5,9) t4[12,14)"
        )
        self.assertEqual(resultado.por_identificador(2).tw, 0)
        self.assertAlmostEqual(resultado.tw_medio, 1.00, places=6)

    def test_teto(self):
        resultado = simular(CENARIO_PRECO_DO_TETO, "PRIOp", protocolo=TETO)
        self.assertEqual(
            resultado.sequencia(), "t1[0,5) t2[5,8) t1[8,9) t4[12,14)"
        )
        self.assertEqual(resultado.por_identificador(2).tw, 3)
        self.assertAlmostEqual(resultado.tw_medio, 2.00, places=6)

    def test_relogio_salta_o_intervalo_ocioso(self):
        resultado = simular(CENARIO_PRECO_DO_TETO, "PRIOp", protocolo=HERANCA)
        self.assertEqual(resultado.por_identificador(4).primeira_execucao, 12)
        self.assertEqual(resultado.instante_final, 14)


class InanicaoEEnvelhecimento(unittest.TestCase):
    """4.6 -- seis tarefas sob prioridade cooperativa."""

    ESPERADO = {
        0: ("t2[0,2) t3[2,4) t4[4,6) t5[6,8) t6[8,10) t1[10,14)", 10, 1.67),
        1: ("t2[0,2) t3[2,4) t1[4,8) t4[8,10) t5[10,12) t6[12,14)", 4, 2.67),
        2: ("t2[0,2) t1[2,6) t3[6,8) t4[8,10) t5[10,12) t6[12,14)", 2, 3.00),
    }

    def test_envelhecimento(self):
        for alfa, (sequencia, tw_t1, tw_medio) in self.ESPERADO.items():
            with self.subTest(alfa=alfa):
                resultado = simular(CENARIO_INANICAO, "PRIOc", alfa=alfa)
                self.assertEqual(resultado.sequencia(), sequencia)
                self.assertEqual(resultado.por_identificador(1).tw, tw_t1)
                self.assertAlmostEqual(resultado.tw_medio, tw_medio, places=2)

    def test_envelhecimento_e_uma_troca_nao_um_ganho(self):
        sem = simular(CENARIO_INANICAO, "PRIOc", alfa=0)
        com = simular(CENARIO_INANICAO, "PRIOc", alfa=2)
        self.assertLess(com.por_identificador(1).tw, sem.por_identificador(1).tw)
        self.assertGreater(com.tw_medio, sem.tw_medio)


class LoteDeCenarios(unittest.TestCase):
    """4.7 -- os numeros nao devem ser reproduzidos; a ordenacao, sim."""

    def test_ordenacao_se_estabiliza(self):
        resumo = gerador.rodar_lote(
            amostras=60, quantidade=5, ingresso_max=8, duracao_max=6,
            prioridade_max=5, quantum=2, custo_troca=0,
            aleatorio=random.Random(20260915),
        )
        menor_tw = min(politicas.ORDEM, key=lambda s: resumo[s]["tw"])
        menor_primeira = min(politicas.ORDEM, key=lambda s: resumo[s]["primeira"])
        self.assertEqual(menor_tw, "SRTF")
        self.assertEqual(menor_primeira, "RR")

    def test_ordenacao_em_varias_execucoes_independentes(self):
        for tentativa in range(5):
            with self.subTest(tentativa=tentativa):
                resumo = gerador.rodar_lote(amostras=40, quantidade=5)
                self.assertEqual(min(politicas.ORDEM, key=lambda s: resumo[s]["tw"]), "SRTF")
                self.assertEqual(
                    min(politicas.ORDEM, key=lambda s: resumo[s]["primeira"]), "RR"
                )


if __name__ == "__main__":
    unittest.main()
