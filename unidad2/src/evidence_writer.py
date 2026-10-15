"""Arma evidencias.md con los resultados de la corrida.

No calcula nada: solo formatea en Markdown los resultados que le pasan
`fairness_audit.py` y `explainability.py`, y rota el archivo anterior para no
pisar la interpretación que ya haya escrito el estudiante.
"""

import os
from datetime import datetime

from src.config import Config
from src.explainability import EstudioSHAP
from src.fairness_audit import ResultadoAuditoria

EVIDENCIAS_FILE_PATH = "evidencias.md"
EVIDENCIAS_ANTERIOR_FILE_PATH = "evidencias.anterior.md"


def _rotar_evidencias_previas() -> None:
    if os.path.isfile(EVIDENCIAS_FILE_PATH):
        os.replace(EVIDENCIAS_FILE_PATH, EVIDENCIAS_ANTERIOR_FILE_PATH)
        print(
            f"Ya existía {EVIDENCIAS_FILE_PATH}: se guardó como "
            f"{EVIDENCIAS_ANTERIOR_FILE_PATH} antes de generar el nuevo."
        )


def _seccion_configuracion(config: Config) -> list[str]:
    origen_dataset = (
        "dataset de demostración (Adult Income, `fairlearn.datasets.fetch_adult`)"
        if config.usa_dataset_demo
        else config.dataset_path
    )
    return [
        "## Configuración de la corrida\n",
        f"- **Dataset:** {origen_dataset}",
        f"- **Columna objetivo:** `{config.target_column}` (clase positiva: `{config.positive_label}`)",
        f"- **Atributo sensible:** `{config.sensitive_attribute}`",
        f"- **Método de mitigación:** `{config.mitigation_method}`",
        f"- **Restricción de equidad:** `{config.fairness_constraint}`\n",
    ]


def _tabla_metricas_por_grupo(resultado: ResultadoAuditoria) -> list[str]:
    lineas = ["| Grupo | Exactitud | Tasa de selección |", "|---|---|---|"]
    for grupo, fila in resultado.metricas_por_grupo.iterrows():
        lineas.append(f"| {grupo} | {fila['exactitud']:.3f} | {fila['tasa_seleccion']:.3f} |")
    return lineas


def _seccion_auditoria_base(resultado: ResultadoAuditoria) -> list[str]:
    lineas = [
        "## Auditoría de equidad — modelo base (pre-mitigación)\n",
        f"- **Exactitud global:** {resultado.exactitud:.3f}",
        f"- **Demographic parity difference:** {resultado.demographic_parity_difference:.3f}",
        f"- **Equalized odds difference:** {resultado.equalized_odds_difference:.3f}",
    ]
    for nombre_metrica, valor in resultado.metricas_extra.items():
        lineas.append(f"- **{nombre_metrica}:** {valor:.3f}")
    lineas.append("\n### Métricas por grupo\n")
    lineas.extend(_tabla_metricas_por_grupo(resultado))
    lineas.append(
        "\n> TODO estudiante: interpretá esta tabla vinculándola con el sesgo documentado "
        "en el caso real analizado en la consigna 3 (¿el patrón que ves acá es consistente "
        "con lo que reportó el caso?).\n"
    )
    return lineas


def _seccion_comparativa(resultados: list[ResultadoAuditoria]) -> list[str]:
    lineas = [
        "## Comparación antes / después de la mitigación\n",
        "| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. |",
        "|---|---|---|---|",
    ]
    for resultado in resultados:
        lineas.append(
            f"| {resultado.nombre_escenario} | {resultado.exactitud:.3f} | "
            f"{resultado.demographic_parity_difference:.3f} | {resultado.equalized_odds_difference:.3f} |"
        )
    lineas.append("\n![Comparación de métricas de equidad](outputs/comparacion_metricas.png)\n")
    lineas.append(
        "> TODO estudiante: discutí qué tan efectiva resultó la mitigación aplicada y qué "
        "limitaciones observaste (consigna 9.c) — por ejemplo, si mejoró la equidad pero "
        "bajó la exactitud, o si algún escenario no logró reducir la disparidad.\n"
    )
    return lineas


def _seccion_shap(estudio: EstudioSHAP, config: Config) -> list[str]:
    instancia_d = estudio.instancia_discrimina
    instancia_nd = estudio.instancia_no_discrimina
    return [
        "## Explicabilidad (SHAP) — modelo base\n",
        "SHAP se aplica siempre sobre el modelo base, antes de cualquier mitigación: el "
        "objetivo es ver qué técnica de auditoría preventiva podría haber detectado el "
        "problema antes del despliegue (consigna 4).\n",
        f"### Predicción {instancia_d.indice} — el atributo sensible más influyó\n",
        f"- Contribución absoluta de `{config.sensitive_attribute}`: "
        f"{instancia_d.contribucion_atributo_sensible:.3f}",
        f"- Predicción del modelo: {instancia_d.prediccion} · Valor real: {instancia_d.valor_real}\n",
        "![SHAP de la predicción donde el modelo discrimina](outputs/shap_prediccion_discrimina.png)\n",
        f"### Predicción {instancia_nd.indice} — el atributo sensible casi no influyó\n",
        f"- Contribución absoluta de `{config.sensitive_attribute}`: "
        f"{instancia_nd.contribucion_atributo_sensible:.3f}",
        f"- Predicción del modelo: {instancia_nd.prediccion} · Valor real: {instancia_nd.valor_real}\n",
        "![SHAP de la predicción donde el modelo no discrimina](outputs/shap_prediccion_no_discrimina.png)\n",
        "### Resumen global\n",
        "![Resumen SHAP de todas las predicciones de test](outputs/shap_resumen.png)\n",
        "> TODO estudiante: vinculá esta evidencia con la consigna 4 — ¿SHAP sobre el modelo "
        "base hubiera permitido detectar este problema antes del despliegue?\n",
    ]


def escribir_evidencias(
    config: Config,
    resultado_base: ResultadoAuditoria,
    resultados_mitigados: list[ResultadoAuditoria],
    estudio_shap: EstudioSHAP,
) -> None:
    """Genera evidencias.md, rotando cualquier versión previa a evidencias.anterior.md."""
    _rotar_evidencias_previas()

    lineas = [
        "# Evidencias — Auditoría de equidad, mitigación y explicabilidad\n",
        f"_Generado automáticamente el {datetime.now():%Y-%m-%d %H:%M}._\n",
    ]
    lineas.extend(_seccion_configuracion(config))
    lineas.extend(_seccion_auditoria_base(resultado_base))
    lineas.extend(_seccion_comparativa([resultado_base, *resultados_mitigados]))
    lineas.extend(_seccion_shap(estudio_shap, config))

    with open(EVIDENCIAS_FILE_PATH, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
