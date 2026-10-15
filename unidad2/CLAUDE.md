# CLAUDE.md — Unidad 2: Calidad, Seguridad y Mejores Prácticas

Este archivo brinda contexto persistente a Claude Code para asistir en la generación del
repositorio base de la actividad práctica de la **Unidad 2 — Calidad, Seguridad y Mejores
Prácticas**, del Seminario de Ciencia de Datos II.

> Este archivo complementa al `CLAUDE.md` raíz del repositorio, donde están definidas las
> restricciones de diseño comunes a todas las unidades (sección 1) y la política de
> calidad de código obligatoria (sección 1.1). No se repiten aquí; ambos archivos deben
> leerse en conjunto.

Este repositorio (carpeta `unidad2/`) es la **plantilla base** que luego usarán los
estudiantes (vía "Use this template" o fork) para completar su propia entrega individual.

**Consigna completa de la actividad (texto oficial de cátedra, consignas 1-6, componente
práctico 7-11 y calificación):**
@docs/actividad-unidad2.md

*(Colocar el archivo `actividad-unidad2.md` dentro de una carpeta `docs/` en la raíz de
`unidad2/` para que este import se resuelva correctamente.)*

---

## 1. Contexto académico

- **Asignatura:** Seminario de Ciencia de Datos II.
- **Unidad:** Unidad 2 — Calidad, Seguridad y Mejores Prácticas en Desarrollos con
  Ciencia de Datos.
- **Actividad:** Análisis de Caso Individual — Evaluación de calidad, sesgos y seguridad
  en un sistema de IA real.
- **Rol de este repositorio:** plantilla base para el componente práctico de la actividad
  (consignas 7 a 11 del documento de la cátedra). Las consignas 1 a 6 (selección del caso,
  descripción del sistema, evidencia de sesgo, técnicas de XAI/auditoría preventivas,
  evaluación bajo marco de IA responsable, propuesta de mejoras) son de resolución
  conceptual y no generan código; este repositorio cubre exclusivamente la verificación
  cuantitativa y reproducible de esos argumentos.

## 2. Objetivo del repositorio

Proveer una estructura de proyecto lista para usar en **GitHub Codespaces**, sin
instalación local ni GPU, que le permita a cada estudiante:

1. Reproducir cuantitativamente, sobre un dataset propio (aprobado por el docente y
   coherente con el caso real elegido en la consigna 1), el tipo de sesgo documentado en
   ese caso.
2. Aplicar una técnica de mitigación de Fairlearn y comparar las métricas de equidad
   antes y después.
3. Aplicar SHAP para explicar predicciones individuales del modelo, conectando con la
   discusión de la consigna 4 sobre auditoría preventiva.
4. Ejecutar todo el flujo de forma reproducible, documentar evidencias y entregar un
   enlace de repositorio.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|----|----|
| RF-01 | El proyecto debe soportar la carga de un dataset tabular arbitrario (CSV), definido por el estudiante mediante variables de entorno (`DATASET_PATH`, `TARGET_COLUMN`, `SENSITIVE_ATTRIBUTE`, `POSITIVE_LABEL`), sin hardcodear ningún dataset específico en el código. Si `DATASET_PATH` no está definido, el proyecto debe correr igual usando un dataset público de demostración descargado en runtime (`fairlearn.datasets.fetch_adult`), para que el repo sea ejecutable de punta a punta sin configuración previa. |
| RF-02 | Debe entrenarse un clasificador simple (regresión logística por defecto) sobre el dataset configurado, con separación train/test reproducible (semilla fija). |
| RF-03 | Debe calcularse, con **Fairlearn**, al menos dos métricas de equidad desagregadas por el atributo sensible configurado (como mínimo *demographic parity difference* y *equalized odds difference*), previas a cualquier mitigación. |
| RF-04 | El proyecto debe soportar al menos dos técnicas de mitigación de Fairlearn intercambiables (`ExponentiatedGradient` y `ThresholdOptimizer`), seleccionables por variable de entorno (`MITIGATION_METHOD`, incluyendo un valor `ambos` que corre y compara las dos en la misma ejecución), y una restricción de equidad seleccionable (`FAIRNESS_CONSTRAINT`: `demographic_parity` | `equalized_odds`), sin duplicar lógica de negocio entre técnicas. |
| RF-05 | Deben recalcularse las mismas métricas de equidad del RF-03 luego de aplicar la mitigación, y reportarse en una tabla comparativa antes/después. |
| RF-06 | Debe aplicarse **SHAP** sobre el modelo base (pre-mitigación) para explicar al menos dos predicciones individuales: una donde el modelo discrimine según el atributo sensible y otra donde no. La selección de ambas predicciones debe ser automática (mayor y menor contribución absoluta del atributo sensible), no manual. |
| RF-07 | Todos los resultados (métricas antes/después, comparación de mitigación, explicaciones SHAP) deben volcarse automáticamente a un archivo `evidencias.md`, más los gráficos correspondientes como PNG en `outputs/` (comparación de métricas, waterfall de cada predicción explicada, resumen global SHAP), listos para pegar en el informe Word/PDF de la entrega. |
| RF-08 | Debe incluirse un `README.md` con instrucciones claras de uso, pensado para que un estudiante sin experiencia previa en Codespaces pueda seguirlo paso a paso. |
| RF-09 | Debe incluirse un archivo `.env.example` (sin valores reales) que documente las variables de entorno esperadas (`DATASET_PATH`, `TARGET_COLUMN`, `SENSITIVE_ATTRIBUTE`, `POSITIVE_LABEL`, `MITIGATION_METHOD`, `FAIRNESS_CONSTRAINT`). |

## 4. Requerimientos no funcionales

| ID | Requerimiento |
|----|----|
| RNF-01 | El entorno debe levantar completamente funcional en GitHub Codespaces sin pasos manuales de instalación (usar `.devcontainer/devcontainer.json` con `postCreateCommand` que instale dependencias de `requirements.txt`). |
| RNF-02 | El código debe correr íntegramente en CPU básica de Codespaces; no se requiere GPU ni Google Colab para esta unidad (a diferencia de la Unidad 1). |
| RNF-03 | El manejo de errores debe ser explícito y con mensajes claros (ej.: dataset no encontrado, columna objetivo o atributo sensible inexistente en el dataset, método de mitigación no soportado), evitando fallos silenciosos o trazas crudas no explicadas. |
| RNF-04 | El código debe seguir la política de calidad definida en la **sección 1.1 del `CLAUDE.md` raíz**: funciones cortas de responsabilidad única, nombres autoexplicativos, sin "magic numbers/strings" sin constante nombrada, y separación simple entre orquestación, entrenamiento, auditoría de equidad, mitigación y explicabilidad, sin sobre-ingeniería. |
| RNF-05 | El repositorio debe quedar apto para convertirse en **template repository** de GitHub (estructura limpia, sin artefactos de ejecución, sin datos personales ni datasets reales de otro estudiante versionados). |

## 5. Estructura de carpetas esperada

> **Nota sobre el devcontainer:** este repositorio es un monorepo con una carpeta por
> unidad, así que la config de Codespaces de Unidad 2 **no vive dentro de `unidad2/`**,
> sino en la raíz del repo bajo `.devcontainer/unidad2/devcontainer.json`, replicando el
> mismo patrón de "múltiples configuraciones" ya usado en la Unidad 1. Ver la sección 2
> del `CLAUDE.md` raíz para el detalle.

```
.devcontainer/
└── unidad2/
    └── devcontainer.json   (vive en la raíz del repo, no dentro de unidad2/)

unidad2/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── docs/
│   └── actividad-unidad2.md
├── data/
│   └── .gitkeep             (el estudiante coloca aquí su dataset; no se versiona)
├── outputs/
│   └── .gitkeep             (PNG generados por la corrida: sí se versionan, son la entrega)
├── evidencias.md            (generado por la corrida; sí se versiona en el fork del
│                              estudiante — no versionar en la plantilla con datos de prueba)
└── src/
    ├── main.py                      # orquesta: config → datos → entrena → audita →
    │                                 #   mitiga → audita → SHAP → gráficos → evidencias
    ├── config.py                    # único módulo que conoce los nombres de las env vars
    ├── data_loader.py               # carga el dataset propio o el de demostración, valida
    │                                 #   columnas y binariza el target
    ├── preprocessing.py             # ColumnTransformer: imputación + codificación/escalado
    ├── model_training.py            # split train/test + entrena la regresión logística base
    ├── fairness_audit.py            # métricas Fairlearn (incluye el único TODO estudiante)
    ├── explainability.py            # SHAP sobre el modelo base, selecciona 2 predicciones
    ├── plots.py                     # genera los PNG de outputs/
    ├── evidence_writer.py           # arma evidencias.md (rota la versión anterior)
    └── mitigation/
        ├── __init__.py
        ├── base_mitigator.py         # contrato común: fit(x, y, sensible) / predict(x, sensible)
        ├── factory.py                 # get_mitigator(nombre, restriccion, estimador_base)
        │                               #   + resolver_metodos() (expande "ambos")
        ├── exponentiated_gradient.py
        └── threshold_optimizer.py
```

## 6. Decisiones de diseño ya tomadas (no las reabras salvo que se indique lo contrario)

- **El repo corre sin configurar nada.** Si `DATASET_PATH` no está definido, se activa un
  modo demo con un dataset público descargado en runtime
  (`fairlearn.datasets.fetch_adult`, atributo sensible `sex`). No se versiona ningún CSV
  en el repositorio. El objetivo pedagógico es que el estudiante vea el flujo completo
  funcionando *antes* de cargar su propio dataset, y que su intervención real sea mínima:
  `.env` + la interpretación escrita en `evidencias.md`.
- La elección de técnica de mitigación se resuelve por variable de entorno
  `MITIGATION_METHOD` (`exponentiated_gradient` | `threshold_optimizer` | `ambos`),
  mediante una **función factory simple** (`get_mitigator(nombre, restriccion,
  estimador_base)`), replicando intencionalmente el mismo patrón usado para
  `get_provider(name)` en la Unidad 1. `main.py` no tiene lógica condicional de método de
  mitigación dispersa: llama a `resolver_metodos()` y `get_mitigator()` desde un único
  lugar. El valor `ambos` expande a las dos técnicas individuales y las compara en la
  misma tabla — da más material para la discusión de la consigna 9.c sin que el
  estudiante escriba código adicional.
- También es configurable por entorno la restricción de equidad que optimiza la
  mitigación (`FAIRNESS_CONSTRAINT`: `demographic_parity` | `equalized_odds`) — hace
  visible que "equidad" no es un concepto único y que distintas métricas pueden entrar en
  tensión entre sí (se observó en pruebas: mejorar demographic parity puede empeorar
  equalized odds).
- El dataset, la columna objetivo, el atributo sensible y el valor de clase positiva
  **nunca se hardcodean**: se parametrizan siempre por variables de entorno
  (`DATASET_PATH`, `TARGET_COLUMN`, `SENSITIVE_ATTRIBUTE`, `POSITIVE_LABEL`), ya que el
  dataset lo elige cada estudiante sujeto a aprobación docente (consigna 8.a), no la
  cátedra.
- Se utiliza un único clasificador simple por defecto (regresión logística) para mantener
  el foco pedagógico en la auditoría de equidad y no en la optimización del modelo en sí;
  no se expone selección de algoritmo de modelado como variable adicional.
- **El atributo sensible se incluye como feature del modelo** (no se excluye del
  entrenamiento): es lo que permite ver con SHAP si el modelo lo usa directamente para
  discriminar, conectando con la consigna 4.
- **Preprocesamiento aplicado por adelantado, no dentro de un `Pipeline` de
  scikit-learn.** El `ColumnTransformer` se ajusta una sola vez sobre train y transforma
  train/test a matrices densas; el estimador que ven Fairlearn y SHAP es una
  `LogisticRegression` pelada. Motivo: las reducciones de Fairlearn llaman
  `estimator.fit(X, y, sample_weight=...)`, firma que un `Pipeline` no acepta
  directamente, y SHAP queda exacto y rápido sobre la matriz ya transformada.
- `ThresholdOptimizer` reutiliza el modelo base ya entrenado (`prefit=True`), en lugar de
  reentrenar uno nuevo: es justamente la diferencia pedagógica con
  `ExponentiatedGradient` (que sí reentrena, reponderando) y evita cómputo redundante.
- Los nombres de features expuestos a SHAP (`preprocessing.obtener_nombres_features`) se
  devuelven **sin el prefijo del `ColumnTransformer`** (`categoricas__`/`numericas__`):
  son más legibles en los gráficos que va a interpretar el estudiante.
- SHAP se aplica siempre sobre el **modelo base (pre-mitigación)**, nunca sobre el
  modelo mitigado: el objetivo pedagógico es conectar con la consigna 4 (qué técnica de
  XAI podría haber detectado el problema de forma preventiva, antes de cualquier
  corrección posterior). Las dos predicciones a explicar se eligen automáticamente por
  mayor/menor contribución absoluta de las columnas del atributo sensible, no a mano.
- `evidencias.md` **nunca pisa trabajo escrito**: si ya existe, `evidence_writer.py` lo
  renombra a `evidencias.anterior.md` antes de generar el nuevo y avisa por consola.
- Cada corrida genera también PNG en `outputs/` (comparación de métricas + dos waterfalls
  SHAP + resumen global) para que el estudiante los pegue directo en el informe Word/PDF.
- Esta actividad no incluye una demo de seguridad de LLMs (prompt injection/jailbreak):
  el alcance práctico se mantiene acotado a sesgo, equidad y explicabilidad, aunque esos
  contenidos (2.3.2) sí se cubren de forma conceptual en la consigna 5.

## 7. Estado de la implementación

La plantilla ya está generada y validada end-to-end (ver estructura en la sección 5). Se
verificó en Docker con la misma imagen del devcontainer (`python:3.11`) que corre:

- sin `.env` (camino demo, `fetch_adult`);
- con `MITIGATION_METHOD=ambos` y `FAIRNESS_CONSTRAINT=equalized_odds`;
- contra un dataset propio (CSV externo) con las tres variables de mitigación distintas;
- y que los errores esperados (dataset inexistente, columnas inexistentes,
  `POSITIVE_LABEL` inexistente, método/restricción inválidos) fallan con mensajes
  explícitos en castellano, sin trazas crudas no explicadas (RNF-03).

Antes de commitear una nueva corrida, verificar que `evidencias.md` y `outputs/*.png`
correspondan a un dataset real aprobado por el docente (nunca a datos de prueba internos).

**El único punto de intervención de código para el estudiante** es `METRICAS_EXTRA` en
`src/fairness_audit.py` (marcado `# TODO estudiante`, opcional). Todo lo demás se
configura por `.env`; no se espera que el estudiante edite ningún otro archivo de `src/`.

## 8. Fuera de alcance (no generar)

- No generar una demo de seguridad de LLMs (prompt injection/jailbreak) — el alcance
  práctico de esta actividad se limita a sesgo, equidad y explicabilidad (ver sección 6).
- No generar infraestructura de despliegue, monitoreo de drift ni MLflow/Docker/FastAPI
  — eso corresponde a la Unidad 3, no a esta actividad.
- No generar lógica de recuperación de documentos (RAG) — corresponde a la Unidad 4.
- No generar tests automatizados extensos; alcanza con que el script sea ejecutable y
  legible (no es el foco evaluativo de esta actividad).
