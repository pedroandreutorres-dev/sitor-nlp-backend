# Parámetros Base: Simulador de Retorno de Inversión (ROI) - Fase 5

Este documento define las constantes operativas innegociables para calcular el impacto financiero de SITOR en el BPO.
Rellena los valores entre corchetes con datos empíricos de tu experiencia en operaciones.

## 1. Volumen Operativo
Volumen total de tickets generados por el Front Office (N1) mensualmente y que serán auditados por el orquestador.
* **VOLUMEN_MENSUAL_TICKETS:** 14500

## 2. Macro-Eficiencia: Prevención de Falsos Escalados en Back Office (N2/BO)
Dado que SITOR no reemplaza al Front Office, el ahorro financiero (ROI) se genera al evitar que un ticket mal enrutado llegue a la cola equivocada de Back Office. Cuando esto ocurre sin SITOR, el agente de BO pierde tiempo identificando el error y reasignando la tripleta.

* **TASA_ERROR_HUMANO_FO_PORCENTAJE:** 15 (Porcentaje histórico de tickets que el Front Office escala erróneamente).
* **AHT_CORRECCION_MAL_ESCALADO_BO_SEGUNDOS:** 120 (Tiempo exacto en segundos que pierde un técnico de BO en identificar un falso escalado y corregir la tripleta manualmente).

## 3. Estructura de Costes (FTE)
Coste bruto por hora del perfil que sufre la ineficiencia (el agente de BO).
* **COSTE_HORA_AGENTE_BO_EUROS:** 12.48

---
**Nota MLOps:** Una vez rellenados los corchetes, notifícalo para inyectar estos parámetros estáticos en el simulador del Cuaderno 07.
