# SITOR - Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

> **Proyecto de Fin de Máster (PFM)**  
> **Máster en Data Science & IA** - *Evolve Academy*  
> **Versión del Alcance:** v8 (Cierre de Negocio y Despliegue MLOps - Sector BPO Telco)

---

## 🎯 1. Valor de Negocio y Macro-Eficiencia (Executive Summary)

En el sector BPO y soporte técnico de telecomunicaciones, el enrutamiento manual de incidencias en el Front Office (Nivel 1) genera cuellos de botella y falsos escalados. SITOR audita, intercepta y resuelve en tiempo real el enrutamiento de la **Tripleta Operativa (56 colas Telco)** mediante Deep Learning, bajo una regla de pasividad estricta (el modelo solo interviene ante alta certeza matemática).

### 🔹 Veredicto de Producción (Hold-Out Ciego)
Evaluado sobre una matriz de cuarentena del 20% (3.081 tickets), **SITOR automatiza un 8.63% del tráfico del Nivel 1 garantizando una Precisión Condicionada del 83.46%**. 

El sistema no busca una micro-eficiencia basada en el ahorro directo de nóminas, sino operar como un verdadero **Cortafuegos Operativo**:
* **Prevención de Penalizaciones (SLA):** Evita el "efecto ping-pong" de tickets mal enrutados, recortando el *Mean Time to Resolve* (MTTR) y previniendo penalizaciones económicas por ruptura de contrato.
* **Amortización de Rotación (*Attrition*):** Asimila la entropía y el exceso de error humano generados durante los picos de contratación masiva de perfiles junior.
* **Desestrangulamiento del Nivel 2:** Limpia el *backlog* técnico de ruido administrativo, permitiendo al BPO absorber mayor volumen de negocio sin requerir nuevos FTEs.
* **Protección del NPS:** Agilizar el cauce correcto incrementa la Tasa de Resolución al Primer Contacto (*FCR*), mitigando de forma directa el riesgo de fuga (*Churn*).

---

## ⚙️ 2. Justificación Algorítmica y Músculo Técnico (Data Science)

El desarrollo del modelo central implicó la deconstrucción empírica de los baselines estadísticos a favor de arquitecturas basadas en atención semántica masiva.

### 🔹 Bake-Off de Modelos: La Ilusión del F1
El Machine Learning clásico (Random Forest + TF-IDF) alcanzó un F1-Macro competitivo (0.58), pero **fracasó operativamente en la calibración probabilística**. Al imponer el umbral estricto de seguridad dictado por Negocio (Softmax > 0.85), el Random Forest colapsó a un 0.00% de automatización, convirtiéndose en un pasivo. 

**RoBERTa (125M de parámetros)** se despliega porque, aunque su F1 global se resiente, su arquitectura semántica genera distribuciones de probabilidad más afiladas y calibradas (menor entropía cruzada / Log-Loss de 1.75), siendo el único modelo capaz de superar el umbral de pasividad de forma segura y productivizable.

### 🔹 Ingeniería en la Función de Pérdida (PyTorch)
El dominio Telco sufre un desbalanceo extremo. Para evitar el colapso del hiperplano predictivo hacia las clases mayoritarias, no nos limitamos a instanciar el modelo base: **se sobreescribió el orquestador nativo de Hugging Face**.
Se inyectó un tensor dinámico en CUDA (raíz cuadrada inversa de frecuencias) directamente en el cálculo de la *Cross-Entropy Loss*. Además, este tensor se recalcula estrictamente dentro de cada iteración del bucle *K-Fold* para neutralizar cualquier vulnerabilidad de *Data Leakage*.

### 🔹 Auditoría de Fricción Taxonómica
El análisis forense de la matriz de colisiones evidenció que el error residual de la red neuronal no es estocástico, sino que responde a ruido estructural (*Ground Truth Noise*) heredado del etiquetado humano de origen. Las áreas de fricción se concentran de forma sistemática en las fronteras procedimentales ambiguas (ej: la delgada línea entre 'Avería General' y 'Soporte Técnico'). El modelo no se equivoca; expone las deficiencias del negocio.

---

## 🛠️ 3. Stack Tecnológico

| Área | Tecnología |
| :--- | :--- |
| **NLP & Deep Learning** | `Hugging Face`, `PyTorch`, `RoBERTa` |
| **Análisis de Datos**| `pandas`, `NumPy`, `Seaborn` |
| **Aceleración Hardware** | GPUs NVIDIA (A100) |
| **Backend API**| `FastAPI`, `Uvicorn`, `Pydantic` |
| **Frontend UI** | `Streamlit` |

---

## 📁 4. Estructura del Repositorio

El pipeline garantiza la reproducibilidad completa, abarcando desde la ingesta del parquet crudo hasta la inferencia en un endpoint desacoplado.

```text
SITOR/
├── data/
│   ├── gold/                # Parquets finales purgados (56 clases Telco)
│   └── raw/                 # Origen crudo de tickets BPO
├── docs/                    # Manifiestos arquitectónicos y hojas de ruta
├── notebook/                # Cuadernos Jupyter del pipeline end-to-end
├── results/                 # Predicciones ciegas Hold-Out
├── metrics/                 # Telemetría de K-Fold y matriz de confusión
├── models/                  # Pesos y tokenizador de RoBERTa para producción
├── src/                     # Código fuente de despliegue MLOps
│   ├── api/                 # Microservicio backend (FastAPI + Pydantic)
│   └── frontend/            # Dashboard multipestaña (Streamlit)
├── README.md                
└── .gitignore               
```

---

## 🚀 5. Guía de Ejecución Rápida (Cómo usar SITOR)

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
