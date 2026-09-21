from model.processo import Periodo
from simulador import TarefaEntrada, simular


def _converter_processo(processo):
    return TarefaEntrada(
        id=int(processo.id),
        ingresso=int(processo.chegada),
        tp=int(processo.duracao),
        prioridade=int(processo.prioridade.numero),
        recurso_inicio=getattr(processo, "recurso_inicio", None),
        recurso_duracao=int(getattr(processo, "recurso_duracao", 0) or 0),
    )


def _copiar_linha_tempo(processos, resultado):
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

    for intervalo in resultado.linha_tempo:
        if intervalo.tipo != "troca" or intervalo.tarefa_id not in por_id:
            continue
        por_id[intervalo.tarefa_id].processamentos.append(
            Periodo(intervalo.inicio, intervalo.fim, "CTX")
        )

    for processo in processos:
        processo.processamentos.sort(key=lambda periodo: (periodo.inicio, periodo.fim))


def simular_escalonamento(processos, algoritmo, quantum_entry=0, ctx_time=0):
    if not processos:
        raise Exception("Nenhum processo foi adicionado.")

    protocolo = "nenhum"
    if algoritmo == 8:
        algoritmo = 6
        protocolo = "heranca"

    tarefas = [_converter_processo(processo) for processo in processos]
    resultado = simular(
        tarefas,
        algoritmo,
        quantum=int(quantum_entry or 2),
        ttc=int(float(ctx_time)),
        protocolo_prioridade=protocolo,
    )
    _copiar_linha_tempo(processos, resultado)
    return resultado.medias["tt"], resultado.medias["tw"], resultado.algoritmo
