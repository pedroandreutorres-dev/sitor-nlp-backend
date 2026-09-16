# Documentación Fase 6: Evaluación y Visualización de Negocio (En Curso)

## 1. Objetivo Operativo
Esta fase representa el punto final analítico del proyecto. Abandona la optimización de hiperparámetros y se centra exclusivamente en el **impacto operativo**. El objetivo es auditar las predicciones crudas exportadas de la Fase 5 y traducirlas a métricas financieras (Ahorro de FTEs) para el Tribunal. Esta fase se ejecuta **100% en local**.

## 2. Artefactos de Entrada (Inputs)
El cuaderno `07_Evaluacion_y_Visualizacion_Negocio.ipynb` debe ingerir obligatoriamente los siguientes artefactos:
*   `predicciones_holdout_roberta.csv`: Salida pura del clasificador, conteniendo la tupla de predicciones ciegamente inferidas, el *ground truth* y la confianza del modelo.
*   Archivos de baselines estadísticos (opcional, para visualización comparativa de ML tradicional vs RoBERTa).

## 3. Directivas de Evaluación Innegociables
Para que el proyecto sea validado, el cuaderno debe contener las siguientes secciones de código:

### A. Auditoría de Desempeño
*   **Matriz de Confusión Masiva (90 clases):** Renderizado de calor para diagnosticar áreas donde RoBERTa aún presenta fricción taxonómica.
*   **Curvas de Umbral (Precision-Recall tradeoff):** Visualización del comportamiento de la precisión frente al descarte de automatización cuando el umbral varía de $0.5$ a $0.9$. 

### B. Simulador de Retorno de Inversión (ROI)
*   Debe implementarse un simulador volumétrico basado en la **Tasa de Automatización (30.46%)** extraída del *Hold-Out*.
*   **Variables clave:**
    *   Volumen mensual de tickets (ej. 50,000 tickets/mes).
    *   TMO (Tiempo Medio de Operación) manual en el Nivel 1.
    *   Umbral dinámico (congelado en $\ge 0.60$ según las reglas de negocio).
*   **Salida requerida:** Cálculo del ahorro de horas mensuales (FTEs liberados) tras delegar el tráfico confiable a la API de Inteligencia Artificial y derivar el restante a validación manual (`MANUAL_REVIEW`).

## 4. Output Esperado
Este cuaderno generará las gráficas estáticas que se incrustarán en la memoria o presentación del PFM, demostrando que SITOR no es solo un modelo de NLP, sino un producto viable.
