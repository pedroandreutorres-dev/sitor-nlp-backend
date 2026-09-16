# 4. Estructura de Costes (FTE)

## Coste bruto por hora del agente

```text
COSTE_HORA_AGENTE_N1_EUROS: 12,48
```

## Perfil utilizado

Para el escenario de SITOR, el perfil más apropiado no es necesariamente el de un teleoperador básico. El agente que recibe el ticket en back office y puede detectar y corregir la tripleta se aproxima más a:

- Gestor/a telefónico/a.
- Gestor/a de clientes.
- Teleoperador/a especialista, si la empresa utiliza esa denominación.
- Agente de back office con funciones de clasificación y reasignación.

La clasificación concreta depende de la empresa y del contenido real del puesto. En el III Convenio colectivo estatal de Contact Center, la tabla de 2026 sitúa el puesto de **Gestor Telefónico** en el nivel 9, mientras que **Teleoperador / Operador Especialista** aparece en el nivel 10. [web:152][web:156]

## Tabla salarial oficial 2026

La Resolución de 23 de febrero de 2026, publicada en el BOE el 6 de marzo de 2026, registra las tablas salariales de 2026 del Convenio colectivo estatal de Contact Center. El incremento aplicado a las tablas es del 3,4 %. [web:152]

| Nivel | Perfil orientativo | Salario anual bruto | Salario base mensual, 14 pagas | Salario mensual con pagas prorrateadas |
|---:|---|---:|---:|---:|
| 10 | Teleoperador/a / Operador/a especialista | 17.139,58 € | 1.224,26 € | 1.428,30 € |
| 9 | Gestor/a telefónico/a | 18.052,54 € | 1.289,47 € | 1.504,38 € |

El salario anual publicado incluye las dos pagas extraordinarias. La tabla de 39 horas semanales utiliza una jornada anual de 1.764 horas. [web:152][web:156]

## Conversión a coste salarial por hora

Para evitar mezclar conceptos, se distinguen dos valores:

### Salario bruto por hora

El salario bruto horario se calcula dividiendo el salario anual entre las horas anuales del convenio:

| Perfil | Cálculo | Salario bruto/hora |
|---|---:|---:|
| Teleoperador/a especialista | 17.139,58 € / 1.764 h | 9,72 €/h |
| Gestor/a telefónico/a | 18.052,54 € / 1.764 h | 10,23 €/h |

### Coste empresarial estimado por hora

La variable del TFM se denomina “coste bruto por hora”, pero para un análisis de ROI de SITOR conviene distinguir el salario bruto del coste laboral total de la empresa. El coste empresarial debe incluir, como mínimo:

- Cotizaciones empresariales a la Seguridad Social.
- Formación y prevención.
- Vacaciones y permisos.
- Absentismo y tiempos no productivos.
- Equipamiento y costes indirectos, si se desea un cálculo completo.

Aplicando un factor prudente del 1,22 sobre el salario bruto, para representar aproximadamente cotizaciones y costes laborales directos adicionales:

| Perfil | Salario bruto/hora | Factor empresarial | Coste empresarial estimado/hora |
|---|---:|---:|---:|
| Teleoperador/a especialista | 9,72 € | 1,22 | 11,86 € |
| Gestor/a telefónico/a | 10,23 € | 1,22 | 12,48 € |

El valor recomendado para SITOR es el del **gestor/a telefónico/a**, porque el trabajo descrito implica revisar contexto, validar la tripleta y corregir un escalado, no limitarse a una operación administrativa elemental.

## Valor recomendado para el TFM

```text
COSTE_HORA_AGENTE_N1_EUROS: 12,48
```

Este valor representa un coste empresarial horario estimado para un perfil equivalente a Gestor/a telefónico/a de nivel 9 del convenio estatal de Contact Center.

Si quieres que la variable represente estrictamente el salario bruto del trabajador, sin cotizaciones empresariales, el valor sería:

```text
COSTE_SALARIAL_BRUTO_HORA_AGENTE_N1_EUROS: 10,23
```

La diferencia debe quedar explícita en el TFM:

```text
SALARIO_BRUTO_HORA: 10,23 €/h
COSTE_EMPRESARIAL_ESTIMADO_HORA: 12,48 €/h
```

## Por qué no usar directamente el nivel 10

El nivel 10, correspondiente a Teleoperador/a u Operador/a especialista, ofrece un salario bruto horario aproximado de 9,72 €. Puede ser correcto si el agente de back office solo selecciona una cola predefinida y realiza una modificación sencilla.

Sin embargo, el caso de SITOR contempla que la persona debe:

1. Revisar el texto del ticket.
2. Detectar una incoherencia de enrutamiento.
3. Interpretar la incidencia.
4. Corregir cola, tipo y prioridad.
5. Reenviar el caso al departamento correcto.

Por ello, el nivel 9 es una aproximación más prudente para el agente que realmente realiza la corrección. Las denominaciones de las empresas pueden variar; lo importante es documentar las funciones, no únicamente el nombre interno del puesto.

## Sensibilidad de costes

| Escenario | Perfil | Coste empresarial estimado/hora |
|---|---|---:|
| Bajo | Teleoperador/a especialista, nivel 10 | 11,86 € |
| Base | Gestor/a telefónico/a, nivel 9 | 12,48 € |
| Alto | Gestor especialista con complementos | 13,50–15,00 € |

El escenario alto no procede directamente de una tabla salarial única: debe utilizarse solo si se añaden pluses, complementos de puesto, turnicidad, nocturnidad, festivos o costes indirectos adicionales.

## Ejemplo aplicado al ahorro de SITOR

Con los parámetros definidos anteriormente:

```text
TICKETS_MAL_ESCALADOS_MES: 2.175
AHT_CORRECCION_MAL_ESCALADO_BO_SEGUNDOS: 120
COSTE_HORA_AGENTE_N1_EUROS: 12,48
```

El tiempo activo mensual de corrección es:

$$
2.175 \times 120 / 3.600 = 72,5 \text{ horas}
$$

El coste laboral mensual asociado sería:

$$
72,5 \times 12,48 = 904,80 \text{ €}
$$

Si SITOR evitara el 70 % de esas correcciones manuales:

$$
904,80 \times 0,70 = 633,36 \text{ € de capacidad mensual potencialmente liberada}
$$

Este cálculo solo cuantifica el trabajo activo de corrección. No incluye:

- El retraso de SLA causado por el rebote.
- El coste de oportunidad del técnico que recibe el ticket equivocado.
- El trabajo duplicado de apertura y análisis.
- El impacto en backlog, disponibilidad y satisfacción del cliente.

## Limitaciones

El BOE publica salarios base y complementos del convenio, no el coste empresarial completo de cada trabajador. Por eso, los 12,48 €/h son una **estimación de coste laboral directo**, calculada aplicando un factor de 1,22 al salario bruto horario.

El factor debe sustituirse por el coste real del centro si se dispone de:

- porcentaje efectivo de cotización;
- absentismo;
- vacaciones y permisos;
- formación;
- incentivos;
- pluses de nocturnidad o festivos;
- coste de supervisión y estructura.

No debe presentarse el valor como una tarifa comercial de BPO ni como el precio facturado al cliente.

## Valor final

```text
COSTE_HORA_AGENTE_N1_EUROS: 12,48
```

Interpretación final:

> Coste empresarial horario estimado de un agente de back office con funciones equivalentes a Gestor/a telefónico/a del nivel 9 del Convenio colectivo estatal de Contact Center 2026. El salario bruto horario de referencia es aproximadamente 10,23 €/h, y el valor de 12,48 €/h incorpora un factor prudente del 22 % para costes empresariales laborales directos.
