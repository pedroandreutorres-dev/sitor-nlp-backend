# Propuestas de Ideación para Trabajo Fin de Máster (TFM)
**Alumno:** Pedro Andreu Torres  
**Máster en Data Science & Inteligencia Artificial**

---

## IDEA 1: Sistema Predictivo de Alerta Temprana para la ZBE de Ponferrada

### 1. Qué problema o necesidad aborda
El Ayuntamiento de Ponferrada ha implementado una Zona de Bajas Emisiones (ZBE) equipada con sensores de calidad del aire. Sin embargo, el modelo de gestión actual es puramente **reactivo**: las restricciones de tráfico o los avisos a la población solo se activan cuando los umbrales de contaminación ($NO_2$, partículas) ya han superado los límites legales, lo que genera problemas logísticos repentinos para los ciudadanos.

### 2. Por qué creo que puede tener impacto o valor
Este proyecto propone la transición hacia un modelo **proactivo** mediante Inteligencia Artificial (Series Temporales / Machine Learning). Al cruzar los históricos de contaminación con variables meteorológicas predictivas (viento, lluvia, inversión térmica), el modelo podrá pronosticar picos de contaminación con 48-72 horas de antelación. Su valor principal es dotar al Ayuntamiento de una herramienta real de *Smart City* para emitir avisos preventivos y evitar llegar a los escenarios de restricción severa.

### 3. Qué me motiva personalmente a trabajar en ella
Como residente de Ponferrada, me motiva profundamente aplicar los conocimientos técnicos del máster para resolver un problema de infraestructura pública en mi propia ciudad. Es una excelente oportunidad para demostrar cómo los datos pueden mejorar la salud pública y facilitar la convivencia entre la movilidad urbana y la sostenibilidad ambiental.

---

## IDEA 2: Detección Proactiva de Ransomware en Sistemas de Backup (Caso: Kópius)

### 1. Qué problema o necesidad aborda
Las empresas proveedoras de servicios Cloud y copias de seguridad, como la firma local Kópius Backup, se enfrentan al reto de las "infecciones latentes" por Ransomware. El peligro real ocurre cuando un virus encripta los sistemas de un cliente y el software de backup realiza una copia de seguridad de esos archivos ya dañados, sobrescribiendo de forma automatizada la última copia sana sin que ningún técnico se dé cuenta a tiempo.

### 2. Por qué creo que puede tener impacto o valor
El proyecto plantea entrenar un modelo de **Aprendizaje No Supervisado (Detección de Anomalías)** basado exclusivamente en la telemetría y metadatos del servidor (tamaño de las copias, tiempo de ejecución, ratio de compresión, archivos modificados), garantizando la privacidad (RGPD) al no leer el contenido de los archivos. El impacto es enorme: la IA detectaría un patrón anómalo de encriptación en tiempo real y bloquearía la sobrescritura del backup, salvando la infraestructura del cliente.

### 3. Qué me motiva personalmente a trabajar en ella
Tengo la oportunidad de colaborar directamente con el sector tecnológico local (Kópius). Me apasiona la idea de construir una arquitectura de Machine Learning orientada a la ciberseguridad que no se quede en un ejercicio académico, sino que pueda ser integrada como una capa de seguridad real (I+D) en los sistemas de una pyme de mi entorno.

---

## IDEA 3: Viticultura de Precisión y Machine Learning en El Bierzo

### 1. Qué problema o necesidad aborda
El sector vitivinícola se enfrenta a pérdidas económicas drásticas debido a factores climáticos imprevisibles, especialmente las plagas (como el mildiu, dependiente de la humedad) y las heladas tardías de primavera. Actualmente, muchos viticultores aplican tratamientos químicos de forma preventiva o genérica, o reaccionan a las heladas cuando el daño en la vid ya es irreversible.

### 2. Por qué creo que puede tener impacto o valor
Mediante la extracción y procesamiento de datos climáticos históricos (ERA5/AEMET) y el uso de algoritmos predictivos, el objetivo es crear un modelo de *Forecasting* de riesgo agrícola. El modelo avisaría a las bodegas con días de antelación sobre la probabilidad exacta de una helada en coordenadas específicas o el riesgo de proliferación de hongos. El impacto es doble: ahorro económico al salvar las cosechas y mejora de la sostenibilidad al reducir drásticamente el uso de sulfatos innecesarios.

### 3. Qué me motiva personalmente a trabajar en ella
El sector del vino y la Denominación de Origen (D.O.) son el motor económico y cultural de la comarca de El Bierzo. Me entusiasma la idea de fusionar la tradición agrícola milenaria de mi tierra con la tecnología predictiva más avanzada, ayudando a modernizar el trabajo en el campo mediante la Inteligencia Artificial.
