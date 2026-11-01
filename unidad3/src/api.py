import json
import sys
from pathlib import Path

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from src.config import ARCHIVO_INFO_MODELO, CARPETA_MODELO_EXPORTADO, ESPECIES


def _cargar_modelo_e_info():
    carpeta = Path(CARPETA_MODELO_EXPORTADO)
    if not carpeta.exists():
        print(
            f"No encontré '{CARPETA_MODELO_EXPORTADO}/'. "
            "Ejecutá primero: python -m src.exportar_modelo"
        )
        sys.exit(1)
    modelo = mlflow.pyfunc.load_model(str(carpeta))
    with open(carpeta / ARCHIVO_INFO_MODELO) as f:
        info = json.load(f)
    id_modelo = f"{info['nombre']} v{info['version']} (@{info['alias']})"
    return modelo, id_modelo


_modelo, _id_modelo = _cargar_modelo_e_info()

app = FastAPI(title="Clasificador de Iris — Unidad 3")


class EntradaFlor(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "largo_sepalo_cm": 5.1,
                "ancho_sepalo_cm": 3.5,
                "largo_petalo_cm": 1.4,
                "ancho_petalo_cm": 0.2,
            }
        }
    )
    largo_sepalo_cm: float = Field(..., gt=0)
    ancho_sepalo_cm: float = Field(..., gt=0)
    largo_petalo_cm: float = Field(..., gt=0)
    ancho_petalo_cm: float = Field(..., gt=0)


class PrediccionFlor(BaseModel):
    especie: str
    clase: int
    modelo: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PrediccionFlor)
def predict(flor: EntradaFlor):
    datos = pd.DataFrame([flor.model_dump()])
    clase = int(_modelo.predict(datos)[0])
    return PrediccionFlor(especie=ESPECIES[clase], clase=clase, modelo=_id_modelo)
