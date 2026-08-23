# Informe de Resultados: Fracaso de XGBoost y Cost-Sensitive Learning

**Fecha:** 23 de Agosto
**Fase:** Modelos No Lineales (Gradient Boosting Secuencial)
**Algoritmo:** XGBoost (`n_estimators=100`, `max_depth=6`)
**Metodología de Ablación:** SMOTE vs Pesos de Clase (Cost-Sensitive Learning)

---

## 1. Contexto del Experimento

Tras el éxito del ensamblado en paralelo (Random Forest, F1 0.68), se plantea la hipótesis de que un ensamblado secuencial (XGBoost) basado en el descenso de gradiente podría exprimir aún más la métrica predictiva.
Adicionalmente, se testea si alterar la función de pérdida del algoritmo con **Pesos de Clase Estadísticos** (penalizando los errores en las clases minoritarias) es computacional y operativamente superior a la inyección masiva de vectores sintéticos (SMOTE).

---

## 2. Resultados del Estudio de Ablación (XGBoost)

Los resultados empíricos rechazan rotundamente la viabilidad de XGBoost para este espacio vectorial en su configuración estándar.

| Configuración XGBoost | F1-Macro Global (EN / ES) | F1 Averías Críticas (EN / ES) | Tiempo de Entrenamiento | Latencia de Inferencia |
| :--- | :---: | :---: | :---: | :---: |
| **Pesos de Clase** (Sin SMOTE) | 0.52 / 0.50 | 0.54 / 0.58 | ~97 segundos | ~95 ms |
| **Inyección Sintética** (SMOTE) | 0.51 / 0.49 | 0.61 / 0.59 | ~250 segundos | ~82 ms |
| *Referencia: Random Forest + SMOTE* | *0.68 / 0.65* | *0.72 / 0.70* | *~15 segundos* | *~65 ms* |

---

## 3. Diagnóstico Científico del Fracaso

La evaluación de XGBoost arroja tres conclusiones negativas críticas para el entorno productivo:

1.  **Regresión Predictiva:** XGBoost devuelve los marcadores predictivos (F1 ~0.50) al nivel de una simple Regresión Logística, destruyendo todo el avance logrado por Random Forest (F1 ~0.68). 
2.  **Maldición de la Dimensionalidad:** El modelo fracasa debido a la estructura ultra-dispersa de la matriz TF-IDF (10.000 dimensiones, 99% ceros). La arquitectura de XGBoost por defecto (con un límite restrictivo de `max_depth=6`) provoca que los árboles "enanos" sean incapaces de capturar las combinaciones léxicas no lineales que Random Forest sí detecta gracias a su crecimiento sin restricciones.
3.  **Inviabilidad MLOps:** XGBoost demostró ser un algoritmo exponencialmente lento. Requirió más de **4 minutos** para procesar la matriz SMOTE, frente a los 15 segundos de Random Forest. Escalar este modelo a una fase de *Hyperparameter Tuning* (GridSearchCV) exigiría horas de computación sin garantías de retorno de inversión (ROI).

## 4. Veredicto

**XGBoost queda oficialmente descartado** de la arquitectura final del proyecto. SMOTE se consolida de nuevo como la técnica más robusta frente al uso de Pesos de Clase, los cuales indujeron severos problemas de Falsos Positivos al volver al algoritmo excesivamente reactivo ante las clases minoritarias.
