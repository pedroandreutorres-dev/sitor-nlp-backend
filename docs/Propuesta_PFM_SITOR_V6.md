# PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
## SITOR
**Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias**

| Programa | Área temática | Tipo de entrega | Versión |
| :--- | :--- | :--- | :--- |
| Máster en Data Science & IA - Evolve Academy | NLP, LLMs y arquitecturas RAG, MLOps | MVP individual con datos públicos + plan de validación con datos reales (PoC) | V6 - Arquitectura MLOps con Evaluación de Coste-Beneficio y Enrutamiento Semántico |

> **Nota sobre esta versión**
> Tras los análisis exploratorios iniciales, esta versión V6 establece un marco de evaluación empírica riguroso. Se evaluará una arquitectura semántica basada en embeddings congelados frente a baselines clásicos (TF-IDF). La arquitectura final se seleccionará mediante validación cruzada multicriterio (rendimiento predictivo, latencia y coste computacional). Adicionalmente, el diseño se concibe como *Config-Driven* para posibilitar el escalado a contextos largos.

---

### 1. Resumen Ejecutivo y Justificación de Negocio
En el sector de Business Process Outsourcing (BPO) y telecomunicaciones, la clasificación inicial de tickets recae en agentes de Nivel 1 operando bajo estrictas métricas de tiempo. La ambigüedad del lenguaje del cliente provoca errores en la tipificación manual de la "tripleta" (Cola, Tipo, Prioridad). 

Estos errores derivan en falsos escalados hacia el Back Office (Nivel 2), consumiendo recursos técnicos costosos. SITOR aborda esta ineficiencia aplicando Inteligencia Artificial para automatizar el enrutamiento. 

**Objetivo principal de negocio:** Predecir de forma íntegra la Tripleta para automatizar el enrutamiento inicial, derivando a revisión humana los casos anómalos o con baja confianza predictiva.

---

### 2. Alcance del PFM: MVP, Extensión Opcional y Fuera de Alcance

| Nivel | Contenido | Compromiso |
| :--- | :--- | :--- |
| **MVP (núcleo entregable)** | Evaluación comparativa de pipelines (TF-IDF vs Embeddings) + microservicio FastAPI + evaluación de ROI sobre dataset público. | Innegociable. |
| **Extensión (si el calendario lo permite)** | Copiloto RAG sobre histórico, y dashboard mínimo de KPIs técnicos. | Deseable. |
| **Fuera de alcance** | Despliegue en CRM real, **Experimento A/B de Traducción Multilingüe** (descartado en esta versión para priorizar la carga computacional de la evaluación arquitectónica). | Documentado como trabajo futuro. |

---

### 3. Estrategia de Datos y Lógica de Abstención

#### 3.1 Dataset base seleccionado
| Nombre | Contenido | Uso en SITOR |
| :--- | :--- | :--- |
| Multilingual Customer Support Tickets (Kaggle) | Tickets con asunto, texto, cola, tipo y prioridad. | `queue` + `type` + `priority` conforman la variable objetivo. |

#### 3.2 Lógica Operativa: Auditoría de Soporte y Confianza
1.  **Auditoría de Soporte (Previo al Split):** Antes de dividir el dataset, se audita el soporte histórico absoluto. Toda clase con un soporte inferior a las muestras mínimas exigidas por el K-Fold (10 muestras) será agrupada bajo la etiqueta `OUT_OF_SCOPE` para evitar colapsos matemáticos. *(Para el MVP actual, el Análisis Exploratorio confirmó que la clase minoritaria posee soporte suficiente, haciendo innecesaria la destrucción de clases).*
2.  **Abstención Dinámica en Inferencia:** En producción, si la predicción matemática del ticket arroja la clase `OUT_OF_SCOPE`, o si arroja cualquier otra clase pero con una confianza inferior al umbral de negocio (ej. 60%), la API colapsará la salida y devolverá el estado `MANUAL_REVIEW` al agente humano.

---

### 4. Arquitectura del MVP y Enrutamiento Semántico

#### 4.1 El Experimento Evaluativo ("Bake-Off")
Se ejecutará un torneo empírico para seleccionar el mejor pipeline desplegable. Los pipelines aplicarán pesos de clase (`class_weight`) durante el entrenamiento para gestionar el desbalanceo natural:

1.  **Baseline Léxico Rápido:** `TF-IDF` + Regresión Logística.
2.  **Baseline Léxico Pesado:** `TF-IDF` + Random Forest (evaluado previamente con un F1-Macro de ~0.56).
3.  **Pipeline Semántico:** *Frozen Embeddings* (ej. `BAAI/bge-small-en-v1.5`) + Regresión Logística. 

#### 4.2 Escalabilidad y Enrutamiento Dinámico (*Model Routing*)
Para garantizar la viabilidad del MVP como un producto B2B SaaS adaptable a diferentes empresas, la arquitectura semántica se diseña bajo un patrón algorítmico:
*   **Profiling Automático:** Al ingerir un nuevo histórico, el sistema calcula el percentil 95 de longitud de los tickets.
*   **Routing Config-Driven:** Si la longitud es corta (< 400 palabras), el orquestador emplea modelos eficientes de 512 tokens (`bge-small`) para optimizar el coste de CPU. Si el contexto es largo (ej. volcados técnicos), aprovisiona modelos de 8192 tokens (ej. `jina-embeddings`). Adicionalmente, implementa truncado inteligente (Head+Tail) para comprimir información irrelevante si existen SLAs de latencia estrictos.

---

### 5. Plan de Evaluación Científica
1.  **Selección de Arquitectura (5-Fold CV):** Se utilizará Validación Cruzada Estratificada (**Stratified 5-Fold CV**) exclusivamente sobre el conjunto de Entrenamiento para decidir el modelo ganador cruzando métricas de F1-Macro, tiempos de CPU (entrenamiento) y latencia (p95).
2.  **Evaluación de Impacto de Negocio (Test Set):** El modelo ganador se evaluará **una única vez** sobre el conjunto de Test (datos nunca vistos). De este resultado se extraerán la Precisión y Recall para el 100% de las clases, aislando los *Service Outages* críticos para el caso de negocio.

---

### 6. Viabilidad Comercial y Caso de Negocio Simulado
Se construye un caso teórico para ilustrar la aplicabilidad:
*   Volumen de tickets/mes: 50.000.
*   Tasa de errores y falsos escalados: 12%.
*   Coste de retrabajo por error: 9€ a 13€.
*   **Ahorro simulado:** La estimación cuantitativa de reducción de costes se documentará tras finalizar la evaluación sobre el conjunto de Test, cruzando los aciertos operativos con el coste de infraestructura de la arquitectura ganadora.
