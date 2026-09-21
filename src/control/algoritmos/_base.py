def avancar_tempo_para_chegada(processo, tempo_atual):
    return processo.chegada if processo.chegada > tempo_atual else tempo_atual


def trocar_contexto(ultimo_processo, processo_atual, tempo_atual, ctx_time, exigir_troca=True):
    if ultimo_processo is None or ctx_time <= 0:
        return tempo_atual
    if exigir_troca and ultimo_processo == processo_atual:
        return tempo_atual

    ctx_duracao = ultimo_processo.adicionar_troca_contexto(tempo_atual, tempo_atual + ctx_time)
    return tempo_atual + ctx_duracao


def selecionar_proximo(processos_ordenados, tempo_atual, chave):
    candidatos = [p for p in processos_ordenados if p.chegada <= tempo_atual]
    if not candidatos:
        return processos_ordenados[0]
    return min(candidatos, key=lambda p: chave(p, tempo_atual))


def finalizar_metricas(total_espera, total_execucao, quantidade, nome):
    return total_espera / quantidade, total_execucao / quantidade, nome


def chave_desempate(processo, tempo_atual=None):
    return (processo.chegada, processo.id)


def trocar_contexto_padrao(ultimo_processo, processo_atual, tempo_atual, ctx_time):
    if ctx_time <= 0:
        return tempo_atual
    if ultimo_processo is not None and ultimo_processo == processo_atual:
        return tempo_atual

    ctx_duracao = processo_atual.adicionar_troca_contexto(tempo_atual, tempo_atual + ctx_time)
    return tempo_atual + ctx_duracao


def despachar_com_quantum(ultimo_processo, processo_atual, tempo_atual, quantum, ctx_time):
    ha_troca = ultimo_processo is None or ultimo_processo != processo_atual

    if ha_troca and ctx_time > 0:
        tempo_atual = trocar_contexto_padrao(ultimo_processo, processo_atual, tempo_atual, ctx_time)
        orcamento = quantum - ctx_time
    else:
        orcamento = quantum

    fim = tempo_atual + min(orcamento, processo_atual.tempo_restante)
    tempo_atual += processo_atual.adicionar_processamento(tempo_atual, fim)
    return tempo_atual
