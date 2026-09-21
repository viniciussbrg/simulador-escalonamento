"""Simulador de escalonamento de tarefas."""

from .modelos import Intervalo, MetricaTarefa, ResultadoSimulacao, TarefaEntrada
from .motor import ALGORITMOS, PROTOCOLOS, SimulacaoErro, simular

__all__ = [
    "ALGORITMOS",
    "PROTOCOLOS",
    "Intervalo",
    "MetricaTarefa",
    "ResultadoSimulacao",
    "SimulacaoErro",
    "TarefaEntrada",
    "simular",
]
