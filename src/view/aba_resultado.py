import tkinter as tk
from tkinter import ttk

from src.control import classificar_suspensoes
from src.view.diagrama import COR_CTX, COR_ESPERA, COR_EXECUCAO, COR_SUSPENSA, desenhar_diagrama
from src.view.estado import UltimoResultado

_TIPO_EXIBICAO = {
    "bloqueio_direto": "Bloqueio direto",
    "inversao": "Inversão de prioridades",
}


def construir(notebook, estado):
    frame = ttk.Frame(notebook)

    resumo_var = tk.StringVar(value="Rode uma simulação na aba Parâmetros.")
    ttk.Label(frame, textvariable=resumo_var, font=("TkDefaultFont", 11, "bold")).pack(pady=8)

    colunas = ("id", "chegada", "t_p", "T", "T_w", "primeira_execucao")
    titulos = ("ID", "Chegada", "t_p", "T", "T_w", "1ª execução")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=8)
    for col, titulo in zip(colunas, titulos):
        tabela.heading(col, text=titulo)
        tabela.column(col, anchor="center", width=90)
    tabela.pack(padx=10, pady=5, fill="x")

    legenda = ttk.Frame(frame)
    legenda.pack(pady=2)
    itens_legenda = (
        (COR_EXECUCAO, "Execução"),
        (COR_CTX, "Troca de contexto"),
        (COR_ESPERA, "Espera"),
        (COR_SUSPENSA, "Suspensa (recurso)"),
    )
    for cor, texto in itens_legenda:
        item = tk.Canvas(legenda, width=14, height=14, highlightthickness=0)
        item.create_rectangle(1, 1, 13, 13, fill=cor, outline=cor)
        item.pack(side="left", padx=(10, 2))
        ttk.Label(legenda, text=texto).pack(side="left")

    canvas_frame = ttk.Frame(frame)
    canvas_frame.pack(padx=10, pady=5, fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame, bg="white", height=220)
    scroll_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=scroll_x.set)
    canvas.pack(side="top", fill="both", expand=True)
    scroll_x.pack(side="bottom", fill="x")

    recursos_frame = ttk.LabelFrame(frame, text="Bloqueios por recurso")
    colunas_recursos = ("tarefa", "recurso", "inicio", "fim", "tipo")
    titulos_recursos = ("Tarefa", "Recurso", "Início", "Fim", "Classificação")
    tabela_recursos = ttk.Treeview(recursos_frame, columns=colunas_recursos, show="headings", height=4)
    for col, titulo in zip(colunas_recursos, titulos_recursos):
        tabela_recursos.heading(col, text=titulo)
        tabela_recursos.column(col, anchor="center", width=100)
    tabela_recursos.pack(padx=5, pady=5, fill="x")

    def atualizar(processos, nome_algoritmo, quantum, ctx_time):
        estado.ultimo_resultado = UltimoResultado(processos, nome_algoritmo, quantum, ctx_time)

        tabela.delete(*tabela.get_children())
        for p in processos:
            tabela.insert(
                "",
                "end",
                values=(
                    p.id,
                    p.chegada,
                    p.duracao,
                    f"{p.get_turnaround():.2f}",
                    f"{p.get_espera():.2f}",
                    f"{p.get_tempo_ate_primeira_execucao():.2f}",
                ),
            )

        media_T = sum(p.get_turnaround() for p in processos) / len(processos)
        media_Tw = sum(p.get_espera() for p in processos) / len(processos)

        if quantum is not None:
            eficiencia_texto = f"{quantum / (quantum + ctx_time):.3f}"
        else:
            eficiencia_texto = "não definida"

        resumo_var.set(
            f"{nome_algoritmo} — T médio: {media_T:.2f}   T_w médio: {media_Tw:.2f}   E: {eficiencia_texto}"
        )

        desenhar_diagrama(canvas, processos)

        suspensoes = classificar_suspensoes(processos)
        tabela_recursos.delete(*tabela_recursos.get_children())
        if suspensoes:
            recursos_frame.pack(padx=10, pady=(0, 10), fill="x")
            for ev in suspensoes:
                tabela_recursos.insert(
                    "",
                    "end",
                    values=(
                        f"Tarefa {ev['tarefa']}",
                        ev["recurso"],
                        ev["inicio"],
                        ev["fim"],
                        _TIPO_EXIBICAO[ev["tipo"]],
                    ),
                )
        else:
            recursos_frame.pack_forget()

    return frame, atualizar
