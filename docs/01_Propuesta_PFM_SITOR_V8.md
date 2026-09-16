# PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
## SITOR
**Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias**

| Programa | Área temática | Tipo de entrega | Versión |
| :--- | :--- | :--- | :--- |
| Máster en Data Science & IA - Evolve Academy | NLP, LLMs y arquitecturas RAG, MLOps | MVP individual con datos públicos + plan de validación con datos reales (PoC) | V8.0 - Cierre Financiero y MLOps |

> **Nota sobre esta versión**
> Esta versión V8.0 integra las lecciones aprendidas durante la Fase 6 de evaluación financiera. Se ha reemplazado el concepto de colas sumidero por una **Regla de Pasividad Estricta**, y se ha eliminado cualquier referencia a umbrales de decisión estáticos (ej. 60%), subordinando la Tasa de Automatización al cálculo dinámico del *Break-Even* financiero bajo escenarios de estrés (25% error FO). El proyecto avanza hacia la Fase 7 (Despliegue FastAPI + Streamlit).

---

### 1. Resumen Ejecutivo y Justificación de Negocio
En el sector de Business Process Outsourcing (BPO) y telecomunicaciones, la clasificación inicial de tickets recae en agentes de Nivel 1 operando bajo estrictas métricas de tiempo. La ambigüedad del lenguaje del cliente provoca errores en la tipificación manual de la "tripleta" (Cola, Tipo, Prioridad). 

Estos errores derivan en falsos escalados hacia el Back Office (Nivel 2), consumiendo recursos técnicos costosos. SITOR aborda esta ineficiencia aplicando Inteligencia Artificial para auditar matemáticamente estas decisiones en tiempo real. 

**Objetivo principal de negocio:** Actuar como un motor de Quality Assurance (QA) que predice la Tripleta real para auditar, validar o auto-corregir el triaje humano, derivando a revisión manual los casos con baja confianza predictiva.

---

### 2. Alcance del PFM: MVP, Extensión Opcional y Fuera de Alcance

| Nivel | Contenido | Compromiso |
| :--- | :--- | :--- |
| **MVP (núcleo entregable)** | Curación anti-falsificación del dataset, validación cruzada con Folds pre-calculados, evaluación multicriterio de pipelines (TF-IDF vs Embeddings vs DL Híbrido/Cloud) + API FastAPI + ROI. | Innegociable. |
| **Extensión (si el calendario lo permite)** | Copiloto RAG sobre histórico, y dashboard mínimo de KPIs técnicos. | Deseable. |
| **Fuera de alcance** | Despliegue en CRM real. **Enrutamiento Dinámico de Modelos (*Model Routing*) por longitud extrema de contexto** (Descartado por YAGNI tras el EDA). | Documentado como trabajo futuro. |

---

### 3. Estrategia de Datos y Lógica de Abstención

#### 3.1 Dataset base seleccionado
| Nombre | Contenido | Uso en SITOR |
| :--- | :--- | :--- |
| Multilingual Customer Support Tickets (Kaggle) | Tickets con asunto, texto, cola, tipo y prioridad. | `queue` + `type` + `priority` conforman la variable objetivo. |

#### 3.2 Lógica Operativa: Anti-Falsificación y Abstención
1.  **Auditoría y Mapeo (Previo al Split):** La formación de la tripleta disparará la cardinalidad de clases. **Queda estrictamente prohibido eliminar filas del dataset.** Toda clase irrelevante o con un volumen estadísticamente inaprendible será colapsada unificadamente bajo la etiqueta `Derivacion_Manual_Minoritaria`. Esto asegura que el denominador volumétrico de producción sea idéntico al histórico. Tras esto, se realizará el *Stratified Train/Test Split*.
2.  **Abstención Dinámica en Inferencia (Regla de Pasividad):** En producción, si la predicción matemática del ticket arroja la clase `Derivacion_Manual_Minoritaria`, o si la red neuronal emite una probabilidad inferior al umbral óptimo de *Break-Even* financiero, el orquestador abortará la intervención. Aplicando una regla de pasividad estricta, SITOR no modificará la tipificación original y permitirá que el ticket mantenga su flujo orgánico humano, asumiendo la tasa de error histórica sin inyectar ruido sintético.

---

### 4. Arquitectura del MVP: El "Bake-Off" Multicriterio

Se ejecutará un torneo empírico utilizando exclusivamente contexto estándar (512 tokens). Todos los pipelines manejarán el desbalanceo. Para aislar las capacidades del Deep Learning respecto a las limitaciones de hardware, la arquitectura D se bifurca:

1.  **Baseline Léxico Rápido (ML):** `TF-IDF` + Regresión Logística.
2.  **Baseline Léxico Pesado (ML):** `TF-IDF` + Random Forest (control histórico).
3.  **Pipeline Semántico (Representación DL + ML):** *Frozen Embeddings* (ej. `BAAI/bge-small-en-v1.5`) + Regresión Logística. (Se forzará el truncado al límite de 512 tokens para proteger la señal de negocio).
4.  **Bifurcación Deep Learning:**
    *   **Modelo D.1 (Local - CPU Limitado):** *Few-Shot Learning* mediante **SetFit** (`bge-small`). Se estresará el hardware local incrementando `num_shots` (ej. 32/64) implementando un fallback dinámico en caso de MemoryError.
    *   **Modelo D.2 (Cloud - GPU 16GB):** *Fine-Tuning* clásico de LLMs (HuggingFace `Trainer`). Entrenado sobre el 100% de la volumetría utilizando técnicas de acumulación de gradientes y *checkpoints* estrictos para tolerar la volatilidad de entornos gratuitos tipo Colab.

---

### 5. Plan de Evaluación Científica y Reproducibilidad
1.  **Garantía de Reproducibilidad (MLOps):** Para asegurar que los modelos locales y en Cloud compiten de forma justa, el dataset particionado y los índices del *5-Fold CV* serán **pre-calculados** en la fase de ingeniería de datos y exportados estáticamente a `.parquet`.
2.  **Validación Cruzada Estratificada (5-Fold CV):** Sobre los Folds pre-calculados, cruzando:
    *   **Predictivas:** F1-Macro (con varianza para medir estabilidad) y F1-Weighted.
    *   **Coste/Rendimiento:** Tiempos de CPU/GPU (entrenamiento) y latencia (p95).
    *   **Negocio:** **Tasa de Automatización de Auditoría** (porcentaje de tickets validados o auto-corregidos de forma autónoma, evaluado contra el 100% del volumen real tras aislar matemáticamente el umbral de *Break-Even* que maximiza el ROI en escenarios de estrés).
3.  **Calibración del Punto de Operación (Operating Point):** Sobre el modelo ganador, se ejecutará un barrido del umbral de confianza probabilística (ej. 0.50 a 0.95) cruzando la curva Precision-Recall con la matriz de costes del negocio, para fijar el umbral estático definitivo.
4.  **Evaluación de Impacto de Negocio (Test Set - One-Shot):** Con el umbral óptimo congelado, el modelo campeón se evaluará **una única vez** sobre el conjunto de Test para extraer métricas definitivas y calcular el ROI de la auditoría autónoma.
