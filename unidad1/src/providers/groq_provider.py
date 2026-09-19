"""Proveedor de inferencia para modelos de pesos abiertos servidos por Groq."""

import os

from groq import Groq

from src.providers.base_provider import BaseProvider

# --- Constantes del proveedor (nada de "magic strings/numbers" inline) ---
GROQ_API_KEY_ENV_VAR = "GROQ_API_KEY"
GROQ_MODEL_NAME_ENV_VAR = "GROQ_MODEL_NAME"
# Modelo de pesos abiertos elegido en la consigna 2: gpt-oss-120b (OpenAI, licencia Apache 2.0,
# mezcla de expertos con 5,1B de parámetros activos), servido por Groq en el nivel gratuito.
# Llama 3.3 70B fue la primera opción, pero Groq lo retiró del plan gratuito el 16/08/2026.
# El catálogo cambia con el tiempo: si este id deja de existir, se puede fijar otro con la
# variable de entorno GROQ_MODEL_NAME sin tocar el código, o listar los vigentes con
# `curl -s -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`.
GROQ_MODEL_NAME_POR_DEFECTO = "openai/gpt-oss-120b"
# Temperatura baja: la tarea es de clasificación y redacción acotada, se busca consistencia.
GROQ_TEMPERATURE = 0.2
# Tope de tokens de salida: la respuesta estructurada es corta (cuatro líneas). Incluye el
# razonamiento interno del modelo, por eso se deja margen.
GROQ_MAX_TOKENS = 1200
# gpt-oss es un modelo de razonamiento: con esfuerzo bajo alcanza para clasificar y redactar,
# y se reduce la latencia y el consumo de tokens del nivel gratuito.
GROQ_REASONING_EFFORT = "low"


class GroqProvider(BaseProvider):
    """Genera respuestas usando un modelo de pesos abiertos vía la API de Groq."""

    def __init__(self):
        api_key = os.environ.get(GROQ_API_KEY_ENV_VAR)
        if not api_key:
            raise ValueError(
                f"Falta la variable de entorno {GROQ_API_KEY_ENV_VAR}. "
                "Obtené una key gratuita en console.groq.com y agregala a tu archivo .env."
            )
        self._client = Groq(api_key=api_key)
        self.nombre_modelo = os.environ.get(GROQ_MODEL_NAME_ENV_VAR, GROQ_MODEL_NAME_POR_DEFECTO)

    def generate(self, prompt: str) -> str:
        try:
            respuesta = self._client.chat.completions.create(
                model=self.nombre_modelo,
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS,
                reasoning_effort=GROQ_REASONING_EFFORT,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as error:
            raise RuntimeError(
                f"Error al consultar la API de Groq: {error}"
            ) from error

        return respuesta.choices[0].message.content
