"""Factory Method simple para instanciar el proveedor según MODEL_PROVIDER.

`main.py` llama a `get_provider()` una sola vez y no necesita saber nada más
sobre cómo se construye cada proveedor. Cada proveedor se importa recién
cuando se lo elige, así solo hace falta tener instalada la librería del
proveedor que realmente se usa (ver requirements.txt).
"""

from src.providers.base_provider import BaseProvider

# --- Nombres válidos de MODEL_PROVIDER ---
PROVIDER_GROQ = "groq"
PROVIDER_GEMINI = "gemini"


def get_provider(name: str) -> BaseProvider:
    """Devuelve la instancia de proveedor correspondiente a `name`.

    `name` debe ser "groq" o "gemini" (valor de la variable de entorno
    MODEL_PROVIDER). Lanza ValueError si el nombre no es reconocido.
    """
    nombre_normalizado = name.strip().lower()

    if nombre_normalizado == PROVIDER_GROQ:
        from src.providers.groq_provider import GroqProvider
        return GroqProvider()

    if nombre_normalizado == PROVIDER_GEMINI:
        from src.providers.gemini_provider import GeminiProvider
        return GeminiProvider()

    raise ValueError(
        f"Proveedor '{name}' no soportado. Usá '{PROVIDER_GROQ}' o '{PROVIDER_GEMINI}' "
        "en la variable de entorno MODEL_PROVIDER."
    )
