# Evaluación y Resultados (Dataset Inglés Nativo)

## 1. Cambio Arquitectónico: La Tripleta
Tras validar los datos crudos en el **Notebook 01**, decidimos apostar por el objetivo original del TFM: enrutar simultáneamente los 3 niveles del ticket (`queue`, `type`, `priority`). En el **Notebook 02**, estas variables se fusionaron en una única variable objetivo (La Tripleta), generando un problema de clasificación extrema con **84 clases únicas** altamente desbalanceadas.
Se aplicó un *split* estratificado estándar (80% Train, 20% Test) para preservar los porcentajes de la realidad empresarial en el Test.

## 2. Procesamiento de Lenguaje Natural (NLP)
En el **Notebook 03**, se limpiaron las variables predictivas (`subject` + `body`) utilizando **spaCy** (`en_core_web_sm`). El texto fue lematizado, tokenizado y limpiado de *stop words*.
Posteriormente, se vectorizó utilizando **TF-IDF**, estableciendo un límite superior de 10.000 dimensiones. El vocabulario real resultante fue de 4.717 palabras únicas, demostrando la alta especificidad técnica del dominio IT de la empresa.

## 3. Torneo de Algoritmos (Bake-Off) y SMOTE
En el **Notebook 04**, se diseñó un torneo empírico para evaluar qué familia algorítmica era matemáticamente más capaz de lidiar con un ecosistema de alta dimensionalidad (4.717 features) y escasez de datos en clases raras (sparsity).

Se evaluaron 6 algoritmos tanto sin balanceo como con balanceo matemático plano (**SMOTE**). El SMOTE demostró ser crítico, multiplicando el conjunto de entrenamiento de 18.493 a 152.376 tickets, obligando a los algoritmos a prestar atención a las clases minoritarias.

### Conclusiones y Veredicto Científico
1. **Fracaso del Boosting (LightGBM y XGBoost):** Se demostró empíricamente que los modelos basados en árboles que crecen por hojas (*leaf-wise*) como LightGBM colapsan ante matrices TF-IDF dispersas (F1-Macro: 0.0013). XGBoost (crecimiento por niveles) sobrevivió, pero su coste computacional (24 minutos de entrenamiento) lo hace inviable en producción frente a otras alternativas.
2. **Resurgir de Modelos Lineales:** SMOTE salvó a Naive Bayes y Regresión Logística del fracaso absoluto, multiplicando su F1-Macro hasta por 15 veces, aunque sin llegar a la excelencia.
3. **El Campeón Absoluto (Random Forest + SMOTE):** Random Forest demostró que su arquitectura *Bagging* (creación de árboles independientes y paralelos sobre subconjuntos aleatorios de features) es perfecta para este problema. Con el apoyo de SMOTE, elevó su Recall masivamente y logró el pico del torneo con un **F1-Macro de 0.6818** en tan solo 2 minutos de entrenamiento.

**Ganador Oficial de la Fase Inglesa:** Random Forest (Con SMOTE).
