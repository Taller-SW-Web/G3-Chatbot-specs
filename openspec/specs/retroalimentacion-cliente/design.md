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
| `CsatModal` | Modal "Califica tu compra": estrellas (1–5), campo de comentario opcional, "Enviar calificación" (deshabilitado sin estrellas) y "Ahora no". Se monta junto con `OrderConfirmation` (SPEC-15). |
| `FeedbackEntryPoint` (en `AccountPage` / "Mi cuenta") | Sección "Ayúdanos a mejorar" con el botón "Enviar sugerencia / Reportar bug". |
| `FeedbackForm` | Toggle Sugerencia/Bug, campo de título, descripción con contador (0/1000), correo prellenado desde el perfil, `AttachmentPicker` opcional (reutiliza el componente de selección de imagen de SPEC-23) y botones "Cancelar"/"Enviar". |
| Puerto `ChatbotApiPort` (ampliado) | `enviarReaccion`, `enviarCalificacion`, `enviarSugerencia`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/mensajes/{mensajeId}/reaccion` (`chatbot_router.py`) | Registra o actualiza la reacción (👍/👎) de un mensaje; sin autenticación obligatoria (usa `cliente_id` o `chat_sid`, igual que el resto del chat). |
| `POST /api/v1/pedidos/{pedidoId}/csat` | Valida la pertenencia del pedido al cliente autenticado, llama a `VentasClient.registrarCsat()`, y propaga `201`/`409`/`503`. |
| `POST /api/v1/sugerencias` | Crea la sugerencia o el bug, sube la captura (si existe) vía `AttachmentStorage`, y encola la notificación interna por outbox. |
| `VentasClient.registrarCsat()` | Cliente de `POST /api/v2/csat`; normaliza errores de Ventas (`codigo` → `code` interno). |
| `SugerenciaService` | Orquesta la validación, la subida opcional de la captura y el registro; aplica el límite de 5 por hora. |
| `RateLimiter` (ampliado) | Agrega el límite de 30 reacciones/minuto y 5 sugerencias/hora por cliente o IP. |
| Tablas `message_reaction` y `feedback_suggestion` | Ver más abajo. |

### Modelo de datos (resumen)

**`message_reaction`**: `id`, `message_id` (FK), `cliente_id` o `chat_sid`, `tipo` (`POSITIVA`/`NEGATIVA`), `creado_en`, `actualizado_en`. Único por `(message_id, cliente_id|chat_sid)` — una reacción vigente por mensaje y por quien reacciona.

**`feedback_suggestion`**: `id`, `cliente_id` (FK, obligatorio — requiere sesión), `tipo` (`SUGERENCIA`/`BUG`), `titulo`, `descripcion`, `correo_contacto`, `attachment_id` (FK opcional a la tabla de SPEC-23), `estado_notificacion` (`PENDIENTE`/`ENVIADA`/`FALLIDA`), `creado_en`.

La calificación de compra **no se guarda** en una tabla propia del chatbot: vive solo en Ventas (vía `POST /api/v2/csat`). El chatbot únicamente registra, si hace falta para la regla de "no repetir el modal", un marcador local ligero (`pedido_id` + `calificado: boolean`) para no tener que preguntarle a Ventas en cada carga de la pantalla.

### Encaje en los casos de uso del núcleo

No se agrega un caso de uso nuevo: la reacción y la sugerencia se agrupan como un nuevo `GestionarRetroalimentacionUseCase` (ligero, sin dependencias externas salvo Ventas para el CSAT), separado de `GestionarConversacionUseCase` para no sobrecargarlo con una responsabilidad que no es de mensajería.

## Desglose para issues

- [ ] `[BE]` Tablas `message_reaction` y `feedback_suggestion`, migración Alembic
- [ ] `[BE]` Endpoint `POST /mensajes/{id}/reaccion` con upsert por `(message_id, cliente_id|chat_sid)`
- [ ] `[BE]` `VentasClient.registrarCsat()` y endpoint `POST /pedidos/{id}/csat`, con normalización de errores y el marcador local "ya calificado"
- [ ] `[BE]` `SugerenciaService`: validación, subida de captura vía `AttachmentStorage`, registro
- [ ] `[BE]` Notificación interna por correo (outbox, reutilizando `EmailSender` de SPEC-16)
- [ ] `[BE]` `RateLimiter`: 30 reacciones/min, 5 sugerencias/hora
- [ ] `[FE]` `MessageFeedback` y `useReaction` con estado optimista
- [ ] `[FE]` `CsatModal` integrado en la confirmación del pedido
- [ ] `[FE]` `FeedbackEntryPoint` en "Mi cuenta" y `FeedbackForm` completo
- [ ] `[INT]` Dar seguimiento al issue abierto en `G5-Ventas-Postventas` sobre la autenticación de `POST /api/v2/csat` (pregunta abierta 1 de la spec)
- [ ] `[INT]` Actualizar `SPEC-16` para quitar la exclusión del CSAT de su "Fuera de alcance"
- [ ] `[INT]` Marcar la pregunta abierta 9 de `docs/conversacion/README.md` como resuelta, enlazando a esta spec
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la idempotencia de la calificación (`409` de Ventas) y el límite de sugerencias por hora
- [ ] `[QA]` Prueba de que una captura de bug nunca llega al LLM ni a una URL pública
