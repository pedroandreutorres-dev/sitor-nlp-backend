# 02 - Selección de Idea y Datos Necesarios

## 1. Idea seleccionada
Tras evaluar las ideas iniciales, he decidido proponer una idea basada en mi experiencia profesional en soporte técnico: **SITOR (Sistema Inteligente de Triaje y Orquestación de Requerimientos)**.

**Problema que resuelve:** En el sector de *Business Process Outsourcing* (BPO), los agentes de soporte de Front Office clasifican incidencias en texto libre bajo extrema presión. Esta presión provoca errores frecuentes en la asignación de la "tripleta" (*Cola / Tipo / Prioridad*). Estos errores generan "falsos escalados" hacia los técnicos de Back Office (Nivel 2), lo que dispara los costes operativos y empeora el Tiempo Medio de Resolución (AHT).

**Solución planteada:** Propongo una arquitectura de Procesamiento de Lenguaje Natural (NLP) basada en *Deep Learning* (Transformers / RoBERTa). La solución actuará como un auditor en tiempo real. En lugar de automatizar todas las clasificaciones, el modelo evaluará su propia certidumbre estadística (Softmax) y aplicará un **sistema de umbrales de confianza**, interviniendo solo cuando su nivel de seguridad supere un límite predefinido.

**MVP del proyecto final:** El Producto Mínimo Viable (MVP) consistirá en el diseño de la arquitectura de un microservicio (FastAPI) que reciba incidencias y devuelva predicciones, acompañado de una simulación de un panel operativo (Streamlit). El sistema autocorregirá el ticket si la confianza es mayor o igual al 80% (escenario base), liberando capacidad operativa (FTEs).

---

## 2. Datos necesarios
Para desarrollar el motor NLP de SITOR, se necesita un corpus textual de tickets de soporte técnico con sus categorizaciones.

* **Variables o campos necesarios:** 
  * **(Imprescindible):** `body` (texto del cliente) y las etiquetas `queue`, `type`, `priority` (fusionadas en una `target_tripleta`).
  * **(Deseable):** `subject` (Asunto). Se fusionará con el cuerpo para crear la variable predictora `full_text`.
* **Nivel de granularidad:** Por ticket individual.
* **Profundidad histórica:** Volumen consolidado de eventos ya resueltos. No es serie temporal.
* **Volumen aproximado:** Tras depurar el idioma (solo inglés), sanear clases minoritarias (< 30 muestras) y aplicar una **deduplicación estricta** para evitar *Data Leakage*, el corpus útil de entrenamiento se sitúa en torno a **18.000 registros únicos**, abarcando **90 clases operativas** (88 reales + 2 sumideros).

---

## 3. Fuentes de datos previstas
* **Fuente concreta:** Dataset público *"Customer IT Support Ticket Dataset"* publicado en Kaggle por Tobias Bueck.
* **Enlace:** [https://www.kaggle.com/datasets/tobiasbueck/customer-it-support-ticket-dataset](https://www.kaggle.com/datasets/tobiasbueck/customer-it-support-ticket-dataset)
* **Formato:** CSV/Parquet.
* **Estabilidad y Riesgos:** La fuente es estática y estable. El principal riesgo inicial era el alto solapamiento (24% de duplicados) entre particiones, el cual ya ha sido mitigado mediante una purga (drop_duplicates) en la capa Silver para garantizar una validación cruzada y un *Hold-out* completamente estancos.

---

## 4. Consideraciones de privacidad y protección de datos
* Los datos proceden de un repositorio abierto (Kaggle) y ya han sido ofuscados en su origen. 
* Nombres propios, IPs, contraseñas o datos de facturación fueron sustituidos por tokens o enmascarados antes de su publicación.
* El proyecto no entraña ningún riesgo de RGPD y los datos pueden usarse de forma segura.

---

## 5. Viabilidad inicial del proyecto
* **Obtención de datos:** Viabilidad total (dataset ya descargado).
* **Calidad de información:** Alta, aunque ha requerido un trabajo de limpieza taxonómica y deduplicación para asegurar la validez del modelo.
* **Desarrollo realista:** Completamente viable. La evolución desde modelos *Baseline* (Random Forest) hacia arquitecturas densas (RoBERTa en Colab) está garantizada.
* **Riesgos:** El principal riesgo técnico era la falta de memoria al intentar entrenar arquitecturas locales, el cual se ha sorteado migrando el entrenamiento a instancias GPU en Google Cloud (Colab).
