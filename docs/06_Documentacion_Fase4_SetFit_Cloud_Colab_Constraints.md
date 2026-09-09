# Fase 4: Experimentación SetFit (BAAI/bge-small-en-v1.5) en Cloud GPU

## 1. Contexto y Salto a la Nube
Tras certificar el límite matemático local (asfixia combinatoria $O(N^2)$ en CPU documentada en el hito 05), la orquestación del Modelo D.2 (SetFit Full-Shot) se transicionó a la infraestructura de Google Colab (Acelerador T4). El objetivo: mantener la paridad del *Bake-Off* (Validación Cruzada K-Fold sobre ~23.000 tickets reales) enfrentando el *Deep Learning* contrastivo contra el Random Forest de la Fase 2.

## 2. Contingencias de Infraestructura (Capa Gratuita)

El despliegue topó con dos cuellos de botella severos a nivel de sistema:

### 2.1. Violación de Segmento (Segfault C++)
**Problema:** La inyección en caliente de dependencias profundas (`setfit`, `datasets`, `fastparquet`) colisionaba con los binarios de C++ precargados en la memoria del entorno por defecto de Colab. Al ejecutar la instanciación de PyTorch en la misma sesión, el núcleo de Linux colapsaba de forma súbita.
**Solución:** Aislamiento estricto de la etapa de aprovisionamiento. La celda de instalación de *pip* se separó del resto de la ejecución, obligando a un reinicio físico del *kernel* (`Restart session`) para purgar la RAM antes de importar los tensores.

### 2.2. Colapso de RAM (Out Of Memory)
**Problema:** A pesar de derivar el *Dataset* a Apache Arrow y aplicar restricciones máximas (`num_iterations=1`, `sampling_strategy="unique"`, `max_seq_length=256`), el mapeo de emparejamientos contrastivos superó sistemáticamente los 12 GB de memoria viva (RAM) del contenedor gratuito de Colab al procesar los 18.400 tickets de entrenamiento por pliegue.

## 3. Decisión Metodológica y Ultimátum Arquitectónico

Ante la falta de memoria RAM física, se plantearon dos vías de contingencia algorítmica que fueron tajantemente rechazadas por auditoría:
- **Techo de Cristal:** Topar el volumen a 100 tickets por cola. *(Rechazado: Destruye el long tail y distorsiona la probabilidad a priori del ecosistema BPO)*.
- **Holdout Estratificado:** Reducir la porción de entrenamiento al 40% del total. *(Rechazado: Invalida el Bake-Off estricto al evaluar sobre distribuciones diferentes al Random Forest)*.

**Dictamen:** 
Se prohíbe cualquier manipulación algorítmica diseñada para sobrevivir a hardware de consumo. Mutilar el *dataset* anula la validez científica del Trabajo de Fin de Máster. El experimento se pausa en estado latente hasta el aprovisionamiento de un entorno de alta capacidad (**Google Colab Pro, High-RAM 32GB**). El bucle maestro final validado operará sobre el 100% de la partición manteniendo intacto el `fold_id` para garantizar la viabilidad de la comparativa.
