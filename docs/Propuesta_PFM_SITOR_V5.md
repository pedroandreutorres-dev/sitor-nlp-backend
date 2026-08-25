# PROPUESTA DE PROYECTO DE FIN DE MÁSTER (PFM)
## SITOR
**Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias**

| Programa | Área temática | Tipo de entrega | Versión |
| :--- | :--- | :--- | :--- |
| Máster en Data Science & IA - Evolve Academy | NLP, LLMs y arquitecturas RAG, MLOps | MVP individual con datos públicos + plan de validación con datos reales (PoC) | V6 - Consolidación del Enrutamiento por Tripleta Completa |

> **Nota sobre esta versión**
> Este documento define el alcance final del proyecto SITOR, enfocado en resolver el problema complejo de negocio: la predicción simultánea de la Tripleta completa del CRM (Cola + Tipo + Prioridad). Se asume una arquitectura multi-clase extrema para maximizar el ROI de automatización, diseñada de forma agnóstica para escalar a cualquier taxonomía empresarial.

---

### 1. Resumen Ejecutivo y Justificación de Negocio
En el sector de Business Process Outsourcing (BPO) y en las grandes compañías de telecomunicaciones, la gestión eficiente de incidencias en los canales de soporte es un factor crítico de coste y de satisfacción del cliente. La clasificación inicial de los tickets recae habitualmente en agentes de Front Office (Nivel 1), que operan bajo estrictas métricas de tiempo de operación (TMO). Esa presión, sumada a la ambigüedad del lenguaje del cliente, provoca errores en la tipificación manual de la "tripleta" (Tipo, Subtipo, Detalle) del CRM. 

Los errores de tipificación derivan en falsos escalados hacia el Back Office (Nivel 2), que consume recursos técnicos costosos en identificar el error y devolver el caso a la cola correcta. SITOR aborda esta ineficiencia combinando procesamiento de lenguaje natural (NLP) e Inteligencia Artificial para automatizar la auditoría de enrutamiento. 

**Objetivo principal de negocio:** Predecir de forma íntegra la Tripleta de clasificación (Queue, Type, Priority) para automatizar el 100% del enrutamiento inicial.

---

### 2. Alcance del PFM: MVP, Extensión Opcional y Fuera de Alcance

| Nivel | Contenido | Compromiso |
| :--- | :--- | :--- |
| **MVP (núcleo entregable)** | Motor de clasificación multi-clase de alta dimensionalidad + microservicio FastAPI + evaluación con métricas reales sobre dataset público | Innegociable. Es lo que se defiende con resultados. |
| **Extensión (si el calendario lo permite)** | Copiloto RAG sobre el mismo histórico, y un dashboard mínimo de KPIs técnicos | Deseable, no crítico para aprobar. |
| **Fuera de alcance (visión de producto)** | Clustering de averías masivas, priorización por churn/sentimiento, PoC con CRM real | Se documentan como trabajo futuro, sin construirse. |

---

### 3. Estrategia de Datos: Un Dataset Concreto, no una Promesa
Un PFM debe partir de un dataset identificado desde el día uno.

#### 3.1 Dataset base seleccionado
| Nombre | Contenido | Uso en SITOR | Limitación reconocida |
| :--- | :--- | :--- | :--- |
| Multilingual Customer Support Tickets (Kaggle) | Tickets de soporte con asunto, cuerpo de texto, idioma, cola (queue), tipo y prioridad | `queue` + `type` + `priority` se combinan para simular la complejidad de un árbol de decisión de un CRM real. | Es un dataset multisector y con una distribución de clases distinta a la de un CRM real de un BPΟ. |

#### 3.2 Adaptación al dominio y Estrategia de Idioma (Experimento A/B)
* **Filtrado de dominio:** Filtrado de las categorías más cercanas a soporte técnico/telco.
* **Limpieza base:** Limpieza, minúsculas, eliminación de PII visible.
* **Experimento de Idioma:** Entrenamiento de la arquitectura con el dataset nativo en **inglés**, y un entrenamiento paralelo evaluando una muestra **traducida automáticamente al español** para medir la degradación semántica.

---

### 4. Arquitectura del MVP

#### 4.1 Núcleo: Clasificación Multi-Clase de Tripleta
El sistema procesa el texto concatenado (Asunto + Cuerpo) del ticket para predecir la tripleta exacta del CRM.
* Preprocesado de texto: limpieza, normalización.
* Vectorización: TF-IDF (10.000 características).
* Gestión del desequilibrio de clases extremo mediante SMOTE (Synthetic Minority Over-sampling Technique).
* Bake-Off algorítmico: Comparativa de Regresión Logística, Random Forest y Gradient Boosting para determinar el modelo óptimo en escenarios de alta dimensionalidad de clases.

#### 4.2 Despliegue: API con FastAPI
* **Input:** Microservicio REST que recibe el texto libre del ticket y la tripleta pre-asignada por el agente humano.
* **Output:** Devuelve la verificación (correcta/incorrecta). Si es incorrecta, devuelve la predicción de la IA como sugerencia.

---

### 5. Plan de Evaluación: Qué se Mide y Cómo
1. Split train/test estratificado por todas las clases combinadas generadas.
2. Métricas por clase: F1-Macro como indicador de inteligencia general.
3. Evaluación quirúrgica de la "Clase Crítica": Recall y F1 en averías masivas (Service Outages).
4. Tiempos de Entrenamiento y Latencia de Inferencia (MLOps) para justificar viabilidad en producción.

---

### 6. Viabilidad Comercial y Caso de Negocio Simulado
Se construye un caso con supuestos explícitos para ilustrar el ROI:
* Volumen de tickets/mes: 50.000.
* Tasa de falsos escalados: 12% (6.000 errores/mes).
* Coste de retrabajo por error: 9€ a 13€ (tiempo de Back Office + recontacto).
* **Ahorro simulado:** Entre 9.000€ y 32.000€ mensuales si la IA intercepta un 60% de los errores.

---

### 7. Riesgos y Limitaciones Reconocidas
* **Riesgo de Alta Dimensionalidad Combinatoria:** Al combinar las variables del CRM, el número de clases se dispara. El volumen acotado del dataset (16k tickets útiles en inglés) distribuido entre un alto número de clases genera un reto estadístico crítico. Se mitigará seleccionando arquitecturas tolerantes a la dimensionalidad dispersa y aplicando SMOTE a las combinaciones infrarrepresentadas.
* **Ruido Semántico:** La traducción al español introducirá ruido en la jerga técnica.
