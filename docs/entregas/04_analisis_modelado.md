# 04 - Diseño del Análisis y Estrategia de Modelado

## 1. Problema que se busca resolver
En el sector del soporte técnico (BPO), los agentes de Front Office (Nivel 1) operan bajo extrema presión de tiempo, lo que provoca errores frecuentes al clasificar manualmente las incidencias de los clientes en el CRM (asignación de la "Tripleta": Cola / Tipo / Prioridad). Actualmente, un error humano en esta tipificación genera un "falso escalado" hacia departamentos de Back Office (Nivel 2) equivocados, disparando los tiempos de resolución (AHT) y los costes operativos por retrabajo.

El resultado concreto que persigue este proyecto es construir **SITOR**, un motor basado en Procesamiento de Lenguaje Natural (NLP) que actuará como un auditor en tiempo real. La utilidad del proyecto quedará validada si el modelo es capaz de interceptar tickets entrantes, leer su descripción textual y predecir su enrutamiento correcto basándose en umbrales de confianza matemática (*Confidence Thresholding*), permitiendo una auto-corrección algorítmica sin intervención humana o, en su defecto, levantando una alerta para revisión.

## 2. Análisis de datos planteado y utilidad esperada
El análisis exploratorio y la investigación de los datos han estado orientados a asegurar la calidad de la predicción y mitigar sesgos semánticos:
*   **Preguntas a responder:** ¿Posee el texto libre redactado por un usuario suficiente riqueza semántica para predecir una categorización ITIL estricta (alta dimensionalidad de clases combinadas)?
*   **Análisis comparativos:** He ejecutado un Test A/B para comprobar la viabilidad de utilizar traducción automática. He comparado el rendimiento de un modelo nativo en inglés frente a uno con datos traducidos sintéticamente al español (Helsinki-NLP) para estudiar la degradación semántica.
*   **Equilibrio de clases:** Al tratarse de un problema de clasificación con una alta cardinalidad de variables objetivo combinadas, el análisis ha estado centrado en medir y mitigar el desbalanceo extremo (clases mayoritarias vs. colas raras).
*   **Utilidad para el MVP:** Este análisis justifica la necesidad arquitectónica de aplicar técnicas de sobremuestreo (SMOTE) para evitar que el algoritmo ignore a las minorías, y apuntala la decisión técnica de utilizar el corpus nativo en inglés para la API de producción.

## 3. Tipo de modelos que se van a plantear
El problema se enmarca en una tarea de **Clasificación Multiclase NLP**. Dado que los textos se han vectorizado matemáticamente (TF-IDF) generando un espacio de altísima dimensionalidad (~10.000 variables dispersas), he descartado algoritmos puramente espaciales (como KNN) para ejecutar un torneo empírico (*Bake-Off*) entre ensamblados basados en árboles y modelos probabilísticos.

| Alternativa | Tipo | Por qué se plantea | Limitación principal empírica |
| :--- | :--- | :--- | :--- |
| **Baseline** | Regresión Logística Multinomial | Proporciona una referencia estadística sólida, rápida y muy robusta frente a la alta dimensionalidad dispersa de TF-IDF. | Estrictamente lineal; incapaz de capturar la complejidad semántica no lineal entre palabras dependientes. |
| **Candidato 1** | Naive Bayes (Multinomial) | Es el estándar probabilístico histórico para clasificación de textos. Funciona excelente como *baseline* secundario. | Asume independencia total entre las palabras (consecuencia de su diseño "Naive"), lo cual es irreal en el lenguaje humano. |
| **Candidato 2** | Random Forest | Algoritmo de ensamble paralelo espacialmente muy flexible. Su arquitectura de *Bagging* mitiga la varianza y el sobreajuste. | Alto consumo de memoria RAM al manejar matrices dispersas gigantescas en paralelo. |
| **Candidato 3** | XGBoost (Gradient Boosting) | Modelo avanzado secuencial (crecimiento por niveles). Penaliza los errores iterativamente, ideal para mejorar el rendimiento en clases minoritarias. | Coste computacional masivo (penalización crítica en tiempo de entrenamiento cruzado) y alto riesgo de sobreajuste. |
| **Candidato 4** | LightGBM | Variante de *Boosting* extremadamente rápida por su crecimiento en profundidad por hojas (*leaf-wise*). | Probada empíricamente su incompatibilidad arquitectónica: colapsa (F1 cercano a 0) ante matrices TF-IDF dispersas. |
| **Candidato 5** | Máquinas de Vectores de Soporte (SVC) / Árboles de decisión simples | Familia probada por su capacidad de segmentar hiperplanos en alta dimensionalidad (SVC) y alta interpretabilidad (Árboles). | Inviabilidad de escalado a grandes volúmenes tras inyectar datos sintéticos (SMOTE). |

## 4. Datos de entrada del análisis y los modelos
La entrada al modelo predictivo consumirá exclusivamente la información generada en la Capa *Processed* (Silver) y *Features* (Gold).

*   **Nombre del dataset:** `en_X_train_tfidf.npz` (Matriz matemática de características) y `df_final_silver.parquet` (Metadatos).
*   **Granularidad:** Una fila representa exactamente un ticket de soporte individual.
*   **Clave identificadora:** `ticket_id` (Generada sintéticamente de forma secuencial).
*   **Variables de entrada principales:** `full_text_clean` (Concatenación de Asunto y Cuerpo del correo, vectorizada mediante TF-IDF).
*   **Variables descartadas por riesgo:** He eliminado por completo la variable `answer` (respuesta del técnico). Su inclusión habría generado una **fuga de datos (Data Leakage)** catastrófica, ya que en el entorno real de producción, el ticket debe ser auditado o enrutado *antes* de que un técnico lo responda.

| Entrada | Descripción | Granularidad / tipo | Uso en el análisis o modelo |
| :--- | :--- | :--- | :--- |
| `full_text_clean` | Texto limpio, tokenizado y lematizado. | Texto (transformado a matriz Numérica TF-IDF) | Variable independiente (Predictora fundamental). |
| `Tripleta` | Concatenación de `queue`, `type` y `priority`. | Categórica (Alta dimensionalidad) | Variable dependiente (Objetivo / Target). |

## 5. Datos de salida y forma de consumo
El modelo no se limitará a devolver una predicción categórica estática, sino que generará una distribución de probabilidades paramétricas para alimentar un motor de reglas de negocio. La salida se consumirá a través de un microservicio REST (API mediante FastAPI).

*   **Cómo utilizará el usuario la salida:** El sistema CRM consultará la API inyectando el texto original en formato JSON. Si la predicción algorítmica contradice la clasificación humana inicial con una probabilidad $\ge$ 85%, el sistema aplicará un `AUTO_CORRECT`. Si la probabilidad oscila entre 60% y 85%, se devolverá un código `REVIEW` para levantar un *flag* de auditoría humana en la interfaz del coordinador (Nivel 2).

| Campo de salida | Descripción | Tipo | Uso posterior |
| :--- | :--- | :--- | :--- |
| `ticket_id` | Identificador del ticket auditado. | string | Trazabilidad algorítmica y unión con el CRM. |
| `tripleta_predicha` | La clase ganadora predicha por la IA. | string | Contraste analítico contra el valor humano original. |
| `probabilidad_max` | Nivel de confianza matemática del modelo (0.0 a 1.0). | float | Disparador de las reglas de auto-enrutamiento. |
| `accion_sugerida` | Decisión de negocio inferida. | string | Integración directa (AUTO_CORRECT, REVIEW, OK). |

## 6. Estrategia para diseñar y seleccionar el modelo
El proceso de selección del ganador del MVP no se ha basado únicamente en obtener la métrica más alta aislada, sino en el balance entre precisión, inmunidad al sobreajuste y tiempos de inferencia:
1.  **Vectorización Limpia:** Transformación del corpus textual a matriz TF-IDF restringida a 10.000 dimensiones máximas.
2.  **Modelado Baseline:** Entrenamiento de la Regresión Logística y Naive Bayes.
3.  **Bake-Off Algorítmico:** Evaluación empírica de los ensamblados arbóreos (Random Forest, XGBoost, LightGBM) frente al Baseline.
4.  **Ajuste de Hiperparámetros (Coarse-to-Fine Tuning):** Selección del ganador indiscutible (Random Forest) y optimización de su arquitectura interna mediante búsquedas algorítmicas iterativas (`RandomizedSearchCV` seguido de `GridSearchCV`).
5.  **Criterio de Decisión Final:** El modelo final seleccionado ha sido aquel capaz de maximizar el F1-Macro sin mostrar signos de colapso en la validación cruzada. Se ha priorizado el Random Forest frente al XGBoost, no solo por métrica pura, sino por su menor coste computacional, lo cual es vital para el despliegue del microservicio.

## 7. Estrategia de validación y evaluación
Al enfrentarme a un problema de clasificación multiclase masiva y altamente desbalanceada, la evaluación exige un diseño matemático muy estricto para evitar ilusiones estadísticas.

| Elemento | Decisión prevista | Justificación |
| :--- | :--- | :--- |
| **Separación de datos** | *Train/Test Split* estratificado (80/20) + K-Fold CV (k=3) en la fase de validación. | La estratificación garantiza forzosamente que las clases minoritarias estén representadas de forma equitativa tanto en Train como en Test. |
| **Métrica principal** | **F1-Macro** | La métrica de exactitud (*Accuracy*) es engañosa en matrices desbalanceadas. El F1-Macro otorga idéntico peso a una clase de 5.000 tickets que a una de 10 tickets, penalizando fuertemente a los modelos sesgados hacia la mayoría. |
| **Prevención Leakage** | `ImbPipeline` (Flujo dinámico) | El sobremuestreo sintético (SMOTE) se inyecta de forma encapsulada *dinámicamente dentro de cada pliegue* de la validación cruzada. Realizar SMOTE globalmente antes del CV provocaría un sangrado de datos sintéticos hacia el conjunto de validación, falseando las métricas de éxito al alza. |
| **Criterio de aceptación** | Superar empíricamente a la Regresión Logística y consolidar un F1-Macro competitivo frente a la alta dimensionalidad. | Cualquier valor sólido que logre superar la barrera del F1-Macro >0.60 en un entorno de alta cardinalidad garantiza la viabilidad del MVP de cara al umbral restrictivo de la API. |

## 8. Riesgos y alternativas
*   **¿La variable objetivo está disponible y representa el fenómeno?** Sí, el histórico ya contiene las tripletas cerradas (`queue`, `type`, `priority`) que simulan fielmente el árbol de decisiones de un CRM real de BPO.
*   **Riesgo de Data Leakage:** Controlado de forma implacable al purgar la columna `answer` (respuesta post-resolución) y utilizar flujos dinámicos (`Pipeline`) en la validación cruzada para encapsular el SMOTE.
*   **Incertidumbre principal (Detectada y Asumida):** La "Hambruna de datos" provocada por la fragmentación espacial del *K-Fold*. Las clases con menos de 5 tickets sufren severamente para ser sobremuestreadas matemáticamente por algoritmos de vecinos cercanos. Esto hunde el F1-Macro durante la validación, exigiendo utilizar pesos de clase (`class_weight='balanced'`) para forzar la penalización matemática.
*   **Alternativa de contingencia:** Si durante la optimización final el modelo hubiera colapsado frente a la complejidad combinatoria de la tripleta completa, el plan B de contingencia consistía en desnormalizar la variable objetivo: se eliminarían las ramificaciones `type` y `priority`, entrenando al clasificador para predecir exclusivamente la variable `queue` (reduciendo la cardinalidad a un Nivel 1 manejable de 5 clases globales). La robustez empírica del algoritmo seleccionado ha hecho innecesario activar esta degradación.
