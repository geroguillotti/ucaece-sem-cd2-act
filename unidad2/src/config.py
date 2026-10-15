"""Lee y valida la configuración del entorno.

Único módulo que conoce los nombres de las variables de entorno. El resto del
proyecto recibe una instancia de `Config` ya validada.
"""

import os
from dataclasses import dataclass

# --- Nombres de variables de entorno ---
DATASET_PATH_ENV_VAR = "DATASET_PATH"
TARGET_COLUMN_ENV_VAR = "TARGET_COLUMN"
SENSITIVE_ATTRIBUTE_ENV_VAR = "SENSITIVE_ATTRIBUTE"
POSITIVE_LABEL_ENV_VAR = "POSITIVE_LABEL"
MITIGATION_METHOD_ENV_VAR = "MITIGATION_METHOD"
FAIRNESS_CONSTRAINT_ENV_VAR = "FAIRNESS_CONSTRAINT"

# --- Valores por defecto (activan el dataset de demostración) ---
DEFAULT_TARGET_COLUMN = "class"
DEFAULT_SENSITIVE_ATTRIBUTE = "sex"
DEFAULT_POSITIVE_LABEL = ">50K"
DEFAULT_MITIGATION_METHOD = "exponentiated_gradient"
DEFAULT_FAIRNESS_CONSTRAINT = "demographic_parity"

MITIGATION_METHOD_AMBOS = "ambos"
METODOS_MITIGACION_VALIDOS = {"exponentiated_gradient", "threshold_optimizer", MITIGATION_METHOD_AMBOS}
RESTRICCIONES_EQUIDAD_VALIDAS = {"demographic_parity", "equalized_odds"}


@dataclass(frozen=True)
class Config:
    """Configuración de una corrida, ya validada."""

    dataset_path: str | None
    target_column: str
    sensitive_attribute: str
    positive_label: str
    mitigation_method: str
    fairness_constraint: str

    @property
    def usa_dataset_demo(self) -> bool:
        return self.dataset_path is None


def cargar_configuracion() -> Config:
    """Lee las variables de entorno y devuelve una `Config` validada.

    Si `DATASET_PATH` no está definido, se activa el modo demo: se usan
    `TARGET_COLUMN`, `SENSITIVE_ATTRIBUTE` y `POSITIVE_LABEL` por defecto,
    coherentes con el dataset público que descarga `data_loader.py`.
    """
    dataset_path = os.environ.get(DATASET_PATH_ENV_VAR, "").strip() or None

    target_column = os.environ.get(TARGET_COLUMN_ENV_VAR, "").strip() or DEFAULT_TARGET_COLUMN
    sensitive_attribute = (
        os.environ.get(SENSITIVE_ATTRIBUTE_ENV_VAR, "").strip() or DEFAULT_SENSITIVE_ATTRIBUTE
    )
    positive_label = os.environ.get(POSITIVE_LABEL_ENV_VAR, "").strip() or DEFAULT_POSITIVE_LABEL

    mitigation_method = (
        os.environ.get(MITIGATION_METHOD_ENV_VAR, "").strip().lower() or DEFAULT_MITIGATION_METHOD
    )
    if mitigation_method not in METODOS_MITIGACION_VALIDOS:
        raise ValueError(
            f"{MITIGATION_METHOD_ENV_VAR}='{mitigation_method}' no es válido. "
            f"Usá uno de: {', '.join(sorted(METODOS_MITIGACION_VALIDOS))}."
        )

    fairness_constraint = (
        os.environ.get(FAIRNESS_CONSTRAINT_ENV_VAR, "").strip().lower() or DEFAULT_FAIRNESS_CONSTRAINT
    )
    if fairness_constraint not in RESTRICCIONES_EQUIDAD_VALIDAS:
        raise ValueError(
            f"{FAIRNESS_CONSTRAINT_ENV_VAR}='{fairness_constraint}' no es válida. "
            f"Usá una de: {', '.join(sorted(RESTRICCIONES_EQUIDAD_VALIDAS))}."
        )

    return Config(
        dataset_path=dataset_path,
        target_column=target_column,
        sensitive_attribute=sensitive_attribute,
        positive_label=positive_label,
        mitigation_method=mitigation_method,
        fairness_constraint=fairness_constraint,
    )
