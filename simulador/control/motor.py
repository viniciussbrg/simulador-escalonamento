"""Mecanismo de simulacao.

Este modulo contem o UNICO laco de simulacao do projeto. Ele avanca o relogio,
mantem o conjunto de tarefas prontas, cobra a troca de contexto, trata a
suspensao em recurso, aplica envelhecimento e coleta as metricas.

A politica -- a decisao de qual tarefa pronta recebe o processador -- e
fornecida de fora (ver control/politicas.py) e nunca esta escrita aqui.

Convencoes implementadas (secao 3 do enunciado):
  C1  tempo discreto, uma unidade por vez
  C2  valor maior de prioridade significa prioridade mais alta
  C3  desempate por menor ingresso, depois menor identificador
  C4  troca de contexto sempre que a tarefa despachada difere da ultima que
      ocupou o processador, inclusive no primeiro despacho
  C5  o custo da troca e descontado da fatia concedida, nunca somado
  C6  quem esgota o quantum volta a cauda depois de quem ingressou no mesmo
      instante
  C7  a secao critica e medida no tempo de execucao propria da tarefa
  C8  tw = tt - tp
  C9  o teto e calculado sobre quem declara secao critica, mesmo sem disputa
  C10 o envelhecimento conta desde o ultimo despacho, ou desde o ingresso
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from model.tarefa import Tarefa

SEM_PROTOCOLO = "nenhum"
HERANCA = "heranca"
TETO = "teto"

EXECUCAO = "execucao"
TROCA = "troca"


# ---------------------------------------------------------------------- #
@dataclass
class Estado:
    """Estado de execucao de uma tarefa dentro de uma simulacao."""

    tarefa: Tarefa
    restante: int
    executado: int = 0
    prioridade_atual: int = 0
    ultimo_despacho: Optional[int] = None
    primeira_execucao: Optional[int] = None
    conclusao: Optional[int] = None
    suspensa: bool = False
    detem_recurso: bool = False
    enfileirada: bool = False
    bloqueio_direto: int = 0
    bloqueio_inversao: int = 0
    culpados_inversao: set = field(default_factory=set)

    @property
    def identificador(self) -> int:
        return self.tarefa.identificador

    @property
    def ingresso(self) -> int:
        return self.tarefa.ingresso

    @property
    def prioridade_base(self) -> int:
        return self.tarefa.prioridade

    @property
    def concluida(self) -> bool:
        return self.conclusao is not None

    # metricas (R3) ----------------------------------------------------- #
    @property
    def tt(self) -> int:
        return self.conclusao - self.ingresso

    @property
    def tp(self) -> int:
        return self.tarefa.tp

    @property
    def tw(self) -> int:
        return self.tt - self.tp  # C8

    @property
    def espera_primeira_execucao(self) -> int:
        return self.primeira_execucao - self.ingresso


@dataclass
class Segmento:
    """Um intervalo continuo da linha do tempo, para o diagrama de tempo."""

    identificador: int
    inicio: int
    fim: int
    tipo: str = EXECUCAO
    detem_recurso: bool = False


@dataclass
class Resultado:
    algoritmo: str
    estados: List[Estado]
    segmentos: List[Segmento]
    trocas: int
    quantum: Optional[int]
    custo_troca: int
    alfa: int
    protocolo: str
    teto_recurso: Optional[int]
    instante_final: int

    # medias (R3) ------------------------------------------------------- #
    def _media(self, atributo: str) -> float:
        if not self.estados:
            return 0.0
        return sum(getattr(e, atributo) for e in self.estados) / len(self.estados)

    @property
    def tt_medio(self) -> float:
        return self._media("tt")

    @property
    def tw_medio(self) -> float:
        return self._media("tw")

    @property
    def primeira_execucao_media(self) -> float:
        return self._media("espera_primeira_execucao")

    @property
    def eficiencia(self) -> Optional[float]:
        """E = tq / (tq + ttc).

        E e propriedade da configuracao do escalonador, nao do conjunto de
        tarefas. Sem quantum ela NAO esta definida -- retorna None, e quem
        exibe deve escrever 'nao definida' em vez de um numero (R4).
        """
        if self.quantum is None:
            return None
        return self.quantum / (self.quantum + self.custo_troca)

    @property
    def houve_inversao(self) -> bool:
        return any(e.bloqueio_inversao > 0 for e in self.estados)

    def por_identificador(self, identificador: int) -> Estado:
        for estado in self.estados:
            if estado.identificador == identificador:
                return estado
        raise KeyError(f"t{identificador} nao participou da simulacao.")

    def execucoes(self) -> List["Segmento"]:
        """Segmentos de execucao com trechos contiguos da mesma tarefa fundidos."""
        fundidos: List[Segmento] = []
        for seg in self.segmentos:
            if seg.tipo != EXECUCAO:
                continue
            if (
                fundidos
                and fundidos[-1].identificador == seg.identificador
                and fundidos[-1].fim == seg.inicio
            ):
                fundidos[-1].fim = seg.fim
            else:
                fundidos.append(
                    Segmento(seg.identificador, seg.inicio, seg.fim, EXECUCAO, seg.detem_recurso)
                )
        return fundidos

    def sequencia(self) -> str:
        """Sequencia de execucao no formato t1[0,5) t4[5,8) ..."""
        return " ".join(
            f"t{s.identificador}[{s.inicio},{s.fim})" for s in self.execucoes()
        )


class ErroDeConfiguracao(ValueError):
    """Combinacao invalida de parametros do escalonador."""


# ---------------------------------------------------------------------- #
class Escalonador:
    """O mecanismo. Unico para os seis algoritmos."""

    def __init__(
        self,
        tarefas: List[Tarefa],
        politica,
        quantum: Optional[int] = None,
        custo_troca: int = 0,
        alfa: int = 0,
        protocolo: str = SEM_PROTOCOLO,
    ) -> None:
        if not tarefas:
            raise ErroDeConfiguracao("Nenhuma tarefa foi informada.")
        if custo_troca < 0:
            raise ErroDeConfiguracao("O custo da troca de contexto nao pode ser negativo.")
        if alfa < 0:
            raise ErroDeConfiguracao("O fator de envelhecimento nao pode ser negativo.")
        if protocolo not in (SEM_PROTOCOLO, HERANCA, TETO):
            raise ErroDeConfiguracao(f"Protocolo desconhecido: {protocolo}.")

        if politica.usa_quantum:
            if quantum is None:
                raise ErroDeConfiguracao("O Round-Robin exige um quantum.")
            if quantum <= custo_troca:
                raise ErroDeConfiguracao(
                    f"O quantum ({quantum}) precisa ser maior que o custo da troca "
                    f"({custo_troca}): se a troca consumisse a fatia inteira, nenhum "
                    "trabalho util seria realizado."
                )
        else:
            quantum = None

        self.politica = politica
        self.quantum = quantum
        self.custo_troca = custo_troca
        self.alfa = alfa
        self.protocolo = protocolo

        self.estados: List[Estado] = [
            Estado(tarefa=t, restante=t.tp, prioridade_atual=t.prioridade) for t in tarefas
        ]
        self.por_id: Dict[int, Estado] = {e.identificador: e for e in self.estados}

        # C9: o teto e calculado sobre quem DECLARA secao critica, ainda que a
        # disputa nunca chegue a ocorrer.
        usuarias = [t.prioridade for t in tarefas if t.usa_recurso]
        self.teto_recurso: Optional[int] = max(usuarias) if usuarias else None

        self.detentor: Optional[Estado] = None
        self.segmentos: List[Segmento] = []
        self.trocas = 0

    # ------------------------------------------------------------------ #
    # envelhecimento (R8 / C10)
    def prioridade_efetiva(self, estado: Estado, instante: int, corrente: Optional[Estado]) -> int:
        if estado is corrente or self.alfa == 0:
            return estado.prioridade_atual
        referencia = estado.ultimo_despacho if estado.ultimo_despacho is not None else estado.ingresso
        return estado.prioridade_atual + self.alfa * (instante - referencia)

    # ------------------------------------------------------------------ #
    def executar(self) -> Resultado:
        instante = 0
        corrente: Optional[Estado] = None
        ultimo_ocupante: Optional[Estado] = None
        fatia_restante = 0

        while any(not e.concluida for e in self.estados):
            self._registrar_ingressos(instante)

            prontas = self._prontas(instante)
            if not prontas:
                proximo = self._proximo_evento(instante)
                if proximo is None:
                    # Todas as tarefas restantes estao suspensas e ninguem pode
                    # liberar o recurso: impasse. Interrompe para nao girar.
                    break
                corrente = None
                fatia_restante = 0
                instante = proximo
                continue

            # --- decisao: qual tarefa recebe o processador ------------- #
            escolhida = corrente
            if corrente is None or fatia_restante <= 0:
                escolhida = self._melhor(prontas, instante, corrente)
            elif self.politica.preemptiva:
                candidata = self._melhor(prontas, instante, corrente)
                if candidata is not corrente and self._chave(
                    candidata, instante, corrente
                ) < self._chave(corrente, instante, corrente):
                    escolhida = candidata

            if escolhida is not corrente:
                if corrente is not None:
                    self.politica.devolver(corrente)
                self.politica.retirar(escolhida)
                corrente = escolhida
                fatia_restante = self.quantum if self.quantum is not None else 10**9

                # C4: troca sempre que a despachada difere da ultima ocupante,
                # inclusive no primeiro despacho.
                if ultimo_ocupante is not corrente:
                    self.trocas += 1
                    if self.custo_troca > 0:
                        self.segmentos.append(
                            Segmento(corrente.identificador, instante,
                                     instante + self.custo_troca, TROCA)
                        )
                        instante += self.custo_troca
                        self._registrar_ingressos(instante)
                    # C5: o custo sai da fatia concedida, nunca e somado a ela.
                    fatia_restante -= self.custo_troca
                ultimo_ocupante = corrente
                corrente.ultimo_despacho = instante  # C10
                if corrente.primeira_execucao is None:
                    corrente.primeira_execucao = instante

            # --- R5: aquisicao do recurso antes de executar a unidade --- #
            if self._precisa_do_recurso(corrente):
                if self.detentor is None:
                    self._adquirir(corrente)
                else:
                    self._suspender(corrente)
                    corrente = None
                    fatia_restante = 0
                    continue

            # --- execucao de uma unidade util (C1) ---------------------- #
            self._contabilizar_bloqueios(corrente)
            self._anotar_execucao(corrente, instante)
            corrente.executado += 1
            corrente.restante -= 1
            instante += 1
            fatia_restante -= 1
            self._registrar_ingressos(instante)

            if corrente.detem_recurso and corrente.executado >= (
                corrente.tarefa.sc_inicio + corrente.tarefa.sc_duracao
            ):
                self._liberar(corrente)

            if corrente.restante == 0:
                corrente.conclusao = instante
                if corrente.detem_recurso:
                    self._liberar(corrente)
                self.politica.concluir(corrente)
                corrente = None
                fatia_restante = 0
            elif fatia_restante <= 0:
                # C6: primeiro entram as que ingressaram neste instante, depois
                # a que esgotou o quantum volta a cauda.
                self._registrar_ingressos(instante)
                self.politica.devolver(corrente)
                corrente = None

        return Resultado(
            algoritmo=self.politica.nome,
            estados=self.estados,
            segmentos=self.segmentos,
            trocas=self.trocas,
            quantum=self.quantum,
            custo_troca=self.custo_troca,
            alfa=self.alfa,
            protocolo=self.protocolo,
            teto_recurso=self.teto_recurso,
            instante_final=instante,
        )

    # ------------------------------------------------------------------ #
    # apoio
    def _registrar_ingressos(self, instante: int) -> None:
        novas = [
            e for e in self.estados
            if not e.enfileirada and not e.concluida and e.ingresso <= instante
        ]
        for estado in sorted(novas, key=lambda e: (e.ingresso, e.identificador)):  # C3
            estado.enfileirada = True
            self.politica.ingressar(estado)

    def _prontas(self, instante: int) -> List[Estado]:
        return [
            e for e in self.estados
            if not e.concluida and not e.suspensa and e.ingresso <= instante
        ]

    def _proximo_evento(self, instante: int) -> Optional[int]:
        """Relogio ocioso: salta para o proximo instante de ingresso."""
        futuros = [
            e.ingresso for e in self.estados
            if not e.concluida and e.ingresso > instante
        ]
        return min(futuros) if futuros else None

    def _chave(self, estado: Estado, instante: int, corrente: Optional[Estado]):
        return self.politica.chave(estado, instante, self)

    def _melhor(self, prontas, instante, corrente) -> Estado:
        return min(prontas, key=lambda e: self.politica.chave(e, instante, self))

    def _anotar_execucao(self, estado: Estado, instante: int) -> None:
        if (
            self.segmentos
            and self.segmentos[-1].tipo == EXECUCAO
            and self.segmentos[-1].identificador == estado.identificador
            and self.segmentos[-1].fim == instante
            and self.segmentos[-1].detem_recurso == estado.detem_recurso
        ):
            self.segmentos[-1].fim = instante + 1
        else:
            self.segmentos.append(
                Segmento(estado.identificador, instante, instante + 1,
                         EXECUCAO, estado.detem_recurso)
            )

    # --- recurso de uso exclusivo (R5, R6, R7) ------------------------- #
    def _precisa_do_recurso(self, estado: Estado) -> bool:
        return (
            estado.tarefa.usa_recurso
            and not estado.detem_recurso
            and estado.executado == estado.tarefa.sc_inicio
        )

    def _adquirir(self, estado: Estado) -> None:
        self.detentor = estado
        estado.detem_recurso = True
        if self.protocolo == TETO and self.teto_recurso is not None:
            # R7: preventivo -- basta existir detentor.
            estado.prioridade_atual = max(estado.prioridade_atual, self.teto_recurso)

    def _suspender(self, estado: Estado) -> None:
        estado.suspensa = True
        self.politica.retirar(estado)
        if self.protocolo == HERANCA:
            # R6: reativo -- so eleva porque ha tarefa bloqueada.
            self._aplicar_heranca()

    def _aplicar_heranca(self) -> None:
        if self.detentor is None:
            return
        bloqueadas = [e.prioridade_base for e in self.estados if e.suspensa]
        self.detentor.prioridade_atual = max([self.detentor.prioridade_base] + bloqueadas)

    def _liberar(self, estado: Estado) -> None:
        estado.detem_recurso = False
        self.detentor = None
        # A heranca e o teto sao temporarios e precisam ser revertidos (R6).
        estado.prioridade_atual = estado.prioridade_base
        for outra in self.estados:
            if outra.suspensa:
                outra.suspensa = False
                self.politica.ingressar(outra)

    def _contabilizar_bloqueios(self, corrente: Estado) -> None:
        """Distingue bloqueio direto de inversao de prioridades (R5)."""
        for estado in self.estados:
            if not estado.suspensa:
                continue
            if corrente is self.detentor:
                estado.bloqueio_direto += 1
            else:
                estado.bloqueio_inversao += 1
                estado.culpados_inversao.add(corrente.identificador)
