EXECUTANDO = "#"
COM_RECURSO = "="
SUSPENSA = "."
NA_FILA = "-"
FORA = " "
TROCA = "x"

LEGENDA = ("#  executando          =  executando com o recurso R\n"
           ".  suspensa esperando R    -  pronta, esperando na fila\n"
           "x  troca de contexto")


def diagrama_de_tempo(tarefas, eventos):
    if not eventos:
        return "Nada a mostrar."

    fim = eventos[-1]["t"] + 1
    por_instante = {e["t"]: e for e in eventos}
    largura = max(3, len(f"t{max(t.id for t in tarefas)}"))

    linhas = [_regua(fim, largura)]

    for tarefa in tarefas:
        celulas = []
        for instante in range(fim):
            celulas.append(_celula(tarefa, por_instante.get(instante)))
        rotulo = f"t{tarefa.id}".ljust(largura)
        linhas.append(f"{rotulo}|{''.join(celulas)}|")

    trocas = "".join(TROCA if por_instante.get(i, {}).get("troca") else " "
                     for i in range(fim))
    linhas.append(f"{'':<{largura}}|{trocas}|")
    linhas.append("")
    linhas.append(LEGENDA)
    return "\n".join(linhas)


def _celula(tarefa, evento):
    if evento is None:
        return FORA
    instante = evento["t"]

    if evento["executando"] == tarefa.id:
        if evento["com_r"] == tarefa.id:
            return COM_RECURSO
        return EXECUTANDO

    if tarefa.id in evento["suspensas"]:
        return SUSPENSA

    ja_entrou = tarefa.ingresso <= instante
    ja_saiu = tarefa.conclusao is not None and instante >= tarefa.conclusao
    if ja_entrou and not ja_saiu:
        return NA_FILA

    return FORA


def _regua(fim, largura):
    topo = [" "] * fim
    for instante in range(0, fim, 5):
        marca = str(instante)
        if instante + len(marca) > fim:
            continue
        for deslocamento, caractere in enumerate(marca):
            topo[instante + deslocamento] = caractere
    return f"{'':<{largura}} {''.join(topo)}"
