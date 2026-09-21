def fcfs(prontas):
    return min(prontas, key=lambda t: (t.ingresso, t.id))

def sjf(prontas):
    return min(prontas, key=lambda t: (t.tp, t.ingresso, t.id))

def srtf(prontas):
    return min(prontas, key=lambda t: (t.restante(), t.ingresso, t.id))

def prio(prontas):
    return min(prontas, key=lambda t: (-t.prio_efetiva(), t.ingresso, t.id))
