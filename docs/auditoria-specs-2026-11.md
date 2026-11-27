# Auditoría de specs contra el código — noviembre 2026

> **Alcance:** 24 capabilities de `openspec/specs/` contra `G3-Chatbot-backend` (`development` en
> `b75fbea6`, 1308 tests) y `G3-Chatbot-frontend` (`development` en `7432d463`, 744 tests), en el estado
> del 2026-11-21.
> **Método:** lectura de cada `spec.md` y `design.md`, contraste con routers, DTOs, casos de uso,
> estados, errores, manifiestos y llamadas del frontend; `docs/openapi.json` como vista canónica.
> **Regla:** la spec manda sobre el código. Si el código no la cumple, se registra como cambio
> pendiente; si la spec describe algo distinto de lo implementado, se corrige solo el drift mecánico
> (rutas, nombres, campos, estados) y se marca la decisión cuando cambia comportamiento.

## 1. Cierre 24/24 (2026-11-21)

| Estado | Significado | Cantidad |
|---|---|---|
| ✅ Al día | La spec describe el comportamiento y los contratos que el código implementa hoy | **23** |
| ⚠️ Drift mecánico corregido | Nombres, rutas, campos o estados desalineados; corregidos sin cambiar comportamiento | **0** |
| 🟡 En implementación | Decisión de producto cerrada y contrato escrito; falta configuración de despliegue | **1** (SPEC-23, almacenamiento de producción) |
| **Total** | | **24** |

> **Corrección 2026-11-21 (auditoría posterior).** El cierre 24/24 "Al día" sobrestimaba SPEC-23: el backend desplegado solo tiene el adaptador de disco local y el de Supabase está en `development` (backend #144 · `e4faadf`) pero no en `main`, mientras la configuración de producción conserva `ATTACHMENT_STORAGE=local` (ADR-0028). La fila 23 y L2 pasan a 🟡. Además, los cambios `alinear-specs-con-prototipo` y `alinear-specs-con-ventas` se archivaron el mismo día: las specs base pasan a **119 requisitos y 416 escenarios** (antes 116 y 389), y ya no quedan cambios pendientes en `openspec/changes/`. **Cifras históricas de esa fecha;** los totales vigentes están en el README y en `docs/producto/trazabilidad.md`. Los hallazgos de la auditoría posterior (SPEC-AUD-01 a 34) se tratan fuera de esta tabla.

**Evidencia de merge:**

- Backend **#141**, mergeado el **2026-11-21T08:50:54Z**; `development` en **`b75fbea6`**, CI verde con
  **1308 tests**.
- Frontend **#109**, mergeado el **2026-11-21T09:38:50Z**; `development` en **`7432d463`**, **744 tests**.
- Specs **#34** mergeado: las 8 specs pendientes, las 5 correcciones mecánicas y los 4 ADR ya están en
  `main`.

**Incidencia de Sonar (no fue un fallo de código).** Los proyectos de Sonar eran privados y el trial
estaba vencido, así que el análisis no podía ejecutarse. Se cambió la visibilidad de los proyectos a
pública; tras ese ajuste el análisis quedó en `success`. No hubo un defecto de código detrás del fallo.

Las 8 specs que estaban en 🟡 (`validacion-celular`, `validacion-stock`, `creacion-reclamo`,
`solicitud-devolucion-cambio`, `adjuntos-imagenes-chat`, `retroalimentacion-cliente`,
`busqueda-filtrado` y `direccion-cotizacion-envio`) pasan a ✅ con el merge de #141/#109. Las 5 que
figuraban como ⚠️ (`registro-cliente`, `motor-conversacion`, `tarjetas-detalle-producto`,
`consulta-reclamo` y `consulta-devolucion-reembolso`) también pasan a ✅ porque su código está en
`development` y la spec quedó alineada.

## 2. Tabla de las 24 specs

Leyenda de evidencia: `BE` = `G3-Chatbot-backend`, `FE` = `G3-Chatbot-frontend`. Las rutas son relativas
a cada repositorio y todas las rutas backend llevan el prefijo `/api/v1`.

> **Actualización 2026-11-26:** las filas 3 (`inicio-sesion`) y 17 (`consulta-estado-pedido`) pasan a 🟡.
> El login no invoca `merge_cart_lines` (Req. 4, [backend#184](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/184))
> y el detalle de un pedido `ANULADO` no muestra el motivo ni el aviso de reembolso
> ([backend#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182),
> [frontend#143](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/143)). El resto de la tabla
> conserva el estado verificado el 2026-11-21.

| # | Capability | Módulo(s) | Estado | Evidencia (`archivo:línea`) | Acción |
|---|---|---|---|---|---|
| 1 | `registro-cliente` (SPEC-01) | `mod-auth` | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:387` (201); `BE/src/modules/mod_auth/application/manage_session_use_case.py:114-116` (`estado`, `correoEnmascarado`); `BE/src/shared/infrastructure/http/security_client.py:205` (`canalOrigen: CHATBOT`) | Cerrada: spec y código alineados; merge #141/#109 |
| 2 | `verificacion-correo` (SPEC-02) | `mod-auth` | ✅ Al día | `BE/src/modules/mod_auth/adapters/http/session_router.py:466` (204), `:482` (202); `BE/src/shared/infrastructure/http/security_client.py` (`verify_email`, `resend_verification`); `FE/src/modules/mod-auth/ui/VerificarCorreoPage.tsx` | Sin cambios; merge #141/#109 |
| 3 | `inicio-sesion` (SPEC-03) | `mod-auth` (+ `mod-cart`) | ✅ Al día → 🟡 2026-11-26 | `BE/src/modules/mod_auth/adapters/http/session_router.py:237` (login), `:340` (refresh), `:359` (logout), `:374` (perfil); cookies `chat_rt`/`chat_chg`; `FE/src/shared/api/http.ts:62-80` (refresh single-flight) | Req. 4 pendiente: el login no invoca `merge_cart_lines` ([backend#184](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/184)); ver nota 2026-11-26 |
| 4 | `validacion-celular` (SPEC-04 · H-17) | `mod-auth` + `mod-checkout` | ✅ Spec al día (D1 + D2) | `BE/src/modules/mod_auth/adapters/http/phone_router.py:81` (`solicitar-otp`), `:92` (`verificar-otp`); `BE/src/modules/mod_auth/application/manage_phone_verification_use_case.py` (HMAC, TTL, intentos, ventana); `BE/src/shared/infrastructure/db/models/phone_otp_challenge.py`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:147-180` (`CheckoutGuard` real); `FE/src/modules/mod-auth/adapters/authApi.ts:83,87` | Implementado D1: OTP, HMAC, flag `REQUIRE_PHONE_VERIFICATION`, guard y UI; BE #141 · `b75fbea6` / FE #109 · `7432d463`. **D2 de SPEC-04 (2026-11-25):** contacto verificado por correo con celular opcional y `REQUIRE_VERIFIED_CONTACT`; `REQUIRE_PHONE_VERIFICATION` queda como modo legado. |
| 5 | `motor-conversacion` (SPEC-05) | `mod-chat` | ✅ Al día | `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:183-213` (`adjuntoIds` implementado), `:154-166` (acciones directas); `BE/src/modules/mod_chat/application/interpret_and_respond_use_case.py:78-85` (`QUICK_ACTIONS`); `BE/src/modules/mod_catalog/application/tools.py:183-219` (tools, incluida `verificar_celular`) | Corregido el escenario de acciones y cerrado el contrato de `adjuntoIds` con SPEC-23; #141/#109 |
| 6 | `busqueda-filtrado` (SPEC-06) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:80-95` (`orden` con el enum cerrado); `BE/src/modules/mod_catalog/application/tools.py:62`; `BE/src/modules/mod_catalog/domain/product_normalizer.py:15` (`DEFAULT_SYNONYMS`) | Implementado D7: `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc` y `400 VALIDACION`; #141 |
| 7 | `recomendacion` (SPEC-07) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:119` (`recommend`), `:274` (`cross_sell`); `BE/src/modules/mod_catalog/application/tools.py:155`; `BE/src/modules/mod_chat/application/tools/action_dispatcher.py` (`SILENCIAR_COMPLEMENTOS`) | Sin cambios; #141/#109 |
| 8 | `ofertas-promociones` (SPEC-08) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/adapters/http/catalog_router.py:106` (`GET /catalogo/promociones`); `BE/src/modules/mod_catalog/application/tools.py:154`; `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py` (`promotions`, `price_projection`) | Sin cambios; #141/#109 |
| 9 | `tarjetas-detalle-producto` (SPEC-09) | `mod-catalog` | ✅ Al día | `BE/src/modules/mod_catalog/application/manage_catalog_use_case.py:674-687` (`product_id`, `image`, `short_description`, `has_variants`, `single_sku`, `availability`); `FE/src/modules/mod-catalog/domain/entities/CatalogoUI.ts:50-62` | Nombres de `ProductoResumen` alineados; #141/#109 |
| 10 | `validacion-stock` (SPEC-10) | `mod-catalog` + `mod-cart` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_cart/application/manage_cart_use_case.py:249-275` (`validate_cart`); `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:264` (`_revalidate_stock`) y `:470-478` (`409` con `lineas`); `BE/src/modules/mod_checkout/module.py:108` (`cart_validator`) | Implementado D3: revalidación masiva y `409 CARRITO_DESACTUALIZADO` con `lineas`; #141 |
| 11 | `gestion-carrito` (SPEC-11) | `mod-cart` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:96-220`; `BE/src/modules/mod_cart/application/manage_cart_use_case.py` (límites 10/20, `version` optimista); `BE/src/shared/infrastructure/db/models/cart.py` (`version_id_col`) | Sin cambios; #141 |
| 12 | `direccion-cotizacion-envio` (SPEC-12) | `mod-shipping` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_shipping/application/shipping_quote.py:29-34` (`sku` + `cantidad`, sin peso/volumen); `BE/src/modules/mod_checkout/adapters/http/checkout_router.py:124` (`guardarDireccion`); `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:480` (`_save_address`) | Implementado D6: `guardarDireccion`, `avisoDireccion` y fallo de Seguridad no bloqueante; #141/#109 |
| 13 | `cupones` (SPEC-13) | `mod-cart` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_cart/adapters/http/cart_router.py:189` (aplicar), `:220` (quitar); `BE/src/modules/mod_cart/application/manage_cart_use_case.py:151-227` (validación, reemplazo, `CouponAttempts`, 429) | Sin cambios; #141 |
| 14 | `checkout-pago` (SPEC-14) | `mod-checkout` | ✅ Al día | `BE/src/modules/mod_checkout/adapters/http/checkout_router.py:93` (201), `:134`, `:156`; `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py` (15 min, 3 intentos, introspección fail-closed, estados `PENDING_PAYMENT`/`PAYMENT_APPROVED`/`FAILED`/`EXPIRED`) | Sin cambios; consume D1, D3 y D6; #141/#109 |
| 15 | `grabacion-pedido` (SPEC-15) | `mod-checkout` + `mod-orders` | ✅ Al día | `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:290-340` (crea pedido en Ventas y `order_ref`); `BE/src/shared/infrastructure/worker/outbox_worker.py:62-74` (`NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`) | Sin cambios; #141/#109 |
| 16 | `notificacion-confirmacion` (SPEC-16) | `mod-orders` | ✅ Al día | `BE/src/modules/mod_orders/application/notification_service.py:48` (`MAX_RESENDS = 2`), `:156-212`; `BE/src/shared/infrastructure/worker/outbox_worker.py:70` (`SEND_EMAIL`), `:158-165` (backoff) | Sin cambios; #141/#109 |
| 17 | `consulta-estado-pedido` (SPEC-17) | `mod-orders` | ✅ Al día → 🟡 2026-11-26 | `BE/src/modules/mod_orders/adapters/http/orders_router.py:138` (lista), `:160` (detalle), `:178` (seguimiento), `:197` (reenvío 202); `BE/src/modules/mod_orders/application/orders_service.py:45-89` | La anulación no muestra motivo ni reembolso ([backend#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182), [frontend#143](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/143)); ver nota 2026-11-26 |
| 18 | `seguimiento-despacho` (SPEC-18) | `mod-orders` + `mod-shipping` | ✅ Al día | `BE/src/modules/mod_orders/adapters/http/orders_router.py:178`; `BE/src/modules/mod_orders/domain/tracking_mapper.py:22-62` (lista blanca, `recibidoPor` solo frontend); `BE/src/modules/mod_shipping/adapters/despacho_client.py:36` (timeout 4 s), `:62-77` | Sin cambios; #141/#109 |
| 19 | `creacion-reclamo` (SPEC-19) | `mod-postventa` | ✅ Al día | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:46` (201), `:53` (`Idempotency-Key`); `BE/src/modules/mod_postventa/application/postventa_service.py:194-202` (`RECLAMO_DUPLICADO`) y `:280-303` (filtro por pedido + motivo) | Implementado D4: detección autoritativa y `forzar`; BE #141 · `b75fbea6` |
| 20 | `consulta-reclamo` (SPEC-20) | `mod-postventa` | ✅ Al día | `BE/src/modules/mod_postventa/adapters/http/claims_router.py:74` (lista), `:94` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:210-226`; estados G5 `REGISTRADO`/`EN_PROCESO`/`ATENDIDO`/`DERIVADO` | Rutas y estados alineados; #141 |
| 21 | `solicitud-devolucion-cambio` (SPEC-21) | `mod-postventa` | ✅ Al día | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:64` (evidencia 201), `:100` (devolución 201); `BE/src/modules/mod_postventa/application/postventa_service.py:94-104` (`DEVOLUCION_DUPLICADA`) y `:305-338` (pedido + motivo + líneas) | Implementado D4: detección autoritativa y `forzar`; #141 |
| 22 | `consulta-devolucion-reembolso` (SPEC-22) | `mod-postventa` | ✅ Al día | `BE/src/modules/mod_postventa/adapters/http/returns_router.py:126` (lista), `:148` (detalle); `BE/src/modules/mod_postventa/application/postventa_service.py:121-140`; `postventa_dto.py` (`resolucion`, `estadoReembolso`) | Rutas y estados alineados; #141 |
| 23 | `adjuntos-imagenes-chat` (SPEC-23) | `mod-chat` (+ `shared/`) | 🟡 En implementación | `BE/src/modules/mod_chat/adapters/http/attachment_router.py:51` (carga 201), `:80` (borrado 204), `:113` (URL firmada); `BE/src/modules/mod_chat/application/attachment_service.py`; `BE/src/modules/mod_chat/adapters/http/chatbot_router.py:183-213` (`adjuntoIds`); `BE/src/shared/application/ports/attachment_storage_port.py`; `BE/src/shared/infrastructure/storage/supabase_attachment_storage.py` | Implementado D2 con adaptador **local**: límites, EXIF, miniaturas, URL firmada (HMAC), limpieza y `adjuntoIds`; BE #141 / FE #109. El adaptador `SupabaseAttachmentStorage` y el selector `ATTACHMENT_STORAGE=local\|supabase` están en `development` (BE #144 · `e4faadf`). **Pendiente:** bucket privado y variables `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ATTACHMENT_BUCKET`, `ATTACHMENT_PUBLIC_BASE_URL` y `ATTACHMENT_SIGNING_SECRET`; el fail-closed de `local` ya está implementado en backend #198. Producción ejecuta `development` y conserva `local` en su configuración hasta configurar Supabase; el disco local es efímero en Railway, así que no es aceptable (ADR-0028, [runbook](operacion/adjuntos-supabase.md)) |
| 24 | `retroalimentacion-cliente` (SPEC-24) | `mod-postventa` + `mod-chat` + `mod-checkout` | ✅ Al día | `BE/src/modules/mod_chat/adapters/http/feedback_router.py:53` (reacción), `:78` (`/sugerencias`); `BE/src/modules/mod_chat/application/feedback_service.py`; `BE/src/modules/mod_postventa/adapters/http/csat_router.py:29`; `order_ref.csat_sent`; `FE/src/modules/mod-chat/ui/BotFeedback.tsx`, `SugerenciaForm.tsx` y `FE/src/modules/mod-checkout/ui/RatingPopup.tsx` conectados | Implementado D5: reacciones, sugerencias/bugs, CSAT, valoración de compra y outbox interno; #141/#109. El contrato del CSAT es de `mod-postventa`; la UI y el adapter también viven en `mod-postventa` y se inyectan desde `app/pedido/page.tsx` (frontend #153; ver nota del 2026-11-27) |

**Nota operativa (fuera de las 24 capabilities).** El contrato de `/health` cambió con la validación de
capacidades: `discovery.configure_modules` aborta si falta una `REQUIRED_CAPABILITIES` y, si falta una
`OPTIONAL_CAPABILITIES`, registra un `ERROR` y `/health` responde `200` con
`{"status": "degraded", "missingCapabilities": [...]}` en vez de `{"status": "ok"}`. No hay una spec
de operación que cubra `/health`; el comportamiento queda documentado en
[`modularizacion.md`](arquitectura/modularizacion.md#3-dag-de-dependencias). Evidencia:
`BE/src/infrastructure/discovery.py:54-74` y `BE/src/shared/infrastructure/http/health_router.py:10-14`.

## 3. Plan S/M/L

El plan original se conserva para trazabilidad. Los ítems de plataforma o deuda documental que no son
capabilities de las 24 quedan como mejoras posteriores; no bloquean el cierre 24/24. La columna
«Dueño sugerido» conserva el reparto original de tareas; el ownership de módulos sigue siendo del
equipo `@Taller-SW-Web/chatbot`.

### S — Corto plazo

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| S1 | Contrato de `/contacto/celular`: `solicitar-otp`/`verificar-otp` | `mod-auth` (BE/FE) | @Ankarmin | ✅ Cerrado (D1) | No queda ninguna llamada del FE a un endpoint ausente; spec y `docs/openapi.json` coinciden |
| S2 | Gate que compare los `endpoints` de cada `module.manifest.ts` contra `docs/openapi.json` | Plataforma / CI | @Ankarmin | ✅ Cerrado (2026-11-25) | El gate falla si un endpoint del manifiesto no existe o tiene otro tag. Evidencia: `G3-Chatbot-frontend/scripts/check-modules.mjs:262-328` (contrato) y job `modules` del CI, requerido por `check`; FE #108 · `ffabd60` |
| S3 | Revisar los `MODULE.md` de `mod-auth`, `mod-postventa` y `mod-chat` | Docs de módulo | Owner de cada módulo | ✅ Cerrado | `MODULE.md` no promete rutas inexistentes |
| S4 | Cerrar la deuda de nombres históricos de `mod-catalog` | `mod-catalog` | @SOoOnny | ✅ Cerrado (2026-11-26) | Los documentos vigentes usan `ProductsClient`; el nombre `ProductosClient` solo queda en el cambio archivado, marcado como histórico |

### M — Medio plazo

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| M1 | Detección de duplicados de reclamos y devoluciones con `forzar: true` | `mod-postventa` | @MathiasTL | ✅ Cerrado (D4) | Escenarios de duplicado y “previa resuelta” pasan; no se crea duplicado sin confirmación |
| M2 | Revalidación de stock en checkout con `409 CARRITO_DESACTUALIZADO` y `lineas` | `mod-checkout` + `mod-cart` | @MathiasTL + @SOoOnny | ✅ Cerrado (D3) | Prueba del carrito que cambia entre agregar y pagar; no se crea checkout/pedido con líneas bloqueantes |
| M3 | Guardado opcional de dirección con `guardarDireccion` sin bloquear | `mod-checkout` + `mod-shipping` | @SOoOnny + @MathiasTL | ✅ Cerrado (D6) | Escenarios “cliente marca guardar” y “Seguridad falla” cubiertos; `avisoDireccion` visible |
| M4 | Aplicar el enum de `orden` en la búsqueda | `mod-catalog` | @SOoOnny | ✅ Cerrado (D7) | Test de cada valor y de `400 VALIDACION`; `_ = orden` desaparece |
| M5 | Ampliar el catálogo de tools conversacionales | `mod-chat` | @Ankarmin | ⬜ Posterior al cierre | Mejora de cobertura conversacional; no es requisito de las 24 |

### L — Largo plazo

| ID | Acción | Módulo / repo | Dueño sugerido | Estado | Criterio de cierre |
|---|---|---|---|---|---|
| L1 | SPEC-04 completo (H-17): OTP, guard, flag y UI | `mod-auth` + `mod-checkout` | @Ankarmin | ✅ Cerrado (D1); D2 de SPEC-04 documentado (2026-11-25) | Los 3 requisitos y sus escenarios pasan; `CELULAR_NO_VERIFICADO` sigue siendo el error del modo legado y `CONTACTO_NO_VERIFICADO` cubre el modo por defecto. |
| L2 | SPEC-23 completo: storage, EXIF, miniaturas, URLs firmadas, límites y limpieza | `mod-chat` + `shared/` | @SebJoq21 | 🟡 Parcial (D2): adaptador en `development`, falta configuración | Los 10 requisitos y sus escenarios pasan; `adjuntoIds` ya no es 501; falta verificar `ATTACHMENT_STORAGE=supabase` en producción. El checklist operativo está en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27). |
| L3 | SPEC-24 completo: reacciones, sugerencias/bugs, valoración, CSAT y outbox | `mod-chat` + `mod-postventa` + `mod-checkout` | @Ankarmin + @MathiasTL | ✅ Cerrado (D5) | Los mecanismos tienen endpoints, tablas y pruebas; la UI dejó de ser estado local |
| L4 | Endurecer el contrato: OpenAPI como fuente y gate bloqueante | Plataforma | @Ankarmin | ✅ Cerrado (2026-11-25) | S2 convertido en gate bloqueante y documentado en `docs/arquitectura/modularizacion.md` §5 y §9. [BE #165](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/165) agregó `Verify committed OpenAPI is up to date` (`export_openapi.py --check`) al job `openapi`; `--check` pasa (47 paths) y falla sobre una copia alterada. Mergeado y verificado en CI |

> [!note] Actualización 2026-11-27 — CSAT sin excepción de tag
> `mod-postventa` es el dueño canónico del contrato, el backend, el adapter y la UI del CSAT; `mod-orders`
> solo expone el detalle del pedido y `csatEnviado`. El manifiesto de `mod-orders` ya no declara
> `/pedidos/{pedidoId}/csat` y `contractTagExceptions` queda vacío (frontend #153). El gate `modules` no
> tiene excepciones de tag. Cierre: specs #88.

## 4. Decisiones de producto resueltas (2026-11-21)

Las siete decisiones quedaron cerradas por el dueño y se implementaron en #141/#109. Se conservan los
IDs de la auditoría original para trazabilidad.

| ID | Pregunta original | Decisión | Impacto |
|---|---|---|---|
| **D1** | ¿Se implementa SPEC-04/H-17 o se retira la verificación local del celular? | **Implementación completa:** OTP de 6 dígitos, TTL 5 min, 3 intentos, 3 reenvíos/15 min, código hasheado, `SmsSender` simulado, `CheckoutGuard` y `REQUIRE_PHONE_VERIFICATION` | SPEC-04; ADR-0026; `phone_otp_challenge` |
| **D2** | ¿SPEC-23 (adjuntos) entra en el alcance? | **Alcance completo:** storage privado, límites, EXIF, miniaturas, URL firmada, limpieza y `adjuntoIds` | SPEC-23; ADR-0028 |
| **D3** | ¿La revalidación de stock es del chatbot o de Ventas? | **El checkout revalida con `validate_cart`** y responde `409 CARRITO_DESACTUALIZADO` con `lineas`; Ventas sigue como segunda barrera | SPEC-10; `POST /checkout` |
| **D4** | ¿La detección de duplicados se hace en el chatbot o en Ventas? | **El chatbot la hace** contra el listado `/me`; `409` con código existente y `forzar: true` para registrar igual | SPEC-19 y SPEC-21; ADR-0027 |
| **D5** | ¿SPEC-24 completo o solo CSAT? | **Completo:** reacciones, sugerencias/bugs con adjunto, CSAT y notificación interna; valoración de compra en `purchase_rating` | SPEC-24; ADR-0029 |
| **D6** | ¿Se guarda la dirección en Seguridad desde el checkout? | **Sí, opcional** (`guardarDireccion`); si Seguridad falla, no bloquea y se informa con `avisoDireccion` | SPEC-12; `POST /checkout` |
| **D7** | ¿`orden` de búsqueda se implementa o se retira? | **Se implementa** con `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc`; `400 VALIDACION` fuera del conjunto | SPEC-06; `GET /catalogo/productos` |

## 5. Seguimiento y cierre

**Criterio de cierre común:** código mergeado en `development`, spec y `design.md` describen el
comportamiento real, `docs/openapi.json` y el manifiesto del frontend coinciden, los escenarios tienen
prueba y el CI está en verde.

| Spec | Decisión | Estado | Entregables verificados | Evidencia de cierre |
|---|---|---|---|---|
| SPEC-04 `validacion-celular` | D1 | ✅ Cerrado | `phone_otp_challenge`, endpoints OTP, `SmsSender`, `CheckoutGuard`, flag, UI del bloque OTP | BE #141 · `b75fbea6`; FE #109 · `7432d463`; tests de OTP y guard; 1308/744 en CI |
| SPEC-06 `busqueda-filtrado` | D7 | ✅ Cerrado | Enum de `orden`, mapeo a Productos y orden por precio | BE #141 · `b75fbea6`; tests de orden; `400 VALIDACION` |
| SPEC-10 `validacion-stock` | D3 | ✅ Cerrado | `validate_cart` en checkout, `lineas` y `503` fail-closed | BE #141 · `b75fbea6`; tests de carrito cambiado y `409` |
| SPEC-12 `direccion-cotizacion-envio` | D6 | ✅ Cerrado | `guardarDireccion`, `GuardarDireccionOpcional` y `avisoDireccion` | BE #141 · `b75fbea6`; FE #109 · `7432d463`; tests de fallo no bloqueante |
| SPEC-19 `creacion-reclamo` | D4 | ✅ Cerrado | Detección autoritativa, `409 RECLAMO_DUPLICADO` y `forzar` | BE #141 · `b75fbea6`; tests de duplicado/forzar/idempotencia |
| SPEC-21 `solicitud-devolucion-cambio` | D4 | ✅ Cerrado | Detección por pedido + motivo + líneas, `409 DEVOLUCION_DUPLICADA` y `forzar` | BE #141 · `b75fbea6`; tests de duplicado/forzar/evidencia |
| SPEC-23 `adjuntos-imagenes-chat` | D2 | 🟡 Parcial (configuración) | `AttachmentStorage` local y Supabase, carga/borrado/URL firmada, EXIF/miniaturas, `adjuntoIds` y limpieza; faltan bucket y variables | BE #141 · `b75fbea6`; BE #144 · `e4faadf`; FE #109 · `7432d463`; tests de storage y seguridad; [runbook](operacion/adjuntos-supabase.md) |
| SPEC-24 `retroalimentacion-cliente` | D5 | ✅ Cerrado | Reacciones, sugerencias/bugs, CSAT, valoración y outbox interno | BE #141 · `b75fbea6`; FE #109 · `7432d463`; tests de feedback y CSAT |

**Resultado al 2026-11-21:** 23 de 24 capabilities en ✅ y **SPEC-23 en 🟡** hasta la configuración del storage. **Actualizado el 2026-11-26:** 21 ✅, con `inicio-sesion` y `consulta-estado-pedido` en 🟡 (ver notas finales). Las 5 correcciones mecánicas (SPEC-01, SPEC-05, SPEC-09,
SPEC-20 y SPEC-22) se promovieron al verificar el código mergeado. El cierre no depende de S4 ni M5:
son deuda documental y una mejora conversacional fuera de las 24 capabilities. S2 quedó cerrado el
2026-11-25; L4 queda pendiente del merge del gate de drift ([BE #165](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/165)).

## 6. Notas de método y límites

- **Esta actualización es documental.** No se tocó código de backend ni frontend; el merge ya ocurrió
  en #141 (backend) y #109 (frontend).
- **CI y tests:** backend `b75fbea6` con 1308 tests; frontend `7432d463` con 744 tests; CI verde.
- **Sonar:** los proyectos privados tenían el trial vencido; se cambiaron a visibilidad pública y el
  análisis quedó en `success`. No fue un fallo de código.
- **Validación OpenSpec:** `npx @fission-ai/openspec validate --specs` pasa las 24 specs con avisos de
  Gherkin en español. `--strict` falla en las 24 porque exige `WHEN`/`THEN` en inglés; no es un fallo
  introducido por esta auditoría.
- **Cobertura de la evidencia:** las rutas `archivo:línea` apuntan al punto que prueba la afirmación;
  cuando el hueco era una ausencia, se citó el archivo que debería contenerlo o el adapter que lo
  llamaba. La evidencia de cierre combina lectura estática y el CI reportado por el equipo.
- **Mantenimiento:** la próxima auditoría solo es necesaria si cambia un contrato, una capability o el
  DAG; el estado de referencia es este 24/24 con fecha 2026-11-21.

> [!note] Actualización 2026-11-23 — SPEC-19 y SPEC-24 cerradas
> Los PR **#149** (backend, motivos/CSAT) y **#113** (frontend, detalle y CSAT) están mergeados: los
> cinco motivos de reclamo, el CSAT al pie del detalle y los filtros `desde`/`hasta` quedan alineados
> con el contrato real de G5. El único 🟡 sigue siendo **SPEC-23** (storage Supabase) hasta crear el
> bucket privado y activar `ATTACHMENT_STORAGE=supabase` en producción.

> [!note] Actualización 2026-11-25 — el adaptador Supabase está en `development`
> El backend **#144** (`e4faadf`) mergeó `SupabaseAttachmentStorage`, el selector
> `ATTACHMENT_STORAGE=local|supabase` y el listado de objetos para la reconciliación de huérfanos.
> `main` todavía no lo contiene y la configuración de producción conserva `local` sobre un volumen de
> Railway. Para cerrar SPEC-23 faltan el bucket privado y las variables de storage; el fail-closed ya
> está implementado en backend #198 (la promoción a `main` no aplica; ver nota del 2026-11-26); el orden, la verificación y el rollback están en el
> [runbook de adjuntos en Supabase](operacion/adjuntos-supabase.md).

> [!note] Actualización 2026-11-25 — D2 de SPEC-04: contacto verificado por correo
> El owner/líder de producto aprobó que la validación de celular por OTP siga implementada y disponible,
> pero que el checkout use el correo verificado por G7 como contacto por defecto y deje el celular como
> opcional. El guard del modo por defecto pasa a `CONTACTO_NO_VERIFICADO` (defensivo) y se controla con
> `REQUIRE_VERIFIED_CONTACT`; `REQUIRE_PHONE_VERIFICATION` queda como modo legado. El requisito del curso
> se cumple con la capacidad disponible, no con exigirla en cada compra. D1 y su evidencia de
> implementación se conservan como historial; esta nota no reescribe la auditoría del 2026-11-21.

> [!note] Actualización 2026-11-25 — L2 asignada a Sebastian
> El proyecto Supabase `olzsuqpowkndoeljpiax` es de **Sebastian (@SebJoq21)**, que queda como responsable
> de L2: bucket privado, variables de Railway, migración vs pérdida de los archivos locales y verificación
> de carga + reinicio + lectura. El checklist operativo está en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27).
> Mathias conserva la coordinación del deploy y H5-X1 (corregido el 2026-11-26: H5-X1 solo verifica
> producción sobre `development`; `main` es un placeholder y no se promueve).

> [!note] Actualización 2026-11-25 — S2 cerrado; L4 pendiente del gate de drift
> El job `modules` del frontend descarga `docs/openapi.json` de `development`, ejecuta
> `pnpm modules:check` y es requerido por `check` (FE #108 · `ffabd60`). El gate falla ante un endpoint
> del manifiesto ausente o con otro tag; la excepción de tag de CSAT se retiró el 2026-11-27. El
> estado quedó reflejado en
> [modularizacion.md](arquitectura/modularizacion.md#estado-real-del-gate-de-contrato).
> Para cerrar L4, [BE #165](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/165) agrega
> `Verify committed OpenAPI is up to date` (`python scripts/export_openapi.py --check`) al job
> `openapi`; `--check` pasa con 47 paths y falla sobre una copia alterada. L4 queda cerrado pendiente
> de ese merge, no verificado en producción.

> [!note] Actualización 2026-11-26 — `main` placeholder y estado real de los pendientes
> Desde el 2026-11-26, `main` es un **placeholder de un único commit** con solo `README.md` en los tres
> repositorios; `development` es la rama por defecto y la que despliega producción (ADR-0020, enmienda
> del 2026-11-26). Por eso **SPEC-23/L2 ya no está bloqueada por una promoción a `main`**: el adaptador
> de Supabase está en `development` y producción ejecuta esa rama. Sigue 🟡 por el bucket privado y las
> variables de storage; el checklist operativo está en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27); el
> fail-closed de `local` ya está implementado en backend #198. **L4 queda cerrado**:
> BE #165 se mergeó el 2026-11-25 (`f7fd0af`) y el gate de drift corre en CI. **M5** (specs#64) sigue
> abierto; **S4** (backend#188) se cerró el 2026-11-26 al alinear los documentos vigentes a `ProductsClient`.
> Ninguno es requisito de las 24 capabilities. El estado real de las 24 specs es **21 ✅, SPEC-23 🟡,
> `inicio-sesion` 🟡 y `consulta-estado-pedido` 🟡**.

> [!warning] Hallazgo 2026-11-26 — `inicio-sesion` no cumple el Req. 4
> `merge_cart_lines` existe y tiene pruebas unitarias, pero `POST /sesion/login` no la invoca y el estado
> `MERGED` no se usa. La auditoría del 2026-11-21 marcaba `inicio-sesion` como ✅; la fila 3 queda 🟡 hasta
> que el login fusione el carrito anónimo. Seguimiento:
> [backend#184](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/184).

> [!warning] Hallazgo 2026-11-26 — `consulta-estado-pedido` no muestra la anulación completa
> La spec exige "Anulado el {fecha}" con el motivo general y el aviso de reembolso. El backend no expone
> el motivo y la UI solo muestra "Anulado". Seguimiento:
> [backend#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182) y
> [frontend#143](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/143). La fila 17 queda 🟡.
