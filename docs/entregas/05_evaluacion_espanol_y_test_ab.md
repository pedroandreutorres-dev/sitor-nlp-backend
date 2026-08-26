# Test A/B: Evaluación del Dataset Traducido (Español)

## 1. Hipótesis de Investigación
El objetivo central de este experimento era determinar si la traducción neuronal masiva de tickets IT del inglés al español (mediante el modelo *Helsinki-NLP/opus-mt-en-es*) aportaba valor semántico que facilitara la clasificación de la Tripleta (84 clases), o si por el contrario introducía ruido que degradaría el rendimiento de los modelos matemáticos.

## 2. Metodología
Se generó un dataset íntegramente en español (`df_final_silver_es.parquet`) fusionando los tickets nativos y los traducidos. Se aplicó una arquitectura estructuralmente idéntica a la fase inglesa:
*   **Split:** 80/20 estratificado.
*   **NLP:** `es_core_news_sm` de spaCy (Lematización y eliminación de *stop words*).
*   **Vectorización:** TF-IDF limitado a 10.000 características.
*   **Balanceo:** Aplanamiento de las 84 clases mediante generación de sintéticos (SMOTE).

## 3. Resultados Cuantitativos (Tracker Español)

A continuación se presenta la tabla de resultados de los 6 algoritmos enfrentados al dataset en español, con y sin balanceo matemático:

| Modelo | Condición | F1-Macro | F1-Micro | Precision (Macro) | Recall (Macro) | Tiempo (seg) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Random Forest | Con SMOTE | **0.6658** | 0.6280 | 0.7957 | 0.6002 | 185.50 |
| Random Forest | Sin SMOTE | 0.5982 | 0.5649 | 0.8171 | 0.5063 | 8.41 |
| Linear SVC | Con SMOTE | 0.5884 | 0.5253 | 0.6202 | 0.5807 | 123.41 |
| Linear SVC | Sin SMOTE | 0.5738 | 0.5186 | 0.6632 | 0.5271 | 17.59 |
| Regresion Logistica | Con SMOTE | 0.5210 | 0.4346 | 0.5432 | 0.5243 | 140.02 |
| XGBoost | Con SMOTE | 0.3855 | 0.3756 | 0.4897 | 0.3415 | **5178.65** |
| Naive Bayes | Con SMOTE | 0.3758 | 0.3312 | 0.3528 | 0.4731 | 0.66 |
| XGBoost | Sin SMOTE | 0.4115 | 0.4135 | 0.5733 | 0.3552 | 1078.55 |
| Regresion Logistica | Sin SMOTE | 0.1599 | 0.2989 | 0.3518 | 0.1477 | 22.52 |
| Naive Bayes | Sin SMOTE | 0.0308 | 0.1783 | 0.0826 | 0.0450 | 0.11 |
| LightGBM | Sin SMOTE | 0.0072 | 0.0522 | 0.0156 | 0.0159 | 219.38 |
| LightGBM | Con SMOTE | 0.0002 | 0.0054 | 0.0001 | 0.0115 | 1965.13 |

## 4. Comparativa Test A/B (Inglés vs Español)

Para resolver la hipótesis, enfrentamos a nuestro campeón arquitectónico (Random Forest con SMOTE) en sus versiones para ambos idiomas:

| Idioma del Dataset | Algoritmo | F1-Macro | Recall (Macro) | Tiempo de Entrenamiento | Límite Dimensional Alcanzado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nativo (Inglés)** | Random Forest + SMOTE | **0.6818** | **0.6262** | **131.84 s** | 4.717 features |
| Traducido (Español)| Random Forest + SMOTE | 0.6658 | 0.6002 | 185.50 s | 10.000 features |

## 5. Conclusiones y Veredicto Científico

1. **El Ruido de la Traducción (Penalización Dimensional):** Se demostró empíricamente que el modelo de traducción neuronal introduce dispersión semántica. Al traducir jerga técnica, generó múltiples sinónimos y variaciones de género/número, forzando a la matriz TF-IDF a chocar contra su límite máximo de 10.000 dimensiones (frente a las 4.717 del inglés). Este ruido matemático degradó el F1-Macro del modelo final en ~2 puntos porcentuales.
2. **El Colapso del Boosting:** Los modelos de ensamblaje secuencial demostraron ser incompatibles con matrices de alta dispersión hiper-balanceadas. XGBoost invirtió **más de 1.4 horas** (5178 segundos) en procesar la matriz española para obtener un resultado mediocre, frente a los 3 minutos de la arquitectura Bagging (Random Forest).
3. **Veredicto de Negocio:** La recomendación arquitectónica definitiva para la empresa es prescindir de la capa de traducción automática. El sistema de enrutamiento más robusto, preciso y eficiente en costes computacionales es el procesamiento directo sobre el dataset **Nativo en Inglés** utilizando **Random Forest apoyado sobre SMOTE**.
