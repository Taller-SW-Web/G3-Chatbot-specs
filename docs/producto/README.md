# Capa de producto — Canal Chatbot

Esta carpeta organiza las 23 specs de [`openspec/specs/`](../../openspec/specs/) en términos de producto ágil: alcance, épicas, historias de usuario, reglas de negocio y trazabilidad. **No reemplaza a las specs**: el comportamiento (requisitos y escenarios DADO/CUANDO/ENTONCES) se define únicamente en cada `spec.md`, y aquí solo se referencia por nombre.

## Contenido

| Documento | Para qué sirve | Lectores principales |
|---|---|---|
| [`alcance.md`](alcance.md) | Visión, roles, canal, capacidades incluidas y excluidas, dependencias externas, restricciones medibles, supuestos, riesgos y **preguntas abiertas** | PO, todo el equipo |
| [`epicas.md`](epicas.md) | Las 9 épicas (`EP-01` a `EP-09`), su valor, hito y dependencias, y el **mapeo a Linear** (proyectos, issues, sub-issues, milestones, prioridades y labels) | PO, Tech lead |
| [`historias/`](historias/) | Un archivo por épica con sus historias `HU-XXX-NN` (105 en total) y la asignación de las tareas de `design.md` a cada historia | Todo el equipo |
| [`reglas-negocio.md`](reglas-negocio.md) | Catálogo de las 162 reglas `RN-XXX-NN` extraídas de las specs, con su dueño (chatbot u otro módulo) | PO, QA |
| [`definicion-listo-terminado.md`](definicion-listo-terminado.md) | Definición de Listo y de Terminado, por niveles y con el rol que valida cada punto | Todo el equipo |
| [`trazabilidad.md`](trazabilidad.md) | Convenciones de IDs, matriz HU → spec → regla → endpoint → hito → prioridad, verificación de cobertura (109/109 requisitos) y totales | PO, QA, Tech lead |

### Historias por épica

| Archivo | Épica | Historias | Puntos |
|---|---|---|---|
| [`EP-01-identidad-sesion.md`](historias/EP-01-identidad-sesion.md) | Identidad y sesión | 14 | 50 |
| [`EP-02-conversacion.md`](historias/EP-02-conversacion.md) | Motor de conversación | 19 | 94 |
| [`EP-03-descubrimiento.md`](historias/EP-03-descubrimiento.md) | Descubrimiento de productos | 16 | 61 |
| [`EP-04-carrito.md`](historias/EP-04-carrito.md) | Carrito y stock | 8 | 36 |
| [`EP-05-checkout-pago.md`](historias/EP-05-checkout-pago.md) | Checkout y pago | 16 | 65 |
| [`EP-06-pedido-confirmacion.md`](historias/EP-06-pedido-confirmacion.md) | Grabación y confirmación del pedido | 8 | 32 |
| [`EP-07-seguimiento.md`](historias/EP-07-seguimiento.md) | Seguimiento de pedidos | 8 | 28 |
| [`EP-08-reclamos.md`](historias/EP-08-reclamos.md) | Reclamos | 7 | 22 |
| [`EP-09-devoluciones.md`](historias/EP-09-devoluciones.md) | Devoluciones y reembolsos | 9 | 31 |

## Cómo leerlo

1. **Empieza por [`alcance.md`](alcance.md)** para saber qué entra, qué no y qué está pendiente de decidir (sección *Preguntas abiertas*).
2. **Sigue con [`epicas.md`](epicas.md)** para ver cómo se agrupa el trabajo y en qué hito cae cada épica.
3. **Abre el archivo de historias de la épica** que vas a trabajar. Cada historia indica:
   - una tabla con épica, prioridad MoSCoW, estimación, hito, requisitos (`SPEC-NN · Req. N`), reglas (`RN-XXX-NN`) y dependencias externas (acuerdos `A1`–`A14`);
   - la historia en formato *Como / quiero / para*;
   - los criterios de aceptación, cada uno con el nombre exacto del escenario de la spec y un resumen de una línea. **El detalle está en la spec**, no se copia aquí.
4. **Consulta [`reglas-negocio.md`](reglas-negocio.md)** para los valores exactos (límites, plazos, reintentos) y quién es dueño de cada regla.
5. **Usa [`trazabilidad.md`](trazabilidad.md)** para ir de un requisito a su historia (o al revés) y para ver los totales por épica, hito y prioridad.
6. **Antes de mover una historia a `Ready` o a `Done`**, revisa [`definicion-listo-terminado.md`](definicion-listo-terminado.md).

## Mantenimiento

- Si cambia una spec (vía `openspec/changes/`), actualiza en este orden: reglas afectadas → historias → trazabilidad.
- Los IDs (`EP`, `HU`, `RN`) no se reutilizan: si una historia se elimina, su ID queda retirado; si se divide, las nuevas toman el siguiente número libre de su área.
- Los estados ✅/🟡 de las dependencias siguen a [`contratos-integracion.md`](../contratos-integracion.md) §6.
