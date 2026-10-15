"""Genera los gráficos PNG de una corrida (métricas y SHAP).

No calcula ninguna métrica ni valor SHAP: solo recibe resultados ya
calculados por `fairness_audit.py` y `explainability.py` y los dibuja, para
que el estudiante los pegue directo en el informe entregable.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap

from src.explainability import EstudioSHAP
from src.fairness_audit import ResultadoAuditoria

# --- Constantes del módulo ---
OUTPUTS_DIR = "outputs"
ARCHIVO_COMPARACION_METRICAS = "comparacion_metricas.png"
ARCHIVO_SHAP_DISCRIMINA = "shap_prediccion_discrimina.png"
ARCHIVO_SHAP_NO_DISCRIMINA = "shap_prediccion_no_discrimina.png"
ARCHIVO_SHAP_RESUMEN = "shap_resumen.png"
ANCHO_BARRA = 0.35


def _ruta(nombre_archivo: str) -> str:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    return os.path.join(OUTPUTS_DIR, nombre_archivo)


def graficar_comparacion_metricas(resultados: list[ResultadoAuditoria]) -> str:
    """Barras de demographic parity difference y equalized odds difference por escenario."""
    escenarios = [resultado.nombre_escenario for resultado in resultados]
    dpd = [resultado.demographic_parity_difference for resultado in resultados]
    eod = [resultado.equalized_odds_difference for resultado in resultados]
    posiciones = range(len(escenarios))

    figura, eje = plt.subplots(figsize=(8, 5))
    eje.bar([p - ANCHO_BARRA / 2 for p in posiciones], dpd, ANCHO_BARRA, label="Demographic parity difference")
    eje.bar([p + ANCHO_BARRA / 2 for p in posiciones], eod, ANCHO_BARRA, label="Equalized odds difference")
    eje.set_xticks(list(posiciones))
    eje.set_xticklabels(escenarios, rotation=15, ha="right")
    eje.set_ylabel("Diferencia entre grupos (menor es más equitativo)")
    eje.set_title("Métricas de equidad por escenario")
    eje.legend()
    figura.tight_layout()

    ruta = _ruta(ARCHIVO_COMPARACION_METRICAS)
    figura.savefig(ruta)
    plt.close(figura)
    return ruta


def graficar_waterfall_instancias(estudio: EstudioSHAP) -> tuple[str, str]:
    """Waterfall SHAP de la instancia que más discrimina y de la que menos discrimina."""

    def _waterfall(indice: int, nombre_archivo: str) -> str:
        figura = plt.figure(figsize=(8, 5))
        shap.plots.waterfall(estudio.explicacion[indice], show=False)
        figura.tight_layout()
        ruta = _ruta(nombre_archivo)
        figura.savefig(ruta)
        plt.close(figura)
        return ruta

    ruta_discrimina = _waterfall(estudio.instancia_discrimina.indice, ARCHIVO_SHAP_DISCRIMINA)
    ruta_no_discrimina = _waterfall(estudio.instancia_no_discrimina.indice, ARCHIVO_SHAP_NO_DISCRIMINA)
    return ruta_discrimina, ruta_no_discrimina


def graficar_resumen_shap(estudio: EstudioSHAP) -> str:
    """Resumen global: impacto de cada feature sobre todas las predicciones de test."""
    shap.summary_plot(estudio.explicacion, show=False)
    figura = plt.gcf()
    figura.tight_layout()
    ruta = _ruta(ARCHIVO_SHAP_RESUMEN)
    figura.savefig(ruta)
    plt.close(figura)
    return ruta
