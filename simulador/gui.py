from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .cenarios import (
    carregar_cenario,
    cenario_aula5,
    cenario_inanicao,
    cenario_inversao_prioridade,
    cenario_teto_sem_disputa,
    comparar_lote,
    gerar_tarefas,
    salvar_cenario,
)
from .modelos import ResultadoSimulacao, TarefaEntrada
from .motor import ALGORITMOS, PROTOCOLOS, SimulacaoErro, simular


class AplicacaoSimulador(tk.Tk):
    CORES_TAREFAS = (
        "#14b8a6",
        "#2dd4bf",
        "#0ea5a4",
        "#5eead4",
        "#06b6d4",
        "#22c55e",
        "#38bdf8",
        "#a3e635",
    )

    def __init__(self) -> None:
        super().__init__()
        self.title("Simulador de Escalonamento de Tarefas")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.tarefas: list[TarefaEntrada] = []
        self.resultado: ResultadoSimulacao | None = None

        self._criar_variaveis()
        self._configurar_estilo()
        self._montar_interface()
        self._carregar_cenario(cenario_aula5())

    def _criar_variaveis(self) -> None:
        self.quantidade_var = tk.StringVar(value="5")
        self.id_var = tk.StringVar(value="1")
        self.ingresso_var = tk.StringVar(value="0")
        self.tp_var = tk.StringVar(value="1")
        self.prioridade_var = tk.StringVar(value="1")
        self.recurso_inicio_var = tk.StringVar(value="")
        self.recurso_duracao_var = tk.StringVar(value="")

        self.algoritmo_var = tk.StringVar(value="FCFS")
        self.quantum_var = tk.StringVar(value="2")
        self.ttc_var = tk.StringVar(value="0")
        self.protocolo_var = tk.StringVar(value="nenhum")
        self.envelhecimento_var = tk.BooleanVar(value=False)
        self.alpha_var = tk.StringVar(value="1")

        self.lote_cenarios_var = tk.StringVar(value="50")
        self.lote_tarefas_var = tk.StringVar(value="5")
        self.lote_ingresso_var = tk.StringVar(value="8")
        self.lote_tp_var = tk.StringVar(value="6")
        self.lote_prioridade_var = tk.StringVar(value="5")

    def _configurar_estilo(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(background="#edf5f4")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#1f3534", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"), foreground="#173b3a")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#587270")
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#0f766e")
        style.configure("TButton", background="#f1f5f4", foreground="#24403e", font=("Segoe UI", 10), padding=(10, 6), borderwidth=1, bordercolor="#cbd9d7")
        style.map("TButton", background=[("active", "#e0ecea"), ("pressed", "#d1e2df")])
        style.configure("Accent.TButton", background="#0f766e", foreground="#ffffff", font=("Segoe UI", 10, "bold"), padding=(12, 7), borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#0d9488"), ("pressed", "#115e59")])
        style.configure("TEntry", fieldbackground="#ffffff", foreground="#1f3534", insertcolor="#0f766e", bordercolor="#b8cecb", lightcolor="#b8cecb", darkcolor="#b8cecb", padding=6)
        style.configure("TCombobox", fieldbackground="#ffffff", background="#f1f5f4", foreground="#1f3534", arrowcolor="#0f766e", padding=5)
        style.map("TCombobox", fieldbackground=[("readonly", "#ffffff")], foreground=[("readonly", "#1f3534")], selectbackground=[("readonly", "#e0ecea")], selectforeground=[("readonly", "#1f3534")])
        style.configure("TCheckbutton", background="#ffffff", foreground="#1f3534")
        style.map("TCheckbutton", background=[("active", "#ffffff")], foreground=[("active", "#0f766e")])
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#1f3534", font=("Segoe UI", 9), rowheight=28, bordercolor="#cbd9d7")
        style.map("Treeview", background=[("selected", "#d3eeea")], foreground=[("selected", "#134e4a")])
        style.configure("Treeview.Heading", background="#eff6f5", foreground="#28514e", font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 7))
        style.map("Treeview.Heading", background=[("active", "#dcecea")])
        style.configure("TNotebook", background="#ffffff", borderwidth=0)
        style.configure("TNotebook.Tab", background="#eff4f3", foreground="#587270", padding=(16, 9), font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff"), ("active", "#e0ecea")], foreground=[("selected", "#0f766e"), ("active", "#28514e")])
        style.configure("Horizontal.TScrollbar", background="#a9c5c1", troughcolor="#eff4f3", bordercolor="#eff4f3", arrowcolor="#0f766e")
        style.configure("Vertical.TScrollbar", background="#a9c5c1", troughcolor="#eff4f3", bordercolor="#eff4f3", arrowcolor="#0f766e")

    def _montar_interface(self) -> None:
        container = ttk.Frame(self, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        cabecalho = ttk.Frame(container)
        cabecalho.pack(fill=tk.X)
        ttk.Label(cabecalho, text="Simulador de Escalonamento", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(cabecalho, text="Configure tarefas, execute políticas e compare o comportamento da CPU.", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(2, 0))

        self.abas = ttk.Notebook(container)
        self.abas.pack(fill=tk.BOTH, expand=True, pady=(16, 0))

        self.aba_tarefas = ttk.Frame(self.abas, padding=16)
        self.aba_resultados = ttk.Frame(self.abas, padding=16)
        self.aba_lote = ttk.Frame(self.abas, padding=16)
        self.abas.add(self.aba_tarefas, text="Tarefas e simulação")
        self.abas.add(self.aba_resultados, text="Resultados")
        self.abas.add(self.aba_lote, text="Comparação em lote")

        self._montar_aba_tarefas()
        self._montar_aba_resultados()
        self._montar_aba_lote()

    def _montar_aba_tarefas(self) -> None:
        painel = ttk.Frame(self.aba_tarefas)
        painel.pack(fill=tk.BOTH, expand=True)
        painel.columnconfigure(1, weight=1)
        painel.rowconfigure(0, weight=1)

        sidebar = ttk.Frame(painel)
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        sidebar.rowconfigure(0, weight=1)
        sidebar.columnconfigure(0, weight=1)
        self.canvas_sidebar = tk.Canvas(sidebar, background="#ffffff", highlightthickness=0, width=252)
        self.canvas_sidebar.grid(row=0, column=0, sticky="nsew")
        scroll_sidebar = ttk.Scrollbar(sidebar, orient=tk.VERTICAL, command=self.canvas_sidebar.yview)
        scroll_sidebar.grid(row=0, column=1, sticky="ns")
        self.canvas_sidebar.configure(yscrollcommand=scroll_sidebar.set)
        self.canvas_sidebar.bind("<Enter>", self._ativar_scroll_sidebar)
        self.canvas_sidebar.bind("<Leave>", self._desativar_scroll_sidebar)

        formulario = ttk.Frame(self.canvas_sidebar)
        self._janela_sidebar = self.canvas_sidebar.create_window((0, 0), window=formulario, anchor=tk.NW)
        formulario.bind("<Configure>", self._atualizar_scroll_sidebar)
        self.canvas_sidebar.bind("<Configure>", self._ajustar_largura_sidebar)

        ttk.Label(formulario, text="Cadastro", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 8))
        self._campo(formulario, "Quantidade", self.quantidade_var, 1, largura=12)
        ttk.Button(formulario, text="Aplicar quantidade", command=self._aplicar_quantidade).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        self._campo(formulario, "ID", self.id_var, 3, largura=12)
        self._campo(formulario, "Ingresso", self.ingresso_var, 4, largura=12)
        self._campo(formulario, "tp", self.tp_var, 5, largura=12)
        self._campo(formulario, "Prioridade", self.prioridade_var, 6, largura=12)
        self._campo(formulario, "R após exec.", self.recurso_inicio_var, 7, largura=12)
        self._campo(formulario, "R duração", self.recurso_duracao_var, 8, largura=12)

        ttk.Button(formulario, text="Adicionar / atualizar", command=self._adicionar_ou_atualizar).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        ttk.Button(formulario, text="Remover selecionada", command=self._remover_tarefa).grid(row=10, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(formulario, text="Limpar tarefas", command=self._limpar_tarefas).grid(row=11, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(formulario, text="Sortear tarefas", command=self._sortear_tarefas).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(12, 4))
        ttk.Button(formulario, text="Salvar cenário", command=self._salvar_cenario).grid(row=13, column=0, columnspan=2, sticky="ew", pady=4)
        ttk.Button(formulario, text="Carregar cenário", command=self._abrir_cenario).grid(row=14, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Label(formulario, text="Cenários oficiais", style="Section.TLabel").grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=(18, 8))
        ttk.Button(formulario, text="Aula 5", command=lambda: self._carregar_cenario(cenario_aula5())).grid(row=16, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(formulario, text="Inversão", command=self._carregar_inversao).grid(row=17, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(formulario, text="Teto sem disputa", command=self._carregar_teto_sem_disputa).grid(row=18, column=0, columnspan=2, sticky="ew", pady=3)
        ttk.Button(formulario, text="Inanição", command=self._carregar_inanicao).grid(row=19, column=0, columnspan=2, sticky="ew", pady=3)

        direita = ttk.Frame(painel)
        direita.grid(row=0, column=1, sticky="nsew")
        direita.rowconfigure(1, weight=1)
        direita.columnconfigure(0, weight=1)

        ttk.Label(direita, text="Tarefas", style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)
        colunas = ("id", "ingresso", "tp", "prioridade", "recurso_inicio", "recurso_duracao")
        self.tabela_tarefas = ttk.Treeview(direita, columns=colunas, show="headings", height=10)
        titulos = {
            "id": "ID",
            "ingresso": "Ingresso",
            "tp": "tp",
            "prioridade": "Prioridade",
            "recurso_inicio": "R após exec.",
            "recurso_duracao": "R duração",
        }
        for coluna in colunas:
            self.tabela_tarefas.heading(coluna, text=titulos[coluna])
            self.tabela_tarefas.column(coluna, width=120, anchor=tk.CENTER)
        self.tabela_tarefas.grid(row=1, column=0, sticky="nsew", pady=(8, 14))
        self.tabela_tarefas.bind("<<TreeviewSelect>>", self._selecionar_tarefa)

        parametros = ttk.Frame(direita)
        parametros.grid(row=2, column=0, sticky="ew")
        for coluna in range(6):
            parametros.columnconfigure(coluna, weight=1)

        ttk.Label(parametros, text="Algoritmo").grid(row=0, column=0, sticky=tk.W)
        algoritmo_combo = ttk.Combobox(parametros, values=list(ALGORITMOS), textvariable=self.algoritmo_var, state="readonly", width=14)
        algoritmo_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ttk.Label(parametros, text="Quantum").grid(row=0, column=1, sticky=tk.W)
        ttk.Entry(parametros, textvariable=self.quantum_var, width=10).grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ttk.Label(parametros, text="ttc").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(parametros, textvariable=self.ttc_var, width=10).grid(row=1, column=2, sticky="ew", padx=(0, 8))

        ttk.Label(parametros, text="Mecanismo").grid(row=0, column=3, sticky=tk.W)
        ttk.Combobox(parametros, values=list(PROTOCOLOS), textvariable=self.protocolo_var, state="readonly", width=14).grid(row=1, column=3, sticky="ew", padx=(0, 8))

        ttk.Checkbutton(parametros, text="Envelhecimento", variable=self.envelhecimento_var).grid(row=1, column=4, sticky=tk.W, padx=(0, 8))

        ttk.Label(parametros, text="alpha").grid(row=0, column=5, sticky=tk.W)
        ttk.Entry(parametros, textvariable=self.alpha_var, width=10).grid(row=1, column=5, sticky="ew")

        ttk.Button(direita, text="Simular e ver resultados", command=self._executar_simulacao, style="Accent.TButton").grid(row=3, column=0, sticky="ew", pady=(16, 0))

    def _montar_aba_resultados(self) -> None:
        self.aba_resultados.rowconfigure(3, weight=1)
        self.aba_resultados.columnconfigure(0, weight=1)

        self.resumo_var = tk.StringVar(value="Execute uma simulação para visualizar as métricas.")
        ttk.Label(self.aba_resultados, textvariable=self.resumo_var, style="Section.TLabel").grid(row=0, column=0, sticky=tk.W)

        colunas = ("id", "ingresso", "tp", "prioridade", "conclusao", "tt", "tw", "primeira")
        self.tabela_metricas = ttk.Treeview(self.aba_resultados, columns=colunas, show="headings", height=7)
        titulos = {
            "id": "ID",
            "ingresso": "Ingresso",
            "tp": "tp",
            "prioridade": "Prioridade",
            "conclusao": "Conclusão",
            "tt": "tt",
            "tw": "tw",
            "primeira": "Até 1a exec.",
        }
        for coluna in colunas:
            self.tabela_metricas.heading(coluna, text=titulos[coluna])
            self.tabela_metricas.column(coluna, width=110, anchor=tk.CENTER)
        self.tabela_metricas.grid(row=1, column=0, sticky="ew", pady=(8, 10))

        self.medias_var = tk.StringVar(value="")
        ttk.Label(self.aba_resultados, textvariable=self.medias_var).grid(row=2, column=0, sticky=tk.W, pady=(0, 8))

        canvas_frame = ttk.Frame(self.aba_resultados)
        canvas_frame.grid(row=3, column=0, sticky="nsew")
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, background="#ffffff", highlightthickness=1, highlightbackground="#cbd9d7")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<MouseWheel>", self._rolar_resultados)
        self.canvas.bind("<Button-4>", self._rolar_resultados)
        self.canvas.bind("<Button-5>", self._rolar_resultados)
        scroll_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        scroll_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        self.sequencia_texto = tk.Text(self.aba_resultados, height=4, wrap=tk.WORD, font=("Consolas", 9), background="#f5f9f8", foreground="#24403e", insertbackground="#0f766e", relief=tk.FLAT, padx=10, pady=8)
        self.sequencia_texto.grid(row=4, column=0, sticky="ew", pady=(10, 0))

    def _montar_aba_lote(self) -> None:
        topo = ttk.Frame(self.aba_lote)
        topo.pack(fill=tk.X)
        for coluna in range(7):
            topo.columnconfigure(coluna, weight=1)

        self._campo_lote(topo, "Cenários", self.lote_cenarios_var, 0)
        self._campo_lote(topo, "Tarefas", self.lote_tarefas_var, 1)
        self._campo_lote(topo, "Ingresso máx.", self.lote_ingresso_var, 2)
        self._campo_lote(topo, "tp máx.", self.lote_tp_var, 3)
        self._campo_lote(topo, "Prioridade máx.", self.lote_prioridade_var, 4)
        ttk.Button(topo, text="Executar lote", command=self._executar_lote).grid(row=1, column=5, columnspan=2, sticky="ew", padx=(8, 0))

        colunas = ("algoritmo", "tt", "tw", "primeira")
        self.tabela_lote = ttk.Treeview(self.aba_lote, columns=colunas, show="headings", height=9)
        for coluna, titulo in {
            "algoritmo": "Algoritmo",
            "tt": "Média tt",
            "tw": "Média tw",
            "primeira": "Média até 1a exec.",
        }.items():
            self.tabela_lote.heading(coluna, text=titulo)
            self.tabela_lote.column(coluna, width=180, anchor=tk.CENTER)
        self.tabela_lote.pack(fill=tk.BOTH, expand=True, pady=(14, 10))

        self.lote_info_var = tk.StringVar(value="O lote sorteia cenários diferentes e compara os seis algoritmos pelas médias.")
        ttk.Label(self.aba_lote, textvariable=self.lote_info_var).pack(anchor=tk.W)

    def _campo(self, pai: ttk.Frame, texto: str, variavel: tk.StringVar, linha: int, largura: int = 16) -> None:
        ttk.Label(pai, text=texto).grid(row=linha, column=0, sticky=tk.W, pady=3)
        ttk.Entry(pai, textvariable=variavel, width=largura).grid(row=linha, column=1, sticky="ew", pady=3)

    def _campo_lote(self, pai: ttk.Frame, texto: str, variavel: tk.StringVar, coluna: int) -> None:
        ttk.Label(pai, text=texto).grid(row=0, column=coluna, sticky=tk.W, padx=(0, 8))
        ttk.Entry(pai, textvariable=variavel, width=12).grid(row=1, column=coluna, sticky="ew", padx=(0, 8))

    def _atualizar_scroll_sidebar(self, _evento: object) -> None:
        self.canvas_sidebar.configure(scrollregion=self.canvas_sidebar.bbox("all"))

    def _ajustar_largura_sidebar(self, evento: tk.Event) -> None:
        self.canvas_sidebar.itemconfigure(self._janela_sidebar, width=evento.width)

    def _ativar_scroll_sidebar(self, _evento: object) -> None:
        self.bind_all("<MouseWheel>", self._rolar_sidebar)

    def _desativar_scroll_sidebar(self, _evento: object) -> None:
        self.unbind_all("<MouseWheel>")

    def _rolar_sidebar(self, evento: tk.Event) -> None:
        self.canvas_sidebar.yview_scroll(-int(evento.delta / 120), "units")

    def _rolar_resultados(self, evento: tk.Event) -> None:
        if getattr(evento, "num", None) == 4:
            self.canvas.yview_scroll(-1, "units")
        elif getattr(evento, "num", None) == 5:
            self.canvas.yview_scroll(1, "units")
        elif getattr(evento, "delta", 0):
            self.canvas.yview_scroll(-int(evento.delta / 120), "units")

    def _aplicar_quantidade(self) -> None:
        try:
            quantidade = self._inteiro(self.quantidade_var.get(), "Quantidade")
            if quantidade <= 0:
                raise SimulacaoErro("A quantidade de tarefas deve ser positiva.")
            self.tarefas = [TarefaEntrada(id=i, ingresso=0, tp=1, prioridade=1) for i in range(1, quantidade + 1)]
            self._atualizar_tabela_tarefas()
        except Exception as erro:
            self._mostrar_erro(erro)

    def _adicionar_ou_atualizar(self) -> None:
        try:
            tarefa = self._ler_tarefa_formulario()
            outras = [item for item in self.tarefas if item.id != tarefa.id]
            simular(outras + [tarefa], "FCFS", ttc=0)
            self.tarefas = sorted(outras + [tarefa], key=lambda t: t.id)
            self._atualizar_tabela_tarefas()
            self._limpar_formulario_tarefa(proximo_id=max(t.id for t in self.tarefas) + 1)
        except Exception as erro:
            self._mostrar_erro(erro)

    def _remover_tarefa(self) -> None:
        selecionado = self.tabela_tarefas.selection()
        if not selecionado:
            return
        tarefa_id = int(self.tabela_tarefas.item(selecionado[0], "values")[0])
        self.tarefas = [tarefa for tarefa in self.tarefas if tarefa.id != tarefa_id]
        self._atualizar_tabela_tarefas()

    def _limpar_tarefas(self) -> None:
        self.tarefas = []
        self._atualizar_tabela_tarefas()
        self._limpar_formulario_tarefa()

    def _sortear_tarefas(self) -> None:
        try:
            quantidade = self._inteiro(self.quantidade_var.get(), "Quantidade")
            self.tarefas = gerar_tarefas(quantidade, incluir_recurso=True)
            self._atualizar_tabela_tarefas()
        except Exception as erro:
            self._mostrar_erro(erro)

    def _salvar_cenario(self) -> None:
        try:
            simular(self.tarefas, "FCFS", ttc=0)
            caminho = filedialog.asksaveasfilename(
                title="Salvar cenário",
                defaultextension=".json",
                filetypes=[("Cenários JSON", "*.json"), ("Todos os arquivos", "*.*")],
                initialfile="cenário.json",
            )
            if caminho:
                salvar_cenario(caminho, self.tarefas)
        except Exception as erro:
            self._mostrar_erro(erro)

    def _abrir_cenario(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Carregar cenário",
            filetypes=[("Cenários JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return
        try:
            self._carregar_cenario(carregar_cenario(caminho))
        except Exception as erro:
            self._mostrar_erro(erro)

    def _carregar_cenario(self, tarefas: list[TarefaEntrada]) -> None:
        self.tarefas = sorted(tarefas, key=lambda tarefa: tarefa.id)
        self.quantidade_var.set(str(len(self.tarefas)))
        self._atualizar_tabela_tarefas()
        if self.tarefas:
            self._preencher_formulario(self.tarefas[0])

    def _carregar_inversao(self) -> None:
        self._carregar_cenario(cenario_inversao_prioridade())
        self.algoritmo_var.set("PRIOp")
        self.protocolo_var.set("nenhum")

    def _carregar_teto_sem_disputa(self) -> None:
        self._carregar_cenario(cenario_teto_sem_disputa())
        self.algoritmo_var.set("PRIOp")
        self.protocolo_var.set("teto")

    def _carregar_inanicao(self) -> None:
        self._carregar_cenario(cenario_inanicao())
        self.algoritmo_var.set("PRIOc")
        self.envelhecimento_var.set(True)
        self.alpha_var.set("1")

    def _selecionar_tarefa(self, _evento: object) -> None:
        selecionado = self.tabela_tarefas.selection()
        if not selecionado:
            return
        tarefa_id = int(self.tabela_tarefas.item(selecionado[0], "values")[0])
        tarefa = next((item for item in self.tarefas if item.id == tarefa_id), None)
        if tarefa is not None:
            self._preencher_formulario(tarefa)

    def _executar_simulacao(self) -> None:
        try:
            resultado = simular(
                self.tarefas,
                self.algoritmo_var.get(),
                quantum=self._inteiro(self.quantum_var.get(), "Quantum"),
                ttc=self._inteiro(self.ttc_var.get(), "ttc"),
                protocolo_prioridade=self.protocolo_var.get(),
                envelhecimento=self.envelhecimento_var.get(),
                alpha=self._inteiro(self.alpha_var.get(), "alpha"),
            )
            self.resultado = resultado
            self._mostrar_resultado(resultado)
            self.abas.select(self.aba_resultados)
        except Exception as erro:
            self._mostrar_erro(erro)

    def _executar_lote(self) -> None:
        try:
            linhas = comparar_lote(
                quantidade_cenarios=self._inteiro(self.lote_cenarios_var.get(), "Cenários"),
                quantidade_tarefas=self._inteiro(self.lote_tarefas_var.get(), "Tarefas"),
                ingresso_max=self._inteiro(self.lote_ingresso_var.get(), "Ingresso máximo"),
                tp_max=self._inteiro(self.lote_tp_var.get(), "tp máximo"),
                prioridade_max=self._inteiro(self.lote_prioridade_var.get(), "Prioridade máxima"),
                quantum=self._inteiro(self.quantum_var.get(), "Quantum"),
                ttc=self._inteiro(self.ttc_var.get(), "ttc"),
            )
            for item in self.tabela_lote.get_children():
                self.tabela_lote.delete(item)
            for linha in linhas:
                self.tabela_lote.insert(
                    "",
                    tk.END,
                    values=(
                        linha["algoritmo"],
                        f"{linha['tt']:.2f}",
                        f"{linha['tw']:.2f}",
                        f"{linha['primeira_execucao']:.2f}",
                    ),
                )
            menor_tw = min(linhas, key=lambda item: item["tw"])["algoritmo"]
            menor_primeira = min(linhas, key=lambda item: item["primeira_execucao"])["algoritmo"]
            self.lote_info_var.set(f"Menor média tw: {menor_tw}. Menor média até 1a execução: {menor_primeira}.")
        except Exception as erro:
            self._mostrar_erro(erro)

    def _mostrar_resultado(self, resultado: ResultadoSimulacao) -> None:
        for item in self.tabela_metricas.get_children():
            self.tabela_metricas.delete(item)
        for metrica in resultado.metricas:
            self.tabela_metricas.insert(
                "",
                tk.END,
                values=(
                    metrica.id,
                    metrica.ingresso,
                    metrica.tp,
                    metrica.prioridade,
                    metrica.conclusao,
                    metrica.tt,
                    metrica.tw,
                    metrica.primeira_execucao,
                ),
            )

        eficiencia = (
            f"{resultado.eficiencia:.3f}"
            if resultado.eficiencia is not None
            else "não definida para algoritmos sem quantum"
        )
        teto = resultado.teto_recurso if resultado.teto_recurso is not None else "não definido"
        self.resumo_var.set(
            f"{resultado.algoritmo} | trocas: {resultado.trocas_contexto} | eficiência: {eficiencia} | teto R: {teto}"
        )
        self.medias_var.set(
            "Médias: "
            f"tt={resultado.medias['tt']:.2f}  "
            f"tp={resultado.medias['tp']:.2f}  "
            f"tw={resultado.medias['tw']:.2f}  "
            f"até 1a execução={resultado.medias['primeira_execucao']:.2f}"
        )
        self._desenhar_linha_tempo(resultado)
        self._mostrar_sequencia(resultado)

    def _desenhar_linha_tempo(self, resultado: ResultadoSimulacao) -> None:
        self.canvas.delete("all")
        tempo_max = max((intervalo.fim for intervalo in resultado.linha_tempo), default=1)
        tempo_max = max(tempo_max, 1)
        largura_disponivel = max(self.canvas.winfo_width(), 900) - 120
        escala = max(24, min(52, largura_disponivel / tempo_max))
        margem_esq = 82
        topo = 44
        altura_linha = 42
        largura_total = int(margem_esq + tempo_max * escala + 80)
        altura_total = int(topo + (len(resultado.tarefas) + 2) * altura_linha + 60)
        self.canvas.configure(scrollregion=(0, 0, largura_total, altura_total))

        self.canvas.create_text(margem_esq - 52, topo - 22, text="CPU", anchor=tk.W, font=("Segoe UI", 9, "bold"))
        for tempo in range(0, tempo_max + 1):
            x = margem_esq + tempo * escala
            self.canvas.create_line(x, topo - 30, x, altura_total - 38, fill="#e3eeec")
            self.canvas.create_text(x, topo - 36, text=str(tempo), font=("Segoe UI", 8), fill="#587270")

        y_cpu = topo
        self.canvas.create_line(margem_esq, y_cpu + 12, margem_esq + tempo_max * escala, y_cpu + 12, fill="#b8cecb")
        for intervalo in resultado.linha_tempo:
            if intervalo.tipo not in {"execucao", "troca", "ocioso"}:
                continue
            x1 = margem_esq + intervalo.inicio * escala
            x2 = margem_esq + intervalo.fim * escala
            if intervalo.tipo == "execucao" and intervalo.tarefa_id is not None:
                cor = self._cor_tarefa(intervalo.tarefa_id)
                texto = ""
            elif intervalo.tipo == "troca":
                cor = "#f4b942"
                texto = "CTX"
            else:
                cor = "#cbd5d9"
                texto = "IDLE"
            self.canvas.create_rectangle(x1, y_cpu, x2, y_cpu + 24, fill=cor, outline=cor)
            if texto and x2 - x1 >= 20:
                self.canvas.create_text((x1 + x2) / 2, y_cpu + 12, text=texto, font=("Segoe UI", 8, "bold"), fill="#42320a" if intervalo.tipo == "troca" else "#405557")

        for indice, tarefa in enumerate(resultado.tarefas, start=1):
            y = topo + indice * altura_linha
            self.canvas.create_text(margem_esq - 72, y + 12, text=f"t{tarefa.id}", anchor=tk.W, font=("Segoe UI", 9, "bold"))
            self.canvas.create_line(margem_esq, y + 12, margem_esq + tempo_max * escala, y + 12, fill="#b8cecb")

            for intervalo in resultado.bloqueios_por_tarefa.get(tarefa.id, []):
                x1 = margem_esq + intervalo.inicio * escala
                x2 = margem_esq + intervalo.fim * escala
                self.canvas.create_rectangle(x1, y, x2, y + 24, fill="#fee2e2", outline="#fca5a5")
                if x2 - x1 >= 22:
                    self.canvas.create_text((x1 + x2) / 2, y + 12, text="R", font=("Segoe UI", 8), fill="#991b1b")

            for intervalo in resultado.execucoes_por_tarefa.get(tarefa.id, []):
                x1 = margem_esq + intervalo.inicio * escala
                x2 = margem_esq + intervalo.fim * escala
                cor_tarefa = self._cor_tarefa(tarefa.id)
                self.canvas.create_rectangle(x1, y, x2, y + 24, fill=cor_tarefa, outline=cor_tarefa)
                if x2 - x1 >= 20:
                    self.canvas.create_text((x1 + x2) / 2, y + 12, text=f"t{tarefa.id}", fill="#073b38", font=("Segoe UI", 8, "bold"))

            for intervalo in resultado.recurso_intervalos:
                if intervalo.tarefa_id != tarefa.id:
                    continue
                x1 = margem_esq + intervalo.inicio * escala
                x2 = margem_esq + intervalo.fim * escala
                self.canvas.create_rectangle(x1, y - 7, x2, y - 1, fill="#84cc16", outline="#84cc16")

        legenda_y = altura_total - 30
        legenda_x = margem_esq
        for tarefa in resultado.tarefas:
            self._legenda(self.canvas, legenda_x, legenda_y, self._cor_tarefa(tarefa.id), f"t{tarefa.id}")
            legenda_x += 58
        self._legenda(self.canvas, legenda_x + 8, legenda_y, "#f4b942", "troca")
        self._legenda(self.canvas, legenda_x + 108, legenda_y, "#fee2e2", "suspensa")
        self._legenda(self.canvas, legenda_x + 230, legenda_y, "#84cc16", "recurso R")

    def _legenda(self, canvas: tk.Canvas, x: int, y: int, cor: str, texto: str) -> None:
        canvas.create_rectangle(x, y, x + 16, y + 12, fill=cor, outline=cor)
        canvas.create_text(x + 22, y + 6, text=texto, anchor=tk.W, font=("Segoe UI", 8), fill="#24403e")

    def _cor_tarefa(self, tarefa_id: int) -> str:
        return self.CORES_TAREFAS[(tarefa_id - 1) % len(self.CORES_TAREFAS)]

    def _mostrar_sequencia(self, resultado: ResultadoSimulacao) -> None:
        partes = [f"t{tid}[{inicio},{fim})" for tid, inicio, fim in resultado.sequencia_execucao()]
        recursos = [
            f"R:t{intervalo.tarefa_id}[{intervalo.inicio},{intervalo.fim})"
            for intervalo in resultado.recurso_intervalos
        ]
        bloqueios = [
            f"bloqueio:t{tid}[{intervalo.inicio},{intervalo.fim})"
            for tid, intervalos in resultado.bloqueios_por_tarefa.items()
            for intervalo in intervalos
        ]
        texto = "Sequência: " + " ".join(partes)
        if recursos:
            texto += "\nRecurso: " + " ".join(recursos)
        if bloqueios:
            texto += "\nSuspensões: " + " ".join(bloqueios)
        self.sequencia_texto.delete("1.0", tk.END)
        self.sequencia_texto.insert("1.0", texto)

    def _atualizar_tabela_tarefas(self) -> None:
        for item in self.tabela_tarefas.get_children():
            self.tabela_tarefas.delete(item)
        for tarefa in sorted(self.tarefas, key=lambda t: t.id):
            self.tabela_tarefas.insert(
                "",
                tk.END,
                values=(
                    tarefa.id,
                    tarefa.ingresso,
                    tarefa.tp,
                    tarefa.prioridade,
                    "" if tarefa.recurso_inicio is None else tarefa.recurso_inicio,
                    "" if tarefa.recurso_duracao == 0 else tarefa.recurso_duracao,
                ),
            )

    def _preencher_formulario(self, tarefa: TarefaEntrada) -> None:
        self.id_var.set(str(tarefa.id))
        self.ingresso_var.set(str(tarefa.ingresso))
        self.tp_var.set(str(tarefa.tp))
        self.prioridade_var.set(str(tarefa.prioridade))
        self.recurso_inicio_var.set("" if tarefa.recurso_inicio is None else str(tarefa.recurso_inicio))
        self.recurso_duracao_var.set("" if tarefa.recurso_duracao == 0 else str(tarefa.recurso_duracao))

    def _limpar_formulario_tarefa(self, proximo_id: int = 1) -> None:
        self.id_var.set(str(proximo_id))
        self.ingresso_var.set("0")
        self.tp_var.set("1")
        self.prioridade_var.set("1")
        self.recurso_inicio_var.set("")
        self.recurso_duracao_var.set("")

    def _ler_tarefa_formulario(self) -> TarefaEntrada:
        recurso_inicio_texto = self.recurso_inicio_var.get().strip()
        recurso_duracao_texto = self.recurso_duracao_var.get().strip()
        recurso_inicio = None
        recurso_duracao = 0
        if recurso_inicio_texto or recurso_duracao_texto:
            recurso_inicio = self._inteiro(recurso_inicio_texto, "R após exec.")
            recurso_duracao = self._inteiro(recurso_duracao_texto, "R duração")

        return TarefaEntrada(
            id=self._inteiro(self.id_var.get(), "ID"),
            ingresso=self._inteiro(self.ingresso_var.get(), "Ingresso"),
            tp=self._inteiro(self.tp_var.get(), "tp"),
            prioridade=self._inteiro(self.prioridade_var.get(), "Prioridade"),
            recurso_inicio=recurso_inicio,
            recurso_duracao=recurso_duracao,
        )

    def _inteiro(self, texto: str, campo: str) -> int:
        valor = str(texto).strip()
        if valor == "":
            raise SimulacaoErro(f"O campo {campo} não pode ficar vazio.")
        try:
            return int(valor)
        except ValueError as exc:
            raise SimulacaoErro(f"O campo {campo} deve ser numérico inteiro.") from exc

    def _mostrar_erro(self, erro: Exception) -> None:
        messagebox.showerror("Erro", str(erro))


def criar_janela() -> None:
    app = AplicacaoSimulador()
    app.mainloop()
