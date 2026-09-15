from model.processo import Periodo
from simulador import TarefaEntrada, simular


def heranca_prioridade(processos, ctx_time=0):
    tarefas = [
        TarefaEntrada(
            id=int(processo.id),
            ingresso=int(processo.chegada),
            tp=int(processo.duracao),
            prioridade=int(processo.prioridade.numero),
            recurso_inicio=getattr(processo, "recurso_inicio", None),
            recurso_duracao=int(getattr(processo, "recurso_duracao", 0) or 0),
        )
        for processo in processos
    ]
    resultado = simular(tarefas, "PRIOp", quantum=2, ttc=int(float(ctx_time)), protocolo_prioridade="heranca")

    por_id = {processo.id: processo for processo in processos}
    for processo in processos:
        processo.processamentos = []
        processo.tempo_restante = 0
    for tarefa_id, intervalos in resultado.execucoes_por_tarefa.items():
        processo = por_id.get(tarefa_id)
        if processo is None:
            continue
        for intervalo in intervalos:
            processo.processamentos.append(Periodo(intervalo.inicio, intervalo.fim))

    return resultado.medias["tw"], resultado.medias["tt"], "Heranca de Prioridade"
