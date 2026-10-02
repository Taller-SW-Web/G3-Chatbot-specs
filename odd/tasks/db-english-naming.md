# Nombres de la base de datos en inglés

Decisión del equipo (2026-10-02): todos los identificadores de la base de datos pasan a inglés: tablas, columnas, valores de enumeración, constraints e índices. Los cambios van directo a `main` de `G3-Chatbot-specs`; el backend se ajusta en `feature/h2-07-conversacion-adjunto`.

## Alcance y restricciones

- Cambia: nombres de tablas, columnas, valores de enumeración dentro de los `CHECK`, nombres de constraints e índices, y las referencias a todos ellos en specs, ADR, historias, diagramas y backend.
- No cambia:
  - Rutas de la API (`/chat/conversaciones`, `/carrito`, `/api/v1/pedidos`) y campos JSON en camelCase (`clienteId`, `idZona`).
  - Nombres de directorios y archivos de SPEC (`openspec/specs/gestion-carrito`, `docs/conversacion/`).
  - Nombres de campos externos dentro del `jsonb` (`product_id`, `precio_regular`, `channel_id`) y las claves internas de los snapshots.
  - La configuración `'spanish'` de `to_tsvector`.
  - La prosa en español de los documentos.
- Los valores que el contrato con Ventas define en español (`CAMBIO`, `DEVOLUCION_DINERO`, `IMAGEN`) se guardan en inglés en la base. El adapter traduce en ambos sentidos (entrada y salida). Esa traducción debe quedar documentada en `modelo-datos.md` y en `contratos-integracion.md`.
- Las etiquetas de la UI siguen en español; las resuelve el frontend a partir del valor en inglés.
- Ante una inconsistencia entre documentos, el escritor no la resuelve: la reporta con archivo y línea.
- No se hacen commits sin confirmación del usuario. El push a `main` de specs requiere confirmación aparte.

## Glosario de tablas

| Antes | Ahora |
|---|---|
| `conversacion` | `conversation` |
| `mensaje` | `message` |
| `celular_verificacion_local` | `local_phone_verification` |
| `carrito` | `cart` |
| `item_carrito` | `cart_item` |
| `checkout` | `checkout` |
| `intento_pago` | `payment_attempt` |
| `pedido_ref` | `order_ref` |
| `notificacion` | `notification` |
| `reclamo_ref` | `claim_ref` |
| `devolucion_ref` | `return_ref` |
| `evidencia` | `evidence` |
| `adjunto` | `attachment` |
| `outbox` | `outbox` |

## Glosario de columnas

| Antes | Ahora | Antes | Ahora |
|---|---|---|---|
| `cliente_id` | `customer_id` | `numero_reenvio` | `resend_number` |
| `conversacion_id` | `conversation_id` | `destinatario` | `recipient` |
| `mensaje_id` | `message_id` | `intentos` | `attempts` |
| `carrito_id` | `cart_id` | `ultimo_error` | `last_error` |
| `pedido_id` | `order_id` | `enviada_en` | `sent_at` |
| `reclamo_id` | `claim_id` | `nombre_archivo_original` | `original_file_name` |
| `devolucion_id` | `return_id` | `tamanio_bytes` | `size_bytes` |
| `producto_id` | `product_id` | `clave_almacenamiento` | `storage_key` |
| `direccion_id` | `address_id` | `clave_miniatura` | `thumbnail_key` |
| `sid_anonimo` | `anonymous_sid` | `tipo_mime` | `mime_type` |
| `titulo` | `title` | `ancho` / `alto` | `width` / `height` |
| `estado` | `status` | `proximo_intento_en` | `next_attempt_at` |
| `contexto` | `context` | `ultimo_intento_en` | `last_attempt_at` |
| `resumen` | `summary` | `procesado_en` | `processed_at` |
| `titulo_busqueda` | `title_search_vector` | `creado_en` | `created_at` |
| `busqueda` | `search_vector` | `actualizado_en` | `updated_at` |
| `ultimo_mensaje_en` | `last_message_at` | `rol` | `role` |
| `verificado_en` | `verified_at` | `texto` | `content` |
| `celular` | `phone` | `bloques` | `blocks` |
| `cupon_codigo` | `coupon_code` | `herramienta` | `tool_name` |
| `envio_snapshot` | `shipping_snapshot` | `argumentos` | `arguments` |
| `totales_snapshot` | `totals_snapshot` | `resultado_codigo` | `result_code` |
| `nombre` | `name` | `tokens_entrada` | `input_tokens` |
| `variante_desc` | `variant_description` | `tokens_salida` | `output_tokens` |
| `imagen_url` | `image_url` | `latencia_ms` | `latency_ms` |
| `cantidad` | `quantity` | `resultado` | `result` |
| `precio_unitario_ref` | `unit_price_ref` | `motivo` | `reason` |
| `intentos_pago` | `payment_attempts` | `id_transaccion` | `transaction_id` |
| `expira_en` | `expires_at` | `marca` | `brand` |
| `estado_local` | `local_status` | `ultimos4` | `last4` |
| `codigo` | `code` | `monto` | `amount` |
| `tipo_solicitado` | `requested_type` | `tipo` | `type` |

Sin cambio: `id`, `total`, `version`, `payload`, `url`, `sku`, `idempotency_key`.

## Glosario de valores de enumeración

| Tabla.columna | Antes | Ahora |
|---|---|---|
| `conversation.status` | `ACTIVA`, `ARCHIVADA`, `CERRADA` | `ACTIVE`, `ARCHIVED`, `CLOSED` |
| `message.role` | `CLIENTE`, `ASISTENTE`, `HERRAMIENTA` | `CUSTOMER`, `ASSISTANT`, `TOOL` |
| `message.result_code` | `OK` o código de error; `VALIDACION` | `OK` o código de error; `VALIDATION` |
| `cart.status` | `ACTIVO`, `EN_CHECKOUT`, `CONVERTIDO`, `ABANDONADO`, `FUSIONADO` | `ACTIVE`, `IN_CHECKOUT`, `CONVERTED`, `ABANDONED`, `MERGED` |
| `checkout.status` | `PENDIENTE_PAGO`, `PAGO_APROBADO`, `CONFIRMADO`, `FALLIDO`, `EXPIRADO` | `PENDING_PAYMENT`, `PAYMENT_APPROVED`, `CONFIRMED`, `FAILED`, `EXPIRED` |
| `payment_attempt.result` | `APROBADO`, `RECHAZADO`, `ERROR` | `APPROVED`, `REJECTED`, `ERROR` |
| `payment_attempt.reason` | `FONDOS_INSUFICIENTES`, `DENEGADA_POR_EMISOR`, `ERROR_PROCESAMIENTO`, `DATOS_INVALIDOS` | `INSUFFICIENT_FUNDS`, `DECLINED_BY_ISSUER`, `PROCESSING_ERROR`, `INVALID_DATA` |
| `payment_attempt.brand` | `VISA`, `MASTERCARD`, `AMEX` | sin cambio |
| `order_ref.local_status` | `CREADO`, `PAGO_PENDIENTE_NOTIFICAR`, `PAGADO_NOTIFICADO`, `ANULACION_SOLICITADA`, `ANULADO` | `CREATED`, `PAYMENT_PENDING_NOTIFICATION`, `PAID_NOTIFIED`, `CANCELLATION_REQUESTED`, `CANCELLED` |
| `notification.type` | `CONFIRMACION_PEDIDO`, `REENVIO_CONFIRMACION` | `ORDER_CONFIRMATION`, `CONFIRMATION_RESEND` |
| `notification.status` | `PENDIENTE`, `ENVIADA`, `FALLIDA` | `PENDING`, `SENT`, `FAILED` |
| `return_ref.requested_type` | `CAMBIO`, `DEVOLUCION_DINERO` | `EXCHANGE`, `MONEY_REFUND` (Ventas: `CAMBIO`, `DEVOLUCION_DINERO`) |
| `evidence.type` | `IMAGEN` | `IMAGE` (Ventas: `IMAGEN`); el valor para PDF sigue pendiente de confirmar con Ventas |
| `attachment.status` | `PENDIENTE`, `ENVIADO` | `PENDING`, `SENT` |
| `outbox.type` | `NOTIFICAR_PAGO_VENTAS`, `SOLICITAR_ANULACION`, `ENVIAR_CORREO` | `NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL` |
| `outbox.status` | `PENDIENTE`, `PROCESADO`, `FALLIDO` | `PENDING`, `PROCESSED`, `FAILED` |

## Constraints e índices

Se traducen todos los nombres con el mismo patrón (`uq_<table>_<cols>`, `ck_<table>_<rule>`, `ix_<table>_<cols>`). Los sufijos descriptivos pasan a inglés (`ck_conversation_owner`, `ck_conversation_title_length`, `ix_attachment_pending_created_at`).

## Tareas

Ruta: escritores delegados, uno por vez (dispara el trigger de 4+ archivos y 2+ archivos no triviales). Cada escritor lee este documento antes de editar.

- [x] **N1** `docs/modelo-datos.md`: tablas, columnas, valores, Mermaid, convenciones, notas 🧩 y pendientes. Documentar la traducción de los literales de Ventas.
- [x] **N2** Resto de specs: SPEC (`spec.md`, `design.md`), ADR, historias, `kpis.md`, `privacidad.md`, `contratos-integracion.md`, `c4.md`, READMEs y `odd/tasks/*.md`. Solo identificadores de la base; reportar inconsistencias sin resolverlas.
- [x] **N3** Diagramas MER: `.excalidraw` (con copia previa en `~/.excalidraw-backups/ChatbotTaller/`) y re-exportar los `.svg`.
- [x] **N4** Backend: modelos, adapters, tests, `models/__init__.py`, comentario de `env.py`, `arquitectura-backend.md` (incluye el cambio de 13 a 14 tablas) y nombres de archivos de modelo y adapter.
- [x] **N5** `odd/tasks/hito-2.md`: nombres de tablas y tareas H2-02 a H2-07 en inglés, y nota de la convención para el resto del equipo.

## Criterios de aceptación

- `rg` de los nombres antiguos (glosarios de arriba) sobre specs y backend no encuentra apariciones, salvo las excepciones listadas en "No cambia" y los apartados que describen el renombre.
- `PYTHONPATH=. python -m pytest tests/unit` pasa.
- Las inconsistencias detectadas están reportadas y resueltas con el usuario.

## Progreso

N1, N2, N4 y N5 hechas y verificadas; N3 reducida por decisión del usuario a `mer-logico` (`mer-conceptual` queda sin cambios, con nombres mezclados). Verificación: barrido de nombres viejos en specs sin apariciones fuera de excepciones justificadas; `pytest tests/unit` con 23 passed; `Base.metadata` lista `attachment`, `conversation` y `local_phone_verification`; `mer-logico.excalidraw` válido y SVG re-exportado. Decisión tomada: unicidad de `notification` = `(order_id, resend_number)`. Quedan abiertas las inconsistencias de N2 (ver informe) y el renombre de los archivos vacíos de modelos y adapters, que cada responsable hace al implementarlos. Commits: pendiente de confirmación del usuario. Espejo en Engram: pendiente (`ambiguous_project`).

## Siguiente paso

Resolver las inconsistencias abiertas, confirmar el commit en specs (directo a `main`) y en backend y frontend (ramas propias), y pedir confirmación aparte para el push.
