# SITOR — Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** — *Evolve Academy*  
> **Versión del Alcance:** v3 (Enfoque en Experimentación Dual y MVP)

---

## 📌 1. Descripción y Contexto de Negocio

En el sector BPO y soporte técnico de telecomunicaciones, la clasificación inicial de incidencias en el Nivel 1 (Front Office) es crítica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la cola de destino en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos costosos, disparando el AHT (Average Handling Time) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Machine Learning**, el sistema analiza el texto del ticket y actúa como un **interceptor en tiempo real**, auditando la decisión del agente y corrigiendo falsos escalados antes de que ocurran, con foco especial en detectar averías masivas críticas (*Service Outages*).

---

## 🔬 2. Metodología "Dual-Track" (Inglés vs Español)

Debido al bajo volumen de tickets nativos en español, el proyecto ha adoptado una estrategia de experimentación paralela (**A/B Testing de Idiomas**) para construir una matriz de Coste/Beneficio empresarial:

1. **Vía Inglesa (Nativa):** ~16.000 tickets procesados directamente en su idioma original.
2. **Vía Española (Traducción):** Los tickets ingleses se han traducido masivamente al español mediante modelos de **Hugging Face (`opus-mt-en-es`)** simulando un entorno de localización.
3. **Objetivo:** Auditar si compensa (a nivel de F1-Score y Latencia de Inferencia) desplegar un modelo localizado en español o pagar una API de traducción en tiempo real hacia un modelo centralizado en inglés.

---

## ✅ 3. Hitos Alcanzados (Estado Actual del Proyecto)

El proyecto se encuentra en plena fase de experimentación algorítmica. Hasta la fecha se ha completado:

### Fase 1: Ingeniería de Datos y MLOps Base
* **Limpieza NLP:** Lematización y tokenización estricta con `spaCy` (`en_core_web_sm` y `es_core_news_sm`).
* **Ingeniería de Features:** Vectorización `TF-IDF` a 10.000 dimensiones.
* **Serialización MLOps:** Desacople arquitectónico guardando los tensores dispersos en formato hipercomprimido `.npz` y `.csv` en la carpeta `data/features` para cargas ultrarrápidas (< 0.5s) en notebooks posteriores.

### Fase 2: Baseline y Estudio de Ablación (SMOTE)
* **Algoritmo Baseline (Naive Bayes):** Demostró estadísticamente que los modelos simples fallan ante el desbalanceo masivo de clases (Recall de averías cayó al 5%).
* **Regresión Logística y SMOTE:** Se diseñó un Estudio de Ablación entrenando modelos lineales *con* y *sin* generación de datos sintéticos (SMOTE).
* **Gran Logro:** SMOTE equilibró el volumen de clases, elevando el F1-Macro a 0.50 y logrando un **Recall del 69% en averías críticas en español**, superando al modelo nativo inglés. Los modelos predicen con latencias en producción inferiores a **2.5 milisegundos**.

### Fase 3: Modelos No Lineales y Bagging (Random Forest)
* **El Salto de Precisión:** La transición a los árboles de decisión (`Random Forest`) elevó la nota F1-Macro nativa de 0.50 a **0.68**. 
* **Trazabilidad MLOps:** El modelo sufre un lógico aumento en la latencia de inferencia (de 2ms a 65ms) y el tiempo de entrenamiento, pero compensa al romper la barrera del **70% de F1-Score en detección de Averías Masivas** en ambos idiomas (usando SMOTE).

---

## 🚀 4. Próximos Pasos (Roadmap)

La siguiente fase se centra en llevar la precisión del modelo desde el actual ~68% hasta el techo operativo (>80%) usando arquitecturas de gradiente:

1. **Titanes de Boosting:** Enfrentamiento directo entre `XGBoost` y `LightGBM`. Se comparará el impacto de generar datos falsos (SMOTE) frente a usar el equilibrado matemático nativo de estos algoritmos (*Class Weights*).
2. **Hyperparameter Tuning (Embudo):** Los dos mejores modelos de las fases anteriores pasarán por un proceso exhaustivo de `GridSearchCV` para exprimir su precisión matemática.
3. **Desarrollo Backend:** Empaquetado del modelo campeón y exposición mediante un microservicio asíncrono con `FastAPI`.

---

## 🛠️ 5. Stack Tecnológico

| Área | Tecnología |
| :--- | :--- |
| **Lenguaje Core** | Python 3.10+ |
| **NLP & Traducción** | `spaCy`, Hugging Face (`Helsinki-NLP/opus-mt-en-es`) |
| **Machine Learning** | `scikit-learn`, `imbalanced-learn` (SMOTE), `XGBoost`, `LightGBM` |
| **Ingeniería de Datos**| `pandas`, `scipy.sparse` (Formatos `.npz` y `.parquet`) |
| **Microservicios (Futuro)**| `FastAPI`, `Uvicorn`, `Pydantic` |

---

## 📂 6. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── raw/                 # Dataset base original
│   ├── processed/           # Trackers de métricas (tracker_en.csv, tracker_es.csv)
│   └── features/            # Matrices TF-IDF (.npz) y etiquetas (.csv) listas para entrenar
├── docs/                    # Documentación técnica, estrategia MLOps y memorias del Test A/B
├── notebook/                # Laboratorio de IA (Pipelines numéricos y experimentales)
├── src/                     # Código fuente de producción (Futuro FastAPI)
├── .gitignore               
├── LICENSE                  
└── README.md                # Este documento
```
