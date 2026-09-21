class EntradaInvalida(Exception):
    pass


def inteiro(texto, nome, minimo=0):
    texto = str(texto).strip()
    if texto == "":
        raise EntradaInvalida(f"{nome}: informe um valor.")
    try:
        valor = int(texto)
    except ValueError:
        raise EntradaInvalida(
            f"{nome}: '{texto}' nao e um numero inteiro.")
    if valor < minimo:
        raise EntradaInvalida(
            f"{nome}: deve ser maior ou igual a {minimo}.")
    return valor


def validar_secao_critica(inicio, duracao, tp):
    if inicio + duracao > tp:
        raise EntradaInvalida(
            f"Secao critica: precisa caber na duracao da tarefa. "
            f"Inicio {inicio} mais duracao {duracao} passa de {tp}.")
    return (inicio, duracao)


def validar_quantum(tq, ttc):
    if tq <= ttc:
        raise EntradaInvalida(
            f"Quantum {tq} nao e maior que o custo da troca {ttc}. "
            f"A troca consumiria a fatia inteira e nenhum trabalho "
            f"util seria realizado.")
    return tq


def ler_tarefa(id, txt_ingresso, txt_tp, txt_prioridade,
               txt_sc_inicio="", txt_sc_duracao=""):
    ingresso = inteiro(txt_ingresso, "Ingresso", 0)
    tp = inteiro(txt_tp, "Duracao", 1)
    prioridade = inteiro(txt_prioridade, "Prioridade", 1)

    usa_sc = str(txt_sc_inicio).strip() != "" or str(txt_sc_duracao).strip() != ""
    secao = None
    if usa_sc:
        inicio = inteiro(txt_sc_inicio, "Inicio da secao critica", 0)
        duracao = inteiro(txt_sc_duracao, "Duracao da secao critica", 1)
        secao = validar_secao_critica(inicio, duracao, tp)

    return (id, ingresso, tp, prioridade, secao)
