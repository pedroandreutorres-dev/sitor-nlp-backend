# SITOR - Propuesta de PFM
**Evolve Academy Data Science & IA**

## PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
**SITOR: Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias**

| Concepto | Detalle |
| :--- | :--- |
| **Programa** | Máster en Data Science & IA - Evolve Academy |
| **Área temática** | NLP, LLMs y arquitecturas RAG, MLOps |
| **Tipo de entrega** | MVP individual con datos públicos + plan de validación con datos reales (PoC) |
| **Versión** | V2 - Alcance acotado a MVP defendible |

> **Nota sobre esta versión:** Este documento revisa la propuesta original de SITOR para ajustarla a lo que un Trabajo de Fin de Máster individual puede ejecutar y defender en el tiempo disponible: un dataset público identificado desde el inicio, un alcance de MVP (clasificación + API) con la arquitectura RAG como extensión opcional, un caso de negocio simulado con supuestos explícitos y citados (Sección 7), y un tratamiento honesto de las limitaciones de generalización a entornos empresariales reales.

---

## 1. Resumen Ejecutivo y Justificación de Negocio

En el sector de Business Process Outsourcing (BPO) y en las grandes compañías de telecomunicaciones, la gestión eficiente de incidencias en los canales de soporte es un factor crítico de coste y de satisfacción del cliente. La clasificación inicial de los tickets recae habitualmente en agentes de Front Office (Nivel 1), que operan bajo estrictas métricas de tiempo de operación (TMO). Esa presión, sumada a la ambigüedad del lenguaje del cliente, provoca errores en la tipificación manual de la "tripleta" (Tipo, Subtipo, Detalle) del CRM.

Los errores de tipificación derivan en falsos escalados hacia el Back Office (Nivel 2), que consume recursos técnicos costosos en identificar el error y devolver el caso a la cola correcta. SITOR aborda esta ineficiencia combinando procesamiento de lenguaje natural (NLP) e Inteligencia Artificial Generativa para automatizar la auditoría de enrutamiento y acelerar la resolución de incidencias.

* **Objetivo principal de negocio:** reducir los falsos escalados, optimizar el tiempo medio de resolución (AHT) del Back Office mediante asistencia contextual, y dotar a la dirección de métricas de impacto económico.

### Encuadre honesto del proyecto
Esta versión del documento distingue de forma explícita entre lo que el PFM construye y valida con datos públicos (el MVP) y lo que se plantea como hipótesis de despliegue comercial, pendiente de validar con datos reales de una empresa (la PoC). El primero es defendible con resultados; el segundo es una propuesta razonada, no un resultado.

---

## 2. Alcance del PFM: MVP, Extensión Opcional y Fuera de Alcance

La propuesta original planteaba cuatro fases con el mismo nivel de profundidad. Para un trabajo individual con un calendario de máster, ese alcance equivale a un roadmap de producto de varios meses con equipo, no a un PFM. Se redefine el alcance en tres niveles:

| Nivel | Contenido | Compromiso |
| :--- | :--- | :--- |
| **MVP (núcleo entregable)** | Motor de clasificación jerárquica de tripletas (Fase 1) + microservicio FastAPI (Fase 3) + evaluación con métricas reales sobre dataset público | **Innegociable.** Es lo que se defiende con resultados. |
| **Extensión (si el calendario lo permite)** | Copiloto RAG (Fase 2) sobre el mismo histórico, y un dashboard mínimo de KPIs técnicos (sin ROI en euros) | **Deseable**, no crítico para aprobar. |
| **Fuera de alcance (visión de producto)** | Cálculo de ROI en €, clustering de averías masivas, priorización por churn/sentimiento, PoC con CRM real | Se documentan como trabajo futuro, **sin construirse**. |

Este recorte no reduce la ambición del proyecto: concentra el esfuerzo donde se puede demostrar con números reales (precisión del clasificador, tiempo de respuesta de la API), en lugar de repartirlo en cuatro frentes que quedarían a medio terminar.

---

## 3. Estrategia de Datos: Un Dataset Concreto, no una Promesa

La propuesta original mencionaba "datasets de Kaggle o UCI" y "generación de datos sintéticos" en términos genéricos, sin nombrar ninguno. Esa ambigüedad es uno de los puntos que un tribunal exigente señalaría primero: un PFM debe partir de un dataset identificado desde el día uno, no de una categoría de datasets.

### 3.1 Dataset base seleccionado

| Atributo | Detalle |
| :--- | :--- |
| **Nombre** | Multilingual Customer Support Tickets (Kaggle, T. Bueck) |
| **Contenido** | Tickets de soporte con asunto, cuerpo de texto, idioma, cola/departamento (queue), tipo y prioridad; incluye una porción de tickets en español |
| **Uso en SITOR** | "queue" + "type" + "priority" se combinan como proxy de la tripleta Tipo/Subtipo/Detalle del CRM de telco |
| **Limitación reconocida** | Es un dataset multisector (no específico de telecomunicaciones) y con una distribución de clases distinta a la de un CRM real de un BPO. No sustituye una validación con datos reales. |

### 3.2 Adaptación al dominio de telecomunicaciones

* Filtrado de las categorías más cercanas a soporte técnico/telco (Technical Support, Product Support, IT Support) para aproximar la casuística de una operadora.
* Normalización de texto en español: limpieza, minúsculas, eliminación de PII visible, manejo de abreviaturas frecuentes del sector (ONT, router, APN, IMEI, etc., mediante diccionario propio).
* Si el volumen en español resulta insuficiente tras el filtrado, se documentará explícitamente el tamaño final de la muestra y se valorará complementar con traducción asistida de una porción del subconjunto en inglés, dejando trazabilidad de qué texto es original y cuál traducido.

**Por qué esto es mejor que la versión anterior:**
La Sección 4 original defendía que un modelo entrenado con datos públicos no generaliza a un CRM privado, y a la vez la Sección 6 proponía entrenar precisamente con datos públicos sin reconocerlo como la misma limitación. Aquí se nombra el dataset, se reconoce la limitación desde el principio y se evita la contradicción.

---

## 4. Arquitectura del MVP

### 4.1 Núcleo: Motor NLP y Clasificación Jerárquica
El sistema procesa el texto libre del ticket para predecir la tripleta (aproximada como queue + type + priority en el dataset elegido).

* Preprocesado de texto en español: limpieza, normalización, tokenización con spaCy.
* Vectorización mediante TF-IDF como baseline, y embeddings (sentence-transformers) como segunda iteración, comparando ambos enfoques con métricas.
* Gestión del desequilibrio de clases mediante ajuste de pesos de clase y, si es necesario, SMOTE sobre el espacio de embeddings.
* Umbral de confianza operativa: por debajo de un umbral definido empíricamente (no fijado a priori en 85% sin evidencia), el ticket se marca para revisión humana en vez de auto-enrutarse.

### 4.2 Extensión opcional: Copiloto RAG
Si el calendario lo permite tras cerrar el núcleo: indexación de un subconjunto de tickets resueltos (campo de respuesta del agente, presente en el dataset) en una base vectorial (ChromaDB), recuperación de los casos más similares ante un ticket nuevo, y generación de una propuesta de resolución mediante un LLM (API de OpenAI o modelo open-source vía Ollama, según presupuesto disponible para el PFM).

### 4.3 Despliegue: API con FastAPI
* Microservicio REST que recibe el texto del ticket vía JSON y devuelve tripleta predicha, nivel de confianza y, si aplica, sugerencia del copiloto.
* Documentación automática vía OpenAPI/Swagger, generada por FastAPI.
* Diseño desacoplado del CRM (integración vía webhook), manteniéndolo como diseño de interfaz, no como integración real con ningún CRM concreto.

| Componente | Descripción | Tecnologías |
| :--- | :--- | :--- |
| **Motor de clasificación** | Predicción de tripleta con control de umbral de incertidumbre | Python, scikit-learn, spaCy, XGBoost |
| **Módulo RAG (opcional)** | Búsqueda semántica de soluciones previas y síntesis con LLM | LangChain, ChromaDB, OpenAI API / Ollama |
| **Infraestructura API** | Endpoints asíncronos para predicción en tiempo real | FastAPI, Uvicorn, Pydantic |
| **Evaluación / BI mínimo** | Tabla y gráficas de métricas (F1 por clase, matriz de confusión) | Pandas, Matplotlib/Plotly |

---

## 5. Plan de Evaluación: Qué se Mide y Cómo

Esta sección no existía como tal en la propuesta original, que hablaba de "métricas de negocio" sin especificar ninguna cifra de referencia ni metodología de cálculo. Se define aquí lo mínimo que un tribunal esperará ver con resultados reales:

1. Split train/validation/test estratificado por clase, dado el desequilibrio esperado.
2. Métricas por clase: precisión, recall y F1, con especial atención a las clases minoritarias (las más sensibles a falsos escalados).
3. Comparación de al menos dos modelos (p. ej. TF-IDF + XGBoost vs. embeddings + clasificador lineal) para justificar la elección final.
4. Análisis de la matriz de confusión para identificar qué pares de categorías se confunden más, conectándolo con la narrativa de negocio (qué tipo de error es más costoso escalar).
5. Si se implementa el copiloto RAG: evaluación cualitativa con una muestra de casos (no exhaustiva), documentando ejemplos de aciertos y de fallos del LLM.

---

## 6. Viabilidad Comercial: de la Hipótesis a la PoC

Se mantiene el razonamiento original sobre la falacia del "modelo universal", pero se reformula como lo que es: una hipótesis de trabajo a validar en el futuro, no una garantía del proyecto.

### 6.1 El MVP no es el producto final
SITOR, tal como se construye en el PFM, es una demostración de viabilidad técnica sobre datos públicos. El argumento de que el valor real reside en la infraestructura de MLOps (el pipeline de reentrenamiento) y no en los pesos del modelo es válido como tesis, pero exige reconocer que el PFM no construye ni ejecuta ese pipeline de reentrenamiento con datos de cliente real, sino que lo deja documentado como diseño.

### 6.2 PoC propuesta para un eventual cliente (trabajo futuro, no parte del PFM)
1. Extracción de un histórico acotado y anonimizado (ej. 20.000 tickets de los últimos 6 meses).
2. Reentrenamiento del motor NLP con la casuística local del cliente.
3. Evaluación contra las tipificaciones manuales reales para estimar la tasa de interceptación de falsos escalados.
4. Solo en esta fase, con datos reales y costes reales del cliente, tendría sentido calcular un ROI en euros; calcularlo antes, sobre datos sintéticos, produciría una cifra sin respaldo.

---

## 7. Caso de Negocio Simulado y Metodología de ROI

Esta sección responde directamente a la naturaleza de negocio exigida al PFM. Se construye un caso de negocio con supuestos explícitos, anclados en datos públicos del sector (citados), y se distingue con claridad de un ROI medido. El objetivo es demostrar capacidad de razonamiento financiero aplicado a un proyecto de IA, sin disfrazar una estimación de una medición real.

> **Regla de esta sección:** Todo número que aparece aquí es una simulación con supuestos declarados, no un resultado del PFM. Cada supuesto indica su origen: una referencia de mercado citada, o una hipótesis razonable marcada como tal. Esta distinción se mantiene visible para que el caso de negocio sea creíble en lugar de inflado.

### 7.1 Supuestos del escenario

| Supuesto | Valor usado en la simulación | Origen |
| :--- | :--- | :--- |
| **Volumen de tickets/mes** | 50.000 (BPO/telco de tamaño medio) | Hipótesis declarada, orden de magnitud razonable para el sector |
| **Tasa de falsos escalados** | 12% de los tickets de Nivel 1 | Hipótesis declarada (no existe benchmark público de misrouting; se usa un valor conservador dentro del rango plausible) |
| **Coste de un recontacto/retrabajo** | 9 € por caso (rango de mercado 7-12 €) | Benchmark de coste de recontacto en contact centers |
| **Coste/hora agente Back Office (España)** | 10 €/hora bruto + 30% cargas sociales ≈ 13 €/hora coste empresa | Salario medio de Backoffice/Soporte Nivel 2 en España (Glassdoor) |
| **Tasa de interceptación del modelo** | 60% de los falsos escalados detectados antes de llegar a Nivel 2 | Hipótesis declarada, conservadora frente al umbral de confianza calibrado en el MVP (Sección 4.1) |

### 7.2 Cálculo orientativo del ahorro mensual

* Con los supuestos anteriores: 50.000 tickets/mes x 12% de error = 6.000 falsos escalados/mes.
* Si SITOR intercepta el 60% antes de llegar a Nivel 2, evita 3.600 retrabajos/mes.
* Ahorro por coste de recontacto evitado: 3.600 x 9 € ≈ 32.400 €/mes.
* Ahorro alternativo en horas de Back Office (si se mide en tiempo en vez de coste de recontacto): asumiendo 12 minutos de retrabajo por caso mal escalado, 3.600 x 0,2 h x 13 €/h ≈ 9.360 €/mes.

Las dos cifras se presentan juntas, no sumadas, porque miden el mismo fenómeno desde dos ángulos distintos (coste de recontacto vs. coste de horas-agente) y combinarlas sería contar el ahorro dos veces. La memoria del PFM debe presentar el rango (9.000-32.000 €/mes según el método de cálculo) en vez de una cifra única, dejando claro que es una banda de plausibilidad, no una previsión.

### 7.3 Cómo se mediría el ROI real (más allá del PFM)
Esto es lo que de verdad demuestra criterio de negocio: no inventar el número final, sino especificar cómo se obtendría con datos reales de producción.

1. Periodo de control (4-8 semanas) midiendo la tasa real de falsos escalados actual del cliente, sin el sistema activo.
2. Despliegue de SITOR en modo sombra (shadow mode): el modelo predice pero no enruta, comparando su predicción contra la decisión real del agente para medir precisión real sobre tráfico en vivo.
3. Activación parcial (A/B test por cola o por turno) midiendo la diferencia real en tasa de escalado, AHT de Back Office y tasa de reapertura entre el grupo con SITOR activo y el grupo de control.
4. Solo con esos datos de producción se sustituyen los supuestos de la tabla 7.1 por cifras reales del cliente, y el ROI deja de ser una simulación.

---

## 8. Visión de Producto: Evoluciones Futuras (Fuera del PFM)

Se conservan como visión de producto, igual que en la propuesta original, dejando explícito que no se implementan en el PFM y que dependen de datos reales de producción que el alcance académico no puede proporcionar.

### 8.1 Detección temprana de averías masivas (clustering semántico)
Pipeline no supervisado (HDBSCAN o K-Means sobre embeddings) que analizaría ventanas temporales de tickets entrantes para detectar concentraciones anómalas de quejas semánticamente similares y alertar de una posible avería masiva.

### 8.2 Priorización dinámica por sentimiento y riesgo de churn
Modelo secundario de análisis de sentimiento que inyectaría un factor de prioridad a tickets con frustración extrema, amenazas de baja o menciones a organismos reguladores, reordenando la cola de Back Office.

---

## 9. Riesgos y Limitaciones Reconocidas

Una sección que no existía en el documento original y que conviene incluir explícitamente, porque anticipar las objeciones del tribunal es parte de defender bien un PFM.

* **Brecha dominio público → dominio privado:** las métricas obtenidas con el dataset público no son extrapolables directamente a un CRM real de telco. Se presentan como cota de viabilidad técnica, no como cifra de producción.
* **Calidad del español en el dataset:** si el volumen en español resulta limitado tras filtrar por categorías de telco, se documentará el tamaño final y su impacto en la robustez de las métricas.
* **Coste de la API de LLM (si se implementa RAG):** se acotará el número de llamadas de evaluación y se considerará una alternativa local (Ollama) si el presupuesto es una restricción real.
* **Umbral de confianza del 85%:** no se fija a priori; se calibrará con la curva precisión-cobertura obtenida en validación y se justificará el valor final elegido.
* **Supuestos del caso de negocio (Sección 7):** la tasa de falsos escalados (12%) y la tasa de interceptación (60%) son hipótesis declaradas, no datos medidos. El rango de ahorro presentado es una banda de plausibilidad para argumentar el caso, no una previsión financiera comprometida.

---

## 10. Cronograma Orientativo

| Periodo | Tareas |
| :--- | :--- |
| **Semanas 1-2** | Selección y filtrado del dataset, análisis exploratorio, definición de la tripleta proxy |
| **Semanas 3-5** | Preprocesado, baseline TF-IDF, segundo modelo con embeddings, ajuste de desbalanceo |
| **Semanas 6-7** | Evaluación comparativa, calibración del umbral de confianza, cierre del MVP de clasificación |
| **Semanas 8-9** | Construcción de la API en FastAPI e integración con el modelo entrenado |
| **Semanas 10-11** | Si hay margen: módulo RAG (indexación + recuperación + generación) y dashboard mínimo de métricas |
| **Semana 12** | Redacción de la memoria, preparación de la defensa |

*Calendario orientativo a 12 semanas; debe ajustarse a la duración real del módulo de TFM de Evolve Academy, que conviene confirmar con la coordinación académica antes de fijar fechas internas.*

### Resumen del cambio respecto a la versión original
Mismo dominio de negocio y misma ambición de arquitectura, pero con un dataset nombrado desde el inicio, un alcance dividido en MVP / extensión / fuera de alcance, un plan de evaluación con métricas concretas, un caso de negocio simulado con supuestos citados y una metodología clara para medir el ROI real en producción, y una sección de riesgos que reconoce las limitaciones en vez de ocultarlas detrás del lenguaje comercial. Esto es lo que hace que el proyecto sea defendible, no solo presentable.