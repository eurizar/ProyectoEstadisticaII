"""Conexion y operaciones con Supabase PostgreSQL."""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

load_dotenv()


def obtener_cliente_base() -> Client:
    """Cliente Supabase sin JWT — solo para auth.refresh_session() antes de tener tokens."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Faltan SUPABASE_URL y SUPABASE_KEY en .env")
    return create_client(url, key)


def obtener_cliente() -> Client:
    """Retorna cliente Supabase autenticado con el JWT del usuario en sesion.
    Sin JWT, las RLS policies (auth.uid() = user_id) rechazan INSERT/SELECT."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError(
            "Faltan variables de entorno SUPABASE_URL y SUPABASE_KEY en el archivo .env"
        )
    cliente = create_client(url, key)

    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")
    if access_token and refresh_token:
        try:
            cliente.auth.set_session(access_token, refresh_token)
        except Exception:
            # Token expirado o invalido — sesion se renueva en proximo login
            pass
        try:
            cliente.postgrest.auth(access_token)
        except Exception:
            pass
    return cliente


def guardar_encuestas(df: pd.DataFrame, user_id: str) -> tuple[bool, str]:
    """
    Inserta registros del DataFrame en la tabla 'encuestas'.
    Retorna (exito, mensaje).
    """
    try:
        cliente = obtener_cliente()
        registros = df.to_dict(orient="records")
        for registro in registros:
            registro["user_id"] = user_id
            # Convertir bool de numpy a bool nativo
            if "uso_billetera_digital" in registro:
                registro["uso_billetera_digital"] = bool(registro["uso_billetera_digital"])
            # Convertir numericos de numpy a tipos nativos
            if "gasto_semanal" in registro:
                registro["gasto_semanal"] = float(registro["gasto_semanal"])
            if "edad" in registro:
                registro["edad"] = int(registro["edad"])
            if "confianza_digital" in registro:
                registro["confianza_digital"] = int(registro["confianza_digital"])
        cliente.table("encuestas").insert(registros).execute()
        return True, f"{len(registros)} registros guardados exitosamente."
    except Exception as e:
        return False, f"Error al guardar encuestas: {str(e)}"


def obtener_encuestas(user_id: str) -> pd.DataFrame:
    """Carga todas las encuestas del usuario desde Supabase."""
    try:
        cliente = obtener_cliente()
        respuesta = (
            cliente.table("encuestas")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        if respuesta.data:
            return pd.DataFrame(respuesta.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener encuestas: {str(e)}")
        return pd.DataFrame()


def guardar_analisis(user_id: str, nombre: str, descripcion: str, total_registros: int, alpha: float) -> int | None:
    """Inserta un nuevo analisis y retorna su ID generado."""
    try:
        cliente = obtener_cliente()
        respuesta = (
            cliente.table("analisis")
            .insert({
                "user_id": user_id,
                "nombre": nombre,
                "descripcion": descripcion,
                "total_registros": total_registros,
                "alpha": alpha,
            })
            .execute()
        )
        return respuesta.data[0]["id"]
    except Exception as e:
        st.error(f"Error al guardar analisis: {str(e)}")
        return None


def guardar_resultado_prueba(analisis_id: int, tipo_prueba: str, estadistico: float,
                              p_valor: float, grados_libertad: int | None,
                              rechaza_h0: bool, detalles: dict) -> bool:
    """Inserta el resultado de una prueba estadistica."""
    try:
        cliente = obtener_cliente()
        cliente.table("resultados_pruebas").insert({
            "analisis_id": analisis_id,
            "tipo_prueba": tipo_prueba,
            "estadistico": round(float(estadistico), 4),
            "p_valor": round(float(p_valor), 6),
            "grados_libertad": grados_libertad,
            "rechaza_h0": bool(rechaza_h0),
            "detalles": detalles,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar resultado de prueba: {str(e)}")
        return False


def guardar_decision(analisis_id: int, decision: str, conclusion: str,
                     recomendacion: str, nivel_alerta: str) -> bool:
    """Inserta una decision generada por el motor de decisiones."""
    try:
        cliente = obtener_cliente()
        cliente.table("decisiones_generadas").insert({
            "analisis_id": analisis_id,
            "decision": decision,
            "conclusion": conclusion,
            "recomendacion": recomendacion,
            "nivel_alerta": nivel_alerta,
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar decision: {str(e)}")
        return False


def obtener_historico(user_id: str) -> pd.DataFrame:
    """Retorna lista de analisis previos del usuario."""
    try:
        cliente = obtener_cliente()
        respuesta = (
            cliente.table("analisis")
            .select("*")
            .eq("user_id", user_id)
            .order("fecha_ejecucion", desc=True)
            .execute()
        )
        if respuesta.data:
            return pd.DataFrame(respuesta.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener historico: {str(e)}")
        return pd.DataFrame()


def obtener_encuestas_publico() -> pd.DataFrame:
    """Carga todas las encuestas usando clave anonima (sin JWT). Requiere politica publica en Supabase."""
    try:
        cliente = obtener_cliente_base()
        respuesta = cliente.table("encuestas").select("*").execute()
        if respuesta.data:
            return pd.DataFrame(respuesta.data)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def obtener_ultimo_analisis_publico() -> dict:
    """
    Carga el analisis mas reciente y sus resultados/decisiones/encuestas
    usando la clave anonima (sin JWT).
    Requiere ejecutar sql/04_politicas_publicas.sql en Supabase.
    Retorna: {"analisis": {...}, "resultados": {clave: ResultadoPrueba}, "decisiones": [...], "df_encuestas": DataFrame}
    """
    try:
        from modules.pruebas import ResultadoPrueba
        cliente = obtener_cliente_base()

        resp_a = (
            cliente.table("analisis")
            .select("*")
            .order("fecha_ejecucion", desc=True)
            .limit(1)
            .execute()
        )
        if not resp_a.data:
            return {}

        analisis = resp_a.data[0]
        analisis_id = analisis["id"]
        alpha = float(analisis.get("alpha", 0.05))

        resp_r = (
            cliente.table("resultados_pruebas")
            .select("*")
            .eq("analisis_id", analisis_id)
            .execute()
        )
        resp_d = (
            cliente.table("decisiones_generadas")
            .select("*")
            .eq("analisis_id", analisis_id)
            .execute()
        )
        resp_e = (
            cliente.table("encuestas")
            .select("*")
            .eq("user_id", analisis["user_id"])
            .execute()
        )

        # Mapea el tipo_prueba guardado en DB → clave usada en session_state
        _TIPO_A_CLAVE = {
            "t de Student":      "t_student",
            "Chi-cuadrado":      "chi_cuadrado",
            "Z para proporcion": "z_proporcion",
        }

        resultados = {}
        for row in (resp_r.data or []):
            tipo = row.get("tipo_prueba", "")
            clave = _TIPO_A_CLAVE.get(tipo, tipo)
            resultados[clave] = ResultadoPrueba(
                tipo_prueba=tipo,
                estadistico=float(row.get("estadistico") or 0),
                p_valor=float(row.get("p_valor") or 0),
                grados_libertad=row.get("grados_libertad"),
                rechaza_h0=bool(row.get("rechaza_h0", False)),
                alpha=alpha,
                detalles=row.get("detalles") or {},
            )

        df_encuestas = pd.DataFrame(resp_e.data) if resp_e.data else pd.DataFrame()

        return {
            "analisis": analisis,
            "resultados": resultados,
            "decisiones": resp_d.data or [],
            "df_encuestas": df_encuestas,
        }
    except Exception as e:
        return {"error": str(e)}


def obtener_detalle_analisis(analisis_id: int) -> dict:
    """
    Retorna diccionario con resultados y decisiones de un analisis especifico.
    Estructura: {"resultados": [...], "decisiones": [...]}
    """
    try:
        cliente = obtener_cliente()
        resultados = (
            cliente.table("resultados_pruebas")
            .select("*")
            .eq("analisis_id", analisis_id)
            .execute()
        )
        decisiones = (
            cliente.table("decisiones_generadas")
            .select("*")
            .eq("analisis_id", analisis_id)
            .execute()
        )
        return {
            "resultados": resultados.data or [],
            "decisiones": decisiones.data or [],
        }
    except Exception as e:
        st.error(f"Error al obtener detalle del analisis: {str(e)}")
        return {"resultados": [], "decisiones": []}
