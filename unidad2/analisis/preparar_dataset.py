"""Descarga los microdatos ACS PUMS 2024 de Washington y arma el CSV de la auditoría.

Fuente: U.S. Census Bureau, American Community Survey (ACS) 2024 1-Year Public
Use Microdata Sample, archivo de personas del estado de Washington. Son datos
públicos (dominio público del gobierno de EE. UU.) y se descargan sin cuenta.

Población: personas ocupadas de 22 a 64 años con título de grado o superior,
es decir, el conjunto de graduados que podría postularse a un puesto técnico.

Objetivo `trabajo_tech`: "Tech" si la ocupación actual es de computación
(código SOC 15-1xxx) o de gerencia de sistemas (SOC 11-3021); "No tech" si no.
Es el registro histórico de quién ocupa hoy esos puestos: el mismo tipo de
datos del que aprendió el filtro de currículums de Amazon (Dastin, 2018).

Variables: solo las que un filtro de currículums podría leer o inferir de un
CV (edad, nivel educativo y campo del título) más el género, que es el
atributo sensible auditado. No se incluyen otros atributos protegidos.

Uso (desde la carpeta unidad2/):
    python -m analisis.preparar_dataset
"""

import csv
import io
import os
import urllib.request
import zipfile

import pandas as pd

# --- Fuentes (U.S. Census Bureau) ---
URL_MICRODATOS = "https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pwa.zip"
URL_DICCIONARIO = (
    "https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2024.csv"
)
ARCHIVO_PERSONAS = "psam_p53.csv"

# --- Rutas locales (data/ no se versiona) ---
CARPETA_CRUDOS = os.path.join("data", "crudo")
RUTA_ZIP = os.path.join(CARPETA_CRUDOS, "csv_pwa.zip")
RUTA_DICCIONARIO = os.path.join(CARPETA_CRUDOS, "PUMS_Data_Dictionary_2024.csv")
RUTA_SALIDA = os.path.join("data", "acs_wa_tech_2024.csv")

# --- Filtros de la población ---
COLUMNAS_CRUDAS = ["AGEP", "SEX", "ESR", "SCHL", "FOD1P", "SOCP"]
ESR_OCUPADOS = {"1", "2", "4", "5"}  # ocupado civil o en fuerzas armadas, trabajando o no
SCHL_GRADO_O_MAS = {"21", "22", "23", "24"}
EDAD_MINIMA = 22
EDAD_MAXIMA = 64

# --- Definición del objetivo ---
PREFIJO_SOC_COMPUTACION = "151"
SOC_GERENCIA_SISTEMAS = "113021"
ETIQUETA_TECH = "Tech"
ETIQUETA_NO_TECH = "No tech"

# --- Etiquetas legibles ---
GENEROS = {"1": "Hombre", "2": "Mujer"}
NIVELES_EDUCATIVOS = {
    "21": "Grado",
    "22": "Maestría",
    "23": "Posgrado profesional",
    "24": "Doctorado",
}
MINIMO_FILAS_POR_CAMPO = 20  # campos de título más chicos se agrupan
CAMPO_AGRUPADO = "Otro campo"

COLUMNAS_SALIDA = ["edad", "nivel_educativo", "campo_titulo", "genero", "trabajo_tech"]


def _descargar_si_falta(url: str, ruta: str) -> None:
    if os.path.isfile(ruta):
        return
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    print(f"Descargando {url} ...")
    urllib.request.urlretrieve(url, ruta)


def _leer_microdatos() -> pd.DataFrame:
    with zipfile.ZipFile(RUTA_ZIP) as archivo_zip:
        with archivo_zip.open(ARCHIVO_PERSONAS) as archivo:
            crudo = pd.read_csv(archivo, dtype=str, usecols=COLUMNAS_CRUDAS, keep_default_na=False)
    return crudo.apply(lambda columna: columna.str.strip())


def _etiquetas_campo_titulo() -> dict[str, str]:
    """Nombres de los campos de título (variable FOD1P) según el diccionario oficial."""
    etiquetas = {}
    with open(RUTA_DICCIONARIO, newline="", encoding="utf-8-sig") as archivo:
        for fila in csv.reader(archivo):
            if len(fila) >= 7 and fila[0] == "VAL" and fila[1] == "FOD1P" and fila[4].strip().isdigit():
                etiquetas[fila[4].strip()] = fila[6].strip()
    if not etiquetas:
        raise ValueError(f"No se encontraron etiquetas de FOD1P en {RUTA_DICCIONARIO}.")
    return etiquetas


def _filtrar_poblacion(crudo: pd.DataFrame) -> pd.DataFrame:
    edad = pd.to_numeric(crudo["AGEP"], errors="coerce")
    en_poblacion = (
        crudo["ESR"].isin(ESR_OCUPADOS)
        & edad.between(EDAD_MINIMA, EDAD_MAXIMA)
        & crudo["SCHL"].isin(SCHL_GRADO_O_MAS)
        & (crudo["SOCP"] != "")
    )
    return crudo.loc[en_poblacion].copy()


def _agrupar_campos_chicos(campos: pd.Series) -> pd.Series:
    conteo = campos.value_counts()
    campos_chicos = conteo[conteo < MINIMO_FILAS_POR_CAMPO].index
    return campos.where(~campos.isin(campos_chicos), CAMPO_AGRUPADO)


def _construir_dataset(poblacion: pd.DataFrame, etiquetas_campo: dict[str, str]) -> pd.DataFrame:
    es_tech = poblacion["SOCP"].str.startswith(PREFIJO_SOC_COMPUTACION) | (
        poblacion["SOCP"] == SOC_GERENCIA_SISTEMAS
    )
    dataset = pd.DataFrame(
        {
            "edad": pd.to_numeric(poblacion["AGEP"]).astype(int),
            "nivel_educativo": poblacion["SCHL"].map(NIVELES_EDUCATIVOS),
            "campo_titulo": _agrupar_campos_chicos(poblacion["FOD1P"].map(etiquetas_campo)),
            "genero": poblacion["SEX"].map(GENEROS),
            "trabajo_tech": es_tech.map({True: ETIQUETA_TECH, False: ETIQUETA_NO_TECH}),
        }
    )
    return dataset[COLUMNAS_SALIDA].dropna().reset_index(drop=True)


def _resumir(dataset: pd.DataFrame) -> None:
    print(f"Filas: {len(dataset):,}, campos de título distintos: {dataset['campo_titulo'].nunique()}")
    tasa_tech = (dataset["trabajo_tech"] == ETIQUETA_TECH).groupby(dataset["genero"]).mean()
    print("Proporción real con trabajo tech por género (no ponderada):")
    print(tasa_tech.round(3).to_string())


def main() -> None:
    _descargar_si_falta(URL_MICRODATOS, RUTA_ZIP)
    _descargar_si_falta(URL_DICCIONARIO, RUTA_DICCIONARIO)
    poblacion = _filtrar_poblacion(_leer_microdatos())
    dataset = _construir_dataset(poblacion, _etiquetas_campo_titulo())
    dataset.to_csv(RUTA_SALIDA, index=False)
    _resumir(dataset)
    print(f"Dataset guardado en {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
