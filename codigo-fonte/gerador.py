import random
from tarefa import Tarefa

def sortear_dados(n, ingresso_max=8, tp_max=6, prio_max=5, com_recurso=False):
    dados = []
    for i in range(1, n + 1):
        ingresso = random.randint(0, ingresso_max)
        tp = random.randint(1, tp_max)
        prioridade = random.randint(1, prio_max)
        secao = None
        if com_recurso and random.random() < 0.5:
            inicio = random.randint(0, tp - 1)
            duracao = random.randint(1, tp - inicio)
            secao = (inicio, duracao)
        dados.append((i, ingresso, tp, prioridade, secao))
    return dados


def montar(dados):
    return [Tarefa(*d) for d in dados]
