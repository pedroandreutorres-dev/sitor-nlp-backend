# Resumen Ejecutivo del Proyecto SITOR
**Fecha de corte:** 21 de Agosto de 2026

Este documento es una radiografía exacta del punto en el que se encuentra el TFM tras la clausura del Pipeline MLOps y la ejecución de la Fase Lineal de modelado.

---

## 1. El Hito Arquitectónico (Notebooks 02, 03 y 04)

Hemos superado con éxito la fase más farragosa y peligrosa del proyecto: la preparación de datos.
*   **Traducción Masiva:** Se tradujeron más de 23.000 tickets de soporte técnico al español mediante el modelo Open Source `Helsinki-NLP/opus-mt-en-es` usando técnicas de batching y checkpointing.
*   **Ingeniería NLP:** Ambos idiomas han pasado por un túnel de lavado léxico usando `spaCy`, extrayendo lemas, purgando pronombres y limpiando ruido.
*   **Serialización MLOps:** Hemos abandonado los `.csv` gigantes. Las matrices matemáticas `TF-IDF` de 10.000 dimensiones se han volcado a disco duro en formato hipercomprimido `.npz` de `SciPy`.
*   **Resultado Operativo:** Ahora podemos cargar el cerebro de los 24.000 tickets en memoria RAM en apenas **0.3 segundos**, lo que permite una iteración algorítmica ultrarrápida.

---

## 2. El Test A/B y el Descubrimiento del Baseline

En el **Notebook 04**, establecimos el *Baseline* del proyecto usando `Multinomial Naive Bayes`. 
Descubrimos empíricamente el mayor problema del dataset: **el desbalanceo brutal de clases**.
El modelo Baseline en español alcanzó un paupérrimo **5% de Recall** en la clase crítica *Service Outages*. La clase mayoritaria (*Technical Support*) ahogaba matemáticamente a las demás. 

Este aparente fracaso fue, en realidad, nuestra mayor victoria documental: nos dio la justificación de negocio innegable para aplicar Inteligencia Artificial avanzada (SMOTE y Boosting).

---

## 3. La Fase Lineal y el Éxito de SMOTE (Notebook 05)

En el **Notebook 05**, ejecutamos el Estudio de Ablación usando **Regresión Logística**, probando el impacto de inyectar datos falsos pero estadísticamente viables (`SMOTE`).

**Logros alcanzados:**
*   **Subidón de las Minorías:** Al aplicar SMOTE, clases ignoradas como *Sales* e *IT Support* duplicaron su eficacia (F1-Score).
*   **Resurrección del Español:** El modelo en español, alimentado con el texto traducido y apoyado por SMOTE, logró identificar casi el **70% de las averías críticas (Recall)**, superando al modelo nativo en inglés (64%).
*   **Trazabilidad Garantizada:** Se han creado dos Trackers Maestros (`tracker_en.csv` y `tracker_es.csv`) que guardan celosamente el resultado de cada experimento.

---

## 4. La Fase de Ensamblado: Random Forest (Notebook 06)

En el **Notebook 06**, escalamos a modelos no lineales usando técnica de *Bagging* (Random Forest con 100 árboles). 

**Logros alcanzados:**
*   **El salto de inteligencia:** Random Forest aplastó a la Regresión Logística. Incluso sin SMOTE, los árboles consiguieron un F1-Macro de 0.61 (vs 0.46 lineal).
*   **La ceguera corregida:** Al inyectarle SMOTE, Random Forest logró atrapar el **68% de las averías masivas en inglés** (F1 de 0.73) y el **64% en español** (F1 de 0.70). 
*   **Impacto MLOps:** Documentamos que la latencia de inferencia saltó de 2ms a 65ms al tener que evaluar 100 árboles por ticket, un dato crítico para la arquitectura de producción.

---

## 5. La Caída del Titán: XGBoost (Notebook 07)

Bajo la hipótesis de que el descenso de gradiente superaría al Bagging, se ejecutó un Estudio de Ablación cruzado con XGBoost, enfrentando el balanceo matemático (*Class Weights*) contra el sintético (SMOTE).

**Resultados Empíricos (Fracaso Absoluto):**
*   **Regresión Predictiva:** XGBoost se hundió a un F1-Macro de 0.51, quedando al mismo nivel que una simple Regresión Logística y muy por debajo del 0.68 de Random Forest.
*   **Colapso Computacional:** El tiempo de entrenamiento se disparó de 15 segundos a más de 4 minutos (267 segundos) al intentar procesar la matriz SMOTE ultra-dispersa.
*   **Diagnóstico:** XGBoost sufre de la Maldición de la Dimensionalidad en NLP puro si no se somete a un profundo y costoso proceso de *Hyperparameter Tuning*. 
*   **Veredicto:** Oficialmente descartado de la arquitectura de producción.

---

## 6. Siguiente Fase (Roadmap Inmediato)

1.  **La Última Bala del Boosting (LightGBM):** Evaluaremos la arquitectura de Microsoft. Si LightGBM sufre el mismo destino que XGBoost, declararemos a Random Forest vencedor absoluto de la fase algorítmica.
2.  **Hyperparameter Tuning (Embudo):** El algoritmo que sobreviva (RF o LightGBM) será sometido a `GridSearchCV` para exprimir su precisión.
3.  **Microservicio (Backend):** Despliegue del cerebro ganador en `FastAPI`.
