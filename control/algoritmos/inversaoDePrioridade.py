from control.simular_escalonamento import simular_escalonamento


def inversao_prioridade(processos, ctx_time=0):
    media_execucao, media_espera, nome = simular_escalonamento(processos, 6, 2, ctx_time)
    return media_espera, media_execucao, nome
