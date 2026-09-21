"""Gravacao e recarga de cenarios (R2).

Um sorteio interessante nao pode se perder ao fim da execucao: qualquer
conjunto de tarefas, digitado ou sorteado, pode ser gravado em arquivo e
reexaminado depois. Guarda tambem os parametros do escalonador, porque um
cenario sem o quantum e o custo da troca que o produziram nao se reproduz.
"""

import json
from typing import List, Tuple

from model.tarefa import EntradaInvalida, Tarefa

FORMATO = "simulador-escalonamento/1"


def gravar(
    caminho: str,
    tarefas: List[Tarefa],
    parametros: dict = None,
    descricao: str = "",
) -> None:
    conteudo = {
        "formato": FORMATO,
        "descricao": descricao,
        "parametros": parametros or {},
        "tarefas": [t.para_dicionario() for t in tarefas],
    }
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=2, ensure_ascii=False)


def carregar(caminho: str) -> Tuple[List[Tarefa], dict, str]:
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = json.load(arquivo)
    except json.JSONDecodeError as erro:
        raise EntradaInvalida(f"O arquivo nao e um cenario valido: {erro}") from erro
    except OSError as erro:
        raise EntradaInvalida(f"Nao foi possivel abrir o arquivo: {erro}") from erro

    if not isinstance(conteudo, dict) or "tarefas" not in conteudo:
        raise EntradaInvalida("O arquivo nao contem uma lista de tarefas.")

    tarefas = [Tarefa.de_dicionario(d) for d in conteudo["tarefas"]]
    if not tarefas:
        raise EntradaInvalida("O cenario nao tem nenhuma tarefa.")

    identificadores = [t.identificador for t in tarefas]
    if len(set(identificadores)) != len(identificadores):
        raise EntradaInvalida("Ha identificadores repetidos no cenario.")

    return tarefas, conteudo.get("parametros", {}) or {}, conteudo.get("descricao", "")
