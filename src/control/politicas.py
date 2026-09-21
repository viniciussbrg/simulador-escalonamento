from dataclasses import dataclass
from typing import Callable

from src.control.algoritmos._base import chave_desempate
from src.control.algoritmos.nomes import Algoritmo


@dataclass(frozen=True)
class Politica:
    algoritmo: Algoritmo
    chave_selecao: Callable
    preemptivo: bool
    usa_quantum: bool = False
    suporta_envelhecimento: bool = False
    suporta_recursos: bool = False


def _chave_sjf(p, tempo_atual=None):
    return (p.duracao, *chave_desempate(p))


def _chave_srtf(p, tempo_atual=None):
    return (p.tempo_restante, *chave_desempate(p))


def _chave_prioridade(p, tempo_atual=None):
    return (-p.prioridade.numero, *chave_desempate(p))


def _momento_referencia_envelhecimento(p):
    execucoes = [periodo for periodo in p.processamentos if periodo.tipo == "Execução"]
    return execucoes[-1].inicio if execucoes else p.chegada


def chave_prioridade_com_envelhecimento(alfa):
    def chave(p, tempo_atual):
        referencia = _momento_referencia_envelhecimento(p)
        prioridade_efetiva = p.prioridade.numero + alfa * (tempo_atual - referencia)
        return (-prioridade_efetiva, *chave_desempate(p))

    return chave


POLITICAS = {
    Algoritmo.FCFS: Politica(Algoritmo.FCFS, chave_desempate, preemptivo=False),
    Algoritmo.SJF: Politica(Algoritmo.SJF, _chave_sjf, preemptivo=False),
    Algoritmo.SRTF: Politica(Algoritmo.SRTF, _chave_srtf, preemptivo=True),
    Algoritmo.ROUND_ROBIN: Politica(Algoritmo.ROUND_ROBIN, chave_desempate, preemptivo=True, usa_quantum=True),
    Algoritmo.PRIORIDADE_COOPERATIVO: Politica(
        Algoritmo.PRIORIDADE_COOPERATIVO, _chave_prioridade, preemptivo=False, suporta_envelhecimento=True
    ),
    Algoritmo.PRIORIDADE_PREEMPTIVO: Politica(
        Algoritmo.PRIORIDADE_PREEMPTIVO, _chave_prioridade, preemptivo=True, suporta_recursos=True
    ),
}
