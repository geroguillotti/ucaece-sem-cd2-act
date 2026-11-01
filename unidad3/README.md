# Unidad 3 — MLOps/LLMOps: pipeline completo sobre Iris

En esta actividad vas a recorrer, comando por comando, las etapas del ciclo de vida de un
modelo de clasificación sobre el dataset Iris (incluido en scikit-learn, sin descargas ni
configuración extra).

| Etapa del ciclo de vida | Comando |
|---|---|
| Entorno reproducible | Crear el Codespace `unidad3-seminario-cd2` |
| Experimentación | `python -m src.entrenar --max-depth 1` y `--max-depth 3` |
| Registro (Model Registry) | `python -m src.registrar` |
| Serving | `python -m src.exportar_modelo` y `uvicorn src.api:app --port 8000` |
| Empaquetado y despliegue | `docker build -t modelo-u3:1.0 .` y `docker run` |
| LLMOps (opcional) | `python -m src.comparar_prompts` |

---

## 1. Crear el Codespace

1. Hacé un fork del repositorio de la cátedra (si ya lo tenés de unidades anteriores,
   actualizalo con **Sync fork**).
2. En tu fork: **Code → Codespaces → "..." (tres puntos) → New with options**.
3. En "Dev container configuration" elegí **`unidad3-seminario-cd2`** y creá el Codespace.
   (No uses el atajo "Create codespace on main": no garantiza qué configuración usa cuando
   hay varias disponibles.)
4. Las dependencias (MLflow, scikit-learn, FastAPI y Docker) quedan instaladas
   automáticamente.

---

## 2. Experimentar y registrar con MLflow

Necesitás dos terminales abiertas en el Codespace.

**Terminal 1 — levantar el servidor de MLflow:**

```bash
mlflow ui
```

Cuando aparezca el mensaje `Uvicorn running on http://127.0.0.1:5000`, abrí la pestaña **PORTS**,
buscá el puerto 5000 y hacé clic en el globo para abrirlo en el navegador.

**Terminal 2 — entrenar y registrar:**

```bash
python -m src.entrenar --max-depth 1
python -m src.entrenar --max-depth 3
python -m src.registrar
```

Cada ejecución de `entrenar` crea una corrida en el experimento `u3-pipeline-iris` con
sus parámetros, métricas y el modelo. `registrar` busca la corrida con mayor accuracy y
la guarda como versión `modelo-u3 v1` con el alias `@champion`.

---

## 3. Servir con FastAPI

Desde la Terminal 2 (con el servidor de MLflow corriendo en la 1):

```bash
python -m src.exportar_modelo
uvicorn src.api:app --port 8000
```

Cuando aparezca `Application startup complete`, abrí la pestaña **PORTS**, buscá el
puerto 8000 y hacé clic en el globo. Al final de la URL del navegador agregá `/docs`
para ver la documentación interactiva de la API.

Desde `/docs` podés probar `POST /predict` con los valores del ejemplo precargado o con
tus propios valores. Probá también enviar `"abc"` en un campo numérico para ver el error
HTTP 422.

---

## 4. Empaquetar con Docker

Antes de construir la imagen, **detené la API** con `Ctrl+C` en la Terminal 2 para
liberar el puerto 8000. El servidor de MLflow puede seguir corriendo.

```bash
docker build -t modelo-u3:1.0 .
docker run --rm -p 8000:8000 modelo-u3:1.0
```

Abrí la pestaña **PORTS**, puerto 8000, y repetí una predicción desde `/docs` para
confirmar que la API funciona dentro del contenedor.

---

## 5. Paso opcional: LLMOps con Groq

Este paso requiere una API key gratuita de Groq (la misma de la Unidad 1).

```bash
cp .env.example .env
# Editá .env y completá GROQ_API_KEY=tu_clave_aquí
python -m src.comparar_prompts
```

El script compara dos plantillas de prompt (zero-shot y few-shot) para clasificar el
sentimiento de reseñas breves. Registra métricas y trazas en el experimento
`u3-llmops-prompts`, visible en la UI de MLflow.

---

## 6. Completar `resultados.md` y entregar

1. Completá las tablas y respuestas breves en `resultados.md`.
2. Guardá las capturas de pantalla en `capturas/` con los nombres sugeridos en el archivo.
3. Hacé commit y push:

```bash
git add resultados.md capturas/
git commit -m "Agrego resultados y capturas unidad 3"
git push
```

4. Incluí el enlace al repositorio en el documento Word/PDF de tu entrega.

---

## 7. Errores comunes

| Mensaje | Causa | Solución |
|---|---|---|
| `No encuentro MLflow en http://127.0.0.1:5000` | El servidor de MLflow no está corriendo | Abrí otra terminal y ejecutá `mlflow ui` |
| `No encontré el experimento 'u3-pipeline-iris'` | No hay corridas todavía | Ejecutá primero `python -m src.entrenar` |
| `No hay corridas en 'u3-pipeline-iris'` | El experimento existe pero está vacío | Ejecutá primero `python -m src.entrenar` |
| `No encontré el modelo 'modelo-u3' con alias @champion` | El modelo no fue registrado | Ejecutá primero `python -m src.registrar` |
| `No encontré 'modelo_exportado/'` | La carpeta del modelo exportado no existe | Ejecutá primero `python -m src.exportar_modelo` |
| `No encontré GROQ_API_KEY` | Falta la variable de entorno | Copiá `.env.example` a `.env` y completá tu clave |
| `COPY modelo_exportado: not found` en `docker build` | La carpeta no existe al construir la imagen | Ejecutá `python -m src.exportar_modelo` antes del build |
| `403` o `Invalid Host header` al abrir MLflow en el navegador | El Codespace no fue creado con la configuración `unidad3-seminario-cd2` | Recreá el Codespace eligiendo `unidad3-seminario-cd2` en New with options |
| `port is already allocated` en `docker run` | La API local sigue corriendo y ocupa el puerto 8000 | Detené la API con `Ctrl+C` antes de ejecutar `docker run` |
| `Cannot connect to the Docker daemon` | El servicio de Docker aún no terminó de iniciar | Esperá un minuto y reintentá, o recreá el Codespace con la configuración `unidad3-seminario-cd2` |
| `Unable to find image 'modelo-u3:1.0' locally` / `pull access denied` en `docker run` | La imagen no fue construida | Ejecutá `docker build -t modelo-u3:1.0 .` desde `unidad3/` y esperá a que termine sin `ERROR` |
