# 05 - Diseño del Frontal y Experiencia de Usuario

## 1. Resumen de la solución y del usuario
* **Qué problema resuelve:** Los falsos escalados derivados de una mala tipificación inicial de tickets por parte de los agentes de Nivel 1 en *Call Centers* (BPO), lo que aumenta los costes operativos.
* **Quién es el usuario principal:** El Coordinador de Soporte o Auditor de Calidad (Nivel 2).
* **Necesidad o tarea concreta:** Revisar y auditar de forma ágil aquellos tickets donde el modelo no alcanza la confianza matemática suficiente para ejecutar un auto-enrutamiento.
* **Tipo de producto diseñado:** Herramienta Operativa de Auditoría (*Human-in-the-loop*).
* **Acción principal obtenida:** Validar la sugerencia de enrutamiento de la IA (estado `OVERRIDE`) o mantener la clasificación humana original (estado `VERIFIED`) mediante un solo clic.

## 2. Imagen mockup del frontal
*(Nota conceptual: Este diseño es un prototipo visual provisional para ilustrar la interacción operativa entre la lógica del backend y la toma de decisiones humana).*

![Mockup del frontal SITOR](../assets/05_mockup_frontal.png)

## 3. Justificación del diseño

### 3.1. Utilidad y valor de la solución
El frontal resuelve el problema clásico de la "caja negra" en la IA. El auditor necesita contexto rápido. La interfaz reduce la carga cognitiva: en lugar de leer el ticket y navegar por un árbol de decisión mental de 90 clases, el auditor recibe la sugerencia pre-procesada del modelo. Esto ahorra tiempo por ticket, disminuyendo el riesgo de falso escalado y convirtiendo un resultado probabilístico en una acción operativa.

### 3.2. Flujo de usuario
1. **Punto de entrada:** El usuario accede a la vista de auditoría. Solo ve los tickets que el backend ha marcado para revisión manual (aquellos donde la confianza o *Softmax* está por debajo del umbral del escenario operativo, ej. < 80%).
2. **Entradas o selecciones:** No necesita introducir texto. Su entrada es la revisión visual de la columna izquierda (origen humano) frente a la columna derecha (análisis algorítmico).
3. **Procesamiento (Backend invisible):** El endpoint RESTful (FastAPI) ejecuta el flujo enviando el texto al Tokenizador y procesando la inferencia a través del modelo `RoBERTa`.
4. **Resultado:** Recibe la clase propuesta y un *Confidence Score* numérico continuo (0.0 a 1.0).
5. **Acción:** Pulsa el botón de confirmación para acatar la clasificación del algoritmo, o la ignora.

### 3.3. Experiencia de usuario (UX)
He diseñado la interfaz bajo los principios de mínima fricción visual:
* **Simplicidad:** He descartado incluir gráficas temporales complejas en esta vista. La interfaz es puramente resolutiva y no distrae de la tarea de auditoría.
* **Transparencia estadística:** Mostrar explícitamente que el modelo tiene un "72%" de confianza (no superando el 80% exigido) invita al humano a colaborar, reduciendo el rechazo habitual hacia los sistemas automatizados opacos.

## 4. Presentación de resultados y explicabilidad
El resultado principal se acompaña de métricas de interpretabilidad para proporcionar contexto sobre la estimación:
* **Enfoque Discriminativo:** Aunque `RoBERTa` pertenece a la familia de *Transformers*, en SITOR se utiliza estrictamente bajo un paradigma de clasificación (*Sequence Classification*). La arquitectura no genera texto nuevo, evitando el riesgo de respuestas incorrectas ("alucinaciones") que serían problemáticas en un entorno corporativo.
* **El contexto del resultado:** La etiqueta predicha se presenta bajo un componente de "*Confidence Score*" con una barra de progreso que mapea la probabilidad frente al umbral operativo (80%).

## 5. Alcance del MVP
Este diseño es una representación visual orientada a la visión del producto. Para el alcance evaluable de este TFM (MVP), el esfuerzo técnico se ha centrado en el desarrollo del modelo predictivo y su integración como microservicio mediante **FastAPI**. 

Si el calendario lo permite, el frontal se desarrollará como un panel operativo simplificado (por ejemplo, con *Streamlit*) para poder interactuar con la API mediante ejemplos de prueba durante la presentación del proyecto. Cualquier elemento adicional de navegación compleja queda fuera del alcance del MVP y se considera trabajo futuro.
