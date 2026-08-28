# Hoja de Ruta: Optimización y Despliegue a Producción (MLOps)

Tras evaluar el rendimiento estructural de los algoritmos y confirmar que el procesamiento nativo en inglés con Random Forest y balanceo sintético (SMOTE) presenta la mayor capacidad de generalización, la investigación avanza hacia sus dos fases finales: la optimización matemática del modelo y el diseño de la arquitectura de producción.

## 1. Optimización de Hiperparámetros (Fine-Tuning)

El objetivo de esta fase es abandonar los parámetros por defecto de Random Forest y explorar el espacio dimensional de configuración para maximizar la métrica F1-Macro, garantizando la rigurosidad estadística en la evaluación.

### Metodología de Optimización:
* **Búsqueda Iterativa Controlada:** Se sustituye la búsqueda exhaustiva (`GridSearchCV`) por `RandomizedSearchCV`, limitando el muestreo aleatorio a 60 configuraciones para asegurar la viabilidad del cómputo sin sacrificar el alcance analítico.
* **Validación Cruzada (K-Fold=3):** Se descarta la partición estática convencional. El conjunto de datos de entrenamiento se evalúa mediante rotación de tres pliegues para evitar sobreajustes locales.
* **Pipeline de Prevención de Fuga de Datos:** Se implementa la clase `Pipeline` de la librería `imblearn` para asegurar que el algoritmo de generación sintética (SMOTE) se ejecute de forma dinámica y exclusiva sobre los fragmentos de entrenamiento de cada iteración del K-Fold. Esta decisión arquitectónica corrige los problemas de Data Leakage, garantizando que el conjunto de evaluación permanezca inalterado durante la optimización cruzada.

## 2. Serialización y Arquitectura MLOps (Despliegue)

Una vez identificada la configuración matemática óptima, el modelo definitivo se entrenará utilizando el 100% de la matriz disponible. A partir de ese punto, el proyecto transiciona hacia la ingeniería de software para integrarse en la operativa de negocio del CRM.

### Fases de Implementación en Producción:

1. **Serialización del Pipeline Analítico:**
   Se procederá a la congelación en disco (mediante la librería `joblib` o `pickle`) de los tres artefactos indispensables para la inferencia futura:
   * El modelo predictivo final (Random Forest).
   * El vectorizador semántico (TF-IDF), responsable de mapear las 10.000 dimensiones del vocabulario técnico.
   * El codificador de etiquetas (`LabelEncoder`), encargado de transcodificar la salida binaria del modelo en la nomenclatura categórica original de la Tripleta.

2. **Ingeniería del Motor de Inferencia (Umbrales de Confianza):**
   El código de producción no utilizará la función de clasificación estándar, sino la estimación probabilística (`predict_proba`). Esto permite establecer una lógica de automatización basada en niveles de confianza algorítmica:
   * **Recepción de Datos:** El sistema recibirá listados de tickets de soporte en formato JSON a través de llamadas API.
   * **Evaluación Probabilística:** El modelo NLP limpiará y vectorizará el texto del ticket en milisegundos, devolviendo un vector de probabilidades para las 84 posibles tripletas.
   * **Lógica de Triaje y Enrutamiento Automático:** Se comparará la tripleta predicha por el modelo frente a la tripleta asignada originalmente en el JSON:
     * **Validación:** Si coinciden, el registro se marca como correcto sin requerir acción adicional.
     * **Auto-Corrección (Confianza $\ge$ 85%):** Si difieren y el modelo posee un umbral de certeza superior al 85%, el sistema aplicará auto-enrutamiento, sobreescribiendo el JSON sin intervención manual, generando un ahorro directo de recursos en el nivel de soporte N1.
     * **Revisión Humana (Confianza entre 60% y 85%):** Si difieren y la confianza se encuentra en este intervalo, el sistema no forzará la sobreescritura, sino que etiquetará el ticket para revisión humana, derivándolo a un auditor de calidad operativa.
     * **Rechazo/Inseguridad (Confianza < 60%):** En escenarios de alta ambigüedad semántica, el algoritmo se abstiene de actuar y eleva el ticket a revisión humana directa.

3. **Exposición como Servicio (API REST):**
   La lógica descrita se encapsulará utilizando el framework **FastAPI**, habilitando un *endpoint* de inferencia de baja latencia capaz de absorber la demanda de tickets en tiempo real. 

Esta arquitectura certifica que la investigación no se limita al diseño teórico de modelos estadísticos, sino que culmina en un producto de Inteligencia Artificial plenamente operativo y orientado al retorno de inversión (ROI) del negocio.
