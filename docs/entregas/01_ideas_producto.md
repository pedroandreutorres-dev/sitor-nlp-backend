# Propuestas de Ideación para Trabajo Fin de Máster (TFM)
**Alumno:** Pedro Andreu Torres  
**Máster en Data Science & Inteligencia Artificial**

---

## IDEA 1 (SELECCIONADA): SITOR - Sistema Inteligente de Triaje y Orquestación de Requerimientos

### 1. Qué problema o necesidad aborda
En el entorno de los BPO (Business Process Outsourcing) y grandes centros de soporte técnico (Helpdesk), el triaje inicial de incidencias sufre de ineficiencias críticas. Los agentes humanos (Front-Office) deben leer solicitudes en texto libre y clasificarlas en taxonomías complejas (casi 100 clases). La fatiga y la alta rotación de personal generan tasas de error del 15% al 25%. Esto provoca "falsos escalados": tickets que se derivan al departamento equivocado del Back-Office, generando cuellos de botella, pérdida de tiempo operativo (AHT) y un impacto financiero directo por horas malgastadas.

### 2. Por qué creo que puede tener impacto o valor
SITOR propone auditar y automatizar este enrutamiento utilizando modelos de Procesamiento de Lenguaje Natural (NLP) basados en arquitecturas *Transformer* (RoBERTa). El valor del proyecto es que no busca una automatización completa, sino implementar un **sistema basado en umbrales de confianza**: el modelo calculará su propia certidumbre estadística y solo intervendrá (sobrescribiendo la decisión del agente) cuando su confianza supere un límite de seguridad estricto (ej. > 0.80). El impacto será una liberación medible de capacidad operativa (FTEs) y una reducción del trabajo acumulado en el Nivel 2, demostrando rentabilidad (ROI).

### 3. Qué me motiva personalmente a trabajar en ella
Al conocer de primera mano el tejido corporativo y los problemas de orquestación en *Service Desks*, me motiva construir una solución que resuelva un problema real de negocio. Supone un reto técnico (pasar de *Machine Learning* clásico a *Deep Learning*) y me permite explorar cómo la Inteligencia Artificial puede integrarse en la empresa como una herramienta de apoyo y corrección de errores, más que como un mero experimento académico.

---

## IDEA 2 (DESCARTADA): Sistema Predictivo de Alerta Temprana para la ZBE de Ponferrada

### 1. Qué problema o necesidad aborda
El Ayuntamiento de Ponferrada ha implementado una Zona de Bajas Emisiones (ZBE). Sin embargo, el modelo de gestión actual es reactivo: las restricciones de tráfico se activan cuando la contaminación ya ha superado los límites, generando caos logístico repentino.

### 2. Por qué creo que puede tener impacto o valor
Se proponía un modelo proactivo cruzando datos de calidad del aire con predicciones meteorológicas para pronosticar picos de contaminación con 48 horas de antelación.

### 3. Qué me motiva personalmente a trabajar en ella
Aplicar *Machine Learning* predictivo a la infraestructura pública (*Smart City*) de mi propia ciudad para mejorar la sostenibilidad urbana.

---

## IDEA 3 (DESCARTADA): Detección Proactiva de Ransomware en Sistemas de Backup

### 1. Qué problema o necesidad aborda
Los proveedores de *Cloud Backup* se enfrentan al peligro de respaldar archivos ya encriptados por un Ransomware latente, sobrescribiendo la última copia sana del cliente.

### 2. Por qué creo que puede tener impacto o valor
Mediante detección de anomalías (Aprendizaje No Supervisado) sobre metadatos de telemetría (ratios de compresión, tiempos), la IA bloquearía el backup corrompido sin necesidad de leer archivos.

### 3. Qué me motiva personalmente a trabajar en ella
Construir una arquitectura de ciberseguridad aplicada al sector local para evitar desastres empresariales irremediables.
