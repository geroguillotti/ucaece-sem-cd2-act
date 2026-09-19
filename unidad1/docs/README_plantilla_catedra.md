# Unidad 1 — Foundation Models: prompt engineering + PEFT

Plantilla base para el componente práctico (consignas 6 a 10) del Trabajo Práctico
Individual de la Unidad 1, Seminario de Ciencia de Datos II. Este README explica cómo
completar tu entrega individual a partir de esta plantilla.

> Las consignas 1 a 5 (caso de uso, elección de Foundation Model, estrategia de
> adaptación, hardware, esquema del flujo) se responden en un documento aparte (Word/PDF)
> y no generan código. Este repositorio cubre exclusivamente la parte ejecutable
> (consignas 6 a 10). Ver el texto completo en [`docs/actividad-unidad1.md`](docs/actividad-unidad1.md).

## 1. Elegí tu rama de trabajo

Según lo que hayas justificado en la consigna 2 y 3:

| Consigna 2 (modelo) | Consigna 3 (adaptación) | Qué usás en este repo |
|---|---|---|
| Modelo cerrado (Gemini) | Prompt engineering | `src/main.py` con `MODEL_PROVIDER=gemini` |
| Modelo de pesos abiertos (Groq) | Prompt engineering | `src/main.py` con `MODEL_PROVIDER=groq` |
| Modelo de pesos abiertos | PEFT (LoRA/QLoRA) | `notebooks/notebook_peft.ipynb` en Google Colab |
| Cualquiera | Full fine-tuning | No se implementa acá (excede el hardware gratuito). Implementá la rama PEFT como aproximación factible y dejá esa limitación explicitada en tu informe. |

## 2. Preparar el entorno (consigna 6)

Este repositorio agrupa varias unidades, cada una con su propio entorno. Por eso, para
crear el Codespace **no uses el botón de un clic** ("Create codespace on main"): hay que
elegir explícitamente la configuración de Unidad 1.

1. Desde este repositorio en GitHub, hacé clic en **Use this template** (o forkealo).
2. En tu copia, andá a **Code → Codespaces** y hacé clic en los **tres puntos ("...")**
   junto al botón verde → **New with options**.
3. En el campo **Dev container configuration**, elegí **unidad1-seminario-cd2** y
   confirmá con **Create codespace**.
4. Esperá a que termine de levantar el Codespace (instala las dependencias de
   `requirements.txt` automáticamente, no hace falta ningún paso manual). La terminal se
   abre directamente parada en la carpeta `unidad1/`.
5. Verificá que Python esté disponible corriendo:
   ```bash
   python3 --version
   ```

## 3. Obtener tu API key (consigna 7)

Según el modelo que hayas elegido en la consigna 2:

- **Gemini (modelo cerrado):** creá una key gratuita en
  [Google AI Studio](https://aistudio.google.com/app/apikey).
- **Groq (modelo de pesos abiertos):** creá una key gratuita en
  [console.groq.com](https://console.groq.com/keys).

Luego, en la terminal del Codespace (ya parada en `unidad1/`):

```bash
cp .env.example .env
```

Editá `.env` y completá:

```env
MODEL_PROVIDER=groq      # o "gemini", según tu elección
GROQ_API_KEY=tu-key-aca
GEMINI_API_KEY=tu-key-aca
```

Solo necesitás completar la key del proveedor que vayas a usar. **Nunca subas el
archivo `.env` al repositorio** (ya está excluido en `.gitignore`).

## 4. Instalar dependencias (consigna 8)

Ya se instalan solas al crear el Codespace (`postCreateCommand` en
`.devcontainer/unidad1/devcontainer.json`, en la raíz del repositorio). Si necesitás
reinstalarlas manualmente:

```bash
pip install -r requirements.txt
```

## 5. Ejecutar la rama de prompt engineering (consigna 9a)

Antes de ejecutar, personalizá tu entrega:

- En [`src/prompt_templates.py`](src/prompt_templates.py), reemplazá `EJEMPLOS_FEW_SHOT`
  por ejemplos de tu propio caso de uso (consigna 1). Si tu justificación de la
  consigna 3 fue chain-of-thought en lugar de few-shot, cambiá
  `CONSTRUIR_PROMPT` en `main.py` por `construir_prompt_chain_of_thought`.
- En [`src/main.py`](src/main.py), reemplazá `CONSULTAS_DE_EJEMPLO` por al menos 3
  consultas reales de tu caso de uso.

Ejecutá el script (la terminal ya está parada en `unidad1/`):

```bash
python -m src.main
```

Vas a ver cada consulta y su respuesta impresas en la terminal, y se genera
automáticamente un archivo `evidencias.md` con el prompt y la respuesta completa de
cada una.

### Errores comunes

- `Falta la variable de entorno MODEL_PROVIDER` → no copiaste/completaste el `.env`.
- `Falta la variable de entorno GROQ_API_KEY` / `GEMINI_API_KEY` → falta esa key en tu
  `.env`, o elegiste un `MODEL_PROVIDER` distinto al de la key que cargaste.
- `Proveedor '...' no soportado` → `MODEL_PROVIDER` debe ser exactamente `groq` o
  `gemini`.
- `Error code: 404 ... model_not_found` (rama Groq) → el catálogo de modelos de Groq
  cambia con el tiempo y el modelo pineado puede haber sido discontinuado. Corré en la
  terminal del Codespace (no expone tu key en el resultado):
  ```bash
  curl -s -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
  ```
  Elegí un `id` vigente de la respuesta y reemplazá `GROQ_MODEL_NAME` en
  `src/providers/groq_provider.py` por ese valor.

## 6. Ejecutar la rama PEFT (consigna 9b)

Si tu consigna 3 justificó PEFT (LoRA/QLoRA). Colab tiene integración nativa con
GitHub: **no hace falta subir nada a Google Drive** en ningún paso.

1. Abrí [Google Colab](https://colab.research.google.com) → **Archivo → Abrir notebook
   → pestaña GitHub** → pegá la URL de **tu propio fork** (o buscá tu usuario + el
   nombre del repo) → seleccioná `unidad1/notebooks/notebook_peft.ipynb`.

   Alternativa más rápida: armá la URL directo en el navegador, reemplazando
   `TU-USUARIO` por tu usuario de GitHub:
   ```
   https://colab.research.google.com/github/TU-USUARIO/ucaece-sem-cd2-act/blob/master/unidad1/notebooks/notebook_peft.ipynb
   ```
   > Importante: usá **tu fork**, no el repositorio de la cátedra. Si abrís el
   > original vas a estar trabajando sobre la plantilla, no sobre tu copia.

2. Activá GPU: **Entorno de ejecución → Cambiar tipo de entorno de ejecución → GPU (T4)**.
3. Ejecutá las celdas en orden. El notebook ya viene resuelto de punta a punta con un
   modelo base (GPT-2) y un dataset de ejemplo genérico.
4. Reemplazá el dataset de ejemplo (celda marcada `TODO`) por ejemplos propios de tu
   caso de uso, y ajustá los hiperparámetros marcados con `TODO` si querés experimentar.
5. Al final del notebook vas a tener una comparación de las respuestas del modelo
   **antes y después** del ajuste con LoRA — esa comparación es tu evidencia para la
   consigna 9b.
6. Guardá el resultado en tu repositorio con **Archivo → Guardar una copia en GitHub**
   (la primera vez te va a pedir autorizar la conexión Colab↔GitHub). Elegí tu fork,
   la rama `master` y la misma ruta `unidad1/notebooks/notebook_peft.ipynb`, y confirmá
   — Colab commitea el notebook ejecutado (con outputs) directo a tu repositorio, sin
   pasar por Drive ni por el Codespace.

## 7. Registrar y entregar (consigna 10)

1. Commiteá tu código, el notebook ejecutado y `evidencias.md`.
2. Completá este README (o un archivo aparte) resumiendo: caso de uso elegido, modelo
   elegido y estrategia de adaptación.
3. En el documento entregado (Word/PDF con las consignas 1 a 5), incluí el enlace a tu
   repositorio y capturas de una ejecución exitosa.

## Estructura del repositorio

```
.devcontainer/
└── unidad1/devcontainer.json         # config de Codespaces para Unidad 1 (Python 3.11)
                                       # el repo agrupa varias unidades; cada una tiene
                                       # su propia config bajo .devcontainer/<unidad>/
unidad1/
├── .env.example                      # variables de entorno esperadas (sin valores reales)
├── docs/actividad-unidad1.md         # consigna oficial de cátedra
├── notebooks/notebook_peft.ipynb     # rama PEFT (LoRA), para Google Colab
├── requirements.txt
└── src/
    ├── main.py                       # orquesta: lee config, corre consultas, escribe evidencias
    ├── prompt_templates.py           # técnicas de prompting (few-shot / chain-of-thought)
    └── providers/
        ├── base_provider.py          # contrato común: generate(prompt) -> str
        ├── factory.py                # get_provider(name) según MODEL_PROVIDER
        ├── groq_provider.py
        └── gemini_provider.py
```
