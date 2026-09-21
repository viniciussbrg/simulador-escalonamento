from dataclasses import dataclass, field

from src.model.processo import Processo


@dataclass
class UltimoResultado:
    """Guarda o suficiente da última simulação para a aba Resultado montar a
    tabela por tarefa e calcular E — tudo aqui já é derivável de
    Processo.get_turnaround()/get_espera(), sem precisar de nenhuma função
    nova no control."""

    processos: list[Processo]
    nome_algoritmo: str
    quantum: int | None
    ctx_time: float


@dataclass
class AppState:
    tarefas: list[Processo] = field(default_factory=list)
    ultimo_resultado: UltimoResultado | None = None
