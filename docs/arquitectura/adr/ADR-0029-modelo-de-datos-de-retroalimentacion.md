# ADR-0029: Modelo de datos de retroalimentación: tablas propias y CSAT en Ventas

## Estado

Aceptada

## Fecha

2026-11-21 (decisión del dueño, D5 de la [auditoría](../../auditoria-specs-2026-11.md))

## Contexto

- `retroalimentacion-cliente/spec.md` describe cuatro mecanismos: reacciones 👍/👎 por mensaje, sugerencias/bugs con captura, calificación de la entrega (CSAT de Ventas) y valoración de la experiencia de compra.
- La auditoría 2026-11 encontró que solo existe `POST /pedidos/{id}/csat`; `BotFeedback`, `SugerenciaForm` y `RatingPopup` son estado local y no hay tablas ni endpoints para reacciones, sugerencias ni valoración de compra.
- Ventas ya publica `POST /api/v2/csat` con `canal: "CHATBOT"` y autenticación con el token del cliente (A15). El chatbot no debe duplicar esa fuente de verdad.
- `modelo-datos.md` ya define `message_reaction`, `feedback_suggestion`, `purchase_rating` y `order_ref.csat_sent`; falta conectarlas.

## Decisión

1. **Reacciones en `message_reaction`.** Una reacción vigente por mensaje y autor (`customer_id` o `anonymous_sid`), con `reaction` `POSITIVE`/`NEGATIVE`. Cambiar de 👍 a 👎 actualiza la fila; "Copiar" no se registra. Índice único `UNIQUE NULLS NOT DISTINCT (message_id, customer_id, anonymous_sid)`.
2. **Sugerencias/bugs en `feedback_suggestion`.** Requiere sesión (`customer_id`), `type` `SUGGESTION`/`BUG`, `title` ≥ 3, `description` 6–1000, `contact_email`, `screenshot_key` opcional, `notification_status` (`PENDING`/`SENT`/`FAILED`) e `idempotency_key` única.
3. **Valoración de compra en `purchase_rating`.** Una fila por `order_id` (`UNIQUE`), `rating` 1–5 y `comment` opcional (≤ 500). Es propia del chatbot y no se envía a Ventas. "Ahora no" no crea fila; el descarte se recuerda en el navegador por dispositivo.
4. **CSAT sigue en Ventas.** El chatbot no guarda una tabla de CSAT: `POST /api/v1/pedidos/{pedidoId}/csat` reenvía el token del cliente a `POST /api/v2/csat` y normaliza el `403` de Ventas a `404 RECURSO_NO_ENCONTRADO` (anti-enumeración) y propaga `201`/`409`/`422`/`503`. La columna `order_ref.csat_sent` marca que ya se envió (o que Ventas respondió `409`), y solo se actualiza si existe la fila de `order_ref`.
5. **Notificación interna por outbox.** `POST /sugerencias` registra la fila y encola `SEND_EMAIL` con el mismo `EmailSender`/outbox de SPEC-16; el worker actualiza `notification_status`. Un fallo de correo no se muestra al cliente ni borra la sugerencia.
6. **Captura con `AttachmentStorage`, sin `attachment`.** La captura de un bug usa el puerto de SPEC-23 y se guarda en `feedback_suggestion.screenshot_key`; no se crea una fila en `attachment` porque no pertenece a una conversación.
7. **Sin tabla genérica de feedback.** Cada mecanismo tiene su ciclo de vida y sus restricciones; unificarlos en una sola tabla `feedback` obligaría a columnas nulas y reglas condicionales.

**Límites:** no hay panel de revisión de sugerencias ni de valoraciones en la app; el seguimiento es por correo. No se define el plazo de retención de ninguna de las tres tablas. El límite de frecuencia de las calificaciones (caritas y estrellas) queda pendiente; solo se fijan 30 reacciones/minuto y 5 sugerencias/hora.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Una tabla `feedback` genérica para los cuatro mecanismos | Reacciones, sugerencias, CSAT y valoración tienen dueños, claves y ciclos distintos; la tabla quedaría llena de columnas nulas y `CHECK` condicionales |
| Guardar el CSAT también en el chatbot | Duplica la fuente de verdad de Ventas y obliga a reconciliar dos estados |
| Usar la tabla `attachment` para la captura del bug | `attachment` está ligada a una conversación y a un mensaje; una sugerencia no tiene ninguno de los dos |
| No persistir y solo registrar en logs | No permite métricas, seguimiento ni idempotencia; la spec exige códigos de seguimiento |
| Reutilizar `message` para reacciones | `message` es solo inserción y pertenece a la conversación; una reacción es un upsert por autor |

## Consecuencias

**Positivas**

- Cada mecanismo tiene una tabla y un dueño claros, con restricciones que la base puede verificar.
- El CSAT no se duplica: Ventas sigue siendo la fuente de verdad y `csat_sent` evita preguntarle en cada carga.
- La captura reutiliza el storage privado de SPEC-23 sin mezclarse con los adjuntos del chat.

**Negativas y riesgos aceptados**

- Tres tablas nuevas y una columna (`order_ref.csat_sent`), más un outbox interno y un límite de frecuencia.
- La valoración de compra queda sin panel de revisión; se consulta por SQL o por el correo interno.
- La retención de reacciones, sugerencias y valoraciones no está definida; se registra como deuda en `modelo-datos.md`.
- Si Ventas no responde al CSAT, el bloque se conserva para reintentar; no se guarda localmente como respaldo.

## Referencias

- [`retroalimentacion-cliente/spec.md`](../../../openspec/specs/retroalimentacion-cliente/spec.md) y [`design.md`](../../../openspec/specs/retroalimentacion-cliente/design.md)
- [`modelo-datos.md`](../../modelo-datos.md) — tablas `message_reaction`, `feedback_suggestion`, `purchase_rating` y `order_ref.csat_sent`
- [ADR-0011](ADR-0011-outbox-transaccional.md) — outbox para la notificación interna
- [ADR-0028](ADR-0028-adjuntos-almacenamiento-externo-privado.md) — storage privado reutilizado para la captura
- [`auditoria-specs-2026-11.md`](../../auditoria-specs-2026-11.md) §4, D5
- [`contratos-integracion.md`](../../contratos-integracion.md) §2.9
