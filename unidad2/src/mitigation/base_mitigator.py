"""Contrato común que deben cumplir las técnicas de mitigación de Fairlearn.

No se usa `abc.ABC` a propósito (ver CLAUDE.md raíz, sección 1.1): con dos
técnicas alcanza con una clase simple que documente el contrato y falle de
forma clara si alguien olvida implementarlo.
"""


class BaseMitigator:
    """Define el contrato que debe cumplir una técnica de mitigación.

    Cualquier mitigador concreto debe implementar:
        fit(x_train, y_train, sensible_train) -> None
        predict(x_test, sensible_test) -> np.ndarray

    `predict` siempre recibe el atributo sensible del conjunto a predecir,
    aunque algunas técnicas (ej. ExponentiatedGradient) no lo necesiten: así
    el resto del pipeline no tiene que conocer la diferencia entre técnicas.
    """

    def fit(self, x_train, y_train, sensible_train) -> None:
        raise NotImplementedError("Cada mitigador debe implementar fit().")

    def predict(self, x_test, sensible_test):
        raise NotImplementedError("Cada mitigador debe implementar predict().")
