# Informe de Resultados: LightGBM y Elección del Campeón Algorítmico

**Fecha:** 24 de Agosto
**Fase:** Modelos No Lineales (Gradient Boosting por Hojas)
**Algoritmo:** LightGBM (`n_estimators=100`, `class_weight='balanced'`)
**Metodología:** SMOTE vs Pesos de Clase

---

## 1. Contexto del Experimento Final

Tras el colapso de XGBoost debido a la alta dimensionalidad de las matrices NLP (10.000 características dispersas), se evaluó LightGBM (Microsoft). Su algoritmo *leaf-wise* promete mayor eficiencia de memoria y rapidez frente al crecimiento simétrico (*level-wise*) de XGBoost.

---

## 2. Resultados de LightGBM (Estudio de Ablación)

| Configuración LightGBM | F1-Macro Global (EN / ES) | F1 Averías Críticas (EN / ES) | Tiempo de Entrenamiento | Latencia Inferencia |
| :--- | :---: | :---: | :---: | :---: |
| **Pesos de Clase** (Sin SMOTE) | 0.56 / 0.52 | 0.62 / 0.59 | ~36 segundos | ~57 ms |
| **Inyección Sintética** (SMOTE) | 0.56 / 0.54 | 0.65 / 0.60 | ~101 segundos | ~52 ms |

### Comparativa directa con el líder (Random Forest)
*   **F1-Macro Máximo:** Random Forest (0.68) vs LightGBM (0.56).
*   **T. Entrenamiento:** Random Forest (~15s) vs LightGBM (~101s).

---

## 3. Conclusiones y Elección Final

1.  **Victoria de la Arquitectura de Microsoft sobre XGBoost:** LightGBM logró un incremento sustancial en la velocidad de entrenamiento frente a XGBoost (de 267 segundos bajó a 101 segundos con SMOTE). 
2.  **Fracaso del Boosting en NLP Disperso:** A pesar de las optimizaciones, LightGBM fracasa a la hora de encontrar patrones no lineales puros en océanos de ceros. Al igual que XGBoost, su F1-Macro queda estancado en el rango del 0.50.
3.  **Veredicto Definitivo:** Se declara terminada la fase de *Broad Sweep* (Barrido Algorítmico). La técnica de ensamblado en paralelo (*Bagging*) a través de **Random Forest**, combinada con **SMOTE**, ha demostrado una superioridad absoluta y apabullante en Precisión y Retorno de Inversión Computacional.

**El modelo Random Forest avanza como finalista único a la fase de Hyperparameter Tuning (GridSearchCV).**
