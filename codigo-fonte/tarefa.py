class Tarefa:
    def __init__(self, id, ingresso, tp, prioridade=1, secao_critica=None):
        self.id = id
        self.ingresso = ingresso
        self.tp = tp
        self.prioridade = prioridade
        self.secao_critica = secao_critica
        self.executado = 0
        self.conclusao = None
        self.primeira_exec = None
        self.suspensa = False
        self.elevacao = None
        self.bonus = 0
        self.ultimo_despacho = None

    def restante(self):
        return self.tp - self.executado

    def terminou(self):
        return self.executado >= self.tp

    def precisa_de_r(self):
        if self.secao_critica is None:
            return False
        inicio, duracao = self.secao_critica
        return inicio <= self.executado < inicio + duracao

    def prio_efetiva(self):
        base = self.prioridade
        if self.elevacao is not None:
            base = max(base, self.elevacao)
        return base + self.bonus

    def tt(self):
        return self.conclusao - self.ingresso

    def tw(self):
        return self.tt() - self.tp
