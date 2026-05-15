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
            _ejecutar_analisis(df, user_id, nombre, descripcion, alpha)

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


def _ejecutar_analisis(df, user_id, nombre, descripcion, alpha):
    from modules.pruebas import ejecutar_todas_las_pruebas
    from modules.decisiones import generar_todas_las_decisiones
    from modules.graficas import grafica_resumen_kpis

    progress = st.progress(0, "Iniciando análisis...")

    try:
        progress.progress(10, "Ejecutando prueba t de Student...")
        resultados = {}
        from modules.pruebas import prueba_t_student
        from modules.carga_datos import separar_grupos_pago
        try:
            ef, dig = separar_grupos_pago(df)
            resultados["t_student"] = prueba_t_student(ef, dig, alpha)
        except Exception as e:
            resultados["t_student"] = f"Error: {str(e)}"

        progress.progress(35, "Ejecutando prueba Chi-cuadrado...")
        from modules.pruebas import prueba_chi_cuadrado
        try:
            resultados["chi_cuadrado"] = prueba_chi_cuadrado(df, alpha=alpha)
        except Exception as e:
            resultados["chi_cuadrado"] = f"Error: {str(e)}"

        progress.progress(60, "Ejecutando prueba Z para proporción...")
        from modules.pruebas import prueba_z_proporcion
        try:
            resultados["z_proporcion"] = prueba_z_proporcion(df["uso_billetera_digital"], alpha=alpha)
        except Exception as e:
            resultados["z_proporcion"] = f"Error: {str(e)}"

        progress.progress(75, "Generando decisiones empresariales...")
        decisiones = generar_todas_las_decisiones(resultados)

        progress.progress(85, "Guardando en Supabase...")
        analisis_id = None
        try:
            from modules.db import guardar_analisis, guardar_resultado_prueba, guardar_decision
            analisis_id = guardar_analisis(user_id, nombre, descripcion, len(df), alpha)
            if analisis_id:
                for clave, res in resultados.items():
                    from modules.pruebas import ResultadoPrueba
                    if isinstance(res, ResultadoPrueba):
                        guardar_resultado_prueba(
                            analisis_id, res.tipo_prueba, res.estadistico,
                            res.p_valor, res.grados_libertad, res.rechaza_h0, res.detalles,
                        )
                for dec in decisiones:
                    guardar_decision(analisis_id, dec.decision, dec.conclusion,
                                     dec.recomendacion, dec.nivel_alerta)
        except Exception as e:
            st.warning(f"No se pudo guardar en Supabase: {str(e)}")

        progress.progress(100, "Análisis completado.")

        kpis = grafica_resumen_kpis(df)
        info_analisis = {
            "id": analisis_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "total_registros": len(df),
            "alpha": alpha,
        }
        st.session_state["ultimo_analisis"] = info_analisis
        st.session_state["resultados_pruebas"] = resultados
        st.session_state["decisiones"] = [d.a_dict() for d in decisiones]
        st.session_state["kpis"] = kpis

        # ── Resumen inmediato ──────────────────────────────────
        st.markdown(
            '<p class="section-title"><i class="ti ti-circle-check"></i> Resultados obtenidos</p>',
            unsafe_allow_html=True,
        )

        from modules.pruebas import ResultadoPrueba
        nombres = {
            "t_student": "t de Student",
            "chi_cuadrado": "Chi-cuadrado",
            "z_proporcion": "Z Proporción",
        }
        for clave, res in resultados.items():
            if isinstance(res, ResultadoPrueba):
                clase = "rechaza" if res.rechaza_h0 else "no-rechaza"
                icon_color = "#E53935" if res.rechaza_h0 else "#2E7D32"
                icon_name = "ti-circle-x" if res.rechaza_h0 else "ti-circle-check"
                decision_txt = "Rechaza H₀" if res.rechaza_h0 else "No rechaza H₀"
                st.markdown(f"""
                <div class="result-card {clase}">
                    <div class="test-name">
                        <i class="ti {icon_name}" style="color:{icon_color}"></i>
                        {nombres.get(clave, res.tipo_prueba)}
                    </div>
                    <div class="stat-grid">
                        <div class="stat-item">
                            <div class="slabel">Estadístico</div>
                            <div class="svalue">{res.estadistico:.4f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="slabel">p-valor</div>
                            <div class="svalue">{res.p_valor:.6f}</div>
                        </div>
                        <div class="stat-item">
                            <div class="slabel">Decisión</div>
                            <div class="svalue" style="font-family:var(--font-body);font-size:.9rem">
                                {decision_txt}
                            </div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="decision-card medio">
                    <div class="d-label">
                        <i class="ti ti-alert-triangle"></i> {nombres.get(clave, clave)}
                    </div>
                    <p>{res}</p>
                </div>""", unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("Ver resultados completos", use_container_width=True):
                st.switch_page("pages/4_Resultados.py")
        with col_r2:
            if st.button("Exportar PDF", use_container_width=True):
                st.switch_page("pages/6_Exportar.py")

    except Exception as e:
        st.error(f"Error inesperado en el análisis: {str(e)}")
        progress.progress(0)


main()
