"""Minimización de datos personales antes de enviar un mensaje al modelo.

Los mensajes de pacientes pueden traer teléfonos, DNI, números de afiliado o
correos. Como el modelo se consume vía una API externa, se enmascaran esos datos
antes de construir el prompt: el modelo no los necesita para clasificar la
intención ni para redactar la respuesta, y así nunca salen del sistema propio.
"""

import re

# --- Patrones de datos personales frecuentes en mensajes de pacientes ---
PATRON_TELEFONO = re.compile(r"(?:\+?54\s?)?(?:9\s?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}")
PATRON_DNI = re.compile(r"\b\d{1,2}[.\s]?\d{3}[.\s]?\d{3}\b")
PATRON_CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

MARCA_TELEFONO = "[TELÉFONO]"
MARCA_DNI = "[DNI]"
MARCA_CORREO = "[CORREO]"


def enmascarar_datos_personales(texto: str) -> str:
    """Reemplaza correos, DNI y teléfonos por marcas genéricas, en ese orden."""
    texto = PATRON_CORREO.sub(MARCA_CORREO, texto)
    texto = PATRON_DNI.sub(MARCA_DNI, texto)
    texto = PATRON_TELEFONO.sub(MARCA_TELEFONO, texto)
    return texto
