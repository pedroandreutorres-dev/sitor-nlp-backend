# Informe de Resultados: Random Forest (Bagging) y Desbalanceo

**Fecha:** 23 de Agosto
**Fase:** Modelos No Lineales (Ensamblado basado en Árboles)
**Algoritmo:** Random Forest (`n_estimators=100`)
**Idiomas:** Inglés (Nativo) vs Español (Traducido vía `opus-mt-en-es`)

---

## 1. Contexto del Experimento

Tras el techo de cristal encontrado en la Regresión Logística (F1-Macro de 0.50), el proyecto evoluciona hacia modelos no lineales. **Random Forest** utiliza la técnica de *Bagging*, construyendo 100 árboles de decisión independientes que votan entre sí. 

El objetivo de este experimento es verificar si la complejidad jerárquica de los árboles es capaz de:
1. Superar el rendimiento base de los algoritmos geométricos lineales.
2. Manejar el desbalanceo masivo de clases (Estudio de Ablación con/sin SMOTE).

---

## 2. Matriz Comparativa de Rendimiento

El siguiente cuadro detalla el impacto cruzado entre el cambio de algoritmo y la técnica de balanceo de datos (SMOTE).

| Hito Algorítmico | 🇬🇧 F1-Macro Global (EN) | 🇬🇧 F1 Averías (EN) | 🇪🇸 F1-Macro Global (ES) | 🇪🇸 F1 Averías (ES) |
| :--- | :---: | :---: | :---: | :---: |
| **Modelo Lineal Curado** (LogReg + SMOTE) | 0.50 | 0.56 | 0.50 | 0.59 |
| **Árboles Ciegos** (Random Forest Sin SMOTE) | 0.61 | 0.68 | 0.58 | 0.61 |
| **Árboles Curados** (Random Forest + SMOTE) | **0.68** | **0.72** | **0.65** | **0.70** |

---

## 3. Impacto Operativo (MLOps)

El salto de complejidad algorítmica y el aumento del tamaño de la matriz (vía SMOTE) tiene un coste directo en hardware y latencia:

*   **Tiempos de Entrenamiento:** Mientras que la Regresión Logística entrenaba en ~5 segundos, Random Forest con SMOTE exige **~15 segundos**. Es un aumento del 300%, justificable por el salto masivo en F1.
*   **Latencia de Inferencia:** El tiempo de predicción en producción (el milisegundo en el que el modelo procesa un ticket entrante) pasa de **~2 ms a ~65 ms**. Sigue estando muy por debajo de los SLAs estándar de la industria (< 200 ms).

---

## 4. Conclusiones para la Memoria

1. **La Superioridad del Ensamblado:** El modelo Random Forest *sin* SMOTE destroza al modelo lineal *con* SMOTE. Esto demuestra de manera concluyente que la separación lineal es insuficiente para el procesamiento de lenguaje natural en este dataset; el texto exige modelos que entiendan reglas complejas.
2. **El Síndrome de la "Cobardía Perfeccionista":** Analizando el reporte de Random Forest sin SMOTE, se observó que la clase `Sales` lograba un 100% de Precisión pero un ~25% de Recall. Los árboles, sesgados por la clase mayoritaria, prefieren no predecir las clases minoritarias a menos que tengan certeza absoluta.
3. **SMOTE cura la ceguera:** Al inyectar la matriz sintética, el Recall de averías críticas se disparó (del 55% al 68% en inglés), sacrificando precisión pero optimizando el modelo para el caso de uso real de la operadora (evitar falsos negativos).
4. **Inglés vs Español:** A diferencia del modelo lineal, donde la traducción al español favoreció la detección de averías, en los árboles el inglés nativo es superior (0.72 vs 0.70). Los árboles se nutren de la alta varianza léxica del idioma nativo, la cual se aplana ligeramente durante la traducción automática.
