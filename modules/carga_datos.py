"""Lectura, validacion y normalizacion de archivos CSV y Excel."""

import pandas as pd
import numpy as np

# Prefijo de la primera pregunta real del formulario Google Forms
_PREFIJO_FORMS = "cu"   # "cuál es su edad"


# ── Mapeos Google Forms → esquema BD ──────────────────────────────────────────

_MAPA_GRUPO_ETARIO = {
    "18": ("18-25", 21),
    "26": ("26-35", 30),
    "36": ("36-50", 43),
    "51": ("51+",   57),
}

_MAPA_METODO_PAGO = {
    "billetera": "Billetera digital",
    "efectivo":  "Efectivo",
    "tarjeta de cr": "Tarjeta credito",
    "tarjeta de d":  "Tarjeta debito",
    "transferencia": "Transferencia",
}

_MAPA_INGRESO = {
    "menos":         "<Q1500",
    "1,500 a q 3":   "Q1500-3000",
    "1.500 a q 3":   "Q1500-3000",
    "3,000 a q 5":   "Q3000-5000",
    "3.000 a q 5":   "Q3000-5000",
    "5,000 a q10":   "Q5000-10000",
    "5.000 a q10":   "Q5000-10000",
    "5,000 a q 10":  "Q5000-10000",
    "5.000 a q 10":  "Q5000-10000",
    "s de q 10":     ">Q10000",
    "s de q10":      ">Q10000",
}

_MAPA_RAZON = {
    "costumbre":    "Costumbre",
    "facilidad":    "Facilidad de acceso",
    "rapidez":      "Rapidez",
    "seguridad":    "Seguridad",
    "nico":         "Solo disponible",   # "único disponible..."
    "unico":        "Solo disponible",
    "solo":         "Solo disponible",
}

_MAPA_OCUPACION = {
    "estudia y trabaja": "Ambas",
    "estudia":           "Estudia",
    "trabaja":           "Trabaja",
    "ama":               "Ama de casa",
}


def _mapear(valor: str, mapa: dict, fallback: str | None = None) -> str:
    """Busca la primera clave del mapa que sea substring del valor en minúsculas."""
    v = str(valor).lower().strip()
    for clave, resultado in mapa.items():
        if clave in v:
            return resultado
    return fallback if fallback is not None else str(valor)[:30]


def detectar_formato_google_forms(df: pd.DataFrame) -> bool:
    """True si el DataFrame tiene columnas con preguntas largas (Google Forms)."""
    for col in df.columns:
        if len(col) > 40:
            return True
    return False


def transformar_google_forms(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Convierte el DataFrame exportado de Google Forms al esquema de BD.
    Filtra filas de personas que no residen en Cobán.
    Retorna (df_transformado, geo_data).
    """
    cols = df.columns.tolist()
    total_original = len(df)

    def _col(idx: int) -> pd.Series:
        return df.iloc[:, idx]

    # ── Filtrar no residentes de Cobán (última columna) ────────────────────
    col_coban = _col(13) if len(cols) > 13 else None
    excluidos = 0
    if col_coban is not None:
        mask = col_coban.astype(str).str.lower().str.strip().isin(["sí", "si", "sí"])
        excluidos = (~mask).sum()
        df = df[mask].copy()

    geo_data = {
        "total_original": total_original,
        "incluidos":      len(df),
        "excluidos":      int(excluidos),
    }

    if df.empty:
        return df, geo_data

    # ── grupo_etario y edad ────────────────────────────────────────────────
    def _grupo_edad(val):
        v = str(val)
        for prefijo, (grupo, edad) in _MAPA_GRUPO_ETARIO.items():
            if v.startswith(prefijo) or prefijo in v:
                return grupo, edad
        return "18-25", 21

    grupos_edades = _col(1).apply(_grupo_edad)
    grupo_etario = grupos_edades.apply(lambda x: x[0])
    edad         = grupos_edades.apply(lambda x: x[1])

    # ── Resto de columnas ──────────────────────────────────────────────────
    genero    = _col(2).astype(str).str.strip()
    ocupacion = _col(3).apply(lambda v: _mapear(v, _MAPA_OCUPACION))
    ingreso   = _col(4).apply(lambda v: _mapear(v, _MAPA_INGRESO))
    metodo    = _col(5).apply(lambda v: _mapear(v, _MAPA_METODO_PAGO))
    frec_ef   = _col(6).astype(str).str.strip()
    frec_dig  = _col(7).astype(str).str.strip()
    comercio  = _col(8).astype(str).str.strip().str[:30]
    gasto     = pd.to_numeric(_col(9), errors="coerce")
    razon     = _col(10).apply(lambda v: _mapear(v, _MAPA_RAZON))
    billetera = _col(11).astype(str).str.lower().str.strip().map(
        {"sí": True, "si": True, "sí": True, "no": False}
    )
    confianza = pd.to_numeric(_col(12), errors="coerce").astype("Int64")

    resultado = pd.DataFrame({
        "edad":                  edad,
        "grupo_etario":          grupo_etario,
        "genero":                genero,
        "ocupacion":             ocupacion,
        "ingreso_mensual":       ingreso,
        "metodo_pago_preferido": metodo,
        "frecuencia_efectivo":   frec_ef,
        "frecuencia_digital":    frec_dig,
        "tipo_comercio":         comercio,
        "gasto_semanal":         gasto,
        "razon_metodo":          razon,
        "uso_billetera_digital": billetera,
        "confianza_digital":     confianza,
    })

    return resultado.reset_index(drop=True), geo_data


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
        outliers = df[df["gasto_semanal"] > 50000].shape[0]
        if outliers:
            advertencias.append(
                f"{outliers} registro(s) con gasto_semanal > Q50,000 — posible error de captura. Verifica antes de guardar."
            )
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
    Pipeline completo: leer -> (transformar si Google Forms) -> normalizar -> validar -> limpiar.
    Retorna (df_procesado, reporte) donde reporte tiene claves: 'exito', 'errores', 'advertencias', 'total_registros'.
    """
    reporte = {"exito": False, "errores": [], "advertencias": [], "total_registros": 0, "geo_data": None}

    df, error = leer_archivo(archivo)
    if error:
        reporte["errores"].append(error)
        return None, reporte

    if detectar_formato_google_forms(df):
        reporte["advertencias"].append(
            "Formato Google Forms detectado — transformando columnas automáticamente."
        )
        df, geo_data = transformar_google_forms(df)
        reporte["geo_data"] = geo_data
        if df.empty:
            reporte["errores"].append("No quedaron registros tras filtrar residentes de Cobán.")
            return None, reporte
        if geo_data["excluidos"] > 0:
            reporte["advertencias"].append(
                f"{geo_data['excluidos']} encuesta(s) excluida(s) por no residir en Cobán "
                f"(de {geo_data['total_original']} totales)."
            )
    else:
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
