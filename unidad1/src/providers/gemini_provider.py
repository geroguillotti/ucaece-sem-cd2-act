"""Proveedor de inferencia para el modelo cerrado Gemini (Google AI Studio).

Rama alternativa heredada de la plantilla de la cátedra; no se usa en esta entrega.
Requiere instalar aparte `google-generativeai==0.8.3` (biblioteca en mantenimiento
limitado; el reemplazo oficial es `google-genai`).
"""

import google.generativeai as genai

from src.providers.base_provider import BaseProvider, leer_api_key

# --- Constantes del proveedor (nada de "magic strings/numbers" inline) ---
GEMINI_API_KEY_ENV_VAR = "GEMINI_API_KEY"
GEMINI_SITIO_API_KEY = "Google AI Studio"
# La plantilla traía gemini-1.5-flash, pero Google lo dio de baja en septiembre de 2025.
GEMINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.2


class GeminiProvider(BaseProvider):
    """Genera respuestas usando el modelo cerrado Gemini vía Google AI Studio."""

    def __init__(self):
        genai.configure(api_key=leer_api_key(GEMINI_API_KEY_ENV_VAR, GEMINI_SITIO_API_KEY))
        self._model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        self.nombre_modelo = GEMINI_MODEL_NAME

    def generate(self, prompt: str) -> str:
        try:
            respuesta = self._model.generate_content(
                prompt,
                generation_config={"temperature": GEMINI_TEMPERATURE},
            )
        except Exception as error:
            raise RuntimeError(f"Error al consultar la API de Gemini: {error}") from error

        return respuesta.text
