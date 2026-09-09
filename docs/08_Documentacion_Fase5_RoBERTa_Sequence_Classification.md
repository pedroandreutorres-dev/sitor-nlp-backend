# Documentación Fase 5: Estabilización Deep Learning y Hold-Out Maestro (RoBERTa)

## 1. Pivotando a Contingencia (roberta-base)
Tras evaluar las alternativas descritas en la auditoría técnica, se escaló la arquitectura hacia el "caballo de batalla industrial": **RoBERTa-base (125M de parámetros)**. La robustez de sus gradientes era un requisito innegociable tras los colapsos de *SetFit* frente al ruido de un *dataset* de alta cardinalidad (102 clases).

El enfoque abandonó el *Few-Shot Learning* y se consolidó como **Sequence Classification Nativo**, orquestando un entrenamiento *Full-Shot* apoyado sobre aceleradores gráficos pesados (NVIDIA T4 y A100).

## 2. El Cuello de Botella Geométrico y la Intervención Taxonómica
El primer ciclo de validación *K-Fold* arrojó un diagnóstico crítico de "Asfixia Matemática":
- **Diagnóstico:** El desbalance volumétrico era insostenible. La clase mayoritaria contaba con 2132 tickets, mientras que la minoritaria apenas registraba 24. Esto destruía la capacidad del optimizador de trazar fronteras de decisión estables.
- **Intervención Purgativa:** Se ejecutó un mapeo taxonómico de emergencia. Se agruparon 13 colas residuales (identificadas como basura operativa de derivación cruzada) bajo una única macro-etiqueta: `Derivacion_Manual_Minoritaria`. El espacio de negocio pasó de 102 a **90 clases**.

## 3. Amortiguación Logarítmica (Square Root Class Weights)
El modelo colapsaba al inyectarle una función de pérdida estándar ponderada (`class_weight='balanced'`), ya que aplicaba castigos exponenciales de hasta 80x en los gradientes de la clase mayoritaria. Como resultado, la Tasa de Automatización se desplomó al 7.7%.
- **Solución Ingenieril:** Se subclassificó el `Trainer` de Hugging Face inyectando un tensor suavizado por raíz cuadrada: `1.0 / np.sqrt(frecuencias)`.
- **Efecto Físico:** El *Log-Loss* se contrajo masivamente (de 2.6 a 1.9). La red neuronal recuperó la tracción para predecir las clases mayoritarias con confianza, sin sufrir olvido catastrófico en la cola minoritaria.

## 4. Orquestador Maestro y Veredicto de Producción
Se desplegó el código en **Google Colab Pro (GPU A100)** ejecutando la ingesta sobre el 100% de la matriz de entrenamiento sin particiones (*Hold-Out Ciego*). Tras 10 épocas, el modelo evaluó los datos secuestrados en cuarentena, cerrando matemáticamente el proyecto:
- **Tasa de Automatización:** **30.46%** (Volumen puramente interceptado).
- **Precisión Condicionada:** **78.63%** (Acierto sobre el flujo interceptado).
- **F1-Macro:** **0.5152** (Hito estadístico: superada la barrera del 0.50 en 90 clases).
- **Log-Loss:** **1.9952**

La arquitectura algorítmica ha sido sellada y empaquetada como un binario `.safetensors` listo para el despliegue backend.
