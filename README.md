# SITOR — Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** — *Evolve Academy*  
> **Versión del Alcance:** v7 (Cierre de Arquitectura Deep Learning y Evaluación de Negocio)

---

## 🎯 1. Descripción y Contexto de Negocio

En el sector BPO y soporte técnico de telecomunicaciones, la clasificación inicial de incidencias en el Nivel 1 (Front Office) es crítica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la **Tripleta de Enrutamiento (Cola + Tipo + Prioridad)** en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos técnicos costosos, disparando el AHT (*Average Handling Time*) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Deep Learning**, el sistema analiza el texto crudo del ticket y actúa como un **interceptor en tiempo real**, auditando la tripleta asignada por el agente y automatizando el enrutamiento o alertando de desviaciones.

El objetivo matemático de SITOR es **predecir la combinación exacta de las 3 variables (altísima dimensionalidad)** para maximizar la automatización y el ROI del negocio, siendo un sistema escalable y agnóstico a la taxonomía específica de cualquier CRM.

---

## 🔬 2. Hitos Alcanzados (Evolución de la Arquitectura)

El ecosistema algorítmico ha atravesado una evolución desde modelos lineales hasta arquitecturas masivas de Transformers para romper el techo de cristal geométrico del negocio.

### ✅ Fase 1 y 2: Baselines de Machine Learning Clásico (TF-IDF)
* **Ingeniería de la Tripleta:** Fusión de `Queue`, `Type` y `Priority` en una variable objetivo combinada de más de 100 clases.
* **Vectorización y Modelado:** Transformación del corpus a una matriz dispersa `TF-IDF`. Evaluación empírica de Regresión Logística, Naive Bayes, LightGBM, XGBoost y Random Forest. 
* **Conclusión:** Random Forest se coronó como el campeón de la IA clásica, pero demostró empíricamente la asfixia del enfoque estadístico (TF-IDF no comprende el contexto semántico de tickets complejos).

### ✅ Fase 3: Intervención Taxonómica y Limpieza de Ruido
* **Auditoría de Clases:** El negocio presentaba un desbalance extremo (88x). Se identificó "basura operativa" (colas con menos de 30-50 tickets que destruían el optimizador).
* **Colapso Semántico:** Se agruparon 13 colas residuales de baja frecuencia en una macro-clase `Derivacion_Manual_Minoritaria`, estabilizando el mapa de salidas en **90 clases** operativas viables.

### ✅ Fase 4 y 5: Deep Learning y Transición a GPU (RoBERTa)
* **Abandono de Few-Shot:** Se descartó el modelo contrastivo *SetFit* debido a la colisión geométrica provocada por el alto ruido del corpus.
* **Sequence Classification Nativo:** Migración a una arquitectura densa basada en **RoBERTa-base (125M)** entrenada sobre GPUs T4/A100.
* **Balanceo Matemático (Log-Loss):** Inyección de un tensor de penalización suavizado mediante **raíz cuadrada** (`1 / sqrt(frecuencias)`). Esto evitó la explosión del gradiente en clases pequeñas sin destruir el acierto en las masivas.
* **Validación Hold-Out Maestro:** Tras estabilizar el *K-Fold*, el entrenamiento *Full-Shot* sobre los 23.000 tickets certificó la viabilidad del proyecto.

---

## 📊 3. Veredicto de Producción (Métricas Finales)

El modelo maestro, evaluado contra un *Test Set* ciego de cuarentena (20% de los datos), arrojó las siguientes métricas definitivas bajo un umbral de seguridad estricto ($P \ge 0.60$):

* **Tasa de Automatización:** **30.46%** (Volumen de Nivel 1 interceptado y resuelto por IA).
* **Precisión Condicionada:** **78.63%** (Acierto real de la IA sobre ese 30% automatizado).
* **F1-Macro:** **0.5152** (Demostración de estabilidad geométrica a través de las 90 clases).
* **Log-Loss:** **1.9952** (Reducción de entropía en las colas de probabilidad).

---

## 🚀 4. Próximos Pasos (Visualización y MLOps)

El proyecto entra en su fase de defensa académica e ingeniería de software:

1. **Evaluación Visual de Negocio (Fase 6):** Programación de un cuaderno local para ingestar los CSVs de telemetría y generar las matrices de confusión, curvas F1 y gráficas de ROI (Automatización vs Precisión) para la memoria del Máster.
2. **Ingeniería Backend:** Empaquetado de los `.safetensors` de RoBERTa y exposición de un endpoint `/predict` mediante `FastAPI` (Arquitectura Asíncrona).
3. **Despliegue Mockup:** Construcción del prototipo web visual para interactuar en vivo durante el tribunal.

---

## 🛠️ 5. Stack Tecnológico

| Área | Tecnología |
| :--- | :--- |
| **NLP & Deep Learning** | `Hugging Face (Transformers, Datasets)`, `PyTorch`, `RoBERTa` |
| **Machine Learning Base** | `scikit-learn`, `Random Forest` |
| **Ingeniería de Datos**| `pandas`, `Apache Arrow`, `fastparquet` |
| **Aceleración Hardware** | GPUs NVIDIA (T4 / A100) |
| **Microservicios (Futuro)**| `FastAPI`, `Uvicorn` |

---

## 📁 6. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── gold/                # Parquets finales purgados (90 clases)
│   └── resultados/          # CSVs de telemetría (K-Fold y Hold-out Maestro)
├── docs/                    # Memoria, diagramas y mockups de negocio
├── notebook/
│   ├── colab/               # Orquestadores GPU pesados (Entrenamiento RoBERTa)
│   ├── kaggle/              # Experimentación K-Fold y validaciones previas
│   └── historico/           # Pipelines obsoletos de ML clásico (Fase 2)
├── src/                     # Código fuente del microservicio (Backend API)
├── README.md                
└── .gitignore               
```
