# Roadmap de Entrenamiento Dual (Inglés y Español)

## Arquitectura de Entrenamiento Paralelo

Este documento define la metodología estricta para la fase de modelado del MVP. Tras realizar el Test A/B de idioma y comprobar que la traducción automática degrada el rendimiento de los modelos más simples (Naive Bayes), se ha tomado una **decisión de negocio crítica**: desarrollar y entrenar los modelos avanzados en **ambos idiomas en paralelo** (Dual-Track Experimentation). 

El objetivo es construir una matriz de Coste/Beneficio. Evaluaremos si la diferencia de rendimiento entre un modelo nativo en español y un modelo en inglés (que requiere traducción en tiempo real mediante API) justifica los sobrecostes operativos.

---

## 1. Fases del Preprocesado NLP (Pipeline)

El texto predictivo se extrae de la concatenación de `subject` y `body` (`full_text`). Dependiendo del idioma, el procesamiento varía:
* **Inglés (Notebook 02):** Limpieza y lematización utilizando el motor `en_core_web_sm` de spaCy.
* **Español (Notebook 04):** Limpieza y lematización utilizando el motor `es_core_news_sm` de spaCy, eliminando *stop-words* específicas del castellano.

---

## 2. Matriz de Experimentación Definitiva (SITOR V6)

Para demostrar científicamente el impacto del balanceo de datos, se ha diseñado una estrategia basada en **Ablation Studies** (comparar el mismo algoritmo con y sin balanceo). Se probarán 6 familias de algoritmos en orden ascendente de complejidad:

### Fase 1: Baseline Estadístico (Completado)
* **Modelo:** Multinomial Naive Bayes (MNB)
* **Balanceo:** Ninguno (`None`).
* **Objetivo:** Establecer la marca de agua y demostrar el sesgo hacia la clase mayoritaria.

### Fase 2: Modelos Lineales (Estudio de Ablación SMOTE)
* **Modelos:** Regresión Logística (LogReg) y LinearSVC.
* **Balanceo:** Sin SMOTE vs Con SMOTE.
* **Objetivo:** Estos modelos son hiper-rápidos. Medir su rendimiento con y sin SMOTE demostrará matemáticamente que la inyección de datos sintéticos es la clave para rescatar el Recall de las averías críticas sin penalizar la latencia operativa.

### Fase 3: Ensamblado Básico (Bagging)
* **Modelo:** Random Forest (RF).
* **Balanceo:** Sin SMOTE vs Con SMOTE.
* **Objetivo:** Demostrar que los algoritmos basados en árboles de decisión sufren fuertemente ante el desbalanceo si no se fuerza la creación de datos de las clases minoritarias.

### Fase 4: Titanes Industriales (Boosting y Pesos de Clase)
* **Modelos:** XGBoost y LightGBM.
* **Balanceo:** SMOTE vs Class Weights (Equilibrado matemático interno del algoritmo).
* **Objetivo:** Buscar el "Techo de Precisión". Estos algoritmos pesados incorporan mecánicas nativas de penalización de errores. El experimento determinará si es más óptimo generar datos falsos (SMOTE) o penalizar matemáticamente al modelo cuando falla en una avería (*Class Weights*). Se comparará también la eficiencia computacional entre XGBoost y el framework de Microsoft (LightGBM).

---

## 3. Estructura del Registro de Experimentos (Experiment Trackers)

Se mantienen dos DataFrames paralelos (`tracker_df_en` y `tracker_df_es`) con la siguiente estructura idéntica para facilitar la auditoría cruzada:

| Columna | Descripción | Justificación |
| :--- | :--- | :--- |
| `exp_id` | Identificador único (ej. `EN_L1_TFIDF_XGB_SMOTE`) | Trazabilidad del experimento y del idioma. |
| `target_level` | `queue`, `type`, o `priority` | Nivel actual de la cascada. |
| `vectorization` | `tfidf` o `embeddings` | Evaluar coste de extracción de features. |
| `model` | `mnb`, `logreg`, `linearsvc`, `rf`, `xgboost`, `lightgbm` | Evaluar algoritmo base. |
| `balancing` | `none`, `weights`, o `smote` | Evaluar mitigación del sesgo. |
| `hyperparameters` | JSON o texto con los parámetros (ej. `n_estimators=500`) | Permite replicar el modelo exacto y comparar iteraciones de *Fine-Tuning*. |
| `train_time_sec` | Tiempo de entrenamiento en segundos | Métrica de complejidad de MLOps. |
| `inference_time_ms` | Tiempo de predicción en milisegundos | Crítico para la latencia del microservicio FastAPI. |
| `f1_macro` | Métrica global sin sesgo por volumen | Evalúa el rendimiento general equilibrado. |
| `f1_minority_class` | F1-Score de *Service Outages* | Métrica de negocio: Detección de averías masivas. |
