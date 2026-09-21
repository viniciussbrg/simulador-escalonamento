from __future__ import annotations

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ARQUIVOS = [
    ("documentacao_projeto.md", "documentacao_projeto.pdf"),
    ("tutorial_execucao.md", "tutorial_execucao.pdf"),
    ("tutorial_uso.md", "tutorial_uso.pdf"),
]


def gerar_pdf(origem: Path, destino: Path) -> None:
    estilos = getSampleStyleSheet()
    normal = estilos["BodyText"]
    normal.fontName = "Helvetica"
    normal.fontSize = 9
    normal.leading = 12
    titulo = estilos["Title"]
    h1 = estilos["Heading1"]
    h2 = estilos["Heading2"]
    codigo = estilos["Code"]
    codigo.fontName = "Courier"
    codigo.fontSize = 7
    codigo.leading = 9

    elementos = []
    linhas = origem.read_text(encoding="utf-8").splitlines()
    tabela: list[list[str]] = []
    bloco_codigo: list[str] = []
    em_codigo = False

    def descarregar_tabela() -> None:
        nonlocal tabela
        if not tabela:
            return
        dados = []
        for linha in tabela:
            if all(set(celula.strip()) <= {"-", ":"} for celula in linha):
                continue
            dados.append([Paragraph(escape(celula.strip()), normal) for celula in linha])
        if dados:
            tabela_pdf = Table(dados, repeatRows=1)
            tabela_pdf.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#b8c0cc")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elementos.append(tabela_pdf)
            elementos.append(Spacer(1, 8))
        tabela = []

    def descarregar_codigo() -> None:
        nonlocal bloco_codigo
        if bloco_codigo:
            elementos.append(Preformatted("\n".join(bloco_codigo), codigo))
            elementos.append(Spacer(1, 8))
        bloco_codigo = []

    def adicionar_imagem(texto: str) -> bool:
        correspondencia = re.fullmatch(r"!\[(?P<alt>.*?)\]\((?P<caminho>.*?)\)", texto)
        if not correspondencia:
            return False
        caminho_imagem = (origem.parent / correspondencia.group("caminho")).resolve()
        if not caminho_imagem.exists():
            elementos.append(Paragraph(f"[imagem ausente: {escape(correspondencia.group('caminho'))}]", normal))
            elementos.append(Spacer(1, 8))
            return True

        imagem = Image(str(caminho_imagem))
        largura_maxima = A4[0] - 72
        altura_maxima = 330
        escala = min(largura_maxima / imagem.imageWidth, altura_maxima / imagem.imageHeight, 1)
        imagem.drawWidth = imagem.imageWidth * escala
        imagem.drawHeight = imagem.imageHeight * escala
        elementos.append(imagem)
        elementos.append(Spacer(1, 8))
        return True

    for linha in linhas:
        if linha.startswith("```"):
            if em_codigo:
                descarregar_codigo()
                em_codigo = False
            else:
                descarregar_tabela()
                em_codigo = True
            continue

        if em_codigo:
            bloco_codigo.append(linha)
            continue

        if linha.startswith("|") and linha.endswith("|"):
            tabela.append([celula for celula in linha.strip("|").split("|")])
            continue

        descarregar_tabela()
        texto = linha.strip()
        if not texto:
            elementos.append(Spacer(1, 6))
        elif texto.startswith("# "):
            elementos.append(Paragraph(escape(texto[2:]), titulo))
            elementos.append(Spacer(1, 8))
        elif texto.startswith("## "):
            elementos.append(Paragraph(escape(texto[3:]), h1))
            elementos.append(Spacer(1, 6))
        elif texto.startswith("### "):
            elementos.append(Paragraph(escape(texto[4:]), h2))
            elementos.append(Spacer(1, 4))
        elif adicionar_imagem(texto):
            continue
        elif texto.startswith("- "):
            elementos.append(Paragraph("- " + escape(texto[2:]), normal))
        elif texto[0:2].isdigit() and ". " in texto[:4]:
            elementos.append(Paragraph(escape(texto), normal))
        else:
            elementos.append(Paragraph(escape(texto), normal))

    descarregar_tabela()
    descarregar_codigo()
    elementos.append(PageBreak())

    destino.parent.mkdir(parents=True, exist_ok=True)
    documento = SimpleDocTemplate(
        str(destino),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    documento.build(elementos)


def main() -> None:
    for entrada, saida in ARQUIVOS:
        gerar_pdf(DOCS / entrada, DOCS / saida)
        print(f"gerado: {DOCS / saida}")


if __name__ == "__main__":
    main()
