# Recopilación de Notebooks Completos - Proyecto SITOR

Este documento contiene el código fuente, las explicaciones (Markdown) y las salidas de consola de todos los cuadernos ejecutados durante el TFM.


---

# Notebook: 01_Auditoria_y_Deduplicacion.ipynb

Auditoría de Datos, EDA y Deduplicación

Este cuaderno implementa la Fase 1 del plan de choque. Antes de aplicar ninguna limpieza o hash difuso, realizamos un Análisis Exploratorio de Datos (EDA) estricto sobre los tres archivos `raw` originales para:
1. Validar la integridad de los esquemas (columnas) entre versiones.
2. Identificar variables de segmentación ignoradas en el pipeline anterior (ej. `business_type`).
3. Evaluar el solapamiento de registros entre los ficheros antes de la concatenación.

`python
import pandas as pd
from pathlib import Path

# Definición de rutas relativas asumiendo ejecución desde la carpeta /notebook
RUTA_RAW = Path("../data/raw")

archivos = {
    'v1_50': 'aa_dataset-tickets-multi-lang-5-2-50-version.csv',
    'v2_20k': 'dataset-tickets-multi-lang-4-20k.csv',
    'v3_4k': 'dataset-tickets-multi-lang3-4k.csv'
}

# Carga en memoria y auditoría de esquemas
dfs = {}
for nombre, archivo in archivos.items():
    ruta = RUTA_RAW / archivo
    if ruta.exists():
        # Usamos low_memory=False por si hay tipos mixtos en las columnas
        dfs[nombre] = pd.read_csv(ruta, low_memory=False)
        print(f"--- Dataset: {nombre} ---")
        print(f"Filas: {dfs[nombre].shape[0]} | Columnas: {dfs[nombre].shape[1]}")
        print(f"Esquema: {list(dfs[nombre].columns)}\n")
    else:
        print(f"Error: No se pudo localizar {ruta}")
`

**Salida (Output):**
`	ext
--- Dataset: v1_50 ---
Filas: 28587 | Columnas: 16
Esquema: ['subject', 'body', 'answer', 'type', 'queue', 'priority', 'language', 'version', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8']

--- Dataset: v2_20k ---
Filas: 20000 | Columnas: 15
Esquema: ['subject', 'body', 'answer', 'type', 'queue', 'priority', 'language', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8']

--- Dataset: v3_4k ---
Filas: 4000 | Columnas: 17
Esquema: ['subject', 'body', 'answer', 'type', 'queue', 'priority', 'language', 'business_type', 'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8', 'tag_9']
`

Auditoría de variables asimétricas y solapamiento

Inspeccionamos la distribución de `business_type` en el único fichero que la contiene para descartarla formalmente del pipeline por falta de soporte. 

A continuación, cuantificamos el solapamiento exacto de textos entre los tres ficheros originales. Esto medirá la cantidad de duplicados puros inyectados en el corpus antes siquiera de aplicar el Hash Difuso para los casi-duplicados.

`python
# Justificación para descartar business_type
print("--- Distribución de 'business_type' en v3_4k ---")
print(dfs['v3_4k']['business_type'].value_counts(dropna=False))

# Análisis de solapamiento exacto (fuga de datos estructural)
# Comparamos el contenido exacto de la columna 'body' ignorando nulos
cuerpos_v1 = set(dfs['v1_50']['body'].dropna())
cuerpos_v2 = set(dfs['v2_20k']['body'].dropna())
cuerpos_v3 = set(dfs['v3_4k']['body'].dropna())

print("\n--- Textos únicos por fichero ---")
print(f"Textos en v1_50: {len(cuerpos_v1)}")
print(f"Textos en v2_20k: {len(cuerpos_v2)}")
print(f"Textos en v3_4k:  {len(cuerpos_v3)}")

# Intersecciones
solap_v1_v2 = len(cuerpos_v1.intersection(cuerpos_v2))
solap_v1_v3 = len(cuerpos_v1.intersection(cuerpos_v3))
solap_v2_v3 = len(cuerpos_v2.intersection(cuerpos_v3))

print("\n--- Solapamiento cruzado ---")
print(f"Textos de v2_20k que ya están en v1_50: {solap_v1_v2}")
print(f"Textos de v3_4k que ya están en v1_50:  {solap_v1_v3}")
print(f"Textos de v3_4k que ya están en v2_20k: {solap_v2_v3}")
`

**Salida (Output):**
`	ext
--- Distribución de 'business_type' en v3_4k ---
business_type
IT Services                     1716
Tech Online Store               1395
IT Consulting Firm               391
Software Development Company     311
Online Store                     171
IT Consulting Service              7
Pit Services                       5
Adobe Photoshop 2024               2
_IT_Services_                      2
Name: count, dtype: int64

--- Textos únicos por fichero ---
Textos en v1_50: 28587
Textos en v2_20k: 19998
Textos en v3_4k:  3999

--- Solapamiento cruzado ---
Textos de v2_20k que ya están en v1_50: 8399
Textos de v3_4k que ya están en v1_50:  0
Textos de v3_4k que ya están en v2_20k: 0
`

Consolidación y Filtros de Dominio

Se unifican los ficheros proyectando únicamente las columnas estructurales compartidas. A continuación, se aplican los filtros de negocio para acotar el problema al dominio establecido: retención exclusiva de tickets en inglés y filtrado de las colas operativas del sector Telco. 

Por último, se aplica una deduplicación exacta sobre el texto completo (asunto y cuerpo) para eliminar el solapamiento inter-ficheros detectado y aligerar la carga computacional del posterior hash difuso.

`python
columnas_relevantes = ['subject', 'body', 'queue', 'type', 'priority', 'language']

# Proyección y concatenación
df_concat = pd.concat([
    dfs['v1_50'][columnas_relevantes],
    dfs['v2_20k'][columnas_relevantes],
    dfs['v3_4k'][columnas_relevantes]
], ignore_index=True)

# Tratamiento de nulos estructurales
df_concat['subject'] = df_concat['subject'].fillna('No Subject')
df_concat = df_concat.dropna(subset=['body'])

# Filtros de negocio (Inglés y Sector Telco)
df_telco = df_concat[df_concat['language'] == 'en'].copy()

colas_telco = [
    'Technical Support', 'Service Outages and Maintenance', 
    'Billing and Payments', 'Sales and Pre-Sales', 'Customer Service'
]
df_telco = df_telco[df_telco['queue'].isin(colas_telco)]
df_telco = df_telco.drop(columns=['language'])

# Fusión para evaluación de similitud
df_telco['full_text'] = df_telco['subject'] + ". " + df_telco['body']

# Deduplicación exacta (limpieza del solapamiento evidente)
vol_pre = len(df_telco)
df_telco = df_telco.drop_duplicates(subset=['full_text'], keep='first')
vol_post = len(df_telco)

print(f"Volumen unificado tras filtros de negocio: {vol_pre} tickets")
print(f"Volumen retenido tras deduplicación exacta: {vol_post} tickets")
print(f"Duplicados exactos destruidos: {vol_pre - vol_post}")
`

**Salida (Output):**
`	ext
Volumen unificado tras filtros de negocio: 18158 tickets
Volumen retenido tras deduplicación exacta: 15403 tickets
Duplicados exactos destruidos: 2755
`

Agrupación de Casi-Duplicados (Fuzzy Hashing)

Para evitar fugas de datos (Data Leakage) en las particiones de entrenamiento y test, se agrupan los tickets que comparten estructuras léxicas casi idénticas (plantillas). Se extraen n-gramas del cuerpo del ticket y se aplica el algoritmo MinHash con Locality-Sensitive Hashing (LSH) para detectar similitudes superiores al umbral establecido, asignando a cada ticket un identificador de clúster único.

`python
import re
# pip install datasketch
from datasketch import MinHash, MinHashLSH

def limpiar_texto_hash(texto):
    """Normalización estricta para la extracción de características del hash."""
    texto = str(texto).lower()
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.strip()

def obtener_shingles(texto, n_gram=3):
    """Tokenización por n-gramas solapados para capturar contexto estructural."""
    tokens = texto.split()
    if len(tokens) < n_gram:
        return set(tokens)
    return set([' '.join(tokens[i:i+n_gram]) for i in range(len(tokens) - n_gram + 1)])

UMBRAL_SIMILITUD = 0.85
NUM_PERM = 128

print(f"Generando firmas MinHash al {UMBRAL_SIMILITUD*100}% de similitud...")
lsh = MinHashLSH(threshold=UMBRAL_SIMILITUD, num_perm=NUM_PERM)
firmas = {}

# Reset de índice necesario para mapear correctamente con LSH
df_telco = df_telco.reset_index(drop=True)

# 1. Extracción e ingesta en LSH
for idx, row in df_telco.iterrows():
    texto_limpio = limpiar_texto_hash(row['body'])
    shingles = obtener_shingles(texto_limpio)
    
    m = MinHash(num_perm=NUM_PERM)
    for s in shingles:
        m.update(s.encode('utf8'))
        
    lsh.insert(str(idx), m)
    firmas[str(idx)] = m

# 2. Agrupación por vecindarios
print("Calculando intersecciones y asignando clústeres...")
visitados = set()
mapa_clusters = {}
id_cluster = 0

for idx in firmas.keys():
    if idx not in visitados:
        vecinos = lsh.query(firmas[idx])
        for v in vecinos:
            visitados.add(v)
            mapa_clusters[int(v)] = f"cluster_{id_cluster}"
        id_cluster += 1

df_telco['cluster_id'] = df_telco.index.map(mapa_clusters)

print(f"\n--- Resultados del Hash Difuso ---")
print(f"Tickets analizados: {len(df_telco)}")
print(f"Clústeres únicos (plantillas reales): {id_cluster}")
print(f"Reducción lograda: {len(df_telco) - id_cluster} tickets eran casi-duplicados")
`

**Salida (Output):**
`	ext
Generando firmas MinHash al 85.0% de similitud...
Calculando intersecciones y asignando clústeres...

--- Resultados del Hash Difuso ---
Tickets analizados: 15403
Clústeres únicos (plantillas reales): 15241
Reducción lograda: 162 tickets eran casi-duplicados
`

Construcción de la Variable Objetivo y Clases Minoritarias

Se concatena la jerarquía de tipificación para formar la clase objetivo completa (Cola + Tipo + Prioridad). Para garantizar la representatividad estadística en las particiones de los modelos de validación cruzada, se audita el soporte de cada clase contando el número de clústeres independientes, no los tickets individuales.

Las tripletas con un soporte inferior al umbral mínimo de validación se colapsan a la categoría genérica `OUT_OF_SCOPE`. Estas observaciones se evaluarán siempre como "no automatizables" en el simulador financiero.

`python
# Fusión de la clase objetivo
df_telco['target_tripleta'] = (
    df_telco['queue'].astype(str) + '_' + 
    df_telco['type'].astype(str) + '_' + 
    df_telco['priority'].astype(str)
)

# Auditoría de soporte basado estrictamente en la varianza estructural (clústeres)
soporte_por_clase = df_telco.groupby('target_tripleta')['cluster_id'].nunique()

MIN_SAMPLES = 20

clases_validas = soporte_por_clase[soporte_por_clase >= MIN_SAMPLES].index
clases_descartadas = soporte_por_clase[soporte_por_clase < MIN_SAMPLES].index

# Aplicación del colapso de clases raras
OUT_OF_SCOPE_LABEL = 'OUT_OF_SCOPE'
df_telco['target_tripleta'] = df_telco['target_tripleta'].apply(
    lambda x: x if x in clases_validas else OUT_OF_SCOPE_LABEL
)

# Resumen analítico
print(f"Total de combinaciones únicas observadas: {len(soporte_por_clase)}")
print(f"Clases retenidas (soporte >= {MIN_SAMPLES} clústeres): {len(clases_validas)}")
print(f"Clases descartadas por bajo soporte: {len(clases_descartadas)}")

out_of_scope_tickets = len(df_telco[df_telco['target_tripleta'] == OUT_OF_SCOPE_LABEL])
out_of_scope_pct = (out_of_scope_tickets / len(df_telco)) * 100

print(f"\nTickets desplazados a {OUT_OF_SCOPE_LABEL}: {out_of_scope_tickets} ({out_of_scope_pct:.2f}%)")

print("\nTop 5 Clases Mayoritarias:")
print(df_telco['target_tripleta'].value_counts().head())
`

**Salida (Output):**
`	ext
Total de combinaciones únicas observadas: 60
Clases retenidas (soporte >= 20 clústeres): 55
Clases descartadas por bajo soporte: 5

Tickets desplazados a OUT_OF_SCOPE: 71 (0.46%)

Top 5 Clases Mayoritarias:
target_tripleta
Technical Support_Incident_high      2262
Technical Support_Incident_medium    1115
Technical Support_Problem_high        884
Technical Support_Request_high        857
Customer Service_Request_medium       828
Name: count, dtype: int64
`

Exportación de la Capa Gold (Corpus de Entrenamiento)

Con la variable objetivo consolidada, el ruido estructural eliminado y el mapeo de clústeres para prevenir fugas de datos finalizado, se congela el estado del dataframe. 

Se proyectan únicamente las variables estrictamente necesarias para la tubería de Machine Learning (el texto unificado, la tripleta objetivo y el identificador de clúster) y se persiste en formato Parquet para garantizar compresión y tipado estricto en la lectura de los siguientes cuadernos.

`python
import os

# Creación de directorio si fue purgado
GOLD_DIR = "../data/gold"
os.makedirs(GOLD_DIR, exist_ok=True)

# Proyección de variables para entrenamiento
columnas_modelo = ['full_text', 'target_tripleta', 'cluster_id']
df_gold = df_telco[columnas_modelo].copy()

# Persistencia estática
ruta_export = os.path.join(GOLD_DIR, 'corpus_sitor_limpio.parquet')

# Usamos fastparquet (si da error, instala pip install fastparquet)
df_gold.to_parquet(ruta_export, engine='fastparquet', index=False)

print("--- Pipeline de Preparación Finalizado ---")
print(f"Ruta de exportación: {ruta_export}")
print(f"Total de registros listos para particionar: {len(df_gold)}")
`

**Salida (Output):**
`	ext
--- Pipeline de Preparación Finalizado ---
Ruta de exportación: ../data/gold\corpus_sitor_limpio.parquet
Total de registros listos para particionar: 15403
`


---

# Notebook: 02_Baselines_ML_Clasico.ipynb

Modelado de Línea Base (Baselines) y Vectorización Clásica

El objetivo de este cuaderno es establecer el rendimiento mínimo exigible (baseline) para el problema de clasificación de 55 tripletas. Si un modelo complejo (RoBERTa) no es capaz de batir con margen a estos modelos clásicos, la arquitectura profunda no estará justificada a nivel de negocio.

Para los algoritmos estadísticos (Regresión Logística y Random Forest), sí es estrictamente necesario aplicar limpieza de ruido gramatical y vectorización discreta. Se utilizará TF-IDF extrayendo unigramas y bigramas, descartando palabras vacías (stopwords). 

El vector objetivo será la tripleta y la estrategia de partición respetará los clústeres calculados en la Fase 1 mediante GroupKFold para impedir la fuga de datos.

`python
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

# Ingesta estricta de la Capa Gold
RUTA_GOLD = Path("../data/gold/corpus_sitor_limpio.parquet")

if not RUTA_GOLD.exists():
    raise FileNotFoundError("El corpus gold no existe. Debes ejecutar el notebook 01 previamente.")

df_gold = pd.read_parquet(RUTA_GOLD)

print("--- Auditoría de Ingesta Gold ---")
print(f"Total de registros: {len(df_gold)}")
print(f"Clases a predecir: {df_gold['target_tripleta'].nunique()}")
print(f"Clústeres (Grupos independientes): {df_gold['cluster_id'].nunique()}")

# Codificación del Target (Etiquetas de texto a enteros)
le = LabelEncoder()
y_encoded = le.fit_transform(df_gold['target_tripleta'])
grupos = df_gold['cluster_id']

# Vectorización Matemática para ML Clásico
print("\nTransformando texto a espacio vectorial TF-IDF...")
vectorizador = TfidfVectorizer(
    max_features=5000, 
    stop_words='english', 
    ngram_range=(1, 2)
)

X_tfidf = vectorizador.fit_transform(df_gold['full_text'])

print(f"Dimensiones de Matriz X (Features): {X_tfidf.shape}")
print(f"Dimensiones de Vector y (Target): {y_encoded.shape}")
`

**Salida (Output):**
`	ext
--- Auditoría de Ingesta Gold ---
Total de registros: 15403
Clases a predecir: 56
Clústeres (Grupos independientes): 15241

Transformando texto a espacio vectorial TF-IDF...
Dimensiones de Matriz X (Features): (15403, 5000)
Dimensiones de Vector y (Target): (15403,)
`

Evaluación Robusta de Línea Base (Baselines)

Para obtener una estimación insesgada del rendimiento de los algoritmos clásicos, se implementa una validación cruzada anidada lógica mediante `StratifiedGroupKFold` (5 particiones). 

Este particionador resuelve los dos problemas estructurales del dataset de forma simultánea:
* `Stratified`: Mantiene la proporción de las 56 clases en cada fold, vital dado el extremo desbalanceo.
* `Group`: Obliga a que todos los tickets de un mismo `cluster_id` (plantilla) caigan en la misma partición (entrenamiento o validación), cerrando definitivamente cualquier fuga de datos por similitud léxica.

Se evalúa Regresión Logística y Random Forest penalizando a las clases mayoritarias (`class_weight='balanced'`) y monitorizando la métrica F1-Macro, que es el indicador real de rendimiento en matrices desbalanceadas.

`python
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import warnings

# Suprimimos warnings de clases raras cayendo en un solo fold temporalmente
warnings.filterwarnings('ignore', category=UserWarning)

print("Inicializando StratifiedGroupKFold (K=5)...")
cv_strategy = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)

modelos = {
    "Regresion_Logistica": LogisticRegression(
        class_weight='balanced', 
        max_iter=1000, 
        random_state=42,
        n_jobs=-1
    ),
    "Random_Forest": RandomForestClassifier(
        n_estimators=100, 
        class_weight='balanced', 
        max_depth=30, # Acotamos profundidad para evitar overfitting masivo en TF-IDF
        random_state=42,
        n_jobs=-1
    )
}

resultados_cv = []

for nombre, modelo in modelos.items():
    print(f"\nEjecutando Cross-Validation para: {nombre}...")
    
    scores = cross_validate(
        estimator=modelo, 
        X=X_tfidf, 
        y=y_encoded, 
        groups=grupos, 
        cv=cv_strategy,
        scoring=['accuracy', 'f1_macro'],
        return_train_score=False,
        n_jobs=1 # Ejecución secuencial de particiones para proteger la RAM local
    )
    
    acc_mean = np.mean(scores['test_accuracy'])
    f1_mean = np.mean(scores['test_f1_macro'])
    
    print(f"[{nombre}] Accuracy: {acc_mean:.4f} | F1-Macro: {f1_mean:.4f}")
    
    resultados_cv.append({
        'Modelo': nombre,
        'Accuracy': acc_mean,
        'F1_Macro': f1_mean
    })

df_resumen = pd.DataFrame(resultados_cv).sort_values(by='F1_Macro', ascending=False)
print("\n--- Rendimiento Definitivo de Línea Base ---")
display(df_resumen)
`

**Salida (Output):**
`	ext
Inicializando StratifiedGroupKFold (K=5)...

Ejecutando Cross-Validation para: Regresion_Logistica...
d:\MasterEvolve\Proyecto TFM\SITOR\.venv\Lib\site-packages\sklearn\linear_model\_logistic.py:1457: FutureWarning: 'n_jobs' has no effect since 1.8 and will be removed in 1.10. You provided 'n_jobs=-1', please leave it unspecified.
  warnings.warn(msg, category=FutureWarning)
d:\MasterEvolve\Proyecto TFM\SITOR\.venv\Lib\site-packages\sklearn\linear_model\_logistic.py:1457: FutureWarning: 'n_jobs' has no effect since 1.8 and will be removed in 1.10. You provided 'n_jobs=-1', please leave it unspecified.
  warnings.warn(msg, category=FutureWarning)
d:\MasterEvolve\Proyecto TFM\SITOR\.venv\Lib\site-packages\sklearn\linear_model\_logistic.py:1457: FutureWarning: 'n_jobs' has no effect since 1.8 and will be removed in 1.10. You provided 'n_jobs=-1', please leave it unspecified.
  warnings.warn(msg, category=FutureWarning)
d:\MasterEvolve\Proyecto TFM\SITOR\.venv\Lib\site-packages\sklearn\linear_model\_logistic.py:1457: FutureWarning: 'n_jobs' has no effect since 1.8 and will be removed in 1.10. You provided 'n_jobs=-1', please leave it unspecified.
  warnings.warn(msg, category=FutureWarning)
d:\MasterEvolve\Proyecto TFM\SITOR\.venv\Lib\site-packages\sklearn\linear_model\_logistic.py:1457: FutureWarning: 'n_jobs' has no effect since 1.8 and will be removed in 1.10. You provided 'n_jobs=-1', please leave it unspecified.
  warnings.warn(msg, category=FutureWarning)
[Regresion_Logistica] Accuracy: 0.3543 | F1-Macro: 0.4071

Ejecutando Cross-Validation para: Random_Forest...
[Random_Forest] Accuracy: 0.3923 | F1-Macro: 0.4395

--- Rendimiento Definitivo de Línea Base ---
                Modelo  Accuracy  F1_Macro
1        Random_Forest  0.392325  0.439457
0  Regresion_Logistica  0.354281  0.407052
`

Auditoría de Degradación por Clases

Para documentar empíricamente las limitaciones de los enfoques basados en bolsa de palabras (Bag of Words / TF-IDF) frente a problemas de alta cardinalidad, se aísla una partición estática de validación (Hold-out 80/20) respetando la agrupación por plantillas. 

Se evalúa el modelo ganador (Random Forest) generando un reporte de clasificación detallado. El objetivo es evidenciar el colapso de la métrica F1-Score en las tripletas minoritarias y justificar la transición a arquitecturas de Deep Learning con comprensión semántica.

`python
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report

# Extraemos una partición estática 80/20 protegiendo los clústeres
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X_tfidf, y_encoded, groups=grupos))

X_train, X_test = X_tfidf[train_idx], X_tfidf[test_idx]
y_train, y_test = y_encoded[train_idx], y_encoded[test_idx]

print(f"Entrenando Random Forest de auditoría (Train: {len(y_train)} | Test: {len(y_test)})...")

rf_audit = RandomForestClassifier(
    n_estimators=100, 
    class_weight='balanced', 
    max_depth=30,
    random_state=42,
    n_jobs=-1
)

rf_audit.fit(X_train, y_train)
y_pred = rf_audit.predict(X_test)

# Mapeamos las clases que realmente existen en el set de test para evitar desajustes
clases_en_test = np.unique(y_test)
nombres_clases = le.inverse_transform(clases_en_test)

reporte = classification_report(
    y_test, 
    y_pred, 
    target_names=nombres_clases,
    zero_division=0
)

print("\n--- Reporte de Clasificación Detallado (Random Forest) ---")
print(reporte)
`

**Salida (Output):**
`	ext
Entrenando Random Forest de auditoría (Train: 12323 | Test: 3080)...

--- Reporte de Clasificación Detallado (Random Forest) ---
                                                 precision    recall  f1-score   support

               Billing and Payments_Change_high       0.93      0.88      0.90        16
                Billing and Payments_Change_low       1.00      1.00      1.00         7
             Billing and Payments_Change_medium       0.57      0.67      0.62         6
             Billing and Payments_Incident_high       0.67      0.56      0.61        39
              Billing and Payments_Incident_low       0.75      0.52      0.62        23
           Billing and Payments_Incident_medium       0.49      0.58      0.53        50
              Billing and Payments_Problem_high       0.69      0.75      0.72        32
               Billing and Payments_Problem_low       0.72      0.57      0.64        37
            Billing and Payments_Problem_medium       0.58      0.51      0.54        57
              Billing and Payments_Request_high       0.64      0.44      0.52        66
               Billing and Payments_Request_low       0.59      0.52      0.55        58
            Billing and Payments_Request_medium       0.62      0.33      0.43       133
                   Customer Service_Change_high       0.31      0.71      0.43         7
                    Customer Service_Change_low       0.36      0.62      0.46        13
                 Customer Service_Change_medium       0.55      0.72      0.63        29
                 Customer Service_Incident_high       0.40      0.53      0.46        45
                  Customer Service_Incident_low       0.42      0.48      0.45        71
               Customer Service_Incident_medium       0.29      0.27      0.28        83
                  Customer Service_Problem_high       0.26      0.52      0.35        21
                   Customer Service_Problem_low       0.44      0.48      0.46        58
                Customer Service_Problem_medium       0.35      0.39      0.37        88
                  Customer Service_Request_high       0.24      0.45      0.31        58
                   Customer Service_Request_low       0.42      0.43      0.43       105
                Customer Service_Request_medium       0.48      0.29      0.37       164
                                   OUT_OF_SCOPE       0.30      0.25      0.27        12
                Sales and Pre-Sales_Change_high       0.30      0.38      0.33         8
                 Sales and Pre-Sales_Change_low       0.46      0.75      0.57         8
              Sales and Pre-Sales_Change_medium       0.30      0.27      0.29        11
               Sales and Pre-Sales_Incident_low       0.24      0.80      0.36        10
            Sales and Pre-Sales_Incident_medium       0.19      0.57      0.29        21
                Sales and Pre-Sales_Problem_low       0.24      1.00      0.39         7
             Sales and Pre-Sales_Problem_medium       0.15      0.67      0.25         6
               Sales and Pre-Sales_Request_high       0.43      0.67      0.53        15
                Sales and Pre-Sales_Request_low       0.18      0.52      0.27        21
             Sales and Pre-Sales_Request_medium       0.40      0.49      0.44        35
    Service Outages and Maintenance_Change_high       0.40      0.58      0.47        24
     Service Outages and Maintenance_Change_low       0.25      0.80      0.38         5
  Service Outages and Maintenance_Change_medium       0.38      0.60      0.46         5
  Service Outages and Maintenance_Incident_high       0.38      0.81      0.52        78
   Service Outages and Maintenance_Incident_low       0.65      0.81      0.72        16
Service Outages and Maintenance_Incident_medium       0.50      0.64      0.56        22
   Service Outages and Maintenance_Problem_high       0.25      0.40      0.31         5
   Service Outages and Maintenance_Request_high       0.23      0.40      0.29        20
 Service Outages and Maintenance_Request_medium       0.30      0.50      0.38         6
                  Technical Support_Change_high       0.53      0.76      0.62        62
                   Technical Support_Change_low       0.38      0.46      0.41        13
                Technical Support_Change_medium       0.64      0.58      0.61        31
                Technical Support_Incident_high       0.56      0.21      0.31       454
                 Technical Support_Incident_low       0.24      0.44      0.31       101
              Technical Support_Incident_medium       0.36      0.23      0.28       226
                 Technical Support_Problem_high       0.31      0.25      0.28       144
                  Technical Support_Problem_low       0.32      0.57      0.41        44
               Technical Support_Problem_medium       0.27      0.33      0.30        97
                 Technical Support_Request_high       0.52      0.35      0.41       185
                  Technical Support_Request_low       0.27      0.50      0.35        34
               Technical Support_Request_medium       0.35      0.33      0.34        88

                                       accuracy                           0.40      3080
                                      macro avg       0.43      0.54      0.45      3080
                                   weighted avg       0.45      0.40      0.40      3080
`


---

# Notebook: 03_Entrenamiento_RoBERTa.ipynb

# Aprovisionamiento de Hardware, Conexión a Drive e Ingesta de Datos

Este bloque verifica la asignación del acelerador gráfico y monta el sistema de archivos persistente. Es obligatorio ejecutar este cuaderno en un entorno con GPU. Una vez montado, se ingesta el corpus maestro y se extrae el vector de etiquetas operativas puras para el orquestador neuronal.

`python
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
from google.colab import drive

# Auditoría de Hardware
dispositivo = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if dispositivo.type == 'cpu':
    raise SystemError("CRÍTICO: Entorno sin GPU detectado. Deteniendo ejecución para evitar saturación de memoria RAM.")
else:
    print(f"Acelerador gráfico activo: {torch.cuda.get_device_name(0)}")

# Conexión persistente a Google Drive
print("\nConectando con Google Drive...")
drive.mount('/content/drive')

# Rutas persistentes
BASE_DIR = Path('/content/drive/MyDrive/MasterEvolve/Proyecto TFM/SITOR')
RUTA_GOLD = BASE_DIR / "data" / "gold" / "corpus_sitor_limpio.parquet"
DIR_MODELOS = BASE_DIR / "src" / "models" / "roberta_corporativo"
DIR_METRICAS = BASE_DIR / "metrics"

DIR_MODELOS.mkdir(parents=True, exist_ok=True)
DIR_METRICAS.mkdir(parents=True, exist_ok=True)

if not RUTA_GOLD.exists():
    raise FileNotFoundError(f"No se encuentra la ruta: {RUTA_GOLD}.")

# Ingesta
df = pd.read_parquet(RUTA_GOLD)
print(f"\nCorpus inyectado directamente desde Drive.")
print(f"Volumen: {len(df)} registros")

# Codificación de la Tripleta Objetivo
le = LabelEncoder()
df['label_id'] = le.fit_transform(df['target_tripleta'])
print(f"Clases únicas a predecir: {len(le.classes_)}")
`

**Salida (Output):**
`	ext
Acelerador gráfico activo: NVIDIA A100-SXM4-80GB

Conectando con Google Drive...
Mounted at /content/drive

Corpus inyectado directamente desde Drive.
Volumen: 15403 registros
Clases únicas a predecir: 56
`

# Tokenización y Construcción del Dataset (PyTorch)

Los modelos Transformer no consumen matrices dispersas (TF-IDF), sino secuencias densas de tokens enteros. Instanciamos el tokenizador de `roberta-base`.

Se define una clase heredada de `torch.utils.data.Dataset` para la ingesta eficiente. Fijamos la longitud de contexto en `MAX_LEN = 256` truncando el texto sobrante. En el dominio de soporte técnico, la anomalía o urgencia suele describirse en las primeras líneas; 256 tokens capturan esta señal sin desperdiciar VRAM. Además, exportamos el mapeo de clases para garantizar la trazabilidad operativa en inferencia.

`python
import json
import torch
from transformers import AutoTokenizer
from torch.utils.data import Dataset

# 1. Extracción y sellado del mapeo de clases (Imprescindible para producción)
id2label = {int(idx): str(label) for idx, label in enumerate(le.classes_)}
label2id = {v: k for k, v in id2label.items()}

with open(DIR_MODELOS / "label_mapping.json", "w", encoding="utf-8") as f:
    json.dump(id2label, f, indent=4)
print(f"Diccionario de etiquetas (56 clases) sellado en: {DIR_MODELOS / 'label_mapping.json'}")

# 2. Descarga del Tokenizador
print("\nDescargando tokenizador: roberta-base...")
tokenizer = AutoTokenizer.from_pretrained("roberta-base")
# Guardamos también el tokenizador en nuestro directorio para inferencia offline
tokenizer.save_pretrained(DIR_MODELOS)
print("Tokenizador guardado localmente.")

# 3. Construcción del motor de ingesta (Dataset)
class SitorDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=256):
        self.texts = texts.tolist() if isinstance(texts, pd.Series) else texts
        self.labels = labels.tolist() if isinstance(labels, pd.Series) else labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        texto = str(self.texts[idx])
        etiqueta = self.labels[idx]

        # Tokenización on-the-fly
        encoding = self.tokenizer(
            texto,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(etiqueta, dtype=torch.long)
        }

print("\nClase SitorDataset definida correctamente.")
`

**Salida (Output):**
`	ext
Diccionario de etiquetas (56 clases) sellado en: /content/drive/MyDrive/MasterEvolve/Proyecto TFM/SITOR/src/models/roberta_corporativo/label_mapping.json

Descargando tokenizador: roberta-base...
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
WARNING:huggingface_hub.utils._http:Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
config.json:   0%|          | 0.00/481 [00:00<?, ?B/s]tokenizer_config.json:   0%|          | 0.00/25.0 [00:00<?, ?B/s]vocab.json:   0%|          | 0.00/899k [00:00<?, ?B/s]merges.txt:   0%|          | 0.00/456k [00:00<?, ?B/s]tokenizer.json:   0%|          | 0.00/1.36M [00:00<?, ?B/s]Tokenizador guardado localmente.

Clase SitorDataset definida correctamente.
`

# Orquestador Neuronal K-Fold con Validación Anidada (Fuga Cero y OOM Safe)

Para mantener la dinámica de convergencia óptima sin incurrir en fugas de datos (Data Leakage), se implementa una arquitectura de validación anidada.

La partición principal del `StratifiedGroupKFold` aísla un conjunto *Out-Of-Fold* (OOF) estrictamente ciego. Internamente, la porción de entrenamiento se sub-divide (90/10). El 10% resultante se inyecta como conjunto de monitoreo para el `EarlyStoppingCallback`. Se ha añadido una lógica de repliegue (fallback) en esta subdivisión: si el desbalanceo extremo deja a la clase minoritaria con menos de dos instancias en el pliegue, se desactiva temporalmente la estratificación para evitar colapsos (ValueError) en Scikit-Learn.

A nivel de negocio, el orquestador monitorea el `eval_accuracy` en lugar de la pérdida cruzada, priorizando la automatización del volumen masivo de tickets.

A nivel de infraestructura, el bucle incluye un limpiador explícito de memoria de vídeo (vaciado de caché CUDA y recolección de basura de PyTorch) al final de cada iteración, garantizando que los tensores residuales no provoquen un error `Out of Memory` (OOM) en la A100.

Finalmente, las métricas de rendimiento real se extraen evaluando el modelo restaurado contra el conjunto OOF virgen, reportando estimadores insesgados (cuasi-desviación estándar) para auditar la estabilidad operativa tanto en clases mayoritarias como en el long-tail.

`python
import gc
import torch
import numpy as np
from sklearn.model_selection import StratifiedGroupKFold, train_test_split
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer, EarlyStoppingCallback

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    acc = accuracy_score(labels, preds)
    f1_macro = f1_score(labels, preds, average='macro')
    f1_weighted = f1_score(labels, preds, average='weighted')
    return {'accuracy': acc, 'f1_macro': f1_macro, 'f1_weighted': f1_weighted}

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
splits = list(cv.split(df['full_text'], df['label_id'], groups=df['cluster_id']))

metricas_cv = []
EPOCHS_FINAL = 20

for fold, (train_idx, val_idx) in enumerate(splits):
    print(f"\n{'='*50}")
    print(f" Iniciando Entrenamiento Anidado - Fold {fold + 1}/5")
    print(f"{'='*50}")

    train_data_full = df.iloc[train_idx]
    val_data_oof = df.iloc[val_idx]

    # Lógica de fallback para proteger contra el desbalanceo extremo
    min_class_count = train_data_full['label_id'].value_counts().min()

    if min_class_count < 2:
        print(f" [!] Fallback activo: La clase más rara tiene {min_class_count} instancias.")
        print(f" [!] Desactivando estratificación en el particionado interno.")
        train_inner, val_inner = train_test_split(
            train_data_full,
            test_size=0.10,
            random_state=42
        )
    else:
        train_inner, val_inner = train_test_split(
            train_data_full,
            test_size=0.10,
            stratify=train_data_full['label_id'],
            random_state=42
        )

    print(f"Volumetrías del Fold:")
    print(f" - Entrenamiento puro: {len(train_inner)} tickets")
    print(f" - Monitoreo interno (Early Stopping): {len(val_inner)} tickets")
    print(f" - Evaluación ciega (OOF): {len(val_data_oof)} tickets")

    train_dataset = SitorDataset(train_inner['full_text'], train_inner['label_id'], tokenizer)
    val_inner_dataset = SitorDataset(val_inner['full_text'], val_inner['label_id'], tokenizer)
    val_oof_dataset = SitorDataset(val_data_oof['full_text'], val_data_oof['label_id'], tokenizer)

    modelo = AutoModelForSequenceClassification.from_pretrained(
        "roberta-base",
        num_labels=len(le.classes_)
    ).to(dispositivo)

    # Configuración de entrenamiento orientada a volumen (Accuracy)
    args = TrainingArguments(
        output_dir=str(DIR_MODELOS / f"checkpoints_fold_{fold + 1}"),
        num_train_epochs=EPOCHS_FINAL,
        per_device_train_batch_size=16,
        learning_rate=2e-5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_accuracy", # CORRECCIÓN: Optimizar a volumen
        logging_steps=100,
        save_total_limit=1,
        report_to="none"
    )

    trainer = Trainer(
        model=modelo,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=val_inner_dataset,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
        compute_metrics=compute_metrics
    )

    print("\nOptimizando pesos...")
    trainer.train()

    print("\nEvaluando partición OOF (Verdadera capacidad de generalización)...")
    metricas = trainer.evaluate(eval_dataset=val_oof_dataset)
    print(metricas)
    metricas_cv.append(metricas)

    if fold == 4:
        ruta_final = str(DIR_MODELOS / "roberta_corporativo_final")
        trainer.save_model(ruta_final)
        print(f"\nModelo de producción sellado en: {ruta_final}")

    # =====================================================================
    # PREVENCIÓN DE COLAPSO (OOM) EN PYTORCH
    # =====================================================================
    del modelo
    del trainer
    del train_dataset
    del val_inner_dataset
    del val_oof_dataset
    gc.collect()
    torch.cuda.empty_cache()


# =====================================================================
# AUDITORÍA FORENSE FINAL
# =====================================================================

acc_folds = [m['eval_accuracy'] for m in metricas_cv]
f1_macro_folds = [m['eval_f1_macro'] for m in metricas_cv]

acc_mean = np.mean(acc_folds)
acc_std = np.std(acc_folds, ddof=1)

f1_mean = np.mean(f1_macro_folds)
f1_std = np.std(f1_macro_folds, ddof=1)

print("\n" + "="*50)
print(" RENDIMIENTO ESTADÍSTICO (K-FOLD CV)")
print("="*50)
print(f"Accuracy Medio K-Fold:  {acc_mean:.4f} ± {acc_std:.4f}")
print(f"F1-Macro Medio K-Fold:  {f1_mean:.4f} ± {f1_std:.4f}")

inestabilidad_detectada = False

if acc_std > 0.05:
    print("\nADVERTENCIA (Mayoritaria): Alta varianza en Accuracy. Inestabilidad en la predicción de volumen.")
    inestabilidad_detectada = True

if f1_std > 0.05:
    print("\nADVERTENCIA (Minoritaria): Alta varianza en F1-Macro. La red es errática aprendiendo las clases raras.")
    inestabilidad_detectada = True

if not inestabilidad_detectada:
    print("\nESTABILIDAD CONFIRMADA: La red neuronal converge de forma robusta tanto en clases mayoritarias como en el long-tail.")
`

**Salida (Output):**
`	ext
==================================================
 Iniciando Entrenamiento Anidado - Fold 1/5
==================================================
Volumetrías del Fold:
 - Entrenamiento puro: 11092 tickets
 - Monitoreo interno (Early Stopping): 1233 tickets
 - Evaluación ciega (OOF): 3078 tickets
model.safetensors: reconstructing file:   0%|          |  0.00B /  499MB            model.safetensors: downloading bytes:           |  0.00B            Loading weights:   0%|          | 0/197 [00:00<?, ?it/s][transformers] [1mRobertaForSequenceClassification LOAD REPORT[0m from: roberta-base
Key                        | Status     | 
---------------------------+------------+-
lm_head.dense.bias         | UNEXPECTED | 
lm_head.layer_norm.weight  | UNEXPECTED | 
lm_head.layer_norm.bias    | UNEXPECTED | 
lm_head.dense.weight       | UNEXPECTED | 
lm_head.bias               | UNEXPECTED | 
classifier.out_proj.bias   | MISSING    | 
classifier.dense.weight    | MISSING    | 
classifier.dense.bias      | MISSING    | 
classifier.out_proj.weight | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.

Optimizando pesos...
<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Evaluando partición OOF (Verdadera capacidad de generalización)...
<IPython.core.display.HTML object><IPython.core.display.HTML object>{'eval_loss': 2.2767796516418457, 'eval_accuracy': 0.5795971410006497, 'eval_f1_macro': 0.5645393260280769, 'eval_f1_weighted': 0.5799206085268825}

==================================================
 Iniciando Entrenamiento Anidado - Fold 2/5
==================================================
Volumetrías del Fold:
 - Entrenamiento puro: 11090 tickets
 - Monitoreo interno (Early Stopping): 1233 tickets
 - Evaluación ciega (OOF): 3080 tickets
Loading weights:   0%|          | 0/197 [00:00<?, ?it/s][transformers] [1mRobertaForSequenceClassification LOAD REPORT[0m from: roberta-base
Key                        | Status     | 
---------------------------+------------+-
lm_head.dense.bias         | UNEXPECTED | 
lm_head.layer_norm.weight  | UNEXPECTED | 
lm_head.layer_norm.bias    | UNEXPECTED | 
lm_head.dense.weight       | UNEXPECTED | 
lm_head.bias               | UNEXPECTED | 
classifier.out_proj.bias   | MISSING    | 
classifier.dense.weight    | MISSING    | 
classifier.dense.bias      | MISSING    | 
classifier.out_proj.weight | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.

Optimizando pesos...
<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Evaluando partición OOF (Verdadera capacidad de generalización)...
<IPython.core.display.HTML object><IPython.core.display.HTML object>{'eval_loss': 2.268331527709961, 'eval_accuracy': 0.5918831168831169, 'eval_f1_macro': 0.5618430898772779, 'eval_f1_weighted': 0.593146927601249}

==================================================
 Iniciando Entrenamiento Anidado - Fold 3/5
==================================================
Volumetrías del Fold:
 - Entrenamiento puro: 11090 tickets
 - Monitoreo interno (Early Stopping): 1233 tickets
 - Evaluación ciega (OOF): 3080 tickets
Loading weights:   0%|          | 0/197 [00:00<?, ?it/s][transformers] [1mRobertaForSequenceClassification LOAD REPORT[0m from: roberta-base
Key                        | Status     | 
---------------------------+------------+-
lm_head.dense.bias         | UNEXPECTED | 
lm_head.layer_norm.weight  | UNEXPECTED | 
lm_head.layer_norm.bias    | UNEXPECTED | 
lm_head.dense.weight       | UNEXPECTED | 
lm_head.bias               | UNEXPECTED | 
classifier.out_proj.bias   | MISSING    | 
classifier.dense.weight    | MISSING    | 
classifier.dense.bias      | MISSING    | 
classifier.out_proj.weight | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.

Optimizando pesos...
<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Evaluando partición OOF (Verdadera capacidad de generalización)...
<IPython.core.display.HTML object><IPython.core.display.HTML object>{'eval_loss': 2.281916379928589, 'eval_accuracy': 0.5782467532467532, 'eval_f1_macro': 0.5239691783931658, 'eval_f1_weighted': 0.577370651567094}

==================================================
 Iniciando Entrenamiento Anidado - Fold 4/5
==================================================
Volumetrías del Fold:
 - Entrenamiento puro: 11093 tickets
 - Monitoreo interno (Early Stopping): 1233 tickets
 - Evaluación ciega (OOF): 3077 tickets
Loading weights:   0%|          | 0/197 [00:00<?, ?it/s][transformers] [1mRobertaForSequenceClassification LOAD REPORT[0m from: roberta-base
Key                        | Status     | 
---------------------------+------------+-
lm_head.dense.bias         | UNEXPECTED | 
lm_head.layer_norm.weight  | UNEXPECTED | 
lm_head.layer_norm.bias    | UNEXPECTED | 
lm_head.dense.weight       | UNEXPECTED | 
lm_head.bias               | UNEXPECTED | 
classifier.out_proj.bias   | MISSING    | 
classifier.dense.weight    | MISSING    | 
classifier.dense.bias      | MISSING    | 
classifier.out_proj.weight | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.

Optimizando pesos...
<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Evaluando partición OOF (Verdadera capacidad de generalización)...
<IPython.core.display.HTML object><IPython.core.display.HTML object>{'eval_loss': 2.2671432495117188, 'eval_accuracy': 0.5885602859928502, 'eval_f1_macro': 0.5489069280474441, 'eval_f1_weighted': 0.5850434215247491}

==================================================
 Iniciando Entrenamiento Anidado - Fold 5/5
==================================================
Volumetrías del Fold:
 - Entrenamiento puro: 11083 tickets
 - Monitoreo interno (Early Stopping): 1232 tickets
 - Evaluación ciega (OOF): 3088 tickets
Loading weights:   0%|          | 0/197 [00:00<?, ?it/s][transformers] [1mRobertaForSequenceClassification LOAD REPORT[0m from: roberta-base
Key                        | Status     | 
---------------------------+------------+-
lm_head.dense.bias         | UNEXPECTED | 
lm_head.layer_norm.weight  | UNEXPECTED | 
lm_head.layer_norm.bias    | UNEXPECTED | 
lm_head.dense.weight       | UNEXPECTED | 
lm_head.bias               | UNEXPECTED | 
classifier.out_proj.bias   | MISSING    | 
classifier.dense.weight    | MISSING    | 
classifier.dense.bias      | MISSING    | 
classifier.out_proj.weight | MISSING    | 

Notes:
- UNEXPECTED:	can be ignored when loading from different task/architecture; not ok if you expect identical arch.
- MISSING:	those params were newly initialized because missing from the checkpoint. Consider training on your downstream task.

Optimizando pesos...
<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]<IPython.core.display.HTML object>Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Evaluando partición OOF (Verdadera capacidad de generalización)...
<IPython.core.display.HTML object><IPython.core.display.HTML object>{'eval_loss': 2.066459894180298, 'eval_accuracy': 0.6026554404145078, 'eval_f1_macro': 0.5304542144658183, 'eval_f1_weighted': 0.6004383869271307}
Writing model shards:   0%|          | 0/1 [00:00<?, ?it/s]
Modelo de producción sellado en: /content/drive/MyDrive/MasterEvolve/Proyecto TFM/SITOR/src/models/roberta_corporativo/roberta_corporativo_final

==================================================
 RENDIMIENTO ESTADÍSTICO (K-FOLD CV)
==================================================
Accuracy Medio K-Fold:  0.5882 ± 0.0099
F1-Macro Medio K-Fold:  0.5459 ± 0.0182

ESTABILIDAD CONFIRMADA: La red neuronal converge de forma robusta tanto en clases mayoritarias como en el long-tail.
`


---

# Notebook: 04_Evaluacion_Marginal_y_ROI.ipynb

# Evaluación del Modelo, Calibración Térmica y Extracción del Hold-Out

Este cuaderno ejecuta la auditoría final del modelo RoBERTa corporativo sobre el conjunto Hold-Out (Fold 5) estrictamente invisible durante el entrenamiento.

Dado que el particionado en el entrenamiento se realizó mediante `StratifiedGroupKFold` para evitar la fuga de datos por repetición de `INCIDENT_ID`, se reproduce iterativamente el mismo generador pseudoaleatorio (`random_state=42`) sobre el corpus maestro (`corpus_sitor_limpio.parquet`) para aislar matemáticamente los mismos tickets de test.

Se implementa además una calibración térmica mediante el optimizador L-BFGS (Broyden–Fletcher–Goldfarb–Shanno). Las redes neuronales profundas tienden a sufrir de *overconfidence* en sus *logits* de salida. L-BFGS escala la distribución térmica minimizando la función de pérdida empírica (Negative Log-Likelihood) sobre el Hold-Out, garantizando que el Softmax refleje probabilidades frecuentistas reales antes de inyectarlas en el simulador financiero.

`python
import json
import torch
import torch.nn.functional as F
import pandas as pd
import numpy as np
import scipy.optimize as optim
from pathlib import Path
from tqdm import tqdm
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from google.colab import drive
import warnings
warnings.filterwarnings('ignore')

# 1. Montaje de Entorno Cloud
drive.mount('/content/drive')
BASE_DIR = Path('/content/drive/MyDrive/MasterEvolve/Proyecto TFM/SITOR')

RUTA_GOLD = BASE_DIR / "data" / "gold" / "corpus_sitor_limpio.parquet"
DIR_RAIZ_MODELO = BASE_DIR / "src" / "models" / "roberta_corporativo"
DIR_PESOS = DIR_RAIZ_MODELO / "roberta_corporativo_final"
RUTA_MAPPING = DIR_RAIZ_MODELO / "label_mapping.json"

# Sanity Check de Arquitectura
if not DIR_PESOS.exists():
    raise FileNotFoundError(f"🚨 FATAL: No se encuentran los pesos en {DIR_PESOS}")

# 2. Reconstrucción Aislada del Fold 5
print("Cargando corpus maestro...")
df_gold = pd.read_parquet(RUTA_GOLD)

le = LabelEncoder()
target_encoded = le.fit_transform(df_gold['target_tripleta'])

# CORRECCIÓN: Agrupamos por cluster_id tal y como se hizo en el Notebook 03
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
splits = list(sgkf.split(df_gold, target_encoded, groups=df_gold['cluster_id']))

train_idx, test_idx = splits[4]
df_test = df_gold.iloc[test_idx].copy()
print(f"Conjunto Hold-Out (Fold 5) extraído matemáticamente: {len(df_test)} tickets puros.")

# 3. Arranque del Motor de Inferencia en GPU
dispositivo = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Motor de inferencia levantado en: {dispositivo}")
if dispositivo.type == 'cpu':
    print("⚠️ AVISO: Estás corriendo en CPU. Asegúrate de poner el entorno en T4 GPU.")

tokenizer = AutoTokenizer.from_pretrained(DIR_RAIZ_MODELO)
modelo = AutoModelForSequenceClassification.from_pretrained(DIR_PESOS).to(dispositivo)
modelo.eval()

with open(RUTA_MAPPING, "r", encoding="utf-8") as f:
    id2label = {int(k): v for k, v in json.load(f).items()}

# 4. Extracción de Logits Crudos (Batch Inferencia)
print("\nExtrayendo logits crudos del modelo sobre Hold-Out...")
textos = df_test['full_text'].tolist()
# Mapeo invertido de string a índice usando el JSON
label2id = {v: k for k, v in id2label.items()}
labels = df_test['target_tripleta'].map(lambda x: label2id[x]).tolist()

logits_list = []
batch_size = 32

for i in tqdm(range(0, len(textos), batch_size), desc="Procesando tensores"):
    batch_text = textos[i:i+batch_size]
    inputs = tokenizer(batch_text, padding=True, truncation=True, max_length=256, return_tensors="pt").to(dispositivo)
    with torch.no_grad():
        outputs = modelo(**inputs)
        logits_list.append(outputs.logits.cpu())

logits_tensor = torch.cat(logits_list, dim=0)
labels_tensor = torch.tensor(labels)

# 5. Calibración Matemática L-BFGS
print("\nBuscando Temperatura óptima minimizando Negative Log-Likelihood...")
def nll_obj(t_val):
    t_tensor = torch.tensor([t_val])
    scaled_logits = logits_tensor / t_tensor
    return F.cross_entropy(scaled_logits, labels_tensor).item()

res = optim.minimize(nll_obj, x0=1.5, method='L-BFGS-B', bounds=[(0.1, 5.0)])
T_opt = float(res.x[0])
print(f"🌡️ Temperatura calibrada matemáticamente: {T_opt:.4f}")
`

**Salida (Output):**
`	ext
Mounted at /content/drive
Cargando corpus maestro...
Conjunto Hold-Out (Fold 5) extraído matemáticamente: 3088 tickets puros.
Motor de inferencia levantado en: cuda
Loading weights:   0%|          | 0/201 [00:00<?, ?it/s]
Extrayendo logits crudos del modelo sobre Hold-Out...
Procesando tensores: 100%|██████████| 97/97 [00:06<00:00, 14.05it/s]
Buscando Temperatura óptima minimizando Negative Log-Likelihood...
🌡️ Temperatura calibrada matemáticamente: 1.6139
`

# Marginalización y Simulación Financiera mediante Matriz de Costes Asimétrica

En problemas de clasificación masiva (56 clases) para operaciones de negocio, la métrica genérica de *Accuracy* es inservible. Confundir dos etiquetas semánticamente cercanas no tiene el mismo impacto que enrutar un ticket al departamento equivocado.

Se implementa una marginalización de la probabilidad calibrada hacia la Cola (departamento). Posteriormente, la simulación de ROI evalúa el rendimiento sobre un Motor de Reglas Heurísticas (Matriz de Costes Asimétrica) que penaliza las predicciones fallidas basándose en su impacto operativo real:

* **Nivel 1 (Rebote Departamental):** Error en la predicción de la Cola. Requiere re-enrutamiento manual (Nivel 1). Coste fijo operativo.
* **Nivel 2 (Rotura de SLA explícita):** La Cola es correcta, pero la urgencia predicha difiere de la real, comprometiendo los tiempos de resolución garantizados por contrato. Coste de multa (variable según riesgo).
* **Nivel 3 (Rotura de SLA encubierta):** Excepciones críticas de negocio hardcodeadas (ej. procesos que requieren ciclos de facturación mensuales frente a resoluciones en 48h). Coste de multa por riesgo.
* **Nivel 4 (Fricción Administrativa Nula):** Errores puramente estadísticos donde la topología del sub-tipo predicho comparte la misma raíz operativa que el real. El agente de Back-Office gestiona el ticket sin alteración de tiempo. Coste 0.00€.
* **Nivel 5 (Fricción Administrativa Menor):** La predicción difiere en sub-tipo obligando al agente a cambiar la sub-categoría en el CRM antes de la resolución. Coste de fricción evaluado en céntimos (segundos de tiempo extra).

`python
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# =========================================================
# 1. MARGINALIZACIÓN DE PROBABILIDADES POR COLAS
# =========================================================
probs_calibradas = F.softmax(logits_tensor / T_opt, dim=-1).numpy()
print("Agregando masa de probabilidad por Colas (Marginalización)...")
resultados = []

for i in range(len(df_test)):
    fila = df_test.iloc[i]
    probs = probs_calibradas[i]

    idx_max = np.argmax(probs)
    pred_tripleta = id2label[idx_max]

    true_tripleta = fila['target_tripleta']
    true_cola = true_tripleta.split('_')[0]
    pred_cola = pred_tripleta.split('_')[0]

    confianza_cola = 0.0
    for j, prob in enumerate(probs):
        clase_j = id2label[j]
        cola_j = clase_j.split('_')[0]
        if cola_j == pred_cola:
            confianza_cola += prob

    if pred_tripleta == "OUT_OF_SCOPE":
        confianza_cola = 0.0

    resultados.append({
        'true_tripleta': true_tripleta,
        'true_cola': true_cola,
        'pred_tripleta': pred_tripleta,
        'pred_cola': pred_cola,
        'confianza_cola': confianza_cola
    })

df_resultados = pd.DataFrame(resultados)

# =========================================================
# 2. MOTOR DE EVALUACIÓN HEURÍSTICA Y SIMULACIÓN DE ROI
# =========================================================
EXCEPCIONES_CRITICAS = [
    {"recalculo", "recalculoproximociclo"}
]

def calcular_coste_prediccion(true_trip, pred_trip, coste_sla):
    if true_trip == pred_trip:
        return 0.00

    partes_true = true_trip.split('_')
    partes_pred = pred_trip.split('_')

    true_cola, true_urg = partes_true[0], partes_true[-1]
    true_tipo = "_".join(partes_true[1:-1]) if len(partes_true) > 2 else ""

    pred_cola, pred_urg = partes_pred[0], partes_pred[-1]
    pred_tipo = "_".join(partes_pred[1:-1]) if len(partes_pred) > 2 else ""

    # 1. Rebote (Falla la Cola Padre)
    if true_cola != pred_cola:
        return 1.01

    # 2. Rotura SLA Explícita (Falla la Urgencia final)
    if true_urg != pred_urg:
        return coste_sla

    # 3. Rotura SLA Encubierta (Excepciones de sub-tipo letales)
    conjunto_tipos = {true_tipo.lower(), pred_tipo.lower()}
    for par_toxico in EXCEPCIONES_CRITICAS:
        if par_toxico.issubset(conjunto_tipos):
            return coste_sla

    # 4. Error Estadístico (Misma familia operativa, impacto cero)
    distancia = len(set(true_tipo) ^ set(pred_tipo))
    if distancia < 5 or true_tipo[:5] == pred_tipo[:5]:
        return 0.00

    # 5. Fricción Administrativa (El agente cambia el desplegable, 5 seg)
    return 0.05

volumen_mensual_bpo = 2500
coste_ticket_manual = 0.404
coste_ticket_ia = 0.005
gasto_escenario_viejo = volumen_mensual_bpo * coste_ticket_manual

escenarios_sla = {
    'Tolerante (Startup)': 2.00,
    'Base (Estándar BPO)': 5.00,
    'Estricto (Banca/Salud)': 10.00
}

resumen_financiero = []
print("Ejecutando simulación de ROI (Matriz de Costes Asimétrica)...")

for nombre_escenario, coste_error_sla in escenarios_sla.items():
    mejor_ahorro = -float('inf')
    umbral_optimo = 0.50
    cobertura_optima = 0.0

    for u in np.arange(0.50, 1.00, 0.01):
        df_auto = df_resultados[df_resultados['confianza_cola'] >= u]
        if len(df_auto) == 0:
            continue

        tasa_cob = len(df_auto) / len(df_resultados)
        vol_auto = volumen_mensual_bpo * tasa_cob

        coste_errores_total = 0.0
        for _, row in df_auto.iterrows():
            coste_unitario = calcular_coste_prediccion(row['true_tripleta'], row['pred_tripleta'], coste_error_sla)
            peso_proporcional = vol_auto / len(df_auto)
            coste_errores_total += (coste_unitario * peso_proporcional)

        coste_nuevo = ((volumen_mensual_bpo - vol_auto) * coste_ticket_manual) + \
                      (vol_auto * coste_ticket_ia) + \
                      coste_errores_total

        ahorro = gasto_escenario_viejo - coste_nuevo

        if ahorro > mejor_ahorro:
            mejor_ahorro = ahorro
            umbral_optimo = u
            cobertura_optima = tasa_cob

    resumen_financiero.append({
        'Perfil Riesgo': nombre_escenario,
        'Multa SLA': f"{coste_error_sla:.2f} €",
        'Umbral': f"{umbral_optimo:.2f}",
        'Cobertura': f"{cobertura_optima*100:.1f}%",
        'Ahorro/Mes': f"{mejor_ahorro:.2f} €"
    })

df_reporte = pd.DataFrame(resumen_financiero)
print("\n" + "="*70)
print(" REPORTE DE ROI (MOTOR DE REGLAS HEURÍSTICAS)")
print("="*70)
print(f"Gasto actual (100% Manual): {gasto_escenario_viejo:.2f} €\n")
print(df_reporte.to_string(index=False))
`

**Salida (Output):**
`	ext
Agregando masa de probabilidad por Colas (Marginalización)...
Ejecutando simulación de ROI (Matriz de Costes Asimétrica)...

======================================================================
 REPORTE DE ROI (MOTOR DE REGLAS HEURÍSTICAS)
======================================================================
Gasto actual (100% Manual): 1010.00 €

         Perfil Riesgo Multa SLA Umbral Cobertura Ahorro/Mes
   Tolerante (Startup)    2.00 €   0.85     42.3%   110.96 €
   Base (Estándar BPO)    5.00 €   0.93     12.4%    -1.52 €
Estricto (Banca/Salud)   10.00 €   0.95      2.8%   -46.93 €
`

`python
!pip install lime
`

**Salida (Output):**
`	ext
Collecting lime
  Downloading lime-0.2.0.1.tar.gz (275 kB)
[?25l     [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m0.0/275.7 kB[0m [31m?[0m eta [36m-:--:--[0m[2K     [90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m [32m275.7/275.7 kB[0m [31m21.2 MB/s[0m eta [36m0:00:00[0m
[?25h  Preparing metadata (setup.py) ... [?25l[?25hdone
Requirement already satisfied: matplotlib in /usr/local/lib/python3.13/dist-packages (from lime) (3.10.0)
Requirement already satisfied: numpy in /usr/local/lib/python3.13/dist-packages (from lime) (2.1.3)
Requirement already satisfied: scipy in /usr/local/lib/python3.13/dist-packages (from lime) (1.16.3)
Requirement already satisfied: tqdm in /usr/local/lib/python3.13/dist-packages (from lime) (4.67.3)
Requirement already satisfied: scikit-learn>=0.18 in /usr/local/lib/python3.13/dist-packages (from lime) (1.6.1)
Requirement already satisfied: scikit-image>=0.12 in /usr/local/lib/python3.13/dist-packages (from lime) (0.25.2)
Requirement already satisfied: networkx>=3.0 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (3.6.1)
Requirement already satisfied: pillow>=10.1 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (11.3.0)
Requirement already satisfied: imageio!=2.35.0,>=2.33 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (2.37.4)
Requirement already satisfied: tifffile>=2022.8.12 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (2026.8.23)
Requirement already satisfied: packaging>=21 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (26.3)
Requirement already satisfied: lazy-loader>=0.4 in /usr/local/lib/python3.13/dist-packages (from scikit-image>=0.12->lime) (0.5)
Requirement already satisfied: joblib>=1.2.0 in /usr/local/lib/python3.13/dist-packages (from scikit-learn>=0.18->lime) (1.6.0)
Requirement already satisfied: threadpoolctl>=3.1.0 in /usr/local/lib/python3.13/dist-packages (from scikit-learn>=0.18->lime) (3.6.0)
Requirement already satisfied: contourpy>=1.0.1 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (1.3.3)
Requirement already satisfied: cycler>=0.10 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (0.12.1)
Requirement already satisfied: fonttools>=4.22.0 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (4.64.0)
Requirement already satisfied: kiwisolver>=1.3.1 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (1.5.1)
Requirement already satisfied: pyparsing>=2.3.1 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (3.3.2)
Requirement already satisfied: python-dateutil>=2.7 in /usr/local/lib/python3.13/dist-packages (from matplotlib->lime) (2.9.0.post0)
Requirement already satisfied: cloudpickle>=3.0 in /usr/local/lib/python3.13/dist-packages (from joblib>=1.2.0->scikit-learn>=0.18->lime) (3.1.2)
Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.13/dist-packages (from python-dateutil>=2.7->matplotlib->lime) (1.17.0)
Building wheels for collected packages: lime
  Building wheel for lime (setup.py) ... [?25l[?25hdone
  Created wheel for lime: filename=lime-0.2.0.1-py3-none-any.whl size=283913 sha256=9f4dc85ca39d9bc02ba87c7b7565fbcbe3cd81c153c5ec0fe2f6d98f88d393dc
  Stored in directory: /root/.cache/pip/wheels/7c/04/5c/157dc9106512a6c7a30653ec064490c94a49e0fc8f63d19ab9
Successfully built lime
Installing collected packages: lime
Successfully installed lime-0.2.0.1
`

# Auditoría Forense de Caja Negra: Calibración, Confusión y Explicabilidad (LIME)

Para garantizar la robustez técnica del modelo y evitar el despliegue de una red inescrutable, se ejecutan tres pruebas periciales tras comprobar el colapso del ROI:

* **Matriz de Confusión Inter-Departamental:** Valida la estanqueidad de la marginalización por Colas, evidenciando empíricamente dónde se están produciendo las fugas (falsos positivos) entre las distintas áreas operativas.
* **Diagrama de Fiabilidad (Calibration Curve):** Demuestra gráficamente la corrección del *overconfidence*. Se plotea la red en bruto frente a la red calibrada térmicamente, documentando cómo la probabilidad original estaba disociada de la precisión real y justificando la severidad de la Temperatura L-BFGS obtenida.
* **Interpretabilidad Local (LIME):** Se auditan los constructos semánticos de la red. Mediante perturbación local masiva, se aísla la carga de decisión de los tokens individuales. Esto descarta que la red esté memorizando ruido del conjunto de entrenamiento y aterriza el análisis de atención en reglas lógicas de negocio.

`python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import numpy as np
import torch
from pathlib import Path

DIR_IMAGES = BASE_DIR / "images"
DIR_IMAGES.mkdir(exist_ok=True)

print("Generando auditoría forense de caja negra...")

# =========================================================
# GRÁFICA 3: Matriz de Confusión de Colas Marginalizadas
# =========================================================
plt.figure(figsize=(10, 8))
colas_unicas = sorted(list(set(df_resultados['true_cola'].unique()) | set(df_resultados['pred_cola'].unique())))

cm = confusion_matrix(df_resultados['true_cola'], df_resultados['pred_cola'], labels=colas_unicas)
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
cm_norm = np.nan_to_num(cm_norm)

sns.heatmap(cm_norm, annot=cm, fmt='d', cmap='Blues', xticklabels=colas_unicas, yticklabels=colas_unicas,
            cbar_kws={'label': 'Proporción (Recall)'}, annot_kws={"size": 12})

plt.title("Matriz de Confusión por Cola Departamental (Hold-Out Real)", fontsize=14, pad=15, fontweight='bold')
plt.xlabel("Cola Predicha por la IA", fontsize=12)
plt.ylabel("Cola Real (Verdad Terreno)", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

ruta_cm = DIR_IMAGES / "confusion_matrix_colas.png"
plt.savefig(ruta_cm, dpi=300)
plt.show()

# =========================================================
# GRÁFICA 4: Diagrama de Fiabilidad (Calibration Curve)
# =========================================================
probs_crudas = torch.nn.functional.softmax(logits_tensor, dim=-1).numpy()

confianzas_crudas = np.max(probs_crudas, axis=1)
aciertos_crudos = (np.argmax(probs_crudas, axis=1) == labels_tensor.numpy()).astype(int)

confianzas_calibradas = np.max(probs_calibradas, axis=1)
aciertos_calibrados = (np.argmax(probs_calibradas, axis=1) == labels_tensor.numpy()).astype(int)

def compute_calibration_bins(confidences, accuracies, num_bins=10):
    bins = np.linspace(0, 1, num_bins + 1)
    bin_indices = np.digitize(confidences, bins) - 1
    bin_accs, bin_confs = [], []
    for i in range(num_bins):
        mask = bin_indices == i
        if np.any(mask):
            bin_accs.append(np.mean(accuracies[mask]))
            bin_confs.append(np.mean(confidences[mask]))
    return bin_confs, bin_accs

crudos_confs, crudos_accs = compute_calibration_bins(confianzas_crudas, aciertos_crudos)
calib_confs, calib_accs = compute_calibration_bins(confianzas_calibradas, aciertos_calibrados)

plt.figure(figsize=(8, 8))
plt.plot([0, 1], [0, 1], 'k--', label="Calibración Perfecta (Teórica)")
plt.plot(crudos_confs, crudos_accs, 's-', color='#e74c3c', label="Red Cruda (Prepotente)", linewidth=2.5)
plt.plot(calib_confs, calib_accs, 'o-', color='#2ecc71', label=f"Red Calibrada (L-BFGS T={T_opt:.2f})", linewidth=2.5)

plt.title("Diagrama de Fiabilidad Estricto (Reliability Curve)", fontsize=14, pad=15, fontweight='bold')
plt.xlabel("Confianza Predicha (Softmax Máxima)", fontsize=12)
plt.ylabel("Precisión Empírica (Acierto Real)", fontsize=12)
plt.legend(loc="upper left", fontsize=10)
plt.xlim(0, 1.05)
plt.ylim(0, 1.05)
plt.tight_layout()

ruta_calib = DIR_IMAGES / "calibration_curve.png"
plt.savefig(ruta_calib, dpi=300)
plt.show()

# =========================================================
# GRÁFICA 5: EXPLICABILIDAD DE TOKENS (LIME)
# =========================================================
from lime.lime_text import LimeTextExplainer

def predict_proba_lime(textos_list):
    inputs = tokenizer(textos_list, padding=True, truncation=True, max_length=256, return_tensors="pt").to(dispositivo)
    with torch.no_grad():
        logits_out = modelo(**inputs).logits
        probs_out = torch.nn.functional.softmax(logits_out / T_opt, dim=-1)
    return probs_out.cpu().numpy()

clases_ordenadas = [v for k, v in sorted(id2label.items())]
explainer = LimeTextExplainer(class_names=clases_ordenadas)

# Al bajar la confianza drásticamente, extraemos el mejor y el peor ticket
idx_claro = df_resultados['confianza_cola'].idxmax()
idx_dudoso = df_resultados['confianza_cola'].idxmin()

print(f"\n[LIME] Analizando semántica de Ticket con máxima confianza encontrada ({df_resultados.loc[idx_claro, 'confianza_cola']:.2f})...")
exp_claro = explainer.explain_instance(textos[idx_claro], predict_proba_lime, num_features=6, top_labels=1, num_samples=5000)
exp_claro.save_to_file(str(DIR_IMAGES / "lime_ticket_max_confianza.html"))

print(f"[LIME] Analizando semántica de Ticket con peor confianza encontrada ({df_resultados.loc[idx_dudoso, 'confianza_cola']:.2f})...")
exp_dudoso = explainer.explain_instance(textos[idx_dudoso], predict_proba_lime, num_features=6, top_labels=1, num_samples=5000)
exp_dudoso.save_to_file(str(DIR_IMAGES / "lime_ticket_peor_confianza.html"))

print(f"✅ Análisis LIME exportado como páginas web interactiva (HTML) en la carpeta images.")
`

**Salida (Output):**
`	ext
Generando auditoría forense de caja negra...
<Figure size 1000x800 with 2 Axes><Figure size 800x800 with 1 Axes>
[LIME] Analizando semántica de Ticket con máxima confianza encontrada (0.96)...
[LIME] Analizando semántica de Ticket con peor confianza encontrada (0.00)...
✅ Análisis LIME exportado como páginas web interactiva (HTML) en la carpeta images.
`

