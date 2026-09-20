# 03 - Modelo de Datos

## 1. Resumen de la idea y datos del proyecto
* **Problema que resuelve:** Los altos costes y tiempos de resolución en los centros de soporte IT causados por el falso escalado y mala tipificación manual de tickets por parte del nivel 1 (Front Office).
* **Solución:** SITOR, un motor B2B basado en Procesamiento de Lenguaje Natural (NLP / RoBERTa) capaz de auditar enrutamientos. Si la tripleta humana contradice la algorítmica con una confianza $\ge$ 80% (umbral base), se aplica auto-enrutamiento.
* **Fuentes de datos:** Dataset público *"Customer IT Support Ticket Dataset"* de Kaggle (CSV).
* **Información que aporta:** Descripciones textuales de incidencias (`subject`, `body`) y su resolución categórica histórica (`queue`, `type`, `priority`).

## 2. Definición del modelo de datos
El modelo de datos diseñado para SITOR se basa en la ingesta, unificación y transformación secuencial de tickets de soporte técnico multilingües, estructurándose en tres capas de madurez (Medallion Architecture adaptada a Machine Learning):

**Tecnología y formatos de almacenamiento elegidos:**
El flujo de datos se diseña para optimizar la ingesta por parte de los tensores de PyTorch y aislar completamente el entorno de entrenamiento del de evaluación (prevención de *Data Leakage*):
1. **Capa Raw (Formato CSV):** Se mantiene en su formato original de extracción (`.csv`) para conservar la trazabilidad inmutable del dato en crudo. Consta de tres archivos independientes que suman 27.818 registros.
2. **Capa Silver (Formato Parquet):** El dataset unificado y limpio se serializa a `.parquet`. Se escoge esta tecnología por su alta compresión columnar y su capacidad para retener metadatos y tipos de datos nativos, evitando las corrupciones típicas del CSV. Aquí se aplica la **deduplicación estricta**.
3. **Capa Gold (Formato Parquet particionado):** Las estructuras finales de entrenamiento y test (`train_set_v7.parquet` y `test_set_v7.parquet`) ya particionadas estratificadamente. Contienen la variable objetivo final `target_tripleta` y el texto fusionado `full_text`. Listas para su ingesta directa por el Tokenizador de *Hugging Face*.

---

## 3. Descripción de los datasets origen (Capa Raw)
Se dispone de tres datasets públicos obtenidos de Kaggle, cada uno con leves variaciones en su esquema y calidad de datos:

| Atributo | Dataset 1 | Dataset 2 | Dataset 3 |
| :--- | :--- | :--- | :--- |
| **Nombre Archivo** | `dataset-tickets-multi-lang-4-20k.csv` | `aa_dataset-tickets-multi-lang-5-2-50-version.csv` | `dataset-tickets-multi-lang3-4k.csv` |
| **Volumen** | 19.999 filas | 5.000 filas | 2.819 filas |
| **Columnas** | 18 | 19 (incluye `version`) | 19 (incluye `business_type`) |
| **Idioma predominante**| Inglés (18.172 registros) | Inglés (5.000 registros) | Español (2.819 registros) |
| **Variables predictoras** | `body`, `subject` | `body`, `subject` | `body`, `subject` |
| **Variables objetivo** | `queue`, `type`, `priority` | `queue`, `type`, `priority` | `queue`, `type`, `priority` |
| **Calidad inicial** | Aceptable. Varios nulos en `subject`. Múltiples columnas vacías (`tag_1..8`). | Aceptable. Contiene columna `version` no predictiva y 1 fila con nulo en `body`. | Deficiente. Múltiples filas y columnas vacías. Requiere limpieza intensiva. |

---

## 4. Entidad generada (Capa Silver)
El procesamiento inicial se encarga de unificar los tres archivos CSV crudos en una única entidad desnormalizada, saneando la estructura y acotando el alcance al idioma base del modelo.

| **Nombre de la entidad** | `tickets_silver_cleaned.parquet` |
| :--- | :--- |
| **Propósito** | Almacenar el histórico consolidado de tickets válidos, deduplicados y libres de ruido. |
| **Volumen final aproximado** | ~23.700 registros (Tras el filtrado de idioma base y saneamiento de nulos). |
| **Nivel de agregación** | Incidencia única (Ticket). |
| **Reglas de integridad** | - Eliminación de registros sin `body`. <br> - Imputación de `"No Subject"` en asuntos vacíos. <br> - Fusión de `subject` y `body` en `full_text`. <br> - **Deduplicación estricta** por `full_text` para eliminar copias idénticas. |

---

## 5. Estructura Final para Modelado (Capa Gold)
La capa final (Gold) aplica las lógicas de negocio al espacio de etiquetas (Taxonomía) y estratifica el conjunto de datos para el ecosistema de *Machine Learning*.

| **Variables Objetivo** | `queue`, `type` y `priority` codificadas como una única cadena alfanumérica (`target_tripleta`). |
| **Taxonomía Saneada** | Las clases con soporte estadístico insuficiente (< 30 muestras) se agrupan en clases genéricas (`OUT_OF_SCOPE` / `Derivacion_Manual_Minoritaria`), reduciendo la taxonomía a **90 clases operativas**. |
| **Particionado** | División 80/20 estratificada por `target_tripleta`, garantizando que la distribución de la clasificación se respete de forma exacta en los conjuntos de entrenamiento (`train_set_v7.parquet`) y validación (`test_set_v7.parquet`). |
