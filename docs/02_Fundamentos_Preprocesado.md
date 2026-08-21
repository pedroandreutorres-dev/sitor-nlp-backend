
# Documento Técnico: Preprocesado NLP (SITOR)

## 1. Contexto y Objetivo
Como paso previo a la vectorización mediante TF-IDF (baseline algorítmico definido en la arquitectura del MVP[cite: 1]), es imperativo estandarizar el texto libre de los tickets de soporte ("Multilingual Customer Support Tickets"[cite: 1]). 

El objetivo es reducir la dispersión de la matriz matemática (sparsity) y unificar el vocabulario sin destruir la carga semántica que permite predecir la tipificación del ticket.

## 2. Diseño del Pipeline NLP (spaCy optimizado)
Para la tokenización y lematización se ha implementado `spaCy` (`en_core_web_sm`), cumpliendo con el diseño arquitectónico establecido[cite: 1]. Para garantizar la eficiencia computacional exigida en entornos productivos (MLOps), el modelo acústico se carga desactivando explícitamente los componentes de análisis sintáctico (`parser`) y reconocimiento de entidades (`ner`), que no aportan valor a la limpieza básica y penalizan la latencia.

## 3. Decisiones Técnicas y de Dominio (Telco/IT)
El pipeline implementa las siguientes reglas de negocio:

* **Corrección Estructural de Datos Públicos:** Se aplica una purga previa mediante expresiones regulares (`re`) para eliminar literales de escape (`\n`, `\r`) incrustados en el texto crudo. Esto evita que el tokenizador una palabras disjuntas, lo cual generaría dimensiones espurias en la matriz TF-IDF.
* **Preservación de Entidades Alfanuméricas:** Se ha evitado el filtrado ciego de caracteres estrictamente alfabéticos (`token.is_alpha`). En el dominio de soporte técnico[cite: 1], eliminar códigos alfanuméricos (ej. "5G", "IPv4", "Error404") destruiría información predictiva vital. Se eliminan exclusivamente *stop words*, puntuación y espacios.
* **Lematización con Contexto de Capitalización:** El texto crudo se pasa al motor NLP respetando las mayúsculas originales para maximizar la precisión estadística del modelo de `spaCy`. La conversión a minúsculas se aplica de forma terminal sobre el lema extraído (`token.lemma_.lower()`).

## 4. Estado Actual
La transformación se ha aplicado de forma aislada (*row-wise*) a los 23.112 registros del subconjunto en inglés, almacenando el resultado en una nueva variable (`body_clean`) para preservar la trazabilidad frente al texto original.