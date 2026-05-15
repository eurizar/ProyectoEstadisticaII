"""Pagina de historico: lista de analisis previos del usuario con detalle expandible."""

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Histórico — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario


def _formatear_fecha(fecha_str: str) -> str:
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return fecha_str[:16] if fecha_str else "—"


def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_id
    requerir_autenticacion()
    sidebar_usuario("Historico")
    user_id = obtener_user_id()

    st.markdown("""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-history"></i> Histórico
        </span>
        <h1>Historial de análisis</h1>
        <p>Todos los análisis ejecutados por tu cuenta · Haz clic en uno para ver el detalle</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1])

    with col_side:
        st.markdown("""
        <div class="info-box fade-in">
            <strong><i class="ti ti-database"></i> ¿Qué se guarda?</strong><br>
            Cada análisis registra:<br>
            · Nombre y descripción<br>
            · Total de registros<br>
            · Nivel α utilizado<br>
            · Resultados de las 3 pruebas<br>
            · Decisiones generadas<br>
            · Fecha de ejecución
        </div>
        """, unsafe_allow_html=True)

        if st.button("Nuevo análisis", use_container_width=True, type="primary"):
            st.switch_page("pages/3_Nuevo_Analisis.py")

    with col_main:
        with st.spinner("Cargando historial..."):
            try:
                from modules.db import obtener_historico
                df_hist = obtener_historico(user_id)
            except Exception as e:
                st.error(f"Error al cargar histórico: {str(e)}")
                df_hist = pd.DataFrame()

        if df_hist.empty:
            st.markdown("""
            <div class="empty-state fade-in">
                <div class="es-icon"><i class="ti ti-clock-off"></i></div>
                <h3>Sin análisis previos</h3>
                <p>Ejecuta tu primer análisis estadístico para verlo aquí.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        st.markdown(f"""
        <p style="font-size:.85rem;color:var(--text-400);margin-bottom:1rem">
            <i class="ti ti-list"></i> {len(df_hist)} análisis encontrados
        </p>""", unsafe_allow_html=True)

        nivel_icons = {
            "alto": ("ti-alert-octagon", "#E53935"),
            "medio": ("ti-alert-triangle", "#F59E0B"),
            "bajo": ("ti-circle-check", "#2E7D32"),
        }

        for _, row in df_hist.iterrows():
            analisis_id = row.get("id")
            nombre = row.get("nombre", "Sin nombre")
            total = row.get("total_registros", "?")
            alpha = row.get("alpha", 0.05)
            fecha = _formatear_fecha(str(row.get("fecha_ejecucion", "")))
            desc = str(row.get("descripcion", ""))[:100]

            with st.expander(f"{nombre} — {fecha}"):
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    st.metric("Registros", total)
                with col_i2:
                    st.metric("Nivel α", alpha)
                with col_i3:
                    st.metric("ID", str(analisis_id)[:8] if analisis_id else "—")

                if desc:
                    st.caption(desc)

                if st.button("Cargar resultados", key=f"load_{analisis_id}"):
                    with st.spinner("Cargando detalle..."):
                        try:
                            from modules.db import obtener_detalle_analisis
                            detalle = obtener_detalle_analisis(analisis_id)
                            resultados = detalle.get("resultados", [])
                            decisiones = detalle.get("decisiones", [])

                            if resultados:
                                st.markdown("**Resultados de pruebas:**")
                                for res in resultados:
                                    rechaza = res.get("rechaza_h0", False)
                                    clase = "rechaza" if rechaza else "no-rechaza"
                                    icon_color = "#E53935" if rechaza else "#2E7D32"
                                    icon_name = "ti-circle-x" if rechaza else "ti-circle-check"
                                    st.markdown(f"""
                                    <div class="result-card {clase}" style="margin-bottom:.5rem">
                                        <div class="test-name" style="font-size:1rem">
                                            <i class="ti {icon_name}" style="color:{icon_color}"></i>
                                            {res.get('tipo_prueba','')}
                                        </div>
                                        <div class="stat-grid">
                                            <div class="stat-item">
                                                <div class="slabel">Estadístico</div>
                                                <div class="svalue">{res.get('estadistico','—')}</div>
                                            </div>
                                            <div class="stat-item">
                                                <div class="slabel">p-valor</div>
                                                <div class="svalue">{res.get('p_valor','—')}</div>
                                            </div>
                                            <div class="stat-item">
                                                <div class="slabel">Decisión</div>
                                                <div class="svalue" style="font-family:var(--font-body);font-size:.85rem">
                                                    {'Rechaza H₀' if rechaza else 'No rechaza H₀'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>""", unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="info-box">
                                    <i class="ti ti-info-circle"></i>
                                    No hay resultados de pruebas guardados para este análisis.
                                </div>""", unsafe_allow_html=True)

                            if decisiones:
                                st.markdown("**Decisiones generadas:**")
                                for dec in decisiones:
                                    nivel = dec.get("nivel_alerta", "bajo")
                                    icon_n, icon_c = nivel_icons.get(nivel, ("ti-info-circle", "#666"))
                                    st.markdown(f"""
                                    <div class="decision-card {nivel}" style="margin-bottom:.5rem">
                                        <div class="d-label">
                                            <i class="ti {icon_n}" style="color:{icon_c}"></i>
                                            Alerta: {nivel.upper()}
                                        </div>
                                        <p><strong>Decisión:</strong> {dec.get('decision','')}</p>
                                        <p><strong>Recomendación:</strong> {dec.get('recomendacion','')}</p>
                                    </div>""", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error al cargar detalle: {str(e)}")


main()
