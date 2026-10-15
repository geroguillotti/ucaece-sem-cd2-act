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
    equalized_odds_difference,
    selection_rate,
)
from sklearn.metrics import accuracy_score

# TODO estudiante (opcional): sumá acá una métrica de equidad adicional de
# fairlearn.metrics para enriquecer la comparación de la consigna 9.c. Cada
# función debe aceptar (y_true, y_pred, sensitive_features=...). Ejemplo:
#
# from fairlearn.metrics import equalized_odds_ratio
# METRICAS_EXTRA = {"equalized_odds_ratio": equalized_odds_ratio}
METRICAS_EXTRA: dict = {}


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
