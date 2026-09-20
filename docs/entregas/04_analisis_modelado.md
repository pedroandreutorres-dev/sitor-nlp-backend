# 04 - Diseño del Análisis y Estrategia de Modelado

## 1. Problema que se busca resolver
En el sector del soporte técnico (BPO), los agentes de Front Office operan bajo presión, lo que puede provocar errores al clasificar manualmente las incidencias en el CRM (asignación de la "Tripleta": Cola / Tipo / Prioridad). Actualmente, un error en esta tipificación genera un "falso escalado" hacia departamentos de Back Office equivocados, aumentando los tiempos de resolución (AHT) y los costes operativos por retrabajo.

El resultado concreto que persigue este proyecto es construir **SITOR**, un sistema basado en Procesamiento de Lenguaje Natural (NLP / Deep Learning) que actuará como un auditor en tiempo real. La utilidad del proyecto quedará validada si el modelo es capaz de analizar tickets entrantes, extraer sus características semánticas y predecir su enrutamiento correcto basándose en umbrales de confianza (*Confidence Thresholding*). Esto permitirá una auto-corrección algorítmica solo cuando el modelo esté estadísticamente seguro (Softmax alto), evitando falsos positivos.

## 2. Análisis de datos planteado y utilidad esperada
El análisis exploratorio ha estado orientado a preparar la taxonomía y mitigar sesgos metodológicos:
*   **Dimensionalidad de clases:** Se ha analizado la distribución de frecuencias. Se observó que las clases con menos de 30 muestras carecen de soporte estadístico suficiente para el entrenamiento, justificando su agrupación en clases genéricas (`OUT_OF_SCOPE`).
*   **Mitigación de desbalanceo (Descarte de SMOTE):** A diferencia de problemas con datos tabulares, la generación sintética (SMOTE) se descartó metodológicamente en favor del uso de pesos de clase suavizados (*Smoothed Class Weights*) integrados directamente en la función de pérdida del modelo (`CrossEntropyLoss`), para mantener la estructura original del texto.
*   **Deduplicación de datos:** Se ejecutó una limpieza (deduplicación) sobre la variable `full_text` en la capa Silver para evitar solapamientos entre los conjuntos de entrenamiento y test (*Data Leakage*).

## 3. Tipo de modelos que se van a plantear
El problema se enmarca en una tarea de clasificación de secuencias de alta cardinalidad. La estrategia de modelado plantea una transición desde algoritmos estadísticos hacia arquitecturas semánticas basadas en redes neuronales.

| Alternativa | Tipo | Por qué se plantea | Limitación principal empírica |
| :--- | :--- | :--- | :--- |
| **Baseline 1** | Regresión Logística y Naive Bayes (TF-IDF) | Proporcionan un rendimiento inicial rápido y robusto frente a la alta dimensionalidad dispersa. | Son modelos lineales; asumen independencia entre palabras, perdiendo el contexto semántico. |
| **Baseline 2** | Random Forest (TF-IDF) | Algoritmo de ensamble. Su arquitectura mitiga el sobreajuste y funciona bien con frecuencias de palabras. | Tendencia al sobreajuste durante la hiperparametrización. La comparación con redes requiere evaluar el mismo espacio de etiquetas. |
| **Alternativa 3** | SetFit (Few-Shot Transformer) | Framework diseñado para entrenar *Sentence Transformers* con pocos datos. Adecuado para hardware local. | Alto coste computacional. La generación de pares contrastivos superó los recursos de memoria y CPU del entorno local (tiempo estimado > 640 horas). |
| **Modelo Seleccionado** | RoBERTa-base (125M params) | Arquitectura *Transformer* basada en atención. Capacidad bidireccional para capturar el contexto. | Requiere aceleración por hardware (GPU T4/A100) en un entorno Cloud (Colab). Ofrece la calibración probabilística continua necesaria para las reglas de negocio. |

## 4. Datos de entrada del análisis y los modelos
La entrada al modelo predictivo consumirá la información generada en la Capa Gold.

*   **Nombre del dataset:** `train_set_v7.parquet` (Entrenamiento) y `test_set_v7.parquet` (Validación Hold-out).
*   **Granularidad:** Una fila representa exactamente un ticket de soporte individual.
*   **Variables de entrada principales:** `full_text` (Concatenación de Asunto y Cuerpo del correo). En el modelo final, este texto se procesa a través del Tokenizador BPE de RoBERTa.
*   **Variables descartadas:** Se eliminó la columna de respuesta del técnico (`answer`) para prevenir fuga de datos. En producción, la predicción debe ocurrir antes de la intervención del técnico.

| Entrada | Descripción | Granularidad / tipo | Uso en el análisis o modelo |
| :--- | :--- | :--- | :--- |
| `full_text` | Texto original (Asunto + Cuerpo). | Texto | Variable independiente (Ingesta al Tokenizador). |
| `target_tripleta` | Concatenación de `queue`, `type` y `priority`. | Categórica (90 clases) | Variable dependiente (Codificada numéricamente). |

## 5. Datos de salida y forma de consumo
El modelo generará una distribución de probabilidades (Softmax) para alimentar el motor de reglas. La salida se consumirá a través de un microservicio.

*   **Cómo utilizará el usuario la salida:** El orquestador consultará un endpoint (`FastAPI`). Si la predicción contradice la clasificación humana con una probabilidad $\ge$ 80% (umbral base), el sistema aplicará un estado `OVERRIDE` (auto-corrección). Si no alcanza el umbral, el orquestador asume `VERIFIED` o delega a una revisión manual, mitigando el impacto de posibles errores algorítmicos.

| Campo de salida | Descripción | Tipo | Uso posterior |
| :--- | :--- | :--- | :--- |
| `ticket_id` | Identificador del ticket. | string | Trazabilidad y unión con el CRM. |
| `tripleta_predicha` | La clase predicha por el modelo. | string | Contraste contra el valor humano original. |
| `probabilidad_max` | Nivel de confianza matemática (Softmax 0.0 - 1.0). | float | Parámetro para las reglas de auto-enrutamiento. |
