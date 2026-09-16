# 1. Volumen Operativo

## Volumen mensual de tickets

```text
VOLUMEN_MENSUAL_TICKETS: 14.500
```

## Definición operativa

El volumen indicado no representa el total de llamadas, chats o contactos recibidos por el contact center. En SITOR, un ticket es un caso operativo que contiene una incidencia, avería, reclamación o solicitud que requiere clasificación y posible derivación a un circuito de back office o de Nivel 2.

Por tanto, el valor corresponde al número estimado de tickets que entran mensualmente en el sistema y que pueden ser evaluados por el orquestador para validar o corregir la tripleta:

```text
cola + tipo + prioridad
```

## Estimación utilizada

El escenario se ha construido para un contact center de tamaño medio-grande, con aproximadamente 200 agentes en el turno de mañana y otros 200 en el turno de tarde.

| Parámetro | Valor estimado |
|---|---:|
| Agentes simultáneos por turno | 200 |
| Número de turnos diarios | 2 |
| Duración de cada turno | 8 horas |
| Días operativos mensuales | 30 |
| AHT medio utilizado | 8 minutos |
| Ocupación media | 82 % |
| Llamadas atendidas estimadas al mes | 59.000 |
| Casos que generan un registro | 35 % |
| Casos que requieren back office | 70 % |
| Tickets evaluables por SITOR | 14.466 |

El cálculo aplicado es:

$$
\text{Tickets SITOR} = \text{llamadas atendidas} \times \text{tasa de creación de caso} \times \text{tasa de back office}
$$

$$
59.040 \times 0,35 \times 0,70 = 14.466
$$

Para facilitar la interpretación en la presentación, el resultado se redondea a:

```text
14.500 tickets mensuales
```

## Alcance de los tickets

El volumen incluye principalmente casos como:

- Averías de fibra, móvil, televisión o servicios convergentes.
- Reclamaciones de facturación, cargos o compensaciones.
- Problemas de portabilidad, provisión o activación.
- Incidencias que requieren intervención técnica de Nivel 2.
- Solicitudes derivadas a departamentos especializados.
- Casos cuya cola, tipo o prioridad deben ser validados antes de su tratamiento.

No se incluyen las interacciones resueltas completamente en el primer contacto ni el volumen total de llamadas del operador.

## Escenarios de sensibilidad

El valor de 14.500 tickets mensuales debe considerarse el escenario base de la simulación, no un dato interno de un operador concreto. Para comprobar la robustez del sistema, se recomienda evaluar también dos escenarios alternativos:

| Escenario | Tickets mensuales | Uso recomendado |
|---|---:|---|
| Conservador | 7.000 | Operación con menor tasa de creación de casos o alcance parcial |
| Base | 14.500 | Escenario principal del TFM |
| Alto | 27.500 | Mayor complejidad, más casos registrados o varios servicios integrados |

## Limitaciones y justificación

No se ha localizado una estadística pública que indique directamente el número de tickets de back office generados por un contact center concreto con esta estructura de agentes. Las empresas suelen publicar llamadas, contactos, reclamaciones o transferencias, pero no la combinación exacta de creación de caso, derivación a Nivel 2 y errores de tipificación.

Por ello, el valor se define como una hipótesis operativa reproducible, calibrada con parámetros habituales de planificación de contact centers y con referencias públicas de grandes operadores de telecomunicaciones. Vodafone, por ejemplo, comunicó más de 42 millones de conversaciones asistidas mensuales a nivel de grupo en su informe anual de 2020; esa magnitud sirve únicamente para contextualizar la escala del sector y no se extrapola directamente a este centro.

La variable debe interpretarse, por tanto, como:

> Número mensual de tickets de avería, reclamación o solicitud especializada que entran en el circuito de back office y son susceptibles de ser auditados por SITOR.

## Valor final para la ficha del proyecto

```text
VOLUMEN_MENSUAL_TICKETS: 14.500
```

Para los cálculos internos puede conservarse el valor exacto de 14.466 tickets y utilizar 14.500 únicamente como valor redondeado en tablas, gráficas y diapositivas.
