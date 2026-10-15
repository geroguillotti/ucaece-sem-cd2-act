# Unidad 2: auditoría de equidad de un filtro de currículums

Entrega individual de Geronimo Guillotti para el Seminario de Ciencia de Datos II (Licenciatura en
Ciencia de Datos, CAECE), 2.º cuatrimestre de 2026.

Esta carpeta tiene el componente práctico (consignas 7 a 11) de la actividad de la Unidad 2. El
análisis conceptual del caso (consignas 1 a 6) va en el informe que se entrega por el campus. Partí
de la plantilla de la cátedra; sus instrucciones originales quedaron en
[`docs/README_plantilla_catedra.md`](docs/README_plantilla_catedra.md).

## Caso

Elegí el sistema de reclutamiento que Amazon dejó de usar en 2017 porque penalizaba a las
candidatas mujeres. Según Reuters (Dastin, 2018), los modelos habían aprendido de diez años de
currículums recibidos por la empresa, en su mayoría de hombres. La idea de esta práctica es
reproducir ese mecanismo de sesgo histórico con datos reales: entrenar un clasificador con el
registro de quién ocupa hoy un puesto de tecnología y ver qué pasa si se lo usa como filtro.

## Dataset

Uso los microdatos de la American Community Survey 2024 (1-Year PUMS) del U.S. Census Bureau, archivo
de personas del estado de Washington, donde tiene su sede Amazon. Son datos públicos y se descargan
sin registrarse. Me quedo con las personas ocupadas de 22 a 64 años que tienen título de grado o
superior (16.028 filas; la plantilla toma una muestra de 10.000 con semilla fija).

La columna objetivo es `trabajo_tech`, que vale `Tech` cuando la ocupación es de computación
(códigos SOC 15-1xxx) o de gerencia de sistemas (SOC 11-3021) y `No tech` en el resto de los casos.
Como variables uso solo lo que un filtro podría leer en un CV: `edad`, `nivel_educativo` y
`campo_titulo` (la carrera de grado). El atributo sensible es `genero` (`Hombre` / `Mujer`). En el
conjunto de test trabaja en tecnología el 19,4 % de los hombres y el 5,7 % de las mujeres.

El CSV no se sube al repositorio (`data/` está en `.gitignore`). Lo arma
[`analisis/preparar_dataset.py`](analisis/preparar_dataset.py), que descarga los microdatos de
census.gov, filtra la población y deja solo esas columnas.

## Resultados

Regresión logística base y mitigación con Fairlearn (`MITIGATION_METHOD=ambos`,
`FAIRNESS_CONSTRAINT=equalized_odds`), medidas sobre el conjunto de test (3.000 personas). H y M son
hombres y mujeres; TPR es la proporción de personas que sí trabajan en tecnología y el modelo
reconoce.

| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. | Selección H / M | TPR H / M |
|---|---|---|---|---|---|
| Modelo base (sin mitigar) | 0,899 | 0,117 | 0,310 | 0,128 / 0,011 | 0,433 / 0,124 |
| ExponentiatedGradient | 0,897 | 0,056 | 0,017 | 0,092 / 0,035 | 0,332 / 0,337 |
| ThresholdOptimizer | 0,889 | 0,031 | 0,007 | 0,058 / 0,027 | 0,220 / 0,213 |

El modelo base no solo copia la brecha de los datos, la agranda. Selecciona al 1,1 % de las mujeres
contra el 12,8 % de los hombres (un cociente de 0,085, lejísimos del 0,8 de la regla de los cuatro
quintos) y reconoce apenas al 12,4 % de las mujeres que sí trabajan en tecnología, contra el 43,3 %
de los hombres. En SHAP, `genero_Mujer` aparece como la variable con más peso del modelo.

Sacar la columna de género no resuelve el problema: la diferencia se mantiene a través de
`campo_titulo`, que está bastante asociada al género (V de Cramér de 0,43). Es lo mismo que le pasó
a Amazon cuando neutralizó la palabra "women's". ExponentiatedGradient con equalized odds deja el
TPR prácticamente igual entre géneros (0,332 y 0,337) sin perder casi exactitud. Con demographic
parity, en cambio, se iguala la tasa de selección pero a costa de desordenar los errores; esa
comparación está en [`outputs/analisis_complementario.md`](outputs/analisis_complementario.md).

La interpretación completa está en [`evidencias.md`](evidencias.md).

## Cómo ejecutarlo

1. Crear el Codespace desde GitHub con Code, Codespaces, el menú de los tres puntos y "New with
   options", eligiendo la configuración `unidad2-seminario-cd2`. La terminal abre en `unidad2/` con
   Python 3.11 y las dependencias de [`requirements.txt`](requirements.txt) instaladas (fairlearn
   0.11.0, scikit-learn 1.5.2, shap 0.46.0, pandas 2.2.3 y numpy 1.26.4, con versión fija).
2. Descargar y preparar el dataset:
   ```bash
   python -m analisis.preparar_dataset
   ```
3. Copiar la plantilla de variables de entorno y completarla:
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
4. Correr la auditoría, la mitigación y SHAP, que generan `evidencias.md` y los gráficos de
   `outputs/`:
   ```bash
   python -m src.main
   ```
5. Correr el análisis complementario (tabla por grupo, modelo sin la columna de género, prueba
   contrafáctica, las dos restricciones de equidad y un caso SHAP elegido a propósito):
   ```bash
   python -m analisis.complementario
   ```

Cada paso tarda menos de un minuto en el Codespace estándar de 2 núcleos.

## Cambios respecto de la plantilla

En `src/fairness_audit.py` completé el punto opcional con dos métricas más:
`demographic_parity_ratio`, que es la regla de los cuatro quintos, y `equal_opportunity_difference`,
que mide la brecha de verdaderos positivos. En `src/main.py` fijé la semilla global de numpy, porque
ExponentiatedGradient y ThresholdOptimizer dan predicciones aleatorizadas y sin semilla los números
cambiaban un poco entre corridas. Lo demás que agregué está en `analisis/` y usa los módulos de
`src/` sin modificarlos.
