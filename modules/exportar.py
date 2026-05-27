"""Generacion de reportes PDF con ReportLab."""

import io
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.shapes import String as GStr
from reportlab.graphics.charts.piecharts import Pie

# ─── Colores ──────────────────────────────────────────────────────────────────
AZUL_UMG   = colors.HexColor("#003087")
AZUL_CLARO = colors.HexColor("#1565C0")
AZUL_FONDO = colors.HexColor("#F0F4FF")
ROJO       = colors.HexColor("#D32F2F")
VERDE      = colors.HexColor("#2E7D32")
NARANJA    = colors.HexColor("#F57C00")
GRIS       = colors.HexColor("#616161")
BLANCO     = colors.white
CYAN       = colors.HexColor("#0077B6")
CELESTE    = colors.HexColor("#00B4D8")


def _color_alerta(nivel: str) -> colors.Color:
    if nivel == "alto":
        return ROJO
    if nivel == "medio":
        return NARANJA
    return VERDE


def _fmt(val, fmt: str = ".4f", fallback: str = "N/A") -> str:
    """Convierte val a string con formato; retorna fallback si falla."""
    try:
        return format(float(val), fmt)
    except (TypeError, ValueError):
        return fallback


# ─── Estilos ──────────────────────────────────────────────────────────────────

def _estilos(base):
    return {
        "titulo_principal": ParagraphStyle(
            "titulo_principal", parent=base["Title"],
            fontSize=20, textColor=AZUL_UMG, alignment=TA_CENTER,
            spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base["Normal"],
            fontSize=12, textColor=AZUL_CLARO, alignment=TA_CENTER, spaceAfter=4,
        ),
        "seccion": ParagraphStyle(
            "seccion", parent=base["Heading1"],
            fontSize=14, textColor=AZUL_UMG,
            spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "subseccion": ParagraphStyle(
            "subseccion", parent=base["Heading2"],
            fontSize=12, textColor=AZUL_CLARO,
            spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold",
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo", parent=base["Normal"],
            fontSize=10, textColor=colors.black,
            alignment=TA_JUSTIFY, spaceAfter=4, leading=14,
        ),
        "etiqueta": ParagraphStyle(
            "etiqueta", parent=base["Normal"],
            fontSize=9, textColor=GRIS, spaceAfter=2,
        ),
        "decision_texto": ParagraphStyle(
            "decision_texto", parent=base["Normal"],
            fontSize=10, textColor=colors.black,
            alignment=TA_JUSTIFY, leading=14, spaceAfter=3,
        ),
        "pie_pagina": ParagraphStyle(
            "pie_pagina", parent=base["Normal"],
            fontSize=8, textColor=GRIS, alignment=TA_CENTER,
        ),
    }


_HDR = [
    ("BACKGROUND", (0, 0), (-1, 0), AZUL_UMG),
    ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
    ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",   (0, 0), (-1, 0), 10),
]
_BASE = [
    ("FONTSIZE",      (0, 1), (-1, -1), 9),
    ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ("ALIGN",         (0, 1), (0,  -1), "LEFT"),
    ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, AZUL_FONDO]),
    ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
    ("TOPPADDING",    (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]


# ─── Tablas ───────────────────────────────────────────────────────────────────

def _tabla_kpis(kpis: dict) -> Table:
    datos = [
        ["Indicador", "Valor"],
        ["Total Encuestados",        str(kpis.get("total_encuestados", "—"))],
        ["% Usuarios Efectivo",      f"{kpis.get('pct_efectivo', '—')}%"],
        ["% Usuarios Digital",       f"{kpis.get('pct_digital', '—')}%"],
        ["% Uso Billetera Digital",  f"{kpis.get('pct_billetera', '—')}%"],
        ["Gasto Semanal Promedio",   f"Q{float(kpis['gasto_promedio']):.2f}" if isinstance(kpis.get('gasto_promedio'), (int, float)) else f"Q{kpis.get('gasto_promedio', '—')}"],
        ["Confianza Digital Promedio",f"{kpis.get('confianza_promedio', '—')} / 5"],
    ]
    t = Table(datos, colWidths=[3.5 * inch, 2.5 * inch])
    t.setStyle(TableStyle(_HDR + _BASE + [
        ("FONTSIZE",       (0, 0), (-1, 0),  11),
        ("TOPPADDING",     (0, 0), (-1, -1),  6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1),  6),
    ]))
    return t


def _tabla_resultado(resultado: dict) -> Table:
    rechaza = resultado.get("rechaza_h0", False)
    gl = resultado.get("grados_libertad")
    datos = [
        ["Parámetro",          "Valor"],
        ["Estadístico",        _fmt(resultado.get("estadistico"), ".4f")],
        ["p-valor",            _fmt(resultado.get("p_valor"),     ".6f")],
        ["Alpha",              str(resultado.get("alpha", 0.05))],
        ["Grados de libertad", str(gl) if gl is not None else "N/A"],
        ["Decision sobre H0",  "RECHAZA H0" if rechaza else "NO se rechaza H0"],
    ]
    color_dec = ROJO if rechaza else VERDE
    t = Table(datos, colWidths=[3 * inch, 3 * inch])
    t.setStyle(TableStyle(_HDR + _BASE + [
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND",    (0, -1), (-1, -1), color_dec),
        ("TEXTCOLOR",     (0, -1), (-1, -1), BLANCO),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    return t


def _tabla_det_t(det: dict) -> Table | None:
    if not det:
        return None
    igual = det.get("varianzas_iguales")
    levene_p = det.get("levene_p")
    datos = [
        ["Detalle",               "Efectivo",                            "Digital"],
        ["n (muestra)",           str(det.get("n_efectivo", "—")),       str(det.get("n_digital", "—"))],
        ["Media gasto semanal (Q)",_fmt(det.get("media_efectivo"), ".2f"),_fmt(det.get("media_digital"), ".2f")],
        ["Desviación estándar (Q)",_fmt(det.get("desv_efectivo"), ".2f"),_fmt(det.get("desv_digital"), ".2f")],
        ["Tipo de prueba t",       det.get("tipo_t", "—"),               ""],
        ["Prueba Levene (p-valor)",
         _fmt(levene_p, ".4f") if levene_p is not None else "—",
         "Varianzas iguales" if igual else "Varianzas desiguales"],
    ]
    t = Table(datos, colWidths=[2.5 * inch, 2 * inch, 2 * inch])
    t.setStyle(TableStyle(_HDR + _BASE))
    return t


def _tabla_det_chi(det: dict) -> Table | None:
    if not det:
        return None
    colapsado = det.get("categorias_colapsadas", False)
    nota_style = ParagraphStyle("nota_chi", fontSize=8, textColor=GRIS, leading=11)
    datos = [
        ["Parámetro",               "Valor"],
        ["V de Cramer",             _fmt(det.get("v_cramer"), ".4f")],
        ["Interpretación V Cramer", det.get("interpretacion_v_cramer", "—")],
        ["n total",                 str(det.get("n_total", "—"))],
        ["Supuesto chi² cumplido",  "Sí" if det.get("supuesto_cumplido") else "No"],
        ["Categorías colapsadas",   "Sí" if colapsado else "No"],
    ]
    if colapsado and det.get("nota_colapso"):
        datos.append(["Nota", Paragraph(det["nota_colapso"], nota_style)])
    t = Table(datos, colWidths=[2.5 * inch, 4 * inch])
    t.setStyle(TableStyle(_HDR + _BASE + [("ALIGN", (0, 0), (-1, -1), "LEFT")]))
    return t


def _tabla_contingencia(tabla_dict: dict) -> Table | None:
    if not tabla_dict:
        return None
    metodos = list(tabla_dict.keys())
    grupos  = list(list(tabla_dict.values())[0].keys()) if metodos else []
    if not metodos or not grupos:
        return None
    filas = [["Grupo etario"] + [str(m) for m in metodos]]
    for g in grupos:
        fila = [str(g)]
        for m in metodos:
            fila.append(str(tabla_dict[m].get(g, 0)))
        filas.append(fila)
    col_w = 6.5 * inch / len(filas[0])
    t = Table(filas, colWidths=[col_w] * len(filas[0]))
    t.setStyle(TableStyle(_HDR + _BASE))
    return t


def _tabla_det_z(det: dict) -> Table | None:
    if not det:
        return None
    ic = det.get("intervalo_confianza_95", [0, 0])
    ic_str = (f"[{float(ic[0])*100:.1f}%,  {float(ic[1])*100:.1f}%]"
              if ic and len(ic) == 2 else "—")
    p_m = det.get("p_muestral", 0)
    p0  = det.get("p0_hipotetico", 0.40)
    datos = [
        ["Parámetro",                  "Valor"],
        ["n total",                    str(det.get("n_total", "—"))],
        ["Éxitos (usan billetera)",    str(det.get("exitos", "—"))],
        ["Proporcion muestral (p^)", f"{_fmt(p_m, '.4f')}  ({_fmt(p_m, '.1%')})"],
        ["Proporcion hipotetica (p0)", f"{_fmt(p0, '.0%')}"],
        ["Intervalo de confianza 95%", ic_str],
        ["Z crítico (unilateral)",     _fmt(det.get("z_critico"), ".4f")],
        ["Supuesto normal cumplido",
         "Sí" if det.get("supuesto_normal_cumplido") else "No"],
    ]
    t = Table(datos, colWidths=[3 * inch, 3 * inch])
    t.setStyle(TableStyle(_HDR + _BASE + [
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


# ─── Gráficas (ReportLab Drawing) ────────────────────────────────────────────

def _chart_pie_pago(pct_ef: float, pct_dig: float) -> Drawing:
    """Pie: distribución efectivo vs digital."""
    d = Drawing(504, 130)
    pie = Pie()
    pie.x, pie.y, pie.width, pie.height = 170, 15, 110, 110
    pie.data   = [max(float(pct_ef or 0), 0.001), max(float(pct_dig or 0), 0.001)]
    pie.labels = ["", ""]
    pie.slices[0].fillColor   = AZUL_UMG
    pie.slices[0].strokeColor = BLANCO
    pie.slices[0].strokeWidth = 0.5
    pie.slices[1].fillColor   = CELESTE
    pie.slices[1].strokeColor = BLANCO
    pie.slices[1].strokeWidth = 0.5
    d.add(pie)
    d.add(Rect(320, 88, 13, 13, fillColor=AZUL_UMG,  strokeColor=None))
    d.add(GStr(338, 89, f"Efectivo  {pct_ef:.1f}%",  fontSize=9, fillColor=colors.black))
    d.add(Rect(320, 66, 13, 13, fillColor=CELESTE,   strokeColor=None))
    d.add(GStr(338, 67, f"Digital   {pct_dig:.1f}%", fontSize=9, fillColor=colors.black))
    return d


def _chart_gasto(media_ef: float, media_dig: float) -> Drawing:
    """Barras horizontales: gasto promedio por método."""
    d = Drawing(504, 90)
    max_v = max(float(media_ef or 1), float(media_dig or 1), 1)
    scale = 270.0 / max_v
    w1 = float(media_ef  or 0) * scale
    w2 = float(media_dig or 0) * scale
    d.add(Rect(130, 52, w1, 24, fillColor=AZUL_UMG, strokeColor=None))
    d.add(GStr(5,   60, "Efectivo", fontSize=9, fillColor=AZUL_UMG))
    d.add(GStr(min(135 + w1, 478), 60, f"Q{media_ef:,.2f}",  fontSize=9, fillColor=AZUL_UMG))
    d.add(Rect(130, 18, w2, 24, fillColor=CELESTE,  strokeColor=None))
    d.add(GStr(5,   26, "Digital",  fontSize=9, fillColor=CYAN))
    d.add(GStr(min(135 + w2, 478), 26, f"Q{media_dig:,.2f}", fontSize=9, fillColor=CYAN))
    return d


def _chart_proporcion(p_muestral: float, p0: float = 0.40) -> Drawing:
    """Barra de progreso: proporción muestral vs umbral hipotético."""
    d = Drawing(504, 72)
    bx, btotal = 100, 300
    p = float(p_muestral or 0)
    d.add(Rect(bx, 26, btotal, 24,
               fillColor=colors.HexColor("#E3F2FD"),
               strokeColor=colors.lightgrey, strokeWidth=0.5))
    fill_w   = min(p * btotal, btotal)
    bar_c    = VERDE if p > p0 else NARANJA
    d.add(Rect(bx, 26, fill_w, 24, fillColor=bar_c, strokeColor=None))
    tx = bx + p0 * btotal
    d.add(Line(tx, 22, tx, 54, strokeColor=ROJO, strokeWidth=2))
    d.add(GStr(5, 34, "Adopción:", fontSize=9, fillColor=colors.black))
    d.add(GStr(min(bx + fill_w + 5, 488), 34,
               f"{p*100:.1f}%", fontSize=10, fillColor=bar_c))
    d.add(GStr(tx - 18, 16, f"umbral {p0*100:.0f}%", fontSize=7, fillColor=ROJO))
    d.add(GStr(bx - 2,  16, "0%",   fontSize=7, fillColor=GRIS))
    d.add(GStr(bx + btotal - 14, 16, "100%", fontSize=7, fillColor=GRIS))
    return d


# ─── Generador principal ──────────────────────────────────────────────────────

def generar_pdf(
    analisis_info: dict,
    kpis: dict,
    resultados_pruebas: list[dict],
    decisiones: list[dict],
    resumen_ejecutivo: str,
    user_email: str,
) -> bytes:
    """Genera el reporte PDF completo y retorna bytes descargables."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=0.75 * inch,   bottomMargin=0.75 * inch,
    )
    base   = getSampleStyleSheet()
    est    = _estilos(base)
    elems  = []
    fecha  = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Encabezado ─────────────────────────────────────────────────────────────
    for txt in [
        "Universidad Mariano Galvez de Guatemala",
        "Campus Coban, Alta Verapaz",
        "Curso de Estadistica II — Ingenieria en Sistemas",
    ]:
        elems.append(Paragraph(txt, est["subtitulo"]))
    elems.append(Spacer(1, 0.15 * inch))
    elems.append(HRFlowable(width="100%", thickness=2, color=AZUL_UMG))
    elems.append(Spacer(1, 0.1  * inch))
    elems.append(Paragraph("Reporte de Analisis Estadistico", est["titulo_principal"]))
    elems.append(Paragraph(
        "Habitos de Pago y Brecha Generacional en Consumidores de Coban",
        est["subtitulo"],
    ))
    elems.append(Spacer(1, 0.1  * inch))
    elems.append(HRFlowable(width="100%", thickness=2, color=AZUL_UMG))
    elems.append(Spacer(1, 0.15 * inch))

    info_t = Table(
        [
            ["Nombre del analisis:", analisis_info.get("nombre", "Sin nombre")],
            ["Usuario:",             user_email],
            ["Fecha de ejecucion:",  fecha],
            ["Total de registros:",  str(analisis_info.get("total_registros", "—"))],
            ["Nivel de significancia:", f"alpha = {analisis_info.get('alpha', 0.05)}"],
        ],
        colWidths=[2.5 * inch, 4.5 * inch],
    )
    info_t.setStyle(TableStyle([
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("FONTNAME",      (0, 0), (0,  -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 0), (0,  -1), AZUL_UMG),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elems.append(info_t)
    elems.append(Spacer(1, 0.2 * inch))

    # ── 1. KPIs ────────────────────────────────────────────────────────────────
    elems.append(Paragraph("1. Indicadores Clave (KPIs)", est["seccion"]))
    elems.append(_tabla_kpis(kpis))
    pct_ef  = kpis.get("pct_efectivo")
    pct_dig = kpis.get("pct_digital")
    if pct_ef is not None and pct_dig is not None:
        try:
            elems.append(Spacer(1, 0.1 * inch))
            elems.append(Paragraph("Distribución del método de pago principal:", est["etiqueta"]))
            elems.append(_chart_pie_pago(float(pct_ef), float(pct_dig)))
        except Exception:
            pass
    elems.append(Spacer(1, 0.2 * inch))

    # ── 2. Resumen ejecutivo ───────────────────────────────────────────────────
    elems.append(Paragraph("2. Resumen Ejecutivo", est["seccion"]))
    elems.append(Paragraph(resumen_ejecutivo, est["cuerpo"]))
    elems.append(Spacer(1, 0.2 * inch))

    # ── 3. Resultados de pruebas ───────────────────────────────────────────────
    elems.append(Paragraph("3. Resultados de Pruebas Estadisticas", est["seccion"]))

    if not resultados_pruebas:
        elems.append(Paragraph(
            "No se encontraron resultados. Ejecute el analisis desde Nuevo Analisis.",
            est["cuerpo"],
        ))
    else:
        for i, res in enumerate(resultados_pruebas, 1):
            tipo  = res.get("tipo_prueba", f"Prueba {i}")
            det   = res.get("detalles") or {}
            tl    = tipo.lower()

            elems.append(Paragraph(f"3.{i} {tipo}", est["subseccion"]))
            elems.append(_tabla_resultado(res))
            elems.append(Spacer(1, 0.12 * inch))

            if "student" in tl or "t de" in tl:
                t_det = _tabla_det_t(det)
                if t_det:
                    elems.append(Paragraph("Estadísticos descriptivos por grupo:", est["etiqueta"]))
                    elems.append(t_det)
                    elems.append(Spacer(1, 0.1 * inch))
                me = det.get("media_efectivo")
                md = det.get("media_digital")
                if me is not None and md is not None:
                    try:
                        elems.append(Paragraph("Comparación gasto promedio semanal (Q):", est["etiqueta"]))
                        elems.append(_chart_gasto(float(me), float(md)))
                    except Exception:
                        pass

            elif "chi" in tl:
                t_det = _tabla_det_chi(det)
                if t_det:
                    elems.append(Paragraph("Medida de efecto y supuestos:", est["etiqueta"]))
                    elems.append(t_det)
                    elems.append(Spacer(1, 0.1 * inch))
                tabla_cont = det.get("tabla_contingencia")
                if tabla_cont:
                    ct = _tabla_contingencia(tabla_cont)
                    if ct:
                        elems.append(Paragraph("Tabla de contingencia observada:", est["etiqueta"]))
                        elems.append(ct)

            elif "z" in tl or "proporcion" in tl:
                t_det = _tabla_det_z(det)
                if t_det:
                    elems.append(Paragraph("Parámetros de la prueba:", est["etiqueta"]))
                    elems.append(t_det)
                    elems.append(Spacer(1, 0.1 * inch))
                pm = det.get("p_muestral")
                p0 = det.get("p0_hipotetico", 0.40)
                if pm is not None:
                    try:
                        elems.append(Paragraph("Proporción muestral vs umbral hipotético:", est["etiqueta"]))
                        elems.append(_chart_proporcion(float(pm), float(p0)))
                    except Exception:
                        pass

            elems.append(Spacer(1, 0.2 * inch))

    # ── 4. Decisiones empresariales ────────────────────────────────────────────
    elems.append(PageBreak())
    elems.append(Paragraph("4. Decisiones Empresariales Generadas", est["seccion"]))

    for i, dec in enumerate(decisiones, 1):
        nivel = dec.get("nivel_alerta", "bajo")
        elems.append(Paragraph(
            f"4.{i} {dec.get('prueba', f'Decision {i}')}  [Alerta: {nivel.upper()}]",
            est["subseccion"],
        ))
        elems.append(Paragraph("<b>Decisión:</b>",      est["etiqueta"]))
        elems.append(Paragraph(dec.get("decision",      ""), est["decision_texto"]))
        elems.append(Spacer(1, 0.05 * inch))
        elems.append(Paragraph("<b>Conclusión:</b>",    est["etiqueta"]))
        elems.append(Paragraph(dec.get("conclusion",    ""), est["decision_texto"]))
        elems.append(Spacer(1, 0.05 * inch))
        elems.append(Paragraph("<b>Recomendación:</b>", est["etiqueta"]))
        elems.append(Paragraph(dec.get("recomendacion", ""), est["decision_texto"]))
        elems.append(Spacer(1, 0.15 * inch))

    # ── Pie ────────────────────────────────────────────────────────────────────
    elems.append(HRFlowable(width="100%", thickness=1, color=GRIS))
    elems.append(Spacer(1, 0.1 * inch))
    elems.append(Paragraph(
        f"Generado el {fecha} | Estadistica II — UMG Coban | "
        "Analisis estadistico de habitos de pago en consumidores de Coban, Alta Verapaz.",
        est["pie_pagina"],
    ))

    doc.build(elems)
    buffer.seek(0)
    return buffer.getvalue()
