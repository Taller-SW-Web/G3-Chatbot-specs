# ADR-0011: Outbox transaccional para notificaciones a Ventas y correos

## Estado

Aceptada; modificada por [ADR-0030](ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md) (ver [Actualización](#actualización-2026-11-24-el-worker-pasa-a-ser-relay-hacia-rabbitmq))

## Fecha

2026-09-24 (fecha de registro; decisión de SPEC-15 y SPEC-16, sin fecha)

## Contexto

- Cuando el simulador aprueba un pago, el chatbot tiene que notificarlo a Ventas (`POST /api/v1/pedidos/{id}/pagos/notificacion`, `CREADO → PAGADO`). Si esa llamada falla y se pierde, queda un cobro aprobado sin pedido pagado.
- Los checkouts expirados o con 3 pagos rechazados requieren anular el pedido en Ventas (`POST /pedidos/{id}/anulaciones`, motivo `PAGO_NO_COMPLETADO`).
- El correo de confirmación no debe bloquear la compra y debe enviarse una sola vez por pedido (SPEC-16).
- La integración es síncrona por API, sin broker de mensajería ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)).

## Decisión

- Toda notificación a otro sistema que no puede perderse se registra en la tabla **`outbox`**, **en la misma transacción** que el cambio de estado local (p. ej. el intento de pago aprobado). Tipos: `NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL`.
- Un **`OutboxWorker`** (APScheduler) procesa las tareas pendientes:
  - Backoff exponencial de 5 intentos (5 s, 15 s, 45 s, 2 min, 5 min); agotados, la tarea queda `FAILED` para revisión manual (`/admin/outbox-fallidos`, log `ERROR`).
  - Distingue errores reintentables (`5xx`, timeout) de no reintentables (`400`, `409`), que no se reintentan.
  - Llama a Ventas con el token de servicio ([ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md)).
- Idempotencia de la entrega:
  - notificación de pago con `transaccionId` como clave;
  - correo deduplicado por `(order_id, resend_number)` en `notification` (máx. 3 reintentos SMTP por notificación).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Llamar a Ventas y al SMTP en línea dentro de la petición de pago (*alternativa estándar, no documentada*) | Un fallo o timeout de Ventas perdería la notificación de un pago ya aprobado y bloquearía la respuesta al cliente |
| Broker de mensajería (RabbitMQ) | En esta versión no se usan eventos ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)). **Ya no vigente:** el 2026-11-24 se adopta RabbitMQ en CloudAMQP, alimentado por este mismo outbox ([ADR-0030](ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md)) |

## Consecuencias

**Positivas**
- Entrega eventual garantizada ante caídas de Ventas o del SMTP; el chat muestra "Pago aprobado. Estamos confirmando tu pedido…" mientras tanto.
- La compra no depende del correo.

**Negativas y riesgos aceptados**
- Consistencia eventual: durante los reintentos el pedido sigue `CREADO` en Ventas.
- Las tareas `FAILED` requieren revisión manual.
- No hay plazo de retención definido para `outbox.payload` (`privacidad.md` §2).
- No está decidido si el worker corre como proceso aparte o dentro de la API ([C4, preguntas abiertas](../c4.md#preguntas-abiertas)).

## Actualización 2026-11-24: el worker pasa a ser relay hacia RabbitMQ

El outbox **se mantiene**: las tareas se siguen escribiendo en la misma transacción que el cambio de estado local, con los mismos cuatro tipos (`NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL` y `SEND_FEEDBACK_EMAIL`, que se agregó después del registro original). Lo que cambia, según [ADR-0030](ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md) y con `OUTBOX_DISPATCH_MODE=broker`:

- El worker pasa a ser un **relay**: publica cada tarea pendiente en RabbitMQ con confirmaciones del publicador y mensajes persistentes, y solo marca la fila `PROCESSED` tras la confirmación del broker. Con el broker caído las filas quedan `PENDING` y se reintenta la publicación con backoff, sin incrementar `attempts`.
- El **backoff de 5 intentos** (5 s, 15 s, 45 s, 2 min, 5 min) y la **clasificación** no reintentable (`400`, `409`) o reintentable (cualquier otro error, incluidos `5xx`, `429` y *timeout*) se mueven al **consumidor**, que los aplica con colas de espera con TTL. Agotados los intentos, o ante un error no reintentable, la fila queda `FAILED` y el mensaje va a la DLQ para revisión manual. El correo conserva su propia política de reintentos (1, 5 y 15 min, SPEC-16).
- La **idempotencia** de la entrega no cambia: `transaccionId` para el pago y `(order_id, resend_number)` para el correo.
- Con `OUTBOX_DISPATCH_MODE=direct` rige el comportamiento descrito arriba (el worker llama a Ventas y al SMTP); es el valor por omisión y el interruptor de reversa.
- **Pregunta abierta resuelta:** el consumidor corre como **proceso aparte**; el relay permanece donde corre hoy el worker, en el *lifespan* de la API (`OUTBOX_WORKER_ENABLED`). Hoy ese worker es un bucle `asyncio` y no APScheduler, y producción tiene un único servicio; `SKIP LOCKED` permite más de una instancia sin duplicar publicaciones.
- Sin cambio de esquema: en modo `broker`, `PROCESSED` significa "publicada y confirmada por el broker".

## Referencias

- `openspec/specs/grabacion-pedido/spec.md` Req. 2 y 3 (líneas 96-155) e idempotencia (línea 174)
- `openspec/specs/grabacion-pedido/design.md` (`OutboxWorker`, alertas)
- `openspec/specs/notificacion-confirmacion/spec.md` Req. 1 a 3 (líneas 31-75) y `design.md`
- `docs/modelo-datos.md` tablas `outbox`, `notification`, `order_ref`
- `docs/contratos-integracion.md` §5 (línea 243); `README.md` §1.5 (APScheduler)
