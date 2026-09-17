# Plan de Despliegue MLOps (Fase 7)

Este documento detalla la arquitectura de software y el paso a paso para la construcción del ecosistema FastAPI (Backend) y Streamlit (Frontend). Todo el código respetará la Regla de Pasividad Estricta y las métricas de negocio auditadas en el Cuaderno 07.

## 1. Variables de Entorno y Configuración Global
Para garantizar que el umbral de decisión no está *hardcodeado* en el código de Python, crearemos un archivo oculto `.env` en la raíz del proyecto.

- **[.env]** Alojará las constantes del entorno de producción:
  - `UMBRAL_PASIVIDAD=0.75` (El punto óptimo de *Break-Even* bajo estrés).
  - `MODEL_PATH=models/produccion_roberta/` (La ruta a los binarios del modelo entrenado).

---

## 2. Contrato de Datos (Pydantic) y Diseño REST
El orquestador debe integrarse simulando un *Webhook* de un CRM real, operando por eventos (Event-Driven). El tipado estricto separa campos vitales de metadatos de relleno.

- **[src/api/schemas.py]** Definirá el contrato de red:
  - `TicketInput`:
    - **Campos Obligatorios (Required):** `ticket_id` (trazabilidad) y `raw_text` (motor de inferencia). Si faltan, detonará un Error 422. Y la tripleta original: `human_queue`, `human_type`, `human_priority` (para la gestión de pasividad).
    - **Campos Opcionales (Optional):** Metadatos operativos como `created_at`, `agent_id`. Si el CRM no los envía, el modelo no colapsa.
  - `TicketResponse`: El payload de salida consumido por el CRM/Streamlit. Garantiza la trazabilidad devolviendo el `ticket_id`, la `latency_ms` del servidor, el `softmax_confidence` y el `verdict` final (Sobreescritura vs Pasividad), junto con la tripleta empaquetada.

---

## 3. Servidor de Inferencia (FastAPI) y Pipeline de Transformación
El núcleo SITOR. Ejecutará inferencia bajo estricto control de excepciones y protegerá el enrutamiento ante dudas matemáticas.

- **[src/api/main.py]** Implementará la siguiente topología:
  1.  **Arranque (Lifespan Event):** Carga el Tokenizador, RoBERTa y el diccionario de mapeo estructural (`id2label`) en RAM al encender el servicio.
  2.  **Manejo de Errores (Exception Handler):** Interceptores para devolver un `HTTP 422 Unprocessable Entity` estructurado si el CRM inyecta un payload inválido.
  3.  **Endpoint Unitario `POST /api/v1/predict`:** Recibe el `TicketInput`.
  4.  **Pipeline de Transformación y Telemetría:**
      - Inicia cronómetro con `time.perf_counter()`.
      - *Ingesta:* Extrae el `raw_text`.
      - *Pre-procesamiento & Tokenización:* `AutoTokenizer` (max 256 tokens).
      - *Inferencia:* Tensor -> Modelo -> Logits -> Softmax.
      - Detiene cronómetro y extrae `latency_ms`.
      - *Post-procesamiento:* Mapea el ID ganador a la macro-etiqueta a través del diccionario en RAM, y aplica un *split*.
  5.  **Lógica de Decisión (El Blindaje de Negocio):** 
      - Si `Softmax >= UMBRAL_PASIVIDAD`: 
        - `verdict = "OVERRIDE_APPROVED"`
        - La tripleta de salida contiene la **Predicción SITOR**.
      - Si `Softmax < UMBRAL_PASIVIDAD`: 
        - `verdict = "HUMAN_ROUTING_MAINTAINED"`
        - **Acción Obligatoria:** La tripleta de salida se **sobrescribe devolviendo los valores originales (humanos)** recibidos en el Request. Esto anula cualquier riesgo de inyección de predicciones basura en el CRM.
  6.  **Respuesta:** Empaqueta y devuelve el `TicketResponse`.

---

## 4. Frontend Ejecutivo (Streamlit) - Observabilidad MLOps
La Torre de Control que renderizará la telemetría en tiempo real bajo las directrices estrictas de los mockups de Figma.

- **[src/frontend/app.py]** Estructurado como una aplicación multipestaña (`st.tabs`):
  -   **Tab 1 (Live Observability):** Motor de streaming consumiendo el CSV crudo contra el endpoint `/predict`. **Renderizado Condicional (Sin regresiones funcionales):** La vista ejecutará una bifurcación visual obligatoria basada en la llave `verdict`. Los tickets `OVERRIDE_APPROVED` se renderizarán en verde neón; los tickets `HUMAN_ROUTING_MAINTAINED` se renderizarán atenuados en gris oscuro.
  -   **Tab 2 (API Sandbox):** Una caja de texto interactiva simulando el CRM para inyectar payloads manuales y auditar la latencia y la respuesta JSON del servidor HTTP.
