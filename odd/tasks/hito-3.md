# Hito 3: Demo 1

## Objetivo

Entregar la primera demo funcional y desplegada: un cliente se registra, inicia sesión, conversa con el asistente, busca productos y arma un carrito, con el frontend conectado al backend real.

## Problema

Estado verificado el 2026-10-10 contra `origin/development` de ambos repositorios.

| Área | Estado inicial |
|---|---|
| Backend | Solo está implementada la persistencia (modelos, adapters y migración `0001`). Dominio, puertos, casos de uso, HTTP, WebSocket, clientes httpx y NLP son archivos vacíos |
| Frontend | Interfaz construida con datos mock (`mockData.ts`); ya existen los puertos `ChatbotApiPort` y `WebSocketPort`, sus adapters y seis casos de uso, sin conexión al backend |
| CI backend | Ejecuta únicamente `pytest tests/unit`; sin lint, sin pruebas contra PostgreSQL y sin verificación de migraciones |
| CI frontend | Pasa en verde sin ejecutar nada: el workflow exige `pnpm-lock.yaml` y el repositorio no lo tiene |
| Despliegue | No existe en ningún repositorio; `docs/arquitectura/c4.md` lo lista como pregunta abierta, junto con la topología del worker |
| Ramas | `main` y `development` sin protección en ambos repositorios; dos PR del Hito 2 entraron sin aprobación |
| PR abiertos | Backend #35 (`feature/h3-motor-herramientas`, +1111 líneas, CI en verde, sin revisión) |

## Alcance

Según `docs/producto/epicas.md`:

- SPEC-01 a 03: registro, verificación de correo, inicio de sesión y gestión de sesión.
- SPEC-05 (núcleo): conversaciones múltiples, interpretación de intención, tool calling y streaming.
- SPEC-06 y 09: búsqueda y filtrado; carrusel, tarjetas y detalle de producto.
- SPEC-10 y 11: carrito y validación de stock.
- Pista de DevOps: CI, CD y despliegue de ambos repositorios.

Fuera de alcance: SPEC-04, 07, 08 y 23 (Hito 4), checkout y pedido (Hito 4), seguimiento y postventa (Hito 5–6), e integración con las APIs reales de los otros módulos (credenciales desde el Hito 4; se usan mocks según ADR-0017).

## Restricciones

- Destinos de despliegue (decisión provisional del 2026-10-10, pendiente de ADR): backend en Railway plan Hobby, con la API y el worker como servicios separados; frontend en Vercel; base de datos en Supabase.
- Cada integrante trabaja en rama propia y abre PR contra `development`. Todo PR requiere CI en verde y una aprobación.
- Solo Sebastian genera migraciones de Alembic, con revisión secuencial (`0002`, `0003`, ...) y `--rev-id` explícito.
- Identificadores de base de datos en inglés; etiquetas de interfaz en español, resueltas por el frontend.
- Next.js se usa solo como frontend (ADR-0004): sin Route Handlers ni Server Actions hacia el backend.
- Precios, stock y descuentos provienen siempre de las herramientas, nunca del texto del LLM.
- Gestor de paquetes del frontend: pnpm (decisión del 2026-10-10, tarea H3-04). Cuando el cambio llegue a `development`, cada integrante debe actualizar su entorno local: instalar pnpm, eliminar `node_modules` y cualquier `package-lock.json` local, ejecutar `pnpm install` y no volver a usar `npm install`.
- Modo TDD: sin configurar. Se ejecutan las verificaciones funcionales de cada repositorio (`python -m pytest` en backend; `lint`, `typecheck`, `test` y `build` en frontend).

## Tareas

Ruta de cada tarea: delegada al responsable indicado, en su propia rama.

### Fase 0: desbloqueo

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-00 | Nikol | specs | Cerrar H2-09 y actualizar `hito-2.md` con lo ya mergeado |
| H3-01 | Mathias | specs | ADR de despliegue y vista de despliegue en `c4.md`; resuelve la topología del worker |
| H3-02 | Mathias | backend, frontend | Protección de `main` y `development`: CI obligatorio y una aprobación |
| H3-03 | Mathias | backend | Dockerfile, endpoint de salud y esqueleto desplegado en Railway |
| H3-04 | Mathias | frontend | Confirmar el gestor de paquetes, versionar el lockfile para que el CI ejecute sus pasos y desplegar el frontend actual en Vercel con vista previa por PR |
| H3-05 | Sebastian | backend, specs | Puertos, contratos (herramienta → caso de uso, bloques, eventos WS), cliente httpx base y configuración por entorno |
| H3-06 | Sonny | backend | Mock de Productos (ADR-0017) |
| H3-07 | Sebastian | backend | Mock de Seguridad (ADR-0017) |
| H3-08 | Sebastian (revisa), Alonso (corrige) | backend | Revisar y mergear el PR #35 |

- [ ] H3-00
- [x] H3-01
- [ ] H3-02
- [ ] H3-03
- [ ] H3-04
- [ ] H3-05
- [ ] H3-06
- [ ] H3-07
- [ ] H3-08

### Fase 1: en paralelo

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-09 | Sebastian | backend | SPEC-01 a 03: registro, verificación de correo, inicio de sesión, MFA, refresh y cierre de sesión |
| H3-10 | Mathias | backend | SPEC-05 núcleo: CRUD de conversaciones, bucle del agente (máximo 5 iteraciones), system prompt, `LLMProvider` y WebSocket |
| H3-11 | Alonso | backend | Declaración de las herramientas del hito, `ActionDispatcher`, `OutputValidator` y modo degradado |
| H3-12 | Sonny | backend | SPEC-06, 09, 10 y 11: catálogo, detalle de producto, carrito y validación de stock |
| H3-13 | David | frontend | Sustituir `mockData.ts` por los adapters reales (`ChatbotApiAxiosAdapter`, `ChatbotWebSocketAdapter`) y conectar los componentes de chat, tarjetas de producto y carrito |
| H3-14 | Diego | frontend | `HomePage`, `Sidebar`, `ChatPage`, `CartPage` y formularios de registro e inicio de sesión sobre el design system (`docs/design-system.md`) |
| H3-15 | Sebastian, Diego | frontend | Sesión en el cliente: almacenamiento del token, refresh y mitigaciones de XSS exigidas por SPEC-01 a 03 |
| H3-16 | Nikol | specs, frontend | Casos de prueba a partir de los escenarios de las specs del hito y E2E de humo con Playwright |
| H3-17 | Mathias | backend | CI: lint, pruebas de integración con PostgreSQL como servicio y verificación de `alembic upgrade head` |
| H3-18 | Mathias | backend, frontend | CD: `development` → staging y `main` → producción, con las migraciones como paso del despliegue; secretos por entorno (LLM, Supabase, URLs base de los mocks) |

- [ ] H3-09
- [ ] H3-10
- [ ] H3-11
- [ ] H3-12
- [ ] H3-13
- [ ] H3-14
- [ ] H3-15
- [ ] H3-16
- [ ] H3-17
- [ ] H3-18

### Fase 2: integración y demo

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-19 | Todos, coordina Nikol | backend, frontend | E2E sobre staging y corrección de fallas |
| H3-20 | Mathias | backend, frontend | Promoción a producción y guion de la demo |

- [ ] H3-19
- [ ] H3-20

## Criterios de aceptación

- En el entorno desplegado, un cliente se registra, verifica su correo, inicia sesión, conversa, busca productos y arma un carrito.
- Las respuestas llegan en streaming por WebSocket y los datos comerciales de las tarjetas provienen de las herramientas.
- El frontend no depende de `mockData.ts` en los flujos del hito.
- Todo PR entra con CI en verde y una aprobación; el CI del frontend ejecuta de verdad `lint`, `typecheck`, `test` y `build`.
- Un merge a `main` despliega backend y frontend sin pasos manuales, con las migraciones aplicadas.
- El despliegue está documentado en un ADR y en `docs/arquitectura/c4.md`.

## Verificaciones aplicables

- Backend: `python -m pytest tests/unit`, pruebas de integración contra PostgreSQL y `alembic upgrade head` seguido de `alembic downgrade base`.
- Frontend: `lint`, `typecheck`, `test` y `build`.
- E2E: Playwright sobre staging.

## Entrega

Estrategia: `ask-on-risk`. El hito supera con holgura las 400 líneas modificadas; se entrega como PR independientes por tarea contra `development`, sin encadenar.

## Riesgos

- **Carga de Mathias:** concentra el bucle del agente y siete tareas de DevOps. Es el cuello de botella del hito; conviene reasignar H3-17 o posponerla hasta cerrar H3-10.
- **Carga de Sebastian en la Fase 0:** contratos, mock de Seguridad y revisión del PR #35. Si se atrasa, se detiene la Fase 1.
- **PR #35 sin revisar:** bloquea H3-10 y H3-11.
- **Fecha de la demo sin definir:** el plan no tiene fechas; hay que fijarla para ordenar la Fase 2.
- **Costo de Railway:** USD 5 al mes; falta definir quién aporta el medio de pago.
- **Dependencia de David con Sebastian:** H3-13 necesita los contratos de H3-05; mientras tanto trabaja contra los puertos ya definidos en el frontend.

## Progreso

Estado al 2026-10-10: Fase 0 iniciada. Documento creado y versionado en `main`. Copia en Engram: tema `odd/hito-3/tasks`.

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-01 | Delegada (un redactor; ADR y `c4.md` son dos archivos no triviales) | ADR-0020 creado; vista de despliegue en `c4.md`; preguntas abiertas de topología del worker y despliegue cerradas. Los seis diagramas Mermaid de `c4.md` renderizan con `mermaid-cli`; enlaces a ADR-0020 verificados | RDD desactivado; nivel evaluado: pasivo | `11484dc` en `main` |
| H3-04 (en curso) | Delegada (un redactor para la migración); corrección de lint en línea | Migración a pnpm 10.34.6 y CI sin el paso que omitía las verificaciones; error de lint previo en `ChatPage.tsx` corregido. `lint`, `typecheck`, `test` y `build` pasan en local. Falta: push, CI en GitHub y despliegue en Vercel con vista previa por PR | RDD desactivado | `b5e0469` y `1794b10` en `development` del frontend, sin push |

Pendientes que deja H3-01: dónde se alojan los mocks en el entorno desplegado (afecta a H3-03, H3-06 y H3-07) y quién aporta el medio de pago de Railway.

## Siguiente paso

Mathias, Sebastian y Sonny inician la Fase 0. La primera decisión por cerrar es la fecha de la demo.
