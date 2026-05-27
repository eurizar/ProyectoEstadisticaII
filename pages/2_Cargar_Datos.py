"""Carga de datos: subir CSV/Excel, validar y persistir en Supabase."""

import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Cargar Datos — Estadística II UMG",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules.ui_helpers import cargar_estilos, sidebar_usuario


def main():
    cargar_estilos()
    from modules.auth import requerir_autenticacion, obtener_user_id
    requerir_autenticacion()
    sidebar_usuario("Cargar_Datos")
    user_id = obtener_user_id()

    st.markdown("""
    <div class="page-header fade-in">
        <span class="header-badge">
            <i class="ti ti-cloud-upload"></i> Carga de Datos
        </span>
        <h1>Cargar encuestas</h1>
        <p>Sube el archivo CSV o Excel · Valida estructura y tipos · Persiste en Supabase</p>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_guide = st.columns([3, 1])

    with col_guide:
        st.markdown("""
        <div class="upload-guide fade-in">
            <h4><i class="ti ti-list-check"></i> Formatos aceptados</h4>
            <ul>
                <li><strong>Google Forms (.xlsx)</strong> — exportación directa, se transforma automáticamente</li>
                <li><strong>Plantilla propia (.xlsx / .csv)</strong> — columnas normalizadas</li>
            </ul>
        </div>
        <div class="info-box">
            <strong><i class="ti ti-file-spreadsheet"></i> Formatos:</strong>
            .xlsx · .xls · .csv<br><br>
            <strong><i class="ti ti-circle-check"></i> Mínimo:</strong> 10 registros válidos<br>
            <strong><i class="ti ti-target"></i> Ideal:</strong> 50 encuestas<br><br>
            <strong><i class="ti ti-filter"></i> Filtro automático:</strong>
            Solo residentes de Cobán
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            "⬇ Plantilla Excel (.xlsx)",
            data=_plantilla_xlsx(),
            file_name="plantilla_encuesta.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
        st.download_button(
            "⬇ Plantilla CSV",
            data=_plantilla_csv(),
            file_name="plantilla_encuesta.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_main:
        st.markdown(
            '<p class="section-title"><i class="ti ti-folder-open"></i> Subir archivo</p>',
            unsafe_allow_html=True,
        )
        archivo = st.file_uploader(
            "Arrastra el archivo o haz clic",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )

        if archivo:
            from modules.carga_datos import procesar_archivo
            with st.spinner("Procesando archivo..."):
                df, reporte = procesar_archivo(archivo)

            st.markdown(
                '<p class="section-title"><i class="ti ti-shield-check"></i> Resultado de validación</p>',
                unsafe_allow_html=True,
            )

            if reporte["errores"]:
                for err in reporte["errores"]:
                    st.markdown(f"""
                    <div class="decision-card alto fade-in">
                        <div class="d-label"><i class="ti ti-circle-x"></i> Error crítico</div>
                        <p>{err}</p>
                    </div>""", unsafe_allow_html=True)
                return

            for adv in reporte["advertencias"]:
                st.markdown(f"""
                <div class="decision-card medio fade-in">
                    <div class="d-label"><i class="ti ti-alert-triangle"></i> Advertencia</div>
                    <p>{adv}</p>
                </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="decision-card bajo fade-in">
                <div class="d-label"><i class="ti ti-circle-check"></i> Archivo válido</div>
                <p><strong>{reporte['total_registros']}</strong> registros listos.
                Superó todas las validaciones requeridas.</p>
            </div>""", unsafe_allow_html=True)

            # KPIs rápidos
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Filas válidas", reporte["total_registros"])
            with c2: st.metric("Columnas", len(df.columns))
            with c3:
                pct = round((df["metodo_pago_preferido"].str.lower() == "efectivo").mean() * 100, 1) \
                      if "metodo_pago_preferido" in df.columns else 0
                st.metric("% Efectivo", f"{pct}%")

            st.markdown(
                '<p class="section-title"><i class="ti ti-table"></i> Vista previa</p>',
                unsafe_allow_html=True,
            )
            st.dataframe(df, use_container_width=True, hide_index=True, height=350)
            st.caption(f"Mostrando {len(df)} registros.")

            st.markdown(
                '<p class="section-title"><i class="ti ti-database-import"></i> Guardar en base de datos</p>',
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div class="info-box">
                <i class="ti ti-alert-circle"></i>
                <strong> Acción permanente:</strong> Los registros se insertarán en Supabase
                asociados a tu cuenta. Verifica que los datos son correctos.
            </div>""", unsafe_allow_html=True)

            @st.dialog("Datos guardados en base de datos")
            def _modal_guardado(total):
                st.markdown(f"""
                <div style="text-align:center; padding:1rem 0">
                    <div style="font-size:2.5rem; color:#1B5E20"><i class="ti ti-circle-check"></i></div>
                    <p style="font-size:1.1rem; font-weight:600; margin:.5rem 0">
                        {total} registros almacenados correctamente
                    </p>
                    <p style="color:var(--text-400); font-size:.9rem">
                        Los datos están disponibles en la base de datos.<br>
                        Puedes ejecutar el análisis estadístico ahora.
                    </p>
                </div>""", unsafe_allow_html=True)
                if st.button("Ir a Nuevo Análisis", type="primary", use_container_width=True):
                    st.switch_page("pages/3_Nuevo_Analisis.py")

            @st.dialog("Datos listos para análisis")
            def _modal_sesion(total):
                st.markdown(f"""
                <div style="text-align:center; padding:1rem 0">
                    <div style="font-size:2.5rem; color:#1565C0"><i class="ti ti-device-floppy"></i></div>
                    <p style="font-size:1.1rem; font-weight:600; margin:.5rem 0">
                        {total} registros cargados en sesión
                    </p>
                    <p style="color:var(--text-400); font-size:.9rem">
                        Los datos no se guardaron en la base de datos.<br>
                        Puedes ejecutar el análisis estadístico ahora.
                    </p>
                </div>""", unsafe_allow_html=True)
                if st.button("Ir a Nuevo Análisis", type="primary", use_container_width=True):
                    st.switch_page("pages/3_Nuevo_Analisis.py")

            col_b1, col_b2, _ = st.columns([2, 2, 2])
            with col_b1:
                if st.button("Guardar en base de datos", use_container_width=True, type="primary"):
                    with st.spinner("Guardando registros..."):
                        try:
                            from modules.db import guardar_encuestas
                            ok, msg = guardar_encuestas(df, user_id)
                            if ok:
                                st.session_state["df_encuestas"] = df
                                if reporte.get("geo_data"):
                                    st.session_state["geo_exclusion"] = reporte["geo_data"]
                                from modules.ui_helpers import lanzar_confeti
                                lanzar_confeti()
                                _modal_guardado(reporte["total_registros"])
                            else:
                                st.error(msg)
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            with col_b2:
                if st.button("Usar sin guardar", use_container_width=True):
                    st.session_state["df_encuestas"] = df
                    if reporte.get("geo_data"):
                        st.session_state["geo_exclusion"] = reporte["geo_data"]
                    _modal_sesion(reporte["total_registros"])
        else:
            st.markdown("""
            <div class="empty-state fade-in">
                <div class="es-icon"><i class="ti ti-file-upload"></i></div>
                <h3>Ningún archivo seleccionado</h3>
                <p>Sube el archivo con las respuestas de la encuesta para continuar.</p>
            </div>""", unsafe_allow_html=True)


def _plantilla_csv() -> str:
    cols = ("edad,grupo_etario,genero,ocupacion,ingreso_mensual,metodo_pago_preferido,"
            "frecuencia_efectivo,frecuencia_digital,tipo_comercio,gasto_semanal,"
            "razon_metodo,uso_billetera_digital,confianza_digital")
    row = ("22,18-25,Masculino,Estudia,<Q1500,Billetera digital,"
           "A veces,Casi siempre,Supermercado,250.00,Rapidez,True,4")
    return f"{cols}\n{row}"


def _plantilla_xlsx() -> bytes:
    datos = {
        "edad":                  [22, 30, 43],
        "grupo_etario":          ["18-25", "26-35", "36-50"],
        "genero":                ["Masculino", "Femenino", "Masculino"],
        "ocupacion":             ["Estudia", "Trabaja", "Ambas"],
        "ingreso_mensual":       ["<Q1500", "Q1500-3000", "Q3000-5000"],
        "metodo_pago_preferido": ["Billetera digital", "Efectivo", "Tarjeta debito"],
        "frecuencia_efectivo":   ["A veces", "Siempre", "Casi siempre"],
        "frecuencia_digital":    ["Casi siempre", "Nunca", "A veces"],
        "tipo_comercio":         ["Supermercado", "Tienda de barrio", "Restaurante / comedor"],
        "gasto_semanal":         [250.00, 400.00, 600.00],
        "razon_metodo":          ["Rapidez", "Costumbre", "Seguridad"],
        "uso_billetera_digital": [True, False, True],
        "confianza_digital":     [4, 2, 5],
    }
    df = pd.DataFrame(datos)
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="encuestas")
    return buf.getvalue()


main()
