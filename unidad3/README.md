# Unidad 3: Pipeline de MLOps con MLflow, FastAPI y Docker

Entrega individual de Geronimo Guillotti para el Seminario de Ciencia de Datos II (Licenciatura en
Ciencia de Datos, CAECE), 2.º cuatrimestre de 2026.

Este directorio contiene el componente práctico (consignas 6 a 10) de la Actividad Formativa 3. El
diseño del pipeline de producción para el caso de la Unidad 1, el asistente de primera respuesta de una
clínica odontológica (consignas 1 a 5), está en el informe entregado por el campus. Se partió de la
plantilla de la cátedra, cuyas instrucciones originales quedaron en
[`docs/README_plantilla_catedra.md`](docs/README_plantilla_catedra.md).

## Qué se hizo

El caso de demostración es el común a todo el curso: clasificar las tres especies del dataset Iris con un
árbol de decisión. Se recorrieron las etapas del ciclo de vida con el código de la plantilla:

| Etapa | Qué se hizo | Resultado |
|---|---|---|
| Experimentación | Cinco corridas de `src.entrenar` con `max_depth` de 1 a 5 en el experimento `u3-pipeline-iris` de MLflow | La mejor corrida es la de `max_depth` = 3 |
| Registro | `src.registrar` busca la corrida con mayor accuracy y la guarda en el Model Registry | `modelo-u3` v1 con el alias `@champion` |
| Serving | `src.exportar_modelo` descarga el modelo `@champion` a `modelo_exportado/` y `src.api` lo expone con FastAPI | `POST /predict` con validación de la entrada |
| Empaquetado | `docker build` con el Dockerfile de la plantilla | Imagen `modelo-u3:1.0` que responde igual que la API local |

## Resultados

Métricas sobre el conjunto de test (45 flores, 15 por especie, separadas con semilla 42):

| Corrida | max_depth | accuracy | f1_macro |
|---|---|---|---|
| arbol_max_depth_1 | 1 | 0,667 | 0,556 |
| arbol_max_depth_2 | 2 | 0,889 | 0,889 |
| arbol_max_depth_3 | 3 | 0,978 | 0,978 |
| arbol_max_depth_4 | 4 | 0,889 | 0,889 |
| arbol_max_depth_5 | 5 | 0,933 | 0,933 |

Con un solo corte el árbol separa setosa pero confunde versicolor con virginica. Con profundidad 3 falla
una sola flor de las 45, y más profundidad no ayuda: con 4 y 5 el árbol se ajusta a detalles del
entrenamiento y empeora en test. La API respondió setosa, versicolor y virginica a una flor típica de cada
especie, y devolvió 422 sin llegar al modelo ante un valor no numérico y dos campos faltantes. El
contenedor dio la misma predicción que la API local. En el paso opcional de LLMOps, las plantillas zero-shot y few-shot
acertaron las seis reseñas de prueba y few-shot consumió 78 tokens más.

## Cómo ejecutar

1. **Entorno.** En GitHub: Code, Codespaces, menú de los tres puntos, New with options, y en Dev
   container configuration la opción `unidad3-seminario-cd2`. La terminal abre en `unidad3/` con
   Python 3.11, Docker y las dependencias de [`requirements.txt`](requirements.txt) instaladas, con
   versiones fijas: mlflow 3.17.1, scikit-learn 1.9.1, fastapi 0.142.2 y uvicorn 0.54.0.
2. **Servidor de MLflow.** En una primera terminal, que queda ocupada; la interfaz se abre desde la
   pestaña Puertos, en el puerto 5000:
   ```bash
   mlflow ui
   ```
3. **Experimentación y registro.** En una segunda terminal:
   ```bash
   for d in 1 2 3 4 5; do python -m src.entrenar --max-depth $d; done
   python -m src.registrar
   ```
4. **Serving.** La documentación interactiva queda en `/docs` del puerto 8000:
   ```bash
   python -m src.exportar_modelo
   uvicorn src.api:app --port 8000
   ```
5. **Docker.** Con la API local detenida (Ctrl+C) para liberar el puerto 8000:
   ```bash
   docker build -t modelo-u3:1.0 .
   docker run --rm -p 8000:8000 modelo-u3:1.0
   ```
6. **LLMOps (opcional).** Necesita una API key de Groq, cargada como secreto de Codespaces con el nombre
   `GROQ_API_KEY` o en un archivo `.env` creado a partir de `.env.example`. Con MLflow corriendo:
   ```bash
   python -m src.comparar_prompts
   ```

`mlflow.db`, `mlartifacts/` y `modelo_exportado/` se generan al ejecutar estos pasos y no se versionan.

## Evidencias

- [`resultados.md`](resultados.md): tabla de corridas, versión registrada, predicciones de la API y
  respuestas breves de las consignas 7.d, 8.d y 9.c.
- [`capturas/`](capturas/): entorno, comparación de corridas y modelo registrado en MLflow,
  documentación y predicciones de la API, predicción contra el contenedor y comparación de prompts con
  sus trazas.

## Cambios respecto de la plantilla

No se modificó el código de `src/` ni el Dockerfile. La guía y el README de la cátedra se movieron a
`docs/`, y se agregaron este README, las capturas y `resultados.md` completo.
