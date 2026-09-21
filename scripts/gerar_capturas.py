from __future__ import annotations

import ctypes
import random
import struct
import sys
import time
import tkinter as tk
import zlib
from pathlib import Path
from tkinter import ttk


ROOT = Path(__file__).resolve().parents[1]
IMAGENS = ROOT / "docs" / "imagens"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulador.cenarios import cenario_inversao_prioridade
from simulador.gui import AplicacaoSimulador


def _png_chunk(tipo: bytes, dados: bytes) -> bytes:
    return (
        struct.pack(">I", len(dados))
        + tipo
        + dados
        + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
    )


def _salvar_png(caminho: Path, largura: int, altura: int, pixels_rgb: bytes) -> None:
    linhas = []
    passo = largura * 3
    for y in range(altura):
        linhas.append(b"\x00" + pixels_rgb[y * passo : (y + 1) * passo])

    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("wb") as arquivo:
        arquivo.write(b"\x89PNG\r\n\x1a\n")
        arquivo.write(_png_chunk(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)))
        arquivo.write(_png_chunk(b"IDAT", zlib.compress(b"".join(linhas), 9)))
        arquivo.write(_png_chunk(b"IEND", b""))


def _salvar_janela_png(janela: tk.Tk, caminho: Path) -> None:
    if sys.platform != "win32":
        raise RuntimeError("A captura automatica usa a API GDI do Windows.")

    janela.update_idletasks()
    janela.update()
    time.sleep(0.2)

    user32 = ctypes.windll.user32
    gdi32 = ctypes.windll.gdi32

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [
            ("biSize", ctypes.c_uint32),
            ("biWidth", ctypes.c_long),
            ("biHeight", ctypes.c_long),
            ("biPlanes", ctypes.c_uint16),
            ("biBitCount", ctypes.c_uint16),
            ("biCompression", ctypes.c_uint32),
            ("biSizeImage", ctypes.c_uint32),
            ("biXPelsPerMeter", ctypes.c_long),
            ("biYPelsPerMeter", ctypes.c_long),
            ("biClrUsed", ctypes.c_uint32),
            ("biClrImportant", ctypes.c_uint32),
        ]

    class BITMAPINFO(ctypes.Structure):
        _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", ctypes.c_uint32 * 3)]

    hwnd = janela.winfo_id()
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("Nao foi possivel obter as dimensoes da janela.")

    largura = rect.right - rect.left
    altura = rect.bottom - rect.top
    hdc = user32.GetWindowDC(hwnd)
    memdc = gdi32.CreateCompatibleDC(hdc)
    bitmap = gdi32.CreateCompatibleBitmap(hdc, largura, altura)
    antigo = gdi32.SelectObject(memdc, bitmap)

    capturou = user32.PrintWindow(hwnd, memdc, 2)
    if not capturou:
        gdi32.BitBlt(memdc, 0, 0, largura, altura, hdc, 0, 0, 0x00CC0020)

    info = BITMAPINFO()
    info.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    info.bmiHeader.biWidth = largura
    info.bmiHeader.biHeight = -altura
    info.bmiHeader.biPlanes = 1
    info.bmiHeader.biBitCount = 32
    info.bmiHeader.biCompression = 0

    buffer = ctypes.create_string_buffer(largura * altura * 4)
    gdi32.GetDIBits(memdc, bitmap, 0, altura, buffer, ctypes.byref(info), 0)

    bruto = buffer.raw
    rgb = bytearray(largura * altura * 3)
    for i in range(largura * altura):
        b = bruto[i * 4]
        g = bruto[i * 4 + 1]
        r = bruto[i * 4 + 2]
        rgb[i * 3 : i * 3 + 3] = bytes((r, g, b))

    gdi32.SelectObject(memdc, antigo)
    gdi32.DeleteObject(bitmap)
    gdi32.DeleteDC(memdc)
    user32.ReleaseDC(hwnd, hdc)

    _salvar_png(caminho, largura, altura, bytes(rgb))


def _notebook(app: AplicacaoSimulador) -> ttk.Notebook:
    pendentes = list(app.winfo_children())
    while pendentes:
        widget = pendentes.pop(0)
        if isinstance(widget, ttk.Notebook):
            return widget
        pendentes.extend(widget.winfo_children())
    raise RuntimeError("Notebook da interface nao encontrado.")


def _capturar_app(nome: str, preparar) -> None:
    app = AplicacaoSimulador()
    app.geometry("1180x760+80+60")
    app.lift()
    app.attributes("-topmost", True)
    preparar(app, _notebook(app))
    app.update_idletasks()
    app.update()
    _salvar_janela_png(app, IMAGENS / nome)
    app.destroy()


def _capturar_pasta() -> None:
    janela = tk.Tk()
    janela.title("Pasta descompactada da entrega")
    janela.geometry("820x430+120+100")
    janela.configure(background="#f7f8fb")

    quadro = ttk.Frame(janela, padding=16)
    quadro.pack(fill=tk.BOTH, expand=True)
    ttk.Label(quadro, text="Pasta da entrega", font=("Segoe UI", 16, "bold")).pack(anchor=tk.W)
    ttk.Label(quadro, text="Arquivos principais visiveis apos descompactar o projeto").pack(anchor=tk.W, pady=(0, 10))

    arvore = ttk.Treeview(quadro, columns=("descricao",), show="tree headings", height=12)
    arvore.heading("#0", text="Arquivo ou pasta")
    arvore.heading("descricao", text="Finalidade")
    arvore.column("#0", width=260)
    arvore.column("descricao", width=470)
    arvore.pack(fill=tk.BOTH, expand=True)

    itens = [
        ("README.md", "primeiro arquivo de leitura da entrega"),
        ("dist/Simulador.exe", "executavel aberto com dois cliques"),
        ("docs/", "documentacao tecnica e tutoriais"),
        ("cenarios/", "cenarios oficiais e arquivos JSON salvos"),
        ("simulador/", "codigo-fonte principal"),
        ("tests/", "testes automatizados dos cenarios de referencia"),
    ]
    for nome, descricao in itens:
        arvore.insert("", tk.END, text=nome, values=(descricao,))

    _salvar_janela_png(janela, IMAGENS / "pasta-entrega.png")
    janela.destroy()


def main() -> None:
    _capturar_pasta()

    _capturar_app("tela-inicial.png", lambda app, abas: None)

    def resultado_fcfs(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        app.algoritmo_var.set("FCFS")
        app.quantum_var.set("2")
        app.ttc_var.set("0")
        app.protocolo_var.set("nenhum")
        app.envelhecimento_var.set(False)
        app._executar_simulacao()
        abas.select(app.aba_resultados)

    _capturar_app("resultado-fcfs.png", resultado_fcfs)

    def quantidade(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        app.quantidade_var.set("3")
        app._aplicar_quantidade()
        abas.select(app.aba_tarefas)

    _capturar_app("quantidade-tarefas.png", quantidade)

    def cadastro_recurso(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        app._carregar_cenario(cenario_inversao_prioridade())
        app._preencher_formulario(app.tarefas[0])
        abas.select(app.aba_tarefas)

    _capturar_app("cadastro-recurso.png", cadastro_recurso)

    def sorteio(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        random.seed(42)
        app.quantidade_var.set("6")
        app._sortear_tarefas()
        abas.select(app.aba_tarefas)

    _capturar_app("sorteio-tarefas.png", sorteio)

    def resultado_inversao(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        app._carregar_cenario(cenario_inversao_prioridade())
        app.algoritmo_var.set("PRIOp")
        app.protocolo_var.set("nenhum")
        app._executar_simulacao()
        abas.select(app.aba_resultados)

    _capturar_app("resultado-inversao.png", resultado_inversao)

    def lote(app: AplicacaoSimulador, abas: ttk.Notebook) -> None:
        random.seed(123)
        app.lote_cenarios_var.set("50")
        app.lote_tarefas_var.set("5")
        app.lote_ingresso_var.set("8")
        app.lote_tp_var.set("6")
        app.lote_prioridade_var.set("5")
        app._executar_lote()
        abas.select(app.aba_lote)

    _capturar_app("lote-resultados.png", lote)

    print(f"capturas geradas em: {IMAGENS}")


if __name__ == "__main__":
    main()
