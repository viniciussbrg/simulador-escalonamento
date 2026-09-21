import copy

from src.control.algoritmos.nomes import Algoritmo
from src.control.motor import simular as simular_motor
from src.control.politicas import POLITICAS

_DISPATCH = {
    Algoritmo.FCFS.value: lambda p, q, c, a, pr: simular_motor(p, POLITICAS[Algoritmo.FCFS], q, c),
    Algoritmo.SJF.value: lambda p, q, c, a, pr: simular_motor(p, POLITICAS[Algoritmo.SJF], q, c),
    Algoritmo.ROUND_ROBIN.value: lambda p, q, c, a, pr: simular_motor(p, POLITICAS[Algoritmo.ROUND_ROBIN], q, c),
    Algoritmo.SRTF.value: lambda p, q, c, a, pr: simular_motor(p, POLITICAS[Algoritmo.SRTF], q, c),
    Algoritmo.PRIORIDADE_COOPERATIVO.value: lambda p, q, c, a, pr: simular_motor(
        p, POLITICAS[Algoritmo.PRIORIDADE_COOPERATIVO], q, c, a
    ),
    Algoritmo.PRIORIDADE_PREEMPTIVO.value: lambda p, q, c, a, pr: simular_motor(
        p, POLITICAS[Algoritmo.PRIORIDADE_PREEMPTIVO], q, c, protocolo=pr
    ),
}


def simular_escalonamento(processos, algoritmo, quantum_entry=0, ctx_time=0.5, alfa=0, protocolo=None):
    if not processos:
        raise ValueError("Nenhum processo foi adicionado.")

    executar = _DISPATCH.get(algoritmo)
    if executar is None:
        raise ValueError("Selecione um algoritmo válido.")

    if protocolo not in (None, "heranca", "teto"):
        raise ValueError("Protocolo de recurso inválido.")

    quantum = None
    if algoritmo == Algoritmo.ROUND_ROBIN.value:
        quantum = int(quantum_entry)
        if quantum <= 0:
            raise ValueError("O quantum do Round Robin deve ser maior que zero.")
        if quantum <= ctx_time:
            raise ValueError("O quantum deve ser maior que o tempo de troca de contexto.")

    processos_simulados = copy.deepcopy(processos)
    media_espera, media_execucao, nome_processo = executar(
        processos_simulados, quantum, float(ctx_time), alfa, protocolo
    )

    return media_execucao, media_espera, nome_processo, processos_simulados
