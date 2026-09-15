from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass(frozen=True)
class TarefaEntrada:
    id: int
    ingresso: int
    tp: int
    prioridade: int
    recurso_inicio: Optional[int] = None
    recurso_duracao: int = 0

    @property
    def usa_recurso(self) -> bool:
        return self.recurso_inicio is not None and self.recurso_duracao > 0

    @property
    def recurso_fim(self) -> Optional[int]:
        if not self.usa_recurso:
            return None
        return int(self.recurso_inicio) + int(self.recurso_duracao)

    def para_json(self) -> dict:
        return asdict(self)

    @classmethod
    def de_json(cls, dados: dict) -> "TarefaEntrada":
        return cls(
            id=int(dados["id"]),
            ingresso=int(dados["ingresso"]),
            tp=int(dados["tp"]),
            prioridade=int(dados["prioridade"]),
            recurso_inicio=(
                None
                if dados.get("recurso_inicio") in (None, "")
                else int(dados.get("recurso_inicio"))
            ),
            recurso_duracao=int(dados.get("recurso_duracao") or 0),
        )


@dataclass
class Intervalo:
    inicio: int
    fim: int
    tipo: str
    tarefa_id: Optional[int] = None
    rotulo: str = ""

    @property
    def duracao(self) -> int:
        return self.fim - self.inicio


@dataclass
class MetricaTarefa:
    id: int
    ingresso: int
    tp: int
    prioridade: int
    conclusao: int
    tt: int
    tw: int
    primeira_execucao: int


@dataclass
class ResultadoSimulacao:
    algoritmo: str
    protocolo_prioridade: str
    envelhecimento: bool
    alpha: int
    quantum: Optional[int]
    ttc: int
    eficiencia: Optional[float]
    trocas_contexto: int
    teto_recurso: Optional[int]
    tarefas: list[TarefaEntrada]
    metricas: list[MetricaTarefa]
    medias: dict[str, float]
    linha_tempo: list[Intervalo] = field(default_factory=list)
    execucoes_por_tarefa: dict[int, list[Intervalo]] = field(default_factory=dict)
    bloqueios_por_tarefa: dict[int, list[Intervalo]] = field(default_factory=dict)
    recurso_intervalos: list[Intervalo] = field(default_factory=list)

    def sequencia_execucao(self) -> list[tuple[int, int, int]]:
        return [
            (intervalo.tarefa_id, intervalo.inicio, intervalo.fim)
            for intervalo in self.linha_tempo
            if intervalo.tipo == "execucao" and intervalo.tarefa_id is not None
        ]
