"""Gerador de cenarios e lote comparativo (R9).

O mesmo gerador serve a dois usos: sortear um cenario unico para observar em
detalhe e sortear um lote de cenarios para comparar os seis algoritmos pelas
medias de tt e tw.

O sorteio e livre e nao se repete: os valores absolutos mudam de uma execucao
para outra. O que precisa se manter e a ORDENACAO entre os algoritmos.
"""

import random
from typing import Dict, List, Optional

from control import politicas
from control.motor import Escalonador, SEM_PROTOCOLO
from model.tarefa import Tarefa


def sortear_cenario(
    quantidade: int,
    ingresso_max: int = 8,
    duracao_max: int = 6,
    prioridade_max: int = 5,
    proporcao_com_recurso: float = 0.0,
    aleatorio: Optional[random.Random] = None,
) -> List[Tarefa]:
    """Sorteia um conjunto de tarefas.

    proporcao_com_recurso > 0 faz parte das tarefas declararem secao critica,
    o que permite sortear cenarios de disputa pelo recurso R.
    """
    if quantidade < 1:
        raise ValueError("O numero de tarefas precisa ser pelo menos 1.")
    rnd = aleatorio or random.Random()

    tarefas: List[Tarefa] = []
    for identificador in range(1, quantidade + 1):
        tp = rnd.randint(1, max(1, duracao_max))
        sc_inicio = None
        sc_duracao = 0
        if tp >= 2 and rnd.random() < proporcao_com_recurso:
            sc_duracao = rnd.randint(1, tp - 1)
            sc_inicio = rnd.randint(0, tp - sc_duracao)
        tarefas.append(
            Tarefa(
                identificador=identificador,
                ingresso=rnd.randint(0, max(0, ingresso_max)),
                tp=tp,
                prioridade=rnd.randint(1, max(1, prioridade_max)),
                sc_inicio=sc_inicio,
                sc_duracao=sc_duracao,
            )
        )
    return tarefas


def comparar(
    tarefas: List[Tarefa],
    quantum: int = 2,
    custo_troca: int = 0,
    alfa: int = 0,
    protocolo: str = SEM_PROTOCOLO,
) -> Dict[str, Dict[str, float]]:
    """Roda os seis algoritmos sobre o MESMO conjunto de tarefas."""
    resumo: Dict[str, Dict[str, float]] = {}
    for sigla in politicas.ORDEM:
        resultado = Escalonador(
            [t.clonar() for t in tarefas],
            politicas.criar(sigla),
            quantum=quantum,
            custo_troca=custo_troca,
            alfa=alfa,
            protocolo=protocolo,
        ).executar()
        resumo[sigla] = {
            "tt": resultado.tt_medio,
            "tw": resultado.tw_medio,
            "primeira": resultado.primeira_execucao_media,
            "trocas": float(resultado.trocas),
        }
    return resumo


def rodar_lote(
    amostras: int = 50,
    quantidade: int = 5,
    ingresso_max: int = 8,
    duracao_max: int = 6,
    prioridade_max: int = 5,
    quantum: int = 2,
    custo_troca: int = 0,
    aleatorio: Optional[random.Random] = None,
) -> Dict[str, Dict[str, float]]:
    """Medias dos seis algoritmos sobre um lote de cenarios sorteados."""
    if amostras < 1:
        raise ValueError("O lote precisa de pelo menos um cenario.")
    rnd = aleatorio or random.Random()

    acumulado = {s: {"tt": 0.0, "tw": 0.0, "primeira": 0.0, "trocas": 0.0}
                 for s in politicas.ORDEM}
    for _ in range(amostras):
        tarefas = sortear_cenario(
            quantidade, ingresso_max, duracao_max, prioridade_max, aleatorio=rnd
        )
        parcial = comparar(tarefas, quantum=quantum, custo_troca=custo_troca)
        for sigla, valores in parcial.items():
            for chave, valor in valores.items():
                acumulado[sigla][chave] += valor

    return {
        sigla: {chave: valor / amostras for chave, valor in valores.items()}
        for sigla, valores in acumulado.items()
    }
