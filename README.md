# SITOR - Sistema Inteligente de TipificaciÃ³n, OrquestaciÃ³n y ResoluciÃ³n de Incidencias

> **Proyecto de Fin de MÃ¡ster (PFM)**  
> **MÃ¡ster en Data Science & IA** - *Evolve Academy*  
> **VersiÃ³n del Alcance:** v8 (Cierre de Negocio y Despliegue MLOps)

---

## ð¯ 1. DescripciÃ³n y Contexto de Negocio

En el sector BPO y soporte tÃ©cnico de telecomunicaciones, la clasificaciÃ³n inicial de incidencias en el Nivel 1 (Front Office) es crÃ­tica. El lenguaje libre y ambiguo del cliente provoca errores humanos frecuentes al asignar la **Tripleta de Enrutamiento (Cola + Tipo + Prioridad)** en el CRM. Un error genera un **falso escalado** hacia el Nivel 2, consumiendo recursos tÃ©cnicos costosos, disparando el AHT (*Average Handling Time*) y frustrando al cliente.

**SITOR** nace para resolver este problema. Mediante **Procesamiento de Lenguaje Natural (NLP)** y **Deep Learning**, el sistema analiza el texto crudo del ticket y actÃºa como un **interceptor en tiempo real**, auditando la tripleta asignada por el agente y automatizando el enrutamiento o alertando de desviaciones, siempre bajo una **Regla de Pasividad Estricta** (si el modelo duda, aborta la operaciÃ³n para no inyectar ruido sintÃ©tico).

El objetivo matemÃ¡tico de SITOR es **predecir la combinaciÃ³n exacta de las 3 variables (altÃ­sima dimensionalidad)** para maximizar la automatizaciÃ³n y el ROI del negocio, siendo un sistema escalable y agnÃ³stico a la taxonomÃ­a especÃ­fica de cualquier CRM.

---

## âï¸ 2. Hitos Alcanzados (EvoluciÃ³n de la Arquitectura)

El ecosistema algorÃ­tmico ha atravesado una evoluciÃ³n desde modelos lineales hasta arquitecturas masivas de Transformers para romper el techo de cristal geomÃ©trico del negocio.

### ð¹ Fase 1 y 2: Baselines de Machine Learning ClÃ¡sico (TF-IDF)
* **IngenierÃ­a de la Tripleta:** FusiÃ³n de `Queue`, `Type` y `Priority` en una variable objetivo combinada.
* **VectorizaciÃ³n y Modelado:** TransformaciÃ³n del corpus a una matriz dispersa `TF-IDF`. Random Forest se coronÃ³ como el campeÃ³n de la IA clÃ¡sica, pero demostrÃ³ empÃ­ricamente la asfixia del enfoque estadÃ­stico (incapacidad semÃ¡ntica profunda).

### ð¹ Fase 3: IntervenciÃ³n TaxonÃ³mica y Limpieza de Ruido
* **AuditorÃ­a de Clases:** El negocio presentaba un desbalance extremo (88x). 
* **Colapso SemÃ¡ntico:** Se agruparon 13 colas residuales de baja frecuencia en una macro-clase `Derivacion_Manual_Minoritaria`, estabilizando el mapa de salidas en **89 clases** operativas viables.

### ð¹ Fase 4 y 5: Deep Learning y TransiciÃ³n a GPU (RoBERTa)
* **Sequence Classification Nativo:** Despliegue de una arquitectura densa basada en **RoBERTa-base (125M)** entrenada sobre GPUs T4/A100.
* **Balanceo MatemÃ¡tico:** InyecciÃ³n de penalizaciÃ³n mediante **raÃ­z cuadrada** de frecuencias (`1 / sqrt(frecuencias)`), protegiendo minorÃ­as sin destruir mayorÃ­as.
* **ValidaciÃ³n Hold-Out Maestro:** Entrenamiento *Full-Shot* sobre los 23.000 tickets certificando la viabilidad matemÃ¡tica.

### ð¹ Fase 6: Cierre Financiero y OptimizaciÃ³n de Break-Even
* **Simulador de EstrÃ©s:** EjecuciÃ³n de Jupyter local procesando la telemetrÃ­a probabilÃ­stica de la Fase 5.
* **Punto de OperaciÃ³n DinÃ¡mico:** LocalizaciÃ³n matemÃ¡tica del *Break-Even* financiero bajo un rÃ©gimen de estrÃ©s humano (25% de error en FO).
* **Macro-Eficiencia:** Desglose del ROI tangible y blindaje intangible (prevenciÃ³n de SLA breaches, amortizaciÃ³n de attrition).

---

## ð 3. Veredicto de ProducciÃ³n (MÃ©tricas Finales)

El modelo maestro, evaluado contra un *Test Set* ciego de cuarentena (20% de los datos), arrojÃ³ las siguientes mÃ©tricas definitivas al aplicar el umbral de confianza Ã³ptimo extraÃ­do algorÃ­tmicamente:

* **Volumen Intervenido:** Secuestro automatizado de mÃ¡s de 2.000 tickets tÃ³xicos mensuales antes de impactar el L2.
* **F1-Macro:** **0.3811** (DemostraciÃ³n de estabilidad geomÃ©trica a travÃ©s de las 89 clases).
* **PrecisiÃ³n Condicionada IA:** Sobre el **85%** en su zona de alta certidumbre.
* **Ahorro Financiero Neto:** ReducciÃ³n contundente del coste del Back Office tras compensar los daÃ±os por falsos positivos.

---

## âï¸ 4. Arquitectura MLOps Desplegada (Fase 7)

El proyecto ha concluido su ciclo de vida de ingenierÃ­a con el empaquetado de un ecosistema de microservicios robusto y testeado:

1. **Backend REST (Event-Driven):** Empaquetado del tensor en un servidor `FastAPI` sÃ­ncrono (protegiendo el Event Loop) en `src/api/`. La API expone el endpoint `/predict` con validaciÃ³n estricta de Pydantic, diseÃ±ado para integrarse con CRMs. Implementa el Cortafuegos de Pasividad (devolviendo la tripleta humana original ante alta entropÃ­a).
2. **Torre de Control (Streamlit):** Dashboard multipestaÃ±a en `src/frontend/` que sirve de interfaz de auditorÃ­a:
   * **Live Observability:** Feed de streaming en tiempo real para el NOC, clonando la estÃ©tica MLOps (Figma). Muestra intercepciones exitosas (verde neÃ³n con tachado rojo de la tripleta humana) y mitiga el sesgo de supervivencia mostrando bloqueos por pasividad (gris).
   * **API Sandbox:** Consola interactiva para inyectar JSONs manuales y auditar el contrato de datos, la latencia (ms) y el comportamiento de la red PyTorch en crudo.

---

## ð ï¸ 5. Stack TecnolÃ³gico

| Ãrea | TecnologÃ­a |
| :--- | :--- |
| **NLP & Deep Learning** | `Hugging Face`, `PyTorch`, `RoBERTa` |
| **AnÃ¡lisis de Datos**| `pandas`, `NumPy`, `Seaborn` |
| **AceleraciÃ³n Hardware** | GPUs NVIDIA (T4 / A100) |
| **Backend API**| `FastAPI`, `Uvicorn`, `Pydantic` |
| **Frontend UI** | `Streamlit` |

---

## ð 6. Estructura del Repositorio

```text
SITOR/
âââ data/
â   âââ gold/                # Parquets finales purgados (89 clases)
â   âââ resultados/          # CSVs de telemetrÃ­a extraÃ­dos del Cloud
âââ docs/                    # Manifiestos arquitectÃ³nicos y hojas de ruta
â   âââ historico_y_borradores/# Propuestas obsoletas (Ignorado por Git)
â   âââ parametros/          # Constantes del BPO para el simulador financiero
â   âââ 11_Arquitectura_Despliegue_Fase7.md # Especificaciones definitivas MLOps
âââ notebook/                # Notebooks de experimentaciÃ³n (Jupyter)
âââ src/                     # CÃ³digo fuente de despliegue MLOps
â   âââ api/                 # Microservicio backend (FastAPI + Pydantic)
â   âââ frontend/            # Dashboard multipestaÃ±a (Streamlit)
âââ README.md                
âââ .gitignore               
```

---

## ?? 7. Guía de Ejecución Rápida (Cómo usar SITOR)

Para levantar el ecosistema completo en tu máquina local:

### 1. Requisitos Previos
Asegúrate de tener Python 3.10+ y el entorno virtual activado. Luego instala las dependencias:
```bash
pip install -r requirements.txt
```

### 2. Levantar la API Backend (FastAPI)
Abre una terminal en la raíz del proyecto y arranca el servidor web:
```bash
uvicorn src.api.main:app --reload --port 8000
```
La API quedará escuchando en `http://localhost:8000`. Puedes consultar la documentación interactiva (Swagger) en `http://localhost:8000/docs`.

### 3. Levantar el Panel de Auditoría (Streamlit)
Abre una **segunda terminal** (dejando la API corriendo de fondo) y ejecuta:
```bash
streamlit run src/frontend/app.py
```
Se abrirá automáticamente tu navegador en `http://localhost:8501`. Desde la pestaña "API Sandbox" podrás inyectar tickets manualmente y ver la predicción de la red neuronal en tiempo real.

