"""Pagina de resultados: visualizacion completa de pruebas y decisiones empresariales."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Resultados — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario


_SQL_PUBLICO = """-- Ejecuta esto en Supabase Dashboard → SQL Editor → New Query
CREATE POLICY "publico_lee_analisis"
  ON analisis FOR SELECT TO anon USING (true);

CREATE POLICY "publico_lee_resultados_pruebas"
  ON resultados_pruebas FOR SELECT TO anon USING (true);

CREATE POLICY "publico_lee_decisiones_generadas"
  ON decisiones_generadas FOR SELECT TO anon USING (true);

CREATE POLICY "publico_lee_encuestas"
  ON encuestas FOR SELECT TO anon USING (true);"""


def _mostrar_instrucciones_sql():
    with st.expander("Activar acceso público · instrucciones para administrador", expanded=True):
        st.markdown("""
        **Para habilitar la vista de resultados públicos**, el administrador debe ejecutar
        las siguientes políticas SQL una sola vez en Supabase:

        1. Abre **Supabase Dashboard** → tu proyecto
        2. Ve a **SQL Editor** → **New Query**
        3. Pega y ejecuta el siguiente SQL:
        """)
        st.code(_SQL_PUBLICO, language="sql")
        st.caption("Estas políticas permiten solo lectura (SELECT) a usuarios anónimos. No afectan escritura ni seguridad de otras operaciones.")


def _mostrar_tarjeta_prueba(clave: str, resultado, nombre: str, df: pd.DataFrame):
    from modules.pruebas import ResultadoPrueba
    if not isinstance(resultado, ResultadoPrueba):
        st.markdown(f"""
        <div class="decision-card medio">
            <div class="d-label"><i class="ti ti-alert-triangle"></i> {nombre} — Error</div>
            <p>{resultado}</p>
        </div>""", unsafe_allow_html=True)
        return

    clase = "rechaza" if resultado.rechaza_h0 else "no-rechaza"
    icon_color = "#E53935" if resultado.rechaza_h0 else "#2E7D32"
    icon_name = "ti-circle-x" if resultado.rechaza_h0 else "ti-circle-check"
    decision_txt = "Se RECHAZA H₀" if resultado.rechaza_h0 else "NO se rechaza H₀"
    badge_clase = "badge-danger" if resultado.rechaza_h0 else "badge-success"

    st.markdown(f"""
    <div class="result-card {clase}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.85rem">
            <div class="test-name">
                <i class="ti {icon_name}" style="color:{icon_color}"></i> {nombre}
            </div>
            <span class="badge {badge_clase}">{decision_txt}</span>
        </div>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="slabel">Estadístico</div>
                <div class="svalue">{resultado.estadistico:.4f}</div>
            </div>
            <div class="stat-item">
                <div class="slabel">p-valor</div>
                <div class="svalue">{resultado.p_valor:.6f}</div>
            </div>
            <div class="stat-item">
                <div class="slabel">Grados lib.</div>
                <div class="svalue">{resultado.grados_libertad if resultado.grados_libertad is not None else 'N/A'}</div>
            </div>
        </div>
        <div style="font-size:.82rem;color:var(--text-400);font-family:var(--font-mono)">
            α = {resultado.alpha} &nbsp;·&nbsp;
            {'p &lt; α → rechaza H₀' if resultado.rechaza_h0 else 'p ≥ α → no rechaza H₀'}
        </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("Ver detalles estadísticos"):
        detalles = resultado.detalles
        if clave == "t_student":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("n efectivo", detalles.get("n_efectivo", "—"))
                st.metric("Media efectivo", f"Q{detalles.get('media_efectivo', 0):.2f}")
                st.metric("Desv. efectivo", f"Q{detalles.get('desv_efectivo', 0):.2f}")
            with col2:
                st.metric("n digital", detalles.get("n_digital", "—"))
                st.metric("Media digital", f"Q{detalles.get('media_digital', 0):.2f}")
                st.metric("Desv. digital", f"Q{detalles.get('desv_digital', 0):.2f}")
            with col3:
                st.metric("Tipo de t", detalles.get("tipo_t", "—"))
                st.metric("Levene p", f"{detalles.get('levene_p', 0):.4f}")
                st.metric("Varianzas iguales", "Sí" if detalles.get("varianzas_iguales") else "No")

        elif clave == "chi_cuadrado":
            st.metric("V de Cramer", detalles.get("v_cramer", "—"))
            st.metric("Interpretación", detalles.get("interpretacion_v_cramer", "—"))
            st.metric("% celdas con frec. baja", f"{detalles.get('porcentaje_celdas_bajas', 0)}%")
            st.metric("Supuesto cumplido", "Sí" if detalles.get("supuesto_cumplido") else "No")

        elif clave == "z_proporcion":
            col1, col2 = st.columns(2)
            with col1:
                st.metric("p muestral", f"{detalles.get('p_muestral', 0)*100:.1f}%")
                st.metric("p₀ hipotético", f"{detalles.get('p0_hipotetico', 0.40)*100:.0f}%")
                st.metric("Z crítico", f"{detalles.get('z_critico', 0):.4f}")
            with col2:
                ic = detalles.get("intervalo_confianza_95", [0, 0])
                st.metric("IC 95%", f"[{ic[0]*100:.1f}%, {ic[1]*100:.1f}%]")
                st.metric("n total", detalles.get("n_total", "—"))
                st.metric("Supuesto normal", "Sí" if detalles.get("supuesto_normal_cumplido") else "No")

        st.json(detalles, expanded=False)


def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_id, es_modo_publico
    requerir_autenticacion(permitir_publico=True)
    sidebar_usuario("Resultados")
    _es_publico = es_modo_publico()

    st.markdown("""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-chart-dots-3"></i> Resultados
        </span>
        <h1>Resultados del análisis estadístico</h1>
        <p>Pruebas inferenciales · Visualizaciones · Decisiones empresariales automáticas</p>
    </div>
    """, unsafe_allow_html=True)

    resultados = st.session_state.get("resultados_pruebas")
    decisiones = st.session_state.get("decisiones", [])
    df = st.session_state.get("df_encuestas", pd.DataFrame())
    analisis_info = st.session_state.get("ultimo_analisis", {})

    if not resultados:
        if _es_publico:
            with st.spinner("Cargando últimos resultados publicados…"):
                try:
                    from modules.db import obtener_ultimo_analisis_publico
                    datos = obtener_ultimo_analisis_publico()
                except Exception as e:
                    datos = {"error": str(e)}

            if datos.get("error"):
                st.markdown(f"""
                <div class="decision-card medio fade-in">
                    <div class="d-label"><i class="ti ti-alert-triangle"></i> Error al cargar datos</div>
                    <p>{datos['error']}</p>
                </div>""", unsafe_allow_html=True)
                _mostrar_instrucciones_sql()
                return
            elif not datos or not datos.get("resultados"):
                st.markdown("""
                <div class="decision-card medio fade-in">
                    <div class="d-label"><i class="ti ti-database-off"></i> Sin acceso público a datos</div>
                    <p>Las políticas de lectura pública no están activas en Supabase, o no hay
                    análisis guardados aún.</p>
                </div>""", unsafe_allow_html=True)
                _mostrar_instrucciones_sql()
                return
            else:
                # Populate session state and continue rendering
                resultados = datos["resultados"]
                decisiones = datos["decisiones"]
                df = datos["df_encuestas"]
                a = datos["analisis"]
                analisis_info = {
                    "nombre":          a.get("nombre", "Análisis publicado"),
                    "total_registros": a.get("total_registros", 0),
                    "alpha":           float(a.get("alpha", 0.05)),
                    "descripcion":     a.get("descripcion", ""),
                }
        else:
            st.markdown("""
            <div class="decision-card medio fade-in">
                <div class="d-label"><i class="ti ti-alert-triangle"></i> Sin análisis ejecutado</div>
                <p>No hay resultados en sesión. Ejecuta un nuevo análisis primero.</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Ir a Nuevo Análisis"):
                st.switch_page("pages/3_Nuevo_Analisis.py")
            return

    if analisis_info:
        st.markdown(f"""
        <div class="info-box fade-in">
            <i class="ti ti-info-circle"></i>
            <strong> {analisis_info.get('nombre','Análisis')}</strong> ·
            {analisis_info.get('total_registros', '?')} registros ·
            α = {analisis_info.get('alpha', 0.05)} ·
            <span style="color:var(--text-400)">{analisis_info.get('descripcion','')[:120]}</span>
        </div>""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "Pruebas estadísticas",
        "Visualizaciones",
        "Decisiones empresariales",
    ])

    nombres_pruebas = {
        "t_student": "Prueba t de Student",
        "chi_cuadrado": "Prueba Chi-cuadrado",
        "z_proporcion": "Prueba Z para Proporción",
    }

    with tab1:
        st.markdown(
            '<p class="section-title"><i class="ti ti-test-pipe"></i> Resultados por prueba</p>',
            unsafe_allow_html=True,
        )
        for clave, nombre in nombres_pruebas.items():
            if clave in resultados:
                _mostrar_tarjeta_prueba(clave, resultados[clave], nombre, df)

    with tab2:
        if df.empty:
            st.markdown("""
            <div class="info-box">
                <i class="ti ti-info-circle"></i>
                Carga el dataset para ver las visualizaciones.
            </div>""", unsafe_allow_html=True)
        else:
            from modules.graficas import (
                grafica_gasto_semanal_boxplot,
                grafica_barras_apiladas_100,
                grafica_z_proporcion,
                grafica_gasto_por_grupo_etario,
                grafica_ingreso_vs_metodo,
                grafica_confianza_digital,
                grafica_tabla_frecuencias,
                grafica_dispersion,
                tabla_frecuencias,
                grafica_resumen_kpis,
                grafica_barras_categoria,
                grafica_donut,
                grafica_cross_apilada,
                grafica_frecuencia_uso_pareada,
            )
            from modules.pruebas import ResultadoPrueba
            from datetime import datetime

            plotly_cfg = {
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
                "toImageButtonOptions": {"format": "png", "scale": 2},
            }

            kpis = grafica_resumen_kpis(df)
            alpha = analisis_info.get("alpha", 0.05)
            n_sig = sum(1 for r in resultados.values()
                        if isinstance(r, ResultadoPrueba) and r.rechaza_h0)
            n_tests = sum(1 for r in resultados.values() if isinstance(r, ResultadoPrueba))

            # ── FILTROS BAR ───────────────────────────────────────
            ts = datetime.now().strftime("%d %b %Y · %H:%M")
            st.markdown(f"""
            <div class="dash-filters">
              <span class="df-label">Cohorte</span>
              <span class="df-chip accent"><i class="ti ti-database"></i>
                <b>{kpis['total_encuestados']}</b> registros</span>
              <span class="df-chip"><i class="ti ti-map-pin"></i> Cobán, A.V.</span>
              <span class="df-chip"><i class="ti ti-percentage"></i> α = <b>{alpha}</b></span>
              <span class="df-chip"><i class="ti ti-flask"></i> <b>{n_sig}/{n_tests}</b> pruebas significativas</span>
              <span class="df-chip" style="margin-left:auto;font-family:var(--font-mono);font-size:.72rem">
                <i class="ti ti-clock"></i> {ts}
              </span>
            </div>
            """, unsafe_allow_html=True)

            # ── KPI STRIP ─────────────────────────────────────────
            def _tile(label, value, unit, foot, klass="", icon="ti-chart-line"):
                return (
                    f'<div class="kpi-tile {klass}">'
                    f'  <div class="kpi-label"><i class="ti {icon}"></i>{label}</div>'
                    f'  <div class="kpi-value">{value}<span class="unit">{unit}</span></div>'
                    f'  <div class="kpi-foot">{foot}</div>'
                    f'</div>'
                )

            pct_dig = kpis["pct_digital"]
            pct_dig_delta = pct_dig - 50
            delta_class = "up" if pct_dig_delta > 0 else ("down" if pct_dig_delta < 0 else "flat")
            delta_arrow = "▲" if pct_dig_delta > 0 else ("▼" if pct_dig_delta < 0 else "—")

            kpi_html = '<div class="kpi-strip">'
            kpi_html += _tile("Encuestados", f"{kpis['total_encuestados']}", "",
                              "muestra total", icon="ti-users")
            kpi_html += _tile("Gasto medio", f"{kpis['gasto_promedio']:.0f}", "Q",
                              "promedio semanal", icon="ti-coin")
            kpi_html += _tile("Pago digital", f"{pct_dig:.1f}", "%",
                              f"<span class='kpi-delta {delta_class}'>{delta_arrow} {abs(pct_dig_delta):.1f} pp vs 50%</span>",
                              klass="pos" if pct_dig_delta > 0 else "neg",
                              icon="ti-device-mobile")
            kpi_html += _tile("Billetera", f"{kpis['pct_billetera']:.1f}", "%",
                              "adopción", icon="ti-wallet")
            kpi_html += _tile("Confianza", f"{kpis['confianza_promedio']:.1f}", "/5",
                              "índice 1–5", icon="ti-shield-check")
            kpi_html += _tile("Decisión", f"{n_sig}", f"/{n_tests}",
                              "tests rechazan H₀",
                              klass="warn" if n_sig > 0 else "",
                              icon="ti-target")
            kpi_html += '</div>'
            st.markdown(kpi_html, unsafe_allow_html=True)

            # ── Helper bento card ─────────────────────────────────
            def _card_open(title, icon, badge_text=None, badge_class="test"):
                badge = (f'<span class="dc-badge {badge_class}">{badge_text}</span>'
                         if badge_text else "")
                st.markdown(f"""
                <div class="dash-card">
                  <div class="dash-card-head">
                    <div class="dc-title"><i class="ti {icon}"></i>{title}</div>
                    {badge}
                  </div>
                  <div class="dash-card-body">
                """, unsafe_allow_html=True)

            def _card_close(foot_html: str = ""):
                if foot_html:
                    st.markdown(f'</div><div class="dash-card-foot">{foot_html}</div></div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown('</div></div>', unsafe_allow_html=True)

            def _section(tag, title, meta=""):
                st.markdown(f"""
                <div class="dash-section-head">
                  <div class="sh-left">
                    <span class="sh-tag">{tag}</span>
                    <h2>{title}</h2>
                  </div>
                  <div class="sh-meta">{meta}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── SECCIÓN 1 · Comparación de medias (t-Student) ────
            res_t = resultados.get("t_student")
            t_badge = ""
            t_meta = ""
            if isinstance(res_t, ResultadoPrueba):
                t_badge = ("RECHAZA H₀", "sig") if res_t.rechaza_h0 else ("NO RECHAZA", "ok")
                t_meta = f"t = {res_t.estadistico:+.3f} · p = {res_t.p_valor:.4f}"
            _section("01", "Diferencia de medias · gasto semanal",
                     f"{t_meta}" if t_meta else "")

            col_a, col_b = st.columns(2)
            with col_a:
                _card_open("Distribución por método",
                           "ti-box-multiple",
                           t_badge[0] if t_badge else None,
                           t_badge[1] if t_badge else "test")
                st.plotly_chart(grafica_gasto_semanal_boxplot(df),
                                use_container_width=True, config=plotly_cfg)
                _card_close(
                    '<span class="dcf-stat">Test · <b>t de Student</b></span>'
                    f'<span class="dcf-stat">μ efectivo vs μ digital</span>'
                )
            with col_b:
                _card_open("Gasto medio por grupo etario", "ti-chart-bar")
                st.plotly_chart(grafica_gasto_por_grupo_etario(df),
                                use_container_width=True, config=plotly_cfg)
                _card_close('<span class="dcf-stat">Barras de error: <b>±1 SD</b></span>')

            # ── SECCIÓN 2 · Asociación (Chi²) ────────────────────
            res_chi = resultados.get("chi_cuadrado")
            chi_badge = ""
            chi_meta = ""
            if isinstance(res_chi, ResultadoPrueba):
                chi_badge = ("ASOCIADO", "sig") if res_chi.rechaza_h0 else ("INDEPENDIENTE", "ok")
                v_cramer = res_chi.detalles.get("v_cramer", 0)
                chi_meta = f"χ² = {res_chi.estadistico:.3f} · p = {res_chi.p_valor:.4f} · V = {v_cramer}"
            _section("02", "Asociación entre variables categóricas", chi_meta)

            if isinstance(res_chi, ResultadoPrueba):
                _card_open("Perfil por grupo etario · barras 100% apiladas",
                           "ti-chart-bar",
                           chi_badge[0] if chi_badge else None,
                           chi_badge[1] if chi_badge else "test")
                st.plotly_chart(grafica_barras_apiladas_100(res_chi.detalles),
                                use_container_width=True, config=plotly_cfg)
                _card_close(
                    '<span class="dcf-stat">Lectura: <b>% de cada grupo</b> por método</span>'
                    '<span class="dcf-stat">Patrones iguales → independencia · distintos → asociación</span>'
                )

            # ── SECCIÓN 3 · Test de proporción (Z) ───────────────
            res_z = resultados.get("z_proporcion")
            z_badge = ""
            z_meta = ""
            if isinstance(res_z, ResultadoPrueba):
                z_badge = ("RECHAZA H₀", "sig") if res_z.rechaza_h0 else ("NO RECHAZA", "ok")
                p_mu = res_z.detalles.get("p_muestral", 0)
                p0 = res_z.detalles.get("p0_hipotetico", 0.40)
                z_meta = f"Z = {res_z.estadistico:+.3f} · p̂ = {p_mu*100:.1f}% · p₀ = {p0*100:.0f}%"
            _section("03", "Proporción de adopción digital", z_meta)

            col_z1, col_z2 = st.columns([1.4, 1])
            with col_z1:
                if isinstance(res_z, ResultadoPrueba):
                    _card_open("Distribución Z · zona de rechazo",
                               "ti-wave-sine",
                               z_badge[0] if z_badge else None,
                               z_badge[1] if z_badge else "test")
                    st.plotly_chart(grafica_z_proporcion(res_z.a_dict()),
                                    use_container_width=True, config=plotly_cfg)
                    _card_close(
                        f'<span class="dcf-stat">α = <b>{alpha}</b> (una cola)</span>'
                        f'<span class="dcf-stat">IC 95% disponible en detalles</span>'
                    )
            with col_z2:
                _card_open("Confianza en pagos digitales", "ti-shield-check")
                st.plotly_chart(grafica_confianza_digital(df),
                                use_container_width=True, config=plotly_cfg)
                _card_close(
                    f'<span class="dcf-stat">Media · <b>{kpis["confianza_promedio"]:.2f} / 5</b></span>'
                )

            # ── SECCIÓN 4 · Cross-cuts ───────────────────────────
            _section("04", "Análisis de dispersión y segmentación",
                     "edad × gasto · ingreso × método")

            _card_open("Edad vs gasto semanal", "ti-scatter-plot")
            st.plotly_chart(grafica_dispersion(df),
                            use_container_width=True, config=plotly_cfg)
            _card_close(
                '<span class="dcf-stat">Burbuja · <b>confianza digital</b></span>'
                '<span class="dcf-stat">Color · método de pago</span>'
            )

            _card_open("Ingreso mensual × método (apilado)", "ti-chart-histogram")
            st.plotly_chart(grafica_ingreso_vs_metodo(df),
                            use_container_width=True, config=plotly_cfg)
            _card_close(
                '<span class="dcf-stat">Distribución por rango de ingreso</span>'
            )

            # ── SECCIÓN 5 · Tablas de frecuencia ─────────────────
            _section("05", "Tablas de frecuencia", "fᵢ · hᵢ · Fᵢ · Hᵢ")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                _card_open("Método de pago preferido", "ti-list-numbers")
                st.plotly_chart(
                    grafica_tabla_frecuencias(df, "metodo_pago_preferido",
                                              "Método de Pago"),
                    use_container_width=True, config={"displayModeBar": False},
                )
                _card_close()
            with col_f2:
                _card_open("Grupo etario", "ti-users")
                st.plotly_chart(
                    grafica_tabla_frecuencias(df, "grupo_etario",
                                              "Grupo Etario"),
                    use_container_width=True, config={"displayModeBar": False},
                )
                _card_close()

            # ── SECCIÓN 6 · Segmentos adicionales ────────────────
            _section("06", "Segmentos adicionales · variables del perfil",
                     "tipo de comercio · razón · frecuencia · demografía")

            # 6.1 Tipo de comercio + razón método
            col_x, col_y = st.columns(2)
            with col_x:
                if "tipo_comercio" in df.columns:
                    _card_open("¿Dónde paga el consumidor?", "ti-building-store")
                    st.plotly_chart(
                        grafica_barras_categoria(df, "tipo_comercio", horizontal=True),
                        use_container_width=True, config=plotly_cfg,
                    )
                    _card_close(
                        f'<span class="dcf-stat">Tipos únicos · <b>{df["tipo_comercio"].nunique()}</b></span>'
                        '<span class="dcf-stat">Etiqueta · <b>casos · %</b></span>'
                    )
            with col_y:
                if "razon_metodo" in df.columns:
                    _card_open("¿Por qué prefiere ese método?", "ti-bulb")
                    st.plotly_chart(
                        grafica_barras_categoria(df, "razon_metodo", horizontal=True),
                        use_container_width=True, config=plotly_cfg,
                    )
                    _card_close(
                        f'<span class="dcf-stat">Razones únicas · <b>{df["razon_metodo"].nunique()}</b></span>'
                        '<span class="dcf-stat">Top: motivo más frecuente</span>'
                    )

            # 6.2 Cruces de tipo_comercio por método de pago
            if "tipo_comercio" in df.columns and "metodo_pago_preferido" in df.columns:
                _card_open("Método de pago por tipo de comercio (apilado)",
                           "ti-chart-bar-popular")
                st.plotly_chart(
                    grafica_cross_apilada(df, "tipo_comercio", "metodo_pago_preferido"),
                    use_container_width=True, config=plotly_cfg,
                )
                _card_close(
                    '<span class="dcf-stat">Lectura · qué se paga en cada comercio</span>'
                    '<span class="dcf-stat">Hover · casos absolutos</span>'
                )

            # 6.3 Frecuencia de uso efectivo vs digital
            if "frecuencia_efectivo" in df.columns and "frecuencia_digital" in df.columns:
                _card_open("Frecuencia de uso · efectivo vs digital",
                           "ti-clock-bolt")
                st.plotly_chart(
                    grafica_frecuencia_uso_pareada(df),
                    use_container_width=True, config=plotly_cfg,
                )
                _card_close(
                    '<span class="dcf-stat">Barras agrupadas · comparación directa por nivel</span>'
                )

            # 6.4 Demografía: género + ocupación
            cols_demo = st.columns(2)
            with cols_demo[0]:
                if "genero" in df.columns:
                    _card_open("Distribución por género", "ti-users-group")
                    st.plotly_chart(
                        grafica_donut(df, "genero"),
                        use_container_width=True, config={"displayModeBar": False},
                    )
                    _card_close()
            with cols_demo[1]:
                if "ocupacion" in df.columns:
                    _card_open("Ocupación de los encuestados", "ti-briefcase-2")
                    st.plotly_chart(
                        grafica_barras_categoria(df, "ocupacion", horizontal=True, top_n=10),
                        use_container_width=True, config=plotly_cfg,
                    )
                    _card_close(
                        f'<span class="dcf-stat">Categorías · <b>{df["ocupacion"].nunique()}</b></span>'
                        '<span class="dcf-stat">Top 10 mostrados</span>'
                    )

            with st.expander("📋 Datos crudos · descarga CSV"):
                tab_mp = tabla_frecuencias(df, "metodo_pago_preferido")
                st.dataframe(tab_mp, use_container_width=True, hide_index=True)
                st.download_button(
                    "Descargar tabla método de pago (CSV)",
                    data=tab_mp.to_csv(index=False).encode("utf-8"),
                    file_name="frecuencias_metodo_pago.csv",
                    mime="text/csv",
                )

            # ── Footer / source ──────────────────────────────────
            st.markdown(f"""
            <div class="dash-source">
              <span><i class="ti ti-database"></i> Fuente: Supabase · tabla <code>encuestas</code></span>
              <span>Estadística II · UMG Cobán · α = {alpha}</span>
              <span>Generado · {ts}</span>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        if decisiones:
            st.markdown(
                '<p class="section-title"><i class="ti ti-briefcase"></i> Conclusiones y recomendaciones empresariales</p>',
                unsafe_allow_html=True,
            )
            nivel_icons = {
                "alto": ("ti-alert-octagon", "#E53935"),
                "medio": ("ti-alert-triangle", "#F59E0B"),
                "bajo": ("ti-circle-check", "#2E7D32"),
            }
            for dec in decisiones:
                nivel = dec.get("nivel_alerta", "bajo")
                icon_n, icon_c = nivel_icons.get(nivel, ("ti-info-circle", "#666"))
                st.markdown(f"""
                <div class="decision-card {nivel} fade-in">
                    <div class="d-label">
                        <i class="ti {icon_n}" style="color:{icon_c}"></i>
                        {dec.get('prueba','')} — Alerta: {nivel.upper()}
                    </div>
                    <p><strong>Decisión:</strong> {dec.get('decision','')}</p>
                    <p><strong>Conclusión:</strong> {dec.get('conclusion','')}</p>
                    <p><strong>Recomendación:</strong> {dec.get('recomendacion','')}</p>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <i class="ti ti-info-circle"></i>
                No hay decisiones generadas. Ejecuta el análisis nuevamente.
            </div>""", unsafe_allow_html=True)

        col_x, col_y = st.columns(2)
        with col_x:
            if not _es_publico:
                if st.button("Nuevo análisis", use_container_width=True):
                    st.switch_page("pages/3_Nuevo_Analisis.py")
        with col_y:
            if not _es_publico:
                if st.button("Exportar reporte PDF", use_container_width=True):
                    st.switch_page("pages/6_Exportar.py")


main()
