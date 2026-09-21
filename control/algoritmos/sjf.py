from control.simular_escalonamento import simular_escalonamento


def sjf(processos, ctx_time=0):
    media_execucao, media_espera, nome = simular_escalonamento(processos, 2, 2, ctx_time)
    return media_espera, media_execucao, nome
