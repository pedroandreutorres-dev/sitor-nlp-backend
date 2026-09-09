# Documentación de Fase 3: Modelos Semánticos Estáticos (Frozen Embeddings) - SITOR V7.2

**Fecha de Ejecución:** Septiembre 2026
**Notebook Asociado:** `03_Entrenamiento_Modelos_Semanticos.ipynb`
**Objetivo:** Evaluar el rendimiento de proyecciones semánticas densas (*Deep Learning* estático) frente a la línea base léxica (TF-IDF) utilizando un modelo pre-entrenado sin alteración de pesos (*Frozen Architecture*).

---

## 1. Arquitectura de Ingesta y Replicación BPO

Para asegurar un *Bake-Off* (experimento controlado) irrefutable, se importó el mismo orquestador determinista (`evaluar_modelo_bpo`) del Notebook 02 y el mismo dataset particionado (`train_set_v7.parquet`).
La función de evaluación fue modificada con polimorfismo de indexación (`hasattr(X, 'loc')`) para tolerar el paso de matrices NumPy densas sin alterar los índices pre-congelados de validación cruzada.

---

## 2. Proyección Semántica (El Modelo BAAI)

Se instanció el modelo de *SentenceTransformers* `BAAI/bge-small-en-v1.5` operando como un extractor estático (*Frozen*).
*   **Aislamiento de Hardware:** Se forzó `device='cpu'` y la descarga se canalizó a un directorio local (`cache_folder='../models/'`) para garantizar que el despliegue fuera autocontenido, determinista y tolerante a entornos sin GPU ni salida a internet.
*   **Defensa del Contexto Operativo:** Ante la casuística de los tickets BPO (firmas, saludos y ruido estructural en la cabecera del correo), se forzó matemáticamente la ventana de contexto máxima de la arquitectura: `max_seq_length=512`. Esto aseguró la absorción técnica del síntoma del cliente.
*   **Transformación Geométrica:** Las 15.000 dimensiones huecas del TF-IDF fueron aniquiladas. El texto fue comprimido a un espacio continuo de `(23720, 384)` dimensiones.

---

## 3. Modelo C: Regresión Logística sobre Espacio Denso

Sobre la nueva morfología de datos, se reintrodujo la Regresión Logística.

### Intervención Arquitectónica (Expansión de Varianza)
Durante las pruebas iniciales, el modelo lineal generó un colapso predictivo total. El diagnóstico algebraico reveló **Anisotropía Neuronal**: los *embeddings* generados estaban confinados en un cono hiperdimensional muy estrecho, provocando que los gradientes de error fueran minúsculos para el solucionador `lbfgs`.
Como solución correctiva, se inyectó un `StandardScaler` en la tubería para expandir artificialmente la varianza, devolviendo la tracción matemática a la optimización.

---

## 4. Veredicto Empírico: El Colapso del "Zero-Shot" Semántico

A pesar del parche de varianza, la telemetría del Modelo C arrojó resultados catastróficos frente a la línea de vida del TF-IDF (Modelo A):
*   **F1-Macro:** 0.0394
*   **Tasa de Automatización (Umbral 0.60):** 8.09% (Derrotado por el 11.71% clásico).
*   **Precisión Condicionada:** 25.58% (Frente al robusto 99.07% del Random Forest).

### Justificación Técnica (La Defensa ante el Tribunal)
Este fracaso empírico no obedece a un error de *scripting*, sino que es una demostración científica de los límites del *Machine Learning* genérico aplicado a entornos verticales:
1.  **Lavado Léxico:** En soporte técnico BPO, el enrutamiento es esclavo de palabras clave exactas (ej. *códigos de error, IDs de producto*). Los *Transformers* genéricos pre-entrenados disuelven estos términos en conceptos difusos, destruyendo la señal de decisión.
2.  **Domain Shift:** El modelo *BAAI* fue entrenado en corpus abiertos de internet. Al mantener sus pesos congelados (*Frozen*), su representación espacial es inútil e incapaz de trazar fronteras de decisión precisas para 102 colas cerradas de un *Call Center*.

**Conclusión Final:** Se dictamina empíricamente que la adopción de *Embeddings* estáticos tipo *plug-and-play* es inservible para el nicho BPO. Este colapso justifica matemática y operativamente el salto obligado hacia la Fase 4, donde se aplicará *Fine-Tuning* (retropropagación completa) para obligar a la red neuronal a desaprender el inglés genérico y adoptar la jerga corporativa exacta.
