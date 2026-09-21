COR_EXECUCAO = "#1E90FF"
COR_CTX = "#FFD700"
COR_ESPERA = "#FF6347"
COR_SUSPENSA = "#A9A9A9"
COR_GRADE = "#E0E0E0"

ALTURA_LINHA = 32
MARGEM_ESQUERDA = 90
MARGEM_SUPERIOR = 20
MARGEM_METRICAS = 20
PIXELS_POR_UNIDADE = 36


def desenhar_diagrama(canvas, processos):
    """Redesenha o diagrama de tempo em tk.Canvas puro — uma linha por
    tarefa, blocos de Execução/CTX/espera, como o antigo grafico_processos
    (matplotlib), só que sem depender de nenhuma biblioteca externa."""
    canvas.delete("all")

    tem_execucao = any(p.processamentos for p in processos)
    if not processos or not tem_execucao:
        canvas.configure(scrollregion=(0, 0, 400, 80))
        canvas.create_text(200, 40, text="Nenhuma execução para exibir.")
        return

    tempo_maximo = max(periodo.fim for p in processos for periodo in p.processamentos)
    largura_grafico = tempo_maximo * PIXELS_POR_UNIDADE
    largura_total = MARGEM_ESQUERDA + largura_grafico + MARGEM_METRICAS + 140
    y_eixo = MARGEM_SUPERIOR + len(processos) * ALTURA_LINHA + 10
    altura_total = y_eixo + 30

    for i, processo in enumerate(processos):
        y0 = MARGEM_SUPERIOR + i * ALTURA_LINHA
        y1 = y0 + ALTURA_LINHA - 6
        y_meio = (y0 + y1) / 2

        canvas.create_text(MARGEM_ESQUERDA - 8, y_meio, text=f"Tarefa {processo.id}", anchor="e")

        tempo_cursor = processo.chegada
        for periodo in processo.processamentos:
            if periodo.inicio > tempo_cursor:
                x0 = MARGEM_ESQUERDA + tempo_cursor * PIXELS_POR_UNIDADE
                x1 = MARGEM_ESQUERDA + periodo.inicio * PIXELS_POR_UNIDADE
                canvas.create_rectangle(x0, y0, x1, y1, fill=COR_ESPERA, outline=COR_ESPERA)
            tempo_cursor = periodo.fim

            x0 = MARGEM_ESQUERDA + periodo.inicio * PIXELS_POR_UNIDADE
            x1 = MARGEM_ESQUERDA + periodo.fim * PIXELS_POR_UNIDADE
            if periodo.tipo == "Execução":
                cor = COR_EXECUCAO
            elif periodo.tipo == "CTX":
                cor = COR_CTX
            else:
                cor = COR_SUSPENSA
            canvas.create_rectangle(x0, y0, x1, y1, fill=cor, outline=cor)
            if periodo.tipo == "CTX" and (x1 - x0) > 14:
                canvas.create_text((x0 + x1) / 2, y_meio, text="CTX", font=("TkDefaultFont", 7))
            elif periodo.tipo == "Suspensa" and (x1 - x0) > 24:
                canvas.create_text((x0 + x1) / 2, y_meio, text="SUSP", font=("TkDefaultFont", 7))

        x_metricas = MARGEM_ESQUERDA + largura_grafico + MARGEM_METRICAS
        texto = f"T={processo.get_turnaround():.1f}  T_w={processo.get_espera():.1f}"
        canvas.create_text(x_metricas, y_meio, text=texto, anchor="w", font=("TkDefaultFont", 8))

    for t in range(0, int(tempo_maximo) + 1):
        x = MARGEM_ESQUERDA + t * PIXELS_POR_UNIDADE
        canvas.create_line(x, MARGEM_SUPERIOR - 4, x, y_eixo, fill=COR_GRADE)
        canvas.create_text(x, y_eixo + 10, text=str(t), font=("TkDefaultFont", 8))

    canvas.configure(scrollregion=(0, 0, largura_total, altura_total))
