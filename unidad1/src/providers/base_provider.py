"""Contrato compartido que deben cumplir todos los proveedores de inferencia.

No se usa `abc.ABC` a propósito: para dos proveedores (Groq y Gemini) alcanza con
una clase simple que documente el contrato y falle de forma clara si alguien
olvida implementarlo. Cada proveedor concreto hereda de `BaseProvider`,
sobrescribe `generate` y define `nombre_modelo` en su constructor.
"""


class BaseProvider:
    """Define el contrato que debe cumplir un proveedor de inferencia.

    Cualquier proveedor concreto debe implementar:
        generate(prompt: str) -> str

    y exponer el atributo:
        nombre_modelo: str   (id del modelo usado, para registrarlo en las evidencias)

    Recibe un prompt de texto ya armado (con la técnica de prompting aplicada,
    ver `prompt_templates.py`) y devuelve la respuesta del modelo como texto.
    """

    nombre_modelo = "desconocido"

    def generate(self, prompt: str) -> str:
        raise NotImplementedError(
            "Cada proveedor debe implementar su propio método generate(prompt)."
        )
