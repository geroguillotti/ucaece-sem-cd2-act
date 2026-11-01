import os
import re
import sys
import time

import mlflow
import mlflow.groq
from dotenv import load_dotenv
from groq import Groq

from src.config import EXPERIMENTO_LLMOPS, MLFLOW_TRACKING_URI
from src.servidor_mlflow import verificar_servidor

load_dotenv()

MODELO_GROQ = "openai/gpt-oss-20b"
TEMPERATURA = 0

RESENAS = [
    ("La película estuvo buenísima, me encantó cada escena.", "positivo"),
    ("Re copado el concierto, tremendo show.", "positivo"),
    ("El restaurante estuvo genial, la comida espectacular.", "positivo"),
    ("Una porquería de servicio, tardaron una hora y llegó frío.", "negativo"),
    ("Malísima experiencia, no volvería nunca más.", "negativo"),
    ("Qué horror de película, me dormí a los diez minutos.", "negativo"),
]

PLANTILLAS = {
    "zero_shot": (
        "Clasificá el sentimiento de la siguiente reseña en una sola palabra: "
        "'positivo' o 'negativo'.\n\nReseña: {resena}"
    ),
    "few_shot": (
        "Clasificá el sentimiento de la siguiente reseña en una sola palabra: "
        "'positivo' o 'negativo'.\n\n"
        "Ejemplo 1: 'Me encantó la película' → positivo\n"
        "Ejemplo 2: 'Una decepción total' → negativo\n\n"
        "Reseña: {resena}"
    ),
}


def normalizar(texto):
    return re.sub(r"[^a-záéíóúñ]", "", texto.lower())


def clasificar_resena(cliente, plantilla_texto, resena):
    inicio = time.time()
    mensaje = plantilla_texto.format(resena=resena)
    respuesta = cliente.chat.completions.create(
        model=MODELO_GROQ,
        messages=[{"role": "user", "content": mensaje}],
        temperature=TEMPERATURA,
    )
    latencia = time.time() - inicio
    texto = normalizar(respuesta.choices[0].message.content)
    tokens = respuesta.usage.total_tokens
    return texto, tokens, latencia


def evaluar_plantilla(cliente, nombre, plantilla_texto):
    aciertos = 0
    tokens_total = 0
    latencias = []

    mlflow.set_experiment(EXPERIMENTO_LLMOPS)
    with mlflow.start_run(run_name=f"prompts_{nombre}"):
        mlflow.log_param("modelo", MODELO_GROQ)
        mlflow.log_param("temperatura", TEMPERATURA)
        mlflow.log_param("plantilla", nombre)

        for resena, etiqueta in RESENAS:
            respuesta, tokens, latencia = clasificar_resena(cliente, plantilla_texto, resena)
            if respuesta == etiqueta:
                aciertos += 1
            tokens_total += tokens
            latencias.append(latencia)

        tasa = aciertos / len(RESENAS)
        latencia_media = sum(latencias) / len(latencias)

        mlflow.log_metric("tasa_exito", tasa)
        mlflow.log_metric("tokens_totales", tokens_total)
        mlflow.log_metric("latencia_media_s", round(latencia_media, 3))
        mlflow.log_text(plantilla_texto, f"plantilla/{nombre}.txt")

    print(f"Plantilla {nombre} · tasa_exito={tasa:.3f} · tokens={tokens_total} · latencia_media={latencia_media:.3f} s")


def verificar_api_key():
    if not os.environ.get("GROQ_API_KEY"):
        print("No encontré GROQ_API_KEY. Copiá .env.example a .env y completá tu clave.")
        sys.exit(1)


def main():
    verificar_servidor()
    verificar_api_key()
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.groq.autolog()
    cliente = Groq()

    for nombre, plantilla_texto in PLANTILLAS.items():
        evaluar_plantilla(cliente, nombre, plantilla_texto)


if __name__ == "__main__":
    main()
