"""Pagina de exportacion: genera el reporte PDF completo descargable."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Exportar PDF — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario


def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_email
    requerir_autenticacion(permitir_publico=True)
    sidebar_usuario("Exportar")
    user_email = obtener_user_email() or "usuario@umg.edu.gt"

    st.markdown("""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-file-invoice"></i> Exportar
        </span>
        <h1>Generar reporte PDF</h1>
        <p>Reporte completo con KPIs · Resultados estadísticos · Decisiones empresariales</p>
    </div>
    """, unsafe_allow_html=True)

    resultados = st.session_state.get("resultados_pruebas")
    decisiones = st.session_state.get("decisiones", [])
    analisis_info = st.session_state.get("ultimo_analisis", {})
    df = st.session_state.get("df_encuestas", pd.DataFrame())
    kpis = st.session_state.get("kpis", {})

    col_main, col_side = st.columns([3, 1])

    with col_side:
        st.markdown("""
        <div class="info-box fade-in">
            <strong><i class="ti ti-list-check"></i> El PDF incluye:</strong><br>
            · Encabezado institucional UMG<br>
            · Datos del análisis<br>
            · Tabla de KPIs<br>
            · Resumen ejecutivo<br>
            · Resultados de las 3 pruebas<br>
            · Decisiones empresariales<br>
            · Conclusiones y recomendaciones
        </div>
        """, unsafe_allow_html=True)

        if not resultados:
            st.markdown("""
            <div class="decision-card medio">
                <div class="d-label"><i class="ti ti-alert-triangle"></i> Requerido</div>
                <p>Ejecuta un análisis primero.</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Ir a Nuevo Análisis", use_container_width=True):
                st.switch_page("pages/3_Nuevo_Analisis.py")

    with col_main:
        if not resultados:
            st.markdown("""
            <div class="empty-state fade-in">
                <div class="es-icon"><i class="ti ti-file-off"></i></div>
                <h3>Sin resultados para exportar</h3>
                <p>Ve a <strong>Nuevo Análisis</strong> y ejecuta las 3 pruebas estadísticas.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        st.markdown(
            '<p class="section-title"><i class="ti ti-clipboard-list"></i> Vista previa del reporte</p>',
            unsafe_allow_html=True,
        )

        if analisis_info:
            st.markdown(f"""
            <div class="stat-card fade-in" style="margin-bottom:1rem">
                <div class="s-label">Análisis a exportar</div>
                <div style="font-size:1.15rem;font-weight:700;color:var(--navy);margin:.3rem 0">
                    {analisis_info.get('nombre','Análisis')}
                </div>
                <div class="s-sub">
                    <i class="ti ti-database"></i>
                    {analisis_info.get('total_registros','?')} registros ·
                    α = {analisis_info.get('alpha', 0.05)} ·
                    {len(decisiones)} decisiones generadas
                </div>
            </div>""", unsafe_allow_html=True)

        if kpis:
            st.markdown("**Indicadores que se incluirán:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Encuestados", kpis.get("total_encuestados", "—"))
                st.metric("% Billetera digital", f"{kpis.get('pct_billetera', '—')}%")
            with col2:
                st.metric("% Efectivo", f"{kpis.get('pct_efectivo', '—')}%")
                st.metric("% Digital", f"{kpis.get('pct_digital', '—')}%")
            with col3:
                st.metric("Gasto prom.", f"Q{kpis.get('gasto_promedio', '—')}")
                st.metric("Confianza digital", f"{kpis.get('confianza_promedio', '—')}/5")

        from modules.pruebas import ResultadoPrueba
        st.markdown("**Pruebas estadísticas incluidas:**")
        nombres = {"t_student": "t de Student", "chi_cuadrado": "Chi-cuadrado", "z_proporcion": "Z Proporción"}
        pruebas_ok = []
        for clave, nombre in nombres.items():
            res = resultados.get(clave)
            # Acepta ResultadoPrueba objects o dicts (desde historial)
            if isinstance(res, ResultadoPrueba):
                pruebas_ok.append(res.a_dict())
                rechaza  = res.rechaza_h0
                estadist = res.estadistico
                p_val    = res.p_valor
            elif isinstance(res, dict) and "tipo_prueba" in res:
                pruebas_ok.append(res)
                rechaza  = res.get("rechaza_h0", False)
                estadist = res.get("estadistico", 0)
                p_val    = res.get("p_valor", 1)
            else:
                continue
            icon_color = "#E53935" if rechaza else "#2E7D32"
            icon_name  = "ti-circle-x" if rechaza else "ti-circle-check"
            decision   = "Rechaza H₀" if rechaza else "No rechaza H₀"
            st.markdown(f"""
            <div class="hyp-card">
                <span class="badge {'badge-danger' if rechaza else 'badge-success'}"
                      style="float:right">{decision}</span>
                <div class="hyp-title">
                    <i class="ti {icon_name}" style="color:{icon_color}"></i> {nombre}
                </div>
                Estadístico: <span class="text-mono">{estadist:.4f}</span> ·
                p-valor: <span class="text-mono">{p_val:.6f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        st.markdown(
            '<p class="section-title"><i class="ti ti-download"></i> Generar y descargar</p>',
            unsafe_allow_html=True,
        )

        col_b1, col_b2, _ = st.columns([2, 2, 2])
        with col_b1:
            if st.button("Generar PDF ahora", use_container_width=True, type="primary"):
                with st.spinner("Generando reporte PDF..."):
                    try:
                        from modules.decisiones import resumen_ejecutivo
                        from modules.exportar import generar_pdf
                        from modules.decisiones import Decision

                        objetos_decision = []
                        for d in decisiones:
                            dec = Decision(
                                prueba=d.get("prueba", ""),
                                decision=d.get("decision", ""),
                                conclusion=d.get("conclusion", ""),
                                recomendacion=d.get("recomendacion", ""),
                                nivel_alerta=d.get("nivel_alerta", "bajo"),
                            )
                            objetos_decision.append(dec)

                        resumen = resumen_ejecutivo(objetos_decision, n=analisis_info.get("total_registros", 0))

                        pdf_bytes = generar_pdf(
                            analisis_info=analisis_info,
                            kpis=kpis,
                            resultados_pruebas=pruebas_ok,
                            decisiones=decisiones,
                            resumen_ejecutivo=resumen,
                            user_email=user_email,
                        )

                        nombre_archivo = (
                            analisis_info.get("nombre", "reporte")
                            .lower()
                            .replace(" ", "_")
                            .replace("á", "a").replace("é", "e")
                            .replace("í", "i").replace("ó", "o")
                            .replace("ú", "u")
                        )

                        st.success("PDF generado correctamente.")
                        from modules.ui_helpers import lanzar_confeti
                        lanzar_confeti()
                        st.download_button(
                            label="Descargar reporte PDF",
                            data=pdf_bytes,
                            file_name=f"{nombre_archivo}_estadistica2_umg.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Error al generar PDF: {str(e)}")
                        st.exception(e)

        with col_b2:
            if st.button("Ver resultados completos", use_container_width=True):
                st.switch_page("pages/4_Resultados.py")


main()
