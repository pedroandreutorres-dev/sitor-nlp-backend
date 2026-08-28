# 03 - Modelo de Datos

## 1. Resumen de la idea y datos del proyecto
* **Problema que resuelve:** Los altos costes y tiempos de resolución en los centros de soporte IT causados por el falso escalado y mala tipificación manual de tickets por parte del nivel 1 (Front Office).
* **Solución:** SITOR, un motor B2B basado en Procesamiento de Lenguaje Natural (NLP) capaz de auditar enrutamientos. Si la tripleta humana contradice la algorítmica con una confianza $\ge$ 85%, se aplica auto-enrutamiento.
* **Fuentes de datos:** Dataset público *"Customer IT Support Ticket Dataset"* de Kaggle (CSV).
* **Información que aporta:** Descripciones textuales de incidencias (`subject`, `body`) y su resolución categórica histórica (`queue`, `type`, `priority`).

## 2. Definición del modelo de datos
El modelo de datos diseñado para SITOR se basa en la ingesta, unificación y transformación secuencial de tickets de soporte técnico multilingües, estructurándose en tres capas de madurez (Medallion Architecture adaptada a Machine Learning):

**Tecnología y formatos de almacenamiento elegidos:**
El flujo de datos se diseña para evitar cuellos de botella en memoria RAM y optimizar la lectura, justificando el formato de cada capa:
1. **Capa Raw (Formato CSV):** Se mantiene en su formato original de extracción (`.csv`) para conservar la trazabilidad inmutable del dato en crudo. Consta de tres archivos independientes que suman 27.818 registros, conteniendo el volcado bruto del CRM.
2. **Capa Processed o Silver (Formato Parquet):** El dataset unificado y limpio se serializa a `.parquet`. Se escoge esta tecnología por su alta compresión columnar y su capacidad crítica para retener los metadatos y tipos de datos nativos de Pandas (ej. `category`, `string`), evitando las corrupciones típicas del CSV.
3. **Capa Features (Formato NPZ - Sparse Matrix):** Las estructuras finales de características se exportan en `.npz` (SciPy Sparse Matrix). Una matriz TF-IDF de 16.000 tickets por 10.000 términos ocupa una fracción mínima de memoria al almacenar únicamente las celdas con valores distintos de cero, previniendo el colapso del sistema durante el entrenamiento de Scikit-Learn.

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

## 4. Entidad generada (Capa Processed)
El procesamiento inicial se encarga de unificar los tres archivos CSV crudos en una única entidad desnormalizada, saneando la estructura y acotando el alcance al dominio de Telecomunicaciones (BPO).

| **Nombre de la entidad** | `df_final_silver.parquet` |
| :--- | :--- |
| **Propósito** | Almacenar el histórico completo de tickets válidos para el entrenamiento, libres de ruido y con las reglas de negocio aplicadas. |
| **Volumen final aproximado** | ~16.000 registros (Tras el filtrado y limpieza del idioma base). |
| **Nivel de agregación** | Incidencia única (Ticket). |
| **Reglas de integridad** | - Eliminación de registros sin `body` (condición indispensable para NLP). <br> - Filtrado de colas ajenas a TI (ej. HR, General Inquiry). <br> - Imputación de `"No Subject"` en asuntos vacíos. |

---

## 5. Estructura de Características (Capa Features)
La capa final (Features) no es una base de datos tabular tradicional, sino un conjunto de artefactos (matrices matemáticas y modelos de codificación) listos para la inyección directa en el algoritmo predictivo.

| **Variables Objetivo** | `queue` (Nivel 1), `type` (Nivel 2) y `priority` (Nivel 3) codificadas como una única "Tripleta". |
| **Variables Predictoras** | `body`, `subject` (textos en bruto) y `full_text_clean` (texto concatenado, tokenizado y lematizado sin stopwords). |
| **Uso posterior** | Entrenamiento de modelos NLP (Random Forest, Regresión Logística), Serialización y exposición en FastAPI. |

### Tabla de metadatos de las Capas Processed y Features

| Artefacto | Granularidad | Descripción | Uso posterior |
| :--- | :--- | :--- | :--- |
| `df_final_silver.parquet` | Una fila por ticket | Dataset unificado, limpio y lematizado. Base para la extracción de características. | Feature Engineering. Ubicado en `data/processed/`. |
| `en_X_train_tfidf.npz` | Matriz dispersa | 10.000 dimensiones (TF-IDF) de los textos de entrenamiento. | NLP Modeling (Entrenamiento). Ubicado en `data/features/`. |
| `en_X_test_tfidf.npz` | Matriz dispersa | 10.000 dimensiones (TF-IDF) de los textos de evaluación. | NLP Modeling (Validación). Ubicado en `data/features/`. |

---

## 6. Relaciones entre datos

* **Único Dataset Desnormalizado:** El proyecto utiliza **tablas planas desnormalizadas**. Al tratarse de un problema de clasificación de Machine Learning clásico (Procesamiento de Lenguaje Natural), los algoritmos requieren que las *features* predictoras (el texto) y las variables objetivo (las etiquetas) estén contenidas en la misma matriz (*flat table*). 
* **Justificación:** No existe necesidad de montar un esquema de Base de Datos Relacional (joins, cruces 1:N) porque la unidad mínima de información (el ticket y su resolución) ya es autoconclusiva. Implementar SQL o tablas cruzadas añadiría una complejidad arquitectónica innecesaria.

---

## 7. Diccionario de datos predictivos (Capa Processed)

| Campo | Descripción | Tipo de dato | Fuente | Obligatorio | Observaciones |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ticket_id` | Identificador único alfanumérico | string | Derivado | **Sí** | *Primary Key* sintética (ej. `TKT-04512`). |
| `body` | Texto descriptivo original escrito por el cliente | string / text | Raw CSVs | **Sí** | Referencia para evaluación humana. |
| `subject` | Asunto o título del ticket | string / text | Raw CSVs | No | Imputado a "No Subject" si estaba vacío. |
| `full_text_clean` | Texto predictivo limpio (Concatenación de Asunto + Cuerpo, lematizado y sin stopwords) | string / text | Derivado | **Sí** | **Variable predictora real** para vectorización. |
| `queue` | Departamento asignado (Cola) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 1. |
| `type` | Naturaleza ITIL (Incident, Request...) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 2. |
| `priority` | Nivel de urgencia (High, Medium, Low) | string / categórico | Raw CSVs | **Sí** | Target predictivo de Nivel 3. |

*(Nota: La exclusión de la variable `answer` es una decisión arquitectónica crítica para evitar **Fuga de Datos** o Data Leakage. En un entorno real, el ticket debe enrutarse antes de ser respondido).*

---

## 8. Problemas de calidad esperados (Según EDA previo)

A través de la auditoría de los tres archivos CSV originales descargados de Kaggle, he aterrizado los siguientes problemas concretos de calidad:
1. **Valores nulos críticos:** Existen tickets sin cuerpo de texto (`body`), lo que imposibilita el cálculo de TF-IDF y el análisis léxico.
2. **Alta dispersión y ruido sintético:** Presencia de etiquetas categóricas masivas vacías (`tag_1` a `tag_9`), variables sintéticas inútiles (`version`), columnas intrusas que no aparecen en todos los ficheros (`business_type`), e información post-resolución no predictiva (`answer`).
3. **Casuística fuera de dominio:** Existen registros pertenecientes a Recursos Humanos, Retail o Consultas Genéricas que "ensucian" las fronteras de decisión de un modelo orientado a Telecomunicaciones/IT.
4. **Desbalanceo idiomático:** Un problema grave de calidad cruzada es la baja representación de tickets nativos en español.

---

## 9. Decisiones de limpieza y transformación previstas

El *pipeline* de procesamiento hacia las capas de consumo ejecutará secuencialmente las siguientes reglas de negocio y transformaciones algorítmicas:

* **Saneamiento Estructural y Nulos:**
  * Purga de columnas irrelevantes o no predictivas: `tag_1` hasta `tag_9`, `version`, `business_type` y **`answer`**.
  * Imputación estática: Los nulos de la columna `subject` se rellenarán con la cadena `"No Subject"`.
  * Borrado de filas (Dropna): Cualquier registro con nulos en `body` será eliminado de la base de datos.
* **Filtros de Dominio BPO/Telco:**
  * Se eliminan los tickets cuyas colas (`queue`) sean `Human Resources`, `Returns and Exchanges` o `General Inquiry`. 
* **Ingeniería de Características (*Feature Engineering*):**
  * **`ticket_id`:** Creación de una clave primaria alfanumérica única tras la concatenación y el reseteo del índice.
  * **`full_text_clean`:** Ejecución intensiva de un *pipeline* de NLP mediante la librería `spaCy` sobre la concatenación previa de Asunto y Cuerpo (reducción a minúsculas, eliminación de puntuación, filtrado de *stopwords* y extracción de lemas).
* **Segregación de Processed a Features:**
  * Los datos se filtrarán por idioma, guardando el dataset consolidado en `data/processed/df_final_silver.parquet` y extrayendo las matrices dispersas finales TF-IDF hacia `data/features/`.

---

## 10. Riesgos del modelo de datos

* **¿Qué parte está más clara?** La estructura final de la tabla desnormalizada. Al acotarlo estrictamente a las variables de la tripleta y los textos limpios (`full_text_clean`), purificando el dataset de "peso muerto" como el `answer`, el modelo de datos es inmutable y encaja a la perfección con la librería Scikit-Learn.
* **¿Qué parte genera más incertidumbre?** La "limpieza semántica" en la construcción de `full_text_clean`. Aunque la estructura sea robusta, es probable que la lematización de spaCy arrastre solapamiento semántico (Concept Drift) o pierda matices técnicos cruciales para el dominio de las telecomunicaciones.
* **¿Qué tabla/fichero puede dar más problemas?** El tercer archivo CSV crudo (`dataset-tickets-multi-lang3-4k.csv`), al ser el fichero con mayores anomalías estructurales detectadas.
* **¿Qué ocurriría si la vectorización colapsa?** Si el procesamiento NLP de spaCy sobre todo el volumen excede los límites de memoria, la vectorización de `full_text_clean` fracasará. El riesgo está mitigado parametrizando la limpieza por *batches*.
* **Riesgo crítico de la Alta Dimensionalidad Combinatoria:** Al contar con un corpus base acotado (~16.000 tickets útiles), existía el riesgo histórico de que el volumen fuera insuficiente al segmentarse en múltiples combinaciones de clases. Como técnica primaria apliqué sobremuestreo sintético (**SMOTE**) con éxito.
* **¿Qué alternativa tendría para simplificar el modelo si fuera necesario?** Si a pesar del SMOTE, la vectorización NLP hubiera colapsado estadísticamente frente a las 84 clases de la "Tripleta", la alternativa de contingencia (Plan B) habría consistido en desnormalizar el modelo de datos eliminando las columnas `type` y `priority` de la variable objetivo. El modelo de clasificación se habría simplificado para predecir únicamente la variable de Nivel 1 (`queue` - 5 categorías), aliviando la carga dimensional. Afortunadamente, **las pruebas empíricas han demostrado que el dataset es capaz de sostener la complejidad de la tripleta completa**, por lo que no ha sido necesario degradar el alcance de la solución.
