# Diseño: Grabación del pedido

> Origen: SPEC-15 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v1/pedidos` | ✅ `api-contract.md` §1.1 |
| Ventas | `POST /api/v1/pedidos/{id}/pagos/notificacion` | ✅ §1.2 |
| Ventas | `POST /api/v1/pedidos/{id}/anulaciones` | ✅ §1.7 |
| Seguridad | Token de servicio `modulo-chatbot` para llamar a Ventas desde el worker (sin token de cliente) | ✅ |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `OrderConfirmation` (bloque `CONFIRMACION_PEDIDO`) | Número de pedido, líneas resumidas, total, tarjeta enmascarada, dirección, plazo y los botones "Ver estado del pedido" y "Seguir comprando". |
| `PendingConfirmation` | Estado "Pago aprobado, confirmando…" con sondeo de `GET /checkout/{id}` cada 5 s (máx. 2 min). |

## Backend

| Componente | Responsabilidad |
|---|---|
| `PedidoService.crear_en_ventas()` | Arma y valida el snapshot con los nombres de campo reales de Ventas, lo envía y guarda `pedido_ref`. |
| `SnapshotBuilder` | Construye `contacto` (con documento, SPEC-12), `items`, `cupon`, `envio` y `pago` a partir del carrito, los totales y el perfil. |
| `VentasClient` | `crear()`, `notificarPago()`, `anular()`, `obtener()` y `listar()`; token de servicio o del cliente según la operación; timeout de 5 s; normaliza `codigo` → `code`. |
| `OutboxWorker` | Procesa `NOTIFICAR_PAGO_VENTAS`, `SOLICITAR_ANULACION` y `ENVIAR_CORREO` con backoff; distingue errores reintentables (`5xx`, timeout) de no reintentables (`400`, `409`). |
| Tabla `pedido_ref` y `outbox` | Ver `modelo-datos.md`. |
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
