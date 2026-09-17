# SITOR - Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** - *Evolve Academy*  
> **Versión del Alcance:** v8 (Cierre de Negocio y Despliegue MLOps)

---

## 🎯 1. Descripción y Contexto de Negocio

En el sector BPO y soporte técnico de telecomunicaciones, la clasificación inicial de incidencias en el Nivel 1 (Front Office) es crítica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la **Tripleta de Enrutamiento (Cola + Tipo + Prioridad)** en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos técnicos costosos, disparando el AHT (*Average Handling Time*) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Deep Learning**, el sistema analiza el texto crudo del ticket y actúa como un **interceptor en tiempo real**, auditando la tripleta asignada por el agente y automatizando el enrutamiento o alertando de desviaciones, siempre bajo una **Regla de Pasividad Estricta** (si el modelo duda, aborta la operación para no inyectar ruido sintético).

El objetivo matemático de SITOR es **predecir la combinación exacta de las 3 variables (altísima dimensionalidad)** para maximizar la automatización y el ROI del negocio, siendo un sistema escalable y agnóstico a la taxonomía específica de cualquier CRM.

---

## ⚙️ 2. Hitos Alcanzados (Evolución de la Arquitectura)

El ecosistema algorítmico ha atravesado una evolución desde modelos lineales hasta arquitecturas masivas de Transformers para romper el techo de cristal geométrico del negocio.

### 🔹 Fase 1 y 2: Baselines de Machine Learning Clásico (TF-IDF)
* **Ingeniería de la Tripleta:** Fusión de `Queue`, `Type` y `Priority` en una variable objetivo combinada.
* **Vectorización y Modelado:** Transformación del corpus a una matriz dispersa `TF-IDF`. Random Forest se coronó como el campeón de la IA clásica, pero demostró empíricamente la asfixia del enfoque estadístico (incapacidad semántica profunda).

### 🔹 Fase 3: Intervención Taxonómica y Limpieza de Ruido
* **Auditoría de Clases:** El negocio presentaba un desbalance extremo (88x). 
* **Colapso Semántico:** Se agruparon 13 colas residuales de baja frecuencia en una macro-clase `Derivacion_Manual_Minoritaria`, estabilizando el mapa de salidas en **90 clases** operativas viables.

### 🔹 Fase 4 y 5: Deep Learning y Transición a GPU (RoBERTa)
* **Sequence Classification Nativo:** Despliegue de una arquitectura densa basada en **RoBERTa-base (125M)** entrenada sobre GPUs T4/A100.
* **Balanceo Matemático:** Inyección de penalización mediante **raíz cuadrada** de frecuencias (`1 / sqrt(frecuencias)`), protegiendo minorías sin destruir mayorías.
* **Validación Hold-Out Maestro:** Entrenamiento *Full-Shot* sobre los 23.000 tickets certificando la viabilidad matemática.

### 🔹 Fase 6: Cierre Financiero y Optimización de Break-Even
* **Simulador de Estrés:** Ejecución de Jupyter local procesando la telemetría probabilística de la Fase 5.
* **Punto de Operación Dinámico:** Localización matemática del *Break-Even* financiero bajo un régimen de estrés humano (25% de error en FO).
* **Macro-Eficiencia:** Desglose del ROI tangible y blindaje intangible (prevención de SLA breaches, amortización de attrition).

---

## 📈 3. Veredicto de Producción (Métricas Finales)

El modelo maestro, evaluado contra un *Test Set* ciego de cuarentena (20% de los datos), arrojó las siguientes métricas definitivas al aplicar el umbral de confianza óptimo extraído algorítmicamente:

* **Volumen Intervenido:** Secuestro automatizado de más de 2.000 tickets tóxicos mensuales antes de impactar el L2.
* **F1-Macro:** **0.5152** (Demostración de estabilidad geométrica a través de las 90 clases).
* **Precisión Condicionada IA:** Sobre el **85%** en su zona de alta certidumbre.
* **Ahorro Financiero Neto:** Reducción contundente del coste del Back Office tras compensar los daños por falsos positivos.

---

## 🚀 4. Arquitectura MLOps en Desarrollo (Fase 7)

El proyecto se encuentra ejecutando su última fase de ingeniería de software para convertirse en un ecosistema de microservicios robusto:

1. **Backend REST (Event-Driven):** Empaquetado del tensor en un servidor `FastAPI` asíncrono en `src/api/`. La API expondrá un endpoint unitario `/predict` con validación estricta de Pydantic, diseñado para integrarse con los webhooks de CRMs (ServiceNow, Zendesk) en tiempo real. Implementa el Cortafuegos de Pasividad (devolviendo la tripleta humana original ante alta entropía).
2. **Torre de Control (Streamlit):** Construcción de un dashboard multipestaña en `src/frontend/`:
   * **Live Observability:** Feed de streaming en tiempo real para el NOC, mostrando intercepciones exitosas (verde) y mitigando el sesgo de supervivencia al mostrar los bloqueos por pasividad (gris).
   * **API Sandbox:** Consola interactiva para inyectar JSONs manuales y auditar el contrato de datos, el veredicto puro y la latencia del servidor.

---

## 🛠️ 5. Stack Tecnológico

| Área | Tecnología |
| :--- | :--- |
| **NLP & Deep Learning** | `Hugging Face`, `PyTorch`, `RoBERTa` |
| **Análisis de Datos**| `pandas`, `NumPy`, `Seaborn` |
| **Aceleración Hardware** | GPUs NVIDIA (T4 / A100) |
| **Backend API**| `FastAPI`, `Uvicorn`, `Pydantic` |
| **Frontend UI** | `Streamlit` |

---

## 📂 6. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── gold/                # Parquets finales purgados (90 clases)
│   └── resultados/          # CSVs de telemetría extraídos del Cloud
├── docs/                    # Manifiestos arquitectónicos y hojas de ruta
│   ├── historico_y_borradores/# Propuestas obsoletas (Ignorado por Git)
│   ├── parametros/          # Constantes del BPO para el simulador financiero
│   └── 11_Arquitectura_Despliegue_Fase7.md # Especificaciones definitivas MLOps
├── notebook/                # Notebooks de experimentación (Jupyter)
├── src/                     # Código fuente de despliegue MLOps
│   ├── api/                 # Microservicio backend (FastAPI + Pydantic)
│   └── frontend/            # Dashboard multipestaña (Streamlit)
├── README.md                
└── .gitignore               
```
