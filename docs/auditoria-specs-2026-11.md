# Auditoría de specs contra el código — noviembre 2026

> **Alcance:** 24 capabilities de `openspec/specs/` contra `G3-Chatbot-backend` (rama `development`,
> 1214 tests) y `G3-Chatbot-frontend` (rama `development`, 663 tests), en el estado del 2026-11-21.
> **Método:** lectura de cada `spec.md` y `design.md`, contraste con routers, DTOs, casos de uso,
> estados, errores, manifiestos y llamadas del frontend; `docs/openapi.json` como vista canónica.
> **Regla:** la spec manda sobre el código. Si el código no la cumple, se registra como cambio
> pendiente; si la spec describe algo distinto de lo implementado, se corrige solo el drift mecánico
> (rutas, nombres, campos, estados) y se marca la decisión cuando cambia comportamiento.

## 1. Resumen

| Estado | Significado | Cantidad |
|---|---|---|
| ✅ Al día | La spec describe el comportamiento y los contratos que el código implementa hoy | **11** |
| ⚠️ Drift mecánico corregido | Nombres, rutas, campos o estados desalineados; corregidos en este PR sin cambiar comportamiento | **7** |
| ❌ Pendiente | La spec exige algo que el código no implementa o implementa distinto; requiere decisión o trabajo de código | **6** |
| **Total** | | **24** |

Correcciones aplicadas: **7 specs ⚠️** + **3 specs ❌** con drift mecánico puntual (rutas/headers/SSE).
Las 6 pendientes no se han “arreglado” inventando: van al plan de §3 y a las decisiones de §4.

## 2. Tabla de las 24 specs

Leyenda de evidencia: `BE` = `G3-Chatbot-backend`, `FE` = `G3-Chatbot-frontend`. Las rutas son relativas
a cada repositorio y todas las rutas backend llevan el prefijo `/api/v1`.

| # | Capability | Módulo(s) | Estado | Evidencia (`archivo:línea`) | Acción |
|---|---|---|---|---|---|
| 1 | `registro-cliente` (SPEC-01) | `mod-auth` | ⚠️ Corregida | `BE/src/modules/mod_auth/adapters/http/session_router.py:387` (201); `BE/src/modules/mod_auth/application/manage_session_use_case.py:114-116` (devuelve `estado` y `correoEnmascarado`); `BE/src/shared/infrastructure/http/security_client.py:205` (`canalOrigen: CHATBOT`) | El escenario decía `201 {id, estado}`. Corregido a `{estado, correoEnmascarado}`; el resto (validación, rate limit 5/IP/10 min, errores) coincide |
| 2 | `verificacion-correo` (SPEC-02) | `mod-auth` | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:466` (204), `:482` (202); `BE/src/shared/infrastructure/http/security_client.py` (`verify_email`, `resend_verification`); `FE/src/modules/mod-auth/ui/VerificarCorreoPage.tsx` | Sin cambios |
| 3 | `inicio-sesion` (SPEC-03) | `mod-auth` (+ `mod-cart`) | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:237` (login), `:340` (refresh), `:359` (logout), `:374` (perfil); cookies `chat_rt`/`chat_chg`; `FE/src/shared/api/http.ts:62-80` (refresh single-flight) | Sin cambios |
| 4 | `validacion-celular` (SPEC-04 · H-17) | `mod-auth` + `mod-checkout` | ❌ Pendiente | `BE/src/shared/infrastructure/db/models/local_phone_verification.py:23-27` solo guarda `customer_id`, `phone` y `verified_at`: no hay almacén de OTP (código, intentos, expiración, límite de reenvíos); `BE/src/shared/infrastructure/persistence/local_phone_verification_postgres_adapter.py:3-6` dice «No incluye OTP/SMS/CheckoutGuard»; `BE/src/shared/infrastructure/http/dependencies/checkout_guard.py:1-3` es solo un shim de `require_customer`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:198-203` solo valida si llega `contacto.celular`; no hay router `/contacto/celular/*`; `FE/src/modules/mod-auth/adapters/authApi.ts:80` llama a `/contacto/celular/verificar-otp` | **Gap de implementación, no de spec:** `openspec/specs/validacion-celular/design.md:24-27` ya define `solicitar-otp`, `verificar-otp`, `SmsSender` y `CheckoutGuard`. Falta el almacén OTP, el `SmsSender`/`SimulatedSmsSender` y el guard efectivo. Mantener ❌ hasta decidir D1 (§4) |
| 5 | `motor-conversacion` (SPEC-05) | `mod-chat` | ⚠️ Corregida | `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:154-166` (acciones directas ya implementadas), `:182-185` (`adjuntoIds` devuelve 501); `BE/src/modules/mod_chat/application/interpret_and_respond_use_case.py:78-85` (`QUICK_ACTIONS`); `BE/src/modules/mod_catalog/application/tools.py:153-179` (catálogo real de tools) | Corregido el escenario que decía que las acciones «aún no están implementadas». Quedan gaps de código: tools de reclamos/devoluciones/cuenta y adjuntos (ver §5) |
| 6 | `busqueda-filtrado` (SPEC-06) | `mod-catalog` | ⚠️ Corregida | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:71-87` (`categoria`, `marca`; `_ = orden` ignora el orden); `BE/src/modules/mod_catalog/application/tools.py:56-62` (esquema real); `BE/src/modules/mod_catalog/domain/product_normalizer.py:15` (`DEFAULT_SYNONYMS`) | Corregido el esquema de la herramienta y el NFR de sinónimos (código, no `config/sinonimos.yaml`). Gap: `orden` no se aplica (M4) |
| 7 | `recomendacion` (SPEC-07) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:119` (`recommend`), `:274` (`cross_sell`); `BE/src/modules/mod_catalog/application/tools.py:155`; `BE/src/modules/mod_chat/application/tools/action_dispatcher.py` (`SILENCIAR_COMPLEMENTOS`) | Sin cambios |
| 8 | `ofertas-promociones` (SPEC-08) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:106` (`GET /catalogo/promociones`); `BE/src/modules/mod_catalog/application/tools.py:154`; `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py` (`promotions`, `price_projection`) | Sin cambios |
| 9 | `tarjetas-detalle-producto` (SPEC-09) | `mod-catalog` | ⚠️ Corregida | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:674-687` (`product_id`, `image`, `short_description`, `has_variants`, `single_sku`, `availability`); `FE/src/modules/mod-catalog/domain/entities/CatalogoUI.ts:50-62` | Corregidos los nombres de `ProductoResumen` en la spec (`productoId`, `nombre`, `imagenUrl`, `precio`, `descripcionBreve`, `tieneVariantes`, `skuUnico` → nombres reales) |
| 10 | `validacion-stock` (SPEC-10) | `mod-catalog` + `mod-cart` + `mod-checkout` | ❌ Pendiente | `BE/src/modules/mod_cart/application/manage_cart_use_case.py:249-275` (`validate_cart` existe); `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:227-321` **no** llama a `validate_cart`; solo mapea el 409 de Ventas a `STOCK_INSUFICIENTE` (`:321`) | Decidir si el checkout revalida en el chatbot o delega en Ventas; si se mantiene la spec, cablear `validate_cart` (M2/D3) |
| 11 | `gestion-carrito` (SPEC-11) | `mod-cart` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:96-220`; `BE/src/modules/mod_cart/application/manage_cart_use_case.py` (límites 10/20, `version` optimista); `BE/src/shared/infrastructure/db/models/cart.py` (`version_id_col`) | Sin cambios |
| 12 | `direccion-cotizacion-envio` (SPEC-12) | `mod-shipping` + `mod-checkout` | ⚠️ Corregida | `BE/src/modules/mod_shipping/application/shipping_quote.py:29-34` (`sku` + `cantidad`, sin peso/volumen); `BE/src/modules/mod_shipping/adapters/http/shipping_router.py:105-122`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:392-410` | Corregidos los pasajes de `pesoKg`/`volumenM3` y el escenario de peso por categoría; el diseño ya decía que Despacho resuelve lo físico. Gap: guardado de dirección (M3) |
| 13 | `cupones` (SPEC-13) | `mod-cart` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:189` (aplicar), `:220` (quitar); `BE/src/modules/mod_cart/application/manage_cart_use_case.py:151-227` (validación, reemplazo, `CouponAttempts`, 429) | Sin cambios |
| 14 | `checkout-pago` (SPEC-14) | `mod-checkout` | ✅ Al día | `BE/src/modules/mod_checkout/adapters/http/checkout_router.py:93` (201), `:134`, `:156`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py` (15 min, 3 intentos, introspección fail-closed, estados `PENDING_PAYMENT`/`PAYMENT_APPROVED`/`FAILED`/`EXPIRED`) | Sin cambios |
| 15 | `grabacion-pedido` (SPEC-15) | `mod-checkout` + `mod-orders` | ✅ Al día | `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:290-340` (crea pedido en Ventas y `order_ref`); `BE/src/shared/infrastructure/worker/outbox_worker.py:62-74` (`NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`) | Sin cambios |
| 16 | `notificacion-confirmacion` (SPEC-16) | `mod-orders` | ✅ Al día | `BE/src/modules/mod_orders/application/notification_service.py:48` (`MAX_RESENDS = 2`), `:156-212`; `BE/src/shared/infrastructure/worker/outbox_worker.py:70` (`SEND_EMAIL`), `:158-165` (backoff) | Sin cambios |
| 17 | `consulta-estado-pedido` (SPEC-17) | `mod-orders` | ✅ Al día | `BE/src/modules/mod_orders/adapters/http/orders_router.py:138` (lista), `:160` (detalle), `:178` (seguimiento), `:197` (reenvío 202); `BE/src/modules/mod_orders/application/orders_service.py:45-89` | Sin cambios |
| 18 | `seguimiento-despacho` (SPEC-18) | `mod-orders` + `mod-shipping` | ✅ Al día | `BE/src/modules/mod_orders/adapters/http/orders_router.py:178`; `BE/src/modules/mod_orders/domain/tracking_mapper.py:22-62` (lista blanca, `recibidoPor` solo frontend); `BE/src/modules/mod_shipping/adapters/despacho_client.py:36` (timeout 4 s), `:62-77` | Sin cambios |
| 19 | `creacion-reclamo` (SPEC-19) | `mod-postventa` | ❌ Pendiente | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:46` (201), `:53` (`Idempotency-Key`); `BE/src/modules/mod_postventa/application/postventa_service.py:142-197` (no consulta el listado para detectar duplicados; solo idempotencia por clave) | Corregido el header (`X-Idempotency-Key` → `Idempotency-Key`) y la ruta de duplicados. Falta la detección de duplicados (M1/D4) |
| 20 | `consulta-reclamo` (SPEC-20) | `mod-postventa` | ⚠️ Corregida | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:74` (lista), `:94` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:210-226`; estados G5 `REGISTRADO`/`EN_PROCESO`/`ATENDIDO`/`DERIVADO` | Corregida la ruta del requisito a `GET /api/v1/reclamos` (proxy a `/me`, sin `clienteId`) |
| 21 | `solicitud-devolucion-cambio` (SPEC-21) | `mod-postventa` | ❌ Pendiente | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:64` (evidencia 201), `:100` (devolución 201); `BE/src/modules/mod_postventa/application/postventa_service.py:69-140` (no consulta `/me` para duplicados); `RETURN_REASON_TO_G5` en `postventa_dto.py` | Corregida la ruta de duplicados a `GET /api/v1/devoluciones`. Falta detección de duplicados (M1/D4) |
| 22 | `consulta-devolucion-reembolso` (SPEC-22) | `mod-postventa` | ⚠️ Corregida | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:126` (lista), `:148` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:121-140`; `postventa_dto.py` (`resolucion`, `estadoReembolso`) | Corregidas las rutas del requisito y del escenario a `/api/v1/devoluciones` (proxy a `/me` y `/{id}`) |
| 23 | `adjuntos-imagenes-chat` (SPEC-23) | `mod-chat` (+ `shared/`) | ❌ Pendiente | `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:182-185` (`adjuntoIds` → 501); `BE/src/shared/infrastructure/persistence/attachment_postgres_adapter.py` y modelo `attachment` existen; no hay endpoints `/chat/conversaciones/{id}/adjuntos` ni `/chat/adjuntos/{id}` en `docs/openapi.json` | Implementar SPEC-23 completo o retirar la UI/manifiesto (D2). Corregido el `202` del diseño a `200 SSE` |
| 24 | `retroalimentacion-cliente` (SPEC-24) | `mod-postventa` + `mod-chat` + `mod-checkout` | ❌ Pendiente | `BE/src/modules/mod_postventa/adapters/http/csat_router.py:29` (solo CSAT); `BE/src/modules/mod_postventa/application/postventa_service.py:228`; no hay endpoints de reacciones, sugerencias ni valoración; `FE/src/modules/mod-chat/ui/BotFeedback.tsx:7-9`, `FE/src/modules/mod-chat/ui/SugerenciaForm.tsx:10-23` y `FE/src/modules/mod-checkout/ui/RatingPopup.tsx:9-13` son estado local | Implementar reacciones (`POST /mensajes/{id}/reaccion`), sugerencias (`POST /sugerencias`) y valoración (`POST /pedidos/{id}/valoracion-compra`) + tablas/outbox, o retirarlos del alcance (D5) |

**Nota operativa (fuera de las 24 capabilities).** El contrato de `/health` cambió con la validación de
capacidades: `discovery.configure_modules` aborta si falta una `REQUIRED_CAPABILITIES` y, si falta una
`OPTIONAL_CAPABILITIES`, registra un `ERROR` y `/health` responde `200` con
`{"status": "degraded", "missingCapabilities": [...]}` en vez de `{"status": "ok"}`. No hay una spec
de operación que cubra
`/health`; el comportamiento queda documentado en
[`modularizacion.md`](arquitectura/modularizacion.md#3-dag-de-dependencias). Evidencia:
`BE/src/infrastructure/discovery.py:54-74` y `BE/src/shared/infrastructure/http/health_router.py:10-14`.

## 3. Plan priorizado para llegar al 100 %

### S — Corto plazo (≤ 1 día cada uno)

| ID | Acción | Módulo / repo | Dueño sugerido | Criterio de cierre |
|---|---|---|---|---|
| S1 | Decidir y ejecutar el contrato de `/contacto/celular`: implementar `solicitar-otp`/`verificar-otp` o retirar `validarContactoCelular`, su manifiesto y su test | `mod-auth` (BE/FE) | @Ankarmin | No queda ninguna llamada del FE a un endpoint ausente; spec y `docs/openapi.json` coinciden |
| S2 | Añadir un gate que compare los `endpoints` de cada `module.manifest.ts` contra `docs/openapi.json` (paths + tag `mod-*`) | Plataforma / CI | @Ankarmin | El gate falla si un endpoint del manifiesto no existe o tiene otro tag; el test manual deja de ser la única red |
| S3 | Revisar y actualizar los `MODULE.md` de `mod-auth`, `mod-postventa` y `mod-chat` con lo que realmente exponen (OTP, duplicados, adjuntos, reacciones) | Docs de módulo | Owner de cada módulo | `MODULE.md` no promete rutas inexistentes |
| S4 | Cerrar la deuda de nombres: `productoId`/`nombre`/`precio` en docs históricos vs `product_id`/`name`/`price` en código | `mod-catalog` | @SOoOnny | Grep de nombres antiguos en specs = 0 (o marcados como históricos) |

### M — Medio plazo (1–3 días cada uno)

| ID | Acción | Módulo / repo | Dueño sugerido | Criterio de cierre |
|---|---|---|---|---|
| M1 | Detección de duplicados de reclamos y devoluciones: consultar `GET /api/v1/reclamos`/`/devoluciones` y filtrar por pedido + motivo/estado antes de crear; avisar y permitir “registrar igual” | `mod-postventa` | @MathiasTL | Escenarios “reclamo/solicitud abierta existente” y “previa resuelta” pasan; no se crea duplicado sin confirmación |
| M2 | Revalidación de stock al iniciar checkout: invocar `validate_cart` y mapear líneas agotadas/insuficientes a `409 CARRITO_DESACTUALIZADO` con detalle, o cambiar la spec para delegar en Ventas | `mod-checkout` + `mod-cart` | @MathiasTL + @SOoOnny | Decisión D3 cerrada; prueba del carrito que cambia entre agregar y pagar |
| M3 | Guardado opcional de dirección en Seguridad (`GuardarDireccionOpcional`) sin bloquear el checkout | `mod-checkout` + `mod-shipping` | @SOoOnny + @MathiasTL | Escenario “cliente marca guardar” y “Seguridad falla” cubiertos |
| M4 | Aplicar `orden` en la búsqueda o retirarlo del contrato/spec | `mod-catalog` | @SOoOnny | `orden` tiene efecto o deja de anunciarse; test de orden por nombre |
| M5 | Completar el catálogo de tools del chat (reclamos, devoluciones, cuenta) o mover esas intenciones a “pendiente” en la spec | `mod-chat` | @Ankarmin | La tabla de intenciones de SPEC-05 coincide con `_TOOLS` y `QUICK_ACTIONS` |

### L — Largo plazo (1–2 semanas)

| ID | Acción | Módulo / repo | Dueño sugerido | Criterio de cierre |
|---|---|---|---|---|
| L1 | SPEC-04 completo (H-17): almacén de OTP (código, intentos, expiración, límite de reenvíos), `SmsSender` simulado, endpoints de OTP, `CheckoutGuard`, bloqueo de checkout y UI | `mod-auth` + `mod-checkout` | @Ankarmin | Los 3 requisitos y 7 escenarios de SPEC-04 pasan; `CELULAR_NO_VERIFICADO` real |
| L2 | SPEC-23 completo: `AttachmentStorage`, carga/borrado/URL firmada, EXIF, miniaturas, multimodal, límites y limpieza | `mod-chat` + `shared/` | @MathiasTL + @Ankarmin | Los 10 requisitos y sus escenarios pasan; `adjuntoIds` deja de ser 501 |
| L3 | SPEC-24 completo: reacciones, sugerencias/bugs, valoración de compra, notificación interna, límites y tablas | `mod-chat` + `mod-postventa` + `mod-checkout` | @Ankarmin + @MathiasTL | CSAT + los 3 mecanismos con endpoints, tablas y pruebas; UI deja de ser estado local |
| L4 | Endurecer el contrato: OpenAPI como fuente, tests de contrato por módulo y validación en CI de los tags | Plataforma | @Ankarmin | S2 convertido en gate bloqueante y documentado en `modularizacion.md` |

## 4. Decisiones de producto necesarias

1. **D1 — ¿Se implementa SPEC-04/H-17 o se retira la verificación local del celular?** El frontend ya llama
   `/contacto/celular/verificar-otp`, el backend no lo expone y el checkout no exige celular verificado.
   Opciones: (a) implementar OTP + guard en el próximo hito; (b) retirar la llamada, el manifiesto y el
   test, y aceptar que el checkout no bloquee por celular. **No se puede dejar como está.**
2. **D2 — ¿SPEC-23 (adjuntos) entra en el alcance?** Hay modelo `attachment`, ruta `/sugerencias` y UI
   de cámara, pero no endpoints ni storage. Si no entra, se retiran del manifiesto y de la UI.
3. **D3 — ¿La revalidación de stock del checkout es responsabilidad del chatbot o de Ventas?** Hoy el
   chatbot tiene `validate_cart` sin cablear y depende del 409 de Ventas. Si se delega, SPEC-10 debe
   cambiar; si no, hay que cablearlo.
4. **D4 — ¿La detección de duplicados de reclamos/devoluciones se hace en el chatbot o Ventas debe
   exponer un filtro por pedido?** La spec hoy dice que el chatbot filtra el listado `/me`.
5. **D5 — ¿SPEC-24 completo o solo CSAT?** Reacciones, sugerencias y valoración de compra tienen UI y
   diseño, pero no endpoints ni tablas. ¿Se implementan o se declaran fuera de alcance?
6. **D6 — ¿Se guarda la dirección en Seguridad desde el checkout?** La casilla existe en la UI y en la
   spec; el backend no llama a `POST /usuarios/{id}/direcciones`.
7. **D7 — ¿`orden` de búsqueda se implementa en el servidor o se retira?** Hoy el router acepta el
   parámetro y lo ignora (`_ = orden`).

## 5. Cambios de código que las specs exigen y aún no existen

| Spec | Cambio exigido | Evidencia del hueco |
|---|---|---|
| SPEC-04 (H-17) | `POST /contacto/celular/solicitar-otp`, `POST /contacto/celular/verificar-otp`, almacén de OTP (código, intentos, expiración, límite de reenvíos), `SmsSender`/`SimulatedSmsSender`, `CheckoutGuard` y bloqueo de checkout | `BE/src/shared/infrastructure/db/models/local_phone_verification.py:23-27`; `BE/src/shared/infrastructure/persistence/local_phone_verification_postgres_adapter.py:3-6`; no hay router; `FE/src/modules/mod-auth/adapters/authApi.ts:80` llama al endpoint ausente. La spec/design ya definen el contrato: el gap es de implementación |
| SPEC-10 | `validate_cart` invocado desde `POST /checkout`, con detalle por línea | `BE/src/modules/mod_cart/application/manage_cart_use_case.py:249` existe; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:227-321` no lo llama |
| SPEC-12 | Prellenado con la dirección guardada y `GuardarDireccionOpcional` en la creación del pedido | `BE/src/modules/mod_shipping/adapters/http/shipping_router.py:105` solo lista direcciones; el frontend no llama `/direcciones`; no hay `POST /direcciones` en el BFF |
| SPEC-19 | Detección de reclamo abierto por pedido + motivo antes de crear | `BE/src/modules/mod_postventa/application/postventa_service.py:142-197` no consulta `list_customer_claims` |
| SPEC-21 | Detección de devolución abierta por pedido antes de crear | `BE/src/modules/mod_postventa/application/postventa_service.py:69-140` no consulta `list_customer_returns` |
| SPEC-23 | Endpoints de adjuntos, `AttachmentStorage`, miniaturas, URLs firmadas, limpieza y multimodal | `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:182-185` (501); no hay endpoints en `docs/openapi.json` |
| SPEC-24 | `POST /mensajes/{id}/reaccion`, `POST /pedidos/{id}/valoracion-compra`, `POST /sugerencias`, tablas `message_reaction`/`feedback_suggestion`/`purchase_rating`, `order_ref.csat_sent` y outbox interno | `BE/src/modules/mod_postventa/adapters/http/csat_router.py:29` es el único endpoint; no hay tablas ni servicios; `FE/src/modules/mod-chat/ui/BotFeedback.tsx`, `FE/src/modules/mod-chat/ui/SugerenciaForm.tsx` y `FE/src/modules/mod-checkout/ui/RatingPopup.tsx` no llaman al backend |
| SPEC-24 | Marcar `order_ref.csat_sent` cuando Ventas responde 201/409 | No existe la columna ni la actualización (grep sin resultados) |
| SPEC-06 | Aplicar `orden` o retirarlo | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:87` (`_ = orden`) |
| SPEC-05 | Tools de reclamos, devoluciones y cuenta; `verificar_celular`; `nueva_conversacion`/`buscar_conversaciones` | `BE/src/modules/mod_catalog/application/tools.py:153-179` solo registra catálogo, carrito, pedidos y `solicitar_registro`; `QUICK_ACTIONS` no los incluye |

## 6. Notas de método y límites

- **No se tocó código de backend ni frontend.** La auditoría es de solo lectura; las correcciones se
  hicieron únicamente en `openspec/specs/`.
- **No se inventaron decisiones.** Las 6 specs ❌ quedan con la pregunta concreta en §4; las
  correcciones mecánicas de §2 están marcadas como tales.
- **Los tests no se ejecutaron** en esta auditoría: el estado “1214 backend / 663 frontend” es el
  reportado por el equipo en `development`. La evidencia es estática (código, OpenAPI, manifiestos).
- **Validación OpenSpec:** `npx @fission-ai/openspec validate --specs` pasa las 24 specs con avisos de
  Gherkin en español. `--strict` falla en las 24 porque exige `WHEN`/`THEN` en inglés; no es un fallo
  introducido por esta auditoría.
- **Cobertura de la evidencia:** las rutas `archivo:línea` apuntan al punto que prueba la afirmación;
  cuando el hueco es una ausencia (p. ej. un endpoint que no existe), se cita el archivo que debería
  contenerlo o el adapter que lo llama.
- **Mantenimiento:** al cerrar cada punto del plan, actualizar esta tabla y el estado de la spec en el
  mismo PR, según [`docs/flujo-de-trabajo.md`](flujo-de-trabajo.md).
