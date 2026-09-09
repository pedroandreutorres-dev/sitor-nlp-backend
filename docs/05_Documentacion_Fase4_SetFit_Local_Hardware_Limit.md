# Documentación de Fase 4: Fine-Tuning Contrastivo Local (Límite de Hardware) - SITOR V7.2

**Fecha de Ejecución:** Septiembre 2026
**Notebook Asociado:** `04_Entrenamiento_SetFit_Local.ipynb`
**Objetivo:** Validar la viabilidad arquitectónica de aplicar un *Fine-Tuning* de Aprendizaje Contrastivo (SetFit) en un entorno local de recursos limitados (CPU), forzando el modelo mediante *Few-Shot Learning* agresivo para establecer el límite físico del hardware.

---

## 1. Arquitectura de Ingesta y Aislamiento BPO

El salto a la orquestación neuronal exigió una reingeniería completa del bucle iterativo para blindar la validación cruzada y evitar la contaminación matemática entre pliegues.

*   **Ingesta Hermética:** Se conservó `train_set_v7.parquet` como fuente inmutable. Se instanció un `LabelEncoder` para transformar la jerga operativa en una matriz dimensional discreta (0 a 101), exportando el diccionario de traducción explícitamente para retener la trazabilidad del negocio.
*   **Desacoplamiento de Telemetría (Prevención de Data Leakage):** En *Deep Learning*, las matrices de pesos retienen gradientes. Si la evaluación se ejecutara sobre la instancia persistente del modelo, el Fold 2 heredaría la memoria del Fold 1. Para evitarlo, el motor de evaluación BPO se extrajo a una función algorítmicamente pura (`calcular_metricas_bpo`). Ésta ingiere exclusivamente *arrays* de NumPy numéricos, garantizando que el ciclo de vida del *Transformer* se instancie y destruya dentro de cada partición de forma aislada.

---

## 2. Contingencia Dinámica: Muestreo Few-Shot Seguro

Entrenar los 33 millones de parámetros del modelo BAAI sobre la población total excedería la memoria local. Se aplicó una estrategia de estrangulamiento de datos (*Few-Shot Learning*), fijada en un máximo teórico de 32 *shots* por clase.

*   **Protección del Long Tail:** Debido al particionado estratificado, algunas colas minoritarias disponían de menos de 30 tickets. Se implementó la directiva matemática `min(max_shots, len(df_clase))` operando sobre estructuras de Pandas puras para blindar la ejecución contra excepciones `ValueError` originadas por sobredemanda.
*   **Transición Diferida:** Para evitar la colisión de tipos entre el muestreo de Pandas y las estructuras generativas, la purificación de tensores y la conversión a formato `Dataset` nativo de HuggingFace se retrasó estratégicamente hasta el último milisegundo previo a inyectarlos en la red neuronal.

---

## 3. Infraestructura y Blindaje de Compilación

La volatilidad del control de hardware exigió aislar la ejecución de las heurísticas de HuggingFace y PyTorch:
*   **Intercepción de Aceleración:** Se inyectó `os.environ["CUDA_VISIBLE_DEVICES"] = ""` para cegar a la librería y forzar operativamente el uso del procesador (CPU), evitando bloqueos fatales por *drivers* incompatibles.
*   **Malla de Captura de Excepciones:** Se programó un bloque conjunto `except (MemoryError, RuntimeError)` capaz de interceptar tanto los desbordamientos estándar del intérprete de Python como los fallos catastróficos originados en el asignador de memoria C++ nativo de PyTorch, permitiendo recular la carga a 16 *shots* sin derribar el kernel.

---

## 4. Veredicto Empírico: El Colapso de Cómputo Local

El experimento quedó abortado durante la compilación del primer pliegue de validación. La interrupción determinó una asfixia de hardware (*Compute-Bound*) intrínseca a la arquitectura contrastiva de la red.

### Autopsia de la Explosión Combinatoria (O(N²))
La extracción del *Few-Shot* limitó la población teórica a ~3.264 muestras, un volumen asumible en algoritmos clásicos. Sin embargo, el *Aprendizaje Contrastivo* no procesa observaciones aisladas; enseña similitudes proyectando emparejamientos cruzados entre todos los vectores.

Debido al límite dinámico que protegió el *long tail*, la población inicial fue amputada ligeramente. A pesar de la reducción, la complejidad cuadrática del algoritmo derivó los datos crudos en exactamente **10.018.912 de pares contrastivos**. Fragmentado en lotes de 16, el orquestador forzó a la máquina a enfrentarse a **626.182 iteraciones**.

### Telemetría de la Asfixia
Privada de clústeres GPU (CUDA) para paralelizar el álgebra, la CPU colapsó bajo el estrangulamiento matricial:
*   **Rendimiento Operativo:** 0.27 lotes por segundo (~4 segundos por iteración).
*   **Proyección de Latencia (1 Fold):** 640 horas (26 días ininterrumpidos).
*   **Proyección del Benchmark:** Más de 4 meses de combustión continua al 100% de la placa base.

### Dictamen Final de Arquitectura
Se decreta el **Fracaso Absoluto del Entorno Local** para el entrenamiento de arquitecturas semánticas sobre taxonomías de alta cardinalidad (102 colas). Bajo restricciones de CPU, el Modelo A (Random Forest, 11.71%) retiene la supremacía operativa por su aplastante eficiencia estadística.

Este colapso valida empíricamente la **migración forzosa del TFM**. La siguiente iteración (Cuaderno 05) se desplegará obligatoriamente sobre un clúster *Cloud* dotado de aceleradores GPU. En dicho entorno, se levantará la inanición del *Few-Shot* inyectando el 100% de la matriz de datos para que el paralelismo gráfico resuelva la gigantesca explosión combinatoria en tiempo de negocio operativo.
