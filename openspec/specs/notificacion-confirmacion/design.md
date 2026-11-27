# Diseño: Notificación de confirmación por correo

> Origen: SPEC-16 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Componente | Uso | Estado |
|---|---|---|
| Proveedor SMTP | Envío | Configurable |
| Datos | Snapshot local del checkout y correo del token o perfil | Internos |

## Frontend

| Componente | Responsabilidad |
|---|---|
| Texto en `OrderConfirmation` | Mención del correo enmascarado. |
| Acción "Reenviar correo" | Botón en el detalle del pedido (SPEC-17). |
| Ruta de destino del enlace | `/pedidos/{pedidoId}` dentro de `OrderHistoryPage` (requiere login; si no hay sesión, pide iniciarla y retoma ahí). |

## Backend

| Componente | Responsabilidad |
|---|---|
| `NotificacionService` | Encola, deduplica y gestiona los reenvíos. |
| `EmailSender` (interfaz) + `SmtpEmailSender` | Envío; implementación falsa para las pruebas. |
| Plantillas Jinja2 `confirmacion_pedido.html` y `.txt` | Contenido del correo. |
| Encolado de la confirmación | Lo dispara el worker de outbox al recibir `nuevoEstado: PAGADO` en `NOTIFY_SALES_PAYMENT` (capacidad `order_confirmation`); con `ANULADO` no se encola. El checkout ya no lo hace. |
| Tarea de outbox `SEND_EMAIL` | La procesa `OutboxWorker` en `direct` o el consumidor de RabbitMQ en `broker` (ADR-0030). |
| `POST /api/v1/pedidos/{id}/reenviar-confirmacion` | Reenvío con límite de 2. |

## Desglose para issues

- [ ] `[BE]` Tabla `notification` e integración con el outbox
- [ ] `[BE]` `EmailSender` SMTP más un sender falso para las pruebas
- [ ] `[BE]` Plantillas HTML y texto con los datos del snapshot
- [ ] `[BE]` Endpoint de reenvío con límite
- [ ] `[FE]` Enlace profundo a `OrderHistoryPage` con el pedido preseleccionado, y botón "Reenviar correo"
- [ ] `[QA]` Pruebas de todos los escenarios; revisión visual de la plantilla en Mailtrap
