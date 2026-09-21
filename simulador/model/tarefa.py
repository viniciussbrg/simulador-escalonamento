"""Modelo de tarefa e validacao de entrada (R2).

Uma tarefa e descrita por identificador, instante de ingresso, tempo de
processamento (tp) e prioridade. Opcionalmente declara uma secao critica
sobre o recurso R, medida no tempo de execucao PROPRIA da tarefa (C7).
"""

from dataclasses import dataclass
from typing import Optional


class EntradaInvalida(ValueError):
    """Erro de validacao com mensagem legivel para o usuario final."""


@dataclass
class Tarefa:
    identificador: int
    ingresso: int
    tp: int
    prioridade: int
    sc_inicio: Optional[int] = None
    sc_duracao: int = 0

    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not isinstance(self.identificador, int) or self.identificador < 1:
            raise EntradaInvalida("O identificador deve ser um inteiro maior ou igual a 1.")
        if not isinstance(self.ingresso, int) or self.ingresso < 0:
            raise EntradaInvalida(
                f"t{self.identificador}: o instante de ingresso nao pode ser negativo."
            )
        if not isinstance(self.tp, int) or self.tp <= 0:
            raise EntradaInvalida(
                f"t{self.identificador}: o tempo de processamento deve ser positivo."
            )
        if not isinstance(self.prioridade, int) or self.prioridade < 1:
            raise EntradaInvalida(
                f"t{self.identificador}: a prioridade deve ser um inteiro maior ou igual a 1."
            )
        if self.sc_inicio is None:
            if self.sc_duracao:
                raise EntradaInvalida(
                    f"t{self.identificador}: duracao de secao critica sem instante de inicio."
                )
            self.sc_duracao = 0
            return
        if self.sc_inicio < 0:
            raise EntradaInvalida(
                f"t{self.identificador}: o inicio da secao critica nao pode ser negativo."
            )
        if self.sc_duracao <= 0:
            raise EntradaInvalida(
                f"t{self.identificador}: a duracao da secao critica deve ser positiva."
            )
        if self.sc_inicio + self.sc_duracao > self.tp:
            raise EntradaInvalida(
                f"t{self.identificador}: a secao critica [{self.sc_inicio}, "
                f"{self.sc_inicio + self.sc_duracao}) nao cabe na duracao {self.tp} da tarefa."
            )

    # ------------------------------------------------------------------ #
    @property
    def usa_recurso(self) -> bool:
        return self.sc_inicio is not None

    @property
    def nome(self) -> str:
        return f"t{self.identificador}"

    def descricao_sc(self) -> str:
        if not self.usa_recurso:
            return "-"
        return f"[{self.sc_inicio}, {self.sc_inicio + self.sc_duracao})"

    def clonar(self) -> "Tarefa":
        """Copia independente, para rodar varios algoritmos sobre o mesmo cenario."""
        return Tarefa(
            self.identificador, self.ingresso, self.tp, self.prioridade,
            self.sc_inicio, self.sc_duracao,
        )

    # ------------------------------------------------------------------ #
    def para_dicionario(self) -> dict:
        dados = {
            "id": self.identificador,
            "ingresso": self.ingresso,
            "tp": self.tp,
            "prioridade": self.prioridade,
        }
        if self.usa_recurso:
            dados["sc_inicio"] = self.sc_inicio
            dados["sc_duracao"] = self.sc_duracao
        return dados

    @staticmethod
    def de_dicionario(dados: dict) -> "Tarefa":
        try:
            return Tarefa(
                identificador=int(dados["id"]),
                ingresso=int(dados["ingresso"]),
                tp=int(dados["tp"]),
                prioridade=int(dados["prioridade"]),
                sc_inicio=(int(dados["sc_inicio"]) if dados.get("sc_inicio") is not None else None),
                sc_duracao=int(dados.get("sc_duracao", 0) or 0),
            )
        except (KeyError, TypeError, ValueError) as erro:
            raise EntradaInvalida(f"Tarefa malformada no arquivo de cenario: {erro}") from erro
