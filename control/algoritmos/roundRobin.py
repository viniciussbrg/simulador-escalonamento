from control.simular_escalonamento import simular_escalonamento


def round_robin(processos, quantum=2, ctx_time=0):
    media_execucao, media_espera, nome = simular_escalonamento(processos, 3, quantum, ctx_time)
    return media_espera, media_execucao, nome
