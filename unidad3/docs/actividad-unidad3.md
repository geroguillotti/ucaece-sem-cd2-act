# Actividad Formativa — Unidad 3: Tendencias Actuales en Implementación y Despliegue de Modelos (MLOps/LLMOps)

Texto de referencia completo de la actividad, para que Claude Code tenga trazabilidad
exacta con el documento oficial de cátedra. Este archivo es importado desde `CLAUDE.md`
mediante `@docs/actividad-unidad3.md`.

**CARRERA:** Licenciatura en Ciencia de Datos
**MATERIA:** Seminario de Ciencia de Datos II
**CUATRIMESTRE Y AÑO:** 2do Cuatrimestre 2026
**PROFESOR/A:** Miguel Méndez Garabetti, Eduardo Piray
**UNIDAD N° 3:** Tendencias Actuales en Implementación y Despliegue de Modelos (MLOps/LLMOps)
**ACTIVIDAD FORMATIVA:** Trabajo Práctico Individual. Diseño de un pipeline de
MLOps/LLMOps para producción.

## Indicaciones generales

El archivo debe tener una portada con: nombre, número de matrícula/usuario, carrera,
materia y profesor. La entrega es individual y debe realizarse en el tiempo y espacio
estipulado por el docente. La denominación del archivo debe seguir el formato:
Apellido, inicial del nombre, materia, número de unidad y actividad (ej.
`PérezM_SemCD2_Un3_Act3`).

La calificación de la actividad podrá realizarse de manera numérica, con un 4 (cuatro)
como nota mínima de aprobación, o de manera cualitativa (Aprobado/Desaprobado).

## Requisitos formales de presentación

El trabajo debe presentarse en formato Word o PDF, con tipografía Arial 11, interlineado
1,5, alineación justificada y márgenes estándar. Si se incluyen citas o fuentes
consultadas, deben referenciarse en formato APA. Extensión sugerida: entre 4 y 6 páginas
(sin contar portada ni bibliografía).

## Criterios de evaluación

- Comprensión e interpretación de la consigna formulada.
- Dominio adecuado de los temas abordados.
- Aplicación de la teoría a situaciones prácticas.
- Manejo del vocabulario específico.
- Pertinencia y claridad en la redacción.
- Estilo académico, correcta construcción gramatical, puntuación y acentuación.
- Cumplimiento de las pautas de presentación de trabajos escritos.

## Consignas teóricas (texto original de cátedra, sin modificar)

1. A partir del caso de uso definido en la actividad de la Unidad 1 (o de uno nuevo si el
   docente lo indica), diseñar el ciclo de vida completo del modelo en producción:
   experimentación, validación, empaquetado, despliegue y monitoreo con eventual
   re-entrenamiento.

2. Seleccionar y justificar las herramientas de tracking y versionado (por ejemplo
   MLflow, Weights & Biases o DVC) y de orquestación (por ejemplo Docker y Kubernetes,
   junto con Airflow, Prefect o Dagster) más adecuadas para el caso elegido.

3. Diseñar la estrategia de serving del modelo: framework elegido (por ejemplo FastAPI,
   BentoML o Triton Inference Server), tipo de API (REST, gRPC o streaming) y estrategia
   de despliegue de nuevas versiones (blue-green, canary release o A/B testing),
   justificando la elección en función del caso de uso.

4. Justificar la elección de hardware de inferencia (GPU cloud, dispositivo edge,
   cuantización, etc.) considerando un análisis costo-beneficio y las métricas de latencia
   y throughput relevantes para el caso (TTFT, TBT, tokens por segundo, según
   corresponda).

5. Definir un plan de monitoreo en producción: qué métricas de drift y de observabilidad
   se relevarían, con qué herramientas, y qué estrategia de re-entrenamiento (periódica,
   gatillada por drift o continua) se aplicaría.

## Componente práctico (versión simplificada, octubre 2026)

Las consignas 1 a 5 diseñan el pipeline para tu propio caso de uso. En esta parte vas a
recorrer, de forma guiada y ejecutable, un pipeline mínimo de MLOps sobre un caso de
demostración común a todo el curso (clasificación de flores del dataset Iris):
experimentar, registrar, servir y empaquetar un modelo. **El código ya está provisto por
la cátedra:** tu trabajo es ejecutar cada etapa, observar lo que produce e interpretar los
resultados. La *Guía paso a paso para el estudiante* acompaña cada consigna con los
comandos exactos. Todo corre en GitHub Codespaces, sin costo y sin GPU.

Las evidencias de esta parte (capturas y respuestas breves) se registran en el archivo
`resultados.md` del repositorio; el documento Word/PDF contiene las consignas 1 a 5 y el
enlace al repositorio.

### 6. Preparación del entorno (Codespaces)

a. Hacer un fork del repositorio de la cátedra (si ya lo tenés de unidades anteriores,
   actualizarlo con **Sync fork**).

b. Crear el Codespace de la Unidad 3: **Code → Codespaces → "..." → New with options →**
   configuración `unidad3-seminario-cd2`. Las dependencias (MLflow, scikit-learn,
   FastAPI y Docker) quedan instaladas automáticamente.

c. Verificar el entorno (`python --version` y `docker --version`) y guardar una captura.

### 7. Experimentación y registro con MLflow (consignas 1 y 2)

a. Levantar la interfaz de MLflow (`mlflow ui`) y abrirla en el navegador.

b. Entrenar el modelo al menos dos veces, cambiando solo la profundidad máxima del árbol
   de decisión (por ejemplo `1` y `3`). Cada corrida queda registrada automáticamente con
   sus parámetros, sus métricas y el modelo entrenado.

c. Comparar las corridas en la interfaz de MLflow y registrar la mejor con el script
   provisto: queda como una versión del modelo `modelo-u3` con el alias `@champion`.

d. Guardar capturas de la comparación de corridas y del modelo registrado, y explicar en
   3 a 5 líneas qué diferencia observaste entre las corridas y por qué conviene
   registrarlas todas, incluso las peores (vínculo con la consigna 2).

### 8. Serving con FastAPI (consigna 3)

a. Exportar el modelo marcado como `@champion` y levantar la API con `uvicorn`.

b. Abrir la documentación automática de la API (`/docs`) e identificar su contrato: qué
   datos recibe y qué devuelve.

c. Realizar al menos tres predicciones válidas (idealmente una por especie) y una con un
   dato inválido; guardar las capturas.

d. Explicar en 3 a 5 líneas qué hace la API cuando recibe un dato inválido y por qué ese
   comportamiento es importante en producción.

### 9. Containerización con Docker (consignas 2 y 3)

a. Construir la imagen `modelo-u3:1.0` a partir del `Dockerfile` provisto y ejecutar el
   contenedor.

b. Repetir una predicción contra la API que corre dentro del contenedor y guardar la
   captura.

c. Explicar en 3 a 5 líneas cómo, si existiera una versión `modelo-u3:1.1`, estas imágenes
   permitirían aplicar la estrategia de despliegue elegida en la consigna 3 (blue-green,
   canary o A/B testing), sin necesidad de implementarla.

### 10. Registro y entrega

a. Completar el archivo `resultados.md` de la carpeta `unidad3/` (tabla de corridas,
   versión registrada, capturas y respuestas breves de las consignas 7.d, 8.d y 9.c).

b. Subir los cambios al repositorio (commit y push) e incluir el enlace en el documento
   Word/PDF de la entrega.

### Paso opcional (sin puntaje): una experiencia de LLMOps

Comparar dos plantillas de prompt (zero-shot y few-shot) para clasificar el sentimiento
de reseñas breves, usando la API key gratuita de Groq de la Unidad 1. El script provisto
registra en MLflow la tasa de aciertos, los tokens consumidos y la latencia de cada
plantilla, y guarda la traza de cada llamada al modelo. Si lo realizás, agregá en
`resultados.md` una captura y 2 o 3 líneas de interpretación. Este paso no suma ni resta
puntos.

## Calificación de la actividad

La actividad se calificará de manera cuantitativa, sobre un total de 10 puntos
distribuidos entre las consignas, siendo 4 (cuatro) puntos la nota mínima de aprobación.

| Bloque | Consigna | Puntaje |
| --- | --- | --- |
| Teoría (5 pts) | 1. Ciclo de vida completo (experimentación → re-entrenamiento) | 1 |
| | 2. Selección y justificación de tracking/versionado y orquestación | 1 |
| | 3. Diseño de la estrategia de serving | 1 |
| | 4. Justificación de hardware de inferencia | 1 |
| | 5. Plan de monitoreo y re-entrenamiento | 1 |
| Práctica (5 pts) | 6. Preparación del entorno (Codespaces) | 0,5 |
| | 7. Experimentación y registro con MLflow | 1,5 |
| | 8. Serving con FastAPI | 1,5 |
| | 9. Containerización con Docker | 1 |
| | 10. Registro y entrega | 0,5 |
| | Paso opcional de LLMOps | sin puntaje |
| **Total** | | **10** |
