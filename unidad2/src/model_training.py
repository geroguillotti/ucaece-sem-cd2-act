"""Separa train/test, preprocesa y entrena el clasificador base.

No conoce nada de equidad ni de mitigación: eso vive en `fairness_audit.py` y
`mitigation/`. Este módulo solo produce un modelo base entrenado y los datos
ya transformados, listos para que el resto del pipeline los reutilice.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from src.config import Config
from src.preprocessing import (
    construir_preprocesador,
    obtener_nombres_features,
    transformar_a_matriz_densa,
)

# --- Constantes del módulo ---
SEMILLA = 42
TEST_SIZE = 0.3
MAX_ITERACIONES_MODELO = 1000


@dataclass
class DatosEntrenamiento:
    """Todo lo que necesita el resto del pipeline tras entrenar el modelo base."""

    modelo: LogisticRegression
    nombres_features: list[str]
    x_train: np.ndarray
    x_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    sensible_train: pd.Series
    sensible_test: pd.Series


def entrenar_modelo(dataframe: pd.DataFrame, config: Config) -> DatosEntrenamiento:
    """Separa train/test (semilla fija) y entrena la regresión logística base."""
    features = dataframe.drop(columns=[config.target_column])
    target = dataframe[config.target_column].to_numpy()
    sensible = dataframe[config.sensitive_attribute]

    x_train_crudo, x_test_crudo, y_train, y_test, sensible_train, sensible_test = train_test_split(
        features,
        target,
        sensible,
        test_size=TEST_SIZE,
        random_state=SEMILLA,
        stratify=target,
    )

    preprocesador = construir_preprocesador(x_train_crudo)
    preprocesador.fit(x_train_crudo)
    x_train = transformar_a_matriz_densa(preprocesador, x_train_crudo)
    x_test = transformar_a_matriz_densa(preprocesador, x_test_crudo)
    nombres_features = obtener_nombres_features(preprocesador)

    modelo = LogisticRegression(max_iter=MAX_ITERACIONES_MODELO, random_state=SEMILLA)
    modelo.fit(x_train, y_train)

    return DatosEntrenamiento(
        modelo=modelo,
        nombres_features=nombres_features,
        x_train=x_train,
        x_test=x_test,
        y_train=y_train,
        y_test=y_test,
        sensible_train=sensible_train.reset_index(drop=True),
        sensible_test=sensible_test.reset_index(drop=True),
    )
