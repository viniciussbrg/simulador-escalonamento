"""Ponto de entrada do simulador de escalonamento de tarefas.

Abre com dois cliques e nao recebe nenhum argumento de linha de comando (R10).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def principal() -> None:
    try:
        from view import criar_janela
    except Exception:  # noqa: BLE001 - sem tkinter, ainda assim precisa avisar
        import traceback
        print(traceback.format_exc())
        input("\nNao foi possivel abrir a janela. Pressione Enter para fechar...")
        return
    criar_janela()


if __name__ == "__main__":
    principal()
