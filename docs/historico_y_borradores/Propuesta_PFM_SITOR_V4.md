# PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
## SITOR
**Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias**

| Programa | Área temática | Tipo de entrega | Versión |
| :--- | :--- | :--- | :--- |
| Máster en Data Science & IA - Evolve Academy | NLP, LLMs y arquitecturas RAG, MLOps | MVP individual con datos públicos + plan de validación con datos reales (PoC) | V3 - Actualizada tras EDA (Test A/B Idioma) |

> **Nota sobre esta versión**
> Este documento revisa la propuesta original de SITOR para ajustarla a lo que un Trabajo de Fin de Máster individual puede ejecutar y defender en el tiempo disponible: un dataset público identificado desde el inicio, un alcance de MVP (clasificación + API) con la arquitectura RAG como extensión opcional, un caso de negocio simulado con supuestos explícitos y citados (Sección 7), y un tratamiento honesto de las limitaciones de generalización a entornos empresariales reales.

---

### 1. Resumen Ejecutivo y Justificación de Negocio
En el sector de Business Process Outsourcing (BPO) y en las grandes compañías de telecomunicaciones, la gestión eficiente de incidencias en los canales de soporte es un factor crítico de coste y de satisfacción del cliente. La clasificación inicial de los tickets recae habitualmente en agentes de Front Office (Nivel 1), que operan bajo estrictas métricas de tiempo de operación (TMO). Esa presión, sumada a la ambigüedad del lenguaje del cliente, provoca errores en la tipificación manual de la "tripleta" (Tipo, Subtipo, Detalle) del CRM. 

Los errores de tipificación derivan en falsos escalados hacia el Back Office (Nivel 2), que consume recursos técnicos costosos en identificar el error y devolver el caso a la cola correcta. SITOR aborda esta ineficiencia combinando procesamiento de lenguaje natural (NLP) e Inteligencia Artificial Generativa para automatizar la auditoría de enrutamiento y acelerar la resolución de incidencias. 

**Objetivo principal de negocio:** Reducir los falsos escalados, optimizar el tiempo medio de resolución (AHT) del Back Office mediante asistencia contextual, y dotar a la dirección de métricas de impacto económico.

**Encuadre honesto del proyecto:**
Esta versión del documento distingue de forma explícita entre lo que el PFM construye y valida con datos públicos (el MVP) y lo que se plantea como hipótesis de despliegue comercial, pendiente de validar con datos reales de una empresa (la PoC). El primero es defendible con resultados; el segundo es una propuesta razonada, no un resultado.

---

### 2. Alcance del PFM: MVP, Extensión Opcional y Fuera de Alcance
La propuesta original planteaba cuatro fases con el mismo nivel de profundidad. Para un trabajo individual con un calendario de máster, ese alcance equivale a un roadmap de producto de varios meses con equipo, no a un PFM. Se redefine el alcance en tres niveles:

| Nivel | Contenido | Compromiso |
| :--- | :--- | :--- |
| **MVP (núcleo entregable)** | Motor de clasificación jerárquica de tripletas + microservicio FastAPI + evaluación con métricas reales sobre dataset público | Innegociable. Es lo que se defiende con resultados. |
| **Extensión (si el calendario lo permite)** | Copiloto RAG sobre el mismo histórico, y un dashboard mínimo de KPIs técnicos (sin ROI en euros) | Deseable, no crítico para aprobar. |
| **Fuera de alcance (visión de producto)** | Cálculo de ROI en €, clustering de averías masivas, priorización por churn/sentimiento, PoC con CRM real | Se documentan como trabajo futuro, sin construirse. |

Este recorte no reduce la ambición del proyecto: concentra el esfuerzo donde se puede demostrar con números reales (precisión del clasificador, tiempo de respuesta de la API), en lugar de repartirlo en cuatro frentes que quedarían a medio terminar.

---

### 3. Estrategia de Datos: Un Dataset Concreto, no una Promesa
Un PFM debe partir de un dataset identificado desde el día uno, no de una categoría de datasets.

#### 3.1 Dataset base seleccionado
| Nombre | Contenido | Uso en SITOR | Limitación reconocida |
| :--- | :--- | :--- | :--- |
| Multilingual Customer Support Tickets (Kaggle, T. Bueck) | Tickets de soporte con asunto, cuerpo de texto, idioma, cola/departamento (queue), tipo y prioridad | `queue` + `type` + `priority` se combinan como proxy de la tripleta Tipo/Subtipo/Detalle del CRM de telco | Es un dataset multisector (no específico de telecomunicaciones) y con una distribución de clases distinta a la de un CRM real de un BPΟ. |

#### 3.2 Adaptación al dominio y Estrategia de Idioma (Experimento A/B)
* **Filtrado de dominio:** Filtrado de las categorías más cercanas a soporte técnico/telco (Technical Support, Product Support, IT Support) para aproximar la casuística de una operadora.
* **Limpieza base:** Limpieza, minúsculas, eliminación de PII visible, manejo de abreviaturas frecuentes del sector (ONT, router, APN, IMEI, etc.).
* **Actualización de Viabilidad (Test A/B de Idioma):** Tras el Análisis Exploratorio de Datos (EDA), se ha detectado un volumen críticamente bajo de tickets nativos en español. Por tanto, el PFM ejecutará una fase de experimentación dual mediante dos *notebooks* paralelos:
  1. Un entrenamiento de la arquitectura con el dataset masivo nativo en **inglés** para establecer un *baseline* de rendimiento NLP puro y viabilidad técnica de la arquitectura.
  2. Un entrenamiento evaluando una muestra **traducida automáticamente al español** mediante scripts de *Data Augmentation*, con el objetivo de comprobar la degradación semántica introducida por la traducción de jerga técnica.
  Los resultados empíricos dictarán qué idioma conformará el motor definitivo del MVP.

---

### 4. Arquitectura del MVP

#### 4.1 Núcleo: Motor NLP y Clasificación Jerárquica
El sistema procesa el texto libre del ticket para predecir la tripleta (aproximada como queue + type + priority en el dataset elegido).
* Preprocesado de texto: limpieza, normalización, tokenización con spaCy.
* Vectorización mediante TF-IDF como baseline, y embeddings (sentence-transformers) como segunda iteración, comparando ambos enfoques.
* Gestión del desequilibrio de clases mediante ajuste de pesos o SMOTE.
* Umbral de confianza operativa: por debajo de un umbral definido empíricamente, el ticket se marca para revisión humana en vez de validarse automáticamente.

#### 4.2 Extensión opcional: Copiloto RAG
Indexación de un subconjunto de tickets resueltos en una base vectorial (ChromaDB), recuperación de los casos más similares ante un ticket nuevo, y generación de una propuesta de resolución mediante un LLM (API de OpenAI u Ollama).

#### 4.3 Despliegue: API con FastAPI (Arquitectura de Verificación)
* **Input:** Microservicio REST que recibe vía JSON el texto libre del ticket **y la tripleta ya asignada por el CRM**.
* **Procesamiento:** El motor predice internamente la tripleta correspondiente al texto y la compara dinámicamente con la recibida en el input.
* **Output:** Devuelve un JSON con la **verificación** de la tipificación (correcta/incorrecta). Si es incorrecta, devuelve la tripleta predicha como sugerencia de corrección, junto al nivel de confianza.
* Documentación automática vía OpenAPI/Swagger.

---

### 5. Plan de Evaluación: Qué se Mide y Cómo
1. Split train/validation/test estratificado por clase.
2. Métricas por clase: precisión, recall y F1, con especial atención a las clases minoritarias.
3. Comparación de al menos dos modelos para justificar la elección final.
4. Análisis de la matriz de confusión para identificar qué pares de categorías se confunden más, conectándolo con la narrativa de negocio.
5. Si se implementa RAG: evaluación cualitativa con ejemplos de aciertos y fallos.

---

### 6. Viabilidad Comercial: de la Hipótesis a la PoC
#### 6.1 El MVP no es el producto final
SITOR es una demostración de viabilidad técnica sobre datos públicos. El valor real reside en la infraestructura de MLOps de reentrenamiento, que el PFM deja documentada como diseño arquitectónico.

#### 6.2 PoC propuesta para un eventual cliente (Trabajo futuro)
1. Extracción de un histórico acotado y anonimizado (ej. 20.000 tickets reales).
2. Reentrenamiento del motor NLP con la casuística local del cliente.
3. Evaluación contra tipificaciones manuales reales para estimar interceptación real.
4. Cálculo de ROI definitivo con costes reales del cliente.

---

### 7. Caso de Negocio Simulado y Metodología de ROI
Se construye un caso con supuestos explícitos anclados en datos del sector, distinguiéndolo con claridad de un ROI medido. **Todo número aquí es una simulación, no un resultado del PFM.**

#### 7.1 Supuestos del escenario
| Supuesto | Valor usado en la simulación | Origen |
| :--- | :--- | :--- |
| Volumen de tickets/mes | 50.000 | Hipótesis declarada (BPO medio) |
| Tasa de falsos escalados | 12% de los tickets de Nivel 1 | Hipótesis declarada conservadora |
| Coste de recontacto | 9 € por caso | Benchmark en contact centers |
| Coste/hora Back Office (España) | 13 €/hora coste empresa | Salario medio Glassdoor España |
| Tasa de interceptación | 60% detectados antes de escalar | Hipótesis declarada |

#### 7.2 Cálculo orientativo del ahorro (Rango)
Con 6.000 falsos escalados/mes y una interceptación del 60% (evita 3.600 retrabajos/mes):
* Ahorro por recontacto evitado: 3.600 x 9 € ≈ **32.400 €/mes**.
* Ahorro en tiempo (12 min/caso): 3.600 x 0,2 h x 13 €/h ≈ **9.360 €/mes**.
*(Rango de plausibilidad argumental: 9.000 - 32.000 €/mes).*

#### 7.3 Cómo se mediría el ROI real en producción
Periodo de control sin sistema activo -> Despliegue en *shadow mode* -> Test A/B activo. Solo con los datos de esta última fase el ROI deja de ser una simulación.

---

### 8. Visión de Producto: Evoluciones Futuras (Fuera del PFM)
* **Detección temprana de averías masivas:** Clustering semántico no supervisado sobre embeddings.
* **Priorización dinámica:** Modelo secundario de sentimiento y riesgo de churn.

---

### 9. Riesgos y Limitaciones Reconocidas
* **Brecha dominio público a privado:** Las métricas obtenidas no son extrapolables directamente a un CRM real de telco.
* **Riesgo del Idioma y Traducción Asistida:** El proyecto asume el riesgo de ejecutar un Test A/B reconociendo abiertamente que el uso de traducción automática para generar volumen en español introducirá ruido semántico en el pipeline NLP.
* **Umbral de confianza del 85%:** No se fija a priori; se calibrará empíricamente.
* **Supuestos del caso de negocio:** Son hipótesis declaradas (tasa 12%, interceptación 60%), no datos medidos.

---

### 10. Cronograma Orientativo
* **Semanas 1-2:** Selección y filtrado, EDA, Test A/B de idioma (Traducción vs. Nativo).
* **Semanas 3-5:** Preprocesado, baseline TF-IDF, modelo de embeddings, balanceo.
* **Semanas 6-7:** Evaluación comparativa, calibración de umbral, cierre del MVP.
* **Semanas 8-9:** Construcción de la API en FastAPI.
* **Semanas 10-11:** Módulo RAG (opcional) y dashboard.
* **Semana 12:** Redacción de la memoria y defensa.