import json
import shutil
import sys
import tempfile
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient

from src.config import (
    ALIAS_CAMPEON,
    ARCHIVO_INFO_MODELO,
    CARPETA_MODELO_EXPORTADO,
    MLFLOW_TRACKING_URI,
    NOMBRE_MODELO,
)
from src.servidor_mlflow import verificar_servidor


def obtener_version_champion(client):
    try:
        return client.get_model_version_by_alias(NOMBRE_MODELO, ALIAS_CAMPEON)
    except Exception:
        print(
            f"No encontré el modelo '{NOMBRE_MODELO}' con alias @{ALIAS_CAMPEON}. "
            "Ejecutá primero: python -m src.registrar"
        )
        sys.exit(1)


def descargar_modelo(carpeta):
    if carpeta.exists():
        shutil.rmtree(carpeta)
    uri = f"models:/{NOMBRE_MODELO}@{ALIAS_CAMPEON}"
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_descarga = mlflow.artifacts.download_artifacts(artifact_uri=uri, dst_path=tmpdir)
        shutil.copytree(ruta_descarga, str(carpeta))


def escribir_info(carpeta, version):
    info = {
        "nombre": NOMBRE_MODELO,
        "version": version.version,
        "alias": ALIAS_CAMPEON,
    }
    with open(carpeta / ARCHIVO_INFO_MODELO, "w") as f:
        json.dump(info, f, indent=2)


def main():
    verificar_servidor()
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = MlflowClient()

    version = obtener_version_champion(client)
    carpeta = Path(CARPETA_MODELO_EXPORTADO)
    descargar_modelo(carpeta)
    escribir_info(carpeta, version)

    print(f"Modelo {NOMBRE_MODELO} v{version.version} (@{ALIAS_CAMPEON}) exportado a {CARPETA_MODELO_EXPORTADO}/")


if __name__ == "__main__":
    main()
