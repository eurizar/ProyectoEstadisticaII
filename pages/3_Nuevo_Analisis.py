"""Pagina de nuevo analisis: configurar y ejecutar las 3 pruebas estadisticas."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Nuevo Análisis — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario


def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_id
    requerir_autenticacion()
    sidebar_usuario("Nuevo_Analisis")
    user_id = obtener_user_id()

    st.markdown("""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-flask"></i> Nuevo Análisis
        </span>
        <h1>Ejecutar pruebas estadísticas</h1>
        <p>t de Student · Chi-cuadrado · Z para proporción — con α configurable</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Cargar dataset ─────────────────────────────────────────
    df = st.session_state.get("df_encuestas")
    if df is None or df.empty:
        try:
            from modules.db import obtener_encuestas
            df = obtener_encuestas(user_id)
            if not df.empty:
                st.session_state["df_encuestas"] = df
        except Exception:
            df = pd.DataFrame()

    if df is None or df.empty:
        st.markdown("""
        <div class="decision-card medio fade-in">
            <div class="d-label"><i class="ti ti-alert-triangle"></i> Sin datos</div>
            <p>No hay encuestas cargadas. Ve a <strong>Cargar Datos</strong> primero.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Ir a Cargar Datos", use_container_width=True):
            st.switch_page("pages/2_Cargar_Datos.py")
        return

    col_config, col_hyp = st.columns([2, 1])

    with col_config:
        st.markdown(
            '<p class="section-title"><i class="ti ti-settings"></i> Configuración del análisis</p>',
            unsafe_allow_html=True,
        )

        with st.form("form_analisis"):
            nombre = st.text_input(
                "Nombre del análisis",
                value="Análisis Hábitos de Pago — Cobán 2026",
                placeholder="Ej: Análisis Semana 3",
            )
            descripcion = st.text_area(
                "Descripción",
                value=(
                    "Aplicación de pruebas estadísticas inferenciales sobre los hábitos de pago "
                    "de consumidores de Cobán, Alta Verapaz."
                ),
                height=90,
            )

            st.markdown("<div style='height:.25rem'></div>", unsafe_allow_html=True)

            alpha = st.select_slider(
                "Nivel de significancia (α)",
                options=[0.01, 0.05, 0.10],
                value=0.05,
                format_func=lambda x: f"α = {x}  ({int((1-x)*100)}% confianza)",
            )

            st.markdown(f"""
            <div class="info-box" style="margin-top:.75rem">
                <i class="ti ti-database"></i>
                <strong> Dataset activo:</strong> {len(df)} registros ·
                {df['metodo_pago_preferido'].nunique() if 'metodo_pago_preferido' in df.columns else '?'} métodos de pago ·
                {df['grupo_etario'].nunique() if 'grupo_etario' in df.columns else '?'} grupos etarios
            </div>""", unsafe_allow_html=True)

            ejecutar = st.form_submit_button(
                "Ejecutar las 3 pruebas estadísticas",
                use_container_width=True,
                type="primary",
            )

        if ejecutar:
            _abrir_modal_analisis(df, user_id, nombre, descripcion, alpha)

    with col_hyp:
        st.markdown(
            '<p class="section-title"><i class="ti ti-clipboard-list"></i> Hipótesis</p>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div class="hyp-card fade-in">
            <div class="hyp-title">
                <i class="ti ti-test-pipe" style="color:var(--navy)"></i> Prueba 1 — t de Student
            </div>
            <strong>H₀:</strong> μ_efectivo = μ_digital<br>
            <strong>H₁:</strong> μ_efectivo ≠ μ_digital<br>
            <em style="font-size:.8rem;color:var(--text-400)">Gasto semanal por método de pago</em>
        </div>
        <div class="hyp-card fade-in-1">
            <div class="hyp-title">
                <i class="ti ti-grid-dots" style="color:var(--navy)"></i> Prueba 2 — Chi-cuadrado
            </div>
            <strong>H₀:</strong> Grupo etario ⊥ Método de pago<br>
            <strong>H₁:</strong> Existe relación significativa<br>
            <em style="font-size:.8rem;color:var(--text-400)">Independencia de variables categóricas</em>
        </div>
        <div class="hyp-card fade-in-2">
            <div class="hyp-title">
                <i class="ti ti-percentage" style="color:var(--navy)"></i> Prueba 3 — Z Proporción
            </div>
            <strong>H₀:</strong> p ≤ 0.40<br>
            <strong>H₁:</strong> p > 0.40<br>
            <em style="font-size:.8rem;color:var(--text-400)">Adopción de billetera digital</em>
        </div>

        <div class="info-box" style="margin-top:1rem">
            <strong><i class="ti ti-shield-check"></i> Supuestos verificados:</strong><br>
            · t de Student: Prueba de Levene para varianzas<br>
            · Chi²: Frecuencias esperadas ≥ 5<br>
            · Z: np₀ ≥ 5 y n(1-p₀) ≥ 5
        </div>
        """, unsafe_allow_html=True)


def _abrir_modal_analisis(df, user_id, nombre, descripcion, alpha):
    @st.dialog("Ejecutando análisis estadístico", width="large")
    def _modal():
        st.markdown("""
        <style>
        div[data-testid="stProgress"] > div > div { background:#1a2744 !important; border-radius:99px; }
        div[data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, #0077B6, #00B4D8, #0096C7, #0077B6) !important;
            background-size: 300% 100% !important;
            border-radius: 99px;
            animation: barraFlow 1.8s linear infinite;
        }
        @keyframes barraFlow {
            0%   { background-position: 100% 0; }
            100% { background-position:   0% 0; }
        }
        .paso-item { display:flex; align-items:center; gap:.6rem; padding:.35rem 0;
                     font-size:.9rem; color:#444; }
        .paso-item.done { color:#1B5E20; font-weight:600; }
        .paso-item.active { color:#0077B6; font-weight:600; }
        .paso-dot { width:10px; height:10px; border-radius:50%; background:#ddd; flex-shrink:0; }
        .paso-dot.done { background:#1B5E20; }
        .paso-dot.active { background:#0077B6; animation: pulse 1s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
        </style>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; padding:.5rem 0 1rem">
            <p style="color:#666; font-size:.9rem; margin:0">
                {nombre} · α = {alpha} · {len(df)} registros
            </p>
        </div>""", unsafe_allow_html=True)

        barra    = st.progress(0)
        estado   = st.empty()
        pasos_ph = st.empty()

        PASOS = [
            "t de Student",
            "Chi-cuadrado",
            "Z para proporción",
            "Decisiones empresariales",
            "Guardando resultados",
        ]

        def _render_pasos(actual):
            html = ""
            for i, p in enumerate(PASOS):
                if i < actual:
                    html += f'<div class="paso-item done"><div class="paso-dot done"></div>{p} — listo</div>'
                elif i == actual:
                    html += f'<div class="paso-item active"><div class="paso-dot active"></div>{p}...</div>'
                else:
                    html += f'<div class="paso-item"><div class="paso-dot"></div>{p}</div>'
            pasos_ph.markdown(html, unsafe_allow_html=True)

        from modules.decisiones import generar_todas_las_decisiones
        from modules.graficas import grafica_resumen_kpis
        from modules.pruebas import ResultadoPrueba

        resultados = {}
        try:
            # Paso 0 — t de Student
            _render_pasos(0); barra.progress(10); estado.caption("Prueba t de Student...")
            from modules.pruebas import prueba_t_student
            from modules.carga_datos import separar_grupos_pago
            try:
                ef, dig = separar_grupos_pago(df)
                resultados["t_student"] = prueba_t_student(ef, dig, alpha)
            except Exception as e:
                resultados["t_student"] = f"Error: {str(e)}"

            # Paso 1 — Chi-cuadrado
            _render_pasos(1); barra.progress(35); estado.caption("Prueba Chi-cuadrado...")
            from modules.pruebas import prueba_chi_cuadrado
            try:
                resultados["chi_cuadrado"] = prueba_chi_cuadrado(df, alpha=alpha)
            except Exception as e:
                resultados["chi_cuadrado"] = f"Error: {str(e)}"

            # Paso 2 — Z proporción
            _render_pasos(2); barra.progress(60); estado.caption("Prueba Z para proporción...")
            from modules.pruebas import prueba_z_proporcion
            try:
                resultados["z_proporcion"] = prueba_z_proporcion(df["uso_billetera_digital"], alpha=alpha)
            except Exception as e:
                resultados["z_proporcion"] = f"Error: {str(e)}"

            # Paso 3 — Decisiones
            _render_pasos(3); barra.progress(75); estado.caption("Generando decisiones empresariales...")
            decisiones = generar_todas_las_decisiones(resultados)

            # Paso 4 — Guardar
            _render_pasos(4); barra.progress(88); estado.caption("Guardando en base de datos...")
            analisis_id = None
            try:
                from modules.db import guardar_analisis, guardar_resultado_prueba, guardar_decision
                analisis_id = guardar_analisis(user_id, nombre, descripcion, len(df), alpha)
                if analisis_id:
                    for clave, res in resultados.items():
                        if isinstance(res, ResultadoPrueba):
                            guardar_resultado_prueba(
                                analisis_id, res.tipo_prueba, res.estadistico,
                                res.p_valor, res.grados_libertad, res.rechaza_h0, res.detalles,
                            )
                    for dec in decisiones:
                        guardar_decision(analisis_id, dec.decision, dec.conclusion,
                                         dec.recomendacion, dec.nivel_alerta)
            except Exception:
                pass

            # Completado
            _render_pasos(len(PASOS)); barra.progress(100); estado.empty()

            kpis = grafica_resumen_kpis(df)
            st.session_state["ultimo_analisis"] = {
                "id": analisis_id, "nombre": nombre,
                "descripcion": descripcion, "total_registros": len(df), "alpha": alpha,
            }
            st.session_state["resultados_pruebas"] = resultados
            st.session_state["decisiones"] = [d.a_dict() for d in decisiones]
            st.session_state["kpis"] = kpis

            # Resumen de resultados
            nombres_pr = {"t_student": "t de Student", "chi_cuadrado": "Chi-cuadrado", "z_proporcion": "Z Proporción"}
            resumen_html = '<div style="display:flex; gap:.75rem; flex-wrap:wrap; margin:1rem 0">'
            for clave, res in resultados.items():
                if isinstance(res, ResultadoPrueba):
                    color  = "#E53935" if res.rechaza_h0 else "#2E7D32"
                    icono  = "ti-circle-x" if res.rechaza_h0 else "ti-circle-check"
                    texto  = "Rechaza H₀" if res.rechaza_h0 else "No rechaza H₀"
                    resumen_html += f"""
                    <div style="flex:1; min-width:160px; border:1.5px solid {color}33;
                                border-radius:10px; padding:.75rem; text-align:center">
                        <div style="font-size:.78rem; color:#666; margin-bottom:.3rem">
                            {nombres_pr.get(clave, clave)}
                        </div>
                        <div style="font-size:1.05rem; font-weight:700; color:{color}">
                            <i class="ti {icono}"></i> {texto}
                        </div>
                        <div style="font-size:.78rem; color:#888; margin-top:.2rem">
                            p = {res.p_valor:.4f}
                        </div>
                    </div>"""
            resumen_html += "</div>"
            st.markdown(resumen_html, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Ver resultados completos", type="primary", use_container_width=True):
                    st.switch_page("pages/4_Resultados.py")
            with col2:
                if st.button("Exportar PDF", use_container_width=True):
                    st.switch_page("pages/6_Exportar.py")

        except Exception as e:
            barra.progress(0)
            st.error(f"Error inesperado: {str(e)}")

    _modal()


main()
