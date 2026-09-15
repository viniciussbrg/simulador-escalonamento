import tempfile
import unittest
from pathlib import Path

from simulador import SimulacaoErro, TarefaEntrada, simular
from simulador.cenarios import (
    carregar_cenario,
    cenario_aula5,
    cenario_inanicao,
    cenario_inversao_prioridade,
    cenario_teto_sem_disputa,
    comparar_lote,
    salvar_cenario,
)


def metricas_por_id(resultado):
    return {metrica.id: metrica for metrica in resultado.metricas}


class CenariosOficiaisTest(unittest.TestCase):
    def assert_medias(self, resultado, tt, tw, primeira=None):
        self.assertAlmostEqual(resultado.medias["tt"], tt, places=2)
        self.assertAlmostEqual(resultado.medias["tw"], tw, places=2)
        if primeira is not None:
            self.assertAlmostEqual(resultado.medias["primeira_execucao"], primeira, places=2)

    def test_aula5_seis_algoritmos(self):
        esperados = {
            "FCFS": (8.0, 5.2, 5.2, 5),
            "RR": (8.4, 5.6, 2.8, 8),
            "SJF": (5.8, 3.0, 3.0, 5),
            "SRTF": (5.4, 2.6, 2.4, 6),
            "PRIOc": (6.6, 3.8, 3.8, 5),
            "PRIOp": (5.6, 2.8, 2.2, 7),
        }
        for algoritmo, (tt, tw, primeira, trocas) in esperados.items():
            with self.subTest(algoritmo=algoritmo):
                resultado = simular(cenario_aula5(), algoritmo, quantum=2, ttc=0)
                self.assert_medias(resultado, tt, tw, primeira)
                self.assertEqual(resultado.trocas_contexto, trocas)

    def test_aula5_com_custo_de_troca(self):
        fcfs = simular(cenario_aula5(), "FCFS", quantum=4, ttc=1)
        rr = simular(cenario_aula5(), "RR", quantum=4, ttc=1)

        self.assert_medias(fcfs, 11.0, 8.2)
        self.assertIsNone(fcfs.eficiencia)
        self.assert_medias(rr, 13.4, 10.6)
        self.assertAlmostEqual(rr.eficiencia, 0.8, places=3)

    def test_inversao_de_prioridade_sem_mecanismo(self):
        resultado = simular(cenario_inversao_prioridade(), "PRIOp", ttc=0)
        metricas = metricas_por_id(resultado)

        self.assert_medias(resultado, 9.75, 5.75)
        self.assertEqual(
            [(metricas[i].conclusao, metricas[i].tt, metricas[i].tw) for i in [1, 2, 3, 4]],
            [(16, 16, 10), (11, 7, 3), (9, 3, 0), (15, 13, 10)],
        )
        self.assertEqual([(i.inicio, i.fim) for i in resultado.bloqueios_por_tarefa[4]], [(3, 13)])

    def test_heranca_de_prioridade(self):
        resultado = simular(
            cenario_inversao_prioridade(),
            "PRIOp",
            ttc=0,
            protocolo_prioridade="heranca",
        )
        metricas = metricas_por_id(resultado)

        self.assert_medias(resultado, 9.50, 5.50)
        self.assertEqual(
            [(metricas[i].conclusao, metricas[i].tt, metricas[i].tw) for i in [1, 2, 3, 4]],
            [(16, 16, 10), (15, 11, 7), (11, 5, 2), (8, 6, 3)],
        )
        self.assertEqual([(i.inicio, i.fim) for i in resultado.bloqueios_por_tarefa[4]], [(3, 6)])

    def test_teto_de_prioridade(self):
        resultado = simular(
            cenario_inversao_prioridade(),
            "PRIOp",
            ttc=0,
            protocolo_prioridade="teto",
        )

        self.assert_medias(resultado, 9.50, 5.50)
        self.assertEqual(
            resultado.sequencia_execucao(),
            [(1, 0, 5), (4, 5, 8), (3, 8, 11), (2, 11, 15), (1, 15, 16)],
        )
        self.assertEqual(resultado.teto_recurso, 4)
        self.assertEqual(resultado.bloqueios_por_tarefa[4], [])

    def test_teto_tem_custo_quando_nao_ha_disputa(self):
        heranca = simular(
            cenario_teto_sem_disputa(),
            "PRIOp",
            ttc=0,
            protocolo_prioridade="heranca",
        )
        teto = simular(
            cenario_teto_sem_disputa(),
            "PRIOp",
            ttc=0,
            protocolo_prioridade="teto",
        )

        self.assertEqual(
            heranca.sequencia_execucao(),
            [(1, 0, 2), (2, 2, 5), (1, 5, 9), (4, 12, 14)],
        )
        self.assertEqual(
            teto.sequencia_execucao(),
            [(1, 0, 5), (2, 5, 8), (1, 8, 9), (4, 12, 14)],
        )
        self.assertEqual(metricas_por_id(heranca)[2].tw, 0)
        self.assertEqual(metricas_por_id(teto)[2].tw, 3)
        self.assertAlmostEqual(heranca.medias["tw"], 1.0)
        self.assertAlmostEqual(teto.medias["tw"], 2.0)

    def test_inanicao_e_envelhecimento(self):
        sem = simular(cenario_inanicao(), "PRIOc", ttc=0)
        alpha1 = simular(cenario_inanicao(), "PRIOc", ttc=0, envelhecimento=True, alpha=1)
        alpha2 = simular(cenario_inanicao(), "PRIOc", ttc=0, envelhecimento=True, alpha=2)

        self.assertEqual(sem.sequencia_execucao()[0:6], [(2, 0, 2), (3, 2, 4), (4, 4, 6), (5, 6, 8), (6, 8, 10), (1, 10, 14)])
        self.assertEqual(alpha1.sequencia_execucao(), [(2, 0, 2), (3, 2, 4), (1, 4, 8), (4, 8, 10), (5, 10, 12), (6, 12, 14)])
        self.assertEqual(alpha2.sequencia_execucao(), [(2, 0, 2), (1, 2, 6), (3, 6, 8), (4, 8, 10), (5, 10, 12), (6, 12, 14)])
        self.assertEqual(metricas_por_id(sem)[1].tw, 10)
        self.assertEqual(metricas_por_id(alpha1)[1].tw, 4)
        self.assertEqual(metricas_por_id(alpha2)[1].tw, 2)
        self.assertAlmostEqual(sem.medias["tw"], 1.67, places=2)
        self.assertAlmostEqual(alpha1.medias["tw"], 2.67, places=2)
        self.assertAlmostEqual(alpha2.medias["tw"], 3.00, places=2)


class ValidacaoPersistenciaELoteTest(unittest.TestCase):
    def test_recusa_entradas_invalidas(self):
        with self.assertRaises(SimulacaoErro):
            simular([TarefaEntrada(1, -1, 3, 1)], "FCFS")
        with self.assertRaises(SimulacaoErro):
            simular([TarefaEntrada(1, 0, 0, 1)], "FCFS")
        with self.assertRaises(SimulacaoErro):
            simular([TarefaEntrada(1, 0, 4, 1, 3, 2)], "FCFS")
        with self.assertRaises(SimulacaoErro):
            simular(cenario_aula5(), "RR", quantum=1, ttc=1)

    def test_salva_e_carrega_cenario(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "cenario.json"
            tarefas = cenario_inversao_prioridade()
            salvar_cenario(caminho, tarefas)
            self.assertEqual(carregar_cenario(caminho), tarefas)

    def test_lote_retorna_medias_dos_seis_algoritmos(self):
        linhas = comparar_lote(quantidade_cenarios=12, quantidade_tarefas=5, semente=123)
        self.assertEqual({linha["algoritmo"] for linha in linhas}, {"FCFS", "SJF", "SRTF", "RR", "PRIOc", "PRIOp"})
        for linha in linhas:
            self.assertGreaterEqual(linha["tt"], linha["tw"])
            self.assertGreaterEqual(linha["primeira_execucao"], 0)


if __name__ == "__main__":
    unittest.main()
