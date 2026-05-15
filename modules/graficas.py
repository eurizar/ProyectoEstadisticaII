"""Visualizaciones interactivas con Plotly para el dashboard estadistico."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats

# Paleta institucional UMG
AZUL_UMG = "#003087"
AZUL_CLARO = "#1565C0"
AZUL_ACENTO = "#42A5F5"
GRIS_CLARO = "#F0F4FF"
ROJO_ALERTA = "#D32F2F"
VERDE_OK = "#2E7D32"
NARANJA = "#F57C00"

COLORES_CATEGORIAS = [
    AZUL_UMG, "#1565C0", "#1976D2", "#1E88E5", "#42A5F5",
    "#64B5F6", "#90CAF9", "#BBDEFB", "#0D47A1", "#0277BD",
]

# Paleta corporativa monocromática
CORP_NAVY = "#003087"
CORP_NAVY_2 = "#1A4A9F"
CORP_NAVY_3 = "#4F7BC4"
CORP_NAVY_4 = "#B3CDEA"
CORP_RED = "#C8102E"
CORP_GREEN = "#0D6E3E"
CORP_GOLD = "#C9A846"
CORP_GRAY = "#9CA3AF"
CORP_GRID = "#E5E7EB"
CORP_BG = "#FFFFFF"


def _estilo_corporativo(fig: go.Figure, height: int = 320, show_legend: bool = True) -> go.Figure:
    """Aplica estilo corporativo uniforme: white bg, gridlines tenues, mono fonts en ejes.
    Modebar vertical derecha + legend abajo para evitar traslape."""
    fig.update_layout(
        plot_bgcolor=CORP_BG,
        paper_bgcolor=CORP_BG,
        height=height,
        margin=dict(l=50, r=40, t=20, b=70),
        font=dict(family="Source Sans 3, system-ui, sans-serif", size=11.5, color="#374151"),
        hoverlabel=dict(
            bgcolor="#0A0F1E",
            bordercolor="#0A0F1E",
            font=dict(color="white", family="Source Sans 3", size=12),
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="top", y=-0.18,
            xanchor="left", x=0,
            bgcolor="rgba(255,255,255,0)", bordercolor="rgba(0,0,0,0)",
            font=dict(size=10.5, color="#4B5563"),
            title=dict(text=""),
            itemwidth=30,
        ),
        modebar=dict(
            orientation="v",
            bgcolor="rgba(255,255,255,0.85)",
            color="#9CA3AF",
            activecolor=CORP_NAVY,
        ),
        title=dict(text=""),
        legend_title_text="",
    )
    fig.update_xaxes(
        gridcolor=CORP_GRID, zeroline=False, showline=True,
        linecolor=CORP_GRID, linewidth=1,
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#6B7280"),
        title=dict(font=dict(size=10.5, color="#6B7280")),
    )
    fig.update_yaxes(
        gridcolor=CORP_GRID, zeroline=False, showline=False,
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#6B7280"),
        title=dict(font=dict(size=10.5, color="#6B7280")),
    )
    return fig


def _hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def grafica_sparkline(serie_valores, color: str = CORP_NAVY) -> go.Figure:
    """Mini sparkline para KPI tile."""
    valores = list(serie_valores)
    fig = go.Figure(data=[go.Scatter(
        x=list(range(len(valores))), y=valores,
        mode="lines",
        line=dict(color=color, width=1.8, shape="spline"),
        fill="tozeroy",
        fillcolor=_hex_to_rgba(color, 0.14),
        hoverinfo="skip",
    )])
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=38, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def grafica_distribucion_metodos_pago(df: pd.DataFrame) -> go.Figure:
    """Grafica de barras: distribucion de metodos de pago preferidos."""
    conteo = df["metodo_pago_preferido"].value_counts()
    pct = (conteo / conteo.sum() * 100).round(1)
    etiquetas = [f"{v} · {p}%" for v, p in zip(conteo.values, pct.values)]

    max_v = int(conteo.values.max()) if len(conteo) else 1
    colores = []
    for v in conteo.values:
        t = v / max_v
        if t > .75: colores.append(CORP_NAVY)
        elif t > .50: colores.append(CORP_NAVY_2)
        elif t > .25: colores.append(CORP_NAVY_3)
        else: colores.append(CORP_NAVY_4)

    fig = go.Figure(data=[go.Bar(
        x=conteo.index, y=conteo.values,
        text=etiquetas, textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=CORP_NAVY),
        marker=dict(color=colores, line=dict(width=0)),
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Casos: <b>%{y}</b><br>Proporción: <b>%{customdata}%</b><extra></extra>",
        customdata=pct.values,
    )])
    # Y range con espacio extra para labels outside
    fig.update_layout(
        xaxis=dict(title=""),
        yaxis=dict(title="Consumidores", range=[0, max_v * 1.18]),
    )
    return _estilo_corporativo(fig, height=340, show_legend=False)


def grafica_distribucion_grupos_etarios(df: pd.DataFrame) -> go.Figure:
    """Donut por grupo etario."""
    conteo = df["grupo_etario"].value_counts()
    orden = ["18-25", "26-35", "36-50", "51+"]
    conteo = conteo.reindex([g for g in orden if g in conteo.index])

    paleta = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4, CORP_GOLD]
    fig = go.Figure(data=[go.Pie(
        labels=conteo.index, values=conteo.values,
        hole=0.55,
        marker=dict(colors=paleta[:len(conteo)], line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(family="Source Sans 3", size=11),
        hovertemplate="<b>%{label}</b><br>Casos: <b>%{value}</b><br>Proporción: <b>%{percent}</b><extra></extra>",
    )])
    fig.update_layout(
        plot_bgcolor=CORP_BG, paper_bgcolor=CORP_BG,
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        annotations=[dict(
            text=f"<b>n={int(conteo.sum())}</b>",
            x=0.5, y=0.5, font=dict(size=14, color=CORP_NAVY, family="JetBrains Mono"),
            showarrow=False,
        )],
    )
    return fig


def grafica_gasto_semanal_boxplot(df: pd.DataFrame) -> go.Figure:
    """Boxplot comparativo del gasto semanal por metodo de pago (efectivo vs digital)."""
    efectivo = df[df["metodo_pago_preferido"] == "Efectivo"]["gasto_semanal"].dropna()
    digital = df[df["metodo_pago_preferido"] != "Efectivo"]["gasto_semanal"].dropna()

    fig = go.Figure()
    fig.add_trace(go.Box(
        y=efectivo, name="Efectivo",
        marker=dict(color=CORP_NAVY, size=4, opacity=.5),
        line=dict(color=CORP_NAVY, width=1.5),
        fillcolor=_hex_to_rgba(CORP_NAVY, 0.18),
        boxmean="sd", boxpoints="outliers",
        hovertemplate="<b>Efectivo</b><br>Q%{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Box(
        y=digital, name="Digital",
        marker=dict(color=CORP_NAVY_3, size=4, opacity=.5),
        line=dict(color=CORP_NAVY_3, width=1.5),
        fillcolor=_hex_to_rgba(CORP_NAVY_3, 0.20),
        boxmean="sd", boxpoints="outliers",
        hovertemplate="<b>Digital</b><br>Q%{y:.2f}<extra></extra>",
    ))
    fig.update_layout(yaxis_title="Gasto (Q)")
    return _estilo_corporativo(fig, height=300)


def grafica_barras_apiladas_100(resultado_chi: dict) -> go.Figure:
    """Barras 100% apiladas — perfil de cada grupo etario por metodo de pago.
    Lectura clasica para Chi-cuadrado: si todas las barras tienen patron similar -> independientes;
    si difieren -> asociadas."""
    tabla = resultado_chi.get("tabla_contingencia", {})
    if not tabla:
        return go.Figure()

    df_tabla = pd.DataFrame(tabla)
    orden_filas = ["18-25", "26-35", "36-50", "51+"]
    df_tabla = df_tabla.reindex([f for f in orden_filas if f in df_tabla.index])

    # Convertir a porcentajes por fila
    totales = df_tabla.sum(axis=1).replace(0, np.nan)
    pct = df_tabla.div(totales, axis=0) * 100

    paleta = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4, CORP_GOLD, CORP_GRAY]

    fig = go.Figure()
    for i, metodo in enumerate(df_tabla.columns):
        valores_pct = pct[metodo].values
        valores_abs = df_tabla[metodo].values
        color = paleta[i % len(paleta)]
        # Etiqueta solo si segmento >= 8% (evita texto encimado)
        textos = [f"{p:.0f}%" if p >= 8 else "" for p in valores_pct]
        # Color texto: blanco sobre tonos oscuros, navy sobre claros
        text_colors = ["white" if i < 3 else CORP_NAVY for _ in valores_pct]

        fig.add_trace(go.Bar(
            name=metodo,
            x=df_tabla.index,
            y=valores_pct,
            customdata=np.stack([valores_abs, valores_pct], axis=-1),
            text=textos,
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(family="JetBrains Mono", size=11, color=text_colors[0]),
            marker=dict(color=color, line=dict(width=0)),
            hovertemplate=(
                f"<b>{metodo}</b><br>"
                "Grupo: <b>%{x}</b><br>"
                "Casos: <b>%{customdata[0]:.0f}</b><br>"
                "Proporción: <b>%{customdata[1]:.1f}%</b><extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Grupo Etario", categoryorder="array",
                   categoryarray=list(df_tabla.index)),
        yaxis=dict(title="% del grupo", ticksuffix="%", range=[0, 100]),
        bargap=0.25,
    )
    fig = _estilo_corporativo(fig, height=400, show_legend=True)
    # Override: legenda más prominente para este chart
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=11, color="#374151"),
            bgcolor="rgba(255,255,255,0)",
        ),
        margin=dict(l=60, r=20, t=30, b=50),
    )
    return fig


def grafica_heatmap_chi_cuadrado(resultado_chi: dict) -> go.Figure:
    """Heatmap de la tabla de contingencia con anotaciones (count + % fila)
    + hover con frecuencia esperada y contribucion al chi2."""
    tabla = resultado_chi.get("tabla_contingencia", {})
    esperadas = resultado_chi.get("frecuencias_esperadas", {})
    if not tabla:
        return go.Figure()

    df_tabla = pd.DataFrame(tabla)
    df_esp = pd.DataFrame(esperadas) if esperadas else df_tabla * 0
    orden_filas = ["18-25", "26-35", "36-50", "51+"]
    filas_presentes = [f for f in orden_filas if f in df_tabla.index]
    df_tabla = df_tabla.reindex(filas_presentes)
    df_esp = df_esp.reindex(filas_presentes)

    # Porcentaje por fila (perfil de cada grupo etario)
    totales_fila = df_tabla.sum(axis=1).replace(0, np.nan)
    pct_fila = df_tabla.div(totales_fila, axis=0) * 100

    # Annotations: count grande + % chico
    annotations = []
    for i, fila in enumerate(df_tabla.index):
        for j, col in enumerate(df_tabla.columns):
            count = int(df_tabla.iloc[i, j])
            pct = pct_fila.iloc[i, j]
            color_txt = "white" if count > df_tabla.values.max() * 0.55 else AZUL_UMG
            annotations.append(dict(
                x=col, y=fila,
                text=f"<b>{count}</b><br><span style='font-size:10px;opacity:.85'>{pct:.0f}%</span>",
                showarrow=False, font=dict(color=color_txt, size=13),
            ))

    # Hover personalizado
    hover_text = []
    for i, fila in enumerate(df_tabla.index):
        fila_hover = []
        for j, col in enumerate(df_tabla.columns):
            obs = int(df_tabla.iloc[i, j])
            esp = float(df_esp.iloc[i, j]) if not df_esp.empty else 0
            contrib = ((obs - esp) ** 2 / esp) if esp > 0 else 0
            fila_hover.append(
                f"<b>{fila} × {col}</b><br>"
                f"Observado: <b>{obs}</b><br>"
                f"Esperado: <b>{esp:.2f}</b><br>"
                f"% de la fila: <b>{pct_fila.iloc[i, j]:.1f}%</b><br>"
                f"Contribución χ²: <b>{contrib:.3f}</b>"
            )
        hover_text.append(fila_hover)

    fig = go.Figure(data=go.Heatmap(
        z=df_tabla.values,
        x=list(df_tabla.columns),
        y=list(df_tabla.index),
        colorscale=[
            [0.0, "#EEF4FF"], [0.25, "#B3CDEA"],
            [0.55, AZUL_ACENTO], [0.80, AZUL_CLARO], [1.0, AZUL_UMG],
        ],
        hovertext=hover_text,
        hoverinfo="text",
        colorbar=dict(title=dict(text="Frecuencia", side="right"), thickness=14, len=.7),
        xgap=3, ygap=3,
    ))
    fig.update_layout(
        annotations=annotations,
        title=dict(
            text="<b>Tabla de Contingencia</b>  ·  Grupo Etario × Método de Pago<br>"
                 "<span style='font-size:11px;color:#3D4966'>"
                 "Número grande = casos observados · % = proporción dentro del grupo etario "
                 "· hover muestra valor esperado y contribución χ²</span>",
            font=dict(size=14, color=AZUL_UMG),
        ),
        xaxis=dict(title="Método de Pago", tickfont=dict(size=11), side="bottom"),
        yaxis=dict(title="Grupo Etario", tickfont=dict(size=11), autorange="reversed"),
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Source Sans 3, Arial", size=12),
        height=420, margin=dict(l=80, r=30, t=90, b=70),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# NUEVOS: tabla de frecuencias + scatter dispersion
# ─────────────────────────────────────────────────────────────────────────────

def tabla_frecuencias(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """DataFrame con freq absoluta, relativa %, acumulada y acumulada %."""
    serie = df[columna].dropna().astype(str).value_counts().reset_index()
    serie.columns = [columna, "f_absoluta"]
    serie["f_relativa_%"] = (serie["f_absoluta"] / serie["f_absoluta"].sum() * 100).round(2)
    serie["f_acumulada"] = serie["f_absoluta"].cumsum()
    serie["f_acumulada_%"] = serie["f_relativa_%"].cumsum().round(2)
    return serie


def grafica_tabla_frecuencias(df: pd.DataFrame, columna: str, titulo: str = None) -> go.Figure:
    """Tabla interactiva de frecuencias estilo Plotly."""
    tabla = tabla_frecuencias(df, columna)
    titulo = titulo or f"Tabla de Frecuencias · {columna}"

    # Color de filas alternadas para legibilidad
    fila_colors = [
        ["#EEF4FF" if i % 2 == 0 else "#FFFFFF" for i in range(len(tabla))]
    ] * len(tabla.columns)

    fig = go.Figure(data=[go.Table(
        columnwidth=[2, 1, 1, 1, 1],
        header=dict(
            values=[
                f"<b>{columna.replace('_', ' ').title()}</b>",
                "<b>fᵢ</b><br><span style='font-size:9px;font-weight:400'>absoluta</span>",
                "<b>hᵢ %</b><br><span style='font-size:9px;font-weight:400'>relativa</span>",
                "<b>Fᵢ</b><br><span style='font-size:9px;font-weight:400'>acumulada</span>",
                "<b>Hᵢ %</b><br><span style='font-size:9px;font-weight:400'>acum.</span>",
            ],
            fill_color=AZUL_UMG,
            font=dict(color="white", size=12, family="Source Sans 3"),
            align=["left", "center", "center", "center", "center"],
            height=44,
            line=dict(color=AZUL_UMG, width=0),
        ),
        cells=dict(
            values=[
                tabla[columna],
                tabla["f_absoluta"],
                tabla["f_relativa_%"].astype(str) + " %",
                tabla["f_acumulada"],
                tabla["f_acumulada_%"].astype(str) + " %",
            ],
            fill_color=fila_colors,
            font=dict(color="#0A0F1E", size=12, family="Source Sans 3"),
            align=["left", "center", "center", "center", "center"],
            height=32,
            line=dict(color="#D6E3F8", width=1),
        ),
    )])
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b>  ·  <span style='font-size:11px;color:#3D4966'>"
                 f"n = {tabla['f_absoluta'].sum()} observaciones</span>",
            font=dict(size=14, color=AZUL_UMG),
        ),
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=55, b=10),
        height=80 + 38 * len(tabla),
    )
    return fig


def grafica_dispersion(df: pd.DataFrame) -> go.Figure:
    """Scatter dispersion: edad vs gasto_semanal coloreado por metodo + linea de tendencia."""
    if "edad" not in df.columns or "gasto_semanal" not in df.columns:
        return go.Figure()

    sub = df.dropna(subset=["edad", "gasto_semanal"]).copy()
    sub["edad"] = sub["edad"].astype(float)
    sub["gasto_semanal"] = sub["gasto_semanal"].astype(float)
    if "confianza_digital" in sub.columns:
        sub["confianza_digital"] = pd.to_numeric(sub["confianza_digital"], errors="coerce").fillna(3)
    else:
        sub["confianza_digital"] = 3

    fig = px.scatter(
        sub,
        x="edad", y="gasto_semanal",
        color="metodo_pago_preferido" if "metodo_pago_preferido" in sub.columns else None,
        size="confianza_digital",
        size_max=20,
        color_discrete_sequence=COLORES_CATEGORIAS,
        hover_data={
            "edad": ":.0f",
            "gasto_semanal": ":Q.2f",
            "grupo_etario": True if "grupo_etario" in sub.columns else False,
            "ingreso_mensual": True if "ingreso_mensual" in sub.columns else False,
            "confianza_digital": ":.0f",
        },
        labels={
            "edad": "Edad (años)",
            "gasto_semanal": "Gasto Semanal (Q)",
            "metodo_pago_preferido": "Método de pago",
            "confianza_digital": "Confianza",
        },
    )

    # Trendline manual via numpy polyfit (no necesita statsmodels)
    if len(sub) >= 2:
        coef = np.polyfit(sub["edad"], sub["gasto_semanal"], 1)
        x_line = np.linspace(sub["edad"].min(), sub["edad"].max(), 50)
        y_line = np.polyval(coef, x_line)
        r = float(np.corrcoef(sub["edad"], sub["gasto_semanal"])[0, 1])
        fig.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode="lines",
            name=f"Tendencia OLS (r = {r:+.3f})",
            line=dict(color=ROJO_ALERTA, width=2.5, dash="dash"),
            hovertemplate=f"<b>Tendencia lineal</b><br>pendiente: {coef[0]:.2f} Q/año<br>r: {r:+.3f}<extra></extra>",
        ))

    fig.update_traces(
        selector=dict(mode="markers"),
        marker=dict(line=dict(width=1.2, color="white"), opacity=.85),
    )
    fig.update_layout(hovermode="closest")
    return _estilo_corporativo(fig, height=420, show_legend=True)


def grafica_z_proporcion(resultado_z: dict) -> go.Figure:
    """Visualizacion de la prueba Z: curva normal con zona de rechazo."""
    z_obs = resultado_z.get("estadistico", 0)
    alpha = resultado_z.get("alpha", 0.05)
    z_critico = resultado_z.get("detalles", {}).get("z_critico", 1.645)
    p_muestral = resultado_z.get("detalles", {}).get("p_muestral", 0)
    p0 = resultado_z.get("detalles", {}).get("p0_hipotetico", 0.40)

    x = np.linspace(-4, 4, 400)
    y = stats.norm.pdf(x)

    fig = go.Figure()

    # Curva normal completa
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color=CORP_NAVY, width=2),
        name="N(0,1)",
        hovertemplate="Z = %{x:.2f}<br>f(Z) = %{y:.4f}<extra></extra>",
    ))

    # Zona de rechazo (derecha)
    x_rechazo = x[x >= z_critico]
    y_rechazo = stats.norm.pdf(x_rechazo)
    fig.add_trace(go.Scatter(
        x=np.concatenate([[x_rechazo[0]], x_rechazo, [x_rechazo[-1]]]),
        y=np.concatenate([[0], y_rechazo, [0]]),
        fill="toself",
        fillcolor="rgba(200, 16, 46, 0.18)",
        line=dict(color=ROJO_ALERTA, width=1),
        name=f"Zona rechazo · α={alpha}",
        hoverinfo="skip",
    ))

    # Lineas verticales — sin anotaciones encimadas
    fig.add_vline(x=z_critico, line_dash="dash", line_color=ROJO_ALERTA, line_width=1.5)
    color_obs = ROJO_ALERTA if z_obs > z_critico else VERDE_OK
    fig.add_vline(x=z_obs, line_dash="solid", line_color=color_obs, line_width=2)

    # Anotaciones desplazadas verticalmente para no traslaparse
    y_max = float(stats.norm.pdf(0))
    fig.add_annotation(
        x=z_critico, y=y_max * 0.95,
        text=f"<b>Z crítico</b><br>{z_critico:.3f}",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1, arrowcolor=ROJO_ALERTA,
        ax=40, ay=-10,
        font=dict(family="JetBrains Mono", size=10, color=ROJO_ALERTA),
        bgcolor="rgba(255,255,255,0.92)", bordercolor=ROJO_ALERTA, borderwidth=1, borderpad=4,
    )
    fig.add_annotation(
        x=z_obs, y=y_max * 0.55,
        text=f"<b>Z obs</b><br>{z_obs:+.3f}",
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1, arrowcolor=color_obs,
        ax=-50 if z_obs > z_critico else 50, ay=-10,
        font=dict(family="JetBrains Mono", size=10, color=color_obs),
        bgcolor="rgba(255,255,255,0.92)", bordercolor=color_obs, borderwidth=1, borderpad=4,
    )

    fig.update_layout(
        xaxis_title="Valor Z",
        yaxis_title="Densidad",
    )
    fig = _estilo_corporativo(fig, height=380, show_legend=True)
    # Override: legend centrada + más margen abajo (anotaciones grandes arriba)
    fig.update_layout(
        margin=dict(l=55, r=45, t=30, b=80),
        legend=dict(
            orientation="h", yanchor="top", y=-0.20,
            xanchor="center", x=0.5,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=10.5, color="#4B5563"),
            title=dict(text=""),
        ),
    )
    return fig


def grafica_ingreso_vs_metodo(df: pd.DataFrame) -> go.Figure:
    """Barras apiladas: ingreso mensual vs metodo de pago preferido."""
    orden_ingreso = [
        "<Q1500", "Q1500-3000", "Q3000-5000", "Q5000-10000", ">Q10000"
    ]
    ingreso_existentes = [i for i in orden_ingreso if i in df["ingreso_mensual"].unique()]

    tabla = pd.crosstab(df["ingreso_mensual"], df["metodo_pago_preferido"])
    tabla = tabla.reindex([i for i in ingreso_existentes if i in tabla.index])

    paleta_corp = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4, CORP_GOLD]

    fig = px.bar(
        tabla.reset_index().melt(id_vars="ingreso_mensual"),
        x="ingreso_mensual", y="value",
        color="metodo_pago_preferido",
        barmode="stack",
        color_discrete_sequence=paleta_corp,
        labels={"ingreso_mensual": "", "value": "Casos",
                "metodo_pago_preferido": "Método"},
        category_orders={"ingreso_mensual": ingreso_existentes},
    )
    fig.update_traces(marker_line_width=0, hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}<extra></extra>")
    return _estilo_corporativo(fig, height=320)


def grafica_confianza_digital(df: pd.DataFrame) -> go.Figure:
    """Histograma del nivel de confianza en pagos digitales (escala 1-5)."""
    conteo = df["confianza_digital"].value_counts().sort_index()

    # Gradient navy según valor (1=claro, 5=oscuro)
    paleta = [CORP_NAVY_4, "#7FA0CC", CORP_NAVY_3, CORP_NAVY_2, CORP_NAVY]

    fig = go.Figure(data=[go.Bar(
        x=conteo.index.astype(str),
        y=conteo.values,
        marker=dict(color=[paleta[min(int(i)-1, len(paleta)-1)] for i in conteo.index], line=dict(width=0)),
        text=conteo.values,
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=CORP_NAVY),
        hovertemplate="Nivel <b>%{x}</b><br>%{y} consumidores<extra></extra>",
    )])
    fig.update_layout(
        xaxis_title="Nivel (1=Bajo, 5=Alto)",
        yaxis_title="Consumidores",
        showlegend=False,
    )
    return _estilo_corporativo(fig, height=300, show_legend=False)


def grafica_uso_billetera_digital(df: pd.DataFrame) -> go.Figure:
    """Donut: adopcion de billetera digital."""
    conteo = df["uso_billetera_digital"].value_counts()
    etiquetas = ["Sí ha usado" if bool(v) else "No ha usado" for v in conteo.index]
    colores = [CORP_NAVY if bool(v) else CORP_NAVY_4 for v in conteo.index]

    fig = go.Figure(data=[go.Pie(
        labels=etiquetas, values=conteo.values,
        hole=0.55,
        marker=dict(colors=colores, line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(family="Source Sans 3", size=12),
        hovertemplate="<b>%{label}</b><br>Casos: <b>%{value}</b><br>Proporción: <b>%{percent}</b><extra></extra>",
    )])
    total = int(conteo.sum())
    pct_si = float(conteo.get(True, 0)) / total * 100 if total else 0
    fig.update_layout(
        plot_bgcolor=CORP_BG, paper_bgcolor=CORP_BG,
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False,
        annotations=[dict(
            text=f"<b>{pct_si:.0f}%</b><br><span style='font-size:10px;color:#6B7280'>adopción</span>",
            x=0.5, y=0.5, font=dict(size=18, color=CORP_NAVY, family="JetBrains Mono"),
            showarrow=False,
        )],
    )
    return fig


def grafica_gasto_por_grupo_etario(df: pd.DataFrame) -> go.Figure:
    """Barras con error: gasto semanal promedio por grupo etario."""
    orden = ["18-25", "26-35", "36-50", "51+"]
    grupos = [g for g in orden if g in df["grupo_etario"].unique()]

    medias, desv, n_grupos = [], [], []
    for grupo in grupos:
        sub = df[df["grupo_etario"] == grupo]["gasto_semanal"].dropna()
        medias.append(sub.mean())
        desv.append(sub.std(ddof=1) if len(sub) > 1 else 0)
        n_grupos.append(len(sub))

    # Tono navy según índice
    paleta = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4]
    colores = [paleta[i % len(paleta)] for i in range(len(grupos))]

    fig = go.Figure(data=[go.Bar(
        x=grupos, y=medias,
        error_y=dict(type="data", array=desv, visible=True, color=CORP_GRAY, thickness=1.2, width=8),
        marker=dict(
            color=colores,
            line=dict(width=0),
        ),
        text=[f"Q{m:.0f}" for m in medias],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color=CORP_NAVY),
        hovertemplate="<b>%{x}</b><br>Media: <b>Q%{y:.2f}</b><br>n: <b>%{customdata}</b><extra></extra>",
        customdata=n_grupos,
    )])
    fig.update_layout(
        xaxis_title="", yaxis_title="Gasto medio (Q)",
        showlegend=False,
    )
    return _estilo_corporativo(fig, height=300, show_legend=False)


def grafica_barras_categoria(df: pd.DataFrame, columna: str, titulo: str = None,
                              horizontal: bool = False, top_n: int = None) -> go.Figure:
    """Barras simples para variable categorica. Si horizontal=True, barras horizontales (mejor para etiquetas largas)."""
    if columna not in df.columns:
        return go.Figure()

    conteo = df[columna].dropna().astype(str).value_counts()
    if top_n:
        conteo = conteo.head(top_n)

    total = int(conteo.sum())
    pct = (conteo / total * 100).round(1)
    etiquetas = [f"{v} · {p}%" for v, p in zip(conteo.values, pct.values)]

    # Gradient navy: barra mayor = más oscuro
    max_v = int(conteo.values.max()) if len(conteo) else 1
    colores = []
    for v in conteo.values:
        t = (v / max_v) if max_v > 0 else 0
        if t > .75: colores.append(CORP_NAVY)
        elif t > .50: colores.append(CORP_NAVY_2)
        elif t > .25: colores.append(CORP_NAVY_3)
        else: colores.append(CORP_NAVY_4)

    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=conteo.index, x=conteo.values,
            text=etiquetas, textposition="outside",
            textfont=dict(family="JetBrains Mono", size=11, color=CORP_NAVY),
            orientation="h",
            marker=dict(color=colores, line=dict(width=0)),
            hovertemplate="<b>%{y}</b><br>Casos: <b>%{x}</b><br>Proporción: <b>%{customdata}%</b><extra></extra>",
            customdata=pct.values,
        )])
        fig.update_layout(yaxis=dict(autorange="reversed", title=""),
                          xaxis=dict(title="Casos"))
        height = max(220, 36 * len(conteo) + 80)
    else:
        fig = go.Figure(data=[go.Bar(
            x=conteo.index, y=conteo.values,
            text=etiquetas, textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color=CORP_NAVY),
            marker=dict(color=colores, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Casos: <b>%{y}</b><br>Proporción: <b>%{customdata}%</b><extra></extra>",
            customdata=pct.values,
        )])
        fig.update_layout(xaxis=dict(title=""), yaxis=dict(title="Casos"))
        height = 320

    return _estilo_corporativo(fig, height=height, show_legend=False)


def grafica_donut(df: pd.DataFrame, columna: str, titulo: str = None) -> go.Figure:
    """Donut chart para variable categorica."""
    if columna not in df.columns:
        return go.Figure()
    conteo = df[columna].dropna().astype(str).value_counts()
    paleta = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4, CORP_GOLD, CORP_GRAY]

    fig = go.Figure(data=[go.Pie(
        labels=conteo.index, values=conteo.values,
        hole=0.55,
        marker=dict(colors=paleta[:len(conteo)], line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont=dict(family="Source Sans 3", size=11),
        hovertemplate="<b>%{label}</b><br>Casos: <b>%{value}</b><br>Proporción: <b>%{percent}</b><extra></extra>",
    )])
    fig.update_layout(
        plot_bgcolor=CORP_BG, paper_bgcolor=CORP_BG,
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        annotations=[dict(
            text=f"<b>n={int(conteo.sum())}</b>",
            x=0.5, y=0.5, font=dict(size=14, color=CORP_NAVY, family="JetBrains Mono"),
            showarrow=False,
        )],
    )
    return fig


def grafica_cross_apilada(df: pd.DataFrame, col_x: str, col_color: str,
                          orden_x: list = None) -> go.Figure:
    """Barras apiladas: col_x vs col_color (frecuencia absoluta)."""
    if col_x not in df.columns or col_color not in df.columns:
        return go.Figure()
    tabla = pd.crosstab(df[col_x], df[col_color])
    if orden_x:
        tabla = tabla.reindex([i for i in orden_x if i in tabla.index])

    paleta = [CORP_NAVY, CORP_NAVY_2, CORP_NAVY_3, CORP_NAVY_4, CORP_GOLD, CORP_GRAY]
    fig = go.Figure()
    for i, col in enumerate(tabla.columns):
        fig.add_trace(go.Bar(
            x=tabla.index, y=tabla[col].values,
            name=str(col),
            marker=dict(color=paleta[i % len(paleta)], line=dict(width=0)),
            hovertemplate=f"<b>{col}</b><br>%{{x}}: <b>%{{y}}</b><extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title=""),
        yaxis=dict(title="Casos"),
        bargap=0.25,
    )
    fig = _estilo_corporativo(fig, height=340, show_legend=True)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.18,
                                   xanchor="left", x=0))
    return fig


def grafica_frecuencia_uso_pareada(df: pd.DataFrame) -> go.Figure:
    """Compara frecuencia_efectivo vs frecuencia_digital (barras agrupadas por nivel)."""
    if "frecuencia_efectivo" not in df.columns or "frecuencia_digital" not in df.columns:
        return go.Figure()

    # Orden canonico de niveles si son ordinales (Nunca, Rara vez, A veces, Frecuente, Siempre)
    orden_pref = ["Nunca", "Rara vez", "A veces", "Frecuente", "Siempre",
                  "Diario", "Semanal", "Mensual"]
    niveles_e = df["frecuencia_efectivo"].dropna().astype(str).unique().tolist()
    niveles_d = df["frecuencia_digital"].dropna().astype(str).unique().tolist()
    todos = list(dict.fromkeys(niveles_e + niveles_d))
    todos.sort(key=lambda x: orden_pref.index(x) if x in orden_pref else 999)

    cnt_e = df["frecuencia_efectivo"].astype(str).value_counts().reindex(todos, fill_value=0)
    cnt_d = df["frecuencia_digital"].astype(str).value_counts().reindex(todos, fill_value=0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=todos, y=cnt_e.values, name="Efectivo",
        marker=dict(color=CORP_NAVY, line=dict(width=0)),
        text=cnt_e.values, textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color=CORP_NAVY),
        hovertemplate="<b>Efectivo</b> · %{x}<br>Casos: <b>%{y}</b><extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=todos, y=cnt_d.values, name="Digital",
        marker=dict(color=CORP_NAVY_3, line=dict(width=0)),
        text=cnt_d.values, textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color=CORP_NAVY_2),
        hovertemplate="<b>Digital</b> · %{x}<br>Casos: <b>%{y}</b><extra></extra>",
    ))
    fig.update_layout(
        barmode="group",
        xaxis=dict(title="Frecuencia de uso"),
        yaxis=dict(title="Consumidores"),
        bargap=0.25, bargroupgap=0.1,
    )
    fig = _estilo_corporativo(fig, height=320, show_legend=True)
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.18,
                                   xanchor="left", x=0))
    return fig


def grafica_resumen_kpis(df: pd.DataFrame) -> dict:
    """Retorna diccionario con KPIs calculados para el dashboard."""
    efectivo = df[df["metodo_pago_preferido"] == "Efectivo"]
    digital = df[df["metodo_pago_preferido"] != "Efectivo"]

    return {
        "total_encuestados": len(df),
        "pct_efectivo": round(len(efectivo) / len(df) * 100, 1),
        "pct_digital": round(len(digital) / len(df) * 100, 1),
        "pct_billetera": round(df["uso_billetera_digital"].mean() * 100, 1),
        "gasto_promedio": round(df["gasto_semanal"].mean(), 2),
        "confianza_promedio": round(df["confianza_digital"].mean(), 1),
    }
