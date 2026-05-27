"""Dashboard principal — resumen general del sistema."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario

def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_id, obtener_user_email, es_modo_publico
    requerir_autenticacion(permitir_publico=True)
    sidebar_usuario("Dashboard")

    _es_publico = es_modo_publico()
    user_id    = obtener_user_id()
    user_email = obtener_user_email()
    if _es_publico:
        nombre = "Visitante"
    else:
        nombre = user_email.split("@")[0].capitalize() if user_email else "Usuario"

    # ── Header ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-layout-dashboard"></i> Dashboard
        </span>
        <h1>{'Vista pública' if _es_publico else f'Bienvenido, {nombre}'}</h1>
        <p>Sistema de análisis estadístico de hábitos de pago · Cobán, Alta Verapaz</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Dataset ───────────────────────────────────────────────
    df = st.session_state.get("df_encuestas")
    if df is None or df.empty:
        try:
            if _es_publico:
                from modules.db import obtener_encuestas_publico
                df = obtener_encuestas_publico()
            else:
                from modules.db import obtener_encuestas
                df = obtener_encuestas(user_id)
            if not df.empty:
                st.session_state["df_encuestas"] = df
        except Exception:
            df = pd.DataFrame()

    # ── KPIs ──────────────────────────────────────────────────
    st.markdown(
        '<p class="section-title"><i class="ti ti-trending-up"></i> Indicadores actuales</p>',
        unsafe_allow_html=True,
    )

    if not df.empty:
        from modules.graficas import grafica_resumen_kpis
        k = grafica_resumen_kpis(df)
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "navy",  "ti-users",         "Total encuestados",    str(k["total_encuestados"]),  "registros en base de datos", "fade-in"),
            (c2, "gold",  "ti-device-mobile",  "Billetera digital",   f"{k['pct_billetera']}%",     "adopción en la muestra",     "fade-in-1"),
            (c3, "green", "ti-coin",           "Gasto semanal prom.", f"Q{k['gasto_promedio']}",    "promedio general",           "fade-in-2"),
            (c4, "blue",  "ti-star",           "Confianza digital",   f"{k['confianza_promedio']}",  "promedio escala /5",        "fade-in-3"),
        ]
        for col, variante, icon, label, value, sub, anim in cards:
            with col:
                st.markdown(f"""
                <div class="stat-card {variante} {anim}">
                    <div class="stat-icon {variante}"><i class="ti {icon}"></i></div>
                    <div class="s-label">{label}</div>
                    <div class="s-value">{value}</div>
                    <div class="s-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box fade-in">
            <i class="ti ti-info-circle"></i>
            <strong> Sin datos cargados.</strong> Ve a
            <em>Cargar Datos</em> para subir el archivo CSV o Excel.
        </div>""", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, icon, label in [
            (c1,"ti-users","Encuestados"),
            (c2,"ti-device-mobile","Billetera digital"),
            (c3,"ti-coin","Gasto promedio"),
            (c4,"ti-star","Confianza"),
        ]:
            with col:
                st.markdown(f"""
                <div class="stat-card fade-in">
                    <div class="stat-icon navy"><i class="ti {icon}"></i></div>
                    <div class="s-label">{label}</div>
                    <div class="s-value" style="color:var(--text-400)">—</div>
                    <div class="s-sub">sin datos</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Distribución geográfica ───────────────────────────────
    geo = st.session_state.get("geo_exclusion")
    # En modo visitante geo_exclusion no se carga — mostrar nota estática si el df tiene 41 registros
    if not geo and not df.empty and len(df) == 41:
        st.markdown("""
        <div class="decision-card bajo fade-in" style="border-left:4px solid #1565C0; margin-bottom:1rem">
            <div class="d-label" style="color:#1565C0">
                <i class="ti ti-info-circle"></i> Nota metodológica
            </div>
            <p>
                De las <strong>53</strong> encuestas recolectadas,
                <strong>41</strong> corresponden a residentes de
                <strong>Cobán, Alta Verapaz</strong> y forman la muestra de análisis.
                Las <strong>12</strong> respuestas de otros municipios
                no se incluyen en las pruebas estadísticas ni en las conclusiones del estudio.
            </p>
        </div>""", unsafe_allow_html=True)
    if geo and geo.get("excluidos", 0) > 0:
        st.markdown(
            '<p class="section-title"><i class="ti ti-map-pin"></i> Cobertura geográfica de la muestra</p>',
            unsafe_allow_html=True,
        )
        import plotly.graph_objects as go
        col_geo1, col_geo2 = st.columns([1, 2])
        with col_geo1:
            fig_geo = go.Figure(go.Pie(
                labels=["Cobán, A.V. (incluidos)", "Otros municipios (excluidos)"],
                values=[geo["incluidos"], geo["excluidos"]],
                hole=0.55,
                marker_colors=["#1A237E", "#E0E0E0"],
                textinfo="percent+value",
                hovertemplate="%{label}<br>%{value} encuestas (%{percent})<extra></extra>",
            ))
            fig_geo.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                height=280,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", size=12),
            )
            st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})
        with col_geo2:
            st.markdown(f"""
            <div class="decision-card bajo fade-in" style="border-left:4px solid #1565C0; margin-top:.5rem">
                <div class="d-label" style="color:#1565C0">
                    <i class="ti ti-info-circle"></i> Nota metodológica
                </div>
                <p>
                    De las <strong>{geo['total_original']}</strong> encuestas recolectadas,
                    <strong>{geo['incluidos']}</strong> corresponden a residentes de
                    <strong>Cobán, Alta Verapaz</strong> y forman la muestra de análisis.
                    Las <strong>{geo['excluidos']}</strong> respuestas de otros municipios
                    se muestran aquí para transparencia pero <em>no se incluyen</em> en
                    las pruebas estadísticas ni en las conclusiones del estudio.
                </p>
            </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Gráficas ──────────────────────────────────────────────
    if not df.empty:
        st.markdown(
            '<p class="section-title"><i class="ti ti-chart-bar"></i> Vista general</p>',
            unsafe_allow_html=True,
        )
        from modules.graficas import (
            grafica_distribucion_metodos_pago,
            grafica_distribucion_grupos_etarios,
            grafica_uso_billetera_digital,
            grafica_barras_categoria,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(grafica_distribucion_metodos_pago(df),
                            use_container_width=True, config={"displayModeBar": False})
        with col_b:
            st.plotly_chart(grafica_distribucion_grupos_etarios(df),
                            use_container_width=True, config={"displayModeBar": False})

        col_c, col_d = st.columns([1.4, 1])
        with col_c:
            if "tipo_comercio" in df.columns:
                st.markdown(
                    '<p class="section-title" style="margin-top:.5rem"><i class="ti ti-building-store"></i> Tipos de comercio frecuentados</p>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(
                    grafica_barras_categoria(df, "tipo_comercio", horizontal=True),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
        with col_d:
            st.markdown(
                '<p class="section-title" style="margin-top:.5rem"><i class="ti ti-wallet"></i> Billetera digital</p>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafica_uso_billetera_digital(df),
                            use_container_width=True, config={"displayModeBar": False})

    # ── Accesos rápidos (solo usuarios autenticados) ──────────
    if not _es_publico:
        st.markdown(
            '<p class="section-title"><i class="ti ti-bolt"></i> Accesos rápidos</p>',
            unsafe_allow_html=True,
        )
        ca, cb, cc = st.columns(3)

        def quick_card(col, icon, titulo, desc, page):
            with col:
                st.markdown(f"""
                <div class="nav-card fade-in">
                    <div class="nc-icon"><i class="ti {icon}"></i></div>
                    <div class="nc-title">{titulo}</div>
                    <div class="nc-desc">{desc}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"Ir a {titulo}", key=f"qk_{page}", use_container_width=True):
                    st.switch_page(f"pages/{page}")

        quick_card(ca, "ti-cloud-upload",  "Cargar Datos",  "Sube CSV o Excel con las encuestas",      "2_Cargar_Datos.py")
        quick_card(cb, "ti-flask",         "Nuevo Análisis","Ejecuta las 3 pruebas estadísticas",       "3_Nuevo_Analisis.py")
        quick_card(cc, "ti-file-invoice",  "Exportar PDF",  "Genera el reporte completo descargable",   "6_Exportar.py")

    # ── Acceso directo a resultados (visitantes) ──────────────
    if _es_publico:
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        if st.button("Ver resultados estadísticos completos →",
                     use_container_width=True, type="primary"):
            st.switch_page("pages/4_Resultados.py")

    # ── Último análisis ───────────────────────────────────────
    ultimo = st.session_state.get("ultimo_analisis")
    if ultimo:
        st.markdown(
            '<p class="section-title"><i class="ti ti-clock-hour-4"></i> Último análisis</p>',
            unsafe_allow_html=True,
        )
        st.markdown(f"""
        <div class="hist-row fade-in">
            <div>
                <div class="h-name">{ultimo.get('nombre','Sin nombre')}</div>
                <div class="h-meta">
                    <i class="ti ti-database" style="font-size:.85rem"></i>
                    {ultimo.get('total_registros',0)} registros ·
                    α = {ultimo.get('alpha',0.05)}
                </div>
            </div>
            <span class="badge badge-navy">
                <i class="ti ti-clock"></i> Reciente
            </span>
        </div>""", unsafe_allow_html=True)

main()
