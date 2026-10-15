"""Análisis complementario de la auditoría (consignas 8, 9 y 10).

Reutiliza los módulos de src/ con la misma configuración (.env) y suma
evidencias que el pipeline base no genera:

1. Tabla por grupo del modelo base: tasa real, tasa de selección, TPR y FPR.
2. "Equidad por desconocimiento": el mismo modelo entrenado sin la columna de
   género, para ver cuánta disparidad sobrevive a través de variables proxy.
3. Prueba contrafáctica: cuántas predicciones cambian si solo se invierte el
   género de cada persona del conjunto de test.
4. Las dos restricciones de equidad (demographic parity y equalized odds) con
   ambas técnicas de mitigación, con la tasa de selección y el TPR por grupo.
5. Un caso SHAP elegido a propósito: una mujer que sí trabaja en tecnología y
   que el modelo descarta, junto a su "gemelo" con el mismo perfil y género
   masculino.

Uso (desde unidad2/, después de `python -m src.main`):
    python -m analisis.complementario
Genera outputs/analisis_complementario.md y dos gráficos SHAP en outputs/.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from dotenv import load_dotenv
from fairlearn.metrics import (
    MetricFrame,
    count,
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
    false_positive_rate,
    selection_rate,
    true_positive_rate,
)
from scipy.stats import chi2_contingency
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score
from sklearn.model_selection import train_test_split

from src.config import Config, cargar_configuracion
from src.data_loader import cargar_datos
from src.main import NOMBRES_ESCENARIO_POR_METODO, SEMILLA_GLOBAL
from src.mitigation.factory import METODOS_INDIVIDUALES, get_mitigator
from src.model_training import (
    MAX_ITERACIONES_MODELO,
    SEMILLA,
    TEST_SIZE,
    DatosEntrenamiento,
    entrenar_modelo,
)
from src.preprocessing import construir_preprocesador, transformar_a_matriz_densa

# --- Constantes del módulo ---
RUTA_INFORME = os.path.join("outputs", "analisis_complementario.md")
RUTA_SHAP_CASO = os.path.join("outputs", "shap_caso_mujer_descartada.png")
RUTA_SHAP_GEMELO = os.path.join("outputs", "shap_caso_gemelo_hombre.png")
RESTRICCIONES = ("demographic_parity", "equalized_odds")
GRUPO_DESFAVORECIDO = "Mujer"
GRUPO_FAVORECIDO = "Hombre"
CUANTILES_EDAD = 10


def _tasa_real(y_true, y_pred) -> float:
    return float(np.mean(y_true))


def _tabla_por_grupo(y_true, y_pred, sensible: pd.Series) -> pd.DataFrame:
    """n, tasa real de positivos, tasa de selección, TPR y FPR por grupo."""
    metricas = {
        "n": count,
        "tasa_real": _tasa_real,
        "tasa_seleccion": selection_rate,
        "tpr": true_positive_rate,
        "fpr": false_positive_rate,
    }
    return MetricFrame(metrics=metricas, y_true=y_true, y_pred=y_pred, sensitive_features=sensible).by_group


def _resumen_escenario(nombre: str, y_true, y_pred, sensible: pd.Series) -> dict:
    """Métricas globales y por grupo de un escenario, en una sola fila."""
    por_grupo = _tabla_por_grupo(y_true, y_pred, sensible)
    return {
        "Escenario": nombre,
        "Exactitud": accuracy_score(y_true, y_pred),
        "Exactitud balanceada": balanced_accuracy_score(y_true, y_pred),
        "DPD": demographic_parity_difference(y_true, y_pred, sensitive_features=sensible),
        "EOD": equalized_odds_difference(y_true, y_pred, sensitive_features=sensible),
        "Cociente DP": demographic_parity_ratio(y_true, y_pred, sensitive_features=sensible),
        f"Selección {GRUPO_FAVORECIDO}": por_grupo.loc[GRUPO_FAVORECIDO, "tasa_seleccion"],
        f"Selección {GRUPO_DESFAVORECIDO}": por_grupo.loc[GRUPO_DESFAVORECIDO, "tasa_seleccion"],
        f"TPR {GRUPO_FAVORECIDO}": por_grupo.loc[GRUPO_FAVORECIDO, "tpr"],
        f"TPR {GRUPO_DESFAVORECIDO}": por_grupo.loc[GRUPO_DESFAVORECIDO, "tpr"],
    }


def _separar_crudo(dataframe: pd.DataFrame, config: Config):
    """Mismo split que model_training.py (semilla, proporción y estratificación)."""
    features = dataframe.drop(columns=[config.target_column])
    target = dataframe[config.target_column].to_numpy()
    return train_test_split(features, target, test_size=TEST_SIZE, random_state=SEMILLA, stratify=target)


def _modelo_sin_genero(dataframe: pd.DataFrame, config: Config) -> np.ndarray:
    """Entrena la misma regresión logística sin la columna sensible y predice test."""
    x_train, x_test, y_train, _ = _separar_crudo(dataframe, config)
    x_train = x_train.drop(columns=[config.sensitive_attribute])
    x_test = x_test.drop(columns=[config.sensitive_attribute])
    preprocesador = construir_preprocesador(x_train)
    preprocesador.fit(x_train)
    modelo = LogisticRegression(max_iter=MAX_ITERACIONES_MODELO, random_state=SEMILLA)
    modelo.fit(transformar_a_matriz_densa(preprocesador, x_train), y_train)
    return modelo.predict(transformar_a_matriz_densa(preprocesador, x_test))


def _cramer_v(columna: pd.Series, sensible: pd.Series) -> float:
    tabla = pd.crosstab(columna, sensible)
    chi2 = chi2_contingency(tabla, correction=False)[0]
    return float(np.sqrt(chi2 / (tabla.to_numpy().sum() * (min(tabla.shape) - 1))))


def _asociacion_con_genero(dataframe: pd.DataFrame, config: Config) -> pd.Series:
    """V de Cramér entre cada variable y el género: candidatas a proxy."""
    features = dataframe.drop(columns=[config.target_column, config.sensitive_attribute])
    sensible = dataframe[config.sensitive_attribute]
    asociaciones = {}
    for nombre, columna in features.items():
        if pd.api.types.is_numeric_dtype(columna):
            columna = pd.qcut(columna, CUANTILES_EDAD, duplicates="drop")
        asociaciones[nombre] = _cramer_v(columna, sensible)
    return pd.Series(asociaciones).sort_values(ascending=False)


def _columnas_genero(datos: DatosEntrenamiento, config: Config) -> tuple[int, int]:
    nombres = datos.nombres_features
    prefijo = f"{config.sensitive_attribute}_"
    return nombres.index(prefijo + GRUPO_FAVORECIDO), nombres.index(prefijo + GRUPO_DESFAVORECIDO)


def _invertir_genero(x: np.ndarray, columnas: tuple[int, int]) -> np.ndarray:
    """Intercambia las dos columnas one-hot del género: mismo perfil, otro género."""
    invertido = x.copy()
    invertido[:, list(columnas)] = x[:, list(columnas[::-1])]
    return invertido


def _prueba_contrafactica(datos: DatosEntrenamiento, columnas: tuple[int, int]) -> dict:
    originales = datos.modelo.predict(datos.x_test)
    invertidas = datos.modelo.predict(_invertir_genero(datos.x_test, columnas))
    mujeres = (datos.sensible_test == GRUPO_DESFAVORECIDO).to_numpy()
    mujeres_tech = mujeres & (datos.y_test == 1)
    return {
        "cambian_total": float(np.mean(originales != invertidas)),
        "mujeres_que_pasan_a_tech": int(np.sum(mujeres & (originales == 0) & (invertidas == 1))),
        "mujeres_tech_descartadas": int(np.sum(mujeres_tech & (originales == 0))),
        "mujeres_tech_rescatadas": int(np.sum(mujeres_tech & (originales == 0) & (invertidas == 1))),
        "invertidas": invertidas,
    }


def _comparar_mitigaciones(datos: DatosEntrenamiento) -> list[dict]:
    """Cada restricción con ambas técnicas; la semilla se fija igual que en src/main.py."""
    filas = []
    for restriccion in RESTRICCIONES:
        np.random.seed(SEMILLA_GLOBAL)
        for metodo in METODOS_INDIVIDUALES:
            mitigador = get_mitigator(metodo, restriccion, datos.modelo)
            mitigador.fit(datos.x_train, datos.y_train, datos.sensible_train)
            predicciones = mitigador.predict(datos.x_test, datos.sensible_test)
            nombre = f"{NOMBRES_ESCENARIO_POR_METODO[metodo]} ({restriccion})"
            filas.append(_resumen_escenario(nombre, datos.y_test, predicciones, datos.sensible_test))
    return filas


def _elegir_caso(datos: DatosEntrenamiento, invertidas: np.ndarray) -> int:
    """Mujer que trabaja en tecnología, descartada, y que con género masculino pasaría.

    Entre las candidatas se elige la de mayor probabilidad predicha: el caso en
    que el resto del perfil más se parece al de quienes el modelo selecciona.
    """
    originales = datos.modelo.predict(datos.x_test)
    candidatas = (
        (datos.sensible_test == GRUPO_DESFAVORECIDO).to_numpy()
        & (datos.y_test == 1)
        & (originales == 0)
        & (invertidas == 1)
    )
    if not candidatas.any():
        raise ValueError("No hay mujeres descartadas cuya predicción cambie al invertir el género.")
    probabilidades = datos.modelo.predict_proba(datos.x_test)[:, 1]
    return int(np.argmax(np.where(candidatas, probabilidades, -1.0)))


def _guardar_waterfall(explicacion: shap.Explanation, ruta: str, titulo: str) -> None:
    figura = plt.figure(figsize=(9, 5.5))
    shap.plots.waterfall(explicacion, show=False)
    figura.suptitle(titulo, fontsize=12)
    figura.tight_layout(rect=(0, 0, 1, 0.93))
    figura.savefig(ruta)
    plt.close(figura)


def _explicar_caso(datos: DatosEntrenamiento, indice: int, columnas: tuple[int, int]) -> dict:
    """SHAP del caso y de su gemelo con el género invertido (mismo explicador que src/)."""
    explicador = shap.Explainer(datos.modelo, datos.x_train, feature_names=datos.nombres_features)
    fila = datos.x_test[[indice]]
    caso = explicador(fila)[0]
    gemelo = explicador(_invertir_genero(fila, columnas))[0]
    _guardar_waterfall(caso, RUTA_SHAP_CASO, "Mujer con trabajo tech, descartada por el modelo")
    _guardar_waterfall(gemelo, RUTA_SHAP_GEMELO, "Mismo perfil con género masculino")
    probabilidad = datos.modelo.predict_proba(np.vstack([fila, _invertir_genero(fila, columnas)]))[:, 1]
    return {
        "shap_genero_caso": float(caso.values[list(columnas)].sum()),
        "shap_genero_gemelo": float(gemelo.values[list(columnas)].sum()),
        "probabilidad_caso": float(probabilidad[0]),
        "probabilidad_gemelo": float(probabilidad[1]),
    }


def _perfil_del_caso(dataframe: pd.DataFrame, config: Config, indice: int) -> pd.Series:
    _, x_test, _, _ = _separar_crudo(dataframe, config)
    return x_test.iloc[indice]


def _formatear(valor) -> str:
    if isinstance(valor, (float, np.floating)):
        return f"{valor:.0f}" if valor.is_integer() and abs(valor) >= 1 else f"{valor:.3f}"
    return str(valor)


def _tabla_markdown(tabla: pd.DataFrame) -> str:
    """DataFrame -> tabla Markdown (sin depender de la librería tabulate)."""
    encabezado = [tabla.index.name or "Grupo", *tabla.columns]
    lineas = ["| " + " | ".join(encabezado) + " |", "|" + "---|" * len(encabezado)]
    for indice, fila in tabla.iterrows():
        lineas.append("| " + " | ".join([str(indice), *(_formatear(valor) for valor in fila)]) + " |")
    return "\n".join(lineas)


def _escribir_informe(secciones: list[str]) -> None:
    with open(RUTA_INFORME, "w", encoding="utf-8") as archivo:
        archivo.write("\n\n".join(secciones) + "\n")


def _seccion_base(datos: DatosEntrenamiento) -> str:
    predicciones = datos.modelo.predict(datos.x_test)
    tabla = _tabla_por_grupo(datos.y_test, predicciones, datos.sensible_test)
    exactitud_balanceada = balanced_accuracy_score(datos.y_test, predicciones)
    clase_mayoritaria = 1 - float(np.mean(datos.y_test))
    return (
        "## 1. Modelo base por grupo (test)\n\n"
        f"{_tabla_markdown(tabla)}\n\n"
        f"Exactitud balanceada: {exactitud_balanceada:.3f}. "
        f"Exactitud de predecir siempre la clase mayoritaria: {clase_mayoritaria:.3f}."
    )


def _seccion_sin_genero(dataframe: pd.DataFrame, datos: DatosEntrenamiento, config: Config) -> str:
    predicciones = _modelo_sin_genero(dataframe, config)
    fila = _resumen_escenario("Sin la columna de género", datos.y_test, predicciones, datos.sensible_test)
    asociacion = (
        _asociacion_con_genero(dataframe, config).rename("V de Cramér con el género").rename_axis("Variable")
    )
    return (
        "## 2. Equidad por desconocimiento (modelo sin la columna de género)\n\n"
        f"{_tabla_markdown(pd.DataFrame([fila]).set_index('Escenario'))}\n\n"
        "Asociación de cada variable con el género (candidatas a proxy):\n\n"
        f"{_tabla_markdown(asociacion.to_frame())}"
    )


def _seccion_contrafactica(prueba: dict) -> str:
    return (
        "## 3. Prueba contrafáctica (se invierte solo el género)\n\n"
        f"- Predicciones de test que cambian: {prueba['cambian_total']:.1%}\n"
        f"- Mujeres que pasan de 'No tech' a 'Tech' con género masculino: {prueba['mujeres_que_pasan_a_tech']}\n"
        f"- Mujeres que sí trabajan en tecnología y el modelo descarta: {prueba['mujeres_tech_descartadas']}, "
        f"de las cuales {prueba['mujeres_tech_rescatadas']} serían seleccionadas con género masculino"
    )


def _seccion_mitigaciones(filas_base: list[dict], filas_mitigadas: list[dict]) -> str:
    tabla = pd.DataFrame(filas_base + filas_mitigadas).set_index("Escenario")
    return (
        "## 4. Restricciones de equidad comparadas (misma semilla que src/main.py)\n\n"
        f"{_tabla_markdown(tabla)}"
    )


def _seccion_caso(perfil: pd.Series, explicacion: dict) -> str:
    descripcion = ", ".join(f"{nombre}={valor}" for nombre, valor in perfil.items())
    return (
        "## 5. Caso SHAP elegido: mujer con trabajo tech descartada y su gemelo masculino\n\n"
        f"- Perfil: {descripcion}\n"
        f"- Probabilidad predicha de 'Tech': {explicacion['probabilidad_caso']:.3f} (mujer) frente a "
        f"{explicacion['probabilidad_gemelo']:.3f} (mismo perfil, hombre)\n"
        f"- Aporte SHAP del género (log-odds): {explicacion['shap_genero_caso']:+.3f} (mujer) frente a "
        f"{explicacion['shap_genero_gemelo']:+.3f} (hombre)\n\n"
        f"![Caso](shap_caso_mujer_descartada.png)\n\n![Gemelo](shap_caso_gemelo_hombre.png)"
    )


def main() -> None:
    load_dotenv()
    config = cargar_configuracion()
    dataframe = cargar_datos(config)
    datos = entrenar_modelo(dataframe, config)
    columnas = _columnas_genero(datos, config)

    base = _resumen_escenario("Modelo base", datos.y_test, datos.modelo.predict(datos.x_test), datos.sensible_test)
    prueba = _prueba_contrafactica(datos, columnas)
    indice = _elegir_caso(datos, prueba["invertidas"])

    _escribir_informe(
        [
            "# Análisis complementario de la auditoría",
            _seccion_base(datos),
            _seccion_sin_genero(dataframe, datos, config),
            _seccion_contrafactica(prueba),
            _seccion_mitigaciones([base], _comparar_mitigaciones(datos)),
            _seccion_caso(_perfil_del_caso(dataframe, config, indice), _explicar_caso(datos, indice, columnas)),
        ]
    )
    print(f"Análisis complementario guardado en {RUTA_INFORME}")


if __name__ == "__main__":
    main()
