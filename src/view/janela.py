import tkinter as tk
from tkinter import ttk

from src.view import aba_lote, aba_parametros, aba_resultado, aba_tarefas
from src.view.estado import AppState


def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)

    janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")


def criar_janela():
    janela = tk.Tk()
    janela.title("Simulador de Escalonamento")
    janela.minsize(700, 550)
    centralizar_janela(janela, 950, 700)

    estado = AppState()

    notebook = ttk.Notebook(janela)
    notebook.pack(fill="both", expand=True)

    frame_tarefas = aba_tarefas.construir(notebook, estado)
    frame_resultado, atualizar_resultado = aba_resultado.construir(notebook, estado)
    frame_parametros = aba_parametros.construir(
        notebook, estado, lambda: notebook.select(frame_resultado), atualizar_resultado
    )
    frame_lote = aba_lote.construir(notebook, estado)

    notebook.add(frame_tarefas, text="Tarefas")
    notebook.add(frame_parametros, text="Parâmetros")
    notebook.add(frame_resultado, text="Resultado")
    notebook.add(frame_lote, text="Lote de Cenários")

    janela.mainloop()
