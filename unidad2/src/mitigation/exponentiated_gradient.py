"""Mitigación de sesgo con Fairlearn ExponentiatedGradient.

Reduce el problema de clasificación restringida a una secuencia de modelos
reponderados. Parte del mismo tipo de estimador que el modelo pre-mitigación,
pero lo reentrena desde cero (Fairlearn clona el estimador en cada paso).
"""

from fairlearn.reductions import DemographicParity, EqualizedOdds, ExponentiatedGradient
from sklearn.base import BaseEstimator

from src.mitigation.base_mitigator import BaseMitigator

RESTRICCIONES_DISPONIBLES = {
    "demographic_parity": DemographicParity,
    "equalized_odds": EqualizedOdds,
}


class ExponentiatedGradientMitigator(BaseMitigator):
    """Aplica ExponentiatedGradient con la restricción de equidad configurada."""

    def __init__(self, restriccion: str, estimador_base: BaseEstimator):
        self._reductor = ExponentiatedGradient(
            estimador_base, constraints=RESTRICCIONES_DISPONIBLES[restriccion]()
        )

    def fit(self, x_train, y_train, sensible_train) -> None:
        self._reductor.fit(x_train, y_train, sensitive_features=sensible_train)

    def predict(self, x_test, sensible_test):
        return self._reductor.predict(x_test)
