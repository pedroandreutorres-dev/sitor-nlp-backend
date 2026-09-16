# 3. Error humano de escalado

## Tasa histórica recomendada

```text
TASA_ERROR_HUMANO_ESCALADO_PORCENTAJE: 15
```

El valor base recomendado para SITOR es un **15 % de tickets mal escalados por intervención humana**. En términos operativos, significa que aproximadamente 15 de cada 100 tickets son enviados inicialmente a una cola, técnico o departamento que no corresponde con la tripleta correcta y deben ser corregidos, reasignados o reencaminados.

Este porcentaje no significa que el agente sea incapaz de resolver el caso. Mide un defecto de **tipificación y routing inicial**:

```text
ticket correctamente resuelto por el equipo equivocado
= posible error de escalado
```

La métrica debe confirmarse mediante el historial de reasignaciones, no mediante la tasa general de escaladas.

## Definición exacta para SITOR

Se considera error humano de escalado cuando se cumplen simultáneamente estas condiciones:

1. El ticket recibe una primera tripleta humana.
2. Es enviado a una cola, técnico o departamento.
3. El equipo receptor determina que no es el destino correcto.
4. Se modifica la cola, el tipo, la prioridad o una combinación de ellos.
5. El ticket vuelve a entrar en otro circuito de tratamiento.

La tasa propuesta es:

$$
\text{Tasa de error de escalado} =
\frac{\text{tickets reasignados por error tras la primera asignación}}{\text{tickets inicialmente escalados}} \times 100
$$

Debe excluirse:

- Un cambio de cola solicitado por el cliente después de nueva información.
- Una reasignación planificada por el workflow.
- Un cambio de prioridad causado por la evolución del incidente.
- Un escalado correcto desde N1 a N2 o N3.
- Una transferencia técnica prevista en el procedimiento.

SITOR debe atacar los **rebotes evitables**, no todos los movimientos entre niveles.

## Evidencia encontrada

No existe, hasta donde muestran las fuentes públicas revisadas, un benchmark único y oficial que publique específicamente el porcentaje de tickets de telecomunicaciones enviados al técnico equivocado y devueltos por error. Las organizaciones suelen medirlo con nombres distintos:

- misrouting rate;
- reassignment rate;
- ticket bounce rate;
- first-time-right routing;
- ticket quality;
- escalations that were Level-1 capable.

Por tanto, no sería riguroso afirmar que existe una cifra universal para Vodafone, un BPO o el sector telco.

Sí existe evidencia de magnitud en service desks y soporte técnico:

| Fuente o referencia | Resultado | Interpretación |
|---|---:|---|
| MetricNet/HDI, PRL1C | 18,6 % de media | Tickets resueltos en soporte de escritorio que podrían y deberían haberse resuelto en Nivel 1 |
| MetricNet/HDI, organizaciones con SPOC | 15,3 % | Escalados evitables en organizaciones con punto único de contacto |
| MetricNet/HDI, sin SPOC | 22,8 % | Mayor proporción cuando existen accesos o derivaciones fuera del circuito único |
| MetricNet/HDI, distribución | 4–37 % | Variabilidad observada entre organizaciones |
| Benchmarks comerciales recientes | 12–18 % | Misrouting en routing manual en determinadas muestras |
| Otras recopilaciones comerciales | 15–25 % | Tickets reasignados al menos una vez en operaciones manuales |
| Casos comerciales individuales | 15–35 % | Valores observados antes de automatizar, pero no generalizables |

La referencia más sólida localizada es el indicador **Percent Resolved Level 1 Capable (PRL1C)** de MetricNet/HDI. Este mide el porcentaje de tickets cerrados por soporte de escritorio que podrían haberse resuelto en el service desk. Su media publicada es del 18,6 %, con un rango de 4–37 % y una mediana de 18,1 %. [web:149]

No es exactamente la misma métrica que el rebote de un ticket mal tipificado: un ticket puede estar correctamente escalado aunque finalmente se descubra que era resoluble en Nivel 1. Sin embargo, es una referencia relevante para cuantificar **defectos de escalado y asignación de trabajo entre niveles**.

La propia fuente muestra diferencias según el modelo operativo: las organizaciones con un modelo SPOC presentan un promedio del 15,3 %, frente al 22,8 % de las que no lo utilizan. [web:149]

Fuentes comerciales más recientes sitúan el misrouting manual alrededor del 12–18 % o 15–25 %, pero deben considerarse evidencia secundaria y no benchmarks oficiales de telecomunicaciones. [web:134][web:132]

## Valor seleccionado para el TFM

Se adopta:

```text
TASA_ERROR_HUMANO_ESCALADO_PORCENTAJE: 15
```

La elección se basa en tres razones:

1. Es coherente con el 15,3 % publicado para organizaciones con modelo SPOC.
2. Se encuentra dentro de los rangos recientes de misrouting manual de 12–18 % y 15–25 %.
3. Evita presentar el 18,6 % de PRL1C como si fuera exactamente una tasa de rebote de telecomunicaciones.

El 15 % debe describirse como una **hipótesis base calibrada**, no como un dato observado de un operador concreto.

## Escenarios de sensibilidad

| Escenario | Tasa | Tickets mal escalados con 14.500 tickets/mes | Uso |
|---|---:|---:|---|
| Buen control operativo | 10 % | 1.450 | Taxonomía madura y controles fuertes |
| Base recomendada | 15 % | 2.175 | Escenario principal de SITOR |
| Referencia central externa | 18,6 % | 2.697 | Valor de contraste con PRL1C |
| Alto | 25 % | 3.625 | Taxonomía compleja o routing manual débil |
| Estrés | 35 % | 5.075 | Operación con problemas graves de asignación |

Para las gráficas principales se recomienda utilizar 10 %, 15 % y 25 %. El 18,6 % es útil como referencia externa y el 35 % debe reservarse para un escenario de estrés, no para el caso normal.

## Aplicación al volumen SITOR

Con el escenario operativo ya definido:

```text
VOLUMEN_MENSUAL_TICKETS: 14.500
TASA_ERROR_HUMANO_ESCALADO_PORCENTAJE: 15
```

el volumen mensual de tickets con error de escalado sería:

$$
14.500 \times 0,15 = 2.175 \text{ tickets/mes}
$$

Si cada corrección activa requiere una media de 120 segundos, como se definió en el parámetro anterior:

$$
2.175 \times 120 = 261.000 \text{ segundos}
$$

Esto equivale a:

```text
72,5 horas mensuales de trabajo activo de back office
```

La cifra no incluye el retraso de SLA ocasionado por la espera entre colas, que debe modelarse como una métrica independiente.

## Dónde genera valor SITOR

SITOR puede generar valor en tres niveles:

### Prevención

Evita que el ticket sea enviado inicialmente a la cola incorrecta. Es la situación de mayor valor, porque evita el rebote y el retraso desde el primer momento.

### Detección temprana

Si no puede impedir el primer escalado, identifica la incoherencia antes de que el técnico comience un análisis profundo.

### Corrección asistida

Propone la tripleta correcta para que el agente de back office solo tenga que validar o aceptar la modificación.

La métrica clave no debe ser únicamente la exactitud global del clasificador, sino la reducción de:

```text
first_assignment_wrong
→ reassignment
→ queue bounce
```

## Impacto potencial

Si SITOR evita el 70 % de los errores de escalado que se producirían manualmente:

$$
2.175 \times 0,70 = 1.523 \text{ errores evitados/mes}
$$

Y si cada corrección manual consume 120 segundos:

$$
1.523 \times 120 = 182.760 \text{ segundos}
$$

Resultado aproximado:

```text
50,8 horas mensuales de trabajo activo potencialmente evitado
```

Este cálculo no cuantifica todavía el ahorro más importante: la reducción del tiempo de espera causado por el rebote, la mejora del cumplimiento de SLA y la menor ocupación de los equipos técnicos.

## Cómo medirlo en datos reales

La tasa debe obtenerse del histórico del CRM o ITSM, idealmente durante al menos 3–6 meses. Para cada ticket se necesitan:

```text
ticket_id
initial_queue
initial_type
initial_priority
first_assigned_team
assignment_timestamp
reassignment_timestamp
final_queue
final_type
final_priority
reassignment_reason
reassignment_count
```

Una regla reproducible sería marcar como error de escalado los tickets que:

```text
reassignment_count >= 1
AND reassignment_reason IN {wrong_queue, wrong_team, wrong_type, wrong_priority}
```

El denominador debe ser el número de tickets inicialmente escalados o enviados a back office, no el total de llamadas recibidas por el contact center.

También conviene separar:

| Indicador | Fórmula |
|---|---|
| Tasa de primer destino incorrecto | Tickets con primera asignación errónea / tickets escalados |
| Tasa de rebote | Tickets devueltos o reasignados / tickets escalados |
| Número medio de rebotes | Total de reasignaciones / tickets reasignados |
| Tiempo de corrección | Corrección de tripleta − primera apertura por el equipo |
| Tiempo de retraso | Inicio de trabajo del equipo correcto − primera asignación |

## Limitaciones

El 15 % no debe presentarse como una tasa oficial de Vodafone ni como un valor específico de telecomunicaciones. La evidencia pública más próxima procede de service desks y desktop support, donde la definición puede ser más amplia que la de SITOR.

Además, un ticket reasignado no siempre implica un error humano: puede ser una escalada legítima, una transferencia prevista o una actualización válida de prioridad. Por este motivo, en una implantación real la tasa debería calcularse a partir del motivo de reasignación o mediante una auditoría etiquetada por muestreo.

## Valor final

```text
TASA_ERROR_HUMANO_ESCALADO_PORCENTAJE: 15
```

Interpretación final:

> Se estima que el 15 % de los tickets que requieren escalado presentan una primera asignación humana incorrecta de cola, tipo, prioridad o departamento y generan al menos un rebote o reasignación. El escenario se acompaña de un rango de sensibilidad del 10–25 % y de un escenario de estrés del 35 %.

El 15 % es la cifra más defendible para el escenario base de SITOR: suficientemente respaldada por referencias de defectos de escalado y misrouting, pero sin atribuir a una fuente externa una precisión que las fuentes públicas no proporcionan.
