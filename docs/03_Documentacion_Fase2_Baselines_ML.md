# Documentación de Fase 2: Baselines Clásicos (Machine Learning) - SITOR V7.2

**Fecha de Ejecución:** Septiembre 2026
**Notebook Asociado:** `02_Entrenamiento_Baselines_ML.ipynb`
**Objetivo:** Establecer la línea base de rendimiento mediante algoritmos clásicos de Machine Learning operando sobre un espacio léxico discreto (TF-IDF), fijando el umbral mínimo operativo para los modelos neuronales posteriores.

---

## 1. Arquitectura del Entorno de Evaluación (Orquestador BPO)

Para garantizar un *Bake-Off* (comparativa de modelos) científicamente válido, se programó un orquestador determinista (`evaluar_modelo_bpo`). Sus restricciones operativas son:
*   **Aislamiento de Folds:** Iteración estricta sobre la variable `fold_id` inyectada en la Fase 1, evitando cualquier fuga de datos (*Data Leakage*).
*   **Encapsulación de Vectorización:** Instanciación del `TfidfVectorizer` dentro del Pipeline para asegurar que el diccionario léxico se ajusta exclusivamente con el conjunto de entrenamiento de cada pliegue.
*   **Motor Auditor (Quality Assurance):** Implementación de una barrera operativa. Si la probabilidad máxima predicha (`predict_proba`) es menor a 0.60, el ticket es derivado a `MANUAL_REVIEW`. Si es mayor o igual, el modelo audita (valida o auto-corrige) la decisión del agente.

---

## 2. Definición del Espacio Vectorial Léxico (TF-IDF)

El texto crudo (`full_text`) se proyectó a un hiperplano matemático mediante `TfidfVectorizer`.
*   **Eliminación de Ruido:** Se inyectó `stop_words='english'`.
*   **Restricción de Dimensionalidad:** Se aplicó `max_features=15000` para acotar la explosión de memoria RAM, descartando la cola léxica menos relevante pero reteniendo el núcleo semántico del dataset.

---

## 3. Modelo A: Ensamblado no lineal (Random Forest Calibrado)

El primer baseline testó la capacidad de particionado geométrico ortogonal de los árboles de decisión sobre la alta dimensionalidad dispersa.
*   **Hiperparámetros:** `class_weight='balanced'` para obligar al algoritmo a penalizar duramente los errores en las clases minoritarias del *long tail* (102 clases totales).
*   **Corrección Probabilística:** Se envolvió el estimador en `CalibratedClassifierCV(method='sigmoid', cv=2)`. Esta decisión arquitectónica fue crucial: duplicó el tiempo de entrenamiento estructural pero forzó el ajuste de las votaciones del bosque a una curva matemática paramétrica (escalado de Platt), purificando la matriz de probabilidades y permitiendo el uso del umbral 0.60 sin falsas certezas.

---

## 4. Modelo B: Hiperplano Lineal (Regresión Logística Multinomial)

El segundo baseline testó la separabilidad lineal del espacio TF-IDF.
*   **Hiperparámetros:** `class_weight='balanced'` y `max_iter=1000`.
*   **Optimización Estocástica (Hardware Contingency):** Ante el riesgo de colapso de RAM derivado del solucionador `lbfgs` (que aproxima la matriz Hessiana completa), se inyectó de forma defensiva `solver='saga'`. Este algoritmo opera mediante gradiente estocástico promedio, ideal para matrices ralas (*sparse*), asegurando la convergencia en CPUs estándar a cambio de un mayor tiempo de ejecución.

---

## 5. Veredicto y Fijación de la Línea Base BPO

El cruce de telemetría arrojó las siguientes conclusiones definitivas:

1.  **Colapso Lineal:** El Modelo B (Regresión Logística) fue incapaz de aislar las 102 clases (Tasa de Automatización del 0.94%, F1-Macro 0.31). Queda demostrado empíricamente que el espacio léxico discreto exige algoritmos con fronteras de decisión no lineales.
2.  **Victoria del Baseline:** El Modelo A (Random Forest) se consolidó como ganador del ML clásico. Sus métricas de impacto BPO fijan la "Línea de Vida" que los modelos neuronales de las fases 3 y 4 deberán superar: **11.71% de Tasa de Automatización de Auditoría** con un **99.07% de Precisión Condicionada**.
3.  **Cuello de Botella Representacional:** El parón de rendimiento no obedece a un límite del clasificador, sino a la ceguera semántica del TF-IDF (representación estadística de palabras sueltas sin contexto profundo). Esto justifica sólidamente la transición hacia vectores neuronales densos (*Embeddings*) en la Fase 3.
