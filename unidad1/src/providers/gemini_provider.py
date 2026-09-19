"""Proveedor de inferencia para el modelo cerrado Gemini (Google AI Studio)."""

import os

import google.generativeai as genai

from src.providers.base_provider import BaseProvider

# --- Constantes del proveedor (nada de "magic strings/numbers" inline) ---
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
GEMINI_MODEL_NAME = "gemini-1.5-flash"
GEMINI_TEMPERATURE = 0.7


class GeminiProvider(BaseProvider):
    """Genera respuestas usando el modelo cerrado Gemini vía Google AI Studio."""

    def __init__(self):
        api_key = os.environ.get(GEMINI_API_KEY_ENV_VAR)
        if not api_key:
            raise ValueError(
                f"Falta la variable de entorno {GEMINI_API_KEY_ENV_VAR}. "
                "Obtené una key gratuita en Google AI Studio y agregala a tu archivo .env."
            )
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        self.nombre_modelo = GEMINI_MODEL_NAME

    def generate(self, prompt: str) -> str:
        try:
            respuesta = self._model.generate_content(
                prompt,
                generation_config={"temperature": GEMINI_TEMPERATURE},
            )
        except Exception as error:
            raise RuntimeError(
                f"Error al consultar la API de Gemini: {error}"
            ) from error

        return respuesta.text
