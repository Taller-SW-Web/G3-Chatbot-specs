# Hito 4: Integración

## Objetivo

Presentar el Hito 4 el 2026-11-07 con los cuatro entregables del curso:

1. Implementación de CI/CD (build, compile, test, deploy).
2. Diseño de APIs.
3. Demo funcional con nuevas funcionalidades y mejoras.
4. Implementación de seguridad: autenticación en pantallas y APIs.

## Problema

Estado verificado el 2026-11-03 contra `origin/main` y `origin/development` de ambos repositorios.

| Área | Estado inicial |
|---|---|
| CI backend | `ruff`, pruebas unitarias, integración con PostgreSQL 18 y migraciones up/down/up; promovido a `main` en el PR #56 |
| CI frontend | `lint`, `typecheck`, `test` y `build`; Playwright no corre en CI (E2E-03 a E2E-07 en `test.fixme`) |
| Despliegue | Solo por la integración git de Railway y Vercel; no hay deploy condicionado al CI ni migraciones automáticas al desplegar |
| API | Prefijo `/api/v1` y errores `problem+json`; routers vacíos: `checkout`, `orders`, `shipping`, `contact`, `admin`, `returns`, `claims`, `evidence`; no se exporta `openapi.json` |
| Seguridad backend | Validación JWT con JWKS y RS256; issuer fijo `auth-service` (el real es `https://g7-auth-service.onrender.com/api/v1/auth`); producción con `MODULES_MODE=fake`; rate limit solo en registro; el token de servicio no se usa en ningún cliente |
| Seguridad frontend | Refresh silencioso e interceptor Bearer; token en LocalStorage; protección de pantallas solo por componente, sin guard de rutas |
| Funcionalidades | SPEC-04, 07, 08, 12, 13, 14, 15 y 16 sin implementar; pantallas de checkout y pedidos con mocks |
| Integraciones | Seguridad G7 en curso (PR #57); adaptadores de Ventas G5 y Despacho G2 vacíos; Productos G6 sin URL pública |

## Alcance

- SPEC-04, 07, 08, 12, 13, 14, 15 y 16.
- Integración real con Seguridad (G7) en producción.
- Autenticación en pantallas (frontend) y APIs (backend).
- Deploy condicionado al CI y migraciones automáticas.
- Contratos de las APIs nuevas.

Fuera de alcance: SPEC-23 (imágenes en el chat, H4-F8, movida al Hito 5–6 el 2026-11-03), SPEC-17 a 22 y SPEC-24 (Hito 5–6), pantallas de administración.

## Restricciones

- Cada integrante es responsable de una funcionalidad completa, backend y frontend (regla del curso aplicada desde el Hito 3).
- Cada integrante trabaja en rama propia y abre PR contra `development`. Todo PR requiere CI en verde y una aprobación.
- Solo Sebastian genera migraciones de Alembic, con revisión secuencial y `--rev-id` explícito.
- Los contratos de H4-A1 se acuerdan antes de implementar H4-F1 a H4-F5.
- Si un módulo externo no está disponible para la demo, se usa su mock con el modo por módulo (`SECURITY_MODE`, `PRODUCTS_MODE`, `SALES_MODE`, `DISPATCH_MODE`).
- Precios, stock, descuentos y costos de envío provienen siempre de las herramientas, nunca del texto del LLM.
- Modo TDD: sin configurar. Se ejecutan las verificaciones funcionales de cada repositorio.

## Tareas

Ruta de cada tarea: delegada al responsable indicado, en su propia rama. Prioridad: 🔴 imprescindible para la demo, 🟡 deseable.

### Fase 0: desbloqueo

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H4-A1 | Sebastian | specs, backend | 🔴 | Diseñar los contratos de `checkout`, `orders`, `shipping` y cupones (rutas, cuerpos, códigos de error) antes de implementarlos |
| H4-S1 | Mathias | backend | 🔴 | Mergear el PR #57 (contrato real de G7 e issuer configurable) y abrir el PR de `feat/per-module-modes` (modo por módulo) |
| H4-S3 | Nikol | — | 🔴 | Cerrar con G7: `client_secret` de `modulo-chatbot`, concesión de scopes, URL `https://g3-chatbot-frontend.vercel.app/verificar-correo` y retiro del rol `SERVICIO_INTEGRACION` |

### Fase 1: en paralelo

#### Seguridad

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H4-S2 | Sebastian | frontend | 🔴 | Registro y login contra el contrato real: checkbox de términos, celular `+51`, campos de la política de contraseña y manejo de `PASSWORD_CADUCADA` y `CODIGO_VENCIDO` |
| H4-S4 | Mathias | backend | 🔴 | Producción con `SECURITY_MODE=http` en Railway y prueba real de registro, login y MFA |
| H4-S5 | Diego | frontend | 🔴 | Guard de rutas para mi cuenta, checkout y pedidos. El token está en LocalStorage, por lo que `middleware.ts` no puede leerlo: usar guard en el cliente o una cookie indicadora de sesión |
| H4-S6 | Sebastian | backend | 🔴 / 🟡 | Dependencia `require_customer` en los endpoints que exigen sesión (checkout, pedidos, perfil) 🔴; rate limit en login y chat 🟡 |
| H4-S7 | Sonny | backend | 🔴 | Token de servicio en los clientes de Productos, Ventas y Despacho, y `X-Correlation-Id` como UUID con guiones |
| H4-S8 | Sebastian | specs | 🟡 | Actualizar `contratos-integracion.md`, `inicio-sesion/spec.md` y ADR-0009 (issuer y `SERVICIO_INTEGRACION`) |

#### CI/CD

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H4-C1 | Mathias | backend, frontend | 🔴 | Deploy condicionado al CI: Railway con espera del check y Vercel solo con el check en verde |
| H4-C2 | Mathias | backend | 🔴 | Migraciones automáticas al desplegar (`alembic upgrade head` como comando pre-deploy en Railway) |
| H4-C3 | Nikol | frontend | 🟡 | Playwright E2E en CI y activación de E2E-03 a E2E-07 |
| H4-C4 | Mathias | specs | 🔴 | Evidencia del pipeline (build, compile, test, deploy) para la presentación: diagrama y capturas |

#### Diseño de APIs

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H4-A2 | Sebastian | backend | 🟡 | Exportar `openapi.json` en CI y publicar `/docs` como evidencia |

#### Funcionalidades

El flujo principal de la demo es el checkout: SPEC-12 → 13 → 14 → 15 → 16.

| ID | Responsable | Repositorio | Prioridad | Integración | Tarea |
|---|---|---|---|---|---|
| H4-F1 | David | backend, frontend | 🔴 | Despacho G2 | SPEC-12 Dirección y cotización de envío; retirar `DISTRITOS` de `mockData` |
| H4-F2 | David | backend, frontend | 🟡 | — | SPEC-13 Cupones de descuento |
| H4-F3 | Diego | backend, frontend | 🔴 | — | SPEC-14 Checkout y simulación de pago con tarjeta |
| H4-F4 | Sonny | backend, frontend | 🔴 | Ventas G5 | SPEC-15 Grabación del pedido (outbox e idempotencia) |
| H4-F5 | Nikol | backend, frontend | 🔴 | — | SPEC-16 Notificación de confirmación por correo |
| H4-F6 | Alonso | backend, frontend | 🔴 | Productos G6 | SPEC-07 Recomendación y SPEC-08 Ofertas (herramientas del agente) |
| H4-F7 | Sebastian | backend, frontend | 🟡 | Seguridad G7 | SPEC-04 Validación del número celular |

### Fase 2: integración y demo

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H4-Q1 | Nikol | specs | 🔴 | Casos de prueba del Hito 4 y validación del DoD |
| H4-Q2 | Nikol, Diego | specs | 🔴 | Guion de la demo, `docs/evidencia-hito-4.md` y presentación |
| H4-P1 | Mathias | backend, frontend | 🔴 | Promover `development` a `main` y verificar el flujo completo en producción |

### Movidas al siguiente hito

| ID | Responsable | Tarea | Motivo |
|---|---|---|---|
| H4-F8 | Mathias | SPEC-23 Imágenes en el chat | No es obligatoria; se prioriza el flujo de checkout (decisión del 2026-11-03) |

## Criterios de aceptación

- Un cliente se registra, verifica su correo e inicia sesión con MFA contra Seguridad G7 en producción.
- Las pantallas de mi cuenta, checkout y pedidos redirigen al login sin sesión; los endpoints protegidos responden 401 sin token válido.
- El cliente completa en la demo el flujo búsqueda → carrito → envío → pago → pedido → correo de confirmación.
- Un PR con CI en rojo no puede desplegarse; las migraciones se aplican al desplegar.
- Los contratos de las APIs nuevas están documentados antes de su implementación.

## Verificaciones aplicables

- Backend: `ruff check .`, `python -m pytest tests/unit` y pruebas de integración en CI con PostgreSQL 18.
- Frontend: `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`.
- E2E: Playwright contra producción antes de la demo.

## Riesgos

- G5 y G2 todavía no exponen todo lo necesario (el endpoint de seguimiento de G2 no está implementado). Mitigación: modo por módulo con mocks.
- Productos G6 no tiene URL pública. Mitigación: `PRODUCTS_MODE=fake`.
- David y Sonny son los integrantes más cargados; SPEC-14 y SPEC-16 se reasignaron a Diego y Nikol.
- Plazo corto (4 días): H4-A1 bloquea a H4-F1 a H4-F5.

## Progreso

- 2026-11-03: auditoría del Hito 4 y desglose de tareas. CI de H3-17 promovido a `main` (PR #56). PR #57 de Seguridad G7 abierto. H4-F8 movida al siguiente hito.
- 2026-11-05 (H4-A1, Sebastian): contratos detallados de `cupones` (`POST/DELETE /carrito/cupon`), `envio` (`GET /direcciones`, `POST /envio/cotizar`), `checkout` (`POST /checkout`, `GET /checkout/{id}`, `POST /checkout/{id}/pago`) y `pedidos` (`GET /pedidos`, `GET /pedidos/{id}`, `GET /pedidos/{id}/seguimiento`, `POST /pedidos/{id}/reenviar-confirmacion`) documentados en `docs/contratos-integracion.md` (§2.4, §2.5 y §2.8). El backend incluye DTO, puertos, mapeadores y routers de contrato con pruebas unitarias; la implementación funcional de checkout, envío y pedidos sigue pendiente.
- 2026-11-05: revisión de PRs delegada a Codex. Correcciones de Seguridad (T10 a T12 de `g7-security-integration.md`) mergeadas en `development`: backend #57 y #61 (reemplaza al #58, cerrado al borrarse su rama base) y frontend #32. Los PR #59 y #33 de Diego (H4-S5 y H4-F3) tienen cambios requeridos.
- 2026-11-05: H4-C2 hecha: `alembic upgrade head` como comando pre-deploy en el panel de Railway (no se usa `railway.json` porque Config as Code de Railway quedó obsoleto). H4-C1, parte de Railway: opción "Wait for CI" activada. Falta Vercel.
- 2026-11-06: H4-S3 cerrada con G7: cliente `modulo-chatbot`, scope `tokens:introspeccion`, issuer confirmado y retiro del rol `SERVICIO_INTEGRACION`. Sincronización de `main` en `development` (backend #63) y promoción a `main`: backend #62 y frontend #34, con merge commit para que `main` siga contenida en `development`.
- 2026-11-06: H4-S1 y H4-S4 hechas. Producción con `SECURITY_MODE=http`: registro, verificación de correo y login con MFA probados contra G7. Pendiente: prueba de introspección con una sesión real, coordinada con G7.
- 2026-11-06: correcciones de la revisión de H4-A1 (C1 a C5 de `h4-a1-contract-fixes.md`): el checkout no acepta líneas ni importes del cliente, `contacto` se valida con 400 `DATO_INVALIDO`, el reenvío de confirmación exige `Idempotency-Key` y la cotización sin costo o plazo de Despacho responde 503. Backend #60 y specs #26.
- 2026-11-06: **H4-A1 mergeado** (`04ed44c`, PR #60). **H4-F1 backend** listo en el **PR #65** (reemplaza al #64, cerrado al borrarse su rama base), ya rebasado sobre `development` **con CI en verde**: `DespachoClient` con token de servicio, `ManageShippingUseCase` (líneas desde el carrito, direcciones guardadas de Seguridad) y `/api/v1/direcciones` + `/api/v1/envio/cotizar` registrados. Sin migración. El #65 incluye además el **fake de Despacho** (`DISPATCH_MODE=fake`): sin él la cotización responde 503 en la demo desplegada (`MODULES_MODE=fake`) y el checkout del #35 quedaría bloqueado; el fake devuelve S/ 12.50 y 1 día, el mismo importe de hoy. En el despliegue no poner `DISPATCH_MODE=http` hasta tener credenciales reales de G2. **Frontend** de la cotización en el **PR #35** (CI en verde), pendiente de rebasar sobre el #33 de Diego. **#33**: su CI estaba en rojo por `react-hooks/purity` en `AuthGuard`; el fix está verificado en el **PR #37** hacia su rama. Riesgo abierto: el #59 define su propio `CreateCheckoutRequest` junto al de H4-A1; hay que decidir el canónico antes de mergearlo. **H4-F2 backend** listo en el **PR #66** (CI en verde): aplicar/quitar cupón validando contra Productos sin consumirlo, confirmación de reemplazo, `motivo` del rechazo y límite de 5 fallos en 10 minutos; sin migración y sin tocar `container.py`/`main.py` para no chocar con el #59. Pendiente: credenciales reales de Despacho y el frontend del cupón.

- 2026-11-06 (cierre): el **#37** (fix de `react-hooks/purity` en `AuthGuard`) entró en la rama de Diego y **#33 y #59 están en `development`** (`b9cdaa7` y `525566e`). Rebasé mis tres PR sobre esa base, con CI en verde: **#65** (backend de envío), **#35** (frontend de la cotización; adapté `checkoutPage.test.tsx` al `QueryClientProvider` y al mock de `cotizarEnvio`, los 5 tests de Diego siguen pasando) y **#66** (cupones). **Seguimiento de la auditoría del código mergeado:** el checkout todavía toma el `costoEnvio` del cliente o cae a `12.50`, y el `descuento` del cliente; el frontend sigue enviando líneas e importes aunque el contrato de H4-A1 no lo permite (el #59 no lo aplica porque trae su propio `CreateCheckoutRequest`), así que conviven dos DTO de checkout. Falta integrar la cotización del #65 y el cupón del #66 en el cálculo del checkout.

- 2026-11-06 (noche): **#35 mergeado** (`9573c90`) y **H4-F1 frontend cerrado**. El merge dejó `development` en rojo: el #38 había añadido un caso de `CheckoutPage` que renderiza sin `QueryClientProvider` y la página ya cotiza con React Query; **hotfix #40** (CI verde) lo corrige. **H4-F2 frontend** en el **#39** (CI verde): cupón en el carrito con aplicar, confirmar reemplazo y quitar, con descuento y total del servidor. El #39 incluye el mismo commit del #40; al mergear el hotfix, rebasa sin duplicar. G2 respondió que su cotización espera su conexión con Productos: la demo va con `DISPATCH_MODE=fake` y la validación real queda agendada.

- 2026-11-06 (cierre del día): **#65, #66 y #39 mergeados**; el #40 se cerró porque su commit ya entró con el #39. **H4-F5** mergeado (backend #67, frontend #38) y **H4-S6** mergeado (backend #68: `require_customer` canónico y rate limit en login y chat). Promoción a `main`: backend #69 y frontend #41. **Importes del checkout en el servidor** (`checkout-server-amounts.md`): backend #70 y frontend #42, promovidos en #71 y #43. El checkout recotiza el envío con Despacho, rechaza `lineas` e importes del cliente con `400 VALIDACION` y responde `409 CARRITO_DESACTUALIZADO`. Queda un solo `CreateCheckoutRequest`, el del contrato. **H4-F6** (Alonso) en revisión: backend #72 y frontend #44, con CI en verde.
- 2026-11-06, auditoría de pendientes:
  - **H4-F4 (SPEC-15)** sin empezar: `ventas_api_adapter.py`, `manage_order_use_case.py` y `outbox_worker.py` siguen vacíos, y no hay rama ni PR.
  - **H4-S7** parcial: el token de servicio solo lo usan los clientes de Despacho y Seguridad; faltan Productos y Ventas.
  - **H4-C3** pendiente: `tests/e2e/smoke.spec.ts` mantiene 7 `test.fixme` y ningún workflow ejecuta Playwright.
  - **H4-Q2** y **H4-C4** pendientes: `docs/evidencia-hito-4.md` no existe.
  - Siguen pendientes las tareas 🟡 H4-S8 y H4-F7. El DTO estricto del checkout descarta `contacto.celular`, por lo que la validación de SPEC-04 no se ejecuta en el checkout.
- 2026-11-06 (H4-A2, Sebastian): script `scripts/export_openapi.py` creado, `docs/openapi.json` exportado (30 rutas) y paso de exportación + artefacto `openapi-spec` añadido en `.github/workflows/ci.yml`, con pruebas unitarias en `tests/unit/test_openapi_export.py` que verifican `/docs` (Swagger UI en `https://g3-chatbot-backend.up.railway.app/docs`) y `/openapi.json` (backend PR #74, rama `feature/h4-a2-exportar-openapi-ci`, commit `75d3905`).

## Siguiente paso

1. Revisar y mergear #72 y #44 (H4-F6), y promover a `main`.
2. Decidir el plan de H4-F4 (SPEC-15) para la demo: implementarla o mostrarla con mock.
3. Configurar H4-C1 en Vercel.
4. Preparar la evidencia y el guion de la demo (H4-C4 y H4-Q2).
5. Probar en producción el flujo con sesión (envío, pago, pedido y correo).
6. Coordinar con G7 la prueba de introspección.
7. Conseguir las credenciales reales de Despacho.
8. Documentar `APP_ENV` y `ALLOW_FAKE_SECURITY` en el `.env.template` del backend.
