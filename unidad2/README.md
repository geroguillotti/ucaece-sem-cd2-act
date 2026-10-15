# Unidad 2 — Calidad, Seguridad y Mejores Prácticas: auditoría de equidad

Plantilla base para el componente práctico (consignas 7 a 11) del Análisis de Caso
Individual de la Unidad 2, Seminario de Ciencia de Datos II. Este README explica cómo
completar tu entrega individual a partir de esta plantilla.

> Las consignas 1 a 6 (selección del caso, descripción del sistema, evidencia de sesgo,
> técnicas de XAI/auditoría preventivas, evaluación bajo marco de IA responsable, propuesta
> de mejoras) se responden en un documento aparte (Word/PDF) y no generan código. Este
> repositorio cubre exclusivamente la parte ejecutable (consignas 7 a 11). Ver el texto
> completo en [`docs/actividad-unidad2.md`](docs/actividad-unidad2.md).

**El código ya está completo y funciona de punta a punta sin que edites nada.** Tu trabajo
es: (1) correrlo tal cual para ver el flujo completo, (2) apuntarlo a tu propio dataset vía
variables de entorno, y (3) escribir la interpretación de los resultados en `evidencias.md`
(marcada con `> TODO estudiante`). No hace falta que implementes ni modifiques el pipeline.

## 1. Preparar el entorno (consigna 7.a y 7.b)

Este repositorio agrupa varias unidades, cada una con su propio entorno. Por eso, para
crear el Codespace **no uses el botón de un clic** ("Create codespace on main"): hay que
elegir explícitamente la configuración de Unidad 2.

1. Desde este repositorio en GitHub, hacé clic en **Use this template** (o forkealo).
2. En tu copia, andá a **Code → Codespaces** y hacé clic en los **tres puntos ("...")**
   junto al botón verde → **New with options**.
3. En el campo **Dev container configuration**, elegí **unidad2-seminario-cd2** y
   confirmá con **Create codespace**.
4. Esperá a que termine de levantar el Codespace: instala automáticamente las
   dependencias de `requirements.txt` (`fairlearn`, `scikit-learn`, `shap`, `pandas`,
   `matplotlib`), no hace falta ningún paso manual. La terminal se abre directamente
   parada en la carpeta `unidad2/`.

## 2. Correr la demo (para ver el flujo completo antes de tocar nada)

No hace falta configurar nada todavía. Corré directamente:

```bash
python -m src.main
```

Como no hay `.env`, el script usa automáticamente un dataset público de demostración
([Adult Income](https://archive.ics.uci.edu/dataset/2/adult), atributo sensible: género) y
genera:

- `evidencias.md`: configuración usada, métricas de equidad del modelo base, tabla
  comparativa antes/después de la mitigación, y las explicaciones SHAP.
- `outputs/*.png`: los gráficos correspondientes (comparación de métricas, dos waterfalls
  SHAP y un resumen global), listos para pegar en tu informe.

Revisá esos dos artefactos para entender qué genera cada corrida — es exactamente lo que
vas a interpretar con tu propio dataset en el paso 6.

## 3. Configurar tu propio dataset (consigna 8.a)

1. Elegí un dataset público, tabular, con un atributo sensible identificable (género,
   raza, edad, etc.), coherente con el caso que elegiste en la consigna 1. **Sujeto a
   aprobación previa del docente**, igual que la elección del caso.
2. Colocá el CSV dentro de `data/` (esa carpeta no se versiona, salvo `.gitkeep`).
3. Copiá `.env.example` a `.env` y completá:

   ```bash
   cp .env.example .env
   ```

   ```env
   DATASET_PATH=data/tu_dataset.csv
   TARGET_COLUMN=nombre_de_tu_columna_objetivo
   SENSITIVE_ATTRIBUTE=nombre_de_tu_atributo_sensible
   POSITIVE_LABEL=valor_que_se_considera_clase_positiva
   ```

   `POSITIVE_LABEL` es el valor de `TARGET_COLUMN` que el modelo intenta predecir como
   "positivo" (ej. `"Sí"`, `"1"`, `">50K"`, `"aprobado"`).

## 4. Si tu CSV viene "crudo": limpieza rápida (ETL) antes de correrlo

Muchos datasets públicos (por ejemplo, el de [COMPAS](https://github.com/propublica/compas-analysis)
que suele usarse para casos de sesgo racial en sistemas judiciales) vienen con decenas de
columnas que no deberías usar tal cual: identificadores, texto libre, fechas, o columnas que
directamente filtran el resultado que el modelo tiene que predecir (*data leakage*). El
pipeline no adivina cuáles son: como pide RF-01, acepta cualquier CSV y entrena usando
**todas** las columnas salvo la que configures como `TARGET_COLUMN`. Elegir qué columnas
tienen sentido como *features* es trabajo de preparación de datos, igual que elegir el
dataset en el paso 3.

**Señales de que tu CSV necesita este paso:**

- **La exactitud del modelo base te da sospechosamente alta** (ej. > 0.95) en un problema
  que no debería ser tan fácil de predecir → probablemente alguna columna "filtra" la
  respuesta (contiene información que solo se conocería después de tener el resultado real).
- **La ejecución se cuelga o tarda muchísimo** sin terminar → probablemente hay columnas de
  texto libre o identificadores casi únicos por fila (nombres, IDs, fechas) que el
  `OneHotEncoder` expande en miles de columnas nuevas, disparando el tiempo de entrenamiento.
- **Advertencia de sklearn** `Skipping features without any observed values` → hay una
  columna enteramente vacía; no rompe la corrida, pero es señal de que el CSV no está curado.

**Solución:** quedate solo con las columnas que tengan sentido como features predictoras más
tu columna objetivo. Ejemplo real (el que se usó para llegar a una exactitud realista con el
dataset COMPAS, filtrando primero registros inválidos según el criterio del propio análisis
de ProPublica, y descartando columnas que filtran el resultado como `is_recid` o `event`):

```bash
python -c "
import pandas as pd

df = pd.read_csv('data/tu_dataset_crudo.csv')

# Filtros de calidad específicos del dataset (ajustá o quitá según el tuyo)
# df = df[df['alguna_columna_de_control'] != 'valor_invalido']

columnas = ['columna_a', 'columna_b', 'tu_atributo_sensible', 'tu_columna_objetivo']
df = df[columnas].dropna()
df.to_csv('data/tu_dataset_limpio.csv', index=False)
print(df.shape)
"
```

Después, apuntá `DATASET_PATH` en tu `.env` al CSV limpio (`data/tu_dataset_limpio.csv`) y
volvé a correr `python -m src.main`. Una exactitud que baja a un rango más razonable (ni
sospechosamente perfecta ni al nivel del azar) es la señal de que la limpieza funcionó.

## 5. Elegir la técnica de mitigación y la restricción de equidad (consigna 9.a)

En el mismo `.env`, elegís cómo mitigar el sesgo sin tocar código:

```env
# "exponentiated_gradient", "threshold_optimizer", o "ambos" para comparar las dos
MITIGATION_METHOD=exponentiated_gradient

# "demographic_parity" o "equalized_odds"
FAIRNESS_CONSTRAINT=demographic_parity
```

| Variable | Qué hace |
|---|---|
| `exponentiated_gradient` | Reentrena una secuencia de modelos reponderados hasta satisfacer la restricción. Suele preservar mejor la exactitud. |
| `threshold_optimizer` | No reentrena: ajusta un umbral de decisión distinto por grupo sobre el modelo ya entrenado. Más simple de explicar, pero necesita el atributo sensible también al predecir. |
| `ambos` | Corre las dos técnicas en la misma ejecución y las compara en la misma tabla — útil para la discusión de la consigna 9.c. |
| `demographic_parity` | Busca que la tasa de selección (predicciones positivas) sea similar entre grupos. |
| `equalized_odds` | Busca que la tasa de verdaderos/falsos positivos sea similar entre grupos — más exigente. |

## 6. Ejecutar y generar tus evidencias (consignas 8, 9 y 10)

```bash
python -m src.main
```

El script imprime en la terminal la exactitud de cada escenario y confirma dónde quedaron
guardadas las evidencias. Si ya existía un `evidencias.md` de una corrida anterior, se
conserva como `evidencias.anterior.md` antes de generar el nuevo (no perdés nada de lo que
ya hayas empezado a escribir, pero revisá igual que no se te haya pisado algo).

Abrí `evidencias.md` y completá los bloques marcados `> TODO estudiante:` — ahí es donde
conectás los números con el análisis conceptual de las consignas 1 a 6:

- **Auditoría base:** ¿el patrón de disparidad que ves es consistente con el sesgo
  documentado en el caso real que elegiste (consigna 3)?
- **Comparación antes/después:** ¿qué tan efectiva fue la mitigación? ¿bajó la exactitud a
  cambio de más equidad? ¿qué limitaciones observaste (consigna 9.c)?
- **SHAP:** ¿esta técnica hubiera permitido detectar el problema antes del despliegue
  (consigna 4)?

### Punto opcional de código

En [`src/fairness_audit.py`](src/fairness_audit.py) hay un único lugar marcado
`# TODO estudiante` donde podés sumar una métrica de equidad adicional de
`fairlearn.metrics` (ej. `equalized_odds_ratio`) si querés enriquecer la comparación. Es
completamente opcional: el resto del pipeline funciona igual sin tocarlo.

## 7. Errores comunes

- `No se encontró el archivo '...' (DATASET_PATH)` → revisá que el CSV esté efectivamente
  en `data/` y que la ruta en `.env` sea correcta.
- `No se encontraron en el dataset las columnas [...]` → `TARGET_COLUMN` o
  `SENSITIVE_ATTRIBUTE` no coinciden con los nombres reales de columnas de tu CSV (el
  mensaje lista las columnas disponibles).
- `POSITIVE_LABEL='...' no aparece en la columna '...'` → el valor no existe tal cual en tu
  columna objetivo (revisá mayúsculas/espacios).
- `MITIGATION_METHOD='...' no es válido` / `FAIRNESS_CONSTRAINT='...' no es válida` → usá
  exactamente uno de los valores listados en el mensaje de error.
- **La corrida no termina nunca, o la exactitud te da sospechosamente alta (> 0.95)** → tu
  CSV probablemente tiene columnas de texto libre/IDs o columnas que filtran el resultado.
  Ver la sección 4 (limpieza rápida / ETL) antes de seguir.

## 8. Registrar y entregar (consigna 11)

1. Commiteá tu código (si hiciste el ajuste opcional), `evidencias.md` y los PNG de
   `outputs/`.
2. En el documento entregado (Word/PDF con las consignas 1 a 6), incluí el enlace a tu
   repositorio.
3. Este mismo README ya resume el dataset, el atributo sensible y las métricas
   antes/después una vez que corriste el script con tu configuración — no hace falta que
   agregues nada más acá salvo que quieras ampliar algún punto.

## Estructura del repositorio

```
.devcontainer/
└── unidad2/devcontainer.json         # config de Codespaces para Unidad 2 (Python 3.11)
                                       # el repo agrupa varias unidades; cada una tiene
                                       # su propia config bajo .devcontainer/<unidad>/
unidad2/
├── .env.example                      # variables de entorno esperadas (sin valores reales)
├── docs/actividad-unidad2.md         # consigna oficial de cátedra
├── requirements.txt
├── data/                             # colocá acá tu dataset propio (no se versiona)
├── outputs/                          # gráficos PNG generados por la corrida
├── evidencias.md                     # generado por la corrida (métricas + interpretación)
└── src/
    ├── main.py                       # orquesta: config → datos → entrena → audita →
    │                                 #   mitiga → audita → SHAP → gráficos → evidencias
    ├── config.py                     # lee y valida las variables de entorno
    ├── data_loader.py                # carga el dataset propio o el de demostración
    ├── preprocessing.py              # imputación + codificación/escalado de features
    ├── model_training.py             # split train/test + regresión logística base
    ├── fairness_audit.py             # métricas de equidad de Fairlearn (contiene el
    │                                 #   único TODO estudiante, opcional)
    ├── explainability.py             # SHAP sobre el modelo base
    ├── plots.py                      # genera los PNG de outputs/
    ├── evidence_writer.py            # arma evidencias.md
    └── mitigation/
        ├── base_mitigator.py         # contrato común: fit(...) / predict(...)
        ├── factory.py                # get_mitigator(nombre) según MITIGATION_METHOD
        ├── exponentiated_gradient.py
        └── threshold_optimizer.py
```
