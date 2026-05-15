"""Generacion de reportes PDF con ReportLab."""

import io
from datetime import datetime
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Colores institucionales UMG
AZUL_UMG = colors.HexColor("#003087")
AZUL_CLARO = colors.HexColor("#1565C0")
AZUL_FONDO = colors.HexColor("#F0F4FF")
ROJO = colors.HexColor("#D32F2F")
VERDE = colors.HexColor("#2E7D32")
NARANJA = colors.HexColor("#F57C00")
GRIS = colors.HexColor("#616161")
BLANCO = colors.white


def _color_alerta(nivel: str) -> colors.Color:
    if nivel == "alto":
        return ROJO
    elif nivel == "medio":
        return NARANJA
    return VERDE


def _estilos_personalizados(estilos_base):
    """Retorna diccionario con estilos adicionales para el PDF."""
    return {
        "titulo_principal": ParagraphStyle(
            "titulo_principal",
            parent=estilos_base["Title"],
            fontSize=20,
            textColor=AZUL_UMG,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo",
            parent=estilos_base["Normal"],
            fontSize=12,
            textColor=AZUL_CLARO,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName="Helvetica",
        ),
        "seccion": ParagraphStyle(
            "seccion",
            parent=estilos_base["Heading1"],
            fontSize=14,
            textColor=AZUL_UMG,
            spaceBefore=12,
            spaceAfter=6,
            fontName="Helvetica-Bold",
            borderPad=4,
        ),
        "subseccion": ParagraphStyle(
            "subseccion",
            parent=estilos_base["Heading2"],
            fontSize=12,
            textColor=AZUL_CLARO,
            spaceBefore=8,
            spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo",
            parent=estilos_base["Normal"],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
            leading=14,
        ),
        "etiqueta": ParagraphStyle(
            "etiqueta",
            parent=estilos_base["Normal"],
            fontSize=9,
            textColor=GRIS,
            spaceAfter=2,
        ),
        "valor_destacado": ParagraphStyle(
            "valor_destacado",
            parent=estilos_base["Normal"],
            fontSize=11,
            textColor=AZUL_UMG,
            fontName="Helvetica-Bold",
            spaceAfter=2,
        ),
        "decision_texto": ParagraphStyle(
            "decision_texto",
            parent=estilos_base["Normal"],
            fontSize=10,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            leading=14,
            spaceAfter=3,
        ),
        "pie_pagina": ParagraphStyle(
            "pie_pagina",
            parent=estilos_base["Normal"],
            fontSize=8,
            textColor=GRIS,
            alignment=TA_CENTER,
        ),
    }


def _tabla_kpis(kpis: dict, estilos: dict) -> Table:
    """Genera la tabla de indicadores clave del dashboard."""
    datos = [
        ["Indicador", "Valor"],
        ["Total Encuestados", str(kpis.get("total_encuestados", "—"))],
        ["% Usuarios Efectivo", f"{kpis.get('pct_efectivo', '—')}%"],
        ["% Usuarios Digital", f"{kpis.get('pct_digital', '—')}%"],
        ["% Uso Billetera Digital", f"{kpis.get('pct_billetera', '—')}%"],
        ["Gasto Semanal Promedio", f"Q{kpis.get('gasto_promedio', '—')}"],
        ["Confianza Digital Promedio", f"{kpis.get('confianza_promedio', '—')} / 5"],
    ]
    tabla = Table(datos, colWidths=[3.5 * inch, 2.5 * inch])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_UMG),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLANCO),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, AZUL_FONDO]),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla


def _tabla_resultado_prueba(resultado: dict, estilos: dict) -> Table:
    """Genera tabla con los resultados numericos de una prueba."""
    rechaza = resultado.get("rechaza_h0", False)
    datos = [
        ["Parametro", "Valor"],
        ["Estadistico", f"{resultado.get('estadistico', '—'):.4f}"],
        ["p-valor", f"{resultado.get('p_valor', '—'):.6f}"],
        ["Alpha (α)", f"{resultado.get('alpha', 0.05)}"],
        ["Grados de libertad", str(resultado.get("grados_libertad", "N/A"))],
        ["Decision sobre H₀", "RECHAZA H₀" if rechaza else "NO se rechaza H₀"],
    ]
    tabla = Table(datos, colWidths=[3 * inch, 3 * inch])
    color_decision = ROJO if rechaza else VERDE
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_CLARO),
        ("TEXTCOLOR", (0, 0), (-1, 0), BLANCO),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [BLANCO, AZUL_FONDO]),
        ("BACKGROUND", (0, -1), (-1, -1), color_decision),
        ("TEXTCOLOR", (0, -1), (-1, -1), BLANCO),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tabla


def generar_pdf(
    analisis_info: dict,
    kpis: dict,
    resultados_pruebas: list[dict],
    decisiones: list[dict],
    resumen_ejecutivo: str,
    user_email: str,
) -> bytes:
    """
    Genera el reporte PDF completo y lo retorna como bytes.
    Se puede descargar directamente desde Streamlit con st.download_button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    estilos_base = getSampleStyleSheet()
    estilos = _estilos_personalizados(estilos_base)
    elementos = []
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ─── ENCABEZADO ────────────────────────────────────────────────────────────
    elementos.append(Paragraph("Universidad Mariano Galvez de Guatemala", estilos["subtitulo"]))
    elementos.append(Paragraph("Campus Coban, Alta Verapaz", estilos["subtitulo"]))
    elementos.append(Paragraph("Curso de Estadistica II — Ingenieria en Sistemas", estilos["subtitulo"]))
    elementos.append(Spacer(1, 0.15 * inch))
    elementos.append(HRFlowable(width="100%", thickness=2, color=AZUL_UMG))
    elementos.append(Spacer(1, 0.1 * inch))
    elementos.append(Paragraph("Reporte de Analisis Estadistico", estilos["titulo_principal"]))
    elementos.append(Paragraph(
        "Habitos de Pago y Brecha Generacional en Consumidores de Coban",
        estilos["subtitulo"],
    ))
    elementos.append(Spacer(1, 0.1 * inch))
    elementos.append(HRFlowable(width="100%", thickness=2, color=AZUL_UMG))
    elementos.append(Spacer(1, 0.15 * inch))

    info_tabla = Table(
        [
            ["Nombre del analisis:", analisis_info.get("nombre", "Sin nombre")],
            ["Usuario:", user_email],
            ["Fecha de ejecucion:", fecha_hoy],
            ["Total de registros:", str(analisis_info.get("total_registros", "—"))],
            ["Nivel de significancia:", f"α = {analisis_info.get('alpha', 0.05)}"],
        ],
        colWidths=[2.5 * inch, 4.5 * inch],
    )
    info_tabla.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), AZUL_UMG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(info_tabla)
    elementos.append(Spacer(1, 0.2 * inch))

    # ─── INDICADORES CLAVE ─────────────────────────────────────────────────────
    elementos.append(Paragraph("1. Indicadores Clave (KPIs)", estilos["seccion"]))
    elementos.append(_tabla_kpis(kpis, estilos))
    elementos.append(Spacer(1, 0.2 * inch))

    # ─── RESUMEN EJECUTIVO ─────────────────────────────────────────────────────
    elementos.append(Paragraph("2. Resumen Ejecutivo", estilos["seccion"]))
    elementos.append(Paragraph(resumen_ejecutivo, estilos["cuerpo"]))
    elementos.append(Spacer(1, 0.2 * inch))

    # ─── RESULTADOS DE PRUEBAS ─────────────────────────────────────────────────
    elementos.append(Paragraph("3. Resultados de Pruebas Estadisticas", estilos["seccion"]))

    nombres_pruebas = {
        "t_student": "Prueba t de Student — Gasto Semanal: Efectivo vs Digital",
        "chi_cuadrado": "Prueba Chi-cuadrado — Grupo Etario vs Metodo de Pago",
        "z_proporcion": "Prueba Z para Proporcion — Adopcion de Billetera Digital",
    }

    for i, resultado in enumerate(resultados_pruebas, 1):
        tipo = resultado.get("tipo_prueba", f"Prueba {i}")
        titulo = f"3.{i} {tipo}"
        elementos.append(Paragraph(titulo, estilos["subseccion"]))
        elementos.append(_tabla_resultado_prueba(resultado, estilos))
        elementos.append(Spacer(1, 0.15 * inch))

    # ─── DECISIONES EMPRESARIALES ──────────────────────────────────────────────
    elementos.append(PageBreak())
    elementos.append(Paragraph("4. Decisiones Empresariales Generadas", estilos["seccion"]))

    for i, decision in enumerate(decisiones, 1):
        nivel = decision.get("nivel_alerta", "bajo")
        color = _color_alerta(nivel)

        elementos.append(Paragraph(
            f"4.{i} {decision.get('prueba', f'Decision {i}')} "
            f"[Alerta: {nivel.upper()}]",
            estilos["subseccion"],
        ))

        elementos.append(Paragraph("<b>Decision:</b>", estilos["etiqueta"]))
        elementos.append(Paragraph(decision.get("decision", ""), estilos["decision_texto"]))
        elementos.append(Spacer(1, 0.05 * inch))

        elementos.append(Paragraph("<b>Conclusion:</b>", estilos["etiqueta"]))
        elementos.append(Paragraph(decision.get("conclusion", ""), estilos["decision_texto"]))
        elementos.append(Spacer(1, 0.05 * inch))

        elementos.append(Paragraph("<b>Recomendacion:</b>", estilos["etiqueta"]))
        elementos.append(Paragraph(decision.get("recomendacion", ""), estilos["decision_texto"]))
        elementos.append(Spacer(1, 0.15 * inch))

    # ─── PIE DE PAGINA ─────────────────────────────────────────────────────────
    elementos.append(HRFlowable(width="100%", thickness=1, color=GRIS))
    elementos.append(Spacer(1, 0.1 * inch))
    elementos.append(Paragraph(
        f"Generado el {fecha_hoy} | Estadistica II — UMG Coban | "
        "Analisis estadistico de habitos de pago en consumidores de Coban, Alta Verapaz.",
        estilos["pie_pagina"],
    ))

    doc.build(elementos)
    buffer.seek(0)
    return buffer.getvalue()
