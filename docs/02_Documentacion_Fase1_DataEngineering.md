# Documentación de Ingeniería de Datos (Fase 1) - SITOR V7.2

**Fecha de Ejecución:** Septiembre 2026
**Notebook Asociado:** `01_EDA_y_Analisis_Exploratorio.ipynb`
**Objetivo:** Transición de datos desde la capa Cruda (Bronze) hasta la capa Lista para Modelado (Gold), asegurando rigor estadístico y evitando falsificaciones operativas en el entrenamiento del motor de auditoría de calidad (QA).

---

## Contexto de Negocio (SITOR como Auditor QA)

SITOR no opera como un motor de enrutamiento inicial, sino como un **Sistema de Quality Assurance (QA) y Auditoría**. Su función no es sustituir el triaje primario, sino evaluar matemáticamente la tripleta propuesta por los agentes humanos. Si la confianza de SITOR es alta (>= 0.60), audita la decisión de forma autónoma (validando o auto-corrigiendo). Si la confianza es insuficiente, deriva el ticket a un supervisor (`MANUAL_REVIEW`). Por lo tanto, el volumen operativo no representa "tickets enrutados", sino "decisiones humanas auditadas".

---

## 1. Auditoría Inicial y Transición a Capa Silver

El análisis exploratorio de los tres datasets crudos (`df_01`, `df_02`, `df_03`) reveló inconsistencias de esquema (presencia de columnas exclusivas como `version` o `business_type` y disparidad en etiquetas `tag_x`). 

### Limpieza y Proyección
Para posibilitar la unificación sin inyectar ruido multidimensional, se ejecutó una proyección geométrica estricta. Solo se conservó la intersección de variables útiles: `['subject', 'body', 'queue', 'type', 'priority', 'language']`.

### Tratamiento de Nulos (Completitud)
La auditoría de calidad sobre los 52.587 registros unificados determinó lo siguiente:
*   **Asunto (`subject`):** Presentaba un 11% de valores nulos. Para evitar la destrucción masiva de datos, se aplicó una imputación estática (`fillna('No Subject')`).
*   **Cuerpo (`body`):** Presentaba 3 registros nulos (0.005%). Al ser el core textual indispensable para NLP, estos registros corruptos fueron eliminados matemáticamente.

### Aplicación de Regla de Negocio (Idioma)
El dataset original era multilingüe (Inglés, Alemán, Español, Francés, Portugués), siendo el Inglés la clase mayoritaria (56.4%). 
Se aplicó un filtro restrictivo para aislar el mercado anglosajón. Esta decisión no obedece a un capricho, sino a una limitación técnica estricta:
1.  Mezclar idiomas fragmenta el vocabulario de la matriz de dispersión léxica (TF-IDF).
2.  El pipeline semántico (Modelo C y D) dependerá del encoder monolingüe `BAAI/bge-small-en-v1.5`.
Tras el filtrado, se consolidaron **29.650 tickets válidos**. La columna `language` fue eliminada al presentar varianza cero.

### Feature Engineering Base
Se fusionaron los campos `subject` y `body` en una nueva variable explicativa maestra (`full_text`) para maximizar la carga semántica de los tensores.

---

## 2. Ingeniería del Target y Transición a Capa Gold

La capa Silver limpia reveló un dominio tipográfico perfecto, sin colisiones de sintaxis. Contabilizamos exactamente 10 colas, 4 tipos y 3 prioridades (120 permutaciones posibles en el espacio latente).

### La Tripleta y la Ley de Potencias
Se procedió a concatenar las 3 variables operativas (`queue_type_priority`) para generar el objetivo de clasificación multiclasificación: la **Tripleta**. 
Al analizar las frecuencias, se confirmó matemáticamente la presencia de una distribución *Power Law* clásica en entornos BPO.

### Ejecución de la Regla Anti-Falsificación
En arquitecturas previas (V6), las clases minoritarias eran eliminadas de raíz, lo que falsificaba el volumen de tickets que SITOR debe supervisar (y por ende, la Tasa de Automatización de Auditoría). En la V7.2, se ejecutó un colapso estratégico:
*   **101 Clases Retenidas:** Lograron el soporte estadístico mínimo requerido (>= 30 muestras).
*   **Clase `OUT_OF_SCOPE` (19 Clases Colapsadas):** El *long tail* de ruido (323 tickets, 1.09% del volumen real) fue remapeado a esta nueva categoría virtual, salvaguardando el denominador de tickets.

El problema predictivo quedó fijado en **102 clases concurrentes** (Alta Cardinalidad).

### Particionado Hermético y Congelación de Folds
Para evitar la fuga de datos (*Data Leakage*) y garantizar una comparativa científica justa (*Bake-Off*) entre el hardware local (CPU) y la nube (Google Colab GPU), se aplicó el siguiente protocolo:
1.  **Stratified Split:** Partición estricta 80/20, forzando idéntica proporción de la clase `OUT_OF_SCOPE` en ambos conjuntos.
2.  **K-Fold Inyectado:** Se inyectó una variable `fold_id` (0 a 4) en el conjunto de entrenamiento usando `StratifiedKFold`.
3.  **Serialización Parquet:** Los datos finales fueron exportados mediante motor `fastparquet` a la carpeta `data/gold/`. 

**Volumetría Final (Capa Gold):**
*   Train Set: 23.720 filas (Con folds inyectados)
*   Test Set: 5.930 filas (Aisladas para validación One-Shot)
