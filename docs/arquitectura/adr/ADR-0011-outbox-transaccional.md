# ADR-0011: Outbox transaccional para notificaciones a Ventas y correos

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; decisión de SPEC-15 y SPEC-16, sin fecha)

## Contexto

- Cuando el simulador aprueba un pago, el chatbot tiene que notificarlo a Ventas (`POST /api/v1/pedidos/{id}/pagos/notificacion`, `CREADO → PAGADO`). Si esa llamada falla y se pierde, queda un cobro aprobado sin pedido pagado.
- Los checkouts expirados o con 3 pagos rechazados requieren anular el pedido en Ventas (`POST /pedidos/{id}/anulaciones`, motivo `PAGO_NO_COMPLETADO`).
- El correo de confirmación no debe bloquear la compra y debe enviarse una sola vez por pedido (SPEC-16).
- La integración es síncrona por API, sin broker de mensajería ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)).

## Decisión

- Toda notificación a otro sistema que no puede perderse se registra en la tabla **`outbox`**, **en la misma transacción** que el cambio de estado local (p. ej. el intento de pago aprobado). Tipos: `NOTIFICAR_PAGO_VENTAS`, `SOLICITAR_ANULACION`, `ENVIAR_CORREO`.
- Un **`OutboxWorker`** (APScheduler) procesa las tareas pendientes:
  - Backoff exponencial de 5 intentos (5 s, 15 s, 45 s, 2 min, 5 min); agotados, la tarea queda `FALLIDO` para revisión manual (`/admin/outbox-fallidos`, log `ERROR`).
  - Distingue errores reintentables (`5xx`, timeout) de no reintentables (`400`, `409`), que no se reintentan.
  - Llama a Ventas con el token de servicio ([ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md)).
- Idempotencia de la entrega:
  - notificación de pago con `transaccionId` como clave;
  - correo deduplicado por `pedido_id + tipo + numero_reenvio` en `notificacion` (máx. 3 reintentos SMTP por notificación).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Llamar a Ventas y al SMTP en línea dentro de la petición de pago (*alternativa estándar, no documentada*) | Un fallo o timeout de Ventas perdería la notificación de un pago ya aprobado y bloquearía la respuesta al cliente |
| Broker de mensajería (RabbitMQ) | En esta versión no se usan eventos ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)) |

## Consecuencias

**Positivas**
- Entrega eventual garantizada ante caídas de Ventas o del SMTP; el chat muestra "Pago aprobado. Estamos confirmando tu pedido…" mientras tanto.
- La compra no depende del correo.

**Negativas y riesgos aceptados**
- Consistencia eventual: durante los reintentos el pedido sigue `CREADO` en Ventas.
- Las tareas `FALLIDO` requieren revisión manual.
- No hay plazo de retención definido para `outbox.payload` (`privacidad.md` §2).
- No está decidido si el worker corre como proceso aparte o dentro de la API ([C4, preguntas abiertas](../c4.md#preguntas-abiertas)).

## Referencias

- `openspec/specs/grabacion-pedido/spec.md` Req. 2 y 3 (líneas 96-155) e idempotencia (línea 174)
- `openspec/specs/grabacion-pedido/design.md` (`OutboxWorker`, alertas)
- `openspec/specs/notificacion-confirmacion/spec.md` Req. 1 a 3 (líneas 31-75) y `design.md`
- `docs/modelo-datos.md` tablas `outbox`, `notificacion`, `pedido_ref`
- `docs/contratos-integracion.md` §5 (línea 243); `README.md` §1.5 (APScheduler)
