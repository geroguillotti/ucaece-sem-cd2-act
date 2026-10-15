"""Prepara las features para el modelo: imputación + codificación/escalado.

El atributo sensible se deja como una feature más (no se excluye del
entrenamiento): es lo que permite después ver, con SHAP, si el modelo lo usa
para discriminar. El `ColumnTransformer` se ajusta una sola vez sobre train y
se reutiliza para transformar test, evitando fuga de información.
"""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _separar_columnas_por_tipo(features: pd.DataFrame) -> tuple[list[str], list[str]]:
    columnas_categoricas = features.select_dtypes(include=["object", "category"]).columns.tolist()
    columnas_numericas = [columna for columna in features.columns if columna not in columnas_categoricas]
    return columnas_categoricas, columnas_numericas


def construir_preprocesador(features: pd.DataFrame) -> ColumnTransformer:
    """Arma el `ColumnTransformer` según los tipos de columna presentes en `features`."""
    columnas_categoricas, columnas_numericas = _separar_columnas_por_tipo(features)

    transformador_categorico = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    transformador_numerico = Pipeline(
        steps=[
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("categoricas", transformador_categorico, columnas_categoricas),
            ("numericas", transformador_numerico, columnas_numericas),
        ]
    )


def obtener_nombres_features(preprocesador: ColumnTransformer) -> list[str]:
    """Nombres de las columnas resultantes (sin el prefijo del transformador, más
    legibles en los gráficos de SHAP), en el mismo orden que la matriz transformada."""
    return [nombre.split("__", 1)[-1] for nombre in preprocesador.get_feature_names_out()]


def transformar_a_matriz_densa(preprocesador: ColumnTransformer, features: pd.DataFrame) -> np.ndarray:
    """Aplica un preprocesador ya ajustado y devuelve una matriz densa (no sparse)."""
    matriz = preprocesador.transform(features)
    return matriz.toarray() if hasattr(matriz, "toarray") else np.asarray(matriz)
