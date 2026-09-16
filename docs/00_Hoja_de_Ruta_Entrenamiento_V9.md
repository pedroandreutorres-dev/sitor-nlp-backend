# Hoja de Ruta: Batería de Modelos y Evolución MLOps (V9)

Este documento central es el mapa inmutable del proyecto SITOR. Registra las fases algorítmicas, desde el tratamiento crudo de los datos hasta el empaquetado del orquestador final.

---

## FASE 1: Ingeniería de Target y Reproducibilidad Estricta
**Objetivo:** Crear un conjunto de datos estable, fiel a la volumetría del negocio (BPO).

*   **Paso 1.1 - Fusión de la Tripleta:** Concatenación de `Queue`, `Type` y `Priority`.
*   **Paso 1.2 - Data Splitting Hermético:** División 80% Train y 20% Test (*Hold-Out Ciego*).
*   **Paso 1.3 - Exportación Parquet:** Congelación en disco (`train_set_v7.parquet`, `test_set_v7.parquet`) como fuente de verdad inviolable.

---

## FASE 2: Bake-Off de Machine Learning Clásico (Fase Estadística)
**Objetivo:** Orquestar el torneo de los modelos matemáticos lineales sobre matrices dispersas.

*   **Vectorización:** `TF-IDF`.
*   **Manejo de Desbalanceo:** Aplicación estricta de `SMOTE` exclusivamente dentro de los pliegues de entrenamiento (*K-Fold*).
*   **Ganador Estadístico:** **Random Forest**. Superó a LightGBM, Logistic Regression y Naive Bayes, estableciendo el techo de cristal geométrico del ML tradicional (Tasa de Automatización plana, incapacidad semántica).

---

## FASE 3: Intervención Taxonómica
**Objetivo:** Eliminar la asfixia del optimizador causada por colas de negocio imposibles.

*   **Identificación del Ruido:** Detección de colas de derivación residual (< 50 tickets).
*   **Colapso Manual:** Transformación forzosa de 13 clases minoritarias irrelevantes hacia la etiqueta `Derivacion_Manual_Minoritaria`. El espacio de predicción se optimiza a **90 clases estables**.

---

## FASE 4: Incursión Deep Learning (Fallos e Iteración)
**Objetivo:** Romper la barrera del *F1-Macro* empleando redes neuronales masivas.

*   **Intento 1 (SetFit):** El paradigma *Contrastive Learning* colapsó por estrangulamiento geométrico y restricciones de VRAM.
*   **Intento 2 (Sequence Classification):** Pivotaje hacia el clasificador nativo de Hugging Face.
*   **Selección de Motor:** Se despliega `roberta-base` (125M de parámetros) sobre aceleradores gráficos dedicados.
*   **Estabilización del Gradiente:** El peso lineal estándar hundía el modelo. Se inyectan `Square Root Class Weights` (Raíz cuadrada de frecuencias) para proteger a las minorías sin destruir el acierto masivo.

---

## FASE 5: Orquestador Maestro, Hold-Out e Inferencia Cloud (COMPLETADA)
**Objetivo:** Ingesta total, cierre del experimento y extracción cruda de logits.

*   **Full-Shot Train:** Entrenamiento sin *K-Fold* sobre los 23.000 tickets durante 10 épocas ininterrumpidas (GPU A100).
*   **Veredicto de Cuarentena:** Se ingesta el *Test Set* ciego, arrojando la telemetría oficial del negocio.
*   **Compilación:** Guardado del binario `.safetensors`.
*   **Inferencia Cloud (Cuaderno 06):** Extracción de probabilidades puras (Softmax) en GPU usando el entorno Cloud, resultando en `predicciones_holdout_roberta.csv`.

---

## FASE 6: Visualización y Auditoría de Negocio (COMPLETADA)
**Objetivo:** Extraer conocimiento, cruzar predicciones ciegas con volumetría real y demostrar rentabilidad financiera.

*   **Celda 2 (Bake-Off):** Validación de estabilidad comparando K-Fold (Baseline) vs K-Fold (RoBERTa).
*   **Celda 3 (Fricción):** Matriz masiva y aislamiento de las Top 10 Colisiones Taxonómicas.
*   **Celda 4 (Guillotina):** Gráfico de densidad (KDE) evidenciando el mecanismo de pasividad.
*   **Celda 5 (Sensibilidad):** Optimización iterativa aislando el *Break-Even* financiero bajo regímenes de estrés (25% error humano).
*   **Celda 6 y 7 (Waterfall y ROI):** Desglose del ahorro neto mensual e impacto estructural (Attrition, SLA, Backlog).

---

## FASE 7: MLOps y Despliegue de Interfaz (ACTUAL)
**Objetivo:** Convertir el artefacto de modelado en un ecosistema de microservicios.

*   **Backend Analítico (FastAPI):** Exposición de inferencia REST en `src/api/main.py`. Integración del Gestor de Reglas paramétrico.
*   **Frontend Ejecutivo (Streamlit):** Despliegue de un dashboard interactivo en `src/frontend/app.py` para inyección de tickets y auditoría de telemetría en tiempo real.
