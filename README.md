# SITOR — Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** — *Evolve Academy*  
> **Versión del Alcance:** v6 (Fase de MLOps y Diseño de Producto)

---

## 🎯 1. Descripción y Contexto de Negocio

En el sector BPO y soporte técnico de telecomunicaciones, la clasificación inicial de incidencias en el Nivel 1 (Front Office) es crítica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la **Tripleta de Enrutamiento (Cola + Tipo + Prioridad)** en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos técnicos costosos, disparando el AHT (*Average Handling Time*) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Machine Learning**, el sistema analiza el texto del ticket y actúa como un **interceptor en tiempo real**, auditando la tripleta asignada por el agente y corrigiendo falsos escalados antes de que ocurran. 

El objetivo matemático de SITOR es **predecir la combinación exacta de las 3 variables (alta cardinalidad)** para maximizar la automatización y el ROI del negocio, siendo un sistema escalable y agnóstico a la taxonomía específica de cualquier CRM.

---

## 🔬 2. Hitos Alcanzados (Estado Actual del Proyecto)

El core algorítmico de Data Science ha sido completado y estabilizado.

### ✅ Fase 1: Ingeniería de Datos y Experimentación A/B
* **Traducción y A/B Testing:** Se ejecutó una traducción sintética masiva (`opus-mt-en-es`) comparando el rendimiento de un modelo nativo (Inglés) contra uno localizado (Español). Decisión: SITOR operará en **inglés nativo** para evitar ruido semántico y latencias de traducción.
* **Ingeniería de la Tripleta:** Fusión de `Queue`, `Type` y `Priority` en una variable objetivo combinada de altísima dimensionalidad, forzando al algoritmo a resolver el problema completo del CRM de un solo golpe.

### ✅ Fase 2: Modelado y Bake-Off Algorítmico
* **Vectorización:** Transformación del corpus a una matriz dispersa `TF-IDF` truncada.
* **Prevención de Data Leakage:** Implementación estricta de sobremuestreo dinámico (`SMOTE`) encapsulado exclusivamente dentro de los pliegues de entrenamiento (*K-Fold CV*).
* **El Torneo (Bake-Off):** Evaluación empírica de Regresión Logística, Naive Bayes, LightGBM, XGBoost y Random Forest. **Conclusión:** Se descartó *LightGBM* por colapso estructural ante matrices dispersas, coronándose **Random Forest** como el algoritmo campeón por su equilibrio entre F1-Macro y coste computacional en RAM.
* **Optimización Coarse-to-Fine:** Hiperajuste secuencial mediante `RandomizedSearchCV` seguido de `GridSearchCV` milimétrico.

### ✅ Fase 3: Diseño de Producto (UX/UI)
* Diseño del frontal operativo (*Mockup*) para los auditores de Nivel 2, enfocado en el modelo *Human-in-the-loop*, explicando las variables NLP y mostrando la confianza matemática frente al umbral crítico de auto-enrutamiento (85%).

---

## 🚀 3. Próximos Pasos (Roadmap de MLOps)

El proyecto entra en su fase final orientada al despliegue en producción:

1. **Ingeniería de Software (Backend):** Empaquetado del modelo `.pkl` y exposición de un endpoint `/predict` mediante un microservicio asíncrono con `FastAPI`.
2. **Reglas de Negocio API:** Programar la lógica de negocio (Si Confianza $\ge$ 85% $\rightarrow$ `AUTO_CORRECT`; Si 60-84% $\rightarrow$ `REVIEW`).
3. **Despliegue de Prototipo (Opcional):** Levantamiento de un frontal interactivo mínimo en `Streamlit` para interactuar en vivo con la API durante la defensa del Máster.

---

## 🛠️ 4. Stack Tecnológico

| Área | Tecnología |
| :--- | :--- |
| **Lenguaje Core** | Python 3.10+ |
| **NLP & Preprocesado** | `spaCy`, `NLTK`, Hugging Face |
| **Machine Learning** | `scikit-learn`, `imbalanced-learn` (SMOTE), `Random Forest` |
| **Ingeniería de Datos**| `pandas`, `scipy.sparse` (Formatos `.npz` y `.parquet`) |
| **Microservicios (MLOps)**| `FastAPI`, `Uvicorn`, `Pydantic` |

---

## 📁 5. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── raw/                 # Dataset base original
│   ├── processed/           # Datos limpios capa Silver (.parquet)
│   └── features/            # Matrices TF-IDF listas para entrenar (.npz)
├── docs/                    # Entregables y Mockups UX
├── notebook/                # Laboratorio de IA (Pipelines numéricos)
│   └── historico_L1/        # Backup de arquitecturas descartadas
├── src/                     # Código fuente de producción (Futuro FastAPI)
├── .gitignore               
├── LICENSE                  
└── README.md                # Este documento
```
