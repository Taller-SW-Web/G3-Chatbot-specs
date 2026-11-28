# Casos de prueba del Hito 5

> Tarea **H5-Q1** de [`odd/tasks/hito-5.md`](../odd/tasks/hito-5.md), issue [#60](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/60).
> Fecha de corte: **2026-11-27**. Entorno de referencia: CI de `development` con módulos externos en `fake` (ADR-0022) y producción sobre `development`.

Este documento no reescribe las specs: fija los casos operativos que se ejecutan o se justifican para cerrar el Hito 5. Cada caso tiene precondición, pasos, resultado esperado, tipo y evidencia. Los escenarios completos siguen viviendo en `openspec/specs/<capacidad>/spec.md`.

## 1. Resumen por flujo

| Flujo | Specs de referencia | Casos | Evidencia principal | Estado |
|---|---|---:|---|---|
| Catálogo y ofertas | `busqueda-filtrado`, `ofertas-promociones`, `tarjetas-detalle-producto` | 2 | `tests/unit/mod_catalog/*`, `tests/e2e/home.spec.ts`, `tests/e2e/offers-recommendations.fixture.spec.ts` | Ejecutado |
| Chat y adjuntos | `motor-conversacion`, `adjuntos-imagenes-chat` | 2 | `tests/unit/mod_chat/*`, `tests/e2e/chat.real.spec.ts`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Carrito y cupones | `gestion-carrito`, `cupones` | 2 | `tests/unit/mod_cart/*`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Checkout y pago | `checkout-pago`, `grabacion-pedido` | 2 | `tests/unit/mod_checkout/*`, `tests/integration/mod_checkout/*`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Pedidos y seguimiento | `consulta-estado-pedido`, `seguimiento-despacho`, `notificacion-confirmacion` | 2 | `tests/unit/mod_orders/*`, `tests/integration/mod_orders/*`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Postventa | `creacion-reclamo`, `solicitud-devolucion-cambio`, `consulta-reclamo`, `consulta-devolucion-reembolso` | 2 | `tests/unit/mod_postventa/*`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Cuenta y sesión | `inicio-sesion`, `registro-cliente`, `validacion-celular` | 2 | `tests/unit/mod_auth/*`, `tests/e2e/smoke.spec.ts` | Ejecutado |
| Administración | — | 1 | No hay backoffice en el canal; catálogo y pedidos se administran en G6/G5/G7 | Fuera de alcance justificado |

**Cobertura del criterio “todos los flujos tienen al menos un caso ejecutado o justificado”:** 7 flujos con evidencia en unitarias/E2E y 1 flujo (administración) justificado como fuera del alcance del canal.

## 2. Casos representativos

| ID | Flujo | Precondición | Pasos | Resultado esperado | Tipo | Evidencia |
|---|---|---|---|---|---|---|
| CP-H5-CAT-01 | Catálogo | Backend en `fake` con productos y ofertas | Abrir `/`; esperar la grilla; cambiar el orden; abrir el detalle de un producto | La grilla muestra tarjetas con precio/stock; el orden cambia; el detalle abre con el SKU correcto | E2E | [`home.spec.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/e2e/home.spec.ts), [`homePage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_catalog/homePage.test.tsx) |
| CP-H5-CAT-02 | Catálogo | Un SKU sin stock y otro con oferta vencida | Consultar el catálogo y el detalle | El agotado no permite agregar; el precio vencido se muestra como regular y no como oferta | Unidad/API | [`catalogo.test.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_catalog/catalogo.test.ts), [`test_catalog_partial.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_catalog/test_catalog_partial.py) |
| CP-H5-CHAT-01 | Chat | Sesión anónima con `chat_sid` | Crear conversación; enviar “Hola”; leer el stream SSE | Recibe `event: aceptado`, bloques de respuesta y `event: fin`; el historial persiste | API/E2E | [`test_send_message_sse.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_chat/test_send_message_sse.py), [`chat.real.spec.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/e2e/chat.real.spec.ts) |
| CP-H5-CHAT-02 | Chat/adjuntos | Sesión con una imagen JPG/PNG válida | Adjuntar imagen; enviar mensaje; consultar la URL firmada | La imagen se guarda privada; el mensaje referencia el adjunto; la URL firmada expira | API | [`test_attachment_service.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_chat/test_attachment_service.py), [`chatPage-adjuntos.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_chat/chatPage-adjuntos.test.tsx) |
| CP-H5-CART-01 | Carrito | Catálogo con stock | Agregar un producto; cambiar cantidad; eliminar la línea | Totales recalculados; la línea desaparece al llegar a 0; no se permite superar stock | E2E/Unidad | [`smoke.spec.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/e2e/smoke.spec.ts), [`cartPage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_cart/cartPage.test.tsx) |
| CP-H5-CART-02 | Carrito/cupón | Un cupón válido y otro inválido | Aplicar cupón; recalcular; quitarlo | El válido descuenta; el inválido devuelve `CUPON_INVALIDO`; al quitarlo el total vuelve al subtotal | API/Unidad | [`test_coupon_use_case.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_cart/test_coupon_use_case.py), [`cupon-adapter.test.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_cart/cupon-adapter.test.ts) |
| CP-H5-CHK-01 | Checkout/pago | Cliente autenticado, carrito con stock y dirección válida | Confirmar checkout; pagar con la tarjeta de prueba aprobada | `201`/`200`; se crea el pedido en Ventas; el pago queda aprobado; el carrito se cierra | API/E2E | [`test_manage_checkout_use_case.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_checkout/test_manage_checkout_use_case.py), [`test_cart_checkout_adapters_postgres.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/integration/mod_checkout/test_cart_checkout_adapters_postgres.py) |
| CP-H5-CHK-02 | Checkout/pago | Pago rechazado o timeout de Ventas | Intentar pagar; reintentar con la misma `Idempotency-Key` | No se duplica el pedido; el rechazo se muestra sin perder el carrito; el reintento devuelve el mismo resultado | API | [`test_payment_concurrency_postgres.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/integration/mod_checkout/test_payment_concurrency_postgres.py), [`test_checkout_sales_timeout.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_checkout/test_checkout_sales_timeout.py) |
| CP-H5-ORD-01 | Pedidos | Pedido `ENTREGADO` con historial | Abrir `/pedido?pedidoId=…`; revisar historial y seguimiento | Se ven estado, hitos y datos de envío; no se exponen datos del repartidor ni GPS | Unidad/E2E | [`orderDetailPage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_orders/orderDetailPage.test.tsx), [`seguimientoPage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_orders/seguimientoPage.test.tsx) |
| CP-H5-ORD-02 | Pedidos | Pedido `PAGADO` y Despacho con 404 | Consultar seguimiento | Se devuelve el estado de Ventas con `detalleDisponible=false`, sin error visible | API | [`test_m5_order_tracking.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_orders/test_m5_order_tracking.py) |
| CP-H5-POST-01 | Postventa | Pedido entregado dentro de plazo | Registrar reclamo/devolución con evidencia | `201` con código de seguimiento; el historial muestra la constancia | E2E/Unidad | [`reclamoPage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_postventa/reclamoPage.test.tsx), [`devolucionPage.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_postventa/devolucionPage.test.tsx) |
| CP-H5-POST-02 | Postventa/CSAT | Pedido `ENTREGADO` sin calificar | Enviar CSAT con carita y comentario; reintentar | `201`; el bloque pasa a “Gracias”; un `409` se muestra como “Ya calificaste este pedido” | API/Unidad | [`test_csat_sent.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_postventa/test_csat_sent.py), [`deliveryRating.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_postventa/deliveryRating.test.tsx) |
| CP-H5-AUTH-01 | Cuenta/sesión | Cliente sin sesión | Abrir login; ingresar credenciales válidas; recargar | La sesión persiste; las rutas privadas dejan de redirigir al login | E2E/Unidad | [`loginForm.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_auth/loginForm.test.tsx), [`smoke.spec.ts`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/e2e/smoke.spec.ts) |
| CP-H5-AUTH-02 | Cuenta/sesión | Registro con correo no verificado | Registrarse; reenviar verificación; iniciar sesión | El correo se envía una vez por intento; el login exige verificación; el reenvío respeta el límite | API/Unidad | [`test_session_router.py`](https://github.com/Taller-SW-Web/G3-Chatbot-backend/blob/development/tests/unit/mod_auth/test_session_router.py), [`registroForm.test.tsx`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/tests/unit/mod_auth/registroForm.test.tsx) |
| CP-H5-ADM-01 | Administración | — | — | El canal no tiene backoffice propio: catálogo, pedidos, reclamos y devoluciones se administran en G6/G5/G7; dentro del canal, `/cuenta` cubre perfil y sesión | Justificado fuera de alcance | `docs/arquitectura/modularizacion.md` |

## 3. Evidencia de ejecución

| Evidencia | Enlace |
|---|---|
| CI backend `development` (unitarias, integración, gateway, DAST, Sonar) | [run 45932607534](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45932607534) |
| CI frontend `development` (unitarias, E2E, build, modules) | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758) |
| CI specs `development` | [run 45918803842](https://github.com/Taller-SW-Web/G3-Chatbot-specs/actions/runs/45918803842) |
| Performance con broker (H5-P5) | [run 45887721116](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45887721116) |
| Evidencia del flujo asíncrono (H5-M4) | [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md) |

Los casos de tipo E2E se ejecutan en el job `e2e` del frontend con los módulos en `fake`; los de API, en `pytest`; los unitarios, en Vitest/pytest. Las pruebas con G5/G6/G7 reales se registran en `docs/contratos-integracion.md` y en las issues de integración.

## 4. Validación del DoD del Hito 5

| Tarea | Estado | Evidencia |
|---|---|---|
| H5-C1 | ✅ | `pip-audit` y `pnpm audit` bloqueantes; CI actual |
| H5-C2 | ✅ | DAST ZAP y gate de alertas High; backend #210 |
| H5-C3 | ⚪ | Abandonada por decisión del owner (Ankarmin, 2026-11-27); quedó sin implementar: frontend #139 se cerró como `NOT_PLANNED` al moverse a specs y specs #50 está cerrada. Hoy producción se despliega desde `development` por Vercel y Railway, sin deploy por Actions |
| H5-C4 | ✅ | CODEOWNERS y ruleset; ADR-0024/CI |
| H5-C5 | ✅ | Revisión de seguridad del pipeline; ADR-0024 |
| H5-I1 | ✅ | Pruebas de contrato G7/G6/G2/G5; job bloqueante `contract`; backend #174 cerrada, #226–#229, run 46050322098 |
| H5-I2 | ✅ | E2E sin `test.fixme`; CI frontend |
| H5-E1 | ✅ | Suite y workflow en `development` (backend #230); corrida real 7/9 documentada ([run 46073219673](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/46073219673)); #245 cerrada; los 2 fallos de elección de herramienta quedan en backend #175 y #258 |
| H5-I3 | ✅ | Este documento + [`evidencia-hito-5.md`](evidencia-hito-5.md); sincronizado con specs #117 (H5-F1 enlazada en §4.1) |
| H5-P1/P2/P5 | ✅ | `docs/slo-performance.md`, run 45887721116 |
| H5-P3 | 🟡 | Workflow de k6 hecho; la medición del checkout en paralelo sigue abierta en backend #190 (asignada a Lume03) |
| H5-P4 | ✅ | Lighthouse CI en el gate `check`; frontend #180, #144 cerrada, run 46048924659 |
| H5-G1 | ✅ | ADR-0031; specs #81 |
| H5-G2 | ✅ | Backend #211 y frontend #152 mergeados; backend #178 y frontend #142 cerradas; gateway verificado en producción el 2026-11-27 ([`evidencia-hito-5.md` §8](evidencia-hito-5.md)) |
| H5-G3 | ✅ | Backend #214 mergeado; backend #179 cerrada |
| H5-M1/M2/M3 | ✅ | Código en `development`; consumidor desplegado; backend #177 cerrada |
| H5-M4 | ✅ | [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md) |
| H5-F1 | 🟡 | Informe [`evaluacion-integral-frontend.md`](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/blob/development/docs/evaluacion-integral-frontend.md); consolidación 8/8 en frontend PR #198 (abierto); frontend #145 abierta |
| H5-X1 | ✅ | Verificación de producción sobre `development`; backend #183 cerrada |
| H5-Q1 | ✅ | Este documento |

## 5. Casos fallidos, limitaciones y seguimiento

- **Contratos G7/G6/G2/G5:** el job `contract` es bloqueante y está en verde (backend #174 cerrada; #226–#229).
- **Evals del chatbot:** corrida real 7/9 documentada (run 46073219673); #245 cerrada; los 2 fallos de elección de herramienta quedan en backend #175 y el modelo por defecto y los casos degradados en backend #258.
- **Lighthouse:** cerrado con frontend #180 (job `lighthouse` en el gate `check`); la deuda de LCP/TBT en CI sigue en frontend #164.
- **Gateway Kong:** desplegado y verificado en producción el 2026-11-27 (backend #178/#179 y frontend #142 cerradas).
- **H5-C3 (deploy por Actions):** abandonada por decisión del owner (Ankarmin, 2026-11-27); quedó sin implementar: frontend #139 se cerró como `NOT_PLANNED` al moverse a specs y specs #50 está cerrada. Hoy producción se despliega desde `development` por Vercel y Railway.
- **Checkout en paralelo (H5-P3):** pendiente en backend #190, asignada a Lume03.
- **Evaluación integral del frontend (H5-F1):** 8/8 módulos en frontend PR #198 (abierto); hallazgos P1 abiertos en frontend #182, #184, #186, #188, #189 y #190 (ver [`evidencia-hito-5.md` §4.1](evidencia-hito-5.md#41-evaluación-integral-del-frontend-h5-f1)). Al cerrar #183, #187 y #189 pueden cambiar los casos de catálogo, pedidos y chat; al cerrar #185, los de checkout; #190 afecta a los modales de varios flujos.
- **Adjuntos:** producción usa `ATTACHMENT_STORAGE=local` sobre volumen; el cierre operativo y el checklist están en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27).
- **Administración:** el canal no tiene backoffice; se justifica fuera de alcance y se cubre en los módulos dueños.
- Los casos que dependen de G5/G6/G7 reales se ejecutan de forma manual/controlada; el CI usa fakes para no depender de servicios externos.

Cualquier caso que falle debe quedar enlazado a una issue concreta; los pendientes anteriores son los únicos conocidos al 2026-11-27.
