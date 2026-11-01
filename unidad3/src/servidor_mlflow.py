import sys
import urllib.request
import urllib.error

from src.config import MLFLOW_TRACKING_URI, TIMEOUT_SALUD_MLFLOW_S


def verificar_servidor():
    try:
        urllib.request.urlopen(
            f"{MLFLOW_TRACKING_URI}/health",
            timeout=TIMEOUT_SALUD_MLFLOW_S,
        )
    except Exception:
        print(
            f"No encuentro MLflow en {MLFLOW_TRACKING_URI}. "
            "Abrí otra terminal y ejecutá: mlflow ui"
        )
        sys.exit(1)
