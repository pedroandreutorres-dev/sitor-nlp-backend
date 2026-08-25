# SITOR — Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** — *Evolve Academy*  
> **Versión del Alcance:** v4 (Enfoque Tábula Rasa - Clasificación Multi-Clase de Tripleta)

---

## 📌 1. Descripción y Contexto de Negocio

En el sector BPO y soporte técnico de telecomunicaciones, la clasificación inicial de incidencias en el Nivel 1 (Front Office) es crítica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la **Tripleta de Enrutamiento (Cola + Tipo + Prioridad)** en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos técnicos costosos, disparando el AHT (Average Handling Time) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Machine Learning**, el sistema analiza el texto del ticket y actúa como un **interceptor en tiempo real**, auditando la tripleta asignada por el agente y corrigiendo falsos escalados antes de que ocurran. 
A diferencia de aproximaciones conservadoras que predicen solo la cola de destino, el objetivo matemático de SITOR es **predecir la combinación exacta de las 3 variables (alta dimensionalidad de clases únicas)** para maximizar la automatización y el ROI del negocio, siendo un sistema escalable y agnóstico a la taxonomía específica de cualquier CRM.

---

## 🔬 2. Metodología "Dual-Track" (Inglés vs Español)

Debido al bajo volumen de tickets nativos en español, el proyecto ha adoptado una estrategia de experimentación paralela (**A/B Testing de Idiomas**):

1. **Vía Inglesa (Nativa):** ~16.000 tickets útiles procesados directamente en su idioma original.
2. **Vía Española (Traducción):** Los tickets ingleses se han traducido masivamente al español mediante modelos de **Hugging Face (`opus-mt-en-es`)** simulando un entorno de localización.
3. **Objetivo:** Auditar si compensa (a nivel de F1-Score y Latencia de Inferencia) desplegar un modelo localizado en español o pagar una API de traducción en tiempo real hacia un modelo centralizado en inglés.

---

## ✅ 3. Hitos Alcanzados (Estado Actual del Proyecto)

Se ha ejecutado un reinicio de arquitectura (*Tábula Rasa*) para enfocar todo el *pipeline* algorítmico exclusivamente a la predicción de la Tripleta completa.

### Fase 1: Limpieza, Traducción y Formato (Completado)
* **Preprocesado NLP:** Lematización y tokenización estricta con `spaCy`.
* **Consolidación:** Guardado de la capa Silver limpia en `.parquet`.

### Fase 2: Ingeniería de la Tripleta (En curso)
* **Generación del Target:** Combinación de las variables de negocio en una etiqueta única (`Cola - Tipo - Prioridad`), resultando en una taxonomía consolidada de múltiples clases.
* **Particionado Estratificado:** Creación de splits de Entrenamiento y Test preservando la representación matemática de cada una de las clases en el examen final.

---

## 🚀 4. Próximos Pasos (Roadmap de Modelado)

1. **Vectorización NLP:** Extracción de características mediante `TF-IDF` a 10.000 dimensiones.
2. **Bake-Off Algorítmico (Baseline Multi-Clase):** Competición directa de arquitecturas (`Logistic Regression`, `Random Forest`, `LightGBM`, `XGBoost`) para determinar quién soporta mejor la alta dimensionalidad sin colapsar en RAM o tiempo.
3. **Inyección Sintética (SMOTE) y Tuning:** Aplicación de *Data-Level Balancing* para engordar las combinaciones raras y optimización de hiperparámetros mediante `GridSearchCV` sobre el algoritmo ganador.
4. **Desarrollo Backend:** Empaquetado del modelo campeón y exposición mediante un microservicio asíncrono con `FastAPI`.

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
│   ├── processed/           # Datos limpios capa Silver (.parquet)
│   └── features/            # Textos y etiquetas listas para entrenar
├── docs/                    # Documentación técnica y propuesta de negocio
├── notebook/                # Laboratorio de IA (Pipelines numéricos)
│   └── historico_L1/        # (Oculto) Backup de arquitecturas descartadas
├── src/                     # Código fuente de producción (Futuro FastAPI)
├── .gitignore               
├── LICENSE                  
└── README.md                # Este documento
```
