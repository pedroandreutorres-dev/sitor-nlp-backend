# Documentación del Análisis Exploratorio de Datos (EDA)
## Dataset: df_03 (`dataset-tickets-multi-lang3-4k.csv`)

Este documento recoge los hallazgos, la auditoría estructural y las decisiones de limpieza técnica aplicadas al tercer dataframe (`df_03`), perteneciente a la colección pública "Multilingual Customer Support Tickets" elegida para el MVP[cite: 2]. El objetivo de este análisis es forzar la compatibilidad estructural de este bloque con el esquema estricto de 7 variables ya validado en los fragmentos anteriores antes de su concatenación.

---

## 1. Validación de Compatibilidad del Target (La Tripleta CRM)

Para evitar la generación de ruido y la duplicidad de clases en el motor de clasificación jerárquica, se auditó la taxonomía de la variable objetivo en este archivo, confirmando una alineación perfecta con la estructura previa:

* **Columna `queue` (Nivel 1):** Contiene las mismas 10 categorías originales, sin variaciones de nomenclatura ni duplicados por mayúsculas.
* **Columnas `type` y `priority` (Niveles 2 y 3):** Conservan exactamente las 4 categorías ITIL (`Incident`, `Request`, `Problem`, `Change`) y los 3 niveles de urgencia (`high`, `medium`, `low`).

---

## 2. Detección de Anomalías Estructurales

A diferencia de los archivos previos, la inspección de la estructura (`.info()`) y de las distribuciones de este bloque reveló anomalías críticas que requirieron tratamiento específico:

1. **La columna intrusa (`business_type`):** Se identificó una nueva variable categórica inexistente en los archivos anteriores. Su análisis de frecuencia (`IT Services`, `Tech Online Store`, etc.) confirma la orientación hacia soporte técnico y entornos B2B. Al no formar parte de las variables de entrada requeridas para el MVP[cite: 2], se determinó su eliminación total para no desalinear la matriz en la fase de concatenación.
2. **El "Tag" fantasma (`tag_9`):** El archivo genera una novena etiqueta vacía en su totalidad (inferida como `float64`), lo que agrava la dispersión (*sparsity*) ya conocida de este conjunto de columnas.

---

## 3. Auditoría de Textos, Nulos e Idioma (Pipeline NLP)

El análisis de completitud sobre los 2.203 registros originales dictaminó las siguientes acciones:

* **`subject`:** 269 valores nulos. Se decide su imputación estática (`"No Subject"`).
* **`body`:** 1 valor nulo. Al ser la característica principal (*feature*) para el entrenamiento NLP[cite: 2], se decide la eliminación del registro de raíz.
* **`answer`:** Completitud del 100%, válida para la base de conocimiento del módulo RAG opcional[cite: 2].
* **`language`:** La muestra bruta contiene tickets en inglés y español, requiriendo un conteo exacto de los tickets en español tras aplicar los filtros de dominio de negocio[cite: 2].

---

## 4. Plan Definitivo de Limpieza y Transformación (`df_03`)

Para estandarizar el `df_03` y prepararlo para la fusión, se ejecutó el siguiente pipeline secuencial:

1. **Purga de columnas incompatibles y ruido:** Eliminación de la variable intrusa `business_type` y de todas las etiquetas residuales (`tag_1` a `tag_9`) para respetar el esquema innegociable de 7 variables[cite: 2].
2. **Filtrado de Dominio (Telco/BPO):** Exclusión de los registros de colas ajenas al alcance de soporte técnico y telecomunicaciones (`Human Resources`, `Returns and Exchanges`, `General Inquiry`) para evitar desviar el aprendizaje del clasificador[cite: 2].
3. **Tratamiento de Valores Nulos:** Imputación de `"No Subject"` y eliminación de la fila carente de texto en `body`.
4. **Saneamiento del Índice:** Aplicación del reseteo de índice (`drop=True`) para garantizar la continuidad estructural.

---

## 5. Resultado de la Ejecución (Sanity Check)

Tras la ejecución del script de limpieza, los resultados de la validación técnica en consola confirman la viabilidad del dataset para su unificación:

* **Dimensiones Finales:** El dataset se consolida en una matriz exacta de **2.045 filas y 7 columnas**, alineándose con el esquema estricto requerido para el proyecto[cite: 2].
* **Integridad de Datos:** Conteo de **0 nulos** en todas las variables.
* **Consistencia de Dominio:** Se conserva únicamente la casuística afín al objetivo del Caso de Negocio[cite: 2].
* **Auditoría de Idioma (Punto Crítico):** Se han contabilizado exactamente **750 tickets útiles en español** tras el filtrado. Este volumen queda documentado para su futura suma al conjunto unificado, momento en el cual se dictaminará empíricamente la necesidad de aplicar traducción asistida para garantizar la robustez del modelo en este idioma[cite: 2].