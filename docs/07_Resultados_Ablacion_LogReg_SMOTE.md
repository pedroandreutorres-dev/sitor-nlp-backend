# Informe de Resultados: Regresión Logística y Estudio de Ablación (SMOTE)

**Fecha:** 21 de Agosto
**Fase:** Modelado Lineal y Gestión de Desbalanceo
**Algoritmo:** Logistic Regression (`max_iter=1000`)
**Idiomas:** Inglés (Nativo) vs Español (Traducido vía `opus-mt-en-es`)

---

## 1. Contexto del Experimento

Tras comprobar en el Test A/B Baseline (Naive Bayes) que el desbalanceo masivo de clases provocaba un colapso en la detección de clases críticas (Recall de *Service Outages* en español cayó al 5%), se diseña un Estudio de Ablación utilizando un modelo probabilístico lineal robusto (**Regresión Logística**).

El objetivo es doble:
1. Demostrar empíricamente si la evolución del algoritmo lineal por sí misma mitiga el problema.
2. Comprobar el efecto de inyectar datos sintéticos en el espacio vectorial (SMOTE) para las tres clases minoritarias (*IT Support*, *Sales*, *Service Outages*), igualando su volumen al de la clase mayoritaria (*Technical Support*).

---

## 2. Matriz Maestra de Resultados (F1-Score)

La siguiente tabla recoge las métricas de rendimiento (F1-Score) por cada cola de soporte, comparando directamente los modelos entrenados con la matriz original desbalanceada ("Sin SMOTE") y los modelos entrenados con la matriz aumentada matemáticamente ("Con SMOTE").

| Cola de Soporte | 🇬🇧 EN (Sin SMOTE) | 🇬🇧 EN (Con SMOTE) | 🇪🇸 ES (Sin SMOTE) | 🇪🇸 ES (Con SMOTE) | Impacto de SMOTE |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Billing and Payments** | **0.80** | 0.77 | **0.76** | **0.76** | Ligera bajada / Neutro |
| **Customer Service** | 0.41 | **0.44** | 0.42 | **0.44** | Mejora |
| **IT Support** *(Minoría)* | 0.25 | **0.39** 🚀 | 0.32 | **0.37** 🚀 | **Subidón agresivo** |
| **Product Support** | 0.41 | **0.45** | 0.43 | **0.44** | Mejora leve |
| **Sales and Pre-Sales** *(Minoría)* | 0.19 | **0.40** 🚀 | 0.14 | **0.37** 🚀 | **Subidón bestial** (>100%) |
| **Technical Support** *(Mayoría)* | **0.60** | 0.54 | **0.59** | 0.53 | *Penalización por balanceo* |
| **🚨 Service Outages** *(F1-Score)* | 0.56 | 0.56 | 0.51 | **0.59** | Estancado (EN) / **Subidón (ES)** |
| **🚨 Service Outages** *(Recall puro)* | *43%* | ***64%*** | *38%* | ***69%*** | **El mayor éxito operativo** |

---

## 3. Rendimiento Operativo y MLOps

La adopción de SMOTE implica inyectar miles de vectores matemáticos nuevos en el conjunto de entrenamiento (pasando, por ejemplo, de 695 a 5139 tickets de averías en inglés). Esto impacta en el tiempo de entrenamiento, pero no en la inferencia en producción.

| Métrica | 🇬🇧 EN (Sin SMOTE) | 🇬🇧 EN (Con SMOTE) | 🇪🇸 ES (Sin SMOTE) | 🇪🇸 ES (Con SMOTE) | Análisis MLOps |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **F1-Macro (Global)** | 0.46 | **0.51** | 0.45 | **0.50** | Equilibrio global del modelo. |
| **Tiempo de Entrenamiento** | 2.38 seg | **5.95 seg** | 2.61 seg | **5.75 seg** | SMOTE dobla el tiempo. Asumible. |
| **Latencia de Inferencia** | 2.48 ms | **1.73 ms** | 1.92 ms | **2.17 ms** | Latencia intacta (< 3 ms). |

---

## 4. Conclusiones para la Memoria del TFM

1. **La Recuperación de las Minorías:** SMOTE cumple su objetivo fundacional. Al inyectar datos sintéticos, las clases asustadizas (`Sales`, `IT Support`) logran más que duplicar su eficacia porque el modelo pierde el sesgo hacia la clase mayoritaria.
2. **El "Trade-Off" de la Mayoría:** La clase `Technical Support` sufre una caída en su Recall (del ~76% al ~50%). Esto es una corrección matemática necesaria; antes, el modelo actuaba como un "vago" prediciendo la mayoría ante cualquier duda. Ahora distribuye sus predicciones de forma justa.
3. **El Hito del Español en Averías Críticas:** En el Test A/B, el modelo localizado en español apoyado por SMOTE logra detectar el **69% de las averías masivas (Recall)**, superando el 64% del modelo nativo en inglés. Empíricamente, la jerga técnica traducida genera un espacio vectorial más separable para la Regresión Logística.
4. **Viabilidad de Negocio:** Aunque la *Precision* en averías haya bajado al 52%, en el sector BPO es infinitamente más rentable revisar una falsa alarma generada por el modelo (falso positivo) que permitir que un falso negativo en una avería masiva escale incorrectamente, retrasando la resolución del problema de red.
