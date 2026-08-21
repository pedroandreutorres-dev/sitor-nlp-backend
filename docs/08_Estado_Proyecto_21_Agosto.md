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

## 4. Próxima Fase: Ensamblados Avanzados y Boosting

El proyecto se dirige ahora hacia su clímax técnico. Una vez superado el modelo lineal, vamos a desplegar algoritmos de ensamblado:

1.  **Random Forest (Notebook 06):** Verificaremos si crear un bosque de 100 árboles de decisión es capaz de encontrar patrones no lineales que la Regresión Logística no supo ver.
2.  **Los Titanes del Boosting (Notebook 07):** Ejecutaremos la guerra final entre `XGBoost` (gradiente clásico) y `LightGBM` (arquitectura de hojas, auspiciado por Microsoft). Compararemos el impacto de SMOTE frente a los pesos de clase nativos de estos algoritmos.
3.  **Fase de Embudo (Fine-Tuning):** Aplicaremos `GridSearchCV` únicamente a los campeones de las rondas anteriores para exprimir su máximo potencial matemático, antes de empaquetarlos en la API de FastAPI.
