# Documentación del Análisis Exploratorio de Datos (EDA)
## Dataset: df_01 (`df_aa_dataset-tickets-multi-lang-5-2-50-version`)

Este documento recoge los hallazgos, la interpretación de negocio y las decisiones técnicas tomadas tras auditar las 16 columnas del primer dataframe (`df_01`).

---

## 1. El Bloque del Target (La Tripleta CRM)
Para simular la clasificación jerárquica de tres niveles (Tipo > Subtipo > Detalle) de un CRM de atención al cliente en una gran operadora (como Vodafone), validamos las columnas `queue`, `type` y `priority`.

### 1.1. Columna `queue` (Nivel 1 - Departamentos / Colas)
Presenta **10 valores únicos** con un desequilibrio de clases realista.

| Cola (Category) | Frecuencia | Enfoque para el MVP de SITOR |
| :--- | :--- | :--- |
| **Technical Support** | 4.737 | **Core Telco:** Soporte técnico tradicional (conexión, dispositivos). |
| **Product Support** | 3.073 | **Core Telco:** Problemas con servicios específicos. |
| **Customer Service** | 2.410 | **Core Telco:** Dudas generales, gestiones de línea. |
| **IT Support** | 1.942 | **Core Telco:** Soporte de sistemas, configuración. |
| **Billing and Payments** | 1.595 | **Core Telco:** Reclamaciones de facturas, cargos erróneos, cobros. |
| **Service Outages and Maintenance** | 664 | **Core Telco:** Averías masivas, caídas de red, router sin señal. |
| **Sales and Pre-Sales** | 513 | **Core Telco:** Contrataciones, consultas comerciales. |
| **Returns and Exchanges** | 820 | **Descartar:** Orientado a retail/e-commerce. Fuera de dominio. |
| **Human Resources** | 348 | **Descartar:** Gestión interna de empleados. Fuera de dominio. |
| **General Inquiry** | 236 | **Descartar:** Demasiado genérico, aporta ruido. |

> **Decisión Técnica:** Redefinimos el alcance del dominio. No nos limitamos solo a soporte técnico; mantendremos las colas de **Facturación, Reclamaciones y Atención al Cliente**. Esto refleja el ecosistema real de un contact center de telecomunicaciones, salvando volumen de datos y entrenando al modelo en fronteras semánticas complejas (ej. diferenciar una queja técnica de una queja por cobro).

### 1.2. Columna `type` (Nivel 2 - Naturaleza del Ticket)
Presenta **4 valores únicos** que se alinean perfectamente con las mejores prácticas de la metodología **ITIL** (gestión de servicios de TI):

* **Incident (6.571 casos):** Averías o interrupciones del servicio (ej. "el router no enciende").
* **Request (4.665 casos):** Peticiones de servicio (ej. "quiero activar el roaming").
* **Problem (3.397 casos):** Errores subyacentes o bugs repetitivos en el sistema.
* **Change (1.705 casos):** Solicitudes de modificación (ej. "quiero cambiar de tarifa").

### 1.3. Columna `priority` (Nivel 3 - Urgencia de la Gestión)
Presenta **3 valores únicos** y muestra una distribución notablemente equilibrada, ideal para el entrenamiento:
* **Medium:** 6.618 casos
* **High:** 6.346 casos
* **Low:** 3.374 casos

---

## 2. Auditoría del Texto Libre (Columna `body`)

Hemos analizado las métricas estadísticas de longitud y una muestra cualitativa de los textos del cuerpo del ticket en `df_01` para validar la calidad lingüística del dataset.

### 2.1. Análisis Estadístico (Longitud del Texto)
* **Longitud Media:** ~54 palabras por ticket (con una desviación estándar de 27).
* **Distribución:** El 50% de los tickets (mediana) tienen alrededor de 55 palabras, moviéndose la gran mayoría en un rango de entre 31 y 78 palabras.
* **Veredicto:** No nos enfrentamos a mensajes cortos tipo tweet, sino a correos estructurados de un tamaño mediano constante. Esto es óptimo para modelos basados en Transformers (como BERT o MiniLM), ya que los textos caben perfectamente dentro de su ventana de contexto estándar (512 tokens) sin necesidad de recortar información.

### 2.2. Auditoría Semántica (Calidad y Realismo del Lenguaje)
Tras extraer y analizar cualitativamente muestras de las colas de *Technical Support*, *Billing and Payments* y *Service Outages*, detectamos dos fenómenos críticos de calidad de datos:

1. **Sinteticidad del texto (Falta de ruido real):** Los textos presentan una estructura gramaticalmente perfecta, con saludos y despedidas sumamente formales (*"Dear Customer Support Team..."*, *"I hope this message finds you in good health..."*). Carecen por completo del ruido esperable en un canal de soporte real (abreviaturas coloquiales, faltas de ortografía, errores de puntuación o expresiones de frustración desestructuradas).
2. **Dispersión Semántica (Concept Drift):** Las categorías asignadas en el dataset original son demasiado laxas. Bajo la cola de *Technical Support*, por ejemplo, conviven temáticas totalmente desconectadas entre sí:
   * Caídas de infraestructura cloud (SaaS Portal offline).
   * Peticiones de información pre-venta (foco comercial).
   * Problemas microinformáticos de hardware local (drivers de impresora Laser en macOS).

### 2.3. Decisión de Diseño sobre el Caso de Negocio
Debido a la dispersión semántica identificada, mantener la narrativa de una operadora de telecomunicaciones pura (tipo Vodafone) forzando estos datos restará coherencia al proyecto ante el tribunal. 
* **Pivote narrativo:** Reencuadraremos el Caso de Negocio (Sección 7) no como una Telco pura, sino como un **BPO Multiservicio Tecnológico o un Centro de Servicios Compartidos (Shared Services Center) de IT y Facturación**. Esto hace que la presencia de soporte de software, hardware, facturación y peticiones generales sea 100% coherente con los datos reales que el modelo va a procesar.

### 2.4. Hallazgos Específicos en la Auditoría de Textos (df_01)

Tras analizar los cuerpos de texto de las colas de Facturación y Cortes de Servicio, se han documentado los siguientes patrones críticos de calidad de datos:

1. **Truncamiento de Texto (Data Bug):** En el Registro 22 de *Billing and Payments*, el texto finaliza abruptamente con un *"Additionally, please"*. Esto revela un defecto de truncamiento en la fase de exportación o generación del dataset original. 
   * *Mitigación para el MVP:* El pipeline de NLP deberá incluir un filtro de limpieza de oraciones incompletas o simplemente confiar en que los algoritmos de embeddings (Transformers) son robustos ante ruidos al final del texto.
2. **Contexto B2B e Infraestructura Crítica:** El vocabulario técnico utilizado no pertenece a soporte residencial (hogares), sino a entornos empresariales (B2B):
   * Presencia de consultas sobre software corporativo de terceros (ej. *QuickBooks Online* en finanzas).
   * Incidencias de infraestructura de salud conectada (ej. *EMR/PACS, DevSecOps, SOC*).
3. **Falsos Escalados Implícitos (Casos de Prueba de Negocio):**
   * El Registro 18 de *Service Outages* solicita información preventiva sobre mantenimiento (debería ser una consulta de información o *Request*), pero está etiquetado en la cola de caídas de servicio (*Outages*). 
   * Esto demuestra que el dataset contiene el ruido de enrutamiento ideal para entrenar el validador SITOR y probar si el modelo es capaz de sugerir la reasignación correcta.

---

## 3. El Bloque de Variables de Sistema
### 3.1. Columna `version`
* **Valores únicos:** `[51, 52, 400]`
* **Distribución:** `400` (10.441), `52` (5.346), `51` (551)
* **Diagnóstico de Auditoría:** Estos números no representan variables de negocio reales ni versiones técnicas del cliente. Son identificadores de lote o versiones de plantillas generativas del creador del dataset (sintético).
    * *Decisión:* **Eliminar por completo de la base de datos unificada.** Dejarla podría provocar *data leakage* (fuga de datos), haciendo que el clasificador aprenda correlaciones falsas basadas en el lote de generación y no en el contenido del texto.

---

## 4. Auditoría de las Columnas de Etiquetas (`tag_1` a `tag_8`)

Para evaluar la posibilidad de utilizar los tags como niveles adicionales de la jerarquía de clasificación (ej. Subdetalle), se procedió a auditar su completitud, cardinalidad y consistencia semántica en `df_01`.

### 4.1. Resultados del Análisis
* **Degradación por Valores Nulos:** Se observa una caída drástica de completitud. Mientras `tag_1` no presenta nulos, `tag_4` pierde el 10% de los datos (1.711 nulos), `tag_5` pierde casi el 50% (7.922 nulos), y `tag_8` está vacío en un 98% (16.057 nulos).
* **Alta Cardinalidad:** Las columnas intermedias presentan cientos de valores únicos (ej. `tag_4` tiene 390, `tag_5` tiene 441), lo que provocaría un fraccionamiento inasumible de las clases, impidiendo la generalización del modelo.
* **Ausencia de Estructura Jerárquica:** El análisis de los 5 valores más frecuentes revela que los tags operan como un "saco de palabras clave" (*bag-of-words*) sin orden lógico, en lugar de una ontología jerárquica. Etiquetas como "IT", "Tech Support" o "Performance" se solapan iterativamente entre los tags 2, 3, 4, 5 y 6. Además, presentan una redundancia directa con el Nivel 1 ya establecido (`queue`).

### 4.2. Decisión de Diseño
**Descarte total de las columnas `tag_1` a `tag_8`.** Su inclusión aportaría extrema dispersión (*sparsity*), redundancia semántica y ruido algorítmico sin beneficio de negocio. Esta decisión consolida y justifica empíricamente la elección de la tripleta `[queue, type, priority]` como la variable objetivo (target) más sólida y completa para el entrenamiento del MVP.

## 5. Plan Definitivo de Limpieza y Transformación de Datos (`df_01`)

Basado en las conclusiones de la auditoría de metadatos, textos libres y etiquetas, se establece el siguiente protocolo de preparación de datos para `df_01` antes de su unificación.

### 5.1. Selección de Características (Columnas)

El dataset se reducirá de 16 a **7 columnas esenciales**:

| Columna | Tipo de Rol | Acción | Justificación |
| :--- | :--- | :--- | :--- |
| `body` | Feature (Input Core) | **Mantener** | Texto base para embeddings y entrenamiento NLP. |
| `subject` | Feature (Input Extra)| **Mantener** | Contexto complementario del ticket. |
| `answer` | Feature (RAG Core)   | **Mantener** | Base de conocimiento para la extensión del copiloto. |
| `queue` | Target (Nivel 1)     | **Mantener** | Identificador de la cola/departamento. |
| `type` | Target (Nivel 2)     | **Mantener** | Naturaleza del ticket (ITIL: Incident, Request, etc.). |
| `priority` | Target (Nivel 3)     | **Mantener** | Urgencia operativa de la incidencia. |
| `language` | Filtro Técnico       | **Mantener** | Control para el Test A/B de idioma (Inglés vs. Español). |
| `version` | Ruido de Sistema     | **ELIMINAR** | Lote de generación sintética. Riesgo de *data leakage*. |
| `tag_1` a `tag_8` | Ruido Categórico | **ELIMINAR** | Alta dispersión, nulos masivos y solapamiento semántico. |

### 5.2. Filtrado y Depuración de Registros (Filas)

Para garantizar la máxima calidad del set de datos y la coherencia del Caso de Negocio (BPO Tecnológico Multiservicio), se aplicarán las siguientes transformaciones en el script de preprocesado:

1. **Filtro de Dominio (`queue`):** * Se descartan los registros pertenecientes a las colas `Human Resources` (348 filas), `Returns and Exchanges` (820 filas) y `General Inquiry` (236 filas).
   * *Impacto:* El dataset útil pasa de 16.338 a **14.934 registros**, eliminando vocabulario ajeno al negocio (retail, calzado, gestión de empleados).
2. **Imputación de Nulos en `subject`:**
   * Los 2.607 registros con valor nulo en la columna de asunto se completarán con la cadena de texto fija `"No Subject"`.
3. **Eliminación de Nulos en `answer`:**
   * Se borran las 3 filas que carecen de respuesta grabada, asegurando que la base de datos vectorial para el RAG no contenga vectores vacíos.
4. **Reseteo de Índice:**
   * Tras los descartes de filas, se aplicará un `.reset_index(drop=True)` para mantener la continuidad estructural del dataframe.

   ### 5.3. Resultado de la Ejecución (Sanity Check)
Tras ejecutar el pipeline de limpieza descrito en Pandas, se realizó una auditoría de validación para confirmar la integridad estructural del dataframe resultante, obteniendo las siguientes métricas de éxito:

* **Dimensiones Finales:** El dataset se ha consolidado en una matriz exacta de **14.931 filas y 7 columnas**.
* **Integridad de Datos (Nulos):** El conteo de nulos es de **0 absoluto** en todas las variables, confirmando el éxito de la imputación en `subject` y la depuración en `answer`.
* **Consistencia de Dominio:** La columna `queue` cuenta ahora exclusivamente con las 7 categorías aprobadas para el Caso de Negocio.
* **Índice Estructural:** El índice ha sido reseteado de forma contigua (`RangeIndex(start=0, stop=14931, step=1)`), evitando la creación de columnas residuales y dejando el dataset `df_01` listo para su futura concatenación.