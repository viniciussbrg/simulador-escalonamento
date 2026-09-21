"""Validacao de entrada (R2), configuracao do escalonador (R4) e persistencia."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from control import politicas  # noqa: E402
from control.motor import ErroDeConfiguracao, Escalonador  # noqa: E402
from model import cenario as persistencia  # noqa: E402
from model.tarefa import EntradaInvalida, Tarefa  # noqa: E402


class ValidacaoDeTarefa(unittest.TestCase):
    def test_ingresso_negativo(self):
        with self.assertRaises(EntradaInvalida):
            Tarefa(1, -1, 4, 2)

    def test_duracao_nao_positiva(self):
        with self.assertRaises(EntradaInvalida):
            Tarefa(1, 0, 0, 2)

    def test_secao_critica_precisa_caber_na_duracao(self):
        with self.assertRaises(EntradaInvalida):
            Tarefa(1, 0, 4, 2, sc_inicio=2, sc_duracao=3)

    def test_secao_critica_no_limite_e_aceita(self):
        tarefa = Tarefa(1, 0, 4, 2, sc_inicio=1, sc_duracao=3)
        self.assertEqual(tarefa.descricao_sc(), "[1, 4)")

    def test_duracao_de_secao_critica_sem_inicio(self):
        with self.assertRaises(EntradaInvalida):
            Tarefa(1, 0, 4, 2, sc_inicio=None, sc_duracao=2)


class ConfiguracaoDoEscalonador(unittest.TestCase):
    TAREFAS = [Tarefa(1, 0, 4, 1), Tarefa(2, 1, 3, 2)]

    def test_quantum_precisa_ser_maior_que_o_custo_da_troca(self):
        with self.assertRaises(ErroDeConfiguracao):
            Escalonador(self.TAREFAS, politicas.criar("RR"), quantum=2, custo_troca=2)
        with self.assertRaises(ErroDeConfiguracao):
            Escalonador(self.TAREFAS, politicas.criar("RR"), quantum=1, custo_troca=3)

    def test_quantum_maior_que_o_custo_e_aceito(self):
        resultado = Escalonador(
            [t.clonar() for t in self.TAREFAS], politicas.criar("RR"),
            quantum=3, custo_troca=2,
        ).executar()
        self.assertAlmostEqual(resultado.eficiencia, 3 / 5, places=6)

    def test_custo_de_troca_negativo(self):
        with self.assertRaises(ErroDeConfiguracao):
            Escalonador(self.TAREFAS, politicas.criar("FCFS"), custo_troca=-1)

    def test_sem_tarefas(self):
        with self.assertRaises(ErroDeConfiguracao):
            Escalonador([], politicas.criar("FCFS"))

    def test_algoritmo_desconhecido(self):
        with self.assertRaises(ValueError):
            politicas.criar("XYZ")


class Persistencia(unittest.TestCase):
    """R2 -- um sorteio interessante nao pode se perder."""

    def test_ida_e_volta(self):
        original = [
            Tarefa(1, 0, 6, 1, sc_inicio=1, sc_duracao=4),
            Tarefa(2, 4, 4, 2),
        ]
        parametros = {"quantum": 2, "custo_troca": 1, "protocolo": "heranca"}
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "cenario.json")
            persistencia.gravar(caminho, original, parametros, "teste")
            recarregado, devolvidos, descricao = persistencia.carregar(caminho)

        self.assertEqual(
            [t.para_dicionario() for t in recarregado],
            [t.para_dicionario() for t in original],
        )
        self.assertEqual(devolvidos, parametros)
        self.assertEqual(descricao, "teste")

    def test_arquivo_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "ruim.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("isto nao e json")
            with self.assertRaises(EntradaInvalida):
                persistencia.carregar(caminho)

    def test_cenarios_de_exemplo_carregam(self):
        pasta = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cenarios"
        )
        arquivos = [a for a in os.listdir(pasta) if a.endswith(".json")]
        self.assertGreaterEqual(len(arquivos), 3)
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo):
                tarefas, _, _ = persistencia.carregar(os.path.join(pasta, arquivo))
                self.assertTrue(tarefas)


class SeparacaoPoliticaMecanismo(unittest.TestCase):
    """O simulador tem um unico laco; as politicas apenas escolhem."""

    def test_toda_politica_implementa_apenas_a_escolha(self):
        tarefas = [Tarefa(1, 0, 3, 1), Tarefa(2, 0, 2, 2)]
        for sigla in politicas.ORDEM:
            with self.subTest(algoritmo=sigla):
                resultado = Escalonador(
                    [t.clonar() for t in tarefas], politicas.criar(sigla), quantum=2
                ).executar()
                self.assertTrue(all(e.concluida for e in resultado.estados))
                self.assertEqual(
                    sum(e.tp for e in resultado.estados),
                    sum(s.fim - s.inicio for s in resultado.execucoes()),
                )


if __name__ == "__main__":
    unittest.main()
