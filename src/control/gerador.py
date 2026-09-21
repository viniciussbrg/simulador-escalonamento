import copy
import random
from dataclasses import dataclass

from src.control.algoritmos.nomes import Algoritmo
from src.control.motor import simular
from src.control.politicas import POLITICAS
from src.model.prioridade import Prioridade
from src.model.processo import Processo


@dataclass
class Faixas:

    chegada: tuple[int, int] = (0, 8)
    duracao: tuple[int, int] = (1, 6)
    prioridade: tuple[int, int] = (1, 5)


ALGORITMOS_BASE = (
    Algoritmo.FCFS,
    Algoritmo.SJF,
    Algoritmo.SRTF,
    Algoritmo.ROUND_ROBIN,
    Algoritmo.PRIORIDADE_COOPERATIVO,
    Algoritmo.PRIORIDADE_PREEMPTIVO,
)


def sortear_tarefas(n: int, faixas: Faixas | None = None) -> list[Processo]:
    if n <= 0:
        raise ValueError("O número de tarefas deve ser maior que zero.")

    faixas = faixas or Faixas()

    return [
        Processo(
            id=i,
            chegada=random.randint(*faixas.chegada),
            duracao=random.randint(*faixas.duracao),
            prioridade=Prioridade(random.randint(*faixas.prioridade)),
        )
        for i in range(1, n + 1)
    ]


def rodar_lote(
    n_cenarios: int,
    n_tarefas: int,
    faixas: Faixas | None,
    ctx_time: float,
    quantum: int,
) -> dict[Algoritmo, dict[str, float]]:
    if n_cenarios <= 0:
        raise ValueError("O número de cenários deve ser maior que zero.")

    acumulado = {alg: {"T": 0.0, "T_w": 0.0, "primeira_execucao": 0.0} for alg in ALGORITMOS_BASE}

    for _ in range(n_cenarios):
        tarefas_base = sortear_tarefas(n_tarefas, faixas)

        for alg in ALGORITMOS_BASE:
            tarefas = copy.deepcopy(tarefas_base)
            q = quantum if alg == Algoritmo.ROUND_ROBIN else None

            media_espera, media_execucao, _ = simular(tarefas, POLITICAS[alg], q, ctx_time)
            media_1exec = sum(p.get_tempo_ate_primeira_execucao() for p in tarefas) / len(tarefas)

            acumulado[alg]["T"] += media_execucao
            acumulado[alg]["T_w"] += media_espera
            acumulado[alg]["primeira_execucao"] += media_1exec

    return {
        alg: {chave: total / n_cenarios for chave, total in valores.items()}
        for alg, valores in acumulado.items()
    }
