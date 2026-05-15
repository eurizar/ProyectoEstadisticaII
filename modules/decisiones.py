"""Motor automatico de generacion de conclusiones tipo decision empresarial."""

from modules.pruebas import ResultadoPrueba
from dataclasses import dataclass


@dataclass
class Decision:
    """Representa una conclusion empresarial generada automaticamente."""
    prueba: str
    decision: str
    conclusion: str
    recomendacion: str
    nivel_alerta: str  # "alto", "medio", "bajo"

    def a_dict(self) -> dict:
        return {
            "prueba": self.prueba,
            "decision": self.decision,
            "conclusion": self.conclusion,
            "recomendacion": self.recomendacion,
            "nivel_alerta": self.nivel_alerta,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Motor de decision para prueba t de Student
# ─────────────────────────────────────────────────────────────────────────────

def decision_t_student(resultado: ResultadoPrueba) -> Decision:
    """Genera conclusion empresarial a partir del resultado de la prueba t."""
    d = resultado.detalles
    media_efectivo = d.get("media_efectivo", 0)
    media_digital = d.get("media_digital", 0)
    diferencia = abs(media_efectivo - media_digital)
    p = resultado.p_valor
    alpha = resultado.alpha

    if resultado.rechaza_h0:
        # Se rechaza H0: hay diferencia significativa
        if media_digital > media_efectivo:
            decision = (
                f"Los consumidores que usan metodos digitales gastan significativamente MAS "
                f"que quienes usan efectivo (Q{media_digital:.2f} vs Q{media_efectivo:.2f}, "
                f"diferencia = Q{diferencia:.2f}, p = {p:.4f} < {alpha})."
            )
            conclusion = (
                "Existe evidencia estadistica suficiente para concluir que existe una brecha "
                "significativa en el gasto semanal segun el metodo de pago. Los usuarios digitales "
                "tienen mayor capacidad de gasto, posiblemente asociado a un nivel socioeconomico "
                "mas alto o mayor acceso a credito."
            )
            recomendacion = (
                "Se recomienda a los comercios y fintech de Coban desarrollar productos y "
                "estrategias de fidelizacion orientadas al segmento de usuarios de pagos digitales, "
                "quienes representan mayor valor transaccional. Considerar programas de cashback, "
                "descuentos por pago digital y alianzas con billeteras electronicas."
            )
            nivel_alerta = "alto"
        else:
            decision = (
                f"Los consumidores que usan EFECTIVO gastan significativamente MAS "
                f"que quienes usan metodos digitales (Q{media_efectivo:.2f} vs Q{media_digital:.2f}, "
                f"diferencia = Q{diferencia:.2f}, p = {p:.4f} < {alpha})."
            )
            conclusion = (
                "A pesar de la tendencia hacia la digitalizacion, los usuarios de efectivo "
                "presentan mayor gasto semanal en el contexto local de Coban. Esto puede indicar "
                "que el comercio informal y los mercados tradicionales concentran un volumen "
                "transaccional alto que aun opera fuera del ecosistema digital."
            )
            recomendacion = (
                "Las instituciones financieras deben priorizar la inclusion financiera digital "
                "del segmento de mayor gasto, facilitando la transicion del efectivo a metodos "
                "digitales mediante capacitacion, simplificacion de onboarding y reduccion de "
                "costos de transaccion."
            )
            nivel_alerta = "alto"
    else:
        # No se rechaza H0: no hay diferencia significativa
        decision = (
            f"No existe diferencia estadisticamente significativa en el gasto semanal "
            f"entre usuarios de efectivo (Q{media_efectivo:.2f}) y digitales (Q{media_digital:.2f}) "
            f"(p = {p:.4f} >= {alpha})."
        )
        conclusion = (
            "Los datos no proporcionan evidencia suficiente para afirmar que el metodo de pago "
            "influye en el monto de gasto semanal de los consumidores de Coban. El gasto es "
            "homogeneo entre ambos grupos, sugiriendo que la eleccion del metodo de pago es "
            "independiente del nivel de gasto."
        )
        recomendacion = (
            "Dado que el gasto es similar entre grupos, las estrategias de conversion hacia "
            "pagos digitales deben centrarse en factores no economicos: conveniencia, seguridad "
            "percibida y acceso tecnologico, en lugar de incentivos monetarios diferenciados."
        )
        nivel_alerta = "bajo"

    return Decision(
        prueba="t de Student",
        decision=decision,
        conclusion=conclusion,
        recomendacion=recomendacion,
        nivel_alerta=nivel_alerta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Motor de decision para Chi-cuadrado
# ─────────────────────────────────────────────────────────────────────────────

def decision_chi_cuadrado(resultado: ResultadoPrueba) -> Decision:
    """Genera conclusion empresarial a partir del resultado de la prueba Chi-cuadrado."""
    d = resultado.detalles
    v_cramer = d.get("v_cramer", 0)
    interpretacion_v = d.get("interpretacion_v_cramer", "")
    p = resultado.p_valor
    alpha = resultado.alpha

    if resultado.rechaza_h0:
        decision = (
            f"Existe una asociacion estadisticamente significativa entre el grupo etario y el "
            f"metodo de pago preferido (chi2 = {resultado.estadistico:.4f}, "
            f"p = {p:.4f} < {alpha}, V de Cramer = {v_cramer:.3f} — {interpretacion_v})."
        )
        if v_cramer >= 0.30:
            conclusion = (
                "La brecha generacional en los habitos de pago es estadisticamente comprobada "
                "y de magnitud moderada a grande. Los grupos etarios jovenes (18-35) muestran "
                "mayor preferencia por metodos digitales, mientras que los grupos mayores (36+) "
                "tienden a mantener el uso de efectivo. Esta diferencia es relevante para "
                "estrategias comerciales segmentadas."
            )
            recomendacion = (
                "Implementar estrategias de mercadeo diferenciadas por grupo etario: para jovenes, "
                "potenciar la experiencia digital (apps, QR, billeteras); para adultos mayores, "
                "ofrecer asistencia presencial y programas de educacion financiera digital. "
                "Los comercios deben mantener ambas opciones de pago para no excluir ningun segmento."
            )
            nivel_alerta = "alto"
        else:
            conclusion = (
                "Aunque existe una relacion estadisticamente significativa entre edad y metodo de pago, "
                "el efecto es pequeno. La brecha generacional existe pero no es determinante: "
                "factores como el tipo de comercio, el ingreso mensual o la disponibilidad de "
                "infraestructura tecnologica pueden ser mas influyentes."
            )
            recomendacion = (
                "Investigar factores contextuales adicionales (tipo de comercio, zona geografica, "
                "nivel de ingreso) que puedan explicar mejor la variabilidad en los metodos de pago, "
                "ya que la edad por si sola tiene un poder explicativo limitado."
            )
            nivel_alerta = "medio"
    else:
        decision = (
            f"No existe evidencia estadistica de asociacion entre el grupo etario y el metodo "
            f"de pago preferido (chi2 = {resultado.estadistico:.4f}, p = {p:.4f} >= {alpha})."
        )
        conclusion = (
            "Los datos no respaldan la hipotesis de una brecha generacional significativa en los "
            "metodos de pago de los consumidores de Coban. La eleccion del metodo de pago parece "
            "ser independiente del grupo etario en la muestra analizada, lo que puede deberse a "
            "una adopcion tecnologica mas uniforme de lo esperado en la poblacion local."
        )
        recomendacion = (
            "Replantear la segmentacion de mercado para la adopcion de pagos digitales. "
            "En lugar de segmentar por edad, explorar variables como nivel de ingreso, "
            "tipo de comercio frecuentado o acceso a smartphones como predictores "
            "mas relevantes de la preferencia de pago."
        )
        nivel_alerta = "bajo"

    return Decision(
        prueba="Chi-cuadrado",
        decision=decision,
        conclusion=conclusion,
        recomendacion=recomendacion,
        nivel_alerta=nivel_alerta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Motor de decision para Z para proporcion
# ─────────────────────────────────────────────────────────────────────────────

def decision_z_proporcion(resultado: ResultadoPrueba) -> Decision:
    """Genera conclusion empresarial a partir del resultado de la prueba Z."""
    d = resultado.detalles
    p_muestral = d.get("p_muestral", 0)
    p0 = d.get("p0_hipotetico", 0.40)
    ic = d.get("intervalo_confianza_95", [0, 0])
    n = d.get("n_total", 0)
    p = resultado.p_valor
    alpha = resultado.alpha

    porcentaje = round(p_muestral * 100, 1)
    ic_str = f"[{ic[0]*100:.1f}%, {ic[1]*100:.1f}%]"

    if resultado.rechaza_h0:
        decision = (
            f"La proporcion de consumidores que ha usado billetera digital ({porcentaje}%) "
            f"es significativamente MAYOR al umbral del 40% (Z = {resultado.estadistico:.4f}, "
            f"p = {p:.4f} < {alpha}, IC 95% = {ic_str})."
        )
        conclusion = (
            f"Existe evidencia estadistica solida de que la adopcion de billeteras digitales en "
            f"Coban supera el 40% de la poblacion consumidora. Con una proporcion muestral del "
            f"{porcentaje}% (n = {n}), el mercado de pagos digitales ha alcanzado un nivel de "
            f"penetracion significativo que justifica inversiones en infraestructura y servicios financieros digitales."
        )
        recomendacion = (
            "El mercado de pagos digitales en Coban presenta una base solida para expansion. "
            "Se recomienda a las instituciones financieras y fintech intensificar su presencia "
            "en la region con productos como: cuentas digitales sin comisiones, alianzas con "
            "comercios locales para descuentos por pago digital, y programas de referidos para "
            "incrementar aun mas la adopcion."
        )
        nivel_alerta = "alto"
    else:
        decision = (
            f"No existe evidencia suficiente para afirmar que la proporcion de usuarios de "
            f"billetera digital supera el 40% (proporcion observada: {porcentaje}%, "
            f"Z = {resultado.estadistico:.4f}, p = {p:.4f} >= {alpha}, IC 95% = {ic_str})."
        )
        if p_muestral >= p0 * 0.85:  # Cerca del umbral
            conclusion = (
                f"Aunque la proporcion observada ({porcentaje}%) esta cerca del umbral del "
                f"{p0*100:.0f}%, los datos no son estadisticamente concluyentes. La adopcion de "
                f"billeteras digitales en Coban es emergente pero aun no ha alcanzado el nivel "
                f"de penetracion masiva. Factores como conectividad, confianza en sistemas digitales "
                f"y acceso a smartphones pueden estar limitando el crecimiento."
            )
            nivel_alerta = "medio"
        else:
            conclusion = (
                f"La adopcion de billeteras digitales en Coban ({porcentaje}%) se mantiene "
                f"por debajo del umbral critico del {p0*100:.0f}%. Existe una oportunidad "
                f"significativa de crecimiento que requiere intervenciones estructurales para "
                f"reducir las barreras de entrada al ecosistema digital."
            )
            nivel_alerta = "medio"

        recomendacion = (
            "Priorizar programas de inclusion financiera digital: campanas de educacion sobre "
            "seguridad en pagos moviles, subsidios para smartphones en segmentos vulnerables, "
            "y simplificacion del proceso de apertura de billeteras digitales. Trabajar con "
            "comercios locales para aceptar pagos digitales y crear incentivos de adoption."
        )

    return Decision(
        prueba="Z para proporcion",
        decision=decision,
        conclusion=conclusion,
        recomendacion=recomendacion,
        nivel_alerta=nivel_alerta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Funcion principal: genera todas las decisiones
# ─────────────────────────────────────────────────────────────────────────────

def generar_todas_las_decisiones(
    resultados: dict[str, ResultadoPrueba | str],
) -> list[Decision]:
    """
    Recibe el diccionario de resultados de ejecutar_todas_las_pruebas()
    y retorna lista de Decision generadas automaticamente.
    Solo procesa pruebas que no fallaron (tipo ResultadoPrueba).
    """
    decisiones = []

    if isinstance(resultados.get("t_student"), ResultadoPrueba):
        decisiones.append(decision_t_student(resultados["t_student"]))

    if isinstance(resultados.get("chi_cuadrado"), ResultadoPrueba):
        decisiones.append(decision_chi_cuadrado(resultados["chi_cuadrado"]))

    if isinstance(resultados.get("z_proporcion"), ResultadoPrueba):
        decisiones.append(decision_z_proporcion(resultados["z_proporcion"]))

    return decisiones


def resumen_ejecutivo(decisiones: list[Decision]) -> str:
    """
    Genera un parrafo de resumen ejecutivo combinando las 3 decisiones.
    Util para el reporte PDF.
    """
    if not decisiones:
        return "No se generaron decisiones. Verifique que las pruebas se ejecutaron correctamente."

    total = len(decisiones)
    rechazadas = sum(1 for d in decisiones if d.nivel_alerta == "alto")
    medias = sum(1 for d in decisiones if d.nivel_alerta == "medio")

    if rechazadas == 3:
        apertura = (
            "El analisis estadistico revelo hallazgos de alta relevancia empresarial en las "
            "tres dimensiones evaluadas."
        )
    elif rechazadas >= 2:
        apertura = (
            "El analisis estadistico revelo hallazgos significativos en la mayoria de las "
            "pruebas realizadas."
        )
    elif rechazadas == 1 or medias >= 1:
        apertura = (
            "El analisis estadistico revelo hallazgos mixtos: algunos indicadores son "
            "significativos mientras otros requieren mayor investigacion."
        )
    else:
        apertura = (
            "El analisis estadistico no encontro diferencias significativas en los "
            "indicadores evaluados para la muestra analizada."
        )

    partes = [apertura]
    for d in decisiones:
        partes.append(f"En cuanto a la {d.prueba}: {d.conclusion}")

    partes.append(
        "Estos resultados deben interpretarse en el contexto de una muestra no probabilistica "
        "de 50 consumidores de Coban, Alta Verapaz, y no deben generalizarse sin un estudio "
        "de mayor escala y representatividad."
    )

    return " ".join(partes)
