# SITOR - Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Trabajo de Fin de Máster (TFM)**  
> **Máster en Data Science & IA** - *Evolve Academy*  
> **Autor:** Pedro Andreu Torres

---

## 🎯 1. Impacto de Negocio y Macro-Eficiencia (Executive Summary)

En el sector BPO y soporte técnico de telecomunicaciones, el enrutamiento manual de incidencias en el Nivel 1 genera cuellos de botella y errores por fatiga o falta de contexto. Un error de enrutamiento (ej: enviar una avería técnica urgente a Facturación) provoca retrasos en cascada, multas por rotura de **SLA (Service Level Agreement)** y erosión del **NPS**.

**SITOR no es un sistema de enrutamiento a ciegas; es un Muro de Fuego Algorítmico.**
El sistema evalúa cada ticket entrante y toma una decisión de enrutamiento sobre 56 colas operativas complejas. SITOR está diseñado con una **Matriz de Costes Asimétrica**: solo interviene y automatiza el flujo si supera un umbral de certeza matemática del **0.85**. Si la certeza es menor, delega al humano.

### 📊 Veredicto de Producción (Resultados Finales)
* **Precisión Algorítmica (Base Multiclase):** En validación ciega (K-Fold cruzado), el modelo base arroja un **~59% de Accuracy**. En un problema de clasificación extrema con 56 colas semánticamente solapadas, este es el límite matemático del modelo forzado a predecir a ciegas.
* **El Muro de Fuego (Umbral 0.85):** En lugar de automatizar con un 59% de acierto (inviable para negocio), se aplica calibración L-BFGS y un umbral de confianza. SITOR solo automatiza el **38.5%** del volumen entrante donde su certeza supera el 85%.
* **Precisión Operativa (IA):** Sobre ese 38.5% de volumen automatizado, el modelo alcanza una precisión quirúrgica del **97.3%** (solo 2.7% de error residual).
* **Retorno de Inversión (ROI) in-vitro:** Al derivar los casos dudosos al humano, las simulaciones proyectan una **reducción teórica del 31.8% en los errores operativos**. *(Nota: Tal como se recomienda en auditorías de IA, esta métrica es una proyección in-vitro que requiere ser validada con tickets reales en Shadow Mode antes de su certificación final).*

### 📦 Disponibilidad de Pesos del Modelo
Debido a las restricciones de cuota de GitHub (LFS) para archivos superiores a 100MB, los tensores finales del modelo entrenado (`model.safetensors`, ~500MB) no están incluidos directamente en el repositorio. Para reproducir el modelo, se puede ejecutar el cuaderno `03_Entrenamiento_RoBERTa.ipynb` de principio a fin, el cual generará los pesos localmente en la carpeta `src/models/roberta_corporativo_final/`.

### 🌐 Origen de los Datos (Corpus)
Por motivos de confidencialidad corporativa y rigor académico, el entrenamiento de esta red neuronal no utiliza datos privados de clientes reales. El ecosistema ha sido modelado y validado sobre un **dataset público de Kaggle** especializado en *Customer Support* de Telecomunicaciones. Este corpus original en inglés fue sometido a un severo proceso de deduplicación, limpieza de ruido ortográfico y mapeo asimétrico cruzando 56 colas operativas complejas para simular un entorno BPO Tier-1 real.

---

## 🧠 2. Ingeniería de Machine Learning (Core Matemático)

La arquitectura técnica se sostiene sobre tres pilares diseñados para sobrevivir al escrutinio académico y de negocio:

* **Motor Predictivo (RoBERTa 125M):** *Fine-tuning* de un modelo *Transformer* profundo para dominar la semántica y la jerga de IT/Telco frente al ruido ortográfico.
* **Blindaje contra Data Leakage:** Validación cruzada estricta mediante **StratifiedGroupKFold** para evitar el sobreajuste, asegurando que las métricas reflejen puramente escenarios *Out-of-Distribution* reales.
* **Auditoría Forense y Autoconciencia (L-BFGS):** Las redes neuronales estándar sufren de sobreconfianza (overconfidence). Se inyectó calibración térmica continua (*Temperature Scaling*, T_opt = 1.6139) mediante el algoritmo L-BFGS, haciendo que el modelo adquiera autoconciencia matemática: si duda, aplana sus probabilidades y pasa al humano.

---

## 🏗️ 3. Arquitectura del Ecosistema Híbrido (MLOps)

El ecosistema se despliega en una arquitectura de microservicios robusta simulando un entorno Tier-1:

- **Motor Backend (FastAPI):** Expone un endpoint de inferencia (`/predict`) que mantiene los tensores de PyTorch en memoria viva (*lifespan manager*), logrando latencias inferiores a 200ms.
- **Torre de Control (Streamlit):** Panel de observabilidad en tiempo real (Dashboard). Monitoriza la ingesta de tickets por el CRM, mide el ahorro en AHT (*Average Handling Time*) y dibuja en pantalla el *override* algorítmico de SITOR con sus métricas en directo.

| Capa Técnica | Stack / Tecnologías |
| :--- | :--- |
| **NLP & Deep Learning** | Hugging Face Transformers, PyTorch, RoBERTa |
| **Calibración y ML**| scikit-learn, SciPy (L-BFGS), pandas, NumPy |
| **Backend REST API**| FastAPI, Uvicorn, Pydantic |
| **Torre de Control (UI)** | Streamlit, Requests |
| **Documentación Web** | Reveal.js, PyMuPDF, LibreOffice Headless |

---

## 📁 4. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── inbox/                 # JSONs de volcado del CRM simulado (Spooling)
│   └── outbox/                # JSONs procesados y auditados por SITOR
├── docs/                      
│   ├── entregas/              # Entregables técnicos originales (.pdf, .pptx)
│   ├── Memoria_TFM_SITOR.pdf  # Memoria académica oficial 
│   └── TFM_SITOR_Notebooks_Completos.pdf # Vaciado íntegro de la experimentación
├── images/                    # Asset library (Gráficos, Heatmaps, Sankey)
├── Presentacion_Web_Limpia/   # Aplicación web nativa interactiva para la defensa (Reveal.js)
│   └── index.html             # Doble clic para iniciar la presentación a pantalla completa
├── src/                       # Código fuente de despliegue MLOps
│   ├── api/                   # Microservicio predictivo (FastAPI)
│   ├── frontend/              # Interfaz Torre de Control (Streamlit)
│   └── models/                # Checkpoints y weights (RoBERTa)
├── requirements.txt           # Lock-file con las dependencias estrictas de producción
└── README.md                  # Especificación técnica del proyecto
```

---

## 🚀 5. Despliegue y Ejecución

El proyecto cuenta con un entorno virtual depurado y listo para arrancar la demo interactiva. Abre tu terminal de comandos en la carpeta raíz del proyecto y levanta los dos servicios clave:

**1. Levantar el Motor de Inteligencia (Backend):**
```bash
.venv\Scripts\python.exe src/api/main.py
```

**2. Levantar la Torre de Control (Frontend):**
Abre una nueva terminal en paralelo y ejecuta:
```bash
.venv\Scripts\streamlit.exe run src/frontend/app.py
```

*Una vez levantado el frontend, pulsa el botón **▶ Iniciar Simulación** en la Torre de Control. El ecosistema procesará asíncronamente el archivo inbox de simulación, re-enrutando en tiempo real las incidencias seguras y delegando al humano el ruido operativo, actualizando los KPIs financieros en directo.*
