# Documento Técnico: Estrategia de Partición y Registro de Experimentos (Nivel 1)

## 1. Prevención de Data Leakage y Split Estratificado
En estricto cumplimiento del Plan de Evaluación del MVP, se ha ejecutado un *split* estratificado (Train/Validation/Test) antes de aplicar cualquier vectorización matemática sobre el corpus[cite: 4]. 

La partición se ha estructurado en proporciones `70 / 15 / 15`:
* **Train (70%):** Conjunto exclusivo para el ajuste (`fit`) del vocabulario del modelo TF-IDF y el entrenamiento de los algoritmos de clasificación.
* **Validation (15%):** Conjunto para la calibración de hiperparámetros y la definición empírica del umbral de confianza operativa.
* **Test (15%):** Conjunto *hold-out* inmutable, utilizado únicamente para reportar las métricas finales de negocio.

La estratificación se ha forzado sobre la variable objetivo de Nivel 1 (`queue`). Esto garantiza empíricamente que las clases minoritarias pero críticas (ej. *Service Outages and Maintenance*, ~4.29%) mantengan su distribución estadística inalterada en los tres bloques, permitiendo una evaluación de métricas por clase rigurosa (F1-Score, Precisión, Recall)[cite: 4].

## 2. Estandarización de Índices (MLOps)
Para prevenir corrupciones silenciosas de datos y desalineaciones de matrices durante la posterior inyección de características, se ha forzado un reinicio de índices (`reset_index(drop=True)`) en todos los subconjuntos tras la partición, asegurando la integridad estructural de las matrices `X` y los vectores `y`.

## 3. Inicialización del Baseline (TF-IDF) y Tracker de Experimentos
El diseño arquitectónico del MVP exige establecer un *baseline* robusto (TF-IDF) antes de iterar hacia modelos semánticos complejos (Embeddings)[cite: 4]. 

Para auditar el *trade-off* entre rendimiento y coste computacional, se inicializa un *Experiment Tracker* tabular. Esta estructura almacenará los resultados de cada iteración (Regresión Logística, Random Forest, XGBoost) y las estrategias de balanceo, documentando tiempos de inferencia y métricas F1-Macro. El vectorizador TF-IDF limitará la dimensionalidad matemática ajustando sus pesos de frecuencia exclusivamente sobre `X_train`, tratando cualquier término nuevo en Validación y Test como *Out of Vocabulary* (OOV), replicando así el comportamiento real de la futura API.