# Hoja de Ruta: Fase Final (Tuning y Exportación)

Tras completar el Test A/B y proclamar a la arquitectura **Nativa en Inglés + Random Forest + SMOTE** como la campeona absoluta de la investigación, el Trabajo de Fin de Máster entra en su fase definitiva de optimización de Machine Learning.

## Cuaderno 06: Hyperparameter Tuning (El Exprimido Final)

El objetivo de este cuaderno es tomar el modelo ganador (Random Forest) y, en lugar de usar su configuración por defecto, buscar matemáticamente su "punto dulce" para elevar el F1-Macro por encima del `0.68` actual.

### Pasos a ejecutar:
1. **Pipeline Limpio:** Replicaremos la carga del dataset en inglés, el NLP con spaCy y la vectorización TF-IDF.
2. **K-Fold Cross Validation:** Se descartará el split clásico de validación. Aplicaremos una Validación Cruzada de K iteraciones (K-Fold) sobre el 80% de los datos de Train para evitar el sesgo de partición y maximizar el uso de los tickets raros.
3. **GridSearchCV:** Someteremos al Random Forest a una búsqueda en cuadrícula probando múltiples combinaciones de hiperparámetros:
   * `n_estimators`: Número de árboles (ej. 100, 300, 500).
   * `max_depth`: Profundidad máxima para prevenir el sobreajuste (*overfitting*).
   * `min_samples_split`: Tolerancia de corte de las ramas.
   * `class_weight`: Técnicas internas de balanceo como alternativa o complemento al SMOTE.
4. **Evaluación Definitiva:** El mejor modelo resultante de la cuadrícula matemática se examinará por última y única vez contra el 20% de Test (datos nunca vistos) para obtener la métrica oficial y final de la tesis.

## Fase de Exportación y Despliegue Simulado (MLOps)

Una vez confirmada la métrica final, el modelo entrenado y los objetos de vectorización (TF-IDF y spaCy) se congelarán en disco duro utilizando serialización binaria (`joblib` / `pickle`). Esto demostrará la viabilidad del modelo para ser consumido en tiempo real por una futura API REST dentro del BPO, cerrando el ciclo completo del desarrollo del TFM.
