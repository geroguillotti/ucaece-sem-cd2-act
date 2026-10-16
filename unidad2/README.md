# Unidad 2: Auditoría de equidad de un filtro de currículums (caso Amazon)

Entrega individual de Geronimo Guillotti para el Seminario de Ciencia de Datos II (Licenciatura en
Ciencia de Datos, CAECE), 2.º cuatrimestre de 2026.

Este directorio contiene el componente práctico (consignas 7 a 11) de la Actividad Formativa 2. El
análisis conceptual del caso (consignas 1 a 6) está en el informe entregado por el campus. Se partió
de la plantilla de la cátedra, cuyas instrucciones originales quedaron en
[`docs/README_plantilla_catedra.md`](docs/README_plantilla_catedra.md).

## Caso analizado

Herramienta experimental de reclutamiento de Amazon, discontinuada al detectarse que penalizaba a las
candidatas mujeres. Según Reuters (Dastin, 2018), los modelos se habían entrenado con diez años de
currículums recibidos por la empresa, en su mayoría de hombres. La práctica reproduce ese mecanismo de
sesgo histórico con datos reales: un clasificador entrenado con el registro de quién ocupa hoy un puesto
de tecnología, usado como filtro de candidatos.

## Dataset

Microdatos de la American Community Survey 2024 (1-Year PUMS) del U.S. Census Bureau, archivo de
personas del estado de Washington, donde tiene su sede Amazon. Son datos públicos que se descargan sin
registro desde census.gov, y su uso fue aprobado por la cátedra. La población son las personas ocupadas
de 22 a 64 años con título de grado o superior (16.028 filas; la plantilla toma una muestra de 10.000
con semilla fija).

La columna objetivo es `trabajo_tech`, que vale `Tech` cuando la ocupación es de computación (códigos
SOC 15-1xxx) o de gerencia de sistemas (SOC 11-3021) y `No tech` en el resto de los casos. Como
variables se usan solo las que un filtro podría leer en un CV: `edad`, `nivel_educativo` y
`campo_titulo` (carrera de grado). El atributo sensible es `genero` (`Hombre` / `Mujer`). En el
conjunto de test trabaja en tecnología el 19,4 % de los hombres y el 5,7 % de las mujeres.

El CSV no se versiona (`data/` está en `.gitignore`): lo genera
[`analisis/preparar_dataset.py`](analisis/preparar_dataset.py), que descarga los microdatos, filtra la
población y deja solo esas columnas.

## Resultados

Regresión logística base y mitigación con Fairlearn (`MITIGATION_METHOD=ambos`,
`FAIRNESS_CONSTRAINT=equalized_odds`), medidas sobre el conjunto de test (3.000 personas). H y M son
hombres y mujeres; TPR es la proporción de personas que trabajan en tecnología y que el modelo
reconoce.

| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. | Selección H / M | TPR H / M |
|---|---|---|---|---|---|
| Modelo base (sin mitigar) | 0,899 | 0,117 | 0,310 | 0,128 / 0,011 | 0,433 / 0,124 |
| ExponentiatedGradient | 0,897 | 0,056 | 0,017 | 0,092 / 0,035 | 0,332 / 0,337 |
| ThresholdOptimizer | 0,889 | 0,031 | 0,007 | 0,058 / 0,027 | 0,220 / 0,213 |

El modelo base no solo copia la desproporción de los datos, la agranda: selecciona al 1,1 % de las
mujeres contra el 12,8 % de los hombres (un cociente de 0,085, cuando en los datos es de 0,29 y la
regla de los cuatro quintos pide 0,8) y reconoce apenas al 12,4 % de las mujeres que trabajan en
tecnología, contra el 43,3 % de los hombres. En SHAP, `genero_Mujer` es la variable con más peso del
modelo.

Quitar la columna de género no resuelve el problema: la diferencia se mantiene a través de
`campo_titulo`, que está bastante asociada al género (V de Cramér de 0,43). Es el mismo riesgo que
Reuters señalaba para Amazon: neutralizar la palabra "women's" no garantizaba que el sistema dejara de
discriminar. ExponentiatedGradient con equalized odds deja el TPR prácticamente igual entre géneros
(0,332 y 0,337) sin perder casi exactitud. Con demographic parity, en cambio, se acercan las tasas de
selección (cociente de 0,63) pero a costa de desordenar los errores; esa comparación está en
[`outputs/analisis_complementario.md`](outputs/analisis_complementario.md).

## Cómo ejecutar

1. **Entorno.** En GitHub: Code, Codespaces, menú de los tres puntos, New with options, y en Dev
   container configuration la opción `unidad2-seminario-cd2`. La terminal abre en `unidad2/` con
   Python 3.11 y las dependencias de [`requirements.txt`](requirements.txt) instaladas, con versiones
   fijas: fairlearn 0.11.0, scikit-learn 1.5.2, shap 0.46.0, pandas 2.2.3 y numpy 1.26.4.
2. **Dataset.**
   ```bash
   python -m analisis.preparar_dataset
   ```
3. **Configuración.** Copiar la plantilla de variables de entorno y completarla:
   ```bash
   cp .env.example .env
   ```
   ```env
   DATASET_PATH=data/acs_wa_tech_2024.csv
   TARGET_COLUMN=trabajo_tech
   SENSITIVE_ATTRIBUTE=genero
   POSITIVE_LABEL=Tech
   MITIGATION_METHOD=ambos
   FAIRNESS_CONSTRAINT=equalized_odds
   ```
4. **Auditoría, mitigación y SHAP.** Genera `evidencias.md` y los gráficos de `outputs/`:
   ```bash
   python -m src.main
   ```
5. **Análisis complementario.** Tabla por grupo, modelo sin la columna de género, prueba
   contrafáctica, las dos restricciones de equidad y un caso SHAP elegido:
   ```bash
   python -m analisis.complementario
   ```

Cada paso tarda menos de un minuto en el Codespace estándar de 2 núcleos.

## Evidencias

- [`evidencias.md`](evidencias.md): métricas del modelo base, tabla antes y después de la mitigación,
  explicaciones SHAP y su interpretación (consignas 8 a 10).
- [`outputs/analisis_complementario.md`](outputs/analisis_complementario.md): resultados del análisis
  complementario.
- [`outputs/`](outputs/): gráficos de la comparación de métricas y de SHAP.

## Cambios respecto de la plantilla

En `src/fairness_audit.py` se completó el punto opcional con dos métricas más:
`demographic_parity_ratio`, que es la regla de los cuatro quintos, y `equal_opportunity_difference`,
que mide la brecha de verdaderos positivos. En `src/main.py` se fijó la semilla global de numpy,
porque ExponentiatedGradient y ThresholdOptimizer dan predicciones aleatorizadas y sin semilla los
números cambiaban un poco entre corridas. El resto de lo agregado está en `analisis/` y usa los
módulos de `src/` sin modificarlos.
