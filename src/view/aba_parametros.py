import tkinter as tk
from tkinter import messagebox, ttk

from src.control import simular_escalonamento
from src.control.algoritmos.nomes import Algoritmo

_PROTOCOLOS = {"Nenhum": None, "Herança": "heranca", "Teto": "teto"}


def construir(notebook, estado, ir_para_resultado, atualizar_resultado):
    frame = ttk.Frame(notebook)

    algoritmo_var = tk.IntVar(value=Algoritmo.FCFS.value)

    algoritmos_frame = ttk.LabelFrame(frame, text="Algoritmo")
    algoritmos_frame.pack(padx=10, pady=10, fill="x")

    params_frame = ttk.LabelFrame(frame, text="Parâmetros")
    params_frame.pack(padx=10, pady=10, fill="x")

    ttk.Label(params_frame, text="Tempo de troca de contexto (t_tc):").grid(
        row=0, column=0, sticky="w", padx=5, pady=5
    )
    entrada_ctx = ttk.Entry(params_frame, width=10)
    entrada_ctx.insert(0, "0")
    entrada_ctx.grid(row=0, column=1, padx=5)

    label_quantum = ttk.Label(params_frame, text="Quantum (t_q):")
    entrada_quantum = ttk.Entry(params_frame, width=10)
    entrada_quantum.insert(0, "2")

    label_alfa = ttk.Label(params_frame, text="Envelhecimento (α):")
    entrada_alfa = ttk.Entry(params_frame, width=10)
    entrada_alfa.insert(0, "0")

    protocolo_var = tk.StringVar(value="Nenhum")
    label_protocolo = ttk.Label(params_frame, text="Protocolo de recurso:")
    protocolo_frame = ttk.Frame(params_frame)
    for nome in _PROTOCOLOS:
        ttk.Radiobutton(protocolo_frame, text=nome, variable=protocolo_var, value=nome).pack(side="left", padx=(0, 10))

    def atualizar_campos_visiveis():
        if algoritmo_var.get() == Algoritmo.ROUND_ROBIN.value:
            label_quantum.grid(row=1, column=0, sticky="w", padx=5, pady=5)
            entrada_quantum.grid(row=1, column=1, padx=5)
        else:
            label_quantum.grid_forget()
            entrada_quantum.grid_forget()

        if algoritmo_var.get() == Algoritmo.PRIORIDADE_COOPERATIVO.value:
            label_alfa.grid(row=2, column=0, sticky="w", padx=5, pady=5)
            entrada_alfa.grid(row=2, column=1, padx=5)
        else:
            label_alfa.grid_forget()
            entrada_alfa.grid_forget()

        if algoritmo_var.get() == Algoritmo.PRIORIDADE_PREEMPTIVO.value:
            label_protocolo.grid(row=3, column=0, sticky="w", padx=5, pady=5)
            protocolo_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=5)
        else:
            label_protocolo.grid_forget()
            protocolo_frame.grid_forget()

    for i, alg in enumerate(Algoritmo):
        ttk.Radiobutton(
            algoritmos_frame,
            text=f"{alg.value}. {alg.nome_exibicao}",
            variable=algoritmo_var,
            value=alg.value,
            command=atualizar_campos_visiveis,
        ).grid(row=i // 2, column=i % 2, sticky="w", padx=10, pady=2)

    def simular():
        try:
            ctx_time = int(entrada_ctx.get())
            if ctx_time < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Tempo de troca de contexto inválido. Use um número inteiro não-negativo.")
            return

        quantum_entry = "0"
        if algoritmo_var.get() == Algoritmo.ROUND_ROBIN.value:
            quantum_entry = entrada_quantum.get()
            if not quantum_entry.strip().isdigit():
                messagebox.showerror("Erro", "Quantum inválido. Use um número inteiro maior que zero.")
                return

        alfa = 0
        if algoritmo_var.get() == Algoritmo.PRIORIDADE_COOPERATIVO.value:
            try:
                alfa = int(entrada_alfa.get())
            except ValueError:
                messagebox.showerror("Erro", "Envelhecimento (α) inválido. Use um número inteiro.")
                return

        protocolo = None
        if algoritmo_var.get() == Algoritmo.PRIORIDADE_PREEMPTIVO.value:
            protocolo = _PROTOCOLOS[protocolo_var.get()]

        try:
            _, _, nome_algoritmo, processos_simulados = simular_escalonamento(
                estado.tarefas, algoritmo_var.get(), quantum_entry, ctx_time, alfa, protocolo
            )
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        quantum_usado = int(quantum_entry) if algoritmo_var.get() == Algoritmo.ROUND_ROBIN.value else None
        atualizar_resultado(processos_simulados, nome_algoritmo, quantum_usado, ctx_time)
        ir_para_resultado()

    ttk.Button(frame, text="Simular", command=simular).pack(pady=15)

    atualizar_campos_visiveis()
    return frame
