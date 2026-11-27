# Casos de prueba del Hito 5

> Tarea H5-Q1 de [`odd/tasks/hito-5.md`](../odd/tasks/hito-5.md) (issue [#60](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/60)): matriz de casos por flujo y validación de la Definición de Terminado. Fecha: 2026-11-26.

El Hito 5 no agrega specs nuevas: sus entregables son CI/CD con revisión de seguridad, pruebas de integración, pruebas de performance, API Management y un mecanismo asíncrono. Por eso los casos se organizan por flujo de usuario, para comprobar que lo construido hasta el Hito 4 sigue funcionando con el pipeline, el gateway y el broker nuevos, y por entregable del hito. Los casos por escenario de cada spec siguen en [`casos-prueba-hito-3.md`](casos-prueba-hito-3.md) y [`casos-prueba-hito-4.md`](casos-prueba-hito-4.md).

## Resumen

Estado al 2026-11-26, contra `development` (backend `7443120`, frontend `ecf4794`, specs `1ee214f`).

| Flujo | Casos | Ejecutados | Fallidos | Pendientes | Fuera de alcance |
|---|---|---|---|---|---|
| Catálogo | 6 | 6 | 0 | 0 | 0 |
| Chat | 7 | 5 | 1 | 1 | 0 |
| Sesión | 3 | 3 | 0 | 0 | 0 |
| Carrito | 3 | 2 | 1 | 0 | 0 |
| Checkout | 5 | 5 | 0 | 0 | 0 |
| Pago | 4 | 4 | 0 | 0 | 0 |
| Pedidos | 5 | 3 | 0 | 2 | 0 |
| Postventa | 4 | 4 | 0 | 0 | 0 |
| Administración | 1 | 0 | 0 | 0 | 1 |
| Entregables del hito | 10 | 6 | 0 | 4 | 0 |
| **Total** | **48** | **38** | **2** | **6** | **1** |

Los dos casos fallidos son del E2E nocturno contra el LLM real (CP-H5-CHAT-02 y CP-H5-CART-01). Los pendientes dependen de tareas abiertas: contratos (backend [#174](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/174)), evals (backend [#175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175)), Lighthouse (frontend [#144](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/144)), E2E de pedidos y reclamos (specs [#64](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/64)) y anulación con reembolso (backend [#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182)).

## Cómo leer las tablas

- **Tipo:** cómo se ejecuta el caso.
  - **E2E:** Playwright en el navegador. El job `E2E` del CI del frontend levanta Next.js, el backend y PostgreSQL con los módulos externos en `fake` y sin LLM. Los casos con LLM real están en `chat.real.spec.ts` y corren cada noche en `e2e-real.yml`.
  - **API:** pytest del backend, unitario o de integración contra PostgreSQL, RabbitMQ o Kong levantados en el CI. Cuando el caso tiene interfaz, se cita también la prueba de Vitest del frontend.
  - **Manual:** recorrido en producción, registrado en un documento de evidencia.
- **Evidencia:** archivo de prueba y ejecución que lo corrió. Las ejecuciones de referencia son:
  - **CI backend:** [run 45925594126](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45925594126), commit `7443120`, todos los jobs en verde.
  - **CI frontend:** [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), commit `ecf4794`, todos los jobs en verde, incluido `E2E`.
  - **E2E nocturno con LLM real:** [run 45879581445](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45879581445), 2026-11-26, falló.
  - **Performance con broker:** [run 45887721116](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45887721116), PASS.
  - **Producción:** [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md) (pago del 2026-11-27 UTC) y [Verify production 45925804684](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925804684) del frontend.
- **Estado:** ✅ ejecutado y aprobado · ❌ ejecutado y fallido (con seguimiento) · ⏳ pendiente (con la tarea que lo cierra) · ➖ fuera de alcance (con la razón).

Las rutas `tests/...` sin repositorio son del backend si terminan en `.py` y del frontend si terminan en `.ts` o `.tsx`.

## Catálogo

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-CAT-01 | Pantalla de inicio | Productos responde | Abrir `/` | Se ven el banner, las ofertas destacadas y el campo de conversación | E2E | `tests/e2e/smoke.spec.ts` (E2E-01) y `tests/e2e/home.spec.ts`; CI frontend | ✅ |
| CP-H5-CAT-02 | Búsqueda con filtros | Catálogo de Productos con datos | Buscar por texto y aplicar filtros de categoría y precio | Se listan solo productos que cumplen los filtros, en el orden pedido | API | `tests/unit/mod_catalog/test_catalog_search.py`, `test_catalog_ordering.py` y `tests/integration/mod_catalog/test_discovery_regressions_postgres.py`; CI backend | ✅ |
| CP-H5-CAT-03 | Detalle con variantes, precio y disponibilidad | Producto con variantes | Abrir el detalle de un producto | Se muestran las variantes, el precio por SKU y el badge de disponibilidad sin cantidades exactas | API | `tests/unit/mod_catalog/test_product_detail.py`, `test_stock_validation.py` y `tests/unit/.../tarjetas-disponibilidad-precio.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-CAT-04 | Ofertas: error distinto de vacío | Productos falla o devuelve una lista vacía | Abrir `/` | Un error muestra el aviso con "Reintentar"; una lista vacía muestra el estado vacío | E2E | `tests/e2e/offers-recommendations.fixture.spec.ts`; CI frontend | ✅ |
| CP-H5-CAT-05 | Productos no disponible | Productos no responde a tiempo | Buscar o abrir un detalle | La operación se rechaza de forma controlada, sin inventar precio ni disponibilidad | API | `tests/unit/mod_catalog/test_catalog_partial.py` y `tests/unit/mod_chat/test_degraded_mode.py`; CI backend | ✅ |
| CP-H5-CAT-06 | Recorrido mobile-first | Viewports de móvil y escritorio | Inicio → detalle → chat → carrito, con gestos táctiles y teclado virtual | El recorrido termina en todos los viewports y el compositor sigue visible | E2E | `tests/e2e/mobile-first.spec.ts`; CI frontend | ✅ |

## Chat

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-CHAT-01 | Respuesta en streaming con LLM real | Backend con el proveedor de LLM real | Escribir un mensaje desde el inicio | La respuesta del asistente llega por SSE y se pinta mientras se genera | E2E | `tests/e2e/chat.real.spec.ts` (E2E-03); E2E nocturno 45879581445 | ✅ |
| CP-H5-CHAT-02 | Búsqueda en el chat con LLM real | Backend con el proveedor de LLM real | Pedir un producto en el chat y abrir una tarjeta | Se muestran el carrusel y el detalle del producto | E2E | `tests/e2e/chat.real.spec.ts` (E2E-06); E2E nocturno 45879581445: el carrusel no aparece en 30 s, igual que el 24 y el 25/11 | ❌ Ver [Seguimiento](#seguimiento) |
| CP-H5-CHAT-03 | Barra lateral de conversaciones | Cliente con conversaciones | Listar, buscar y crear una conversación | La lista, la búsqueda y la creación responden contra el backend | E2E | `tests/e2e/smoke.spec.ts` (E2E-02); CI frontend | ✅ |
| CP-H5-CHAT-04 | Datos sensibles fuera del LLM | Mensaje con datos de tarjeta o documento | Enviar el mensaje | El filtro redacta los datos antes de enviarlos al LLM | API | `tests/unit/mod_chat/test_container_sensitive_data_filter.py`; CI backend | ✅ |
| CP-H5-CHAT-05 | Sin precios inventados ni respuestas fuera de dominio | LLM real con módulos fake | Conversaciones de referencia por spec (H5-E1) | Las herramientas llamadas y los datos devueltos coinciden con lo esperado; ningún precio sale de fuera de las herramientas | API (eval) | Sin ejecución: `tests/evals/` solo tiene `.gitkeep` | ⏳ H5-E1, backend [#175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175) |
| CP-H5-CHAT-06 | Adjunto de imagen | Cliente con sesión | Adjuntar una imagen al mensaje | La imagen se guarda, queda asociada al mensaje y se muestra en el historial | API | `tests/integration/mod_chat/test_conversation_attachment_persistence.py` y `tests/unit/.../chatPage-adjuntos.test.tsx`; CI backend y frontend. Límite: en producción los adjuntos viven en un volumen de Railway (SPEC-23 🟡, specs [#53](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/53)) | ✅ |
| CP-H5-CHAT-07 | Acciones del cliente desde el chat (M5) | Bloque con `IR_A_CHECKOUT` o `CERRAR_SESION` | Pulsar la acción | El frontend la ejecuta una sola vez por turno y no la reenvía al BFF | API | `tests/unit/mod_chat/test_m5_catalog_actions.py` y `tests/unit/.../chatPage-actions.test.tsx`; CI backend y frontend. La prueba de contrato de la tarea 4.4 de M5 sigue pendiente (specs [#64](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/64)) | ✅ |

## Sesión

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-SES-01 | Registro | Visitante sin cuenta, Seguridad en `fake` | Registrarse con datos válidos | La cuenta queda pendiente de verificar el correo | E2E | `tests/e2e/smoke.spec.ts` (E2E-04); CI frontend | ✅ |
| CP-H5-SES-02 | Inicio y cierre de sesión | Cliente registrado, Seguridad en `fake` | Iniciar sesión y cerrarla | La sesión se abre y se cierra, y se limpia el estado del chat | E2E | `tests/e2e/smoke.spec.ts` (E2E-05); CI frontend | ✅ |
| CP-H5-SES-03 | Verificación del celular por OTP | Cliente sin celular verificado | Pedir el OTP e ingresarlo | El celular queda verificado; un OTP incorrecto o vencido se rechaza | API | `tests/unit/mod_auth/test_phone_verification.py` y `tests/unit/.../otpCelularFlow.test.tsx`; CI backend y frontend | ✅ |

Contra Seguridad G7 real, E2E-04 y E2E-05 no se automatizan: necesitan correos reales y MFA (ver [`casos-prueba-hito-4.md`](casos-prueba-hito-4.md)).

## Carrito

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-CART-01 | Agregar desde la tarjeta del chat con LLM real | Backend con el proveedor de LLM real | Buscar en el chat y pulsar "Agregar" en una tarjeta | El producto aparece en el carrito | E2E | `tests/e2e/chat.real.spec.ts` (E2E-07); E2E nocturno 45879581445: falla porque antes no aparece el carrusel (CP-H5-CHAT-02) | ❌ Ver [Seguimiento](#seguimiento) |
| CP-H5-CART-02 | Agregar y cambiar cantidades con validación de stock | Producto con disponibilidad conocida | Agregar un producto y subir la cantidad | La operación se acepta si hay stock y se rechaza con `409` si no lo hay | API | `tests/unit/mod_cart/test_cart_management.py`, `tests/unit/mod_catalog/test_stock_validation.py` y `tests/unit/.../cartPage.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-CART-03 | Cupón válido e inválido | Carrito con productos | Aplicar un cupón válido, uno inválido, reemplazarlo y quitarlo | El válido recalcula el total, el inválido se rechaza con motivo, reemplazar pide confirmación y quitar recalcula sin descuento | API | `tests/unit/mod_cart/test_coupon_use_case.py` y `tests/unit/.../cartDiscounts.test.tsx`; CI backend y frontend | ✅ |

## Checkout

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-CHK-01 | Dirección y cotización de envío | Cliente con carrito | Ingresar o elegir la dirección | Despacho cotiza el envío y el total lo incluye | API | `tests/unit/mod_shipping/test_shipping_use_case.py`, `tests/unit/mod_checkout/test_checkout_saved_address.py`, `tests/unit/.../direccionForm.test.tsx` y `cotizacion-envio.test.ts`; CI backend y frontend | ✅ |
| CP-H5-CHK-02 | Revalidación de stock al iniciar | El stock bajó después de agregar al carrito | Iniciar el checkout | Se bloquea con el detalle por línea | API | `tests/unit/mod_checkout/test_checkout_stock_revalidation.py`; CI backend | ✅ |
| CP-H5-CHK-03 | Contacto verificado obligatorio | Cliente sin correo de perfil ni celular verificado | Iniciar el checkout | Se bloquea; con el correo de perfil o el celular verificado continúa | API | `tests/unit/mod_checkout/test_verified_contact_guard.py`; CI backend | ✅ |
| CP-H5-CHK-04 | Ventas no responde a tiempo | Ventas excede el timeout | Confirmar el checkout y reintentar | El checkout queda recuperable; reintentar con la misma `Idempotency-Key` o con otra no duplica el pedido | API | `tests/unit/mod_checkout/test_checkout_sales_timeout.py`; CI backend | ✅ |
| CP-H5-CHK-05 | Checkout de punta a punta en producción | Cliente autenticado en la web de producción | Checkout y pago desde la web | `POST /checkout` 201 y `POST /pago` 200; pedido `PED-2026-00094` por S/ 189.90 | Manual | [`evidencia-mecanismo-asincrono.md` §3.1](evidencia-mecanismo-asincrono.md#31-pago-de-punta-a-punta-2026-11-27) (2026-11-27 UTC). Límite: Ventas G5 en frío puede responder 503 (el 26/11 entre 21:18 y 21:24) | ✅ |

## Pago

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-PAY-01 | Sin doble cobro | Checkout con un pago aprobado | Registrar un segundo intento aprobado | Se rechaza por conflicto; el contador de intentos es atómico y llega como máximo a 3 | API | `tests/integration/mod_checkout/test_payment_concurrency_postgres.py`; CI backend (job `Migrations and integration tests`) | ✅ |
| CP-H5-PAY-02 | Datos de tarjeta no persistidos | Pago con tarjeta | Registrar el intento de pago | La tabla de intentos no tiene columnas de PAN, CVV ni vencimiento, y solo admite inserciones | API | `tests/unit/mod_checkout/test_payment_attempt_adapter.py`; CI backend | ✅ |
| CP-H5-PAY-03 | Pago publicado en RabbitMQ y consumido aparte | RabbitMQ en Docker (CI) o CloudAMQP (producción) | Aprobar un pago | El relay publica `NOTIFY_SALES_PAYMENT` y el consumidor, en otro proceso, lo procesa; el `message_id` es el `id` de la fila del outbox | API y manual | `tests/integration/test_rabbitmq_outbox_publisher.py` y `test_outbox_consumer_rabbitmq.py` (CI backend); producción en [`evidencia-mecanismo-asincrono.md` §3.1](evidencia-mecanismo-asincrono.md#31-pago-de-punta-a-punta-2026-11-27) | ✅ |
| CP-H5-PAY-04 | Pago con el broker caído | Broker detenido | Aprobar un pago, esperar y volver a levantar el broker | La fila queda `PENDING`, se reprograma sin gastar intentos y pasa a `PROCESSED` al volver el broker, sin pérdidas ni duplicados | Manual | [`evidencia-mecanismo-asincrono.md` §5](evidencia-mecanismo-asincrono.md#5-prueba-con-el-broker-caído) (Docker local). Límite: el consumidor no volvía a consumir tras el reinicio; la corrección está en backend [#215](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/215), abierto | ✅ |

## Pedidos

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-ORD-01 | Confirmación por correo y reenvío | Pedido grabado | Ver la confirmación y pulsar "Reenviar correo" | Se encola `SEND_EMAIL`, el correo se muestra enmascarado y se permiten como máximo 2 reenvíos | API | `tests/unit/mod_orders/test_notification_service.py`, `tests/integration/mod_orders/test_notification_orders_postgres.py` y `tests/unit/.../confirmacionPedido.test.tsx`; CI backend y frontend. Límite: producción no tiene SMTP y usa `FakeEmailSender`, así que no se entrega ningún correo real | ✅ |
| CP-H5-ORD-02 | Historial de pedidos | Cliente con pedidos en Ventas G5 | Abrir "Mis pedidos" | Se listan sus pedidos con fecha, total y estado | API | `tests/unit/mod_orders/test_orders_g5_projection.py`, `test_ventas_client_filters.py` y `tests/unit/.../orderHistoryPage.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-ORD-03 | Estado y seguimiento desde el chat | Pedido despachado | Preguntar por el pedido en el chat y abrir el seguimiento | El chat muestra `ESTADO_PEDIDO` con los hitos y el seguimiento de Despacho | API | `tests/unit/mod_orders/test_order_status_chat.py`, `test_m5_order_tracking.py` y `tests/unit/.../seguimientoPage.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-ORD-04 | Recorrido de pedidos y reclamos en el chat | Cliente con pedidos y reclamos | "mis pedidos" → elegir uno → "¿ya viene?" → "mis reclamos" → abrir uno → enviar un reclamo | Lista, estado, seguimiento, lista de reclamos, estado y constancia | E2E | Sin prueba: tarea 4.3 del cambio M5 | ⏳ specs [#64](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/64) |
| CP-H5-ORD-05 | Anulación con reembolso | Pedido anulable y pagado | Anular el pedido | Se solicita la cancelación a Ventas y se informa el reembolso | API | `consulta-estado-pedido` sigue 🟡 por la anulación con reembolso | ⏳ backend [#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182), frontend [#143](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/143) |

## Postventa

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-POST-01 | Reclamo sin duplicados | Pedido entregado | Registrar un reclamo y repetirlo con el mismo pedido y motivo | Se emite la constancia; el duplicado abierto responde `409` con el código existente, salvo que se fuerce; un reclamo cerrado no cuenta | API | `tests/unit/mod_postventa/test_postventa_service.py`, `test_postventa_duplicates.py` y `tests/unit/.../reclamoForm.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-POST-02 | Solicitud de devolución con evidencia | Pedido entregado | Solicitar la devolución con fotos | Se registra con su evidencia y constancia; la repetición abierta responde `409` | API | `tests/unit/mod_postventa/test_evidence_adapter.py`, `test_return_ref_adapter.py`, `test_postventa_duplicates.py` y `tests/unit/.../devolucionForm.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-POST-03 | Consulta de reclamos y devoluciones | Cliente con reclamos o devoluciones | Abrir el estado desde la página o el chat | Se muestran el estado, la respuesta visible al cliente y la resolución sin reformular | API | `tests/unit/mod_postventa/test_postventa_routers.py`, `tests/unit/mod_chat/test_m5_postventa_tools.py`, `tests/unit/.../reclamoPage.test.tsx` y `devolucionPage.test.tsx`; CI backend y frontend | ✅ |
| CP-H5-POST-04 | Retroalimentación y CSAT | Pedido completado o turno del bot | Calificar la compra o el mensaje y dejar un comentario | Se guarda la calificación y se encola el correo de seguimiento | API | `tests/unit/mod_postventa/test_csat_sent.py`, `tests/unit/mod_chat/test_feedback_service.py`, `tests/unit/.../botFeedback.test.tsx` y `ratingPopup.test.tsx`; CI backend y frontend | ✅ |

## Administración

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-ADM-01 | Panel de administración | — | — | — | — | [`alcance.md`](producto/alcance.md#5-fuera-de-alcance-consolidado) deja fuera del canal el registro de administradores (SPEC-01) y el panel de revisión de sugerencias y valoraciones (SPEC-24); ninguna spec define una pantalla de administración | ➖ |

## Entregables del Hito 5

| ID | Caso | Precondición | Pasos | Resultado esperado | Tipo | Evidencia | Estado |
|---|---|---|---|---|---|---|---|
| CP-H5-ENT-01 | Auditoría de dependencias bloqueante | PR contra `development` | Correr el CI | `pip-audit` y `pnpm audit` bloquean el merge si hay una vulnerabilidad sin excepción justificada | API | Job `Dependency audit` en verde en el CI del backend y del frontend; backend #162 (excepción `PYSEC-2026-1845` documentada) y frontend #134. No se registró un PR de prueba con una vulnerabilidad | ✅ |
| CP-H5-ENT-02 | DAST con OWASP ZAP | Stack levantado en el CI | Correr el job DAST | Sin alertas High; toda excepción `IGNORE` está en `docs/seguridad/zap-exceptions.md` | API | Job `DAST (OWASP ZAP)` en verde en el CI del backend (backend #210) | ✅ |
| CP-H5-ENT-03 | Pruebas de contrato con G7, G6, G2 y G5 | Contratos publicados de cada grupo | Correr las pruebas de contrato | Fallan si un cliente deja de coincidir con el contrato del otro grupo | API | Sin pruebas todavía (H5-I1) | ⏳ backend [#174](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/174) |
| CP-H5-ENT-04 | Carga frente a los SLO | Stack de CI con módulos fake y RabbitMQ en Docker | Correr k6 de catálogo, chat y checkout | Los tres flujos cumplen latencia p95, tasa de error y throughput de [`slo-performance.md`](slo-performance.md) | API | [Run 45887721116](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45887721116), PASS: 1533 eventos consumidos, sin reintentos ni DLQ, checkout a 12,77 compras/s. Corrió en la rama `feat/h5-m3-notifications-consumer`, antes de su merge | ✅ |
| CP-H5-ENT-05 | Rendimiento y accesibilidad del frontend | Frontend construido | Correr Lighthouse CI | Cumple el presupuesto de rendimiento y accesibilidad | API | Sin workflow todavía (H5-P4) | ⏳ frontend [#144](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/144) |
| CP-H5-ENT-06 | Tráfico por el gateway | Kong delante del backend | Llamar a la API a través de Kong y navegar el frontend | Las respuestas pasan por Kong con sus cabeceras; el navegador solo llama a `/api/v1/*` del mismo origen | API y E2E | Job `Gateway integration (Kong OSS)` del CI del backend (`tests/integration/test_gateway_kong.py`) y `tests/e2e/gateway.spec.ts` del CI del frontend | ✅ |
| CP-H5-ENT-07 | Gateway en producción | Kong desplegado en Railway y `API_PROXY_TARGET` apuntando a Kong | Correr `gateway.spec.ts` con `PLAYWRIGHT_VERIFY_GATEWAY=true` contra producción | Todo el tráfico del frontend pasa por Kong | E2E | Sin ejecución (H5-G2) | ⏳ backend [#178](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/178), frontend [#142](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/142) |
| CP-H5-ENT-08 | Mecanismo asíncrono entre procesos | API y consumidor como servicios separados en Railway | Ver CP-H5-PAY-03 y CP-H5-PAY-04 | El evento se publica y se consume en otro proceso, y sobrevive a la caída del broker | Manual | [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md) (H5-M4) | ✅ |
| CP-H5-ENT-09 | Reporte de evals | LLM real con módulos fake | Correr las evals de H5-E1 | Existe un reporte con los casos aprobados por spec y ningún precio o dato que no venga de las herramientas | API (eval) | Sin ejecución (ver CP-H5-CHAT-05) | ⏳ backend [#175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175) |
| CP-H5-ENT-10 | Verificación posdespliegue | Despliegue de `development` | Correr `verify-production.yml` | El inicio, las promociones por `/api/v1` y las páginas principales responden sin error | API | Frontend: [run 45925804684](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925804684) en verde. El workflow del backend aparece como `skipped` en sus últimas ejecuciones; la verificación completa es H5-X1 | ✅ |

## Validación de la Definición de Terminado

Se valida el DoD de [`definicion-listo-terminado.md`](producto/definicion-listo-terminado.md) a nivel de hito, con los criterios de aceptación de `hito-5.md`. Fecha: 2026-11-26. La columna "Evidencia" se completará con los enlaces de `evidencia-hito-5.md` (H5-I3, [#61](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/61)) cuando ese documento exista.

| Criterio | Estado | Evidencia |
|---|---|---|
| D1.1 Los escenarios se cumplen | ⏳ Parcial | 38 de 47 casos de alcance ejecutados y aprobados; 2 fallidos y 6 pendientes (ver Resumen) |
| D1.2 Cada escenario tiene prueba automatizada que lo cita | ⏳ Parcial | Los casos de [`casos-prueba-hito-4.md`](casos-prueba-hito-4.md) todavía no tienen docstrings que citen el escenario |
| D2.1 Integración con los módulos externos, con errores y timeouts | ✅ | CP-H5-CAT-05, CP-H5-CHK-04; contra los contratos publicados de cada grupo depende de CP-H5-ENT-03 ⏳ |
| D2.3 `Idempotency-Key` y prueba de doble envío | ✅ | CP-H5-CHK-04, CP-H5-PAY-01 |
| D2.6 Ningún fallo asume disponibilidad | ✅ | CP-H5-CAT-04, CP-H5-CAT-05, CP-H5-CHK-02, CP-H5-PAY-04 |
| D3.2 Datos de tarjeta fuera de la BD y del LLM | ✅ | CP-H5-CHAT-04, CP-H5-PAY-02 |
| D4.1 Mobile-first en móvil y escritorio | ✅ | CP-H5-CAT-06 |
| D4.2 Accesibilidad | ⏳ | CP-H5-ENT-05 (Lighthouse) y la evaluación del frontend H5-F1 (frontend [#145](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/145)) |
| D5.3 CI en verde con linters, tipado, unitarias, integración y E2E | ✅ | CI backend 45925594126 y CI frontend 45925602758 |
| D5.4 Evals de intención con precisión ≥ 90 % | ⏳ | Tareas 4.1 y 4.2 del cambio M5 y H5-E1 (backend #175) |
| D5.5 RNF de rendimiento medidos | ✅ | CP-H5-ENT-04 |
| Hito 5: dependencias y ZAP bloquean el merge | ✅ | CP-H5-ENT-01, CP-H5-ENT-02 |
| Hito 5: contratos fallan si un cliente cambia | ⏳ | CP-H5-ENT-03 |
| Hito 5: reporte de k6 frente a los SLO | ✅ | CP-H5-ENT-04 |
| Hito 5: reporte de evals | ⏳ | CP-H5-ENT-09 |
| Hito 5: hallazgos de la evaluación del frontend corregidos o registrados | ⏳ | H5-F1, frontend #145 |
| Hito 5: todo el tráfico pasa por el gateway | ⏳ | CP-H5-ENT-06 ✅ en CI; CP-H5-ENT-07 ⏳ en producción |
| Hito 5: pago publicado y consumido en otro proceso, con el broker caído sin pérdida | ✅ | CP-H5-PAY-03, CP-H5-PAY-04, CP-H5-ENT-08 |

Los criterios D1.3 a D1.5, D2.2, D2.4, D2.5, D3.1, D3.3 a D3.5, D4.3, D4.4, D5.1, D5.2, D5.6 y D6 se validan por historia en la revisión de cada PR y no tienen un entregable propio en el Hito 5.

## Seguimiento

| Caso | Problema | Seguimiento | Responsable de cierre |
|---|---|---|---|
| CP-H5-CHAT-02, CP-H5-CART-01 | El E2E nocturno con LLM real falla desde el 24/11: tras la búsqueda no aparece el carrusel en 30 s. E2E-03 pasa, así que el streaming funciona | Issue por abrir en el frontend | Por definir |
| CP-H5-CHAT-05, CP-H5-ENT-09 | Evals sin ejecutar | backend [#175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175) | Sonny |
| CP-H5-ENT-03 | Pruebas de contrato sin escribir | backend [#174](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/174) | Sonny |
| CP-H5-ENT-05 | Lighthouse sin workflow | frontend [#144](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/144) | Diego |
| CP-H5-ENT-07 | Gateway sin desplegar en producción | backend [#178](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/178), frontend [#142](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/142) | Sebastian |
| CP-H5-ORD-04 | E2E de pedidos y reclamos sin escribir | specs [#64](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/64) | Nikol |
| CP-H5-ORD-05 | Anulación con reembolso sin terminar | backend [#182](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/182), frontend [#143](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/143) | Por definir |
| CP-H5-PAY-04 | El consumidor no vuelve a consumir tras reiniciar el broker | backend [#215](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/215) (PR abierto) | Mathias |

## Riesgos y limitaciones

- Railway tiene un solo entorno: la prueba con el broker caído y la carga se hicieron en Docker y en el CI, no en producción.
- Ventas G5 y Seguridad G7 corren en Render y pueden responder lento en frío; un checkout en frío puede devolver 503.
- Producción no tiene SMTP: los correos de confirmación y de retroalimentación se procesan con `FakeEmailSender` y no llegan a nadie.
- Los adjuntos viven en un volumen de Railway y se pierden si el servicio se recrea (SPEC-23 🟡).
- Los casos con LLM real dependen del proveedor y del catálogo vivo de Productos G6; antes de la presentación conviene correr `chat.real.spec.ts` contra producción (H5-X1, backend [#183](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/183)).
