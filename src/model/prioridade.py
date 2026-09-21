from dataclasses import dataclass


@dataclass
class Prioridade:
    numero: int

    def __post_init__(self):
        if not isinstance(self.numero, int):
            raise TypeError("numero deve ser um inteiro.")
        if self.numero < 0:
            raise ValueError("numero deve ser não-negativo.")
