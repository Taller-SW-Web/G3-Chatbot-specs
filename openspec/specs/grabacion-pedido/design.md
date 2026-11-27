# Diseño: Grabación del pedido

> Origen: SPEC-15 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v1/pedidos` | ✅ `api-contract.md` §1.1 |
| Ventas | `POST /api/v1/pedidos/{id}/pagos/notificacion` | ✅ §1.2 |
| Ventas | `POST /api/v1/pedidos/{id}/anulaciones` | ✅ §1.7 |
| Ventas | `GET /api/v1/pedidos/{id}` con token de servicio, solo para reconciliar un `409 PEDIDO_NO_ANULABLE` | 🟡 scope `ventas:pedidos:consultar` por confirmar con G5 (figura para `modulo-postventa`) |
| Seguridad | Token de servicio `modulo-chatbot` para llamar a Ventas desde el worker (sin token de cliente), con los scopes `ventas:pedidos:crear`, `ventas:pedidos:anular` y `ventas:pagos:webhook`; `ventas:pedidos:consultar` se necesita para la lectura de reconciliación y aún no está concedido al canal | ✅ `ventas:pagos:webhook` ya concedido (Ventas, A15) |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `OrderConfirmation` (bloque `CONFIRMACION_PEDIDO`) | Número de pedido, líneas resumidas, total, tarjeta enmascarada, dirección, plazo y los botones "Ver estado del pedido" y "Seguir comprando". |
| `PendingConfirmation` | Estado "Pago aprobado, confirmando…" con sondeo de `GET /checkout/{id}` cada 5 s (máx. 2 min). |

## Backend

| Componente | Responsabilidad |
|---|---|
| `PedidoService.crear_en_ventas()` | Arma y valida el snapshot con los nombres de campo reales de Ventas. El checkout ya está persistido antes de la llamada; si Ventas no responde dentro del deadline, el checkout conserva el snapshot y la misma `Idempotency-Key` reconcilia el `pedidoId` y guarda `order_ref` sin duplicar. |
| `SnapshotBuilder` | Construye `contacto` (con documento, SPEC-12), `items`, `cupon`, `envio` y `pago` a partir del carrito, los totales y el perfil. |
| `VentasClient` | `crear()`, `notificarPago()`, `anular()`, `obtener()` y `listar()`; además `get_order_as_service()` (token de servicio, scope `ventas:pedidos:consultar`) para las tareas del outbox sin token de cliente; token de servicio o del cliente según la operación; timeout de 5 s; normaliza `codigo` → `code`. |
| `OutboxWorker` | En `OUTBOX_DISPATCH_MODE=direct` procesa `NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION` y `SEND_EMAIL` con backoff; en `broker` publica en RabbitMQ con confirmaciones (ADR-0030) y el consumidor de H5-M3 procesa con `ack` manual y DLQ. En ambos modos distingue errores reintentables (`5xx`, timeout) de no reintentables (`400`, `409`). Al procesar `NOTIFY_SALES_PAYMENT` sigue `nuevoEstado`: `PAGADO` (o ausente, con advertencia) → `PAID_NOTIFIED` y encola la confirmación (SPEC-16); `ANULADO` → `CANCELLED` sin correo. Un `409 PEDIDO_NO_ANULABLE` en `REQUEST_CANCELLATION` se trata como éxito si Ventas confirma `ANULADO`; `SOLICITUD_DUPLICADA` no se reconcilia. |
| Tabla `order_ref` y `outbox` | Ver `modelo-datos.md`. |
| Alertas | Log estructurado de nivel `ERROR` más un endpoint interno `/admin/outbox-fallidos` para revisión. |

## Desglose para issues

- [ ] `[BE]` `SnapshotBuilder` con los campos reales de `contacto`, `items`, `cupon`, `envio` y `pago`, y validación de la suma
- [ ] `[BE]` `VentasClient` (crear, notificar pago, anular, obtener, listar) con normalización de errores `codigo` → `code`
- [ ] `[BE]` `PedidoService.crear_en_ventas` integrado en `POST /checkout`
- [ ] `[BE]` Tabla `outbox` y `OutboxWorker` con backoff, idempotencia y distinción de errores reintentables
- [ ] `[BE]` Notificación de pago vía `POST /pagos/notificacion` y cierre del checkout y del carrito
- [ ] `[BE]` Anulación por pago no completado vía `POST /anulaciones`
- [ ] `[FE]` `OrderConfirmation` y `PendingConfirmation` con sondeo
- [ ] `[QA]` Pruebas de todos los escenarios; prueba de caos "Ventas cae tras el pago" con verificación de la entrega eventual; prueba de que un `409`/`400` no se reintenta indefinidamente
