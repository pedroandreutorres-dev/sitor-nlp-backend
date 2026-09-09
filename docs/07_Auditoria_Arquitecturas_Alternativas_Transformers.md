# Auditoría de Arquitecturas Alternativas: Deep Learning (Sequence Classification)

Este documento persiste el análisis comparativo de las arquitecturas Transformer candidatas para sustituir al modelo `BAAI/bge-small-en-v1.5`, el cual fracasó estructuralmente por su incompatibilidad topológica (modelo de Embeddings enfrentado a entropía cruzada lineal pura).

El objetivo industrial es clasificar el volumen de negocio (18.000+ tickets) en 102 colas con alta confianza matemática (umbral de automatización > 0.60).

## 1. Familia DeBERTa (microsoft/deberta-v3-small) [SELECCIÓN ACTIVA]
**Estado del arte actual en NLU (Natural Language Understanding)**

*   **Pros:** Utiliza Atención Desacoplada (*Disentangled Attention*). La red procesa el contenido semántico y su posición relativa mediante tensores separados. Ideal para un entorno BPO donde el contexto de la queja está inmerso en ruido corporativo (saludos, firmas corporativas, *logs*). Matemáticamente superior para inferir intención.
*   **Contras:** Alta complejidad algorítmica. Su mecanismo de atención requiere un mayor volumen de operaciones matriciales, consumiendo más VRAM que un modelo clásico a igualdad de parámetros. Obliga a mantener activas las defensas de hardware (FP16 y gradientes acumulados). Latencia de inferencia en producción marginalmente superior.

## 2. Familia RoBERTa (roberta-base) [CONTINGENCIA 1]
**El caballo de batalla industrial para clasificación de textos**

*   **Pros:** Estabilidad de gradientes garantizada. Prescinde de la ineficiente predicción de frase siguiente (NSP) del BERT original y cuenta con un pre-entrenamiento masivo. Extremadamente robusto contra divergencias durante el *Fine-Tuning*, asegurando un descenso de la pérdida predecible.
*   **Contras:** Arquitectura estándar (125M de parámetros) sin los avances de posición relativa. En tickets largos y desordenados, la probabilidad extraída sobre las clases del *long tail* puede diluirse fácilmente por debajo de la exigencia del 0.60.

## 3. Familia DistilBERT (distilbert-base-uncased) [CONTINGENCIA 2]
**La solución táctica centrada en latencia de inferencia**

*   **Pros:** Máxima eficiencia computacional (66M de parámetros). Su ligereza liberaría la gráfica, permitiendo duplicar el *batch size* y acelerando la iteración drásticamente. Única arquitectura capaz de competir de tú a tú en velocidad de inferencia contra el *Random Forest* en el servidor de producción.
*   **Contras:** Amputación paramétrica por Destilación de Conocimiento (*Knowledge Distillation*). Separar 102 clases de negocio con solapamientos semánticos sutiles exige profundidad neuronal. DistilBERT podría ser incapaz de trazar fronteras de decisión finas, aplanando la curva probabilística e impactando la Tasa de Automatización.
