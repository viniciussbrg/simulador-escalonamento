"""As seis politicas de escalonamento (R1).

Uma politica responde a uma unica pergunta: qual tarefa pronta recebe o
processador. Todo o resto -- relogio, fila, troca de contexto, recurso,
envelhecimento, metricas -- e do mecanismo (control/motor.py).

Por isso cada politica cabe em poucas linhas: e o metodo chave(), que devolve
uma tupla onde MENOR e melhor. O desempate por (ingresso, identificador) da
convencao C3 e a cauda de toda tupla.
"""

from typing import List, Optional


class Politica:
    nome = "?"
    sigla = "?"
    usa_quantum = False
    preemptiva = False  # reavalia a escolha a cada unidade de tempo

    def chave(self, estado, instante, motor):
        raise NotImplementedError

    # a maioria das politicas nao guarda estado nenhum
    def ingressar(self, estado): ...
    def retirar(self, estado): ...
    def devolver(self, estado): ...
    def concluir(self, estado): ...


class FCFS(Politica):
    nome = "First-Come, First-Served"
    sigla = "FCFS"

    def chave(self, estado, instante, motor):
        return (estado.ingresso, estado.identificador)


class SJF(Politica):
    nome = "Shortest Job First"
    sigla = "SJF"

    def chave(self, estado, instante, motor):
        return (estado.tp, estado.ingresso, estado.identificador)


class SRTF(Politica):
    nome = "Shortest Remaining Time First"
    sigla = "SRTF"
    preemptiva = True

    def chave(self, estado, instante, motor):
        return (estado.restante, estado.ingresso, estado.identificador)


class PrioridadeCooperativa(Politica):
    nome = "Prioridade cooperativa"
    sigla = "PRIOc"

    def chave(self, estado, instante, motor):
        # C2: valor maior significa prioridade mais alta, logo o sinal negativo.
        return (-motor.prioridade_efetiva(estado, instante, None),
                estado.ingresso, estado.identificador)


class PrioridadePreemptiva(PrioridadeCooperativa):
    nome = "Prioridade preemptiva"
    sigla = "PRIOp"
    preemptiva = True


class RoundRobin(Politica):
    """Unica politica com estado: a fila circular.

    A ordem da fila ja resolve a escolha, entao chave() devolve apenas a
    posicao. A convencao C6 -- quem esgota o quantum volta a cauda depois de
    quem ingressou no mesmo instante -- e consequencia de o mecanismo chamar
    ingressar() antes de devolver().
    """

    nome = "Round-Robin"
    sigla = "RR"
    usa_quantum = True
    preemptiva = False  # a preempcao do RR e por quantum, nunca por criterio

    def __init__(self) -> None:
        self.fila: List = []

    def chave(self, estado, instante, motor):
        return (self.fila.index(estado),) if estado in self.fila else (len(self.fila),)

    def ingressar(self, estado):
        if estado not in self.fila:
            self.fila.append(estado)

    def retirar(self, estado):
        if estado in self.fila:
            self.fila.remove(estado)

    def devolver(self, estado):
        if not estado.concluida and not estado.suspensa and estado not in self.fila:
            self.fila.append(estado)

    def concluir(self, estado):
        self.retirar(estado)


ALGORITMOS = {
    "FCFS": FCFS,
    "SJF": SJF,
    "SRTF": SRTF,
    "RR": RoundRobin,
    "PRIOc": PrioridadeCooperativa,
    "PRIOp": PrioridadePreemptiva,
}

ORDEM = ["FCFS", "RR", "SJF", "SRTF", "PRIOc", "PRIOp"]


def criar(sigla: str) -> Politica:
    try:
        return ALGORITMOS[sigla]()
    except KeyError:
        raise ValueError(f"Algoritmo desconhecido: {sigla}. Use um de {list(ALGORITMOS)}.")
