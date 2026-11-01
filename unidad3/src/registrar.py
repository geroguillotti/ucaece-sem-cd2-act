import sys

import mlflow
from mlflow.tracking import MlflowClient

from src.config import (
    ALIAS_CAMPEON,
    EXPERIMENTO_PIPELINE,
    METRICA_PRINCIPAL,
    MLFLOW_TRACKING_URI,
    NOMBRE_ARTEFACTO_MODELO,
    NOMBRE_MODELO,
)
from src.servidor_mlflow import verificar_servidor


def buscar_mejor_corrida(client):
    experimento = client.get_experiment_by_name(EXPERIMENTO_PIPELINE)
    if experimento is None:
        print(f"No encontré el experimento '{EXPERIMENTO_PIPELINE}'. Primero ejecutá: python -m src.entrenar")
        sys.exit(1)
    corridas = client.search_runs(
        experiment_ids=[experimento.experiment_id],
        order_by=[f"metrics.{METRICA_PRINCIPAL} DESC"],
        max_results=1,
    )
    if not corridas:
        print(f"No hay corridas en '{EXPERIMENTO_PIPELINE}'. Primero ejecutá: python -m src.entrenar")
        sys.exit(1)
    return corridas[0]


def registrar_como_nueva_version(run_id):
    uri = f"runs:/{run_id}/{NOMBRE_ARTEFACTO_MODELO}"
    return mlflow.register_model(uri, NOMBRE_MODELO)


def asignar_alias_campeon(client, version):
    client.set_registered_model_alias(NOMBRE_MODELO, ALIAS_CAMPEON, version)


def main():
    verificar_servidor()
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    corrida = buscar_mejor_corrida(client)
    version_registrada = registrar_como_nueva_version(corrida.info.run_id)
    asignar_alias_campeon(client, version_registrada.version)

    accuracy = corrida.data.metrics[METRICA_PRINCIPAL]
    print(
        f"Registrado {NOMBRE_MODELO} versión {version_registrada.version} con alias @{ALIAS_CAMPEON} "
        f"(corrida {corrida.info.run_name}, accuracy={accuracy:.3f})"
    )


if __name__ == "__main__":
    main()
