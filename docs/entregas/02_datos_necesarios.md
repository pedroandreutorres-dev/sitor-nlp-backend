# 02 - Selección de Idea y Datos Necesarios

## 1. Idea seleccionada
Tras evaluar las ideas iniciales planteadas en la primera entrega, he modificado el enfoque. Inicialmente, la intención era desarrollar un proyecto de ciberseguridad con la empresa de un excompañero, pero ante la falta de respuesta y la **imposibilidad de conseguir datos reales de empresa**, he decidido proponer una **idea nueva** basada en mi experiencia profesional de 16 años en soporte técnico Nivel 2 y Back Office: **SITOR (Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias)**.

**Problema que resuelve:** En el sector de *Business Process Outsourcing* (BPO) y grandes compañías de telecomunicaciones, los agentes de soporte de Front Office (Nivel 1) trabajan bajo una inmensa presión de tiempo. Esta presión, sumada a la ambigüedad del lenguaje natural de los clientes, provoca frecuentes errores en la clasificación y tipificación manual de los tickets (la asignación de la "tripleta" en el CRM: *Cola / Tipo / Prioridad*). Estos errores generan "falsos escalados" hacia los técnicos de Back Office (Nivel 2) o hacia departamentos equivocados, lo que dispara los costes operativos, satura a los técnicos especializados y empeora drásticamente el Tiempo Medio de Resolución (AHT).

**Solución planteada:** Propongo abordar este problema mediante una arquitectura de Procesamiento de Lenguaje Natural (NLP). La solución consistirá en un motor de clasificación jerárquica que actuará como un "auditor inteligente" en tiempo real. El proyecto queda planteado como una prueba de concepto para demostrar la viabilidad técnica, asumiendo que **en un entorno real de producción, el modelo siempre tendría que reentrenarse con los datos propios de la compañía que lo implemente**.

**MVP del proyecto final:** Atendiendo al *feedback* del tutor, el Producto Mínimo Viable (MVP) centrará su alcance estrictamente en **comprobar si es posible validar la tipificación de un ticket**. Presentaré un microservicio en FastAPI que recibirá el texto de una incidencia y la tripleta asignada por el humano. 
*Nota metodológica para la evaluación:* Dado que el dataset público solo contiene tipificaciones "correctas", la validación real de la API durante la defensa exigirá la **inyección de ruido sintético** (etiquetas erróneas deliberadas en el set de *Testing*) para poder evaluar y demostrar empíricamente la capacidad de intercepción del sistema ante un "falso escalado" simulado.

---

## 2. Datos necesarios
Para desarrollar el motor de clasificación NLP de SITOR, se necesita un corpus textual de tickets de soporte técnico con sus correspondientes categorizaciones.

* **Variables o campos necesarios:** 
  * `subject` y `body`: Se utilizará la concatenación de ambos campos (Asunto + Cuerpo) como variable independiente predictora principal, para maximizar el contexto semántico de entrada. *(Nota de desarrollo: Esta decisión de diseño es reciente y su implementación en código se encuentra actualmente pendiente de programar en los notebooks).*
  * `queue` (departamento/cola), `type` (tipo de problema) y `priority` (prioridad): Las variables objetivo que conformarán la "tripleta" a predecir.
  * `language`: Para filtrar y procesar el idioma de los tickets.
* **Nivel de granularidad:** Por ticket o incidencia individual. 
* **Profundidad histórica:** Volumen consolidado de eventos históricos ya resueltos. No se exige serie temporal.
* **Volumen aproximado (Ajuste realista):** Aunque el dataset público roza los 28.000 registros, el filtrado de dominios irrelevantes (ej. RRHH) y la necesaria segregación estricta por idioma para el modelo base (Inglés), nos dejará un **corpus útil de entrenamiento de ~16.000 registros**. Se somete a tutoría si este volumen es robusto para la cascada planteada.

---

## 3. Fuentes de datos previstas
* **Fuente concreta prevista:** Dataset público denominado *"Multilingual Customer Support Tickets"*, publicado en Kaggle por el autor T. Bueck. Su uso es la única alternativa viable ante la **imposibilidad de obtener datos internos reales** de una operadora por políticas de confidencialidad.
* **Accesibilidad:** Fuente abierta sin restricciones de pago ni NDA corporativos.
* **Histórico y Estabilidad:** Dataset consolidado, inmutable y estable.
* **Riesgos detectados y asumidos:**
  * **Limitación estructural (El más crítico):** Como se acordó en tutoría, este dataset público **no permite demostrar directamente que un ticket fue mal escalado**, ya que carece del ciclo de vida (tipificación inicial errónea, corrección y destino final). El proyecto asume que no validará un ahorro monetario real (ROI), sino que será estrictamente una **prueba de viabilidad técnica sobre datos similares**.
  * **Estrategia de Traducción (Test A/B):** El volumen de tickets nativos en español es residual. Para evaluar la viabilidad del modelo en español sin incurrir en bloqueos (*rate limits*) ni costes de APIs comerciales (ej. Google, DeepL), el *Data Augmentation* se realizará en local instanciando **modelos Open Source ligeros de traducción desde HuggingFace** (ej. Helsinki-NLP).

---

## 4. Consideraciones de privacidad y protección de datos
* Al tratarse de un dataset público (Kaggle), los datos ya han sido ofuscados previamente por sus autores y no deberían incluir información personal identificable (PII) directa.
* A pesar de ello, y debido a la naturaleza imprevisible del texto libre (`body`), el *pipeline* de preprocesado incluirá un saneamiento mediante expresiones regulares (Regex). Esta limpieza se aborda desde un enfoque de esfuerzo razonable (*best-effort*) enfocado en neutralizar formatos estandarizados (correos electrónicos y números de teléfono), asumiendo que las vulnerabilidades críticas ya fueron resueltas en origen.

---

## 5. Viabilidad inicial del proyecto
* **¿Parece viable obtener los datos necesarios?** Sí, los datos ya están descargados y bajo custodia local.
* **¿La información tiene suficiente calidad?** La calidad es suficiente para una prueba de viabilidad (MVP), asumiendo que la distribución semántica y de clases no será idéntica a la de un BPO real.
* **¿Puede desarrollarse durante el curso?** Sí. Se ha acotado el alcance innegociable a la validación algorítmica (MVP), desplazando desarrollos complejos como el Copiloto RAG o el cálculo de ROI fuera del marco principal de entrega.
* **Riesgo crítico de la Arquitectura en Cascada:** Al contar con un corpus base acotado (~16.000 tickets), existe el riesgo de que el volumen sea insuficiente para sostener 3 niveles de predicción encadenada, provocando escasez crítica de muestras en las clases profundas. Para mitigarlo:
  * Se aplicarán técnicas de sobremuestreo sintético como **SMOTE** (*Synthetic Minority Over-sampling Technique*) tras la vectorización.
  * Si el rendimiento colapsa a pesar del SMOTE, se plantean tres escenarios (sujetos a opinión del tutor):
    * **Plan A:** Cascada completa (`Queue` > `Type` > `Priority`).
    * **Plan B:** Recortar el MVP al Nivel 2 (`Queue` + `Type`).
    * **Plan C:** Predecir exclusivamente el Nivel 1 (`Queue`).
