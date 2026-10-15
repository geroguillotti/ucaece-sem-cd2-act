# Evidencias — Auditoría de equidad, mitigación y explicabilidad

_Generado automáticamente el 2026-10-15 23:54._

## Configuración de la corrida

- **Dataset:** data/acs_wa_tech_2024.csv
- **Columna objetivo:** `trabajo_tech` (clase positiva: `Tech`)
- **Atributo sensible:** `genero`
- **Método de mitigación:** `ambos`
- **Restricción de equidad:** `equalized_odds`

## Auditoría de equidad — modelo base (pre-mitigación)

- **Exactitud global:** 0.899
- **Demographic parity difference:** 0.117
- **Equalized odds difference:** 0.310
- **demographic_parity_ratio:** 0.085
- **equal_opportunity_difference:** 0.310

### Métricas por grupo

| Grupo | Exactitud | Tasa de selección |
|---|---|---|
| Hombre | 0.846 | 0.128 |
| Mujer | 0.946 | 0.011 |

> TODO estudiante: interpretá esta tabla vinculándola con el sesgo documentado en el caso real analizado en la consigna 3 (¿el patrón que ves acá es consistente con lo que reportó el caso?).

## Comparación antes / después de la mitigación

| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. |
|---|---|---|---|
| Modelo base (sin mitigar) | 0.899 | 0.117 | 0.310 |
| ExponentiatedGradient | 0.897 | 0.056 | 0.017 |
| ThresholdOptimizer | 0.889 | 0.031 | 0.007 |

![Comparación de métricas de equidad](outputs/comparacion_metricas.png)

> TODO estudiante: discutí qué tan efectiva resultó la mitigación aplicada y qué limitaciones observaste (consigna 9.c) — por ejemplo, si mejoró la equidad pero bajó la exactitud, o si algún escenario no logró reducir la disparidad.

## Explicabilidad (SHAP) — modelo base

SHAP se aplica siempre sobre el modelo base, antes de cualquier mitigación: el objetivo es ver qué técnica de auditoría preventiva podría haber detectado el problema antes del despliegue (consigna 4).

### Predicción 4 — el atributo sensible más influyó

- Contribución absoluta de `genero`: 0.451
- Predicción del modelo: 0 · Valor real: 0

![SHAP de la predicción donde el modelo discrimina](outputs/shap_prediccion_discrimina.png)

### Predicción 0 — el atributo sensible casi no influyó

- Contribución absoluta de `genero`: 0.434
- Predicción del modelo: 0 · Valor real: 0

![SHAP de la predicción donde el modelo no discrimina](outputs/shap_prediccion_no_discrimina.png)

### Resumen global

![Resumen SHAP de todas las predicciones de test](outputs/shap_resumen.png)

> TODO estudiante: vinculá esta evidencia con la consigna 4 — ¿SHAP sobre el modelo base hubiera permitido detectar este problema antes del despliegue?
