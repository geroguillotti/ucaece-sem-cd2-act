# Unidad 1: Asistente de primera respuesta para una clínica odontológica

**Entrega individual de Geronimo Guillotti** · Seminario de Ciencia de Datos II · Licenciatura en
Ciencia de Datos (CAECE) · 2do cuatrimestre 2026.

Este directorio contiene el componente práctico (consignas 6 a 10) de la Actividad Formativa 1.
El diseño conceptual (consignas 1 a 5) está en el informe entregado por el campus. Se partió de
la plantilla de la cátedra, cuyas instrucciones originales quedaron en
[`docs/README_plantilla_catedra.md`](docs/README_plantilla_catedra.md).

## Caso de uso

Una clínica odontológica pequeña (caso hipotético, nombres ficticios) recibe por WhatsApp y web
chat decenas de mensajes diarios: pedidos de turno, urgencias por dolor o traumatismos, consultas
por precios y obras sociales, horarios y reclamos. El asistente lee cada mensaje y devuelve una
salida estructurada para que la recepción resuelva más rápido:

```
Intención: <turno | urgencia | precio_cobertura | horario_ubicacion | reclamo | otro>
Urgencia: <alta | media | baja>
Derivar a humano: <sí | no>
Respuesta sugerida: <borrador cordial en español rioplatense, sin diagnósticos>
```

La recepcionista revisa el borrador antes de enviarlo; las urgencias y los reclamos se derivan
siempre a una persona. Restricciones del contexto: presupuesto de PyME, datos sensibles de salud
(Ley 25.326), latencia de pocos segundos y español rioplatense.

## Modelo elegido

**Llama 3.3 70B Instruct (Meta), modelo de pesos abiertos, servido por la API de Groq**
(`llama-3.3-70b-versatile`). Motivos resumidos: costo por token muy bajo y nivel gratuito para el
prototipo; pesos abiertos que permiten migrar a un despliegue propio si la clínica necesita que
ningún dato salga de su infraestructura; y posibilidad futura de ajuste fino (LoRA), algo que un
modelo cerrado no ofrece. La justificación completa frente a un modelo cerrado (Gemini vía Google
AI Studio) está en el informe. El id del modelo puede cambiarse sin tocar el código con la variable
`GROQ_MODEL_NAME` en `.env`.

## Estrategia de adaptación

**Prompt engineering avanzado: few-shot prompting con instrucciones de rol y salida
estructurada** (`src/prompt_templates.py`). El prompt fija el rol del asistente, las políticas de
la clínica, el formato exacto de salida y seis ejemplos resueltos, uno por cada tipo de mensaje.
No se modifica ningún parámetro del modelo: la adaptación vive íntegramente en el prompt, lo que
permite cambiar políticas (horarios, coberturas, precios) en minutos y sin reentrenar. Además,
antes de enviar cada mensaje se enmascaran teléfonos, DNI y correos (`src/privacidad.py`).

## Cómo ejecutar

1. **Entorno.** En GitHub: *Code → Codespaces → "..." → New with options → Dev container
   configuration: `unidad1-seminario-cd2`*. La terminal abre en `unidad1/` con las dependencias
   ya instaladas. Verificar con `python3 --version`. Para correr en una máquina propia:
   `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
2. **API key.** Crear una key gratuita en [console.groq.com/keys](https://console.groq.com/keys)
   y guardarla en un archivo `.env` (nunca en el código ni en el repositorio; `.env` ya está en
   `.gitignore`):
   ```bash
   cp .env.example .env
   # editar .env: MODEL_PROVIDER=groq y GROQ_API_KEY=<tu key>
   ```
3. **Dependencias.** `requirements.txt` registra solo las de la rama elegida: `python-dotenv` y
   `groq` (versiones fijas). Si hiciera falta: `pip install -r requirements.txt`.
4. **Ejecución.**
   ```bash
   python -m src.main
   ```
   El script procesa cinco mensajes de pacientes, imprime la salida estructurada de cada uno y
   genera `evidencias.md` con el prompt completo y la respuesta del modelo para cada consulta.

## Evidencias

- [`evidencias.md`](evidencias.md): mensaje enmascarado, clasificación, prompt enviado y
  respuesta del modelo para cada una de las cinco consultas.
- [`docs/diagrama_flujo.png`](docs/diagrama_flujo.png): esquema del flujo completo, desde el
  mensaje del paciente hasta la respuesta (consigna 5).

## Estructura

```
unidad1/
├── .env.example                 # variables esperadas (sin valores reales)
├── requirements.txt             # python-dotenv + groq
├── evidencias.md                # generado por python -m src.main
├── docs/
│   ├── actividad-unidad1.md     # consigna oficial de la cátedra
│   ├── diagrama_flujo.png       # esquema del flujo de la solución
│   └── README_plantilla_catedra.md
├── notebooks/notebook_peft.ipynb   # rama PEFT de la plantilla (no usada en esta entrega)
└── src/
    ├── main.py                  # orquesta: config, enmascarado, consultas, evidencias
    ├── privacidad.py            # enmascarado de teléfonos, DNI y correos
    ├── prompt_templates.py      # few-shot con rol, políticas y salida estructurada
    └── providers/
        ├── base_provider.py     # contrato: generate(prompt) -> str, nombre_modelo
        ├── factory.py           # get_provider(name) según MODEL_PROVIDER
        ├── groq_provider.py     # Llama 3.3 70B vía Groq (temperatura 0,2)
        └── gemini_provider.py   # alternativa cerrada de la plantilla (no usada)
```
