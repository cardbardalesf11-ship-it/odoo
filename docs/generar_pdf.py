"""Genera el PDF de justificación a partir de justificacion.md.

Uso:
    /Users/carlosdaniel/Documents/odoo/.venv/bin/python docs/generar_pdf.py

El script inserta las capturas reales de docs/capturas/ y genera el PDF final
en docs/justificacion.pdf.
"""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "justificacion.md"
DESTINO = BASE / "justificacion.pdf"

ANCHO_MAXIMO_CAPTURA = 15.5 * cm
ALTO_MAXIMO_CAPTURA = 10.5 * cm


def texto_en_linea(texto):
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", texto)
    texto = re.sub(
        r"(https?://[^\s<]+)",
        r'<link href="\1" color="#1155cc"><u>\1</u></link>',
        texto,
    )
    return texto


def es_tabla(linea):
    return linea.strip().startswith("|") and linea.strip().endswith("|")


def celdas(linea):
    return [celda.strip() for celda in linea.strip().strip("|").split("|")]


def crear_tabla(filas):
    if not filas:
        return None
    columnas = max(len(f) for f in filas)
    filas = [f + [""] * (columnas - len(f)) for f in filas]
    datos = []
    for indice, fila in enumerate(filas):
        estilo = styles["TableHeader"] if indice == 0 else styles["TableCell"]
        datos.append([Paragraph(texto_en_linea(celda), estilo) for celda in fila])
    ancho = 17.0 * cm / columnas
    tabla = Table(datos, colWidths=[ancho] * columnas, repeatRows=1)
    tabla.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c2cc")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return tabla


def numero_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(
        2 * cm,
        1.2 * cm,
        "Examen II – Programación de Negocios UNICAH – Carlos Daniel Bardales",
    )
    canvas.drawRightString(
        letter[0] - 2 * cm,
        1.2 * cm,
        "Página %d" % doc.page,
    )
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TituloDocumento",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        spaceAfter=14,
        textColor=colors.HexColor("#1f3b57"),
    )
)
styles.add(
    ParagraphStyle(
        name="TituloSeccion",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#1f3b57"),
    )
)
styles.add(
    ParagraphStyle(
        name="TituloSubseccion",
        parent=styles["Heading2"],
        fontSize=11.5,
        leading=15,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#2e5c85"),
    )
)
styles.add(
    ParagraphStyle(
        name="Cuerpo",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="Viñeta",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="Cita",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        leftIndent=14,
        rightIndent=10,
        textColor=colors.HexColor("#4a4a4a"),
        backColor=colors.HexColor("#f3f6f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="Codigo",
        parent=styles["Code"],
        fontSize=8.5,
        leading=11,
        leftIndent=10,
        backColor=colors.HexColor("#f1f1f1"),
        borderPadding=4,
        spaceBefore=4,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="PieCaptura",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4a4a4a"),
        spaceBefore=3,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeader",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#1f3b57"),
    )
)
styles.add(
    ParagraphStyle(
        name="TableCell",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
    )
)


def construir_historia():
    lineas = ORIGEN.read_text(encoding="utf-8").splitlines()
    historia = []
    indice = 0

    while indice < len(lineas):
        linea = lineas[indice].rstrip()

        if not linea.strip():
            historia.append(Spacer(1, 0.18 * cm))
            indice += 1
            continue

        if linea.strip() == "---":
            historia.append(
                HRFlowable(
                    width="100%",
                    thickness=0.6,
                    color=colors.HexColor("#c9d3dc"),
                    spaceBefore=6,
                    spaceAfter=8,
                )
            )
            indice += 1
            continue

        if linea.startswith("```"):
            indice += 1
            codigo = []
            while indice < len(lineas) and not lineas[indice].startswith("```"):
                codigo.append(lineas[indice])
                indice += 1
            historia.append(Preformatted("\n".join(codigo), styles["Codigo"]))
            indice += 1
            continue

        if linea.strip().startswith("![") and linea.strip().endswith(")"):
            coincidencia = re.fullmatch(r"!\[(.*?)\]\((.+?)\)", linea.strip())
            if coincidencia:
                descripcion, ruta = coincidencia.groups()
                archivo = (BASE / ruta).resolve()
                if archivo.exists():
                    ancho, alto = ImageReader(str(archivo)).getSize()
                    escala = min(
                        ANCHO_MAXIMO_CAPTURA / ancho,
                        ALTO_MAXIMO_CAPTURA / alto,
                    )
                    imagen = Image(
                        str(archivo),
                        width=ancho * escala,
                        height=alto * escala,
                    )
                    historia.append(
                        KeepTogether(
                            [
                                imagen,
                                Paragraph(
                                    texto_en_linea(descripcion),
                                    styles["PieCaptura"],
                                ),
                            ]
                        )
                    )
                    indice += 1
                    continue

        if linea.startswith("# "):
            historia.append(
                Paragraph(texto_en_linea(linea[2:]), styles["TituloDocumento"])
            )
            indice += 1
            continue

        if linea.startswith("## "):
            historia.append(
                Paragraph(texto_en_linea(linea[3:]), styles["TituloSeccion"])
            )
            indice += 1
            continue

        if linea.startswith("### "):
            historia.append(
                Paragraph(texto_en_linea(linea[4:]), styles["TituloSubseccion"])
            )
            indice += 1
            continue

        if es_tabla(linea):
            filas = []
            while indice < len(lineas) and es_tabla(lineas[indice]):
                fila = celdas(lineas[indice])
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in fila):
                    filas.append(fila)
                indice += 1
            tabla = crear_tabla(filas)
            if tabla:
                historia.append(tabla)
                historia.append(Spacer(1, 0.25 * cm))
            continue

        if linea.startswith("- "):
            while indice < len(lineas) and lineas[indice].startswith("- "):
                historia.append(
                    Paragraph(
                        "• " + texto_en_linea(lineas[indice][2:].strip()),
                        styles["Viñeta"],
                    )
                )
                indice += 1
            continue

        if re.match(r"^\d+\.\s", linea):
            while indice < len(lineas) and re.match(r"^\d+\.\s", lineas[indice]):
                historia.append(
                    Paragraph(
                        texto_en_linea(lineas[indice].strip()),
                        styles["Viñeta"],
                    )
                )
                indice += 1
            continue

        if linea.startswith(">"):
            cita = []
            while indice < len(lineas) and lineas[indice].startswith(">"):
                cita.append(lineas[indice][1:].strip())
                indice += 1
            historia.append(
                Paragraph(texto_en_linea(" ".join(cita)), styles["Cita"])
            )
            continue

        parrafo = [linea.strip()]
        indice += 1
        while indice < len(lineas):
            siguiente = lineas[indice].strip()
            if (
                not siguiente
                or siguiente.startswith(("#", ">", "```", "|", "- ", "!"))
                or re.match(r"^\d+\.\s", siguiente)
                or siguiente == "---"
            ):
                break
            parrafo.append(siguiente)
            indice += 1
        historia.append(
            Paragraph(texto_en_linea(" ".join(parrafo)), styles["Cuerpo"])
        )

    return historia


def main():
    documento = SimpleDocTemplate(
        str(DESTINO),
        pagesize=letter,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Justificación del Examen II – Programación de Negocios UNICAH",
        author="Carlos Daniel Bardales",
    )
    documento.build(
        construir_historia(),
        onFirstPage=numero_pagina,
        onLaterPages=numero_pagina,
    )
    print("PDF generado:", DESTINO)


if __name__ == "__main__":
    main()
