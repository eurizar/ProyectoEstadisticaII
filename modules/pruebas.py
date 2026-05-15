"""Pruebas estadisticas inferenciales: t de Student, Chi-cuadrado, Z para proporcion."""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResultadoPrueba:
    """Estructura estandar para el resultado de cualquier prueba estadistica."""
    tipo_prueba: str
    estadistico: float
    p_valor: float
    grados_libertad: int | None
    rechaza_h0: bool
    alpha: float
    detalles: dict = field(default_factory=dict)

    def a_dict(self) -> dict:
        return {
            "tipo_prueba": self.tipo_prueba,
            "estadistico": self.estadistico,
            "p_valor": self.p_valor,
            "grados_libertad": self.grados_libertad,
            "rechaza_h0": self.rechaza_h0,
            "alpha": self.alpha,
            "detalles": self.detalles,
        }


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 1: t de Student para diferencia de medias (dos muestras independientes)
# H0: mu_efectivo = mu_digital
# H1: mu_efectivo != mu_digital
# ─────────────────────────────────────────────────────────────────────────────

def prueba_t_student(
    grupo_efectivo: pd.Series,
    grupo_digital: pd.Series,
    alpha: float = 0.05,
) -> ResultadoPrueba:
    """
    Aplica la prueba t de Student de dos muestras independientes.
    Usa Levene para decidir si asumir varianzas iguales o no (Welch).
    """
    efectivo = grupo_efectivo.dropna().astype(float)
    digital = grupo_digital.dropna().astype(float)

    if len(efectivo) < 2 or len(digital) < 2:
        raise ValueError(
            f"Grupos insuficientes para la prueba t. "
            f"Efectivo: {len(efectivo)}, Digital: {len(digital)}. "
            f"Se necesitan al menos 2 observaciones por grupo."
        )

    # Prueba de Levene para igualdad de varianzas
    estadistico_levene, p_levene = stats.levene(efectivo, digital)
    varianzas_iguales = p_levene > 0.05

    estadistico_t, p_valor = stats.ttest_ind(
        efectivo, digital, equal_var=varianzas_iguales
    )

    # Grados de libertad
    if varianzas_iguales:
        gl = len(efectivo) + len(digital) - 2
    else:
        # Formula de Welch-Satterthwaite
        s1, s2 = efectivo.var(ddof=1), digital.var(ddof=1)
        n1, n2 = len(efectivo), len(digital)
        num = (s1 / n1 + s2 / n2) ** 2
        den = (s1 / n1) ** 2 / (n1 - 1) + (s2 / n2) ** 2 / (n2 - 1)
        gl = int(num / den)

    rechaza_h0 = float(p_valor) < alpha

    detalles = {
        "n_efectivo": len(efectivo),
        "n_digital": len(digital),
        "media_efectivo": round(float(efectivo.mean()), 2),
        "media_digital": round(float(digital.mean()), 2),
        "desv_efectivo": round(float(efectivo.std(ddof=1)), 2),
        "desv_digital": round(float(digital.std(ddof=1)), 2),
        "varianzas_iguales": bool(varianzas_iguales),
        "levene_estadistico": round(float(estadistico_levene), 4),
        "levene_p": round(float(p_levene), 4),
        "tipo_t": "Student clasica" if varianzas_iguales else "Welch (varianzas desiguales)",
    }

    return ResultadoPrueba(
        tipo_prueba="t de Student",
        estadistico=round(float(estadistico_t), 4),
        p_valor=round(float(p_valor), 6),
        grados_libertad=gl,
        rechaza_h0=rechaza_h0,
        alpha=alpha,
        detalles=detalles,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 2: Chi-cuadrado de independencia
# H0: grupo_etario y metodo_pago_preferido son independientes
# H1: existe relacion significativa entre ambas variables
# ─────────────────────────────────────────────────────────────────────────────

def prueba_chi_cuadrado(
    df: pd.DataFrame,
    columna_fila: str = "grupo_etario",
    columna_columna: str = "metodo_pago_preferido",
    alpha: float = 0.05,
) -> ResultadoPrueba:
    """Aplica la prueba Chi-cuadrado de independencia sobre una tabla de contingencia."""
    tabla_contingencia = pd.crosstab(df[columna_fila], df[columna_columna])

    if tabla_contingencia.shape[0] < 2 or tabla_contingencia.shape[1] < 2:
        raise ValueError(
            "Se necesitan al menos 2 categorias en cada variable para la prueba Chi-cuadrado."
        )

    chi2, p_valor, gl, frecuencias_esperadas = stats.chi2_contingency(tabla_contingencia)

    # Verificar supuesto: <= 20% de celdas con frecuencia esperada < 5
    total_celdas = frecuencias_esperadas.size
    celdas_bajas = np.sum(frecuencias_esperadas < 5)
    porcentaje_bajas = round((celdas_bajas / total_celdas) * 100, 1)

    # V de Cramer como medida del tamano del efecto
    n = tabla_contingencia.sum().sum()
    min_dim = min(tabla_contingencia.shape[0] - 1, tabla_contingencia.shape[1] - 1)
    v_cramer = round(float(np.sqrt(chi2 / (n * min_dim))), 4) if min_dim > 0 else 0.0

    rechaza_h0 = float(p_valor) < alpha

    detalles = {
        "tabla_contingencia": tabla_contingencia.to_dict(),
        "frecuencias_esperadas": pd.DataFrame(
            frecuencias_esperadas,
            index=tabla_contingencia.index,
            columns=tabla_contingencia.columns,
        ).round(2).to_dict(),
        "celdas_con_frecuencia_baja": int(celdas_bajas),
        "porcentaje_celdas_bajas": porcentaje_bajas,
        "supuesto_cumplido": bool(porcentaje_bajas <= 20),
        "v_cramer": v_cramer,
        "interpretacion_v_cramer": _interpretar_v_cramer(v_cramer),
        "n_total": int(n),
    }

    return ResultadoPrueba(
        tipo_prueba="Chi-cuadrado",
        estadistico=round(float(chi2), 4),
        p_valor=round(float(p_valor), 6),
        grados_libertad=int(gl),
        rechaza_h0=rechaza_h0,
        alpha=alpha,
        detalles=detalles,
    )


def _interpretar_v_cramer(v: float) -> str:
    if v < 0.10:
        return "Efecto despreciable"
    elif v < 0.30:
        return "Efecto pequeno"
    elif v < 0.50:
        return "Efecto moderado"
    else:
        return "Efecto grande"


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBA 3: Z para proporcion (una muestra)
# H0: p <= 0.40 (uso de billetera digital)
# H1: p > 0.40 (prueba unilateral derecha)
# ─────────────────────────────────────────────────────────────────────────────

def prueba_z_proporcion(
    serie_uso: pd.Series,
    p0: float = 0.40,
    alpha: float = 0.05,
) -> ResultadoPrueba:
    """
    Aplica la prueba Z para una proporcion poblacional.
    Prueba unilateral derecha: H1: p > p0.
    """
    datos = serie_uso.dropna()
    n = len(datos)

    if n < 30:
        raise ValueError(
            f"Muestra insuficiente para prueba Z ({n} observaciones). "
            f"Se necesitan al menos 30."
        )

    # Convertir a booleano si es necesario
    if datos.dtype == object:
        datos = datos.astype(str).str.lower().str.strip().map(
            {"true": True, "false": False, "si": True, "sí": True, "no": False, "1": True, "0": False}
        )

    exitos = int(datos.sum())
    p_muestral = float(exitos / n)

    # Estadistico Z
    error_estandar = float(np.sqrt(p0 * (1 - p0) / n))
    if error_estandar == 0:
        raise ValueError("Error estandar igual a cero. Verifica el valor p0 y el tamano de muestra.")

    estadistico_z = float((p_muestral - p0) / error_estandar)

    # p-valor unilateral derecho
    p_valor = float(1 - stats.norm.cdf(estadistico_z))

    # Valor critico Z para alpha unilateral
    z_critico = float(stats.norm.ppf(1 - alpha))

    # Intervalo de confianza 95% bilateral para la proporcion
    z_ic = float(stats.norm.ppf(1 - alpha / 2))
    margen = z_ic * float(np.sqrt(p_muestral * (1 - p_muestral) / n))
    ic_inferior = round(max(0.0, p_muestral - margen), 4)
    ic_superior = round(min(1.0, p_muestral + margen), 4)

    rechaza_h0 = estadistico_z > z_critico

    detalles = {
        "n_total": n,
        "exitos": exitos,
        "p_muestral": round(p_muestral, 4),
        "p0_hipotetico": p0,
        "error_estandar": round(error_estandar, 4),
        "z_critico": round(z_critico, 4),
        "tipo_prueba_cola": "Unilateral derecha (H1: p > p0)",
        "intervalo_confianza_95": [ic_inferior, ic_superior],
        "supuesto_np": round(n * p0, 2),
        "supuesto_n1_p": round(n * (1 - p0), 2),
        "supuesto_normal_cumplido": bool(n * p0 >= 5 and n * (1 - p0) >= 5),
    }

    return ResultadoPrueba(
        tipo_prueba="Z para proporcion",
        estadistico=round(estadistico_z, 4),
        p_valor=round(p_valor, 6),
        grados_libertad=None,
        rechaza_h0=rechaza_h0,
        alpha=alpha,
        detalles=detalles,
    )


def ejecutar_todas_las_pruebas(df: pd.DataFrame, alpha: float = 0.05) -> dict[str, ResultadoPrueba | str]:
    """
    Ejecuta las 3 pruebas estadisticas sobre el DataFrame completo.
    Retorna diccionario con claves 't_student', 'chi_cuadrado', 'z_proporcion'.
    Si una prueba falla, el valor es el mensaje de error como cadena.
    """
    from modules.carga_datos import separar_grupos_pago

    resultados: dict[str, Any] = {}

    # Prueba 1: t de Student
    try:
        efectivo, digital = separar_grupos_pago(df)
        resultados["t_student"] = prueba_t_student(efectivo, digital, alpha)
    except Exception as e:
        resultados["t_student"] = f"Error: {str(e)}"

    # Prueba 2: Chi-cuadrado
    try:
        resultados["chi_cuadrado"] = prueba_chi_cuadrado(df, alpha=alpha)
    except Exception as e:
        resultados["chi_cuadrado"] = f"Error: {str(e)}"

    # Prueba 3: Z para proporcion
    try:
        resultados["z_proporcion"] = prueba_z_proporcion(df["uso_billetera_digital"], alpha=alpha)
    except Exception as e:
        resultados["z_proporcion"] = f"Error: {str(e)}"

    return resultados
