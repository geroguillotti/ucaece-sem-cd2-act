"""Contrato compartido que deben cumplir todos los proveedores de inferencia.

No se usa `abc.ABC` a propósito: para dos proveedores (Groq y Gemini) alcanza con
una clase simple que documente el contrato y falle de forma clara si alguien
olvida implementarlo. Cada proveedor concreto hereda de `BaseProvider`,
sobrescribe `generate` y define `nombre_modelo` en su constructor. La lectura
de la API key es común a ambos y vive acá para no duplicarla.
"""

import os


def leer_api_key(nombre_variable: str, donde_obtenerla: str) -> str:
    """Lee la API key del entorno y falla con un mensaje claro si falta."""
    api_key = os.environ.get(nombre_variable)
    if not api_key:
        raise ValueError(
            f"Falta la variable de entorno {nombre_variable}. "
            f"Obtené una key gratuita en {donde_obtenerla} y agregala a tu archivo .env."
        )
    return api_key


class BaseProvider:
    """Define el contrato que debe cumplir un proveedor de inferencia.

    Cualquier proveedor concreto debe implementar:
        generate(prompt: str) -> str

    y exponer los atributos:
        nombre_modelo: str        id del modelo usado, para registrarlo en las evidencias
        tokens_entrada: int | None   tokens del último prompt, si la API los informa
        tokens_salida: int | None    tokens de la última respuesta (incluido el razonamiento)

    Recibe un prompt de texto ya armado (con la técnica de prompting aplicada,
    ver `prompt_templates.py`) y devuelve la respuesta del modelo como texto.
    """

    nombre_modelo = "desconocido"
    tokens_entrada = None
    tokens_salida = None

    def generate(self, prompt: str) -> str:
        raise NotImplementedError(
            "Cada proveedor debe implementar su propio método generate(prompt)."
        )
