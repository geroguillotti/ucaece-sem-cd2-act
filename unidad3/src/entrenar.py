import argparse
import warnings

import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, f1_score
from sklearn.tree import DecisionTreeClassifier

from src.config import (
    EXPERIMENTO_PIPELINE,
    MLFLOW_TRACKING_URI,
    NOMBRE_ARTEFACTO_MODELO,
    PROFUNDIDAD_POR_DEFECTO,
    SEMILLA,
    TIPOS_SKOPS_CONFIABLES,
)
from src.datos import cargar_iris, dividir_train_test
from src.servidor_mlflow import verificar_servidor


def entrenar_modelo(X_train, y_train, max_depth):
    modelo = DecisionTreeClassifier(max_depth=max_depth, random_state=SEMILLA)
    modelo.fit(X_train, y_train)
    return modelo


def calcular_metricas(modelo, X_test, y_test):
    y_pred = modelo.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    return accuracy, f1


def registrar_en_mlflow(max_depth, modelo, X_ejemplo, accuracy, f1):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENTO_PIPELINE)

    with mlflow.start_run(run_name=f"arbol_max_depth_{max_depth}"):
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("modelo", "DecisionTreeClassifier")
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_macro", f1)
        warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer column")  # el target Iris es int; el aviso es inofensivo
        mlflow.sklearn.log_model(
            modelo,
            name=NOMBRE_ARTEFACTO_MODELO,
            input_example=X_ejemplo.iloc[:1],
            skops_trusted_types=TIPOS_SKOPS_CONFIABLES,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=PROFUNDIDAD_POR_DEFECTO)
    args = parser.parse_args()

    verificar_servidor()

    X, y = cargar_iris()
    X_train, X_test, y_train, y_test = dividir_train_test(X, y)

    modelo = entrenar_modelo(X_train, y_train, args.max_depth)
    accuracy, f1 = calcular_metricas(modelo, X_test, y_test)
    registrar_en_mlflow(args.max_depth, modelo, X_train, accuracy, f1)

    print(f"Corrida registrada: max_depth={args.max_depth} · accuracy={accuracy:.3f} · f1_macro={f1:.3f}")


if __name__ == "__main__":
    main()
