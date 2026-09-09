# Hoja de Ruta: Batería de Modelos y Evolución MLOps (V8)

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

## FASE 5: Orquestador Maestro y Hold-Out (COMPLETADA)
**Objetivo:** Ingesta total y cierre del experimento.

*   **Full-Shot Train:** Entrenamiento sin *K-Fold* sobre los 23.000 tickets durante 10 épocas ininterrumpidas (GPU A100).
*   **Veredicto de Cuarentena:** Se ingesta el *Test Set* ciego, arrojando la telemetría oficial del negocio: **30.46% Tasa Automatización**, **78.63% Precisión**, **F1-Macro 0.515**.
*   **Compilación:** Guardado del binario `.safetensors`.

---

## FASE 6: Visualización y Auditoría de Negocio (ACTUAL)
**Objetivo:** Extraer conocimiento y generar los entregables para el Tribunal.

*   **Paso 6.1:** Crear cuaderno local `06_Evaluacion_y_Visualizacion_Negocio.ipynb`.
*   **Paso 6.2:** Ingestar los archivos `.csv` de resultados (*Random Forest* vs *RoBERTa*).
*   **Paso 6.3:** Renderizar gráficos clave: Curvas de convergencia, gráficas de barras comparativas y la gran matriz de confusión ciega.

---

## FASE 7: MLOps y Despliegue Backend (FUTURO)
**Objetivo:** Convertir el binario matemático en un producto de software integrable.

*   **API REST:** Levantar un contenedor `FastAPI` asíncrono exponiendo la ruta `/predict`.
*   **Gestor de Reglas:** Lógica BPO que lea la salida del *Softmax* y la intercepte en función del umbral ($P \ge 0.60$).
*   **Prototipo Visual:** Interfaz mínima (`Streamlit`) para ejecutar demostraciones en vivo.
