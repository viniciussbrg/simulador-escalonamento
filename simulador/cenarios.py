from __future__ import annotations

import json
import random
from pathlib import Path
from statistics import mean
from typing import Optional

from .modelos import TarefaEntrada
from .motor import ALGORITMOS, simular


def gerar_tarefas(
    quantidade: int,
    ingresso_max: int = 8,
    tp_max: int = 6,
    prioridade_max: int = 5,
    incluir_recurso: bool = False,
    semente: Optional[int] = None,
) -> list[TarefaEntrada]:
    if quantidade <= 0:
        raise ValueError("A quantidade de tarefas deve ser positiva.")
    if ingresso_max < 0 or tp_max <= 0 or prioridade_max < 0:
        raise ValueError("Parametros de sorteio invalidos.")

    rng = random.Random(semente)
    tarefas: list[TarefaEntrada] = []
    for indice in range(1, quantidade + 1):
        ingresso = rng.randint(0, ingresso_max)
        tp = rng.randint(1, tp_max)
        prioridade = rng.randint(1, prioridade_max)
        recurso_inicio = None
        recurso_duracao = 0

        if incluir_recurso and tp > 1 and rng.random() < 0.35:
            recurso_inicio = rng.randint(0, tp - 1)
            recurso_duracao = rng.randint(1, tp - recurso_inicio)

        tarefas.append(
            TarefaEntrada(
                id=indice,
                ingresso=ingresso,
                tp=tp,
                prioridade=prioridade,
                recurso_inicio=recurso_inicio,
                recurso_duracao=recurso_duracao,
            )
        )

    return sorted(tarefas, key=lambda tarefa: (tarefa.ingresso, tarefa.id))


def salvar_cenario(caminho: str | Path, tarefas: list[TarefaEntrada]) -> None:
    dados = {
        "versao": 1,
        "tarefas": [tarefa.para_json() for tarefa in sorted(tarefas, key=lambda t: t.id)],
    }
    Path(caminho).write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")


def carregar_cenario(caminho: str | Path) -> list[TarefaEntrada]:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    tarefas = dados["tarefas"] if isinstance(dados, dict) and "tarefas" in dados else dados
    return [TarefaEntrada.de_json(tarefa) for tarefa in tarefas]


def comparar_lote(
    quantidade_cenarios: int = 50,
    quantidade_tarefas: int = 5,
    ingresso_max: int = 8,
    tp_max: int = 6,
    prioridade_max: int = 5,
    quantum: int = 2,
    ttc: int = 0,
    semente: Optional[int] = None,
) -> list[dict[str, float | str]]:
    if quantidade_cenarios <= 0:
        raise ValueError("A quantidade de cenarios deve ser positiva.")

    rng = random.Random(semente)
    acumulado: dict[str, list[dict[str, float]]] = {algoritmo: [] for algoritmo in ALGORITMOS}

    for _ in range(quantidade_cenarios):
        tarefas = gerar_tarefas(
            quantidade=quantidade_tarefas,
            ingresso_max=ingresso_max,
            tp_max=tp_max,
            prioridade_max=prioridade_max,
            incluir_recurso=False,
            semente=rng.randint(1, 10**9),
        )
        for algoritmo in ALGORITMOS:
            resultado = simular(tarefas, algoritmo, quantum=quantum, ttc=ttc)
            acumulado[algoritmo].append(resultado.medias)

    linhas: list[dict[str, float | str]] = []
    for algoritmo, medias in acumulado.items():
        linhas.append(
            {
                "algoritmo": algoritmo,
                "tt": mean(item["tt"] for item in medias),
                "tw": mean(item["tw"] for item in medias),
                "primeira_execucao": mean(item["primeira_execucao"] for item in medias),
            }
        )
    return linhas


def cenario_aula5() -> list[TarefaEntrada]:
    return [
        TarefaEntrada(1, 0, 5, 2),
        TarefaEntrada(2, 0, 2, 3),
        TarefaEntrada(3, 1, 4, 1),
        TarefaEntrada(4, 3, 1, 4),
        TarefaEntrada(5, 5, 2, 5),
    ]


def cenario_inversao_prioridade() -> list[TarefaEntrada]:
    return [
        TarefaEntrada(1, 0, 6, 1, 1, 4),
        TarefaEntrada(2, 4, 4, 2),
        TarefaEntrada(3, 6, 3, 3),
        TarefaEntrada(4, 2, 3, 4, 1, 1),
    ]


def cenario_teto_sem_disputa() -> list[TarefaEntrada]:
    return [
        TarefaEntrada(1, 0, 6, 1, 1, 4),
        TarefaEntrada(2, 2, 3, 2),
        TarefaEntrada(4, 12, 2, 4, 0, 1),
    ]


def cenario_inanicao() -> list[TarefaEntrada]:
    return [
        TarefaEntrada(1, 0, 4, 1),
        TarefaEntrada(2, 0, 2, 5),
        TarefaEntrada(3, 2, 2, 5),
        TarefaEntrada(4, 4, 2, 5),
        TarefaEntrada(5, 6, 2, 5),
        TarefaEntrada(6, 8, 2, 5),
    ]
