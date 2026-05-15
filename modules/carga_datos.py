"""Lectura, validacion y normalizacion de archivos CSV y Excel."""

import pandas as pd
import numpy as np


COLUMNAS_REQUERIDAS = [
    "edad",
    "grupo_etario",
    "genero",
    "ocupacion",
    "ingreso_mensual",
    "metodo_pago_preferido",
    "frecuencia_efectivo",
    "frecuencia_digital",
    "tipo_comercio",
    "gasto_semanal",
    "razon_metodo",
    "uso_billetera_digital",
    "confianza_digital",
]

VALORES_GRUPO_ETARIO = {"18-25", "26-35", "36-50", "51+"}
VALORES_GENERO = {"Masculino", "Femenino"}
VALORES_METODO_PAGO = {"Efectivo", "Transferencia", "Tarjeta debito", "Tarjeta credito", "Billetera digital"}
VALORES_FRECUENCIA = {"Nunca", "A veces", "Casi siempre", "Siempre"}
RANGO_CONFIANZA = (1, 5)


def leer_archivo(archivo) -> tuple[pd.DataFrame | None, str]:
    """
    Lee un archivo CSV o Excel subido via Streamlit.
    Retorna (DataFrame, mensaje_error). Si exito, mensaje_error es cadena vacia.
    """
    nombre = archivo.name.lower()
    try:
        if nombre.endswith(".csv"):
            df = pd.read_csv(archivo, encoding="utf-8")
        elif nombre.endswith((".xlsx", ".xls")):
            df = pd.read_excel(archivo, engine="openpyxl")
        else:
            return None, "Formato no soportado. Sube un archivo .csv, .xlsx o .xls"
        return df, ""
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(archivo, encoding="latin-1")
            return df, ""
        except Exception as e:
            return None, f"Error de codificacion al leer el archivo: {str(e)}"
    except Exception as e:
        return None, f"Error al leer el archivo: {str(e)}"


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte nombres de columnas a minusculas y reemplaza espacios por guiones bajos."""
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df


def validar_columnas(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Verifica que el DataFrame tenga todas las columnas requeridas.
    Retorna (valido, lista_de_columnas_faltantes).
    """
    columnas_df = set(df.columns.tolist())
    faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in columnas_df]
    return len(faltantes) == 0, faltantes


def validar_tipos(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Convierte y valida los tipos de datos del DataFrame.
    Retorna (df_convertido, lista_de_advertencias).
    """
    advertencias = []

    # Edad: entero entre 18 y 110
    try:
        df["edad"] = pd.to_numeric(df["edad"], errors="coerce").astype("Int64")
        invalidos = df[(df["edad"].isna()) | (df["edad"] < 18) | (df["edad"] > 110)].shape[0]
        if invalidos:
            advertencias.append(f"{invalidos} registros con edad fuera del rango 18-110 o no numerica.")
    except Exception:
        advertencias.append("No se pudo convertir la columna 'edad' a entero.")

    # Gasto semanal: float positivo
    try:
        df["gasto_semanal"] = pd.to_numeric(df["gasto_semanal"], errors="coerce")
        invalidos = df[(df["gasto_semanal"].isna()) | (df["gasto_semanal"] < 0)].shape[0]
        if invalidos:
            advertencias.append(f"{invalidos} registros con gasto_semanal invalido (negativo o no numerico).")
    except Exception:
        advertencias.append("No se pudo convertir la columna 'gasto_semanal' a numero.")

    # Confianza digital: entero 1-5
    try:
        df["confianza_digital"] = pd.to_numeric(df["confianza_digital"], errors="coerce").astype("Int64")
        invalidos = df[(df["confianza_digital"].isna()) | (df["confianza_digital"] < 1) | (df["confianza_digital"] > 5)].shape[0]
        if invalidos:
            advertencias.append(f"{invalidos} registros con confianza_digital fuera del rango 1-5.")
    except Exception:
        advertencias.append("No se pudo convertir la columna 'confianza_digital' a entero.")

    # uso_billetera_digital: booleano
    if df["uso_billetera_digital"].dtype == object:
        mapa_bool = {
            "si": True, "sí": True, "yes": True, "true": True, "1": True, "verdadero": True,
            "no": False, "false": False, "0": False, "falso": False,
        }
        df["uso_billetera_digital"] = (
            df["uso_billetera_digital"]
            .astype(str)
            .str.lower()
            .str.strip()
            .map(mapa_bool)
        )
        invalidos = df["uso_billetera_digital"].isna().sum()
        if invalidos:
            advertencias.append(f"{invalidos} registros con uso_billetera_digital con valor no reconocido.")

    return df, advertencias


def eliminar_nulos_criticos(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """
    Elimina filas con nulos en columnas criticas para el analisis estadistico.
    Retorna (df_limpio, cantidad_eliminados).
    """
    columnas_criticas = ["gasto_semanal", "metodo_pago_preferido", "grupo_etario", "uso_billetera_digital"]
    filas_antes = len(df)
    df = df.dropna(subset=columnas_criticas)
    eliminados = filas_antes - len(df)
    return df, eliminados


def procesar_archivo(archivo) -> tuple[pd.DataFrame | None, dict]:
    """
    Pipeline completo: leer -> normalizar -> validar columnas -> validar tipos -> limpiar nulos.
    Retorna (df_procesado, reporte) donde reporte tiene claves: 'exito', 'errores', 'advertencias', 'total_registros'.
    """
    reporte = {"exito": False, "errores": [], "advertencias": [], "total_registros": 0}

    df, error = leer_archivo(archivo)
    if error:
        reporte["errores"].append(error)
        return None, reporte

    df = normalizar_columnas(df)

    valido, faltantes = validar_columnas(df)
    if not valido:
        reporte["errores"].append(
            f"Columnas faltantes en el archivo: {', '.join(faltantes)}"
        )
        return None, reporte

    df, advertencias_tipos = validar_tipos(df)
    reporte["advertencias"].extend(advertencias_tipos)

    df, eliminados = eliminar_nulos_criticos(df)
    if eliminados:
        reporte["advertencias"].append(
            f"{eliminados} filas eliminadas por tener datos criticos nulos."
        )

    if len(df) < 10:
        reporte["errores"].append(
            f"El dataset tiene solo {len(df)} registros validos. Se necesitan al menos 10."
        )
        return None, reporte

    reporte["exito"] = True
    reporte["total_registros"] = len(df)
    return df.reset_index(drop=True), reporte


def separar_grupos_pago(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
    Separa el gasto semanal segun metodo de pago.
    Grupo efectivo = quienes prefieren 'Efectivo'.
    Grupo digital = resto de metodos.
    Retorna (serie_efectivo, serie_digital).
    """
    mascara_efectivo = df["metodo_pago_preferido"].str.lower() == "efectivo"
    efectivo = df.loc[mascara_efectivo, "gasto_semanal"].dropna()
    digital = df.loc[~mascara_efectivo, "gasto_semanal"].dropna()
    return efectivo, digital
