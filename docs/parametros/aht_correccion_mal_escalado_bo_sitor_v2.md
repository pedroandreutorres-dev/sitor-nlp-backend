# 2. Micro-Eficiencia: Corrección de Escalado en Back Office

## Tiempo medio recomendado

```text
AHT_TRIAJE_N1_SEGUNDOS: 120
```

El valor recomendado para el escenario base es **120 segundos**, es decir, **2 minutos de trabajo activo por ticket mal escalado**.

Este valor sustituye la estimación anterior de 420 segundos. La corrección se debe a que la métrica no representa un triaje técnico completo ni una investigación de la incidencia, sino una actuación operativa concreta:

1. Abrir el ticket.
2. Leer el asunto y el cuerpo.
3. Detectar que la cola o la tripleta no es correcta.
4. Seleccionar la cola, el tipo y la prioridad adecuados.
5. Guardar el cambio y reenviar el ticket.

No se incluye la resolución de la avería o reclamación, el diagnóstico técnico, la consulta extensa de sistemas externos ni el tiempo de espera en cola.

## Interpretación de N1

En este TFM, N1 no debe entenderse necesariamente como el agente que atiende al cliente. La variable representa al **primer agente o equipo de back office que recibe el ticket y corrige su escalado**.

Por precisión, la denominación recomendada sería:

```text
AHT_CORRECCION_MAL_ESCALADO_BO_SEGUNDOS: 120
```

Si el formato del proyecto exige conservar la variable original, puede mantenerse:

```text
AHT_TRIAJE_N1_SEGUNDOS: 120
```

con la siguiente definición:

> Tiempo activo que emplea el primer equipo de back office en identificar y corregir manualmente la tripleta de un ticket mal escalado, sin incluir la resolución de la incidencia ni las esperas de cola.

## Evidencia encontrada

No se ha encontrado un benchmark público, específico y suficientemente sólido de operadores de telecomunicaciones que publique el tiempo exacto empleado por un agente de back office únicamente en corregir una tripleta mal escalada. Las fuentes disponibles suelen mezclar:

- triaje inicial;
- primera respuesta;
- ticket handle time;
- diagnóstico;
- resolución;
- espera en cola;
- tiempo total hasta el cierre.

Por tanto, no sería correcto presentar 120 segundos como una cifra oficial del sector. Debe presentarse como una **hipótesis operativa calibrada** con el flujo real descrito y con la experiencia operativa aportada para el caso.

Las fuentes comparables muestran que los tiempos cambian radicalmente según el alcance de la métrica:

| Referencia | Tiempo publicado | Qué incluye o representa |
|---|---:|---|
| ACW general de contact center | ~45 s | Trabajo administrativo posterior a una interacción; no equivale a corregir un ticket |
| ACW habitual en contact center | 30–90 s | Notas, códigos y actualización del sistema |
| Triaje técnico completo | 3–8 min | Clasificación, prioridad y recopilación inicial de contexto |
| Corrección de misrouting con contexto adicional | 5–15 min | Corrección más búsqueda de información omitida |
| Tiempo recomendado para corrección SITOR | 1–3 min | Solo lectura breve, corrección de tripleta y reencolado |

Las referencias de ACW sitúan el trabajo administrativo posterior normalmente entre 30 y 90 segundos, mientras que Verint menciona un promedio aproximado de 45 segundos en contact centers. [web:86][web:87] Sin embargo, esas cifras no incluyen necesariamente abrir un ticket de back office y comprobar la coherencia de la tripleta.

En sentido contrario, algunas referencias de service desk estiman entre 3 y 8 minutos para un triaje técnico completo y entre 5 y 15 minutos para corregir un ticket mal encaminado cuando hay que buscar contexto adicional. [web:111] Esas cifras son más amplias que el proceso SITOR planteado, porque pueden incluir diagnóstico preliminar, revisión de historial o búsqueda de información faltante.

Por último, benchmarks de ticket handle time alrededor de 8,6 minutos incluyen una parte mucho más extensa del trabajo del agente y no deben utilizarse directamente como tiempo de corrección del escalado. [web:104]

## Incorporación de la experiencia operativa

La experiencia descrita —correcciones que pueden resolverse en aproximadamente un minuto, pero que en otros casos requieren dos o tres— es coherente con una distribución heterogénea por complejidad.

No debe modelarse el proceso con un único tiempo idéntico para todos los tickets. Una distribución más realista sería:

| Tipo de corrección | Proporción simulada | Tiempo |
|---|---:|---:|
| Muy clara | 30 % | 60 s |
| Estándar | 45 % | 120 s |
| Ambigua o con más contexto | 20 % | 180 s |
| Excepcional | 5 % | 300 s |

La media ponderada de esta distribución es:

$$
(0,30 \times 60) + (0,45 \times 120) + (0,20 \times 180) + (0,05 \times 300) = 132 \text{ segundos}
$$

El valor exacto resultante es 132 segundos, pero se recomienda redondear el escenario base a:

```text
120 segundos
```

La diferencia entre 120 y 132 segundos no debe interpretarse como precisión estadística; refleja que se trata de una parametrización de simulación sin datos observacionales del CRM.

## Escenarios de sensibilidad

| Escenario | Tiempo | Interpretación |
|---|---:|---|
| Rápido | 60 s | Error evidente y cola de destino conocida |
| Base | 120 s | Corrección habitual de una tripleta incorrecta |
| Alto | 180 s | Ticket ambiguo o con lectura más detenida |
| Excepcional | 300 s | Falta de contexto o comprobación adicional |

Para las gráficas se recomienda usar **60, 120 y 180 segundos**. El valor de 300 segundos debe reservarse para un escenario de estrés y no para el caso normal.

## Cálculo con el volumen operativo

Usando los parámetros definidos anteriormente:

```text
VOLUMEN_MENSUAL_TICKETS: 14.500
TASA_TICKETS_MAL_ESCALADOS: 15 %
AHT_TRIAJE_N1_SEGUNDOS: 120
```

El número estimado de tickets mal escalados es:

$$
14.500 \times 0,15 = 2.175
$$

El tiempo activo mensual destinado a corregirlos manualmente sería:

$$
2.175 \times 120 = 261.000 \text{ segundos}
$$

| Medida | Resultado aproximado |
|---|---:|
| Tickets mal escalados al mes | 2.175 |
| Tiempo activo de corrección | 261.000 s |
| Horas de trabajo de back office | 72,5 h |
| Jornadas de 8 horas | 9,1 jornadas |
| FTE mensuales de 160 h | 0,45 FTE |

Si se utilizase una media de 132 segundos en lugar de 120, el tiempo sería de 79,9 horas mensuales. La diferencia queda cubierta por el análisis de sensibilidad.

## Ahorro potencial de SITOR

Si SITOR evita o corrige automáticamente el 70 % de los mal escalados, el tiempo activo potencialmente evitado sería:

$$
2.175 \times 0,70 \times 120 = 182.700 \text{ segundos}
$$

Equivale aproximadamente a:

```text
50,75 horas mensuales
0,32 FTE mensuales de trabajo activo
```

Esta cifra es ahorro de capacidad operativa, no necesariamente reducción de plantilla. Puede convertirse en menor backlog, más capacidad del back office, reducción de horas extraordinarias o mejora del SLA.

## Diferencia entre trabajo activo y retraso del ticket

Un ticket mal escalado puede provocar un retraso total mucho mayor que los 120 segundos de trabajo activo. La espera hasta que el primer equipo lo revise, el tiempo de reencolado y la espera en la cola correcta deben medirse separadamente.

```text
TIEMPO_ACTIVO_CORRECCION_BO_SEGUNDOS: 120
TIEMPO_TOTAL_RETRASO_POR_MAL_ESCALADO: métrica independiente
```

No debe atribuirse al agente todo el tiempo transcurrido entre la primera asignación y la llegada al departamento correcto.

## Validación futura

La cifra debe validarse en una PoC utilizando marcas temporales del sistema de tickets:

```text
ticket_first_opened_by_assigned_team
ticket_misroute_detected
ticket_triplet_corrected
ticket_rerouted
```

La métrica recomendada es:

$$
T_{corrección} =
T_{triplet\_corrected} - T_{ticket\_first\_opened\_by\_assigned\_team}
$$

Siempre que sea posible, deben excluirse estados de espera, pausas y bloqueos del sistema. Se recomienda informar de la mediana, p75, p90 y media truncada, desglosados por tipo de incidencia y cola de destino.

## Valor final

```text
AHT_TRIAJE_N1_SEGUNDOS: 120
```

Interpretación final:

> Tiempo activo medio estimado de 2 minutos que un agente de back office emplea en detectar que un ticket está mal escalado, corregir manualmente la cola, el tipo y la prioridad, y reenviarlo al circuito adecuado, sin incluir la resolución ni los tiempos de espera.

El intervalo de sensibilidad recomendado es de **60–180 segundos**, con casos excepcionales de hasta 300 segundos. Esta hipótesis es más coherente con el flujo operativo descrito y con la experiencia de que muchas correcciones se realizan en uno, dos o tres minutos.
