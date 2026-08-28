# 02 - Selección de Idea y Datos Necesarios

## 1. Idea seleccionada
Tras evaluar las ideas iniciales planteadas en la primera entrega, he modificado el enfoque. Inicialmente, la intención era desarrollar un proyecto en la empresa de un excompañero, pero ante la falta de respuesta y la **imposibilidad de conseguir datos reales de empresa**, he decidido proponer una **idea nueva** basada en mi experiencia profesional de 16 años en soporte técnico Nivel 2 y Back Office: **SITOR (Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias)**.

**Problema que resuelve:** En el sector de *Business Process Outsourcing* (BPO) y grandes compañías de telecomunicaciones, los agentes de soporte de Front Office (Nivel 1) trabajan bajo una inmensa presión de tiempo. Esta presión, sumada a la ambigüedad del lenguaje natural de los clientes, provoca frecuentes errores en la clasificación y tipificación manual de los tickets (la asignación de la "tripleta" en el CRM: *Cola / Tipo / Prioridad*). Estos errores generan "falsos escalados" hacia los técnicos de Back Office (Nivel 2) o hacia departamentos equivocados, lo que dispara los costes operativos, satura a los técnicos especializados y empeora drásticamente el Tiempo Medio de Resolución (AHT).

**Solución planteada:** Propongo abordar este problema mediante una arquitectura de Procesamiento de Lenguaje Natural (NLP). La solución consistirá en un motor de clasificación jerárquica que actuará como un "auditor inteligente" en tiempo real. El proyecto queda planteado como una prueba de concepto para demostrar la viabilidad técnica, asumiendo que **en un entorno real de producción, el modelo siempre tendría que reentrenarse con los datos propios de la compañía que lo implemente**.

**MVP del proyecto final:** El Producto Mínimo Viable (MVP) centrará su alcance estrictamente en **actuar como motor de auto-enrutamiento basado en umbrales de confianza (*Confidence Thresholding*)**. Presentaré un microservicio en FastAPI que recibirá listados JSON de incidencias. Si el modelo contradice la tipificación humana con una confianza mayor o igual al 85%, el sistema auto-corregirá el ticket. Si la confianza está entre 60% y 85%, lo derivará a auditoría manual. 
*Nota metodológica para la evaluación:* Dado que el dataset público solo contiene tipificaciones "correctas", la validación real de la API durante la defensa exigirá la **inyección de ruido sintético** (etiquetas erróneas deliberadas en el set de *Testing*) para poder evaluar y demostrar empíricamente la capacidad de intercepción del sistema ante un "falso escalado" simulado.

---

## 2. Datos necesarios
Para desarrollar el motor de clasificación NLP de SITOR, se necesita un corpus textual de tickets de soporte técnico con sus correspondientes categorizaciones.

* **Variables o campos necesarios:** 
  * **(Imprescindible):** `body` (texto del cliente) y las etiquetas `queue`, `type`, `priority` (la tripleta objetivo). Sin estos campos, el modelo matemático no tiene ni contexto predictivo ni verdad fundamental (Ground Truth).
  * **(Deseable):** `subject` (Asunto). Aporta un contexto semántico inicial valiosísimo, pero si falta, el sistema puede imputarlo con el valor estático "No Subject" sin que la arquitectura algorítmica colapse.
  * `language`: Para filtrar y procesar el idioma de los tickets.
* **Nivel de granularidad:** Por ticket o incidencia individual. 
* **Profundidad histórica:** Volumen consolidado de eventos históricos ya resueltos. No se exige serie temporal.
* **Volumen aproximado (Ajuste realista):** Aunque el dataset público roza los 28.000 registros, el filtrado de dominios irrelevantes (ej. RRHH) y la necesaria segregación estricta por idioma para el modelo base (Inglés), me dejará un **corpus útil de entrenamiento de ~16.000 registros**. Someto a tutoría si este volumen es robusto para la cascada planteada.

---

## 3. Fuentes de datos previstas
* **Fuente concreta prevista:** Dataset público denominado *"Customer IT Support Ticket Dataset"*, publicado en Kaggle por el autor Tobias Bueck (T. Bueck). 
  * **Enlace:** [https://www.kaggle.com/datasets/tobiasbueck/customer-it-support-ticket-dataset](https://www.kaggle.com/datasets/tobiasbueck/customer-it-support-ticket-dataset)
  * **Formato esperado:** Archivos estructurados en formato `CSV` (Valores separados por comas).
* **Accesibilidad:** Fuente abierta sin restricciones de pago ni NDA corporativos.
* **Histórico y Estabilidad:** Dataset consolidado, inmutable y estable.
* **Riesgos detectados y asumidos:**
  * **Limitación estructural (El más crítico):** Este dataset público **no permite demostrar directamente que un ticket fue mal escalado en su origen**, ya que carece del ciclo de vida (tipificación inicial errónea, corrección y destino final). Sin embargo, el proyecto **sí asume y demuestra un ahorro monetario real (ROI)**: la capacidad de la API para auto-enrutar correctamente un ticket (o interceptar uno dudoso) se traduce directamente en un ahorro de horas-hombre de técnicos de Nivel 1 y Nivel 2, validando tanto la viabilidad técnica como el impacto económico.
  * **Estrategia de Traducción (Test A/B):** El volumen de tickets nativos en español es residual. Tras ejecutar un Test A/B exhaustivo traduciendo el dataset con HuggingFace (Helsinki-NLP), se ha demostrado empíricamente que la traducción inyecta ruido semántico, por lo que el modelo nativo en inglés (F1-Macro superior) se ha consolidado como la base tecnológica definitiva.

---

## 4. Consideraciones de privacidad y protección de datos
* Al tratarse de un dataset público (Kaggle), los datos ya han sido ofuscados previamente por sus autores y no deberían incluir información personal identificable (PII) directa.
* A pesar de ello, y debido a la naturaleza imprevisible del texto libre (`body`), el *pipeline* de preprocesado incluirá un saneamiento mediante expresiones regulares (Regex). Esta limpieza se aborda desde un enfoque de esfuerzo razonable (*best-effort*) enfocado en neutralizar formatos estandarizados (correos electrónicos y números de teléfono), asumiendo que las vulnerabilidades críticas ya fueron resueltas en origen.

---

## 5. Viabilidad inicial del proyecto
* **¿Parece viable obtener los datos necesarios?** Sí, los datos ya están descargados y bajo custodia local.
* **¿La información tiene suficiente calidad?** La calidad es suficiente para una prueba de viabilidad (MVP), asumiendo que la distribución semántica y de clases no será idéntica a la de un BPO real.
* **¿Qué alternativa tendríais si la fuente principal no funciona (los datos no permiten crear el modelo)?** Si la calidad semántica de los ~16.000 tickets útiles hubiera sido insuficiente para predecir las 84 clases combinadas de la "Tripleta", la alternativa (Plan B) habría consistido en simplificar el alcance de la variable objetivo, pasando a predecir únicamente el nivel macro (`queue` - 5 clases). Sin embargo, **no he necesitado ejecutar esta alternativa**, ya que las pruebas empíricas en las fases de modelado han demostrado que el dataset posee suficiente riqueza matemática para sostener la predicción compleja de la tripleta completa.
* **¿Puede desarrollarse durante el curso?** Sí. Se ha acotado el alcance innegociable a la validación algorítmica (MVP), desplazando desarrollos complejos como el Copiloto RAG o el cálculo de ROI fuera del marco principal de entrega.
* **Riesgo crítico de la Alta Dimensionalidad Combinatoria:** Al contar con un corpus base acotado (~16.000 tickets), existe el riesgo de que el volumen sea insuficiente al segmentarse en múltiples combinaciones de clases. Para mitigarlo se aplicarán técnicas de sobremuestreo sintético como **SMOTE** (*Synthetic Minority Over-sampling Technique*) tras la vectorización, garantizando un entrenamiento equitativo para el objetivo matemático de predecir de forma simultánea la tripleta completa (`Queue` + `Type` + `Priority`).
