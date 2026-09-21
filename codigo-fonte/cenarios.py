import json
import os

PASTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "cenarios")


def pasta_de_cenarios():
    os.makedirs(PASTA, exist_ok=True)
    return PASTA


def gravar(caminho, dados, tq=None, ttc=0, alfa=0):
    conteudo = {
        "parametros": {"tq": tq, "ttc": ttc, "alfa": alfa},
        "tarefas": [
            {
                "id": id,
                "ingresso": ingresso,
                "tp": tp,
                "prioridade": prioridade,
                "secao_critica": list(secao) if secao is not None else None,
            }
            for id, ingresso, tp, prioridade, secao in dados
        ],
    }
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=2, ensure_ascii=False)


def carregar(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        conteudo = json.load(arquivo)

    dados = []
    for item in conteudo["tarefas"]:
        secao = item.get("secao_critica")
        dados.append((
            int(item["id"]),
            int(item["ingresso"]),
            int(item["tp"]),
            int(item["prioridade"]),
            tuple(secao) if secao else None,
        ))

    parametros = conteudo.get("parametros", {})
    return dados, parametros
