"""Punto de entrada del proyecto.

Orquesta el flujo completo del asistente de primera respuesta: lee
MODEL_PROVIDER del entorno, instancia el proveedor correspondiente (vía el
factory), enmascara datos personales de cada mensaje, construye el prompt
few-shot, consulta al modelo y vuelca consulta, prompt y respuesta de cada
ejecución a evidencias.md.

Este archivo NO implementa detalles de ninguna API: eso vive en
src/providers/. Tampoco arma prompts a mano: eso vive en
src/prompt_templates.py.
"""

import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.privacidad import enmascarar_datos_personales
from src.prompt_templates import construir_prompt_few_shot
from src.providers.factory import get_provider

# --- Constantes del script (nada de "magic strings/numbers" inline) ---
MODEL_PROVIDER_ENV_VAR = "MODEL_PROVIDER"
EVIDENCIAS_FILE_PATH = "evidencias.md"
CAMPO_DERIVACION = "Derivar a humano"
CAMPO_INTENCION = "Intención"
# El nivel gratuito de Groq limita los tokens por minuto (8.000 TPM para gpt-oss-120b);
# cada consulta usa ~1.500 tokens, así que se espacian las llamadas para no superar el límite.
PAUSA_ENTRE_CONSULTAS_SEGUNDOS = 15

# Técnica de prompting elegida y justificada en la consigna 3: few-shot con rol,
# políticas del negocio y salida estructurada.
CONSTRUIR_PROMPT = construir_prompt_few_shot

# Mensajes reales de ejemplo del caso de uso (consigna 1): pacientes de una
# clínica odontológica escribiendo por WhatsApp. Cubren turnos, urgencias,
# coberturas, reclamos y un caso con datos personales que se enmascaran.
CONSULTAS_DE_EJEMPLO = [
    "Buenas, quería saber si atienden Galeno y si tienen turno para ortodoncia la semana que viene a la mañana",
    "Mi hijo de 8 años se cayó en el colegio y se le aflojó un diente de adelante, está sangrando un poco. Hay que ir ya?",
    "Hola, tenía turno mañana a las 11 y no voy a poder ir, se puede pasar para el jueves? Mi celu es 11 5555 1234 por si me llaman",
    "Me hicieron una extracción el lunes y todavía tengo un poco de dolor, es normal? Tomo ibuprofeno?",
    "Hace una semana que pido presupuesto por mail y nadie me responde, quiero una respuesta hoy",
]


def leer_proveedor_configurado() -> str:
    """Lee MODEL_PROVIDER del entorno y falla con un mensaje claro si falta."""
    proveedor = os.environ.get(MODEL_PROVIDER_ENV_VAR)
    if not proveedor:
        raise ValueError(
            f"Falta la variable de entorno {MODEL_PROVIDER_ENV_VAR}. "
            "Definila en tu archivo .env como 'groq' o 'gemini'."
        )
    return proveedor


def extraer_campo(respuesta: str, nombre_campo: str) -> str:
    """Devuelve el valor de una línea 'Campo: valor' de la salida estructurada."""
    for linea in respuesta.splitlines():
        if linea.strip().lower().startswith(nombre_campo.lower() + ":"):
            return linea.split(":", 1)[1].strip()
    return "no informado"


def ejecutar_consulta(provider, consulta: str) -> tuple[str, str, str]:
    """Enmascara datos personales, arma el prompt y devuelve (consulta segura, prompt, respuesta)."""
    consulta_segura = enmascarar_datos_personales(consulta)
    prompt = CONSTRUIR_PROMPT(consulta_segura)
    respuesta = provider.generate(prompt)
    return consulta_segura, prompt, respuesta


def escribir_evidencias(resultados: list[tuple[str, str, str]], proveedor: str, modelo: str) -> None:
    """Vuelca consulta, prompt y respuesta de cada ejecución a un archivo Markdown."""
    fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lineas = [
        "# Evidencias de ejecución\n",
        f"- **Proveedor:** {proveedor}\n- **Modelo:** {modelo}\n- **Fecha de ejecución:** {fecha}\n",
        "- **Técnica de prompting:** few-shot con instrucciones de rol y salida estructurada\n",
    ]
    for numero, (consulta, prompt, respuesta) in enumerate(resultados, start=1):
        lineas.append(f"## Consulta {numero}\n")
        lineas.append(f"**Mensaje del paciente (con datos personales enmascarados):** {consulta}\n")
        lineas.append(f"**Clasificación:** intención = {extraer_campo(respuesta, CAMPO_INTENCION)} · "
                      f"derivar a humano = {extraer_campo(respuesta, CAMPO_DERIVACION)}\n")
        lineas.append(f"**Prompt enviado al modelo:**\n\n```\n{prompt}\n```\n")
        lineas.append(f"**Respuesta del modelo:**\n\n```\n{respuesta}\n```\n")

    with open(EVIDENCIAS_FILE_PATH, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))


def main() -> None:
    load_dotenv()

    proveedor_configurado = leer_proveedor_configurado()
    provider = get_provider(proveedor_configurado)
    print(f"Proveedor: {proveedor_configurado} · Modelo: {provider.nombre_modelo}\n")

    resultados = []
    for numero, consulta in enumerate(CONSULTAS_DE_EJEMPLO, start=1):
        if numero > 1:
            time.sleep(PAUSA_ENTRE_CONSULTAS_SEGUNDOS)
        consulta_segura, prompt, respuesta = ejecutar_consulta(provider, consulta)
        resultados.append((consulta_segura, prompt, respuesta))
        print(f"[{numero}] Mensaje: {consulta_segura}\n{respuesta}\n")

    escribir_evidencias(resultados, proveedor_configurado, provider.nombre_modelo)
    print(f"Evidencias guardadas en {EVIDENCIAS_FILE_PATH}")


if __name__ == "__main__":
    main()
