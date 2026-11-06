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

## Siguiente paso

Integrar H4-A1 y H4-S1 (`#57` y `#58`), cerrar H4-S3 con G7 y avanzar la Fase 1 (H4-S2, H4-S6 y H4-F1 a H4-F7).
