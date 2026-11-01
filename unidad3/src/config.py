MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENTO_PIPELINE = "u3-pipeline-iris"
EXPERIMENTO_LLMOPS = "u3-llmops-prompts"
NOMBRE_MODELO = "modelo-u3"
ALIAS_CAMPEON = "champion"
NOMBRE_ARTEFACTO_MODELO = "modelo"
METRICA_PRINCIPAL = "accuracy"
SEMILLA = 42
PROPORCION_TEST = 0.3
PROFUNDIDAD_POR_DEFECTO = 3
CARPETA_MODELO_EXPORTADO = "modelo_exportado"
ARCHIVO_INFO_MODELO = "info_modelo.json"

MAPEO_COLUMNAS = {
    "sepal length (cm)": "largo_sepalo_cm",
    "sepal width (cm)": "ancho_sepalo_cm",
    "petal length (cm)": "largo_petalo_cm",
    "petal width (cm)": "ancho_petalo_cm",
}

ESPECIES = ["setosa", "versicolor", "virginica"]

TIPOS_SKOPS_CONFIABLES = ["sklearn.tree._tree.Tree"]  # seguridad skops: MLflow rechaza tipos no declarados (ver Unidad 2)

TIMEOUT_SALUD_MLFLOW_S = 3
