"""Mitigación de sesgo con Fairlearn ThresholdOptimizer.

A diferencia de ExponentiatedGradient, no reentrena el modelo: ajusta un
umbral de decisión distinto por grupo sobre el mismo modelo base ya entrenado
(`prefit=True`), por eso necesita el atributo sensible también al predecir.
"""

from fairlearn.postprocessing import ThresholdOptimizer
from sklearn.base import BaseEstimator

from src.mitigation.base_mitigator import BaseMitigator

RESTRICCIONES_DISPONIBLES = {"demographic_parity", "equalized_odds"}


class ThresholdOptimizerMitigator(BaseMitigator):
    """Aplica ThresholdOptimizer sobre un modelo base ya entrenado."""

    def __init__(self, restriccion: str, estimador_base: BaseEstimator):
        if restriccion not in RESTRICCIONES_DISPONIBLES:
            raise ValueError(f"Restricción '{restriccion}' no soportada por ThresholdOptimizer.")
        self._optimizador = ThresholdOptimizer(
            estimator=estimador_base,
            constraints=restriccion,
            predict_method="predict_proba",
            prefit=True,
        )

    def fit(self, x_train, y_train, sensible_train) -> None:
        self._optimizador.fit(x_train, y_train, sensitive_features=sensible_train)

    def predict(self, x_test, sensible_test):
        return self._optimizador.predict(x_test, sensitive_features=sensible_test)
