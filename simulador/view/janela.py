"""Ponto de entrada do simulador de escalonamento de tarefas.

Abre com dois cliques e nao recebe nenhum argumento de linha de comando (R10).
"""

import os
import sys
import random
import tkinter as tk
import traceback
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from control import gerador, politicas
from control.motor import EXECUCAO, HERANCA, SEM_PROTOCOLO, TETO, ErroDeConfiguracao, Escalonador
from model import cenario as persistencia
from model.tarefa import EntradaInvalida, Tarefa
from view import relatorio

FONTE_MONO = ("Courier New", 10)
PASTA_CENARIOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cenarios")


class Aplicacao(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Simulador de escalonamento de tarefas")
        self.geometry("1180x760")
        self.minsize(960, 640)

        self.tarefas = []
        self._montar()
        self._atualizar_lista()

    # ------------------------------------------------------------------ #
    def _montar(self) -> None:
        painel = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        painel.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        esquerda = ttk.Frame(painel)
        direita = ttk.Frame(painel)
        painel.add(esquerda, weight=0)
        painel.add(direita, weight=1)

        self._montar_tarefas(esquerda)
        self._montar_configuracao(esquerda)
        self._montar_acoes(esquerda)
        self._montar_saida(direita)

    # --- R2: entrada de tarefas ---------------------------------------- #
    def _montar_tarefas(self, pai) -> None:
        caixa = ttk.LabelFrame(pai, text="Tarefas (R2)")
        caixa.pack(fill=tk.X, pady=(0, 8))

        campos = ttk.Frame(caixa)
        campos.pack(fill=tk.X, padx=6, pady=6)

        self.entradas = {}
        rotulos = [
            ("ingresso", "Ingresso"),
            ("tp", "tp"),
            ("prioridade", "Prioridade"),
            ("sc_inicio", "SC inicio"),
            ("sc_duracao", "SC duracao"),
        ]
        for coluna, (chave, rotulo) in enumerate(rotulos):
            ttk.Label(campos, text=rotulo).grid(row=0, column=coluna, padx=2)
            entrada = ttk.Entry(campos, width=9)
            entrada.grid(row=1, column=coluna, padx=2)
            self.entradas[chave] = entrada
        ttk.Label(
            campos,
            text="Secao critica opcional: deixe os dois ultimos campos vazios se a tarefa nao usa R.",
            foreground="#555",
        ).grid(row=2, column=0, columnspan=5, sticky="w", pady=(4, 0))

        botoes = ttk.Frame(caixa)
        botoes.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(botoes, text="Adicionar", command=self.adicionar_tarefa).pack(side=tk.LEFT)
        ttk.Button(botoes, text="Remover selecionada", command=self.remover_tarefa).pack(side=tk.LEFT, padx=4)
        ttk.Button(botoes, text="Limpar tudo", command=self.limpar_tarefas).pack(side=tk.LEFT)

        self.lista = tk.Listbox(caixa, height=9, font=FONTE_MONO)
        self.lista.pack(fill=tk.X, padx=6, pady=(0, 6))

        sorteio = ttk.LabelFrame(caixa, text="Sorteio (R9)")
        sorteio.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.sorteio_campos = {}
        especificacao = [
            ("quantidade", "Quantas tarefas", "5"),
            ("ingresso_max", "Ingresso ate", "8"),
            ("duracao_max", "Duracao ate", "6"),
            ("prioridade_max", "Prioridade ate", "5"),
            ("proporcao", "% com recurso", "0"),
        ]
        for coluna, (chave, rotulo, padrao) in enumerate(especificacao):
            ttk.Label(sorteio, text=rotulo).grid(row=0, column=coluna, padx=2)
            entrada = ttk.Entry(sorteio, width=9)
            entrada.insert(0, padrao)
            entrada.grid(row=1, column=coluna, padx=2, pady=(0, 4))
            self.sorteio_campos[chave] = entrada
        ttk.Button(sorteio, text="Sortear cenario", command=self.sortear).grid(
            row=2, column=0, columnspan=5, sticky="we", padx=2, pady=(0, 4)
        )

        arquivo = ttk.Frame(caixa)
        arquivo.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(arquivo, text="Gravar cenario...", command=self.gravar).pack(side=tk.LEFT)
        ttk.Button(arquivo, text="Carregar cenario...", command=self.carregar).pack(side=tk.LEFT, padx=4)

    # --- R4, R6, R7, R8: configuracao do escalonador -------------------- #
    def _montar_configuracao(self, pai) -> None:
        caixa = ttk.LabelFrame(pai, text="Escalonador (R4, R6, R7, R8)")
        caixa.pack(fill=tk.X, pady=(0, 8))

        linha = ttk.Frame(caixa)
        linha.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(linha, text="Algoritmo").grid(row=0, column=0, sticky="w")
        self.algoritmo = tk.StringVar(value="FCFS")
        combo = ttk.Combobox(
            linha, textvariable=self.algoritmo, width=8, state="readonly",
            values=politicas.ORDEM,
        )
        combo.grid(row=1, column=0, padx=2)

        ttk.Label(linha, text="Quantum tq").grid(row=0, column=1, sticky="w")
        self.quantum = ttk.Entry(linha, width=8)
        self.quantum.insert(0, "2")
        self.quantum.grid(row=1, column=1, padx=2)

        ttk.Label(linha, text="Custo troca ttc").grid(row=0, column=2, sticky="w")
        self.custo = ttk.Entry(linha, width=8)
        self.custo.insert(0, "0")
        self.custo.grid(row=1, column=2, padx=2)

        ttk.Label(linha, text="Alfa (aging)").grid(row=0, column=3, sticky="w")
        self.alfa = ttk.Entry(linha, width=8)
        self.alfa.insert(0, "0")
        self.alfa.grid(row=1, column=3, padx=2)

        ttk.Label(linha, text="Protocolo").grid(row=0, column=4, sticky="w")
        self.protocolo = tk.StringVar(value=SEM_PROTOCOLO)
        ttk.Combobox(
            linha, textvariable=self.protocolo, width=10, state="readonly",
            values=[SEM_PROTOCOLO, HERANCA, TETO],
        ).grid(row=1, column=4, padx=2)

    def _montar_acoes(self, pai) -> None:
        caixa = ttk.Frame(pai)
        caixa.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(caixa, text="Simular", command=self.simular).pack(side=tk.LEFT)
        ttk.Button(caixa, text="Comparar os seis", command=self.comparar).pack(side=tk.LEFT, padx=4)

        lote = ttk.LabelFrame(pai, text="Lote de cenarios (R9)")
        lote.pack(fill=tk.X)
        interno = ttk.Frame(lote)
        interno.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(interno, text="Amostras").grid(row=0, column=0)
        self.amostras = ttk.Entry(interno, width=8)
        self.amostras.insert(0, "50")
        self.amostras.grid(row=0, column=1, padx=4)
        ttk.Button(interno, text="Rodar lote", command=self.rodar_lote).grid(row=0, column=2, padx=4)

    def _montar_saida(self, pai) -> None:
        caixa = ttk.LabelFrame(pai, text="Resultado")
        caixa.pack(fill=tk.BOTH, expand=True)
        barra = ttk.Scrollbar(caixa, orient=tk.VERTICAL)
        self.saida = tk.Text(caixa, wrap=tk.NONE, font=FONTE_MONO, yscrollcommand=barra.set)
        barra.config(command=self.saida.yview)
        barra.pack(side=tk.RIGHT, fill=tk.Y)
        horizontal = ttk.Scrollbar(caixa, orient=tk.HORIZONTAL, command=self.saida.xview)
        horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        self.saida.config(xscrollcommand=horizontal.set)
        self.saida.pack(fill=tk.BOTH, expand=True)
        self._escrever(
            "Simulador de escalonamento de tarefas\n\n"
            "1. Informe as tarefas (digitando ou sorteando) ou carregue um cenario da pasta cenarios/.\n"
            "2. Ajuste quantum, custo da troca, alfa e protocolo.\n"
            "3. Clique em Simular, Comparar os seis ou Rodar lote.\n"
        )

    # ------------------------------------------------------------------ #
    # acoes
    def adicionar_tarefa(self) -> None:
        try:
            valores = {}
            for chave in ("ingresso", "tp", "prioridade"):
                bruto = self.entradas[chave].get().strip()
                if bruto == "":
                    raise EntradaInvalida(f"O campo '{chave}' nao pode ficar vazio.")
                valores[chave] = self._inteiro(bruto, chave)

            sc_inicio_bruto = self.entradas["sc_inicio"].get().strip()
            sc_duracao_bruto = self.entradas["sc_duracao"].get().strip()
            if bool(sc_inicio_bruto) != bool(sc_duracao_bruto):
                raise EntradaInvalida(
                    "Informe inicio E duracao da secao critica, ou deixe os dois vazios."
                )
            sc_inicio = self._inteiro(sc_inicio_bruto, "SC inicio") if sc_inicio_bruto else None
            sc_duracao = self._inteiro(sc_duracao_bruto, "SC duracao") if sc_duracao_bruto else 0

            identificador = max((t.identificador for t in self.tarefas), default=0) + 1
            tarefa = Tarefa(identificador, valores["ingresso"], valores["tp"],
                            valores["prioridade"], sc_inicio, sc_duracao)
        except EntradaInvalida as erro:
            messagebox.showerror("Valor invalido", str(erro))
            return

        self.tarefas.append(tarefa)
        self._atualizar_lista()
        for entrada in self.entradas.values():
            entrada.delete(0, tk.END)

    @staticmethod
    def _inteiro(bruto: str, campo: str) -> int:
        try:
            return int(bruto)
        except ValueError:
            raise EntradaInvalida(
                f"'{bruto}' nao e um numero inteiro valido para o campo '{campo}'."
            )

    def remover_tarefa(self) -> None:
        selecao = self.lista.curselection()
        if not selecao:
            messagebox.showinfo("Remover", "Selecione uma tarefa na lista.")
            return
        del self.tarefas[selecao[0]]
        self._renumerar()
        self._atualizar_lista()

    def limpar_tarefas(self) -> None:
        self.tarefas = []
        self._atualizar_lista()

    def _renumerar(self) -> None:
        for indice, tarefa in enumerate(self.tarefas, start=1):
            tarefa.identificador = indice

    def _atualizar_lista(self) -> None:
        self.lista.delete(0, tk.END)
        for tarefa in self.tarefas:
            self.lista.insert(
                tk.END,
                f"{tarefa.nome:<4} ingresso={tarefa.ingresso:<3} tp={tarefa.tp:<3} "
                f"prio={tarefa.prioridade:<3} SC={tarefa.descricao_sc()}",
            )

    def sortear(self) -> None:
        try:
            quantidade = self._inteiro(self.sorteio_campos["quantidade"].get().strip() or "0", "Quantas tarefas")
            proporcao = self._inteiro(self.sorteio_campos["proporcao"].get().strip() or "0", "% com recurso")
            self.tarefas = gerador.sortear_cenario(
                quantidade,
                self._inteiro(self.sorteio_campos["ingresso_max"].get().strip() or "0", "Ingresso ate"),
                self._inteiro(self.sorteio_campos["duracao_max"].get().strip() or "1", "Duracao ate"),
                self._inteiro(self.sorteio_campos["prioridade_max"].get().strip() or "1", "Prioridade ate"),
                proporcao_com_recurso=max(0.0, min(1.0, proporcao / 100)),
                aleatorio=random.Random(),
            )
        except (EntradaInvalida, ValueError) as erro:
            messagebox.showerror("Sorteio invalido", str(erro))
            return
        self._atualizar_lista()
        self._escrever("Cenario sorteado. Grave-o se quiser reexamina-lo depois.\n")

    def gravar(self) -> None:
        if not self.tarefas:
            messagebox.showinfo("Gravar", "Nao ha tarefas para gravar.")
            return
        caminho = filedialog.asksaveasfilename(
            defaultextension=".json", initialdir=PASTA_CENARIOS,
            filetypes=[("Cenario JSON", "*.json")],
        )
        if not caminho:
            return
        try:
            persistencia.gravar(caminho, self.tarefas, self._parametros_brutos())
        except OSError as erro:
            messagebox.showerror("Gravar", f"Nao foi possivel gravar: {erro}")
            return
        self._escrever(f"Cenario gravado em {caminho}\n")

    def carregar(self) -> None:
        caminho = filedialog.askopenfilename(
            initialdir=PASTA_CENARIOS, filetypes=[("Cenario JSON", "*.json")]
        )
        if not caminho:
            return
        try:
            tarefas, parametros, descricao = persistencia.carregar(caminho)
        except EntradaInvalida as erro:
            messagebox.showerror("Carregar", str(erro))
            return
        self.tarefas = tarefas
        self._aplicar_parametros(parametros)
        self._atualizar_lista()
        self._escrever(f"Cenario carregado de {caminho}\n{descricao}\n")

    def _parametros_brutos(self) -> dict:
        return {
            "quantum": self.quantum.get().strip(),
            "custo_troca": self.custo.get().strip(),
            "alfa": self.alfa.get().strip(),
            "protocolo": self.protocolo.get(),
            "algoritmo": self.algoritmo.get(),
        }

    def _aplicar_parametros(self, parametros: dict) -> None:
        for campo, chave in ((self.quantum, "quantum"), (self.custo, "custo_troca"), (self.alfa, "alfa")):
            if chave in parametros:
                campo.delete(0, tk.END)
                campo.insert(0, str(parametros[chave]))
        if parametros.get("protocolo") in (SEM_PROTOCOLO, HERANCA, TETO):
            self.protocolo.set(parametros["protocolo"])
        if parametros.get("algoritmo") in politicas.ORDEM:
            self.algoritmo.set(parametros["algoritmo"])

    # --- simulacao ------------------------------------------------------ #
    def _configuracao(self):
        quantum = self._inteiro(self.quantum.get().strip() or "0", "Quantum tq")
        custo = self._inteiro(self.custo.get().strip() or "0", "Custo troca ttc")
        alfa = self._inteiro(self.alfa.get().strip() or "0", "Alfa")
        return quantum, custo, alfa

    def simular(self) -> None:
        if not self.tarefas:
            messagebox.showinfo("Simular", "Adicione ou sorteie ao menos uma tarefa.")
            return
        try:
            quantum, custo, alfa = self._configuracao()
            resultado = Escalonador(
                [t.clonar() for t in self.tarefas],
                politicas.criar(self.algoritmo.get()),
                quantum=quantum,
                custo_troca=custo,
                alfa=alfa,
                protocolo=self.protocolo.get(),
            ).executar()
        except (EntradaInvalida, ErroDeConfiguracao, ValueError) as erro:
            messagebox.showerror("Configuracao invalida", str(erro))
            return

        partes = [
            relatorio.formatar_metricas(resultado),
            "",
            "★ Diagrama de tempo e relatório de bloqueios gerados com sucesso!",
            "Verifique a nova janela gráfica que se abriu para visualizar a linha do tempo."
        ]
        self._escrever("\n".join(partes))

        # Chama a função visual de diagrama 
        fim = max((s.fim for s in resultado.segmentos), default=0)
        if hasattr(resultado, 'instante_final'):
            fim = max(fim, resultado.instante_final)
        
        bloqueios_mapa = relatorio._mapa_de_bloqueios(resultado, fim)
        relatorio.exibir_diagrama_canvas(resultado, bloqueios_mapa, parent=self)

    def comparar(self) -> None:
        if not self.tarefas:
            messagebox.showinfo("Comparar", "Adicione ou sorteie ao menos uma tarefa.")
            return
        try:
            quantum, custo, alfa = self._configuracao()
            resumo = gerador.comparar(
                self.tarefas, quantum=quantum, custo_troca=custo,
                alfa=alfa, protocolo=self.protocolo.get(),
            )
        except (EntradaInvalida, ErroDeConfiguracao, ValueError) as erro:
            messagebox.showerror("Configuracao invalida", str(erro))
            return
            
        self._escrever(
            relatorio.formatar_comparativo(
                resumo, f"Os seis algoritmos sobre este cenario ({len(self.tarefas)} tarefas)"
            )
        )

    def rodar_lote(self) -> None:
        try:
            amostras = self._inteiro(self.amostras.get().strip() or "0", "Amostras")
            quantidade = self._inteiro(self.sorteio_campos["quantidade"].get().strip() or "0", "Quantas tarefas")
            quantum, custo, _ = self._configuracao()
            self._escrever("Rodando lote...\n")
            self.update_idletasks()
            resumo = gerador.rodar_lote(
                amostras=amostras,
                quantidade=quantidade,
                ingresso_max=self._inteiro(self.sorteio_campos["ingresso_max"].get().strip() or "0", "Ingresso ate"),
                duracao_max=self._inteiro(self.sorteio_campos["duracao_max"].get().strip() or "1", "Duracao ate"),
                prioridade_max=self._inteiro(self.sorteio_campos["prioridade_max"].get().strip() or "1", "Prioridade ate"),
                quantum=quantum,
                custo_troca=custo,
            )
        except (EntradaInvalida, ErroDeConfiguracao, ValueError) as erro:
            messagebox.showerror("Lote invalido", str(erro))
            return
            
        self._escrever(
            relatorio.formatar_comparativo(
                resumo, f"Medias sobre {amostras} cenarios de {quantidade} tarefas"
            )
        )

    # ------------------------------------------------------------------ #
    def _escrever(self, texto: str) -> None:
        self.saida.delete("1.0", tk.END)
        self.saida.insert(tk.END, texto)


def criar_janela() -> None:
    """Abre a janela. Nao fecha sozinha nem ao terminar nem diante de erro (R10)."""
    try:
        aplicacao = Aplicacao()
        aplicacao.report_callback_exception = _erro_nao_tratado
        aplicacao.mainloop()
    except Exception:  # noqa: BLE001 - a janela nao pode sumir sem mostrar o erro
        _mostrar_falha_fatal(traceback.format_exc())


def _erro_nao_tratado(tipo, valor, tb) -> None:
    messagebox.showerror(
        "Erro inesperado",
        "Ocorreu um erro, mas o programa continua aberto:\n\n"
        + "".join(traceback.format_exception(tipo, valor, tb)),
    )


def _mostrar_falha_fatal(texto: str) -> None:
    try:
        janela = tk.Tk()
        janela.title("Falha ao iniciar o simulador")
        area = tk.Text(janela, wrap=tk.WORD, font=FONTE_MONO, width=100, height=30)
        area.insert(tk.END, texto)
        area.pack(fill=tk.BOTH, expand=True)
        tk.Button(janela, text="Fechar", command=janela.destroy).pack(pady=6)
        janela.mainloop()
    except Exception:  # noqa: BLE001 - ultimo recurso: console que espera Enter
        print(texto)
        input("\nPressione Enter para fechar...")