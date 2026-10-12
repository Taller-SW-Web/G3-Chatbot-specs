# Diseño: Retroalimentación del cliente

> Origen: SPEC-24 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Componente | Uso | Estado |
|---|---|---|
| Ventas, `POST /api/v2/csat` | Registrar la calificación de la compra | ✅ Publicado, `canal: "CHATBOT"` contemplado. Scope por confirmar (pregunta abierta 1 de la spec; issue abierto en G5-Ventas-Postventas) |
| `AttachmentStorage` (SPEC-23, reutilizado) | Guardar la captura de pantalla de un bug/sugerencia | ✅ Puerto ya existente; esta spec no crea un segundo mecanismo de carga |
| `EmailSender` / outbox (SPEC-16, reutilizado) | Notificación interna de sugerencias y bugs | ✅ Adaptador ya existente |
| "Mi cuenta" (`openspec/changes/alinear-specs-con-prototipo`) | Punto de entrada al formulario de sugerencia/bug | 🟡 Cambio todavía sin aplicar a `inicio-sesion` |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `MessageFeedback` (en `MessageRenderer`) | Fila de 👍, 👎 y "Copiar" debajo de cada bloque de respuesta; estado optimista al tocar un ícono. |
| `useReaction` (hook) | Envía la reacción al backend, con reintento silencioso en segundo plano si falla. |
| `PurchaseRatingModal` | Popup "Califica tu compra" tras el pago: estrellas (1–5), comentario opcional, "Enviar calificación" (deshabilitado sin estrellas) y "Ahora no". Se monta junto con `OrderConfirmation` (SPEC-15). Se guarda en el chatbot. |
| `DeliveryRatingFooter` | Bloque al pie del detalle de un pedido (`OrderDetail`), solo si el estado es `ENTREGADO` y no está calificado: "¿Qué tal fue tu pedido?", tres caritas (5, 3, 1) y "Enviar calificación". Se envía a Ventas. |
| `FeedbackEntryPoint` (en `AccountPage` / "Mi cuenta") | Sección "Ayúdanos a mejorar" con el botón "Enviar sugerencia / Reportar bug". |
| `FeedbackForm` | Toggle Sugerencia/Bug, campo de título, descripción con contador (0/1000), correo prellenado desde el perfil, `AttachmentPicker` opcional (reutiliza el componente de selección de imagen de SPEC-23) y botones "Cancelar"/"Enviar". |
| Puerto `ChatbotApiPort` (ampliado) | `enviarReaccion`, `enviarCalificacion`, `enviarSugerencia`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/mensajes/{mensajeId}/reaccion` (`chatbot_router.py`) | Registra o actualiza la reacción (👍/👎) de un mensaje; sin autenticación obligatoria (usa `cliente_id` o `chat_sid`, igual que el resto del chat). |
| `POST /api/v1/pedidos/{pedidoId}/csat` | Valida la pertenencia del pedido al cliente autenticado y que esté `ENTREGADO`, llama a `VentasClient.registrarCsat()`, y propaga `201`/`409`/`422`/`503`. Marca `order_ref.csat_sent`. |
| `POST /api/v1/pedidos/{pedidoId}/valoracion-compra` | Guarda la valoración de la experiencia de compra en `purchase_rating` (una por pedido). |
| `POST /api/v1/sugerencias` | Crea la sugerencia o el bug, sube la captura (si existe) vía `AttachmentStorage`, y encola la notificación interna por outbox. |
| `VentasClient.registrarCsat()` | Cliente de `POST /api/v2/csat`; normaliza errores de Ventas (`codigo` → `code` interno). |
| `SugerenciaService` | Orquesta la validación, la subida opcional de la captura y el registro; aplica el límite de 5 por hora. |
| `RateLimiter` (ampliado) | Agrega el límite de 30 reacciones/minuto y 5 sugerencias/hora por cliente o IP. |
| Tablas `message_reaction`, `feedback_suggestion` y `purchase_rating` | Ver más abajo. |

### Modelo de datos (resumen)

**`message_reaction`**: `id` (uuid, `uuidv7()`), `message_id` (FK → `message`, `ON DELETE CASCADE`), `customer_id` (uuid, nulo), `anonymous_sid` (text, nulo), `reaction` (`POSITIVE`/`NEGATIVE`), `created_at`, `updated_at`. `CHECK (customer_id IS NOT NULL OR anonymous_sid IS NOT NULL)` y único por `(message_id, customer_id, anonymous_sid)`: una reacción vigente por mensaje y por quien reacciona.

**`feedback_suggestion`**: `id`, `customer_id` (obligatorio, requiere sesión), `type` (`SUGGESTION`/`BUG`), `title` (≥ 3), `description` (6–1000), `contact_email`, `attachment_id` (FK opcional a `attachment`), `notification_status` (`PENDING`/`SENT`/`FAILED`, por defecto `PENDING`), `created_at`.

**`purchase_rating`**: `id`, `order_id` (único; referencia al pedido del chatbot), `customer_id`, `rating` (`CHECK BETWEEN 1 AND 5`, estrellas), `comment` (nulo, máx. 500), `created_at`. Valoración de la experiencia de comprar en el chat; no se envía a Ventas.

**`order_ref.csat_sent`** (`boolean NOT NULL DEFAULT false`): marca que la calificación del pedido ya se envió a Ventas (o que Ventas respondió `409`), para no volver a mostrar el bloque sin preguntarle a Ventas en cada carga.

La calificación del pedido (CSAT) **no se guarda** como calificación propia: vive en Ventas (`POST /api/v2/csat`). La valoración de la compra sí es propia del chatbot (`purchase_rating`). 🧩 Pendiente de Ventas (issue #37): token con el que se llama al endpoint y validación de `clienteId`.

### Encaje en los casos de uso del núcleo

No se agrega un caso de uso nuevo: la reacción y la sugerencia se agrupan como un nuevo `GestionarRetroalimentacionUseCase` (ligero, sin dependencias externas salvo Ventas para el CSAT), separado de `GestionarConversacionUseCase` para no sobrecargarlo con una responsabilidad que no es de mensajería.

## Desglose para issues

- [ ] `[BE]` Tablas `message_reaction`, `feedback_suggestion` y `purchase_rating`, columna `order_ref.csat_sent`, migración Alembic
- [ ] `[BE]` Endpoint `POST /mensajes/{id}/reaccion` con upsert por `(message_id, cliente_id|chat_sid)`
- [ ] `[BE]` `VentasClient.registrarCsat()` y endpoint `POST /pedidos/{id}/csat` (solo `ENTREGADO`, 1/3/5), con normalización de errores y `order_ref.csat_sent`
- [ ] `[BE]` Endpoint `POST /pedidos/{id}/valoracion-compra` y `purchase_rating`
- [ ] `[BE]` `SugerenciaService`: validación, subida de captura vía `AttachmentStorage`, registro
- [ ] `[BE]` Notificación interna por correo (outbox, reutilizando `EmailSender` de SPEC-16)
- [ ] `[BE]` `RateLimiter`: 30 reacciones/min, 5 sugerencias/hora
- [ ] `[FE]` `MessageFeedback` y `useReaction` con estado optimista
- [ ] `[FE]` `PurchaseRatingModal` tras la confirmación del pedido y `DeliveryRatingFooter` en el detalle de un pedido `ENTREGADO`
- [ ] `[FE]` `FeedbackEntryPoint` en "Mi cuenta" y `FeedbackForm` completo
- [ ] `[INT]` Dar seguimiento al issue abierto en `G5-Ventas-Postventas` sobre la autenticación de `POST /api/v2/csat` (pregunta abierta 1 de la spec)
- [ ] `[INT]` Actualizar `SPEC-16` para quitar la exclusión del CSAT de su "Fuera de alcance"
- [ ] `[INT]` Marcar la pregunta abierta 9 de `docs/conversacion/README.md` como resuelta, enlazando a esta spec
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la idempotencia de la calificación (`409` de Ventas) y el límite de sugerencias por hora
- [ ] `[QA]` Prueba de que una captura de bug nunca llega al LLM ni a una URL pública
