# CONSOLIDADO DE PARÁMETROS FINANCIEROS Y OPERATIVOS

Este documento define las variables estructurales del negocio utilizadas por el orquestador y el simulador de ROI de SITOR para calcular la macro-eficiencia operativa del modelo.

## 1. Volumen Operativo

```text
VOLUMEN_MENSUAL_TICKETS: 14.500
```

**Definición operativa:** El volumen no representa el total de llamadas recibidas por el contact center, sino el subconjunto de tickets de soporte, averías o reclamaciones (Sector Telco) susceptibles de ser auditados por SITOR (Nivel 1 hacia Nivel 2). 

## 2. Coste del Falso Escalado (Micro-Eficiencia)

```text
AHT_TRIAJE_N1_SEGUNDOS: 120
```

**Interpretación:** Tiempo medio (en segundos) que un técnico especializado de Back Office (Nivel 2) pierde en abrir un ticket mal enrutado, leerlo, identificar que no pertenece a su cola, seleccionar la tipología correcta y reasignarlo. Se estiman **2 minutos** perdidos por cada impacto de ineficiencia.

```text
COSTE_HORA_AGENTE_N2: 12.48
```
**Justificación:** Coste por hora (en euros) de un agente especializado de Nivel 2, utilizado para monetizar los ahorros de tiempo.

## 3. Tasa de Error Humano

```text
TASA_ERROR_HUMANO_ESCALADO_PORCENTAJE: 15
```

**Interpretación de Negocio:**
Se estima que el **15%** de los tickets escalados presentan una primera asignación humana incorrecta (Tripleta Operativa equivocada) y generan al menos un rebote o reasignación.

**Escenarios de Estrés (Tiempos de Guerra):**
Debido a la alta rotación (attrition) característica de los BPO, cuando entran oleadas de agentes sin experiencia o existen picos de demanda masiva, este error puede elevarse al **25%**. Es en estos escenarios donde SITOR despliega su máximo valor como cortafuegos operativo, reduciendo dinámicamente su umbral algorítmico (ej: `Softmax >= 0.85`) para absorber esta entropía.

## 4. Impacto Potencial y Break-Even

Al cruzar los 14.500 tickets con un error humano del 15% y un coste de 120 segundos a 12,48 €/h, se establece la línea base de pérdidas operativas del BPO. SITOR intersecta esta métrica mediante validación cruzada y simulación:

*   **Punto Dulce Operativo (Base):** Con un umbral en **0.86**, SITOR garantiza máxima precisión (90.91%) sacrificando levemente la automatización (7.5%) para asegurar rentabilidad neta (26,72 €/mes).
*   **Punto de Estrés Operativo:** Con un umbral en **0.85**, aumenta el secuestro de tickets (8.8% de automatización) manteniendo una precisión férrea (89.63%), logrando un ahorro de 77,33 €/mes para compensar económicamente el caos del Front Office.

El verdadero objetivo financiero no es reemplazar agentes, sino **blindar los SLAs**, desestrangular el L2 y amortizar la inexperiencia del personal junior sin que el cliente corporativo perciba caídas en la calidad del servicio.