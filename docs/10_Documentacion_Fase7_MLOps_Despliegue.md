# FASE 7: MLOps y Despliegue de Interfaz

## Objetivo Estratégico
Transformar el artefacto matemático (RoBERTa) entrenado en las fases previas en un producto de software funcional y desacoplado. Abandonamos el ecosistema interactivo de Jupyter Notebooks para establecer una arquitectura de microservicios pura (Backend + Frontend) capaz de soportar inferencia de tickets en tiempo real y *batch*.

---

## Arquitectura de Microservicios

Para asegurar escalabilidad operativa y un aislamiento de responsabilidades (Separation of Concerns) estricto, el despliegue se divide en dos nodos aislados computacionalmente:

### 1. Backend Analítico (FastAPI)
**Ubicación:** `src/api/`
**Propósito:** Servidor asíncrono que ingesta el binario `.safetensors`. Expone rutas HTTP para recibir cargas útiles JSON, procesar la tokenización, ejecutar la inferencia de PyTorch y devolver el veredicto probabilístico.
**El Gestor de Reglas (Business Logic):** Este nodo no solo devuelve el tensor crudo. Implementa la lógica de la "Guillotina de Seguridad" descubierta en el Cuaderno 07.
*   Recibe un *batch* de tickets.
*   Calcula el vector *Softmax*.
*   Filtra mediante el umbral de estrés descubierto.
*   Emite la orden final al sistema (SOBREESCRIBIR_TICKET o MANTENER_FLUJO_HUMANO).

### 2. Frontend Ejecutivo (Streamlit)
**Ubicación:** `src/frontend/`
**Propósito:** Interfaz de usuario (UI) diseñada para directivos de operaciones. 
*   Se comunica exclusivamente vía HTTP con el servidor FastAPI. 
*   Permite al usuario inyectar tickets JSON a través de un panel frontal.
*   Renderiza visualizaciones en tiempo real: medidores de confianza (gauges), veredictos del gestor de reglas y el impacto financiero simulado en vivo, cerrando el ciclo de validación de negocio.

---

## Cronograma de Ejecución (Siguientes Pasos)

1.  **Aprovisionamiento de la Estructura de Directorios:**
    *   Crear `/src/api/` y `/src/frontend/`.
2.  **Contrato de Datos (Pydantic):**
    *   Definir los esquemas de validación de entrada (Request) y salida (Response) que exigirá FastAPI.
3.  **Desarrollo del Backend (`main.py`):**
    *   Carga estática del modelo en memoria global en el evento de inicio (startup) para evitar latencia de lectura de disco por cada request.
    *   Codificación de las rutas de estado (`/health`) y de predicción (`/api/v1/predict/batch`).
4.  **Desarrollo del Frontend (`app.py`):**
    *   Maquetación del *Dashboard* simulando la pantalla del director de operaciones.
5.  **Pruebas End-to-End:**
    *   Inyección de un JSON local para verificar el flujo completo API-Front.
