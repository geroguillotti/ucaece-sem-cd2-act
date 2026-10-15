"""Punto de entrada del proyecto.

Orquesta el flujo completo: carga configuración y datos, entrena el modelo
base, audita equidad, aplica la(s) técnica(s) de mitigación configurada(s),
vuelve a auditar, explica con SHAP y vuelca todo a evidencias.md y outputs/.

Este archivo no implementa detalles de ninguna etapa: cada paso vive en su
propio módulo dentro de src/.
"""

from dotenv import load_dotenv

from src.config import Config, cargar_configuracion
from src.data_loader import cargar_datos
from src.evidence_writer import escribir_evidencias
from src.explainability import explicar_modelo_base
from src.fairness_audit import ResultadoAuditoria, auditar_equidad
from src.mitigation.factory import get_mitigator, resolver_metodos
from src.model_training import DatosEntrenamiento, entrenar_modelo
from src.plots import (
    graficar_comparacion_metricas,
    graficar_resumen_shap,
    graficar_waterfall_instancias,
)

# --- Constantes del script ---
NOMBRE_ESCENARIO_BASE = "Modelo base (sin mitigar)"
NOMBRES_ESCENARIO_POR_METODO = {
    "exponentiated_gradient": "ExponentiatedGradient",
    "threshold_optimizer": "ThresholdOptimizer",
}


def _auditar_mitigaciones(datos: DatosEntrenamiento, config: Config) -> list[ResultadoAuditoria]:
    """Aplica cada método de mitigación configurado y audita el resultado."""
    resultados = []
    for metodo in resolver_metodos(config.mitigation_method):
        mitigador = get_mitigator(metodo, config.fairness_constraint, datos.modelo)
        mitigador.fit(datos.x_train, datos.y_train, datos.sensible_train)
        predicciones = mitigador.predict(datos.x_test, datos.sensible_test)

        resultado = auditar_equidad(
            NOMBRES_ESCENARIO_POR_METODO[metodo], datos.y_test, predicciones, datos.sensible_test
        )
        resultados.append(resultado)
        print(f"{resultado.nombre_escenario}: exactitud={resultado.exactitud:.3f}")

    return resultados


def main() -> None:
    load_dotenv()

    config = cargar_configuracion()
    dataframe = cargar_datos(config)
    datos = entrenar_modelo(dataframe, config)

    predicciones_base = datos.modelo.predict(datos.x_test)
    resultado_base = auditar_equidad(
        NOMBRE_ESCENARIO_BASE, datos.y_test, predicciones_base, datos.sensible_test
    )
    print(f"{resultado_base.nombre_escenario}: exactitud={resultado_base.exactitud:.3f}")

    resultados_mitigados = _auditar_mitigaciones(datos, config)

    estudio_shap = explicar_modelo_base(
        datos.modelo,
        datos.x_train,
        datos.x_test,
        datos.y_test,
        datos.nombres_features,
        config.sensitive_attribute,
    )

    graficar_comparacion_metricas([resultado_base, *resultados_mitigados])
    graficar_waterfall_instancias(estudio_shap)
    graficar_resumen_shap(estudio_shap)

    escribir_evidencias(config, resultado_base, resultados_mitigados, estudio_shap)
    print("Evidencias guardadas en evidencias.md y outputs/")


if __name__ == "__main__":
    main()
