# Actividad Formativa — Unidad 2: Calidad, Seguridad y Mejores Prácticas

**CARRERA:** Licenciatura en Ciencia de Datos
**MATERIA:** Seminario de Ciencia de Datos II
**CUATRIMESTRE Y AÑO:** 2do Cuatrimestre 2026
**PROFESOR/A:** Miguel Méndez Garabetti, Eduardo Piray
**UNIDAD N° 2:** Calidad, Seguridad y Mejores Prácticas en Desarrollos con Ciencia de Datos
**ACTIVIDAD FORMATIVA:** Análisis de Caso Individual. Evaluación de calidad, sesgos y seguridad en un sistema de IA real.

## Indicaciones generales

El archivo debe tener una portada con: nombre, número de matrícula/usuario, carrera,
materia y profesor. La entrega es individual y debe realizarse en el tiempo y espacio
estipulado por el docente. La denominación del archivo debe seguir el formato:
Apellido, inicial del nombre, materia, número de unidad y actividad (ej.
`PérezM_SemCD2_Un2_Act2`).

La calificación de la actividad podrá realizarse de manera numérica, con un 4 (cuatro)
como nota mínima de aprobación, o de manera cualitativa (Aprobado/Desaprobado).

## Requisitos formales de presentación

El trabajo debe presentarse en formato Word o PDF, con tipografía Arial 11, interlineado
1,5, alineación justificada y márgenes estándar. Si se incluyen citas o fuentes
consultadas, deben referenciarse en formato APA. Extensión sugerida: entre 3 y 4 páginas
(sin contar portada ni bibliografía).

## Criterios de evaluación

- Comprensión e interpretación de la consigna formulada.
- Dominio adecuado de los temas abordados.
- Aplicación de la teoría a situaciones prácticas.
- Manejo del vocabulario específico.
- Pertinencia y claridad en la redacción.
- Estilo académico, correcta construcción gramatical, puntuación y acentuación.
- Cumplimiento de las pautas de presentación de trabajos escritos.

## Consignas teóricas

1. Seleccionar uno de los siguientes casos reales documentados en la bibliografía de la
   unidad: (a) el estudio Gender Shades sobre disparidades raciales y de género en
   sistemas comerciales de reconocimiento facial (Buolamwini & Gebru, 2018), o (b) el
   sistema de reclutamiento automatizado discontinuado por Amazon al detectarse que
   penalizaba sistemáticamente a candidatas mujeres (Dastin, 2018). También puede
   proponerse otro caso real de falla de un sistema de IA, sujeto a aprobación previa
   del docente.

2. Describir brevemente el sistema de IA involucrado en el caso elegido, su objetivo
   original y el contexto de uso en el que fue desplegado.

3. Identificar qué evidencia de sesgo o inequidad se documentó en el caso, explicando su
   origen (datos de entrenamiento, diseño del modelo, o ambos) con apoyo en los
   conceptos de la unidad (orígenes de sesgos, métricas de equidad).

4. Analizar qué técnicas de explicabilidad (XAI) o de auditoría de sesgos desarrolladas
   en la unidad (por ejemplo SHAP, LIME o métricas de equidad específicas) podrían
   haberse aplicado de forma preventiva para detectar el problema antes del despliegue
   en producción.

5. Evaluar el caso a la luz de al menos un marco de IA responsable o regulatorio
   desarrollado en la unidad (por ejemplo los principios de IA responsable o el EU AI
   Act), explicando qué categoría de riesgo u obligación aplicaría al sistema analizado.

6. Proponer al menos tres mejoras concretas, técnicas y/o de gobernanza, que podrían
   haber evitado o mitigado el problema identificado.

## Componente práctico

### Consignas prácticas

Las consignas 1 a 6 definieron el análisis conceptual de un caso real de falla de un
sistema de IA. A continuación se solicita verificar de forma cuantitativa y reproducible
el sesgo identificado en ese caso, siguiendo los pasos detallados debajo. Todo el
entorno de trabajo es gratuito y no requiere hardware propio de alta capacidad: el
cómputo ocurre en la nube (GitHub Codespaces), nunca en la máquina local.

**7. Preparación del entorno de trabajo**

a. Crear un repositorio en GitHub para la actividad (puede partir de la plantilla
provista por la cátedra, mediante "Use this template" o fork al repositorio compartido
oportunamente por los tutores de la cátedra).

b. Abrir el repositorio en GitHub Codespaces (Code → Codespaces → Create codespace on
main).

c. Instalar dentro del Codespace las dependencias necesarias (`fairlearn`,
`scikit-learn`, `shap`, `pandas`), registrando las versiones exactas en un archivo
`requirements.txt`.

**8. Selección del dataset y reproducción cuantitativa del sesgo (consigna 3)**

a. Seleccionar un dataset público, tabular, con al menos un atributo sensible
identificable (por ejemplo género, raza o edad) y coherente con el caso elegido en la
consigna 1. La elección del dataset queda sujeta a aprobación previa del docente, del
mismo modo que la elección del caso en la consigna 1.

b. Entrenar un clasificador simple (regresión logística o árbol de decisión) sobre ese
dataset.

c. Calcular con la librería Fairlearn al menos dos métricas de equidad desagregadas por
el atributo sensible elegido (por ejemplo, demographic parity difference y equalized
odds difference).

d. Guardar los resultados obtenidos y su interpretación en un archivo `evidencias.md`,
vinculándolos explícitamente con el sesgo documentado en el caso real analizado en la
consigna 3.

**9. Mitigación del sesgo con Fairlearn (consigna 4)**

a. Aplicar sobre el mismo modelo una técnica de mitigación de la librería Fairlearn
(`ExponentiatedGradient` o `ThresholdOptimizer`).

b. Recalcular las mismas métricas de equidad utilizadas en el punto 8 luego de la
mitigación.

c. Reportar en `evidencias.md` una tabla comparativa antes/después, discutiendo qué tan
efectiva resultó la mitigación aplicada y qué limitaciones se observaron.

**10. Explicabilidad del modelo (consigna 4)**

a. Aplicar la librería SHAP sobre el modelo entrenado en el punto 8 para explicar al
menos dos predicciones individuales (una donde el modelo discrimine y otra donde no).

b. Vincular explícitamente esta evidencia, en el documento entregado, con la discusión
de la consigna 4 sobre qué técnica de XAI podría haber detectado el problema de forma
preventiva antes del despliegue.

**11. Registro y entrega**

a. Realizar los commits correspondientes al código y las evidencias generadas.

b. Redactar en el propio repositorio un `README.md` breve que describa el dataset
utilizado, el atributo sensible analizado, las métricas de equidad obtenidas antes y
después de la mitigación, y cómo ejecutar el script.

c. Incluir en el documento entregado (Word/PDF) el enlace de acceso al repositorio de
GitHub.

## Calificación de la actividad

La actividad se calificará de manera cuantitativa, sobre un total de 10 puntos
distribuidos entre las consignas, siendo 4 (cuatro) puntos la nota mínima de aprobación.
La distribución de puntaje por consigna es la siguiente:

| Bloque | Consigna | Puntaje |
| --- | --- | --- |
| Teoría (5 pts) | 1. Selección del caso | 0,5 |
| | 2. Descripción del sistema y contexto | 0,5 |
| | 3. Identificación de evidencia de sesgo/inequidad | 1 |
| | 4. Técnicas de XAI/auditoría preventivas | 1 |
| | 5. Evaluación bajo marco de IA responsable/regulatorio | 1 |
| | 6. Propuesta de mejoras | 1 |
| Práctica (5 pts) | 7. Preparación del entorno (Codespaces) | 0,5 |
| | 8. Reproducción cuantitativa del sesgo (Fairlearn) | 1,5 |
| | 9. Mitigación del sesgo (Fairlearn, antes/después) | 2 |
| | 10. Explicabilidad (SHAP) | 0,75 |
| | 11. Registro, README y entrega del enlace | 0,25 |
| **Total** | | **10** |
