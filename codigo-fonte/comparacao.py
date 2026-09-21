from politicas import fcfs, sjf, srtf, prio
from motor import simular
from gerador import sortear_dados, montar

ALGORITMOS = {
    "FCFS":  {"politica": fcfs, "preemptivo": False, "usa_quantum": False},
    "RR":    {"politica": None, "preemptivo": False, "usa_quantum": True},
    "SJF":   {"politica": sjf,  "preemptivo": False, "usa_quantum": False},
    "SRTF":  {"politica": srtf, "preemptivo": True,  "usa_quantum": False},
    "PRIOc": {"politica": prio, "preemptivo": False, "usa_quantum": False},
    "PRIOp": {"politica": prio, "preemptivo": True,  "usa_quantum": False},
}


def rodar(dados, nome, tq=2, ttc=0, protocolo=None, alfa=0):
    cfg = ALGORITMOS[nome]
    tarefas = montar(dados)
    simular(tarefas,
            politica=cfg["politica"],
            preemptivo=cfg["preemptivo"],
            ttc=ttc,
            tq=tq if cfg["usa_quantum"] else None,
            protocolo=protocolo,
            alfa=alfa)
    n = len(tarefas)
    return {
        "Tt": sum(t.tt() for t in tarefas) / n,
        "Tw": sum(t.tw() for t in tarefas) / n,
        "primeira": sum(t.primeira_exec for t in tarefas) / n,
    }


def comparar_lote(n_cenarios=50, n_tarefas=5, tq=2, ttc=0):
    soma = {nome: {"Tt": 0.0, "Tw": 0.0, "primeira": 0.0}
            for nome in ALGORITMOS}
    for _ in range(n_cenarios):
        dados = sortear_dados(n_tarefas)
        for nome in ALGORITMOS:
            r = rodar(dados, nome, tq=tq, ttc=ttc)
            for k in soma[nome]:
                soma[nome][k] += r[k]
    return {nome: {k: v / n_cenarios for k, v in m.items()}
            for nome, m in soma.items()}
