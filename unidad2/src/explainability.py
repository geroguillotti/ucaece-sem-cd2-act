"""Aplica SHAP sobre el modelo base (pre-mitigación) para explicar predicciones.

Selecciona automáticamente dos instancias del conjunto de test: aquella donde
el atributo sensible más influye en la predicción según SHAP, y aquella donde
menos influye. Conecta directamente con la consigna 4 de la actividad (qué
técnica de XAI podría haber detectado el problema de forma preventiva).
"""

from dataclasses import dataclass

import numpy as np
import shap


@dataclass
class InstanciaExplicada:
    """Una predicción individual seleccionada para explicar."""

    indice: int
    contribucion_atributo_sensible: float
    prediccion: int
    valor_real: int


@dataclass
class EstudioSHAP:
    """Resultado completo del análisis SHAP sobre el conjunto de test."""

    explicacion: shap.Explanation
    columnas_sensibles: list[int]
    instancia_discrimina: InstanciaExplicada
    instancia_no_discrimina: InstanciaExplicada


def _columnas_del_atributo_sensible(nombres_features: list[str], atributo_sensible: str) -> list[int]:
    """Ubica, tras el preprocesamiento, qué columnas transformadas vienen del atributo sensible.

    Una columna categórica se expande en varias (`<atributo>_<categoría>` vía
    OneHotEncoder); una numérica conserva su propio nombre.
    """
    prefijo_categorico = f"{atributo_sensible}_"
    return [
        indice
        for indice, nombre in enumerate(nombres_features)
        if nombre.startswith(prefijo_categorico) or nombre == atributo_sensible
    ]


def _instancia_en(
    indice: int, contribucion_sensible: np.ndarray, predicciones: np.ndarray, y_test: np.ndarray
) -> InstanciaExplicada:
    return InstanciaExplicada(
        indice=indice,
        contribucion_atributo_sensible=float(contribucion_sensible[indice]),
        prediccion=int(predicciones[indice]),
        valor_real=int(y_test[indice]),
    )


def explicar_modelo_base(
    modelo,
    x_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    nombres_features: list[str],
    atributo_sensible: str,
) -> EstudioSHAP:
    """Calcula SHAP sobre `modelo` y elige las dos instancias más representativas."""
    columnas_sensibles = _columnas_del_atributo_sensible(nombres_features, atributo_sensible)
    if not columnas_sensibles:
        raise ValueError(
            f"No se encontraron columnas del atributo sensible '{atributo_sensible}' tras el "
            "preprocesamiento; no se puede calcular su contribución con SHAP."
        )

    explicador = shap.Explainer(modelo, x_train, feature_names=nombres_features)
    explicacion = explicador(x_test)

    contribucion_sensible = np.abs(explicacion.values[:, columnas_sensibles]).sum(axis=1)
    predicciones = modelo.predict(x_test)

    indice_discrimina = int(np.argmax(contribucion_sensible))
    indice_no_discrimina = int(np.argmin(contribucion_sensible))

    return EstudioSHAP(
        explicacion=explicacion,
        columnas_sensibles=columnas_sensibles,
        instancia_discrimina=_instancia_en(indice_discrimina, contribucion_sensible, predicciones, y_test),
        instancia_no_discrimina=_instancia_en(
            indice_no_discrimina, contribucion_sensible, predicciones, y_test
        ),
    )
