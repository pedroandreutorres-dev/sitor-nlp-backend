# Reporte Forense: Test A/B de Idioma (Modelos Baseline)

## Contexto del Experimento
Este documento consolida los resultados empíricos obtenidos tras entrenar el **Baseline de Clasificación** (algoritmo Multinomial Naive Bayes con representación TF-IDF a 10.000 dimensiones) de forma paralela en dos conjuntos de datos:
* **Conjunto Nativo (Inglés):** Procesado en Notebook 02.
* **Conjunto Traducido (Español):** Procesado en Notebook 04, generado a partir de una traducción automática de Hugging Face.

El objetivo de este Test A/B es medir el impacto del "ruido de traducción" en la precisión del algoritmo estadístico, justificando así las decisiones posteriores de arquitectura en el PFM.

---

## 1. Cuadro Comparativo Global (Métricas MLOps y Desempeño)

| Métrica MLOps | 🇬🇧 Inglés (Nativo) | 🇪🇸 Español (Traducido) | Diferencia / Impacto Operativo |
| :--- | :---: | :---: | :--- |
| **Tiempo de Entrenamiento** | ~0.044 seg | **0.063 seg** | +43% tiempo |
| **Latencia de Inferencia** | ~2.40 ms | **4.34 ms** | +80% latencia |
| **F1-Macro (Nota Global)** | **0.3347** | 0.3088 | **-7.7% rendimiento** |
| **F1 Averías Críticas** | **0.2775** | 0.0870 | **-68% rendimiento** (Desastre total) |

**Conclusión Operativa:** La densidad del texto en español incrementa significativamente la latencia de inferencia (+80%). Aunque 4 ms es asumible para una API REST, demuestra que los idiomas más prolijos exigen mayor carga computacional.

---

## 2. Radiografía de Clases (Precisión y Exhaustividad)

Desglose analítico del rendimiento por clase predictiva (Queue):

| Cola de Soporte (Queue) | Precision (En) | Precision (Es) | Recall (En) | Recall (Es) | F1 (En) | F1 (Es) | Impacto de Traducción |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Billing and Payments** | 0.93 | 0.93 | 0.65 | 0.62 | 0.76 | 0.74 | Ligeramente Peor |
| **Customer Service** | 0.31 | 0.31 | 0.45 | 0.45 | 0.37 | 0.37 | **Idéntico** |
| **IT Support** | 0.50 | **0.76** | 0.03 | 0.05 | 0.06 | **0.09** | **Mejoró (Falso Positivo)** |
| **Product Support** | 0.42 | 0.44 | 0.24 | 0.25 | 0.31 | 0.32 | Ligeramente Mejor |
| **Sales and Pre-Sales** | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | Cero absoluto en ambos |
| **Technical Support** | 0.44 | 0.44 | 0.77 | 0.78 | 0.56 | 0.56 | **Idéntico** |
| **🚨 Service Outages** | **1.00** | 0.88 | **0.16** | **0.05** | **0.28** | **0.09** | **Colapso Estadístico** |

## 3. Diagnóstico Técnico de Negocio

El Test A/B dictamina un fallo sistémico en la traslación del léxico técnico:

1. **Fragmentación de Vocabulario:** La traducción automática generó múltiples sinónimos (ej. *outage* se tradujo como *corte, caída, avería, interrupción*), lo que diluyó la fuerza estadística de las palabras clave, cegando al modelo Naive Bayes ante las averías masivas (Recall cayó al 0.05).
2. **Justificación de Siguientes Fases:** Este resultado actúa como prueba empírica irrefutable para la defensa del proyecto. Demuestra que los algoritmos estadísticos básicos (MNB) no son aptos para la complejidad semántica de entornos multi-idioma B2B. Justifica económicamente la necesidad de invertir en sobremuestreo sintético (SMOTE) y ensamblados no lineales (XGBoost/Random Forest) capaces de manejar el "ruido" de la traducción.
