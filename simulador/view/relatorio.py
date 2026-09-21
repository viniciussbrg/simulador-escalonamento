import tkinter as tk

def exibir_diagrama_canvas(resultado, bloqueios_mapa, parent=None):
    """
    Desenha o diagrama de tempo graficamente usando apenas tkinter.Canvas.
    A janela abre por cima sem bloquear o relatório em texto original.
    """
    janela = tk.Toplevel(parent)
    janela.title(f"Diagrama de Tempo: {resultado.algoritmo}")
    
    largura = 950
    altura = max(400, len(resultado.estados) * 60 + 150)
    margem_esq = 80
    margem_dir = 120
    margem_top = 60
    margem_bot = 80
    
    canvas = tk.Canvas(janela, width=largura, height=altura, bg="white")
    canvas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    if not resultado.segmentos:
        canvas.create_text(largura/2, altura/2, text="(sem execuções)", font=("Arial", 14))
        return

    fim_tempo = max(s.fim for s in resultado.segmentos)
    if hasattr(resultado, 'instante_final'):
        fim_tempo = max(fim_tempo, resultado.instante_final)
        
    largura_util = largura - margem_esq - margem_dir
    escala_x = largura_util / fim_tempo if fim_tempo > 0 else 1
    altura_linha = (altura - margem_top - margem_bot) / len(resultado.estados)
    
    # Desenhar Eixos
    canvas.create_line(margem_esq, margem_top, margem_esq, altura - margem_bot, width=2)
    canvas.create_line(margem_esq, altura - margem_bot, largura - margem_dir + 20, altura - margem_bot, width=2)
    
    # Marcadores e grade do Eixo X
    for t in range(fim_tempo + 1):
        x = margem_esq + (t * escala_x)
        canvas.create_line(x, altura - margem_bot, x, altura - margem_bot + 5, width=1)
        canvas.create_text(x, altura - margem_bot + 15, text=str(t), font=("Arial", 8))
        canvas.create_line(x, margem_top, x, altura - margem_bot, fill="#E8E8E8", dash=(2, 4))
        
    estados_ordenados = sorted(resultado.estados, key=lambda e: e.identificador)
    
    for i, estado in enumerate(estados_ordenados):
        y_centro = margem_top + (i * altura_linha) + (altura_linha / 2)
        y_top = y_centro - (altura_linha * 0.3)
        y_bot = y_centro + (altura_linha * 0.3)
        
        # Rótulo da Tarefa
        canvas.create_text(margem_esq - 10, y_centro, text=estado.tarefa.nome, anchor="e", font=("Arial", 10, "bold"))
        
        # Bloqueios (Fundo Vermelho)
        instantes_bloqueados = bloqueios_mapa.get(estado.identificador, set())
        for t in instantes_bloqueados:
            if t < fim_tempo:
                x0 = margem_esq + (t * escala_x)
                x1 = margem_esq + ((t + 1) * escala_x)
                canvas.create_rectangle(x0, y_top, x1, y_bot, fill="#FF6347", outline="")
                
        # Execuções e Trocas
        from control.motor import EXECUCAO 
        for seg in resultado.segmentos:
            if seg.identificador == estado.identificador:
                x0 = margem_esq + (seg.inicio * escala_x)
                x1 = margem_esq + (seg.fim * escala_x)
                
                if seg.tipo == EXECUCAO: 
                    cor = "#8A2BE2" if getattr(seg, 'detem_recurso', False) else "#1E90FF"
                    canvas.create_rectangle(x0, y_top, x1, y_bot, fill=cor, outline="black")
                else: 
                    # Troca de Contexto
                    canvas.create_rectangle(x0, y_top, x1, y_bot, fill="#FFD700", outline="black")
                    canvas.create_text((x0 + x1)/2, y_centro, text="CTX", font=("Arial", 7, "bold"))
                    
        # Métricas na lateral direita
        canvas.create_text(largura - margem_dir + 30, y_centro, 
                           text=f"Tt: {estado.tt}\nTw: {estado.tw}", anchor="w", font=("Arial", 9))

    # Título e Legendas
    canvas.create_text(largura/2, 25, text=f"Diagrama de Tempo: {resultado.algoritmo}", font=("Arial", 14, "bold"))
    
    y_legenda = altura - 30
    canvas.create_rectangle(margem_esq, y_legenda-5, margem_esq+15, y_legenda+10, fill="#1E90FF", outline="black")
    canvas.create_text(margem_esq+25, y_legenda+2, text="Execução", anchor="w")
    
    canvas.create_rectangle(margem_esq + 120, y_legenda-5, margem_esq+135, y_legenda+10, fill="#8A2BE2", outline="black")
    canvas.create_text(margem_esq+145, y_legenda+2, text="Posse de R", anchor="w")
    
    canvas.create_rectangle(margem_esq + 260, y_legenda-5, margem_esq+275, y_legenda+10, fill="#FF6347", outline="black")
    canvas.create_text(margem_esq+285, y_legenda+2, text="Bloqueado", anchor="w")
    
    canvas.create_rectangle(margem_esq + 400, y_legenda-5, margem_esq+415, y_legenda+10, fill="#FFD700", outline="black")
    canvas.create_text(margem_esq+425, y_legenda+2, text="Troca (CTX)", anchor="w")

    janela.update_idletasks()
    w = janela.winfo_width()
    h = janela.winfo_height()
    x = (janela.winfo_screenwidth() // 2) - (w // 2)
    y = (janela.winfo_screenheight() // 2) - (h // 2)
    janela.geometry(f'{w}x{h}+{x}+{y}')


def _mapa_de_bloqueios(resultado, fim: int) -> dict[int, set]:
    """Reconstroi os instantes em que cada tarefa esteve suspensa em R."""
    from control.motor import EXECUCAO 
    
    ocupado: dict[int, int] = {}
    for seg in resultado.segmentos:
        if seg.tipo == EXECUCAO:
            for instante in range(seg.inicio, seg.fim):
                ocupado[instante] = seg.identificador

    bloqueios: dict[int, set] = {}
    for estado in resultado.estados:
        total = estado.bloqueio_direto + estado.bloqueio_inversao
        if total == 0 or getattr(estado, 'primeira_execucao', None) is None:
            continue
            
        proprios = set()
        for seg in resultado.segmentos:
            if seg.identificador == estado.identificador and seg.tipo == EXECUCAO:
                proprios.update(range(seg.inicio, seg.fim))
                
        candidatos = [
            instante
            for instante in range(estado.ingresso, estado.conclusao or fim)
            if instante not in proprios and instante in ocupado
        ]
        bloqueios[estado.identificador] = set(candidatos[-total:]) if total else set()
        
    return bloqueios


def formatar_metricas(resultado):
    """
    Gera o relatório em texto com as métricas de tempo de execução (tt),
    tempo de processamento (tp), tempo de espera (tw) e primeira execução,
    por tarefa e as médias (R3), além do quantum, custo da troca e
    eficiência da configuração (R4).
    """
    estados = resultado.estados
    if not estados:
        return "Nenhuma tarefa foi processada."

    n = len(estados)
    tt_medio = sum(e.tt for e in estados) / n
    tp_medio = sum(e.tp for e in estados) / n
    tw_medio = sum(e.tw for e in estados) / n

    soma_primeira_exec = sum(
        (e.primeira_execucao - e.ingresso) for e in estados if getattr(e, 'primeira_execucao', None) is not None
    )
    primeira_exec_media = soma_primeira_exec / n

    linhas = []
    linhas.append(f"Algoritmo: {resultado.algoritmo}")

    # R4: quantum, custo da troca e eficiencia da configuracao. E so existe
    # com quantum -- fora do Round-Robin o simulador escreve "nao definida"
    # em vez de um numero.
    eficiencia = resultado.eficiencia
    eficiencia_texto = f"{eficiencia:.3f}" if eficiencia is not None else "não definida (sem quantum)"
    quantum_texto = str(resultado.quantum) if resultado.quantum is not None else "-"
    linhas.append(
        f"Quantum tq: {quantum_texto}   |   Custo da troca ttc: {resultado.custo_troca}   |   "
        f"Eficiência E = tq/(tq+ttc): {eficiencia_texto}"
    )
    linhas.append("")

    linhas.append(f"{'Tarefa':<8} | {'Tt':<6} | {'Tp':<6} | {'Tw':<6} | {'1ª Exec'}")
    linhas.append("-" * 45)

    for e in sorted(estados, key=lambda x: x.identificador):
        primeira_exec = (e.primeira_execucao - e.ingresso) if getattr(e, 'primeira_execucao', None) is not None else 0
        linhas.append(
            f"{e.tarefa.nome:<8} | {e.tt:<6.1f} | {e.tp:<6.1f} | {e.tw:<6.1f} | {primeira_exec:.1f}"
        )

    linhas.append("-" * 45)
    linhas.append(
        f"{'Médias':<8} | {tt_medio:<6.2f} | {tp_medio:<6.2f} | {tw_medio:<6.2f} | {primeira_exec_media:.2f}"
    )

    return "\n".join(linhas)


def formatar_comparativo(resumo: dict, titulo: str = "") -> str:
    """Gera a tabela comparativa entre os 6 algoritmos de escalonamento."""
    linhas = []
    if titulo:
        linhas.append(titulo)
        linhas.append("")
        
    cabecalho = f"{'Algoritmo':<10} {'Tt':>8} {'Tw':>8} {'1a exec.':>10} {'trocas':>8}"
    linhas.append(cabecalho)
    linhas.append("-" * len(cabecalho))
    
    for sigla, valores in resumo.items():
        linhas.append(
            f"{sigla:<10} {valores.get('tt', 0):>8.2f} {valores.get('tw', 0):>8.2f} "
            f"{valores.get('primeira', 0):>10.2f} {valores.get('trocas', 0):>8.2f}"
        )
        
    linhas.append("")
    if resumo:
        menor_tw = min(resumo.keys(), key=lambda s: resumo[s].get("tw", float('inf')))
        menor_primeira = min(resumo.keys(), key=lambda s: resumo[s].get("primeira", float('inf')))
        linhas.append(f"Menor Tw: {menor_tw}")
        linhas.append(f"Menor tempo médio até a primeira execução: {menor_primeira}")
        
    linhas.append("")
    linhas.append(
        "Os valores absolutos mudam a cada execução porque os cenários são\n"
        "sorteados. O que precisa se manter é a ordenação: SRTF com o menor Tw\n"
        "e Round-Robin com o menor tempo até a primeira execução."
    )
    return "\n".join(linhas)