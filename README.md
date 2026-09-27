# SITOR - Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** - *Evolve Academy*  
> **Autor:** Pedro Andreu Torres

---

## 🛡️ 1. Valor de Negocio y Macro-Eficiencia (Executive Summary)

En el sector BPO y soporte técnico de telecomunicaciones, el enrutamiento manual de incidencias en el Nivel 1 genera cuellos de botella y errores bajo presión. Un error de enrutamiento (ej: enviar una avería técnica urgente a Facturación) genera un "efecto ping-pong" que retrasa la resolución, pone en riesgo el cumplimiento estricto de los **SLA (Acuerdos de Nivel de Servicio)** y erosiona drásticamente el **NPS (Net Promoter Score)** al percibir el cliente que su problema no es atendido a tiempo.

**SITOR no automatiza a ciegas, actúa como un Auditor de Calidad (Cortafuegos Operativo).**
SITOR intercepta en tiempo real los tickets guardados por los agentes y, mediante Deep Learning, audita la decisión humana. Si detecta una discrepancia grave con alta certeza matemática, corrige la **Tripleta Operativa (56 colas)** en tiempo real, garantizando el cauce correcto y protegiendo la calidad del servicio.

### 📊 Veredicto de Producción (Matriz Asimétrica)
El valor del modelo trasciende la clásica métrica de Accuracy. Se construyó bajo una **Matriz de Costes Asimétrica**, asumiendo que no todos los errores tienen el mismo impacto de negocio. Aunque el modelo RoBERTa base alcanza un ~60% de precisión global en un dataset público genérico, al imponer un **umbral estricto de seguridad de 0.85**, SITOR actúa de forma pasiva y segura (IA Honesta). Solo interviene cuando la certeza es máxima, automatizando el flujo de los tickets claros, liberando a los equipos técnicos de ruido administrativo y permitiendo a la operadora cumplir sus SLA de resolución sin necesidad de sobredimensionar la plantilla.

---

## 🧠 2. Justificación Algorítmica y Data Science

El desarrollo empírico descartó el ML clásico a favor de arquitecturas de atención masiva adaptadas a las exigencias de negocio:

* **RoBERTa (125M de parámetros):** Se eligió por su capacidad de entender jerga técnica (correlación semántica fuerte) frente al ruido ortográfico.
* **Ingeniería de la Función de Pérdida (PyTorch):** Se inyectaron pesos dinámicos en la *Cross-Entropy Loss* re-calculados en cada iteración del *StratifiedGroupKFold* para combatir el desbalanceo extremo sin incurrir en Data Leakage.
* **Calibración Térmica (L-BFGS):** La red neuronal sufría de arrogancia probabilística. Se aplicó Temperature Scaling para aplanar las probabilidades, forzando a la red a dudar y evitando que la máquina disparase correcciones erróneas.
* **MLOps y Deriva de Datos (Data Drift):** SITOR está preparado para reciclar tripletas maestras en campañas estacionales inyectando Oversampling histórico en pipelines de re-entrenamiento.

---

## 🏗️ 3. Arquitectura de Microservicios (Stack)

El sistema se despliega imitando un entorno de producción Tier-1 corporativo:
- **Backend (FastAPI):** Expone endpoints REST (`/predict` y `/explain`). Mantiene los pesos de PyTorch en RAM mediante un lifespan manager para inferencia asíncrona de 0 latencia y ejecuta la interpretabilidad XAI en el servidor para evitar sobrecargar al cliente.
- **Frontend (Streamlit):** Panel de mando QA multipestaña (Live Waterfall Feed & LIME Sandbox) que consume lotes JSON inyectados por el CRM y evalúa decisiones en directo.

| Área | Tecnología |
| :--- | :--- |
| **NLP & Deep Learning** | Hugging Face, PyTorch, RoBERTa |
| **Análisis de Datos**| pandas, NumPy, Scikit-Learn |
| **Backend API**| FastAPI, Uvicorn, Pydantic, LIME |
| **Frontend UI** | Streamlit, Requests |

---

## 📁 4. Estructura del Repositorio

```text
SITOR/
├── data/
│   ├── gold/                  # Datasets refinados
│   ├── inbox/                 # JSONs de volcado del CRM simulado (Spooling)
│   ├── outbox/                # JSONs procesados por la API
│   └── raw/                   # Origen crudo de tickets
├── docs/                      # Memoria, Propuesta, y Guion de Presentación
├── notebook/                  # Cuadernos Jupyter del pipeline end-to-end
│   ├── 01_Auditoria_y_Deduplicacion.ipynb
│   ├── 02_Baselines_ML_Clasico.ipynb
│   ├── 03_Entrenamiento_RoBERTa.ipynb
│   ├── 04_Evaluacion_Marginal_y_ROI.ipynb
│   └── generador_demo.ipynb   # Generador de lotes JSON y ruido adversario
├── src/                       # Código fuente de despliegue
│   ├── api/                   # Microservicio backend (FastAPI)
│   ├── frontend/              # Dashboard multipestaña (Streamlit)
│   └── models/                # Pesos de RoBERTa para producción
└── README.md                
```

---

## 🚀 5. Guía de Ejecución Local (El Día de la Defensa)

Para arrancar el ecosistema en el entorno de la presentación final y evitar problemas de concurrencia de memoria con PyTorch, se ha consolidado el arranque en un orquestador único.

Simplemente haz doble clic o ejecuta en la terminal el archivo de lanzamiento:
```cmd
lanzar_demo.bat
```

Este script automatizado se encarga de:
1. Activar el entorno virtual (`.venv`).
2. Levantar el microservicio **FastAPI** (Backend) en el puerto `8000`, inyectando el modelo y LIME en RAM.
3. Desplegar la interfaz **Streamlit** (Frontend) en el puerto `8501` en una ventana separada.

* **Pestaña 1 (Live Observability):** Escucha la carpeta `data/inbox`, inicia la inferencia del lote simulado y muestra el *waterfall* en tiempo real con las métricas BPO, trasladando los tickets a `data/outbox`.
* **Pestaña 2 (API Sandbox):** Consola interactiva para que el tribunal pueda auditar tickets a mano, forzar errores humanos y visualizar el análisis semántico interno (XAI LIME) que SITOR realiza para tomar la decisión.
