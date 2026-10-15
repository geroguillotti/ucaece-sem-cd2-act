"""Calcula métricas de equidad de Fairlearn sobre las predicciones de un modelo.

No entrena ni mitiga nada (eso vive en `model_training.py` y `mitigation/`):
solo audita. Se usa tanto para el modelo base como para cada modelo mitigado,
con la misma función, así los resultados son directamente comparables.
"""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    demographic_parity_ratio,
    equal_opportunity_difference,
    equalized_odds_difference,
    selection_rate,
)
from sklearn.metrics import accuracy_score

# Métricas extra (punto opcional de la consigna 9.c). Cada función acepta
# (y_true, y_pred, sensitive_features=...).
# - demographic_parity_ratio: tasa de selección del grupo menos seleccionado
#   dividida por la del más seleccionado; es la heurística de los "cuatro
#   quintos" (< 0,8 indica impacto adverso) usada en selección de personal.
# - equal_opportunity_difference: brecha de tasa de verdaderos positivos, es
#   decir, de personas que sí trabajan en tecnología y el modelo descarta: el
#   daño del caso Amazon (candidatas calificadas filtradas).
METRICAS_EXTRA = {
    "demographic_parity_ratio": demographic_parity_ratio,
    "equal_opportunity_difference": equal_opportunity_difference,
}


@dataclass
class ResultadoAuditoria:
    """Resultado de auditar un escenario (modelo base o una mitigación) puntual."""

    nombre_escenario: str
    exactitud: float
    metricas_por_grupo: pd.DataFrame
    demographic_parity_difference: float
    equalized_odds_difference: float
    metricas_extra: dict = field(default_factory=dict)


def auditar_equidad(
    nombre_escenario: str,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensible: pd.Series,
) -> ResultadoAuditoria:
    """Calcula exactitud global, métricas por grupo y las métricas de disparidad."""
    metric_frame = MetricFrame(
        metrics={"exactitud": accuracy_score, "tasa_seleccion": selection_rate},
        y_true=y_true,
        y_pred=y_pred,
        sensitive_features=sensible,
    )
    metricas_extra = {
        nombre: funcion(y_true, y_pred, sensitive_features=sensible)
        for nombre, funcion in METRICAS_EXTRA.items()
    }

    return ResultadoAuditoria(
        nombre_escenario=nombre_escenario,
        exactitud=accuracy_score(y_true, y_pred),
        metricas_por_grupo=metric_frame.by_group,
        demographic_parity_difference=demographic_parity_difference(
            y_true, y_pred, sensitive_features=sensible
        ),
        equalized_odds_difference=equalized_odds_difference(
            y_true, y_pred, sensitive_features=sensible
        ),
        metricas_extra=metricas_extra,
    )
