from tkinter import messagebox, ttk

from src.control import Faixas, rodar_lote


def construir(notebook, estado):
    frame = ttk.Frame(notebook)

    ttk.Label(
        frame,
        text="Sorteia vários cenários e roda os 6 algoritmos em cada um, "
        "comparando as médias.",
        wraplength=600,
        justify="left",
    ).pack(padx=10, pady=10, anchor="w")

    form = ttk.Frame(frame)
    form.pack(pady=5)

    campos = {}
    linhas = [
        ("n_cenarios", "Nº de cenários:", "20"),
        ("n_tarefas", "Nº de tarefas por cenário:", "5"),
        ("ctx_time", "Tempo de troca de contexto (t_tc):", "0"),
        ("quantum", "Quantum do Round Robin (t_q):", "2"),
    ]
    for i, (chave, rotulo, padrao) in enumerate(linhas):
        ttk.Label(form, text=rotulo).grid(row=i, column=0, sticky="w", padx=5, pady=3)
        entrada = ttk.Entry(form, width=10)
        entrada.insert(0, padrao)
        entrada.grid(row=i, column=1, padx=5, pady=3)
        campos[chave] = entrada

    colunas = ("algoritmo", "T", "T_w", "primeira_execucao")
    titulos = ("Algoritmo", "T médio", "T_w médio", "1ª execução média")
    tabela = ttk.Treeview(frame, columns=colunas, show="headings", height=8)
    for col, titulo in zip(colunas, titulos):
        tabela.heading(col, text=titulo)
        tabela.column(col, anchor="center", width=130)
    tabela.pack(padx=10, pady=10, fill="x")

    def rodar():
        try:
            n_cenarios = int(campos["n_cenarios"].get())
            n_tarefas = int(campos["n_tarefas"].get())
            ctx_time = int(campos["ctx_time"].get())
            quantum = int(campos["quantum"].get())
        except ValueError:
            messagebox.showerror("Erro", "Todos os campos devem ser números inteiros.")
            return

        if quantum <= ctx_time:
            messagebox.showerror("Erro", "O quantum deve ser maior que o tempo de troca de contexto.")
            return

        try:
            resultado = rodar_lote(n_cenarios, n_tarefas, Faixas(), ctx_time, quantum)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        tabela.delete(*tabela.get_children())
        for alg, metricas in resultado.items():
            tabela.insert(
                "",
                "end",
                values=(
                    alg.nome_exibicao,
                    f"{metricas['T']:.2f}",
                    f"{metricas['T_w']:.2f}",
                    f"{metricas['primeira_execucao']:.2f}",
                ),
            )

    ttk.Button(frame, text="Rodar lote", command=rodar).pack(pady=10)

    return frame
