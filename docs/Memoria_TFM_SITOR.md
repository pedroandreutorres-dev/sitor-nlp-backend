# MEMORIA TÉCNICA DEL PROYECTO SITOR
## Sistema Inteligente de Tipificación, Orquestación y Resolución de Incidencias

### 1. Contexto Operativo y Problema de Negocio
En la operativa diaria, cuando un usuario reporta un problema mediante texto libre (ticket), un agente humano de Nivel 1 (Front-Office) debe interpretar la solicitud bajo severas restricciones de tiempo y asignarle una tipología exacta basada en tres dimensiones: **Cola (Queue)**, **Tipo (Type)** y **Prioridad (Priority)**. La suma de la ambigüedad del lenguaje natural, la presión operativa, los picos de demanda y la rotación de personal (attrition) en el Nivel 1 provoca un sesgo cognitivo inevitable, traduciéndose en errores de tipificación.

### 1.1 El Coste del "Falso Escalado"
Un error en esta clasificación inicial no es una simple métrica de calidad. Si un agente asigna incorrectamente un ticket, este se enruta físicamente al Nivel 2 (Back-Office) equivocado. Esto desencadena:
*   **Coste Directo (AHT):** Los agentes pierden tiempo identificando y reasignando el ticket (coste operativo interno tasado empíricamente en **0.404 € por ticket** según el AHT ponderado del Nivel 1).
*   **Rotura de SLAs (Service Level Agreements):** Cada rebote entre departamentos prolonga el tiempo de resolución, impactando negativamente en el SLA.
*   **Pérdida de Eficiencia Agregada:** Estos micro-retrasos generan un cuello de botella sistémico.

La solución propuesta, **SITOR**, es un sistema de NLP diseñado no para sustituir al humano a ciegas, sino para desplegarse como un **sistema de validación predictiva (Cortafuegos Operativo)**.

---

## 2. Ingeniería de Datos y Preprocesamiento Operativo

El proyecto se consolidó sobre un corpus final de **15.403 tickets** de soporte técnico centrados exclusivamente en el Sector Telecomunicaciones.

### 2.1. Fusión Dimensional (La Tripleta Telco)
En el diseño arquitectónico, se descartó entrenar tres modelos independientes para predecir Cola, Tipo y Prioridad por separado, ya que destruiría la correlación intrínseca. Se concatenaron las tres variables, consolidando un espacio predictivo de **56 clases**, compuesto por 55 categorías operativas puras del negocio Telco y una clase residual para contener la varianza extrema (OUT_OF_SCOPE).

---

## 3. Fase de Modelado: De la Ilusión Clásica al Deep Learning

### 3.1. Bake-Off de Modelos (Baseline)
El algoritmo TF-IDF combinado con Random Forest alcanzó un **F1-Macro de 0.4394**. A nivel académico establece un suelo base sólido, pero operativamente demuestra que los modelos basados puramente en frecuencias de palabras (BoW) sufren de asfixia estadística frente a la exigencia semántica de 56 fronteras departamentales solapadas.

### 3.2. Transición a RoBERTa
El espacio latente exigía atención semántica profunda. Se transicionó a una arquitectura **RoBERTa-base (125M de parámetros)** entrenada sobre GPUs. El modelo se optimizó mediante validación cruzada, priorizando el acierto global (Accuracy) para garantizar la correcta canalización del mayor volumen posible de tickets de negocio.

### 3.3. El Rendimiento Corporativo
El modelo RoBERTa, entrenado con los hiperparámetros óptimos, logró un **Accuracy global del ~59%** (0.5882 en validación cruzada). Aunque este valor parece modesto en benchmarks de NLP tradicionales, es un hito técnico considerando la extrema complejidad de 56 clases cruzadas y la ambigüedad nativa del lenguaje del cliente. Más importante aún, RoBERTa construyó un espacio latente coherente que permitía aplicar marginalización probabilística en la capa de inferencia.

---

## 4. Auditoría Forense y Calibración Térmica

La evaluación cruda de un modelo de Deep Learning mediante métricas estándar oculta riesgos operativos inasumibles. Para auditar la robustez real del modelo, se implementó un pipeline forense estricto.

### 4.1. Prevención de Data Leakage (Stratified Group K-Fold)
En proyectos corporativos, la duplicidad de tickets (por seguimientos de un mismo usuario) infla artificialmente las métricas. Para evitar falsos positivos financieros, se previno el *Data Leakage* intra-cluster desde la Fase 1. Al imponer una partición estrictamente ciega agrupando por cluster_id (Fuzzy Hashing), se garantizó que la red se enfrentara siempre a incidencias inéditas. Por tanto, el **~59% de Accuracy es el rendimiento real auditado en el peor de los casos (Worst-Case Scenario)**.

### 4.2. El Problema de la Sobreconfianza y L-BFGS
Las redes neuronales modernas sufren de *overconfidence*. La curva de calibración demostró que RoBERTa asignaba casi un 98% de probabilidad a predicciones que empíricamente erraba frecuentemente. 
Para mitigar este riesgo catastrófico en producción, se implementó **Temperature Scaling** mediante optimización L-BFGS. El algoritmo aplicó un factor de corrección térmico (=1.6139$), aplanando la arrogancia estadística y devolviendo la red a la diagonal de fiabilidad perfecta.

---

## 5. Simulador Financiero y Matriz de Costes Asimétrica

Con las probabilidades marginalizadas por Colas y térmicamente calibradas, se procedió a calcular el ROI real del proyecto. Se construyó un **Motor de Reglas Heurísticas (Matriz de Costes Asimétrica)** trazado directamente de la operativa BPO Tier-1:

*   **Coste Inferencia IA (0.005€):** Coste computacional unitario.
*   **Rebote de Cola (1.01€):** Coste de ~2.5 minutos de AHT perdido en el Nivel 2 re-enrutando un ticket mal asignado.
*   **Fricción Administrativa (0.05€):** Error inocuo de subtipo (ej. *tarifa* vs *consumo*). El agente subsana el desplegable en ~10 segundos.
*   **Rotura de SLA (2.00€ - 10.00€):** Penalización variable según la severidad del contrato al degradar la urgencia real o fallar en un subtipo crítico.

### 5.1. Resultados del Análisis de Sensibilidad (ROI)
Para un volumen piloto simulado de **2.500 tickets mensuales**, al exigir un umbral de seguridad estricto, la red calibrada generó los siguientes escenarios:
*   **Escenario Tolerante (Startup / Multa 2.00€):** Rentable. La IA automatiza el 42.3% del tráfico con un ahorro neto de **+110.96€ mensuales**.
*   **Escenario Base (Tier-1 Estándar / Multa 5.00€):** Límite de rentabilidad. Automatización del 12.4% con un déficit mínimo de **-1.52€ mensuales**.
*   **Escenario Estricto (Banca o Salud / Multa 10.00€):** Inviable. Automatización del 2.8% con pérdida neta de **-46.93€ mensuales**.

**Veredicto de Negocio:** Se rechaza el pase a producción End-to-End autónomo en entornos corporativos estrictos (Tier-1). El alto riesgo de penalización por rotura de SLA neutraliza los ahorros salariales directos.

---

## 6. Explicabilidad (LIME) y Matriz de Confusión

Para justificar pericialmente este rechazo operativo ante negocio, se documentó la caja negra:

*   **El Agujero Negro Semántico (Matriz de Confusión):** Como se observa visualmente en las regiones calientes de la matriz, existe una fuga dominante (aprox. 330 incidencias cruzadas) en la frontera entre *Soporte Técnico* y *Atención al Cliente*. El vocabulario genérico de queja del usuario desdibuja la barrera entre una avería y una reclamación.
*   **Interpretación LIME:** La IA demostró interiorizar la lógica del negocio. En tickets con alta confianza (0.96), LIME resaltó pesos masivos en *troubleshooting* (ej. "restart") y gravedad (ej. "significant"). En tickets fuera de alcance, las distribuciones se aplanaron, delegando correctamente la ambigüedad extrema al humano (Cortafuegos CRM).

---

## 7. Pivote Estratégico y Despliegue (MLOps)

Al haber demostrado empírica y financieramente la inviabilidad de la automatización End-to-End ciega, el proyecto pivota hacia un modelo de **Copiloto de Back-Office (Human-in-the-Loop)**. 

Desplegar SITOR como un pre-rellenador (Asistencia Pasiva) elimina el riesgo de SLA (multa 0€) al requerir la validación final humana, transformando el déficit inicial en un ahorro masivo de FTEs operativos al reducir drásticamente el AHT.

Para materializar este producto, la arquitectura se sella con el empaquetado del tensor en un microservicio **FastAPI** y su exposición visual interactiva mediante un dashboard en **Streamlit**. Esta interfaz no solo entrega la predicción al agente, sino que expone el porqué (Caja Blanca / LIME) para generar confianza en la operación.

**Trabajo Futuro:** Como siguiente fase analítica, se recomienda el entrenamiento de clasificadores jerárquicos (*One-vs-Rest*) especializados en desambiguar la frontera semántica conflictiva entre Soporte Técnico y Atención al Cliente.

