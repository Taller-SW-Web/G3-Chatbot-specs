# EP-06 · Grabación y confirmación del pedido — Historias de usuario

> Specs: [SPEC-15](../../../openspec/specs/grabacion-pedido/spec.md), [SPEC-16](../../../openspec/specs/notificacion-confirmacion/spec.md) · Área `PED` · 8 historias · 32 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.

---

## HU-PED-01 · Registrar mi pedido en Ventas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 8 | Hito 4 | `SPEC-15 · Req. 1` | RN-PED-01, RN-PED-02, RN-PED-03 | Ventas ✅ (A8, A14) |

**Como** cliente que confirmó su compra, **quiero** que mi pedido quede registrado en el sistema de ventas con exactamente lo que acepté, **para** que se prepare y se me entregue.

**Criterios de aceptación**
- `SPEC-15 · Req. 1 · Scenario: Pedido creado` — ante `201` se guarda `pedido_ref` (`CREADO`) y se habilita el formulario de pago.
- `SPEC-15 · Req. 1 · Scenario: Ventas rechaza por stock` — ante `409` no se crea el checkout de pago, el carrito vuelve a `ACTIVO` y se muestra qué cambió.
- `SPEC-15 · Req. 1 · Scenario: Datos incompletos` — ante `400` se registra un error interno y se pide revisar los datos.
- `SPEC-15 · Req. 1 · Scenario: Ventas no disponible al crear` — tras 5 s se responde `503`, no se pide la tarjeta y se aclara que no hubo cobro.
- `SPEC-15 · Req. 1 · Scenario: Reintento con la misma clave` — la misma `Idempotency-Key` devuelve el mismo `pedidoId`.

**Prioridad:** Must: es la "grabación del pedido" que exige el curso.

**Notas:** incluye `SnapshotBuilder` (compartido con HU-PED-04) y `VentasClient` con la normalización `codigo` → `code`. RNF: creación p95 ≤ 1,5 s; `X-Correlation-Id` propagado a Ventas.

---

## HU-PED-02 · Confirmar mi pedido pagado aunque Ventas falle temporalmente

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 8 | Hito 4 | `SPEC-15 · Req. 2` | RN-PED-04, RN-PED-05, RN-PED-06 | Ventas ✅ (A8: `/pagos/notificacion`) |

**Como** cliente que pagó, **quiero** ver la confirmación de mi pedido y tener la garantía de que el pago se informará a ventas aunque haya fallas, **para** no perder mi compra ni pagar dos veces.

**Criterios de aceptación**
- `SPEC-15 · Req. 2 · Scenario: Notificación exitosa` — el outbox notifica el pago, `pedido_ref` pasa a `PAGADO_NOTIFICADO`, el carrito a `CONVERTIDO`, se encola el correo y se muestra `CONFIRMACION_PEDIDO`.
- `SPEC-15 · Req. 2 · Scenario: Ventas cae después del cobro` — el worker reintenta 5 veces con backoff y el chat muestra "Pago aprobado. Estamos confirmando tu pedido…".
- `SPEC-15 · Req. 2 · Scenario: Montos inconsistentes` — un `400` no se reintenta y se alerta para revisión.
- `SPEC-15 · Req. 2 · Scenario: Pedido en un estado que no admite la notificación` — un `409` no se reintenta y se registra para revisión manual.

**Prioridad:** Must: ningún pago aprobado puede quedar sin notificar.

**Notas:** incluye la tabla `outbox`, el `OutboxWorker` y `PendingConfirmation` (sondeo cada 5 s, máx. 2 min).

---

## HU-PED-03 · Liberar los pedidos que no se pagaron

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 3 | Hito 4 | `SPEC-15 · Req. 3` | RN-PED-06, RN-PED-07 | Ventas ✅ (A9: `/anulaciones`) |

**Como** negocio, **quiero** que los pedidos cuyo pago falló o expiró se anulen automáticamente en Ventas, **para** no dejar pedidos `CREADO` colgados que distorsionen stock y reportes.

**Criterios de aceptación**
- `SPEC-15 · Req. 3 · Scenario: Anulación directa` — el outbox `SOLICITAR_ANULACION` recibe `200` con `ANULADO` y `pedido_ref` pasa a `ANULADO`.
- `SPEC-15 · Req. 3 · Scenario: Pedido ya avanzó de estado` — ante `409` se registra la alerta y no se reintenta.

**Prioridad:** Must: completa los caminos de fallo de HU-CHK-15 y HU-CHK-16.

---

## HU-PED-04 · Garantizar que se registra exactamente lo confirmado

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 2 | Hito 4 | `SPEC-15 · Req. 4` | RN-PED-08, RN-PED-09 | — |

**Como** cliente, **quiero** que los importes registrados en mi pedido coincidan con los que vi y confirmé, **para** confiar en que no se me cobra un monto distinto.

**Criterios de aceptación**
- `SPEC-15 · Req. 4 · Scenario: Verificación del total` — si la suma no cuadra a 0,01, se aborta con error interno y no se crea el pedido.
- `SPEC-15 · Req. 4 · Scenario: Líneas no disponibles` — las líneas "Ya no disponible" se excluyen de `items`.

**Prioridad:** Must: es un control de integridad del dinero (simulado).

---

## HU-PED-05 · Recibir el correo de confirmación de mi compra

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 5 | Hito 4 | `SPEC-16 · Req. 1` | RN-PED-10, RN-PED-14 | Proveedor SMTP (Mailtrap en desarrollo) |

**Como** cliente que compró, **quiero** recibir un correo con el detalle de mi pedido, **para** tener una constancia fuera del chat y un enlace para consultar su estado.

**Criterios de aceptación**
- `SPEC-16 · Req. 1 · Scenario: Correo enviado` — el worker envía el correo con el asunto y el detalle completo, y `notificacion` queda `ENVIADA`.
- `SPEC-16 · Req. 1 · Scenario: Contenido fiel al pedido` — los importes coinciden con el snapshot enviado a Ventas y la tarjeta aparece enmascarada.

**Prioridad:** Must: el curso exige notificaciones por correo del pedido al cliente.

**Notas:** RNF: plantilla probada en Gmail y Outlook (web y móvil), ancho máximo de 600 px; envío dentro de los 60 s en el 95 % de los casos.

---

## HU-PED-06 · Recibir un único correo aunque haya fallos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 3 | Hito 4 | `SPEC-16 · Req. 2` | RN-PED-10, RN-PED-11 | Proveedor SMTP |

**Como** cliente, **quiero** recibir la confirmación una sola vez, aunque el sistema reintente por fallas del correo, **para** no confundirme con correos duplicados.

**Criterios de aceptación**
- `SPEC-16 · Req. 2 · Scenario: Reproceso del evento` — un correo ya `ENVIADA` no se reenvía (clave única `pedido_id + tipo`).
- `SPEC-16 · Req. 2 · Scenario: Proveedor SMTP caído` — se reintenta hasta 3 veces (1, 5 y 15 min) y luego queda `FALLIDA` sin afectar el pedido.

**Prioridad:** Must: sin idempotencia, los reintentos del outbox duplicarían correos.

---

## HU-PED-07 · Ver mi compra confirmada aunque el correo se demore

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Must | 1 | Hito 4 | `SPEC-16 · Req. 3` (escenario 1) | RN-PED-12 | — |

**Como** cliente, **quiero** que el chat me confirme la compra sin depender del correo, **para** saber que todo salió bien aunque el correo llegue después.

**Criterios de aceptación**
- `SPEC-16 · Req. 3 · Scenario: Confirmación en el chat sin correo` — el mensaje dice "Te enviaremos la confirmación a m****a@…", sin prometer que ya llegó.

**Prioridad:** Must: el correo no puede bloquear la confirmación de la compra.

---

## HU-PED-08 · Pedir el reenvío del correo de confirmación

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-06 | Should | 2 | Hito 4 | `SPEC-16 · Req. 3` (escenario 2) | RN-PED-13 | Proveedor SMTP |

**Como** cliente que no encuentra el correo, **quiero** pedir que me lo reenvíen, **para** tener mi constancia sin contactar a soporte.

**Criterios de aceptación**
- `SPEC-16 · Req. 3 · Scenario: El cliente pide reenviar el correo` — se sugiere revisar spam y se ofrece "Reenviar" (máx. 2 por pedido).

**Prioridad:** Should: comodidad posterior a la compra; la confirmación principal ya existe.

**Notas:** el botón "Reenviar correo" vive en el detalle del pedido (SPEC-17). Ver la pregunta abierta sobre el tipo `REENVIO_CONFIRMACION` frente a la clave única de `notificacion` ([`alcance.md`](../alcance.md#preguntas-abiertas)).

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-15 | T1 `[BE]` SnapshotBuilder → HU-PED-04 (relacionada: HU-PED-01) · T2 `[BE]` VentasClient → HU-PED-01 · T3 `[BE]` `PedidoService.crear_en_ventas` → HU-PED-01 · T4 `[BE]` tabla `outbox` y OutboxWorker → HU-PED-02 · T5 `[BE]` notificación de pago y cierre → HU-PED-02 · T6 `[BE]` anulación → HU-PED-03 · T7 `[FE]` OrderConfirmation y PendingConfirmation → HU-PED-02 · T8 `[QA]` → HU-PED-01 a HU-PED-04 |
| SPEC-16 | T1 `[BE]` tabla `notificacion` e integración con el outbox → HU-PED-06 · T2 `[BE]` EmailSender SMTP y falso → HU-PED-05 · T3 `[BE]` plantillas → HU-PED-05 · T4 `[BE]` endpoint de reenvío → HU-PED-08 · T5 `[FE]` enlace profundo y botón "Reenviar correo" → HU-PED-08 · T6 `[QA]` → HU-PED-05 a HU-PED-08 |
