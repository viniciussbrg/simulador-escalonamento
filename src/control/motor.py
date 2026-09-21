from src.control.algoritmos._base import (
    avancar_tempo_para_chegada,
    chave_desempate,
    selecionar_proximo,
    trocar_contexto_padrao,
    despachar_com_quantum,
)
from src.control.algoritmos.recursos import bloqueada_por_recurso, calcular_tetos, prioridade_efetiva
from src.control.politicas import chave_prioridade_com_envelhecimento
from src.model.processo import Periodo


def simular(processos, politica, quantum, ctx_time, alfa=0, protocolo=None):
    if politica.usa_quantum:
        total_espera, total_execucao = _simular_round_robin(processos, quantum, ctx_time)
    elif politica.suporta_recursos:
        total_espera, total_execucao = _simular_prioridade_preemptiva_com_recursos(processos, ctx_time, protocolo)
    else:
        chave_selecao = politica.chave_selecao
        if alfa and politica.suporta_envelhecimento:
            chave_selecao = chave_prioridade_com_envelhecimento(alfa)

        total_espera, total_execucao = _simular_por_chave(
            processos, chave_selecao, politica.preemptivo, ctx_time
        )

    quantidade = len(processos)
    nome = politica.algoritmo.nome_exibicao
    return total_espera / quantidade, total_execucao / quantidade, nome


def _simular_por_chave(processos, chave_selecao, preemptivo, ctx_time):
    tempo_atual = 0
    total_espera = 0
    total_execucao = 0
    ultimo_processo = None

    pendentes = list(processos)

    while pendentes:
        proxima_chegada = min(pendentes, key=lambda p: p.chegada)
        tempo_atual = avancar_tempo_para_chegada(proxima_chegada, tempo_atual)

        processo_atual = selecionar_proximo(pendentes, tempo_atual, chave_selecao)
        tempo_atual = trocar_contexto_padrao(ultimo_processo, processo_atual, tempo_atual, ctx_time)

        duracao_fatia = 1 if preemptivo else processo_atual.duracao
        fim = tempo_atual + min(duracao_fatia, processo_atual.tempo_restante)
        tempo_atual += processo_atual.adicionar_processamento(tempo_atual, fim)

        ultimo_processo = processo_atual

        if processo_atual.tempo_restante == 0:
            total_execucao += processo_atual.get_turnaround()
            total_espera += processo_atual.get_espera()
            pendentes.remove(processo_atual)

    return total_espera, total_execucao


def _simular_prioridade_preemptiva_com_recursos(processos, ctx_time, protocolo):
    tempo_atual = 0
    total_espera = 0
    total_execucao = 0
    ultimo_processo = None

    pendentes = list(processos)
    tetos = calcular_tetos(processos)
    suspensa_desde = {}

    while pendentes:
        proxima_chegada = min(pendentes, key=lambda p: p.chegada)
        tempo_atual = avancar_tempo_para_chegada(proxima_chegada, tempo_atual)

        # Só tarefas já chegadas contam para detentor/bloqueio — senão uma
        # tarefa com início de seção crítica 0 pareceria "dentro" dela antes
        # mesmo de chegar (executado=0 é indistinguível de "ainda não
        # chegou" olhando só para o Processo).
        prontas = [p for p in pendentes if p.chegada <= tempo_atual]

        for p in prontas:
            bloqueada = bloqueada_por_recurso(p, prontas)
            if bloqueada and p not in suspensa_desde:
                suspensa_desde[p] = tempo_atual
            elif not bloqueada and p in suspensa_desde:
                inicio_suspensao = suspensa_desde.pop(p)
                if tempo_atual > inicio_suspensao:
                    p.processamentos.append(Periodo(inicio_suspensao, tempo_atual, "Suspensa"))

        candidatos = [p for p in prontas if p not in suspensa_desde]
        if not candidatos:
            candidatos = prontas

        def chave(p):
            return (-prioridade_efetiva(p, prontas, protocolo, tetos), *chave_desempate(p))

        processo_atual = min(candidatos, key=chave)

        tempo_atual = trocar_contexto_padrao(ultimo_processo, processo_atual, tempo_atual, ctx_time)

        fim = tempo_atual + min(1, processo_atual.tempo_restante)
        tempo_atual += processo_atual.adicionar_processamento(tempo_atual, fim)

        ultimo_processo = processo_atual

        if processo_atual.tempo_restante == 0:
            total_execucao += processo_atual.get_turnaround()
            total_espera += processo_atual.get_espera()
            pendentes.remove(processo_atual)
            suspensa_desde.pop(processo_atual, None)

    return total_espera, total_execucao


def _simular_round_robin(processos, quantum, ctx_time):
    if quantum is None or quantum <= 0:
        raise ValueError("O quantum deve ser maior que zero.")

    tempo_atual = 0
    total_espera = 0
    total_execucao = 0
    ultimo_processo = None

    pendentes = sorted(processos, key=lambda p: (p.chegada, p.id))
    fila = []

    while pendentes:
        for processo in pendentes:
            if processo.chegada <= tempo_atual and processo not in fila:
                fila.append(processo)

        if not fila:
            tempo_atual = min(p.chegada for p in pendentes)
            continue

        processo_atual = fila.pop(0)
        pendentes.remove(processo_atual)

        tempo_atual = despachar_com_quantum(ultimo_processo, processo_atual, tempo_atual, quantum, ctx_time)

        if processo_atual.tempo_restante == 0:
            total_execucao += processo_atual.get_turnaround()
            total_espera += processo_atual.get_espera()
        else:
            pendentes.append(processo_atual)

        ultimo_processo = processo_atual

    return total_espera, total_execucao
