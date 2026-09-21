"""Proveedor de inferencia para modelos de pesos abiertos servidos por Groq."""

import os

from groq import Groq

from src.providers.base_provider import BaseProvider, leer_api_key

# --- Constantes del proveedor (nada de "magic strings/numbers" inline) ---
GROQ_API_KEY_ENV_VAR = "GROQ_API_KEY"
GROQ_SITIO_API_KEY = "console.groq.com"
GROQ_MODEL_NAME_ENV_VAR = "GROQ_MODEL_NAME"
# Modelo elegido en la consigna 2: gpt-oss-120b (pesos abiertos, Apache 2.0). La idea original era
# Llama 3.3 70B, pero Groq lo sacó del plan gratuito en agosto de 2026 y recomienda este.
# Como el catálogo cambia seguido, el id se puede pisar con GROQ_MODEL_NAME en el .env, o
# ver los vigentes con: curl -s -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
GROQ_MODEL_NAME_POR_DEFECTO = "openai/gpt-oss-120b"
# Temperatura baja porque acá lo que importa es que clasifique siempre igual, no la creatividad.
GROQ_TEMPERATURE = 0.2
# La respuesta son cuatro líneas, pero el tope también cuenta el razonamiento interno del modelo,
# así que dejo margen.
GROQ_MAX_COMPLETION_TOKENS = 1200
# gpt-oss razona antes de responder; con esfuerzo bajo alcanza para esta tarea y gasta menos
# tokens del plan gratuito.
GROQ_REASONING_EFFORT = "low"


class GroqProvider(BaseProvider):
    """Genera respuestas usando un modelo de pesos abiertos vía la API de Groq."""

    def __init__(self):
        self._client = Groq(api_key=leer_api_key(GROQ_API_KEY_ENV_VAR, GROQ_SITIO_API_KEY))
        self.nombre_modelo = os.environ.get(GROQ_MODEL_NAME_ENV_VAR, GROQ_MODEL_NAME_POR_DEFECTO)

    def generate(self, prompt: str) -> str:
        try:
            respuesta = self._client.chat.completions.create(
                model=self.nombre_modelo,
                temperature=GROQ_TEMPERATURE,
                max_completion_tokens=GROQ_MAX_COMPLETION_TOKENS,
                reasoning_effort=GROQ_REASONING_EFFORT,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as error:
            raise RuntimeError(f"Error al consultar la API de Groq: {error}") from error

        eleccion = respuesta.choices[0]
        if not eleccion.message.content:
            raise RuntimeError(
                "La API de Groq no devolvió texto de respuesta "
                f"(finish_reason={eleccion.finish_reason}). "
                "Subí GROQ_MAX_COMPLETION_TOKENS o bajá GROQ_REASONING_EFFORT."
            )
        if respuesta.usage is not None:
            self.tokens_entrada = respuesta.usage.prompt_tokens
            self.tokens_salida = respuesta.usage.completion_tokens
        return eleccion.message.content
