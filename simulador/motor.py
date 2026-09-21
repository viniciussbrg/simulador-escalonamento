from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional

from .modelos import Intervalo, MetricaTarefa, ResultadoSimulacao, TarefaEntrada


ALGORITMOS = {
    "FCFS": "First-Come, First-Served",
    "SJF": "Shortest Job First",
    "SRTF": "Shortest Remaining Time First",
    "RR": "Round-Robin",
    "PRIOc": "Prioridade cooperativa",
    "PRIOp": "Prioridade preemptiva",
}

PROTOCOLOS = {
    "nenhum": "Sem mecanismo",
    "heranca": "Heranca de prioridade",
    "teto": "Teto de prioridade",
}

_CODIGOS_ALGORITMOS = {
    1: "FCFS",
    2: "SJF",
    3: "RR",
    4: "SRTF",
    5: "PRIOc",
    6: "PRIOp",
}

_APELIDOS_ALGORITMOS = {
    "fcfs": "FCFS",
    "sjf": "SJF",
    "srtf": "SRTF",
    "rr": "RR",
    "round-robin": "RR",
    "round robin": "RR",
    "prioc": "PRIOc",
    "prioridade cooperativa": "PRIOc",
    "prioridade cooperativo": "PRIOc",
    "priop": "PRIOp",
    "prioridade preemptiva": "PRIOp",
    "prioridade preemptivo": "PRIOp",
}


class SimulacaoErro(ValueError):
    """Erro de configuracao ou entrada do simulador."""


@dataclass
class _TarefaRuntime:
    entrada: TarefaEntrada
    restante: int = field(init=False)
    executado: int = 0
    conclusao: Optional[int] = None
    primeira_execucao: Optional[int] = None
    bloqueada: bool = False
    bloqueio_inicio: Optional[int] = None
    ultimo_despacho: int = field(init=False)
    segura_recurso: bool = False
    recurso_concluido: bool = False
    execucoes: list[Intervalo] = field(default_factory=list)
    bloqueios: list[Intervalo] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.restante = self.entrada.tp
        self.ultimo_despacho = self.entrada.ingresso

    @property
    def id(self) -> int:
        return self.entrada.id

    @property
    def ingresso(self) -> int:
        return self.entrada.ingresso

    @property
    def tp(self) -> int:
        return self.entrada.tp

    @property
    def prioridade_base(self) -> int:
        return self.entrada.prioridade

    @property
    def concluida(self) -> bool:
        return self.restante == 0


class _Motor:
    def __init__(
        self,
        tarefas: list[TarefaEntrada],
        algoritmo: str,
        quantum: Optional[int],
        ttc: int,
        protocolo: str,
        envelhecimento: bool,
        alpha: int,
    ) -> None:
        self.tarefas = [_TarefaRuntime(tarefa) for tarefa in sorted(tarefas, key=lambda t: t.id)]
        self.por_id = {tarefa.id: tarefa for tarefa in self.tarefas}
        self.algoritmo = algoritmo
        self.quantum = quantum
        self.ttc = ttc
        self.protocolo = protocolo
        self.envelhecimento = envelhecimento
        self.alpha = alpha
        self.tempo = 0
        self.ultimo_tarefa_id: Optional[int] = None
        self.trocas_contexto = 0
        self.linha_tempo: list[Intervalo] = []
        self.recurso_dono: Optional[int] = None
        self.recurso_inicio_tempo: Optional[int] = None
        self.recurso_intervalos: list[Intervalo] = []
        prioridades_com_recurso = [
            tarefa.prioridade for tarefa in tarefas if tarefa.usa_recurso
        ]
        self.teto_recurso = max(prioridades_com_recurso) if prioridades_com_recurso else None

    def executar(self) -> ResultadoSimulacao:
        if self.algoritmo == "RR":
            self._executar_round_robin()
        else:
            self._executar_padrao()
        return self._montar_resultado()

    def _executar_padrao(self) -> None:
        preemptivo = self.algoritmo in {"SRTF", "PRIOp"}

        while not self._todas_concluidas():
            prontas = self._tarefas_prontas()
            if not prontas:
                self._avancar_ocioso()
                continue

            tarefa = self._escolher_tarefa(prontas)
            self._despachar(tarefa)

            if preemptivo:
                if self._preparar_unidade(tarefa):
                    self._executar_unidade(tarefa)
                continue

            while tarefa.restante > 0:
                if not self._preparar_unidade(tarefa):
                    break
                self._executar_unidade(tarefa)

    def _executar_round_robin(self) -> None:
        if self.quantum is None:
            raise SimulacaoErro("Informe o quantum para Round-Robin.")

        fila: list[int] = []
        em_fila: set[int] = set()

        def enfileirar_chegadas(excluir_id: Optional[int] = None) -> None:
            for tarefa in sorted(self.tarefas, key=lambda t: (t.ingresso, t.id)):
                if tarefa.id == excluir_id:
                    continue
                if tarefa.id in em_fila:
                    continue
                if tarefa.concluida or tarefa.bloqueada:
                    continue
                if tarefa.ingresso <= self.tempo:
                    fila.append(tarefa.id)
                    em_fila.add(tarefa.id)

        while not self._todas_concluidas():
            enfileirar_chegadas()

            if not fila:
                self._avancar_ocioso()
                enfileirar_chegadas()
                continue

            tarefa = self.por_id[fila.pop(0)]
            em_fila.discard(tarefa.id)
            if tarefa.concluida or tarefa.bloqueada:
                continue

            houve_troca = self._despachar(tarefa)
            enfileirar_chegadas(excluir_id=tarefa.id)

            tempo_util = self.quantum - self.ttc if houve_troca else self.quantum
            if tempo_util <= 0:
                raise SimulacaoErro("No Round-Robin, o quantum deve ser maior que o custo da troca de contexto.")

            usado = 0
            while usado < tempo_util and tarefa.restante > 0:
                if not self._preparar_unidade(tarefa):
                    break
                self._executar_unidade(tarefa)
                usado += 1
                enfileirar_chegadas(excluir_id=tarefa.id)

            enfileirar_chegadas(excluir_id=tarefa.id)
            if usado == tempo_util and tarefa.restante > 0 and not tarefa.bloqueada:
                fila.append(tarefa.id)
                em_fila.add(tarefa.id)

    def _todas_concluidas(self) -> bool:
        return all(tarefa.concluida for tarefa in self.tarefas)

    def _tarefas_prontas(self) -> list[_TarefaRuntime]:
        return [
            tarefa
            for tarefa in self.tarefas
            if tarefa.ingresso <= self.tempo
            and not tarefa.concluida
            and not tarefa.bloqueada
        ]

    def _avancar_ocioso(self) -> None:
        proximos = [
            tarefa.ingresso
            for tarefa in self.tarefas
            if not tarefa.concluida and not tarefa.bloqueada and tarefa.ingresso > self.tempo
        ]
        if proximos:
            proximo_tempo = min(proximos)
            self._adicionar_intervalo(self.linha_tempo, "ocioso", self.tempo, proximo_tempo, None, "IDLE")
            self.tempo = proximo_tempo
            return

        bloqueadas = [tarefa for tarefa in self.tarefas if tarefa.bloqueada and not tarefa.concluida]
        if bloqueadas:
            raise SimulacaoErro("Todas as tarefas prontas estao suspensas aguardando o recurso R.")
        raise SimulacaoErro("Nao ha tarefa pronta para executar.")

    def _escolher_tarefa(self, prontas: list[_TarefaRuntime]) -> _TarefaRuntime:
        if self.algoritmo == "FCFS":
            return min(prontas, key=lambda t: (t.ingresso, t.id))
        if self.algoritmo == "SJF":
            return min(prontas, key=lambda t: (t.tp, t.ingresso, t.id))
        if self.algoritmo == "SRTF":
            return min(prontas, key=lambda t: (t.restante, t.ingresso, t.id))
        if self.algoritmo in {"PRIOc", "PRIOp"}:
            return min(prontas, key=lambda t: (-self._prioridade_efetiva(t), t.ingresso, t.id))
        raise SimulacaoErro(f"Algoritmo desconhecido: {self.algoritmo}.")

    def _prioridade_efetiva(self, tarefa: _TarefaRuntime) -> int:
        prioridade = tarefa.prioridade_base

        if self.envelhecimento and not tarefa.bloqueada and not tarefa.concluida:
            prioridade += self.alpha * max(0, self.tempo - tarefa.ultimo_despacho)

        if self.protocolo == "teto" and self.recurso_dono == tarefa.id and self.teto_recurso is not None:
            prioridade = max(prioridade, self.teto_recurso)

        if self.protocolo == "heranca" and self.recurso_dono == tarefa.id:
            prioridades_bloqueadas = [
                bloqueada.prioridade_base
                for bloqueada in self.tarefas
                if bloqueada.bloqueada and not bloqueada.concluida
            ]
            if prioridades_bloqueadas:
                prioridade = max(prioridade, max(prioridades_bloqueadas))

        return prioridade

    def _despachar(self, tarefa: _TarefaRuntime) -> bool:
        houve_troca = self.ultimo_tarefa_id != tarefa.id
        if houve_troca:
            self.trocas_contexto += 1
            if self.ttc > 0:
                inicio = self.tempo
                self.tempo += self.ttc
                self._adicionar_intervalo(self.linha_tempo, "troca", inicio, self.tempo, tarefa.id, "CTX")
            self.ultimo_tarefa_id = tarefa.id
        return houve_troca

    def _preparar_unidade(self, tarefa: _TarefaRuntime) -> bool:
        entrada = tarefa.entrada
        if (
            entrada.usa_recurso
            and not tarefa.recurso_concluido
            and not tarefa.segura_recurso
            and tarefa.executado == entrada.recurso_inicio
        ):
            if self.recurso_dono is None or self.recurso_dono == tarefa.id:
                self._obter_recurso(tarefa)
            else:
                self._suspender(tarefa)
                return False
        return True

    def _obter_recurso(self, tarefa: _TarefaRuntime) -> None:
        self.recurso_dono = tarefa.id
        self.recurso_inicio_tempo = self.tempo
        tarefa.segura_recurso = True

    def _suspender(self, tarefa: _TarefaRuntime) -> None:
        if tarefa.bloqueada:
            return
        tarefa.bloqueada = True
        tarefa.bloqueio_inicio = self.tempo

    def _liberar_recurso(self, tarefa: _TarefaRuntime) -> None:
        if self.recurso_dono != tarefa.id:
            return

        inicio = self.recurso_inicio_tempo
        if inicio is not None:
            intervalo = Intervalo(inicio, self.tempo, "recurso", tarefa.id, "R")
            self.recurso_intervalos.append(intervalo)

        self.recurso_dono = None
        self.recurso_inicio_tempo = None
        tarefa.segura_recurso = False
        tarefa.recurso_concluido = True

        for bloqueada in sorted(self.tarefas, key=lambda t: (t.ingresso, t.id)):
            if bloqueada.bloqueada and bloqueada.bloqueio_inicio is not None:
                intervalo = Intervalo(
                    bloqueada.bloqueio_inicio,
                    self.tempo,
                    "bloqueado",
                    bloqueada.id,
                    "R",
                )
                bloqueada.bloqueios.append(intervalo)
                self._adicionar_intervalo(
                    self.linha_tempo,
                    "bloqueado",
                    intervalo.inicio,
                    intervalo.fim,
                    bloqueada.id,
                    "R",
                )
                bloqueada.bloqueada = False
                bloqueada.bloqueio_inicio = None
                bloqueada.ultimo_despacho = self.tempo

    def _executar_unidade(self, tarefa: _TarefaRuntime) -> None:
        if tarefa.primeira_execucao is None:
            tarefa.primeira_execucao = self.tempo
        tarefa.ultimo_despacho = self.tempo

        inicio = self.tempo
        self.tempo += 1
        tarefa.executado += 1
        tarefa.restante -= 1

        intervalo = Intervalo(inicio, self.tempo, "execucao", tarefa.id, f"t{tarefa.id}")
        self._adicionar_intervalo(self.linha_tempo, intervalo.tipo, intervalo.inicio, intervalo.fim, intervalo.tarefa_id, intervalo.rotulo)
        self._adicionar_intervalo(tarefa.execucoes, intervalo.tipo, intervalo.inicio, intervalo.fim, intervalo.tarefa_id, intervalo.rotulo)

        if (
            tarefa.segura_recurso
            and tarefa.entrada.recurso_fim is not None
            and tarefa.executado >= tarefa.entrada.recurso_fim
        ):
            self._liberar_recurso(tarefa)

        if tarefa.restante == 0:
            tarefa.conclusao = self.tempo
            if tarefa.segura_recurso:
                self._liberar_recurso(tarefa)

    def _adicionar_intervalo(
        self,
        colecao: list[Intervalo],
        tipo: str,
        inicio: int,
        fim: int,
        tarefa_id: Optional[int],
        rotulo: str = "",
    ) -> None:
        if fim <= inicio:
            return
        if colecao:
            ultimo = colecao[-1]
            if (
                ultimo.fim == inicio
                and ultimo.tipo == tipo
                and ultimo.tarefa_id == tarefa_id
                and ultimo.rotulo == rotulo
            ):
                ultimo.fim = fim
                return
        colecao.append(Intervalo(inicio, fim, tipo, tarefa_id, rotulo))

    def _montar_resultado(self) -> ResultadoSimulacao:
        metricas: list[MetricaTarefa] = []
        for tarefa in sorted(self.tarefas, key=lambda t: t.id):
            if tarefa.conclusao is None:
                raise SimulacaoErro(f"Tarefa {tarefa.id} nao foi concluida.")
            primeira_execucao = tarefa.primeira_execucao
            if primeira_execucao is None:
                raise SimulacaoErro(f"Tarefa {tarefa.id} nunca recebeu o processador.")
            tt = tarefa.conclusao - tarefa.ingresso
            metricas.append(
                MetricaTarefa(
                    id=tarefa.id,
                    ingresso=tarefa.ingresso,
                    tp=tarefa.tp,
                    prioridade=tarefa.prioridade_base,
                    conclusao=tarefa.conclusao,
                    tt=tt,
                    tw=tt - tarefa.tp,
                    primeira_execucao=primeira_execucao - tarefa.ingresso,
                )
            )

        quantidade = len(metricas)
        medias = {
            "tt": sum(metrica.tt for metrica in metricas) / quantidade,
            "tp": sum(metrica.tp for metrica in metricas) / quantidade,
            "tw": sum(metrica.tw for metrica in metricas) / quantidade,
            "primeira_execucao": sum(metrica.primeira_execucao for metrica in metricas) / quantidade,
        }
        eficiencia = None
        if self.algoritmo == "RR" and self.quantum is not None:
            eficiencia = self.quantum / (self.quantum + self.ttc)

        return ResultadoSimulacao(
            algoritmo=self.algoritmo,
            protocolo_prioridade=self.protocolo,
            envelhecimento=self.envelhecimento,
            alpha=self.alpha,
            quantum=self.quantum,
            ttc=self.ttc,
            eficiencia=eficiencia,
            trocas_contexto=self.trocas_contexto,
            teto_recurso=self.teto_recurso,
            tarefas=[tarefa.entrada for tarefa in sorted(self.tarefas, key=lambda t: t.id)],
            metricas=metricas,
            medias=medias,
            linha_tempo=self.linha_tempo,
            execucoes_por_tarefa={
                tarefa.id: tarefa.execucoes for tarefa in sorted(self.tarefas, key=lambda t: t.id)
            },
            bloqueios_por_tarefa={
                tarefa.id: tarefa.bloqueios for tarefa in sorted(self.tarefas, key=lambda t: t.id)
            },
            recurso_intervalos=self.recurso_intervalos,
        )


def simular(
    tarefas: Iterable[TarefaEntrada],
    algoritmo: str | int,
    quantum: Optional[int] = None,
    ttc: int = 0,
    protocolo_prioridade: str = "nenhum",
    envelhecimento: bool = False,
    alpha: int = 0,
) -> ResultadoSimulacao:
    tarefas_validadas = _validar_tarefas(list(tarefas))
    algoritmo_normalizado = _normalizar_algoritmo(algoritmo)
    protocolo = _normalizar_protocolo(protocolo_prioridade)
    quantum_validado = _validar_configuracao(algoritmo_normalizado, quantum, ttc, protocolo, envelhecimento, alpha)
    motor = _Motor(
        tarefas=tarefas_validadas,
        algoritmo=algoritmo_normalizado,
        quantum=quantum_validado,
        ttc=int(ttc),
        protocolo=protocolo,
        envelhecimento=bool(envelhecimento),
        alpha=int(alpha),
    )
    return motor.executar()


def _normalizar_algoritmo(algoritmo: str | int) -> str:
    if isinstance(algoritmo, int):
        try:
            return _CODIGOS_ALGORITMOS[algoritmo]
        except KeyError as exc:
            raise SimulacaoErro("Selecione um algoritmo valido.") from exc

    chave = str(algoritmo).strip()
    if chave in ALGORITMOS:
        return chave
    normalizada = chave.lower()
    if normalizada in _APELIDOS_ALGORITMOS:
        return _APELIDOS_ALGORITMOS[normalizada]
    raise SimulacaoErro("Selecione um algoritmo valido.")


def _normalizar_protocolo(protocolo: str) -> str:
    normalizado = str(protocolo or "nenhum").strip().lower()
    normalizado = normalizado.replace("ç", "c").replace("ã", "a").replace("á", "a")
    normalizado = normalizado.replace("â", "a").replace("é", "e").replace("ê", "e")
    if normalizado in {"", "sem mecanismo", "nenhum", "none"}:
        return "nenhum"
    if normalizado in {"heranca", "heranca de prioridade", "inheritance"}:
        return "heranca"
    if normalizado in {"teto", "teto de prioridade", "ceiling"}:
        return "teto"
    raise SimulacaoErro("O mecanismo de prioridade deve ser: nenhum, heranca ou teto.")


def _validar_configuracao(
    algoritmo: str,
    quantum: Optional[int],
    ttc: int,
    protocolo: str,
    envelhecimento: bool,
    alpha: int,
) -> Optional[int]:
    if not _inteiro(ttc) or int(ttc) < 0:
        raise SimulacaoErro("O custo de troca de contexto deve ser um inteiro maior ou igual a zero.")
    if protocolo not in PROTOCOLOS:
        raise SimulacaoErro("Heranca e teto sao mecanismos alternativos; escolha apenas uma opcao.")
    if envelhecimento and (not _inteiro(alpha) or int(alpha) < 0):
        raise SimulacaoErro("O passo de envelhecimento alfa deve ser um inteiro maior ou igual a zero.")

    if algoritmo == "RR":
        if quantum is None or str(quantum).strip() == "":
            raise SimulacaoErro("Informe o quantum para Round-Robin.")
        if not _inteiro(quantum) or int(quantum) <= 0:
            raise SimulacaoErro("O quantum deve ser um inteiro positivo.")
        if int(quantum) <= int(ttc):
            raise SimulacaoErro("No Round-Robin, o quantum deve ser maior que o custo da troca de contexto.")
        return int(quantum)

    return int(quantum) if quantum not in (None, "") and _inteiro(quantum) else None


def _validar_tarefas(tarefas: list[TarefaEntrada]) -> list[TarefaEntrada]:
    if not tarefas:
        raise SimulacaoErro("Adicione pelo menos uma tarefa.")

    ids = set()
    validadas: list[TarefaEntrada] = []
    for tarefa in tarefas:
        if not isinstance(tarefa, TarefaEntrada):
            tarefa = TarefaEntrada.de_json(tarefa)

        for campo, valor in {
            "id": tarefa.id,
            "ingresso": tarefa.ingresso,
            "tp": tarefa.tp,
            "prioridade": tarefa.prioridade,
        }.items():
            if not _inteiro(valor):
                raise SimulacaoErro(f"O campo {campo} da tarefa {tarefa.id} deve ser inteiro.")

        if tarefa.id <= 0:
            raise SimulacaoErro("O identificador da tarefa deve ser positivo.")
        if tarefa.id in ids:
            raise SimulacaoErro(f"O identificador {tarefa.id} esta duplicado.")
        ids.add(tarefa.id)

        if tarefa.ingresso < 0:
            raise SimulacaoErro(f"A tarefa {tarefa.id} tem ingresso negativo.")
        if tarefa.tp <= 0:
            raise SimulacaoErro(f"A tarefa {tarefa.id} deve ter tempo de processamento maior que zero.")
        if tarefa.prioridade < 0:
            raise SimulacaoErro(f"A tarefa {tarefa.id} deve ter prioridade maior ou igual a zero.")

        inicio = tarefa.recurso_inicio
        duracao = tarefa.recurso_duracao
        if inicio is None and duracao == 0:
            validadas.append(tarefa)
            continue
        if inicio is None or duracao <= 0:
            raise SimulacaoErro(f"Informe inicio e duracao da secao critica da tarefa {tarefa.id}.")
        if not _inteiro(inicio) or not _inteiro(duracao):
            raise SimulacaoErro(f"A secao critica da tarefa {tarefa.id} deve usar valores inteiros.")
        if inicio < 0:
            raise SimulacaoErro(f"A secao critica da tarefa {tarefa.id} nao pode iniciar antes da execucao.")
        if duracao <= 0:
            raise SimulacaoErro(f"A duracao da secao critica da tarefa {tarefa.id} deve ser positiva.")
        if inicio + duracao > tarefa.tp:
            raise SimulacaoErro(f"A secao critica da tarefa {tarefa.id} deve ficar dentro do tempo de processamento.")
        validadas.append(tarefa)

    return validadas


def _inteiro(valor: object) -> bool:
    if isinstance(valor, bool):
        return False
    if isinstance(valor, int):
        return True
    if isinstance(valor, str):
        texto = valor.strip()
        if texto.startswith("-"):
            return texto[1:].isdigit()
        return texto.isdigit()
    return False
