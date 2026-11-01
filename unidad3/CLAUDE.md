# CLAUDE.md — Unidad 3: Implementación y Despliegue de Modelos (MLOps/LLMOps)

Este archivo brinda contexto persistente a Claude Code para asistir en la generación del
repositorio base de la actividad práctica de la **Unidad 3 — Tendencias Actuales en
Implementación y Despliegue de Modelos (MLOps/LLMOps)**, del Seminario de Ciencia de
Datos II.

> Este archivo complementa al `CLAUDE.md` raíz del repositorio, donde están definidas las
> restricciones de diseño comunes a todas las unidades (sección 1), la política de
> calidad de código obligatoria (sección 1.1) y el patrón de dev container por unidad
> (sección 2). No se repiten aquí; ambos archivos deben leerse en conjunto.

Este repositorio (carpeta `unidad3/`) es la **plantilla base** que luego usarán los
estudiantes (vía fork) para completar su propia entrega individual.

**Consigna completa de la actividad (texto oficial de cátedra, consignas 1-5, componente
práctico simplificado 6-10, paso opcional de LLMOps y calificación):**
@docs/actividad-unidad3.md

---

## 1. Contexto académico

- **Asignatura:** Seminario de Ciencia de Datos II.
- **Unidad:** Unidad 3 — Tendencias Actuales en Implementación y Despliegue de Modelos
  (MLOps/LLMOps).
- **Actividad:** Trabajo Práctico Individual — Diseño de un pipeline de MLOps/LLMOps para
  producción.
- **Rol de este repositorio:** plantilla base para el componente práctico (consignas 6 a
  10 y un paso opcional de LLMOps). Las consignas 1 a 5 son de resolución conceptual
  sobre el caso de uso propio del estudiante y no generan código.

## 2. Objetivo del repositorio: simplicidad ante todo

La cátedra decidió **simplificar al máximo** esta práctica para no confundir a los
estudiantes. El objetivo es una experiencia **simple pero enriquecedora** de MLOps:
recorrer, comando por comando, las etapas del ciclo de vida de un modelo.

| Etapa del ciclo de vida | Comando que ejecuta el estudiante | Consigna |
|---|---|---|
| Entorno reproducible | Crear el Codespace `unidad3-seminario-cd2` | 6 |
| Experimentación | `python -m src.entrenar --max-depth 1` y `--max-depth 3` | 7 |
| Registro (Model Registry) | `python -m src.registrar` | 7 |
| Serving | `python -m src.exportar_modelo` y `uvicorn src.api:app --port 8000` | 8 |
| Empaquetado y despliegue | `docker build -t modelo-u3:1.0 .` y `docker run` | 9 |
| LLMOps (opcional) | `python -m src.comparar_prompts` | opcional |

Principios que guían todas las decisiones de este archivo:

1. **Un solo camino.** Sin bifurcaciones (no hay elección de modelo, de dataset ni de
   backend). Todo funciona sin configurar nada, salvo el paso opcional de LLMOps.
2. **El estudiante no programa.** El código viene completo; el estudiante ejecuta,
   cambia el valor de `--max-depth`, observa, interpreta y documenta en `resultados.md`.
   No hay ningún `# TODO estudiante` en el código de esta unidad.
3. **Cada script es una etapa.** Un archivo por etapa del ciclo de vida, con nombres en
   castellano que se leen como la etapa que representan.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|----|----|
| RF-01 | `src/entrenar.py` entrena un `DecisionTreeClassifier` sobre el dataset Iris incluido en scikit-learn (`load_iris`, sin descargas), con `max_depth` recibido por línea de comandos (`--max-depth`, entero, por defecto 3), separación train/test estratificada y reproducible (semilla fija). |
| RF-02 | Cada ejecución de `entrenar.py` crea una corrida en MLflow (experimento `u3-pipeline-iris`) que registra: parámetros (`max_depth`, `modelo`), métricas (`accuracy`, `f1_macro`) y el modelo (`mlflow.sklearn.log_model`, nombre de artefacto `modelo`, con `input_example`). El nombre de la corrida es `arbol_max_depth_<N>`. |
| RF-03 | `src/registrar.py` busca la corrida con mayor `accuracy` del experimento, la registra como nueva versión del modelo `modelo-u3` en el Model Registry y le asigna el alias `champion` (no usar los *stages* Staging/Production: están obsoletos desde MLflow 2.9). |
| RF-04 | `src/exportar_modelo.py` descarga el modelo `models:/modelo-u3@champion` a la carpeta `modelo_exportado/` (reemplazándola si existe) y escribe allí `info_modelo.json` con nombre, versión y alias. |
| RF-05 | `src/api.py` expone con FastAPI `GET /health` y `POST /predict`. La API carga el modelo **siempre desde `modelo_exportado/`** (mismo código local y en Docker). `/predict` recibe las cuatro medidas de la flor y devuelve la especie, el número de clase y la identificación del modelo que respondió (ej. `"modelo-u3 v1 (@champion)"`). |
| RF-06 | El contrato de entrada de `/predict` se define con Pydantic: cuatro campos `float` obligatorios (`largo_sepalo_cm`, `ancho_sepalo_cm`, `largo_petalo_cm`, `ancho_petalo_cm`), mayores que cero, con valores de ejemplo para que `/docs` muestre un cuerpo listo para probar. Un dato inválido debe devolver HTTP 422 sin llegar al modelo. |
| RF-07 | `Dockerfile` empaqueta la API con las dependencias mínimas de `requirements-api.txt`, copia `src/` y `modelo_exportado/`, expone el puerto 8000 y arranca `uvicorn`. |
| RF-08 | `src/comparar_prompts.py` (paso **opcional** de LLMOps) compara dos plantillas de prompt (`zero_shot` y `few_shot`) para clasificar el sentimiento de 6 reseñas breves fijas, usando Groq. Crea una corrida por plantilla en el experimento `u3-llmops-prompts` con parámetros (modelo, temperatura, plantilla), métricas (`tasa_exito`, `tokens_totales`, `latencia_media_s`) y el texto de la plantilla como artefacto. Activa `mlflow.groq.autolog()` para que cada llamada quede como traza visible en la UI. |
| RF-09 | `resultados.md` es una plantilla para completar a mano (sección 6), con tablas y espacios vacíos para las capturas de `capturas/` y las respuestas breves de las consignas 7.d, 8.d y 9.c. Ningún script lo modifica. |
| RF-10 | `README.md` con instrucciones paso a paso, pensado para un estudiante sin experiencia previa en MLOps (contenido mínimo en la sección 6). |
| RF-11 | `.env.example` documenta únicamente `GROQ_API_KEY` (requerida solo para el paso opcional). |

## 4. Requerimientos no funcionales

| ID | Requerimiento |
|----|----|
| RNF-01 | El Codespace levanta listo para usar, sin pasos manuales de instalación (`.devcontainer/unidad3/devcontainer.json` en la raíz del repo, ya provisto, con Docker-in-Docker y las variables de entorno de MLflow de la sección 7). |
| RNF-02 | Todo corre en la CPU de un Codespace estándar de 2 núcleos. Sin GPU, sin Colab. |
| RNF-03 | Errores esperables con mensajes claros en castellano y sin trazas crudas: servidor de MLflow apagado, experimento sin corridas, modelo sin alias `champion`, `modelo_exportado/` inexistente al levantar la API, `GROQ_API_KEY` ausente. |
| RNF-04 | Código según la sección 1.1 del `CLAUDE.md` raíz: funciones cortas de responsabilidad única, constantes con nombre en `src/config.py`, sin duplicación. **Esta unidad no necesita ningún patrón de diseño** (ni siquiera Factory): solo funciones. |
| RNF-05 | Apto como plantilla: no versionar `mlflow.db`, `mlartifacts/`, `mlruns/`, `modelo_exportado/` ni `.env`. |
| RNF-06 | Mensajes por consola cortos y orientados a la etapa (ej. `Corrida registrada: max_depth=3 · accuracy=0.978 · f1_macro=0.978`), para que el estudiante entienda qué pasó sin leer el código. |

## 5. Estructura de carpetas esperada

> La config de Codespaces vive en la raíz del repo (`.devcontainer/unidad3/`), no dentro
> de `unidad3/`. Ver la sección 2 del `CLAUDE.md` raíz.

```
.devcontainer/
└── unidad3/
    └── devcontainer.json      (ya provisto por la cátedra)

unidad3/
├── CLAUDE.md
├── README.md
├── resultados.md              # plantilla que completa el estudiante (sí se versiona)
├── requirements.txt           # entorno del Codespace (todo)
├── requirements-api.txt       # solo lo que necesita la imagen Docker
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── capturas/
│   └── .gitkeep               # el estudiante guarda aquí sus PNG (sí se versionan)
├── docs/
│   └── actividad-unidad3.md   (ya provisto por la cátedra)
└── src/
    ├── __init__.py
    ├── config.py              # única fuente de constantes (sección 7.2)
    ├── servidor_mlflow.py     # verifica que mlflow ui esté corriendo y conecta el cliente
    ├── datos.py               # carga Iris con nombres de columna en castellano y divide train/test
    ├── entrenar.py            # etapa: experimentación
    ├── registrar.py           # etapa: registro de la mejor corrida con alias @champion
    ├── exportar_modelo.py     # etapa: preparar el modelo para servir
    ├── api.py                 # etapa: serving con FastAPI
    └── comparar_prompts.py    # etapa opcional: LLMOps con Groq
```

Archivos generados en tiempo de ejecución (todos en `.gitignore`): `mlflow.db`,
`mlartifacts/`, `modelo_exportado/`.

## 6. Decisiones de diseño ya tomadas (no las reabras salvo indicación de la cátedra)

- **Dataset fijo: Iris** (`sklearn.datasets.load_iris(as_frame=True)`), incluido en
  scikit-learn: no se descarga nada, no hay claves y la API se prueba con 4 números.
  Las columnas se renombran a `largo_sepalo_cm`, `ancho_sepalo_cm`, `largo_petalo_cm`,
  `ancho_petalo_cm` (mapeo constante en `config.py`) para que el contrato de la API sea
  legible y sin espacios.
- **Modelo fijo: árbol de decisión**, hiperparámetro único `max_depth`. Elegido porque el
  efecto es muy visible con la semilla fijada (ver valores de aceptación, sección 8):
  profundidad 1 rinde 66,7 %, profundidad 3 rinde 97,8 % y profundidad 4 baja a 88,9 %
  (sobreajuste). Eso hace evidente por qué se registran **todas** las corridas.
- **MLflow con `mlflow ui` y backend SQLite por defecto** (`mlflow.db` en `unidad3/`).
  No usar `--backend-store-uri` ni *file store*: desde MLflow 3.7 el backend por defecto
  es SQLite y el de archivos quedó en mantenimiento. Los artefactos los sirve el propio
  servidor en `mlartifacts/`.
- **Alias en lugar de stages:** el Registry usa el alias `champion`. `registrar.py`
  reasigna el alias a la nueva versión cada vez que se ejecuta.
- **El modelo llega a la API por exportación, no por red.** `exportar_modelo.py` descarga
  la versión `@champion` a `modelo_exportado/`; la API y la imagen Docker cargan desde
  esa carpeta. Así hay un único camino de carga, la imagen queda autocontenida
  (es "la unidad que se versiona y se despliega" de la consigna 9.c) y el contenedor no
  depende de que `mlflow ui` esté corriendo ni de configurar redes de Docker.
- **Imagen liviana:** el `Dockerfile` instala `requirements-api.txt` con
  `mlflow-skinny` (no `mlflow` completo), que alcanza para `mlflow.pyfunc.load_model`.
- **`entrenar.py` no registra en el Registry**: entrenar y registrar son etapas
  distintas del ciclo de vida y el estudiante debe verlas por separado.
- **Paso opcional de LLMOps sin puntaje**: reutiliza la API key de Groq de la Unidad 1 y
  el mismo modelo (`openai/gpt-oss-20b`, `temperature=0`). No se implementa Gemini en
  esta unidad (un solo camino). Las 6 reseñas y sus etiquetas esperadas son constantes en
  el propio `comparar_prompts.py` (3 positivas y 3 negativas, en castellano rioplatense).
- **Evidencias fuera del código:** el estudiante pega capturas en `capturas/` y completa
  `resultados.md`. El documento Word/PDF lleva solo las consignas 1 a 5 y el enlace.

### Contenido mínimo de `resultados.md` (plantilla en blanco)

Encabezado con nombre del estudiante y fecha; luego una sección por consigna:
6 (captura del entorno), 7 (tabla `Corrida | max_depth | accuracy | f1_macro` con tres
filas vacías, línea "Versión registrada: modelo-u3 v__ (@champion), corrida con
max_depth = __", dos capturas y respuesta 7.d), 8 (tabla `Entrada | Respuesta de la API`
con 4 filas: tres válidas y una inválida, dos capturas y respuesta 8.d), 9 (captura y
respuesta 9.c) y opcional LLMOps (tabla `Plantilla | tasa_exito | tokens_totales |
latencia_media_s`, captura e interpretación). Cada respuesta va como cita en blanco
(`> Escribí acá tu respuesta (3 a 5 líneas).`). Las imágenes se referencian con rutas
relativas sugeridas: `capturas/6_entorno.png`, `capturas/7_comparacion.png`,
`capturas/7_registro.png`, `capturas/8_docs.png`, `capturas/8_predicciones.png`,
`capturas/9_docker.png`, `capturas/opcional_llmops.png`.

### Contenido mínimo de `README.md`

1. Qué vas a hacer (tabla de la sección 2 de este archivo, sin la columna de consignas).
2. Crear el Codespace (fork → Code → Codespaces → "..." → New with options →
   `unidad3-seminario-cd2`, nunca el atajo "Create codespace on main").
3. Experimentar y registrar con MLflow (dos terminales: una para `mlflow ui`, otra para
   los scripts; cómo abrir el puerto 5000 desde la pestaña PORTS).
4. Servir con FastAPI (`exportar_modelo`, `uvicorn`, abrir el puerto 8000 y agregar
   `/docs` al final de la URL).
5. Empaquetar con Docker (detener antes la API local con Ctrl+C para liberar el puerto
   8000; `docker build`, `docker run --rm -p 8000:8000 modelo-u3:1.0`).
6. Paso opcional de LLMOps (`cp .env.example .env`, completar `GROQ_API_KEY`, ejecutar).
7. Errores comunes (tabla mensaje → causa → solución; incluir al menos los de RNF-03 y
   "COPY modelo_exportado: not found" en `docker build`).
8. Completar `resultados.md`, commit y push.

## 7. Notas técnicas verificadas por la cátedra (no cambiar sin volver a probar)

Prototipo completo ejecutado el 19/10/2026 con Python 3.11.17: entrenamiento con
profundidades 1, 3 y 4, registro con alias, exportación, API con `uvicorn` (3
predicciones válidas y una inválida con HTTP 422), entorno limpio con solo
`requirements-api.txt` sirviendo el modelo exportado, y paso de LLMOps contra un
servidor que simula la API de Groq (2 corridas y 8 trazas registradas). La construcción
de la imagen Docker **no se pudo ejecutar** en el entorno de la cátedra (registro de
imágenes bloqueado): debe verificarse en el Codespace (sección 9, tarea 10).

### 7.1 Versiones fijadas

`requirements.txt` (Codespace):

```
mlflow==3.17.1
scikit-learn==1.9.1
pandas==3.0.6
skops==0.16.0
fastapi==0.142.2
uvicorn==0.54.0
groq==1.7.0
python-dotenv==1.2.4
```

`requirements-api.txt` (imagen Docker):

```
mlflow-skinny==3.17.1
scikit-learn==1.9.1
pandas==3.0.6
skops==0.16.0
fastapi==0.142.2
uvicorn==0.54.0
```

FastAPI se fija en 0.142.2 (30/09/2026) a propósito: las versiones posteriores salieron
con días de diferencia y no tienen antigüedad suficiente.

### 7.2 Constantes de `src/config.py`

`MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"`, `EXPERIMENTO_PIPELINE =
"u3-pipeline-iris"`, `EXPERIMENTO_LLMOPS = "u3-llmops-prompts"`, `NOMBRE_MODELO =
"modelo-u3"`, `ALIAS_CAMPEON = "champion"`, `NOMBRE_ARTEFACTO_MODELO = "modelo"`,
`METRICA_PRINCIPAL = "accuracy"`, `SEMILLA = 42`, `PROPORCION_TEST = 0.3`,
`PROFUNDIDAD_POR_DEFECTO = 3`, `CARPETA_MODELO_EXPORTADO = "modelo_exportado"`,
`ARCHIVO_INFO_MODELO = "info_modelo.json"`, el mapeo de columnas y
`ESPECIES = ["setosa", "versicolor", "virginica"]`, `TIPOS_SKOPS_CONFIABLES =
["sklearn.tree._tree.Tree"]`, `TIMEOUT_SALUD_MLFLOW_S = 3`.

### 7.3 Trampas encontradas al prototipar (ya resueltas)

1. **Serialización segura (skops).** MLflow 3.17 guarda los modelos de scikit-learn con
   `skops` y **rechaza el árbol de decisión** si no se declara su tipo interno:
   `mlflow.sklearn.log_model(..., skops_trusted_types=TIPOS_SKOPS_CONFIABLES)`. Al
   cargar con `mlflow.pyfunc.load_model` no hace falta repetirlo (queda en `MLmodel`).
   Comentar en el código, en una línea, por qué existe la constante (es un control de
   seguridad: conecta con la Unidad 2).
2. **Navegador de Codespaces bloqueado.** Desde MLflow 3.5 el servidor rechaza con 403
   ("Invalid Host header") los pedidos que llegan con el dominio `*.app.github.dev` y,
   además, los POST con ese origen ("Cross-origin request blocked"). Se resuelve con
   `MLFLOW_SERVER_ALLOWED_HOSTS` y `MLFLOW_SERVER_CORS_ALLOWED_ORIGINS` en el
   `containerEnv` del devcontainer (ya provisto). Por eso el comando del estudiante es
   simplemente `mlflow ui`, sin opciones. No mover esas variables al README.
3. **Mensajes de ruido.** MLflow 3.17 imprime un aviso `mlflow.agent.hint` al importarse;
   se silencia con `MLFLOW_DISABLE_AGENT_HINT=1` (en el devcontainer y en el
   `Dockerfile` con `ENV`).
4. **Servidor apagado = espera larga.** Si `mlflow ui` no está corriendo, el cliente de
   MLflow reintenta durante minutos. `servidor_mlflow.verificar_servidor()` debe hacer
   antes un `GET {MLFLOW_TRACKING_URI}/health` con `urllib` y timeout corto, y cortar con
   el mensaje: "No encuentro MLflow en http://127.0.0.1:5000. Abrí otra terminal y
   ejecutá: mlflow ui". Lo usan `entrenar`, `registrar`, `exportar_modelo` y
   `comparar_prompts`.
5. **URI del modelo.** Registrar con `mlflow.register_model(f"runs:/{run_id}/modelo",
   NOMBRE_MODELO)` funciona en MLflow 3.17; exportar con
   `mlflow.artifacts.download_artifacts(artifact_uri="models:/modelo-u3@champion",
   dst_path=...)`; versión por alias con
   `MlflowClient().get_model_version_by_alias(...)`.
6. **Groq.** `mlflow.groq.autolog()` existe en 3.17 y genera una traza por llamada. El
   cliente de Groq respeta la variable `GROQ_BASE_URL`, útil para probar sin clave contra
   un servidor simulado. Normalizar la respuesta (minúsculas, sin puntuación) antes de
   compararla con la etiqueta esperada.
7. **Imagen base del devcontainer.** La imagen `python:3.11` pasó a Debian trixie, donde
   la feature `docker-in-docker` no puede instalar Moby; por eso la imagen se fija en
   `3.11-bookworm`.

## 8. Comportamiento esperado y valores de aceptación

Con la semilla y la proporción de test fijadas, `entrenar.py` debe producir exactamente:

| `--max-depth` | accuracy | f1_macro |
|---|---|---|
| 1 | 0.667 | 0.556 |
| 2 | 0.889 | 0.889 |
| 3 | 0.978 | 0.978 |
| 4 | 0.889 | 0.889 |
| 5 | 0.933 | 0.933 |

Predicciones de referencia (modelo de profundidad 3) para `/predict`:

| Entrada (sépalo largo, ancho · pétalo largo, ancho) | Respuesta esperada |
|---|---|
| 5.1, 3.5 · 1.4, 0.2 | `setosa` (clase 0) |
| 6.0, 2.7 · 4.5, 1.4 | `versicolor` (clase 1) |
| 6.9, 3.1 · 5.8, 2.2 | `virginica` (clase 2) |
| `"abc"` en un campo | HTTP 422 con el detalle del campo inválido |

Mensajes de consola de referencia (la guía del estudiante los cita textualmente; además
de estas líneas, MLflow imprime sus propios enlaces "View run" / "View experiment"):

| Script | Última línea esperada |
|---|---|
| `entrenar.py` | `Corrida registrada: max_depth=3 · accuracy=0.978 · f1_macro=0.978` |
| `registrar.py` | `Registrado modelo-u3 versión 1 con alias @champion (corrida arbol_max_depth_3, accuracy=0.978)` |
| `exportar_modelo.py` | `Modelo modelo-u3 v1 (@champion) exportado a modelo_exportado/` |
| `comparar_prompts.py` | una línea por plantilla: `Plantilla zero_shot · tasa_exito=… · tokens=… · latencia_media=… s` |

La guía paso a paso del estudiante (docx de la cátedra) cita estos mismos valores y
comandos: si alguno cambia, avisar a la cátedra para actualizar la guía.

## 9. Tareas a realizar por Claude Code (orden sugerido)

1. Leer este archivo, el `CLAUDE.md` raíz y `docs/actividad-unidad3.md`.
2. Generar `requirements.txt`, `requirements-api.txt`, `.gitignore`, `.dockerignore`
   (excluir `.env`, `mlflow.db`, `mlartifacts/`, `mlruns/`, `__pycache__/`,
   `capturas/`, `docs/`) y `.env.example`.
3. Generar `src/config.py` y `src/servidor_mlflow.py`.
4. Generar `src/datos.py` y `src/entrenar.py`; verificar los valores de la sección 8.
5. Generar `src/registrar.py` y `src/exportar_modelo.py`.
6. Generar `src/api.py`; verificar las cuatro predicciones de referencia y `/docs`.
7. Generar el `Dockerfile` (base `python:3.11-slim`, `ENV MLFLOW_DISABLE_AGENT_HINT=1`,
   copiar primero `requirements-api.txt` e instalar, después `src/` y
   `modelo_exportado/`, `EXPOSE 8000`, `CMD` con `uvicorn --host 0.0.0.0`).
8. Generar `src/comparar_prompts.py` (opcional para el estudiante, obligatorio en la
   plantilla).
9. Generar `resultados.md`, `capturas/.gitkeep` y `README.md` según la sección 6.
10. Validar en un Codespace real creado con la config `unidad3-seminario-cd2`: abrir la
    UI de MLflow desde el navegador (puerto 5000), recorrer los comandos de la sección 2,
    construir y correr la imagen Docker, y repetir una predicción contra el contenedor.
11. Actualizar la sección 10 de este archivo con el resultado de la validación.

## 10. Estado de la implementación

Plantilla validada el 19/10/2026 en un Codespace real con la configuración
`unidad3-seminario-cd2` (imagen `python:3.11-bookworm`). Se verificaron:

- UI de MLflow abierta desde el navegador (puerto 5000, pestaña PORTS).
- Entrenamiento con `--max-depth 1` y `--max-depth 3`; métricas coinciden con §8.
- Registro del modelo con alias `@champion` (`python -m src.registrar`).
- Exportación del modelo a `modelo_exportado/` (`python -m src.exportar_modelo`).
- API en `/docs` con predicciones correctas y HTTP 422 ante dato inválido.
- Construcción y ejecución de la imagen Docker (`modelo-u3:1.0`); predicción repetida
  contra el contenedor con resultado idéntico al de la API local.

Pendiente de validar en Codespace: paso opcional de LLMOps (`comparar_prompts.py`).

## 11. Fuera de alcance (no generar)

- Kubernetes, Airflow, Prefect, Dagster, Triton o BentoML: se estudian y se justifican en
  las consignas teóricas, no se ejecutan.
- Monitoreo de drift, Prometheus o Grafana: la consigna 5 los trata de forma conceptual.
- Implementar blue-green, canary o A/B testing: la consigna 9.c pide solo explicarlo.
- Elección de dataset propio, de otro algoritmo o de Gemini: contradice el principio de
  un solo camino.
- RAG o agentes: corresponden a la Unidad 4.
- Tests automatizados extensos: alcanza con que cada script sea ejecutable y legible.
