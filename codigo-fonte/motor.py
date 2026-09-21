def teto_de_r(tarefas):
    usuarias = [t.prioridade for t in tarefas if t.secao_critica is not None]
    return max(usuarias) if usuarias else None


def simular(tarefas, politica=None, preemptivo=False, ttc=0, tq=None,
            protocolo=None, alfa=0):
    relogio = 0
    atual = None
    ultima = None
    trocas = 0
    fatia = 0
    linha_do_tempo = []
    eventos = []
    fila = []
    ingressadas = []
    detentor = None
    teto = teto_de_r(tarefas)

    def enfileirar():
        novas = [t for t in tarefas
                 if t.ingresso <= relogio and t not in ingressadas]
        novas.sort(key=lambda t: (t.ingresso, t.id))
        for t in novas:
            ingressadas.append(t)
            fila.append(t)

    while not all(t.terminou() for t in tarefas):
        enfileirar()

        if alfa:
            for t in tarefas:
                if t.ultimo_despacho is None:
                    desde = t.ingresso
                else:
                    desde = t.ultimo_despacho
                t.bonus = alfa * max(0, relogio - desde)

        if protocolo == "heranca" and detentor is not None:
            esperando = [t.prioridade for t in tarefas if t.suspensa]
            detentor.elevacao = max([detentor.prioridade] + esperando)

        if tq is None:
            prontas = [t for t in tarefas
                       if t.ingresso <= relogio and not t.terminou()
                       and not t.suspensa]
            if not prontas:
                relogio = min(t.ingresso for t in tarefas if not t.terminou())
                continue
            if atual is None or atual.terminou() or preemptivo:
                atual = politica(prontas)
        else:
            if atual is None:
                if not fila:
                    relogio = min(t.ingresso for t in tarefas
                                  if not t.terminou())
                    continue
                atual = fila.pop(0)
                fatia = tq if atual is ultima else tq - ttc

        if atual.precisa_de_r() and detentor is not atual:
            if detentor is None:
                detentor = atual
                if protocolo == "teto":
                    atual.elevacao = teto
            else:
                atual.suspensa = True
                atual = None
                continue

        houve_troca = atual is not ultima
        if houve_troca:
            trocas += 1
            for _ in range(ttc):
                eventos.append({"t": relogio, "executando": None,
                                "com_r": None, "suspensas": [], "troca": True})
                relogio += 1
            ultima = atual

        if atual.primeira_exec is None:
            atual.primeira_exec = relogio - atual.ingresso

        linha_do_tempo.append((relogio, atual.id))
        eventos.append({
            "t": relogio,
            "executando": atual.id,
            "com_r": detentor.id if detentor is not None else None,
            "suspensas": [t.id for t in tarefas if t.suspensa],
            "troca": houve_troca and ttc == 0,
        })
        atual.executado += 1
        relogio += 1
        atual.ultimo_despacho = relogio
        fatia -= 1

        if detentor is atual and not atual.precisa_de_r():
            atual.elevacao = None
            detentor = None
            for t in tarefas:
                t.suspensa = False

        if atual.terminou():
            atual.conclusao = relogio
            atual = None
        elif tq is not None and fatia == 0:
            enfileirar()
            fila.append(atual)
            atual = None

    return {"trocas": trocas, "linha_do_tempo": linha_do_tempo,
            "eventos": eventos, "fim": relogio}


def eficiencia(tq, ttc):
    if tq is None:
        return None
    return tq / (tq + ttc)
