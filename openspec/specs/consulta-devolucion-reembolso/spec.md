# Consulta de estado de devolución y reembolso

> Origen: SPEC-22 · Grupo: Postventa · Requiere sesión: Sí · Depende de: [`solicitud-devolucion-cambio`](../solicitud-devolucion-cambio/spec.md) (SPEC-21), [`consulta-estado-pedido`](../consulta-estado-pedido/spec.md) (SPEC-17), Ventas (F3 y F4)

## Purpose

Mostrar al cliente el estado de sus solicitudes de devolución o cambio, incluida la resolución final y, cuando aplique, el estado del reembolso de dinero — sin importar desde qué canal se originó la solicitud.

## Contexto

🧩 Esta spec cubre la pestaña **"Reembolsos"** del historial de pedidos del wireframe, que muestra tarjetas como:

> Reembolso #R-0312 · EN REVISIÓN
> Solicitud: Talla incorrecta · Estado: Pendiente de aprobación

✅ El `api-contract.md` de Ventas (v1.3.0) resuelve todo lo que esta spec necesitaba (acuerdo A10):

- `GET /api/v2/devoluciones?clienteId=&estado=&tipo=&pagina=&tamano=` — listado paginado, **con `estadoReembolso` resumido en cada fila**.
- `GET /api/v2/devoluciones/{id}` — detalle que, cuando la resolución fue `DEVOLUCION_DINERO` y ya se procesó, incluye el bloque anidado `resolucion.reembolso{reembolsoId, estado, monto, moneda, transaccionPasarelaId, fechaEjecucion}`.

Una mejora sobre el diseño anterior: como el listado es por `clienteId` directamente contra Ventas, el chatbot ya no depende de su propio `devolucion_ref` para mostrar el historial — **trae todas las solicitudes del cliente, incluidas las registradas desde otros canales** (Marketplace, Retail), no solo las de este chat.

## Alcance

Incluye:
- Pestaña "Reembolsos" de `OrderHistoryPage`, con el listado completo del cliente desde Ventas.
- Consulta por código o por selección.
- Detalle: estado del expediente, tipo, motivo, evidencia (miniaturas, si las hubo), resolución y — si el resultado fue un reembolso — su estado completo.
- Preguntas directas ("¿ya me devolvieron el dinero?", "¿aprobaron mi cambio?").

### Fuera de alcance

- Apelar una solicitud rechazada.
- Cancelar una solicitud en curso.
- Ejecutar o reintentar el extorno: es F4 de Ventas.

## Requirements

### Requirement: Listar e identificar solicitudes
El sistema DEBE (SHALL) listar todas las solicitudes de devolución/cambio del cliente, consultando `GET /api/v2/devoluciones?clienteId=` directamente, sin importar el canal donde se originaron.

*Trazabilidad: SPEC-22 · Requisito 1.*

#### Scenario: Pestaña "Reembolsos"
- **DADO** un cliente con 2 solicitudes, una registrada desde el chatbot y otra desde el Marketplace
- **CUANDO** abre la pestaña "Reembolsos" de `OrderHistoryPage`
- **ENTONCES** se listan ambas, con código, pedido, fecha, motivo resumido, `estadoReembolso` (cuando aplica) y badge de estado

#### Scenario: Consulta por código
- **DADO** el mensaje "¿qué pasó con mi solicitud DEV-2026-0042?"
- **CUANDO** se consulta
- **ENTONCES** se obtiene `GET /api/v2/devoluciones/DEV-2026-0042` y se muestra su estado si pertenece al cliente

#### Scenario: Código ajeno o inexistente
- **DADO** un código que no existe o que pertenece a otro cliente
- **CUANDO** se consulta
- **ENTONCES** se responde "No encontré esa solicitud en tu cuenta" en ambos casos

#### Scenario: Sin solicitudes
- **DADO** un cliente sin devoluciones registradas en ningún canal
- **CUANDO** abre la pestaña "Reembolsos"
- **ENTONCES** se muestra "Aún no tienes solicitudes de cambio o devolución"

### Requirement: Mostrar el estado del expediente
El sistema DEBE (SHALL) mostrar el estado del expediente con una etiqueta clara y, cuando exista, el fundamento de un rechazo.

| Estado (F3) | Etiqueta |
|---|---|
| `SOLICITADA` | "Recibida" |
| `EN_EVALUACION` | "En revisión" |
| `APROBADA` | "Aprobada" |
| `RECHAZADA` | "Rechazada" |
| `COMPLETADA` | "Completada" |

*Trazabilidad: SPEC-22 · Requisito 2.*

#### Scenario: En revisión
- **DADO** una solicitud `EN_EVALUACION`
- **CUANDO** se consulta
- **ENTONCES** se muestra "En revisión · {motivo} · Pendiente de aprobación", igual que el wireframe

#### Scenario: Rechazada
- **DADO** una solicitud `RECHAZADA` con `resolucion.fundamento`
- **CUANDO** se consulta
- **ENTONCES** se muestra el fundamento registrado por el Gestor, sin que el LLM lo reformule (igual criterio de fidelidad que SPEC-20)

#### Scenario: Aprobada como cambio
- **DADO** una solicitud `APROBADA` con `tipo: CAMBIO`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Aprobada · Coordinando el cambio con logística"

### Requirement: Mostrar el estado del reembolso de dinero
El sistema DEBE (SHALL) mostrar, cuando la resolución fue `DEVOLUCION_DINERO` y Ventas ya incluye el bloque `resolucion.reembolso`, el monto, la moneda, el estado del extorno y la fecha de ejecución.

*Trazabilidad: SPEC-22 · Requisito 3.*

#### Scenario: Reembolso completado
- **DADO** una solicitud `APROBADA` con `resolucion.reembolso {estado: EXITOSO, monto: 129.90, moneda: PEN, fechaEjecucion: "2026-09-23T16:01:10Z"}`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Aprobada · Se reembolsaron S/ 129.90 el 23/09/2026"

#### Scenario: Reembolso aprobado, aún sin bloque de reembolso
- **DADO** una solicitud `APROBADA` con `tipo: DEVOLUCION_DINERO` y `resolucion.reembolso` todavía ausente (F4 no lo ha procesado)
- **CUANDO** se consulta
- **ENTONCES** se muestra "Aprobada · Tu reembolso está en proceso", sin inventar un monto ni una fecha que el backend no entregó

#### Scenario: Reembolso fallido
- **DADO** `resolucion.reembolso.estado: FALLIDO`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Hubo un problema al procesar tu reembolso; el equipo de ventas se contactará contigo", sin exponer detalles técnicos del fallo

### Requirement: Tolerancia a fallos
El sistema DEBE (SHALL) informar la indisponibilidad de Ventas sin mostrar estados inventados.

*Trazabilidad: SPEC-22 · Requisito 4.*

#### Scenario: Ventas no disponible
- **DADO** que Ventas no responde
- **CUANDO** se consulta una solicitud
- **ENTONCES** se muestra "No puedo consultar tus devoluciones ahora" con "Reintentar", y el código y la fecha de registro si existen en `devolucion_ref` local (solo para las que se originaron en este canal)

## Requisitos no funcionales

- **Seguridad:** el listado siempre filtra por `clienteId = sub` del token; el detalle compara la pertenencia antes de mostrar.
- **Fidelidad:** el fundamento de un rechazo y el detalle del reembolso se muestran tal como los registra Ventas, sin resumir ni reinterpretar.
- **Rendimiento:** la consulta tarda p95 ≤ 800 ms.
- **Mapeo de errores:** Ventas responde con la clave `codigo`; se normaliza al `code` interno.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
