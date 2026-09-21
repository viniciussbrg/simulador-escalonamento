import json

from src.model.prioridade import Prioridade
from src.model.processo import Processo, SecaoCritica


def _tarefa_para_dict(processo: Processo) -> dict:
    dados = {
        "id": processo.id,
        "chegada": processo.chegada,
        "duracao": processo.duracao,
        "prioridade": processo.prioridade.numero,
    }
    if processo.secao_critica is not None:
        dados["secao_critica"] = {
            "recurso": processo.secao_critica.recurso,
            "inicio_execucao": processo.secao_critica.inicio_execucao,
            "duracao": processo.secao_critica.duracao,
        }
    return dados


def _tarefa_de_dict(dados: dict) -> Processo:
    secao_critica = None
    dados_secao = dados.get("secao_critica")
    if dados_secao is not None:
        secao_critica = SecaoCritica(
            recurso=dados_secao["recurso"],
            inicio_execucao=dados_secao["inicio_execucao"],
            duracao=dados_secao["duracao"],
        )

    return Processo(
        id=dados["id"],
        chegada=dados["chegada"],
        duracao=dados["duracao"],
        prioridade=Prioridade(dados["prioridade"]),
        secao_critica=secao_critica,
    )


def salvar_cenario(tarefas: list[Processo], caminho: str) -> None:
    dados = [_tarefa_para_dict(p) for p in tarefas]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=2, ensure_ascii=False)


def carregar_cenario(caminho: str) -> list[Processo]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("Arquivo de cenário inválido: esperava uma lista de tarefas.")

    try:
        return [_tarefa_de_dict(item) for item in dados]
    except (KeyError, TypeError) as erro:
        raise ValueError("Arquivo de cenário inválido ou corrompido.") from erro
