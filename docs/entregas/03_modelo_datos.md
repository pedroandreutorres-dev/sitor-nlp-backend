# 03 - Diseño del modelo de datos y capa gold

## 1. Resumen de la idea y datos del proyecto

* **Problema que resuelve:** Los errores en la clasificación manual de tickets (tipificación) por parte de los agentes de Nivel 1 en BPOs y operadoras de telecomunicaciones, lo que provoca "falsos escalados", sobrecostes y un empeoramiento del Tiempo Medio de Resolución (AHT).
* **Solución a construir:** SITOR, un motor de clasificación jerárquica basado en NLP que actuará como auditor en tiempo real, validando o sugiriendo correcciones sobre la tipificación asignada por el agente. El MVP constará de un microservicio FastAPI.
* **Fuentes de datos:** Al no disponer de datos internos empresariales por confidencialidad, se utilizará el dataset público *"Multilingual Customer Support Tickets"* (Kaggle), extraído en tres archivos originales.
* **Tipo de información:** Textos libres escritos por los usuarios (cuerpo del ticket, asunto), resoluciones (respuesta) y etiquetas categóricas estructuradas que simulan la tripleta de un CRM: *queue* (cola), *type* (tipo) y *priority* (prioridad).

---

## 2. Tecnología o formato de almacenamiento elegido

El proyecto utilizará una combinación de formatos adaptada a la madurez del dato:
* **Ficheros CSV (Capa Raw):** Los datos originales de Kaggle se mantendrán en su formato `.csv` nativo para preservar la inmutabilidad de la fuente.
* **Ficheros Parquet (Capas Processed y Gold):** Una vez ejecutado el pipeline de limpieza mediante Pandas, los datasets finales se almacenarán en formato `.parquet`. 
* **Justificación:** Elegimos Parquet para la capa *Gold* porque es un formato columnar optimizado que preserva nativamente los tipos de datos (evitando que Pandas tenga que inferir los tipos categóricos o de texto en cada lectura). Además, reduce drásticamente el peso del archivo en disco y acelera los tiempos de lectura/escritura (I/O), algo crítico cuando se iterará múltiples veces sobre los datos para entrenar modelos NLP o extraer *embeddings*.

---

## 3. Estructura de capas de datos

El repositorio seguirá una arquitectura de datos secuencial orientada a MLOps:

```text
data/
|-- raw/       # Contiene los 3 ficheros CSV originales descargados de Kaggle.
|-- processed/ # Archivos temporales (limpieza intermedia y unificación).
`-- gold/      # Datasets finales segregados para el Test A/B de idioma.
    |-- gold_tickets_en.parquet
    `-- gold_tickets_es.parquet
```

| Capa | Contenido esperado |
| :--- | :--- |
| **Raw** | Ficheros originales descargados de Kaggle (`dataset-tickets-multi-lang3-4k.csv`, `dataset-tickets-multi-lang-4-20k.csv`, `aa_dataset-tickets-multi-lang-5-2-50-version.csv`). Intocables, sin limpieza, con ruido de sistema y datos fuera del dominio BPO. |
| **Processed** | Fragmentos limpios y unificados, con el índice reseteado, justo antes de ejecutar el pipeline intensivo de NLP (lematización). |
| **Gold** | Artefactos de consumo directo para los algoritmos. Son dos ficheros segregados (Inglés y Español) que contienen los textos originales, el texto predictivo limpio (`full_text_clean`), un ID trazable y filtrados por dominio de negocio (Telco). |

---

## 4. Definición de la capa gold

La capa *Gold* estará compuesta por dos datasets físicos segregados idiomáticamente para facilitar la experimentación A/B sin requerir filtrados en memoria durante el entrenamiento.

| Atributo | Definición en la capa Gold |
| :--- | :--- |
| **Nombre del fichero** | `gold_tickets_en.parquet` y `gold_tickets_es.parquet` |
| **Descripción** | Datasets limpios, procesados sintácticamente (lematizados) y listos para vectorización, divididos por el idioma principal del Test A/B. |
| **Nivel de granularidad** | Una fila por ticket (incidencia individual). |
| **Volumen esperado** | ~16.000 registros útiles para el *baseline* en Inglés (tras filtros de dominio y nulos), que servirán de base para la posterior traducción al Español. |
| **Identificador principal** | Clave primaria generada sintéticamente (`ticket_id`), por ejemplo `TKT-00001`, garantizando trazabilidad en el modelo y en la API. |
| **Variables Objetivo** | `queue` (Nivel 1), `type` (Nivel 2) y `priority` (Nivel 3). |
| **Variables Predictoras** | `body`, `subject` (textos en bruto) y `full_text_clean` (texto concatenado, tokenizado y lematizado sin stopwords). |
| **Uso posterior** | Entrenamiento de modelos NLP (XGBoost, Regresión Logística), generación de *Embeddings* y exposición en FastAPI. |

### Tabla de metadatos de la Capa Gold

| Dataset gold | Granularidad | Campos clave | Uso posterior |
| :--- | :--- | :--- | :--- |
| `gold_tickets_en.parquet` | Una fila por ticket | `ticket_id`, `full_text_clean`, `queue`, `type`, `priority` | NLP Modeling (Baseline) |
| `gold_tickets_es.parquet` | Una fila por ticket | `ticket_id`, `full_text_clean`, `queue`, `type`, `priority` | NLP Modeling (Data Augmentation) |

---

## 5. Relaciones entre datos

* **Único Dataset Desnormalizado:** El proyecto utiliza **tablas planas desnormalizadas**. Al tratarse de un problema de clasificación de Machine Learning clásico (Procesamiento de Lenguaje Natural), los algoritmos (XGBoost, Random Forest, Redes Neuronales) requieren que las *features* predictoras (el texto) y las variables objetivo (las etiquetas) estén contenidas en la misma matriz (*flat table*). 
* **Justificación:** No existe necesidad de montar un esquema de Base de Datos Relacional (joins, cruces 1:N) porque la unidad mínima de información (el ticket y su resolución) ya es autoconclusiva. Implementar SQL o tablas cruzadas añadiría una complejidad arquitectónica innecesaria.

---

## 6. Diccionario de datos inicial (Capa Gold)

| Campo | Descripción | Tipo de dato | Fuente | Obligatorio | Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ticket_id` | Identificador único alfanumérico | string | Derivado | **Sí** | *Primary Key* sintética (ej. `TKT-04512`). *(Nota de desarrollo: Pendiente de programar en los notebooks).* |
| `body` | Texto descriptivo original escrito por el cliente | string / text | Raw CSVs | **Sí** | Referencia para evaluación humana. |
| `subject` | Asunto o título del ticket | string / text | Raw CSVs | No | Imputado a "No Subject" si estaba vacío. |
| `full_text_clean` | Texto predictivo limpio (Concatenación de Asunto + Cuerpo, lematizado y sin stopwords) | string / text | Derivado | **Sí** | **Variable predictora real** para vectorización. *(Nota de desarrollo: Pendiente de programar en los notebooks).* |
| `queue` | Departamento asignado (Cola) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 1. |
| `type` | Naturaleza ITIL (Incident, Request...) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 2. |
| `priority` | Nivel de urgencia (High, Medium, Low) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 3. |

*(Nota: Variables operativas descartadas como `answer`, `version`, `business_type`, `language` o `tag_1..9` han sido purgadas de la estructura final para aislar el conjunto de datos predictivo. La exclusión del `answer` de la capa Gold es una decisión reciente y su purgado está pendiente de programar en los notebooks).*

---

## 7. Problemas de calidad esperados (Según EDA previo)

A través de la auditoría de los tres archivos CSV originales descargados de Kaggle, se han aterrizado los siguientes problemas concretos de calidad:
1. **Valores nulos críticos:** Existen tickets sin cuerpo de texto (`body`), lo que imposibilita el cálculo de TF-IDF y el análisis léxico.
2. **Alta dispersión y ruido sintético:** Presencia de etiquetas categóricas masivas vacías (`tag_1` a `tag_9`), variables sintéticas inútiles (`version`), columnas intrusas que no aparecen en todos los ficheros (`business_type`), e información post-resolución no predictiva (`answer`).
3. **Casuística fuera de dominio:** Existen registros pertenecientes a Recursos Humanos, Retail o Consultas Genéricas que "ensucian" las fronteras de decisión de un modelo orientado a Telecomunicaciones/IT.
4. **Desbalanceo idiomático:** Un problema grave de calidad cruzada es la baja representación de tickets nativos en español, lo que motiva la segregación de la capa Gold en dos artefactos para experimentar con el *baseline* en inglés vs la traducción al español.

---

## 8. Decisiones de limpieza y transformación previstas

El *pipeline* de procesamiento hacia la capa Gold ejecutará secuencialmente las siguientes reglas de negocio y transformaciones algorítmicas:

* **Saneamiento Estructural y Nulos:**
  * Purga de columnas irrelevantes o no predictivas: `tag_1` hasta `tag_9`, `version`, `business_type` y **`answer`**. *(Nota de desarrollo: La eliminación de `answer` está pendiente de programar).*
  * Imputación estática: Los nulos de la columna `subject` se rellenarán con la cadena `"No Subject"`.
  * Borrado de filas (Dropna): Cualquier registro con nulos en `body` será eliminado de la base de datos (se revoca la regla anterior de borrar nulos en `answer`, recuperando así datos valiosos de entrenamiento). *(Nota de desarrollo: Dado que los nulos de answer ya fueron borrados en la fase de EDA, la re-ejecución del notebook 01 para regenerar la capa Silver sin este borrado queda pendiente de programar).*
* **Filtros de Dominio BPO/Telco:**
  * Se eliminan los tickets cuyas colas (`queue`) sean `Human Resources`, `Returns and Exchanges` o `General Inquiry`. 
* **Ingeniería de Características (*Feature Engineering*):**
  * **`ticket_id`:** Creación de una clave primaria alfanumérica única tras la concatenación y el reseteo del índice. *(Nota de desarrollo: Pendiente de programar).*
  * **`full_text_clean`:** Ejecución intensiva de un *pipeline* de NLP mediante la librería `spaCy` sobre la concatenación previa de Asunto y Cuerpo (reducción a minúsculas, eliminación de puntuación, filtrado de *stopwords* y extracción de lemas). *(Nota de desarrollo: Pendiente de programar).*
* **Segregación Gold (A/B Test):**
  * Los datos se filtrarán por la variable temporal `language`, guardando el subconjunto `en` en el archivo `gold_tickets_en.parquet` y el subconjunto `es` (nativo + *Data Augmentation* traducido) en `gold_tickets_es.parquet`, descartando finalmente la columna `language`.

---

## 9. Riesgos del modelo de datos

* **¿Qué parte está más clara?** La estructura final de la tabla desnormalizada. Al acotarlo estrictamente a las variables de la tripleta y los textos limpios (`full_text_clean`), purificando el dataset de "peso muerto" como el `answer`, el modelo de datos es inmutable y encaja a la perfección con la librería Scikit-Learn.
* **¿Qué parte genera más incertidumbre?** La "limpieza semántica" en la construcción de `full_text_clean`. Aunque la estructura sea robusta, es probable que la lematización de spaCy arrastre solapamiento semántico (Concept Drift) o pierda matices técnicos cruciales para el dominio de las telecomunicaciones (especialmente en la traducción al español).
* **¿Qué tabla/fichero puede dar más problemas?** El tercer archivo CSV crudo (`dataset-tickets-multi-lang3-4k.csv`), al ser el fichero con mayores anomalías estructurales detectadas.
* **¿Qué ocurriría si no se puede construir la capa gold definida?** Si el procesamiento NLP de spaCy sobre todo el volumen excede los límites de memoria, la construcción de `full_text_clean` fracasará. El riesgo está mitigado parametrizando la limpieza por *batches*.
* **Riesgo crítico de la Arquitectura en Cascada:** Al contar con un corpus base en inglés acotado (~16.000 tickets útiles), existe el riesgo de que el volumen sea insuficiente para sostener 3 niveles de predicción encadenada, provocando escasez crítica de muestras en las clases profundas. Para mitigarlo:
  * Se aplicarán técnicas de sobremuestreo sintético como **SMOTE** (*Synthetic Minority Over-sampling Technique*) tras la vectorización.
  * Si el rendimiento colapsa a pesar del SMOTE, se plantean tres escenarios:
    * **Plan A:** Cascada completa (`Queue` > `Type` > `Priority`).
    * **Plan B:** Recortar el MVP al Nivel 2 (`Queue` + `Type`).
    * **Plan C:** Predecir exclusivamente el Nivel 1 (`Queue`).
