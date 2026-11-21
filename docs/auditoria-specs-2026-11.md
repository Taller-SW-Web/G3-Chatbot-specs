# Auditoría de specs contra el código — noviembre 2026

> **Alcance:** 24 capabilities de `openspec/specs/` contra `G3-Chatbot-backend` (rama `development`,
> 1214 tests) y `G3-Chatbot-frontend` (rama `development`, 663 tests), en el estado del 2026-11-21.
> **Método:** lectura de cada `spec.md` y `design.md`, contraste con routers, DTOs, casos de uso,
> estados, errores, manifiestos y llamadas del frontend; `docs/openapi.json` como vista canónica.
> **Regla:** la spec manda sobre el código. Si el código no la cumple, se registra como cambio
> pendiente; si la spec describe algo distinto de lo implementado, se corrige solo el drift mecánico
> (rutas, nombres, campos, estados) y se marca la decisión cuando cambia comportamiento.
>
> **Actualización 2026-11-21:** el dueño resolvió las 7 decisiones de producto de §4. Las 6 specs
> pendientes pasan a **🟡 En implementación**; SPEC-06 y SPEC-12 se suman porque D7 y D6 convierten sus
> correcciones mecánicas en comportamiento pendiente de código. Ninguna se marca **✅** hasta que el
> código esté mergeado y verificado.

## 1. Resumen

| Estado | Significado | Cantidad |
|---|---|---|
| ✅ Al día | La spec describe el comportamiento y los contratos que el código implementa hoy | **11** |
| ⚠️ Drift mecánico corregido | Nombres, rutas, campos o estados desalineados; corregidos en este PR sin cambiar comportamiento | **5** |
| 🟡 En implementación | Decisión de producto cerrada y contrato escrito; el código aún no está mergeado | **8** |
| **Total** | | **24** |

Correcciones aplicadas: **5 specs ⚠️** (1, 5, 9, 20 y 22) + **8 specs 🟡** con contrato decidido
(4, 6, 10, 12, 19, 21, 23 y 24). Las 8 en implementación no se “arreglan” inventando: cada una tiene
su decisión en §4, su criterio de cierre en §6 y su ADR cuando el impacto es estructural.

> **Por qué 8 y no 6:** la auditoría original marcaba 6 ❌ (4, 10, 19, 21, 23, 24). Las decisiones D6
> (dirección) y D7 (orden) añaden trabajo de código a SPEC-12 y SPEC-06, que estaban como ⚠️; dejarlas
> en ⚠️ ocultaría que su contrato ya cambió. Se reclasifican como 🟡 para que el seguimiento sea honesto.

## 2. Tabla de las 24 specs

Leyenda de evidencia: `BE` = `G3-Chatbot-backend`, `FE` = `G3-Chatbot-frontend`. Las rutas son relativas
a cada repositorio y todas las rutas backend llevan el prefijo `/api/v1`.

| # | Capability | Módulo(s) | Estado | Evidencia (`archivo:línea`) | Acción |
|---|---|---|---|---|---|
| 1 | `registro-cliente` (SPEC-01) | `mod-auth` | ⚠️ Corregida | `BE/src/modules/mod_auth/adapters/http/session_router.py:387` (201); `BE/src/modules/mod_auth/application/manage_session_use_case.py:114-116` (devuelve `estado` y `correoEnmascarado`); `BE/src/shared/infrastructure/http/security_client.py:205` (`canalOrigen: CHATBOT`) | El escenario decía `201 {id, estado}`. Corregido a `{estado, correoEnmascarado}`; el resto (validación, rate limit 5/IP/10 min, errores) coincide. Promover a ✅ al refrescar la auditoría tras el merge |
| 2 | `verificacion-correo` (SPEC-02) | `mod-auth` | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:466` (204), `:482` (202); `BE/src/shared/infrastructure/http/security_client.py` (`verify_email`, `resend_verification`); `FE/src/modules/mod-auth/ui/VerificarCorreoPage.tsx` | Sin cambios |
| 3 | `inicio-sesion` (SPEC-03) | `mod-auth` (+ `mod-cart`) | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:237` (login), `:340` (refresh), `:359` (logout), `:374` (perfil); cookies `chat_rt`/`chat_chg`; `FE/src/shared/api/http.ts:62-80` (refresh single-flight) | Sin cambios |
| 4 | `validacion-celular` (SPEC-04 · H-17) | `mod-auth` + `mod-checkout` | 🟡 En implementación | `BE/src/modules/mod_auth/adapters/http/phone_router.py:81` (`solicitar-otp`) y `:92` (`verificar-otp`); `BE/src/modules/mod_auth/application/manage_phone_verification_use_case.py` (HMAC, TTL, intentos, ventana); `BE/src/shared/infrastructure/db/models/phone_otp_challenge.py`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:198-203` ya consulta el verificador; `FE/src/modules/mod-auth/adapters/authApi.ts:83` y `:87` llaman a ambos endpoints | **D1 resuelta:** implementación presente en la rama; faltan merge, pruebas de los escenarios (reenvío, código consumido, cambio de celular), la bandera documentada y verificar el bloqueo real del checkout. Ver §6 y ADR-0026 |
| 5 | `motor-conversacion` (SPEC-05) | `mod-chat` | ⚠️ Corregida | `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:154-166` (acciones directas ya implementadas), `:182-185` (`adjuntoIds` devuelve 501); `BE/src/modules/mod_chat/application/interpret_and_respond_use_case.py:78-85` (`QUICK_ACTIONS`); `BE/src/modules/mod_catalog/application/tools.py:153-179` (catálogo real de tools) | Corregido el escenario que decía que las acciones «aún no están implementadas». Quedan gaps de código: tools de reclamos/devoluciones/cuenta y adjuntos (ver §5). `adjuntoIds` se cierra con D2 |
| 6 | `busqueda-filtrado` (SPEC-06) | `mod-catalog` | 🟡 En implementación | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:71-87` (`categoria`, `marca`; `_ = orden` ignora el orden); `BE/src/modules/mod_catalog/application/tools.py:56-62` (esquema real); `BE/src/modules/mod_catalog/domain/product_normalizer.py:15` (`DEFAULT_SYNONYMS`) | **D7 resuelta:** `orden` pasa a `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc`, con `400 VALIDACION` fuera del conjunto. Ver §6 |
| 7 | `recomendacion` (SPEC-07) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:119` (`recommend`), `:274` (`cross_sell`); `BE/src/modules/mod_catalog/application/tools.py:155`; `BE/src/modules/mod_chat/application/tools/action_dispatcher.py` (`SILENCIAR_COMPLEMENTOS`) | Sin cambios |
| 8 | `ofertas-promociones` (SPEC-08) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:106` (`GET /catalogo/promociones`); `BE/src/modules/mod_catalog/application/tools.py:154`; `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py` (`promotions`, `price_projection`) | Sin cambios |
| 9 | `tarjetas-detalle-producto` (SPEC-09) | `mod-catalog` | ⚠️ Corregida | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:674-687` (`product_id`, `image`, `short_description`, `has_variants`, `single_sku`, `availability`); `FE/src/modules/mod-catalog/domain/entities/CatalogoUI.ts:50-62` | Corregidos los nombres de `ProductoResumen` en la spec (`productoId`, `nombre`, `imagenUrl`, `precio`, `descripcionBreve`, `tieneVariantes`, `skuUnico` → nombres reales). Promover a ✅ tras el merge |
| 10 | `validacion-stock` (SPEC-10) | `mod-catalog` + `mod-cart` + `mod-checkout` | 🟡 En implementación | `BE/src/modules/mod_cart/application/manage_cart_use_case.py:249-275` (`validate_cart` existe); `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:264` ya invoca `_revalidate_stock` y `module.py:108` cablea `cart_validator=provide_cart_service(session).validate_cart`; el error devuelve `lineas` con `AGOTADO`/`STOCK_INSUFICIENTE`/`NO_CONFIRMADO` | **D3 resuelta:** el cableado existe en la rama de implementación; faltan merge, pruebas del contrato `lineas` y la verificación de que no se crea checkout/pedido. Ver §6 |
| 11 | `gestion-carrito` (SPEC-11) | `mod-cart` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:96-220`; `BE/src/modules/mod_cart/application/manage_cart_use_case.py` (límites 10/20, `version` optimista); `BE/src/shared/infrastructure/db/models/cart.py` (`version_id_col`) | Sin cambios |
| 12 | `direccion-cotizacion-envio` (SPEC-12) | `mod-shipping` + `mod-checkout` | 🟡 En implementación | `BE/src/modules/mod_shipping/application/shipping_quote.py:29-34` (`sku` + `cantidad`, sin peso/volumen); `BE/src/modules/mod_shipping/adapters/http/shipping_router.py:105-122`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:392-410`; `CreateCheckoutRequest.guardarDireccion` existe en `commerce_contracts_dto.py:319` pero el router no lo propaga al caso de uso | **D6 resuelta:** `guardarDireccion` en `POST /checkout`; si Seguridad falla, `201` con `avisoDireccion` y el checkout continúa. Ver §6 |
| 13 | `cupones` (SPEC-13) | `mod-cart` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:189` (aplicar), `:220` (quitar); `BE/src/modules/mod_cart/application/manage_cart_use_case.py:151-227` (validación, reemplazo, `CouponAttempts`, 429) | Sin cambios |
| 14 | `checkout-pago` (SPEC-14) | `mod-checkout` | ✅ Al día | `BE/src/modules/mod_checkout/adapters/http/checkout_router.py:93` (201), `:134`, `:156`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py` (15 min, 3 intentos, introspección fail-closed, estados `PENDING_PAYMENT`/`PAYMENT_APPROVED`/`FAILED`/`EXPIRED`) | Sin cambios; consume D1, D3 y D6 a través de sus guardas |
| 15 | `grabacion-pedido` (SPEC-15) | `mod-checkout` + `mod-orders` | ✅ Al día | `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:290-340` (crea pedido en Ventas y `order_ref`); `BE/src/shared/infrastructure/worker/outbox_worker.py:62-74` (`NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`) | Sin cambios |
| 16 | `notificacion-confirmacion` (SPEC-16) | `mod-orders` | ✅ Al día | `BE/src/modules/mod_orders/application/notification_service.py:48` (`MAX_RESENDS = 2`), `:156-212`; `BE/src/shared/infrastructure/worker/outbox_worker.py:70` (`SEND_EMAIL`), `:158-165` (backoff) | Sin cambios |
| 17 | `consulta-estado-pedido` (SPEC-17) | `mod-orders` | ✅ Al día | `BE/src/modules/mod_orders/adapters/http/orders_router.py:138` (lista), `:160` (detalle), `:178` (seguimiento), `:197` (reenvío 202); `BE/src/modules/mod_orders/application/orders_service.py:45-89` | Sin cambios |
| 18 | `seguimiento-despacho` (SPEC-18) | `mod-orders` + `mod-shipping` | ✅ Al día | `BE/src/modules/mod_orders/adapters/http/orders_router.py:178`; `BE/src/modules/mod_orders/domain/tracking_mapper.py:22-62` (lista blanca, `recibidoPor` solo frontend); `BE/src/modules/mod_shipping/adapters/despacho_client.py:36` (timeout 4 s), `:62-77` | Sin cambios |
| 19 | `creacion-reclamo` (SPEC-19) | `mod-postventa` | 🟡 En implementación | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:46` (201), `:53` (`Idempotency-Key`); `BE/src/modules/mod_postventa/application/postventa_service.py:194-202` detecta `RECLAMO_DUPLICADO` y `:280-303` filtra el listado real por pedido + motivo | **D4 resuelta:** lógica presente en la rama; faltan merge, pruebas de duplicado/forzar/idempotencia y el contrato `{reclamoId, codigoSeguimiento, estado}`. Corregido el header y la ruta de duplicados. Ver §6 |
| 20 | `consulta-reclamo` (SPEC-20) | `mod-postventa` | ⚠️ Corregida | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:74` (lista), `:94` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:210-226`; estados G5 `REGISTRADO`/`EN_PROCESO`/`ATENDIDO`/`DERIVADO` | Corregida la ruta del requisito a `GET /api/v1/reclamos` (proxy a `/me`, sin `clienteId`). Promover a ✅ tras el merge |
| 21 | `solicitud-devolucion-cambio` (SPEC-21) | `mod-postventa` | 🟡 En implementación | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:64` (evidencia 201), `:100` (devolución 201); `BE/src/modules/mod_postventa/application/postventa_service.py:94-104` detecta `DEVOLUCION_DUPLICADA` y `:305-338` compara pedido, motivo y firma de líneas | **D4 resuelta:** lógica presente en la rama; faltan merge, pruebas de duplicado/forzar/evidencia e idempotencia y el contrato `{devolucionId, estado, motivo}`. Corregida la ruta de duplicados a `GET /api/v1/devoluciones`. Ver §6 |
| 22 | `consulta-devolucion-reembolso` (SPEC-22) | `mod-postventa` | ⚠️ Corregida | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:126` (lista), `:148` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:121-140`; `postventa_dto.py` (`resolucion`, `estadoReembolso`) | Corregidas las rutas del requisito y del escenario a `/api/v1/devoluciones` (proxy a `/me` y `/{id}`). Promover a ✅ tras el merge |
| 23 | `adjuntos-imagenes-chat` (SPEC-23) | `mod-chat` (+ `shared/`) | 🟡 En implementación | `BE/src/modules/mod_chat/adapters/http/attachment_router.py:51` (carga 201), `:80` (borrado 204), `:113` (URL firmada); `BE/src/modules/mod_chat/application/attachment_service.py`; `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:183-213` acepta `adjuntoIds` y ya no responde `501`; `BE/src/shared/application/ports/attachment_storage_port.py` | **D2 resuelta:** implementación presente en la rama (storage, límites, EXIF, miniaturas, URL firmada, limpieza y `adjuntoIds`); faltan merge, pruebas de los 10 requisitos y verificar el job de limpieza. Ver §6 y ADR-0028 |
| 24 | `retroalimentacion-cliente` (SPEC-24) | `mod-postventa` + `mod-chat` + `mod-checkout` | 🟡 En implementación | `BE/src/modules/mod_postventa/adapters/http/csat_router.py:29` (solo CSAT); `BE/src/modules/mod_postventa/application/postventa_service.py:228`; no hay endpoints de reacciones, sugerencias ni valoración; `FE/src/modules/mod-chat/ui/BotFeedback.tsx:7-9`, `FE/src/modules/mod-chat/ui/SugerenciaForm.tsx:10-23` y `FE/src/modules/mod-checkout/ui/RatingPopup.tsx:9-13` son estado local | **D5 resuelta:** reacciones, sugerencias/bugs con adjunto, CSAT, valoración de compra y notificación interna. Ver §6 y ADR-0029 |

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

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| S1 | Contrato de `/contacto/celular`: implementar `solicitar-otp`/`verificar-otp` (la ejecución completa está en L1) | `mod-auth` (BE/FE) | @Ankarmin | 🟡 En implementación (D1) | No queda ninguna llamada del FE a un endpoint ausente; spec y `docs/openapi.json` coinciden |
| S2 | Añadir un gate que compare los `endpoints` de cada `module.manifest.ts` contra `docs/openapi.json` (paths + tag `mod-*`) | Plataforma / CI | @Ankarmin | ⬜ Pendiente | El gate falla si un endpoint del manifiesto no existe o tiene otro tag; el test manual deja de ser la única red |
| S3 | Revisar y actualizar los `MODULE.md` de `mod-auth`, `mod-postventa` y `mod-chat` con lo que realmente exponen (OTP, duplicados, adjuntos, reacciones) | Docs de módulo | Owner de cada módulo | 🟡 En implementación | `MODULE.md` no promete rutas inexistentes |
| S4 | Cerrar la deuda de nombres: `productoId`/`nombre`/`precio` en docs históricos vs `product_id`/`name`/`price` en código | `mod-catalog` | @SOoOnny | ⬜ Pendiente | Grep de nombres antiguos en specs = 0 (o marcados como históricos) |

### M — Medio plazo (1–3 días cada uno)

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| M1 | Detección de duplicados de reclamos y devoluciones: consultar `GET /api/v1/reclamos`/`/devoluciones` y filtrar por pedido + motivo/estado antes de crear; avisar y permitir “registrar igual” con `forzar: true` | `mod-postventa` | @MathiasTL | 🟡 En implementación (D4) | Escenarios “reclamo/solicitud abierta existente” y “previa resuelta” pasan; no se crea duplicado sin confirmación; `409` con código existente |
| M2 | Revalidación de stock al iniciar checkout: invocar `validate_cart` y mapear líneas agotadas/insuficientes a `409 CARRITO_DESACTUALIZADO` con `lineas` | `mod-checkout` + `mod-cart` | @MathiasTL + @SOoOnny | 🟡 En implementación (D3) | Prueba del carrito que cambia entre agregar y pagar; no se crea checkout/pedido con líneas bloqueantes |
| M3 | Guardado opcional de dirección en Seguridad (`guardarDireccion`) sin bloquear el checkout | `mod-checkout` + `mod-shipping` | @SOoOnny + @MathiasTL | 🟡 En implementación (D6) | Escenario “cliente marca guardar” y “Seguridad falla” cubiertos; `avisoDireccion` visible y pedido creado |
| M4 | Aplicar `orden` en la búsqueda con el conjunto `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc` | `mod-catalog` | @SOoOnny | 🟡 En implementación (D7) | Test de cada valor y de `400 VALIDACION`; `_ = orden` desaparece |
| M5 | Completar el catálogo de tools del chat (reclamos, devoluciones, cuenta) o mover esas intenciones a “pendiente” en la spec | `mod-chat` | @Ankarmin | ⬜ Pendiente | La tabla de intenciones de SPEC-05 coincide con `_TOOLS` y `QUICK_ACTIONS` |

### L — Largo plazo (1–2 semanas)

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| L1 | SPEC-04 completo (H-17): `phone_otp_challenge`, código hasheado, `SmsSender` simulado, endpoints de OTP, `CheckoutGuard`, bloqueo de checkout y UI | `mod-auth` + `mod-checkout` | @Ankarmin | 🟡 En implementación (D1) | Los 3 requisitos y los escenarios de SPEC-04 pasan; `CELULAR_NO_VERIFICADO` real; `REQUIRE_PHONE_VERIFICATION` documentado |
| L2 | SPEC-23 completo: `AttachmentStorage`, carga/borrado/URL firmada, EXIF, miniaturas, multimodal, límites y limpieza | `mod-chat` + `shared/` | @MathiasTL + @Ankarmin | 🟡 En implementación (D2) | Los 10 requisitos y sus escenarios pasan; `adjuntoIds` deja de ser 501 |
| L3 | SPEC-24 completo: reacciones, sugerencias/bugs, valoración de compra, notificación interna, límites y tablas | `mod-chat` + `mod-postventa` + `mod-checkout` | @Ankarmin + @MathiasTL | 🟡 En implementación (D5) | CSAT + los 3 mecanismos con endpoints, tablas y pruebas; UI deja de ser estado local |
| L4 | Endurecer el contrato: OpenAPI como fuente, tests de contrato por módulo y validación en CI de los tags | Plataforma | @Ankarmin | ⬜ Pendiente | S2 convertido en gate bloqueante y documentado en `modularizacion.md` |

## 4. Decisiones de producto resueltas (2026-11-21)

Las siete decisiones quedaron cerradas por el dueño. Se conservan los IDs de la auditoría original para
trazabilidad.

| ID | Pregunta original | Decisión | Impacto |
|---|---|---|---|
| **D1** | ¿Se implementa SPEC-04/H-17 o se retira la verificación local del celular? | **Implementación completa:** OTP de 6 dígitos, TTL 5 min, 3 intentos, 3 reenvíos/15 min, código hasheado, `SmsSender` simulado, `CheckoutGuard` y `REQUIRE_PHONE_VERIFICATION` | SPEC-04; ADR-0026; `phone_otp_challenge` |
| **D2** | ¿SPEC-23 (adjuntos) entra en el alcance? | **Alcance completo:** storage privado, límites, EXIF, miniaturas, URL firmada, limpieza y `adjuntoIds` | SPEC-23; ADR-0028 |
| **D3** | ¿La revalidación de stock es del chatbot o de Ventas? | **El checkout revalida con `validate_cart`** y responde `409 CARRITO_DESACTUALIZADO` con detalle por línea; Ventas sigue como segunda barrera | SPEC-10; `POST /checkout` |
| **D4** | ¿La detección de duplicados se hace en el chatbot o en Ventas? | **El chatbot la hace** contra el listado `/me`; `409` con código existente y `forzar: true` para registrar igual | SPEC-19 y SPEC-21; ADR-0027 |
| **D5** | ¿SPEC-24 completo o solo CSAT? | **Completo:** reacciones, sugerencias/bugs con adjunto, CSAT y notificación interna; valoración de compra en `purchase_rating` | SPEC-24; ADR-0029 |
| **D6** | ¿Se guarda la dirección en Seguridad desde el checkout? | **Sí, opcional** (`guardarDireccion`); si Seguridad falla, no bloquea y se informa con `avisoDireccion` | SPEC-12; `POST /checkout` |
| **D7** | ¿`orden` de búsqueda se implementa o se retira? | **Se implementa** con `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc`; `400 VALIDACION` fuera del conjunto | SPEC-06; `GET /catalogo/productos` |

## 5. Cambios de código en implementación

Todos están **en implementación**; ninguno se marca implementado hasta el merge. La columna de evidencia distingue lo que ya existe en la rama de lo que sigue pendiente.

| Spec | Cambio exigido | Evidencia y hueco restante | Estado |
|---|---|---|---|
| SPEC-04 (H-17) | `POST /contacto/celular/solicitar-otp`, `POST /contacto/celular/verificar-otp`, `phone_otp_challenge` con HMAC, intentos y reenvíos, `SmsSender`/`SimulatedSmsSender`, `CheckoutGuard` real y `REQUIRE_PHONE_VERIFICATION` | `BE/src/modules/mod_auth/adapters/http/phone_router.py:81,92`; `BE/src/modules/mod_auth/application/manage_phone_verification_use_case.py`; `BE/src/shared/infrastructure/db/models/phone_otp_challenge.py`; `FE/src/modules/mod-auth/adapters/authApi.ts:83,87`. Pendiente: `checkout_guard.py` sigue siendo un shim y el checkout solo valida si llega `contacto.celular`; faltan pruebas de los escenarios y merge | 🟡 D1 |
| SPEC-10 | `validate_cart` invocado desde `POST /checkout`, con `lineas` y `503` si no puede validar | `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:264` invoca `_revalidate_stock` y `module.py:108` cablea `cart_validator`; `BE/src/modules/mod_cart/application/manage_cart_use_case.py:249` existe. Pendiente: pruebas de contrato del `409` y verificación de que no se crea checkout/pedido | 🟡 D3 |
| SPEC-12 | `guardarDireccion` propagado al caso de uso y `GuardarDireccionOpcional`; fallo de Seguridad no bloqueante con `avisoDireccion` | `CreateCheckoutRequest.guardarDireccion` existe en `commerce_contracts_dto.py:319` y `_save_address` en `manage_checkout_use_case.py:480`; `checkout_router.py:112-118` **no** pasa `guardarDireccion` a `CreateCheckoutInput`. Pendiente: cablear el router y probar el fallo no bloqueante | 🟡 D6 |
| SPEC-19 | Detección de reclamo abierto por pedido + motivo antes de crear, `409 RECLAMO_DUPLICADO` y `forzar` | `BE/src/modules/mod_postventa/application/postventa_service.py:194-202` y `:280-303` ya detectan duplicados. Pendiente: pruebas de duplicado/forzar/idempotencia y merge | 🟡 D4 |
| SPEC-21 | Detección de devolución abierta por pedido + motivo + líneas antes de crear, `409 DEVOLUCION_DUPLICADA` y `forzar` | `BE/src/modules/mod_postventa/application/postventa_service.py:94-104` y `:305-338` ya detectan duplicados. Pendiente: pruebas de duplicado/forzar/evidencia/idempotencia y merge | 🟡 D4 |
| SPEC-23 | Endpoints de adjuntos, `AttachmentStorage`, miniaturas, URLs firmadas, limpieza y multimodal; `adjuntoIds` deja de ser 501 | `BE/src/modules/mod_chat/adapters/http/attachment_router.py:51,80,113`; `attachment_service.py`; `chatbot_router.py:183-213` ya acepta `adjuntoIds`. Pendiente: job de limpieza, pruebas de seguridad y merge | 🟡 D2 |
| SPEC-24 | `POST /mensajes/{id}/reaccion`, `POST /pedidos/{id}/valoracion-compra`, `POST /sugerencias`, tablas `message_reaction`/`feedback_suggestion`/`purchase_rating`, `order_ref.csat_sent` y outbox interno | `BE/src/modules/mod_postventa/adapters/http/csat_router.py:29` es el único endpoint; no hay servicios; `FE/src/modules/mod-chat/ui/BotFeedback.tsx`, `FE/src/modules/mod-chat/ui/SugerenciaForm.tsx` y `FE/src/modules/mod-checkout/ui/RatingPopup.tsx` no llaman al backend | 🟡 D5 |
| SPEC-06 | Aplicar `orden` con el conjunto cerrado y `400 VALIDACION` | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:87` (`_ = orden`) y el esquema de tools usa `PRECIO_ASC`/`RELEVANCIA`; pendiente alinear al enum del contrato y aplicar el orden | 🟡 D7 |
| SPEC-05 | Tools de reclamos, devoluciones y cuenta; `verificar_celular`; `nueva_conversacion`/`buscar_conversaciones` | `BE/src/modules/mod_catalog/application/tools.py:153-179` solo registra catálogo, carrito, pedidos y `solicitar_registro`; `QUICK_ACTIONS` no los incluye | ⬜ Pendiente (M5) |

## 6. Seguimiento para cerrar 24/24

**Criterio de cierre común:** el código está mergeado en `development`, la spec y el `design.md`
describen el comportamiento real, `docs/openapi.json` y el manifiesto del frontend coinciden, los
escenarios de la spec tienen prueba y el CI está en verde. Solo entonces la fila pasa a ✅.

| Spec | Decisión | Entregables de código | Criterio de cierre específico | Evidencia de cierre |
|---|---|---|---|---|
| SPEC-04 `validacion-celular` | D1 | `phone_otp_challenge`, endpoints OTP, `SmsSender`, `CheckoutGuard`, flag, UI del bloque OTP | Los 3 requisitos y sus escenarios pasan; `403 CELULAR_NO_VERIFICADO` real; un nuevo envío invalida el anterior; el flag desactivado no bloquea | PR de `mod-auth` + `mod-checkout`; tests de OTP; `openapi.json` con ambos endpoints; `api-rutas-contrato.test.ts` sin rutas ausentes |
| SPEC-06 `busqueda-filtrado` | D7 | Validación del enum, mapeo a Productos y orden por precio en el BFF | Cada uno de los 5 valores tiene prueba; `400 VALIDACION` para un valor inválido; `_ = orden` ya no existe | PR de `mod-catalog`; tests de orden; manifiesto con el parámetro |
| SPEC-10 `validacion-stock` | D3 | `POST /checkout` invoca `validate_cart`; `lineas`; `503` fail-closed | Prueba de carrito que cambia entre agregar y pagar; no se crea checkout/pedido con líneas bloqueantes; no se exponen cantidades | PR de `mod-checkout` + `mod-cart`; test de integración del 409; OpenAPI actualizado |
| SPEC-12 `direccion-cotizacion-envio` | D6 | `guardarDireccion` propagado; `GuardarDireccionOpcional`; `avisoDireccion` | Escenario “cliente marca guardar” y “Seguridad falla” cubiertos; el pedido se crea igual; sin llamada si es `false` | PR de `mod-checkout` + `mod-shipping`; test del fallo no bloqueante; OpenAPI actualizado |
| SPEC-19 `creacion-reclamo` | D4 | Detección autoritativa, `409 RECLAMO_DUPLICADO`, `forzar` | Duplicado abierto bloquea sin `forzar`; con `forzar` crea; clave repetida no duplica; listado caído no impide reclamar | PR de `mod-postventa`; tests de duplicado/forzar/idempotencia; OpenAPI actualizado |
| SPEC-21 `solicitud-devolucion-cambio` | D4 | Detección autoritativa, `409 DEVOLUCION_DUPLICADA`, `forzar` | Estados abiertos/cerrados correctos; `forzar` crea; clave repetida no duplica; evidencia e idempotencia intactas | PR de `mod-postventa`; tests de duplicado/forzar/evidencia; OpenAPI actualizado |
| SPEC-23 `adjuntos-imagenes-chat` | D2 | `AttachmentStorage`, carga/borrado/URL firmada, EXIF/miniaturas, `adjuntoIds`, limpieza | Los 10 requisitos pasan; `adjuntoIds` responde SSE, no 501; pertenencia y URLs firmadas probadas; sin URLs/base64 en logs | PR de `mod-chat` + `shared/`; tests de storage y seguridad; OpenAPI actualizado |
| SPEC-24 `retroalimentacion-cliente` | D5 | Reacciones, sugerencias/bugs con captura, CSAT, valoración y outbox interno | Los 4 mecanismos tienen endpoint y tabla; la UI deja de ser estado local; CSAT 409 marca `csat_sent`; un fallo de correo no pierde la sugerencia | PR de `mod-chat` + `mod-postventa` + `mod-checkout`; tests de reacción/sugerencia/CSAT/valoración; OpenAPI actualizado |

**Para marcar 24/24:** faltan las 8 filas 🟡 de esta tabla y promover a ✅ las 5 specs ⚠️ (1, 5, 9, 20,
22) cuando el código mergeado confirme que las correcciones mecánicas siguen vigentes. Las 11 ✅ no
requieren trabajo. El orden sugerido es L1 (SPEC-04) → L2 (SPEC-23) → L3 (SPEC-24) → M1 (SPEC-19/21) →
M2/M3/M4 (SPEC-10/12/06), porque L1–L3 desbloquean los gates de contrato y las pruebas E2E.

## 7. Notas de método y límites

- **No se tocó código de backend ni frontend en esta actualización.** Las decisiones se documentaron
  en specs, ADR y auditoría; el código vive en las ramas paralelas `feat/pendientes-backend` y
  `feat/pendientes-frontend`.
- **No se inventaron decisiones.** Lo que faltaba se marcó como **supuesto explícito** en la spec o en
  el ADR: nombres de campos (`lineas`, `phone_otp_challenge`), valor por defecto del flag,
  fail-open de duplicados y multipart de sugerencias.
- **Los tests no se ejecutaron** en esta auditoría: el estado “1214 backend / 663 frontend” es el
  reportado por el equipo en `development`. La evidencia es estática (código, OpenAPI, manifiestos).
- **Validación OpenSpec:** `npx @fission-ai/openspec validate --specs` pasa las 24 specs con avisos de
  Gherkin en español. `--strict` falla en las 24 porque exige `WHEN`/`THEN` en inglés; no es un fallo
  introducido por esta auditoría.
- **Cobertura de la evidencia:** las rutas `archivo:línea` apuntan al punto que prueba la afirmación;
  cuando el hueco es una ausencia (p. ej. un endpoint que no existe), se cita el archivo que debería
  contenerlo o el adapter que lo llama.
- **Mantenimiento:** al cerrar cada punto del plan, actualizar esta tabla y el estado de la spec en el
  mismo PR, según [`docs/flujo-de-trabajo.md`](flujo-de-trabajo.md). No se marca ✅ sin código mergeado.
