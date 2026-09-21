def esta_na_secao_critica(p):
    if p.secao_critica is None:
        return False
    executado = p.duracao - p.tempo_restante
    sc = p.secao_critica
    return sc.inicio_execucao <= executado < sc.inicio_execucao + sc.duracao


def detentor_do_recurso(tarefas, recurso):
    return next(
        (
            p
            for p in tarefas
            if p.secao_critica is not None and p.secao_critica.recurso == recurso and esta_na_secao_critica(p)
        ),
        None,
    )


def bloqueada_por_recurso(p, tarefas):
    if p.secao_critica is None or not esta_na_secao_critica(p):
        return False
    detentor = detentor_do_recurso(tarefas, p.secao_critica.recurso)
    return detentor is not None and detentor is not p


def calcular_tetos(processos):
    tetos = {}
    for p in processos:
        if p.secao_critica is not None:
            recurso = p.secao_critica.recurso
            tetos[recurso] = max(tetos.get(recurso, 0), p.prioridade.numero)
    return tetos


def prioridade_efetiva(p, tarefas, protocolo, tetos):
    if p.secao_critica is None or not esta_na_secao_critica(p):
        return p.prioridade.numero

    if protocolo == "teto":
        return tetos[p.secao_critica.recurso]

    if protocolo == "heranca":
        bloqueadores = [
            q
            for q in tarefas
            if q is not p
            and q.secao_critica is not None
            and q.secao_critica.recurso == p.secao_critica.recurso
            and bloqueada_por_recurso(q, tarefas)
        ]
        if bloqueadores:
            return max(p.prioridade.numero, max(q.prioridade.numero for q in bloqueadores))

    return p.prioridade.numero


def classificar_suspensoes(processos):
    resultado = []
    for tarefa in processos:
        if tarefa.secao_critica is None:
            continue
        recurso = tarefa.secao_critica.recurso
        for periodo in tarefa.processamentos:
            if periodo.tipo != "Suspensa":
                continue
            terceiros_rodaram = any(
                per.tipo == "Execução" and periodo.inicio <= per.inicio < periodo.fim
                for outra in processos
                if outra is not tarefa
                and not (outra.secao_critica is not None and outra.secao_critica.recurso == recurso)
                for per in outra.processamentos
            )
            resultado.append(
                {
                    "tarefa": tarefa.id,
                    "recurso": recurso,
                    "inicio": periodo.inicio,
                    "fim": periodo.fim,
                    "tipo": "inversao" if terceiros_rodaram else "bloqueio_direto",
                }
            )
    return resultado
