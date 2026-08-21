# Documentación del Análisis Exploratorio de Datos (EDA)
## Dataset: df_02 (`df_dataset-tickets-multi-lang-4-20k`)

Este documento recoge los hallazgos, la auditoría estructural y las decisiones de limpieza técnica aplicadas al segundo dataframe (`df_02`), con el objetivo de garantizar su absoluta compatibilidad con `df_01` antes de la fase de concatenación. El dataset forma parte de la muestra "Multilingual Customer Support Tickets" seleccionada para el MVP[cite: 3].

---

## 1. Validación de Compatibilidad del Target (La Tripleta CRM)

Para que el modelo NLP aprenda sin generar clases duplicadas o ruido por discrepancias de nomenclatura, se verificó que la variable objetivo (la tripleta aproximada) en `df_02` fuera un clon estructural de `df_01`.

### 1.1. Columna `queue` (Nivel 1 - Departamentos)
La auditoría de valores únicos confirma una coincidencia exacta de las 10 categorías existentes:
* **Mantenidas (Core BPO/Telco):** `Technical Support` (3.412), `Product Support` (2.232), `Customer Service` (1.859), `IT Support` (1.391), `Billing and Payments` (1.302), `Service Outages and Maintenance` (442), `Sales and Pre-Sales` (330).
* **A descartar (Fuera de Dominio):** `Returns and Exchanges` (582), `Human Resources` (205), `General Inquiry` (168).
* *Decisión Técnica:* Se aplica el mismo filtro de exclusión que en `df_01` para asegurar que el clasificador se entrena evaluando fronteras semánticas coherentes con el sector tecnológico y de telecomunicaciones[cite: 3].

### 1.2. Columnas `type` y `priority` (Niveles 2 y 3)
* **`type`:** Confirmación de las 4 categorías ITIL idénticas (`Request`, `Problem`, `Incident`, `Change`).
* **`priority`:** Confirmación visual de la estructura de 3 niveles (`low`, `medium`, `high`).

---

## 2. Auditoría del Texto Libre y Nulos (Pipeline NLP)

El análisis de completitud (`.info()` y `.isnull().sum()`) sobre los 11.923 registros originales reveló las siguientes incidencias en los campos de texto, requiriendo un tratamiento ligeramente distinto al del primer dataset:

1. **`body` (1 valor nulo):** A diferencia de `df_01`, este dataset contiene un ticket sin cuerpo de texto.
   * *Impacto y Decisión:* Un registro sin la *feature* principal de entrada es inútil para la vectorización (TF-IDF/Embeddings). Se elimina la fila de raíz.
2. **`answer` (3 valores nulos):** Se mantiene el patrón del dataset anterior.
   * *Decisión:* Se eliminan para asegurar la integridad de la futura base vectorial (ChromaDB) en caso de desarrollar la extensión RAG opcional[cite: 3].
3. **`subject` (1.032 valores nulos):** Patrón habitual de usuarios que no especifican asunto.
   * *Decisión:* Imputación estática con la cadena `"No Subject"`.

---

## 3. Auditoría de las Columnas de Etiquetas (`tag_1` a `tag_8`)

Al igual que en `df_01`, se comprobó la estructura de los *tags*. 
* **Diagnóstico:** Se repite la degradación crítica por valores nulos (la columna `tag_8` solo posee 1.327 datos válidos frente a los más de 10.000 nulos). Además, persiste la ausencia de jerarquía y la mezcla caótica de conceptos (`Feedback`, `Compliance`, `Breach`).
* **Decisión:** Descarte total de las 8 columnas para evitar *sparsity* y ruido algorítmico.

---

## 4. Plan Definitivo de Limpieza y Transformación (`df_02`)

Para estandarizar el `df_02` al formato de 7 columnas requeridas por el MVP, se ejecuta el siguiente pipeline secuencial:

1. **Purga de columnas:** Eliminación de todas las columnas que comiencen por la cadena `tag_`. (Nota: Este dataset no contenía la columna sintética `version`, por lo que no es necesario dropearla).
2. **Filtrado de Dominio (Filas):** Eliminación de registros donde `queue` pertenezca a `Human Resources`, `Returns and Exchanges` o `General Inquiry`.
3. **Imputación de Asuntos:** `df_02['subject'].fillna('No Subject')`.
4. **Depuración de Textos Clave:** `df_02.dropna(subset=['answer', 'body'])`.
5. **Reconstrucción Estructural:** Reseteo del índice con `drop=True`.

---

## 5. Resultado de la Ejecución (Sanity Check)

Tras la ejecución del script de limpieza, la validación de integridad técnica arroja los siguientes resultados definitivos, dejando el dataset listo para su unificación con `df_01`:

* **Dimensiones Finales:** El dataset se ha reducido de 11.923 filas x 15 columnas a una matriz exacta de **10.964 filas y 7 columnas** (reducción fundamentada en la exclusión de ruido categórico y registros fuera de dominio).
* **Integridad de Datos (Nulos):** Conteo de **0 absoluto** en las 7 columnas. Se confirma la eliminación exitosa del registro inservible por ausencia de `body` y de las 3 filas sin `answer` (para proteger el módulo RAG opcional[cite: 3]).
* **Consistencia de Dominio:** La distribución de la variable objetivo (`queue`) contiene estrictamente las 7 categorías alineadas con la casuística de soporte BPO/Telco.
* **Índice:** Limpio y contiguo (`RangeIndex`), sin columnas de indexación residuales.