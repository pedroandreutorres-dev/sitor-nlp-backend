# PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
## SITOR: Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

| Programa | Área temática | Tipo de entrega |
| :--- | :--- | :--- |
| Máster en Data Science & IA | NLP, Arquitecturas Transformers, MLOps | MVP con datos BPO Sector Telco y orquestación simulada |

### 1. Resumen Ejecutivo y Justificación de Negocio
En el sector de Business Process Outsourcing (BPO) y soporte IT, la clasificación inicial de incidencias (Nivel 1 o Front-Office) es un proceso manual propenso a errores debido a la ambigüedad del lenguaje natural. Un error en la asignación de la tipología provoca derivaciones incorrectas a los equipos técnicos especializados (Nivel 2), incrementando el *Average Handling Time* (AHT).

El proyecto SITOR aborda esta ineficiencia implementando un sistema NLP predictivo que asiste de forma inteligente a los agentes (Copiloto). 

### 2. Alcance del Proyecto
* **MVP (Entregable principal):** Limpieza del corpus, validación de modelos clásicos, desarrollo de un modelo Deep Learning (RoBERTa), evaluación estricta con sellado de Data Leakage, cálculo del impacto financiero (ROI Asimétrico) y despliegue local mediante API REST (FastAPI) y panel de observabilidad visual (Streamlit).
* **Fuera de alcance:** Despliegue en Cloud de producción real y conexión a bases de datos de un CRM comercial.

### 3. Estrategia de Datos
Se utilizará un dataset depurado de 15.403 tickets del sector Telecomunicaciones. Durante el preprocesamiento, las variables queue, 	ype y priority se concatenarán formando una variable objetivo de **56 clases operativas**.

### 4. Metodología y Arquitectura
1. **Fase de Baselines:** Evaluación de modelos clásicos (TF-IDF + Random Forest) para auditar su asfixia estadística frente a la exigencia semántica.
2. **Fase de Deep Learning:** Implementación de RoBERTa-base (125M), con prevención estricta de Data Leakage intra-cluster mediante StratifiedGroupKFold.
3. **Fase Forense y Calibración Térmica:** Mitigación del *Overconfidence* de la red neuronal aplicando escalado térmico (Temperature Scaling) mediante optimización L-BFGS, generando probabilidades frecuentistas reales.
4. **Fase de Evaluación Financiera:** Simulación del ROI mediante una Matriz de Costes Asimétrica (diferenciando fricción administrativa vs rotura de SLA), y extracción pericial de explicabilidad (Caja Negra) mediante LIME.
5. **Fase de Despliegue (MLOps):** Empaquetado en FastAPI con validación Pydantic y exposición del producto en un framework pasivo (Copiloto) en Streamlit.
