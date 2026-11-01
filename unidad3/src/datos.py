from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from src.config import MAPEO_COLUMNAS, SEMILLA, PROPORCION_TEST


def cargar_iris():
    iris = load_iris(as_frame=True)
    X = iris.data.rename(columns=MAPEO_COLUMNAS)
    y = iris.target
    return X, y


def dividir_train_test(X, y):
    return train_test_split(
        X, y,
        test_size=PROPORCION_TEST,
        random_state=SEMILLA,
        stratify=y,
    )
