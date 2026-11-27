# Hito 5: Calidad, rendimiento y arquitectura

## Objetivo

Presentar el Hito 5 con los cuatro entregables del curso:

1. CI/CD incluyendo revisión de seguridad.
2. Evidencia de pruebas de integración.
3. Evidencia de pruebas de performance.
4. Uso de API Management y mecanismo asincrónico entre microservicios.

Fecha de presentación: 2026-11-28.

## Estado inicial (2026-11-22)

> Esta sección conserva el punto de partida del desglose. El estado vigente está en **Estado actual** y **Progreso**.

Estado verificado el 2026-11-22 contra `development` (backend `1c9c333`, frontend `2b47b56`) y la configuración de Railway.

| Área | Estado inicial |
|---|---|
| CI/CD y seguridad | CodeQL, Trivy, hadolint, Sonar, dependency-review, Dependabot, `pip-audit`, `pnpm audit` y secret scanning; CI en verde. Las auditorías de dependencias son informativas (`\|\| echo`), no hay DAST, el entorno `production` no exige aprobación (CI-12), la protección de rama tiene `enforce_admins=false` y no exige revisión de code owners. ADR-0024 sigue en "Propuesta" |
| Pruebas de integración | Unas 12 pruebas de backend en `tests/integration` con PostgreSQL real en CI, Playwright E2E en CI con módulos fake y E2E nocturno contra el entorno real. No hay pruebas de contrato contra los otros grupos (G2, G5, G6, G7) ni `docs/evidencia-hito-5.md`. El smoke de Playwright mantiene casos en `test.fixme` |
| Pruebas de performance | No existen: sin SLO, sin scripts, sin workflow ni reporte |
| API Management | No hay gateway. Solo prefijo `/api/v1`, rate limiter en memoria, exportación de OpenAPI y el proxy de Next.js |
| Mecanismo asíncrono | Outbox transaccional con worker (ADR-0011: `NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL`) dentro del mismo proceso. ADR-0010 declara "sin eventos y sin broker" |
| Producción (Railway) | Un solo entorno (`production`) y un servicio. Todos los módulos en `http` (`SALES_MODE`, `SECURITY_MODE`, `PRODUCTS_MODE`, `DISPATCH_MODE` y `MODULES_MODE`; verificado el 2026-11-24, sin fakes desplegados); `OUTBOX_WORKER_ENABLED=true`; `ATTACHMENT_STORAGE=local` sobre un volumen de Railway |
| PRs abiertos | Backend #149 y #150, frontend #112 y #113 (SPEC-17, 19, 20 y 24), specs #36 y #30. Los PR #112 y #113 fallan solo en el preview de Vercel por falta de `API_PROXY_TARGET` en el entorno Preview |

## Estado actual (2026-11-26)

| Área | Estado |
|---|---|
| CI/CD y seguridad | H5-C1, H5-C2, H5-C4 y H5-C5 hechas; H5-C3 redefinida para desplegar producción desde `development` (frontend #139) |
| Pruebas de integración | H5-I2 hecha (sin `test.fixme`); H5-I1 (contratos) y H5-E1 (evals) pendientes (backend #174, #175); H5-I3 tiene documento base en `docs/evidencia-hito-5.md` (se actualiza al cerrar contratos/evals); H5-Q1 cerrada con `docs/casos-prueba-hito-5.md` |
| Pruebas de performance | H5-P1, H5-P2, H5-P3 y H5-P5 hechas; la corrida con RabbitMQ y consumidor está en el run 45887721116 y en `docs/slo-performance.md`; H5-P4 (Lighthouse) pendiente (frontend #144/#156) |
| API Management | H5-G1 hecha (ADR-0031, specs #81); H5-G2 y H5-G3 tienen el código mergeado (backend #211/#214, frontend #152), pero faltan el despliegue/verificación en Railway y Vercel (backend #178/#179, frontend #142) |
| Mecanismo asíncrono | H5-M1, H5-M2 y H5-M3 (código) hechas (#196/#197/#215); `G3-Chatbot-consumer` está desplegado y consumiendo; falta cerrar #177 con evidencia formal; H5-M4 tiene `docs/evidencia-mecanismo-asincrono.md` (specs #63) |
| Producción | `development` es la rama por defecto y la que despliega Railway/Vercel; `main` es un placeholder de un commit con solo `README.md` desde el 2026-11-26. No se promueve `development` a `main`. H5-X1 se limita a verificar producción (backend #183) |
| Specs y documentación | S2, L4 y S4 cerrados; M5 (#64) cerrado como supersedido (#96, frontend #162, backend #219); H5-Q1 e H5-I3 (documento base) creados; SPEC-23 sigue 🟡 por bucket y variables (specs #53), con fail-closed ya implementado (backend #198); `inicio-sesion` queda 🟡 por el Req. 4 (backend #184) y `consulta-estado-pedido` por la anulación/reembolso (backend #182, frontend #143) |

## Alcance

- Endurecer el pipeline y documentar la revisión de seguridad.
- Pruebas de contrato contra los módulos de otros grupos y evidencia de integración.
- SLO, pruebas de carga del backend y métricas del frontend.
- Gateway de API delante del backend.
- RabbitMQ en CloudAMQP (plan gratuito) como mecanismo asíncrono entre procesos, alimentado por el outbox.
- Cierre de los PR abiertos de SPEC-17, 19, 20 y 24.

Fuera de alcance: lote 2 de `audit-2026-11-fixes.md`, migración de adjuntos a Supabase Storage.

## Decisiones

- 2026-11-22: **RabbitMQ en CloudAMQP (plan Little Lemur)** para el entregable 4. El enunciado pide "uso de" un mecanismo asincrónico "entre microservicios"; el outbox solo es un proceso interno. Se mantiene el outbox: su worker publica en RabbitMQ y un consumidor que corre como proceso separado procesa los eventos. Límites del plan: 1 M de mensajes al mes, 20 conexiones, 100 colas, 10 000 mensajes en cola y borrado de colas inactivas a los 28 días.

- 2026-11-24: **Los cuatro tipos de tarea del outbox pasan por el broker** (`NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL` y `SEND_FEEDBACK_EMAIL`), porque producción ya tiene todos los módulos en `http` y un consumidor aparte puede llamar a Ventas. Se registra en [ADR-0030](../../docs/arquitectura/adr/ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md). ADR-0010 queda **modificado, no reemplazado**: la integración con los módulos externos sigue siendo REST síncrona. Sin cambio de esquema del outbox; interruptor de reversa `OUTBOX_DISPATCH_MODE=broker|direct`.

- 2026-11-26: **Kong OSS en modo DB-less (`kong.yml`) como API Gateway** delante del backend FastAPI en Railway. Se registra en [ADR-0031](../../docs/arquitectura/adr/ADR-0031-api-gateway-kong-oss.md) y se enmienda [ADR-0023](../../docs/arquitectura/adr/ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md): `API_PROXY_TARGET` en Vercel pasa a apuntar a Kong, manteniendo el mismo origen y cookies de primera parte. Kong hace *pass-through* de JWT/cookies hacia FastAPI, fija `read_timeout: 90000` en el *service* y `response_buffering: false` en la *route* SSE de chat, aplica rate limiting perimetral por IP (`policy: local`, manteniendo `rate_limiter.py` en backend como defensa en profundidad para no alterar el contrato `problem+json`) y expone `/openapi.json` y `/docs`.

## Restricciones

- Cada integrante trabaja en rama propia y abre PR contra `development`. Todo PR requiere CI en verde y una aprobación.
- Solo Sebastian genera migraciones de Alembic, con revisión secuencial y `--rev-id` explícito.
- Las pruebas de performance **no** se ejecutan contra producción ni contra CloudAMQP: Railway tiene un solo entorno y una corrida de carga puede agotar la cuota mensual de mensajes. Se usan el stack local o de CI con módulos fake y RabbitMQ en Docker.
- Cada proceso abre una sola conexión persistente a RabbitMQ (CloudAMQP limita las conexiones nuevas por segundo).
- El consumidor declara sus colas al arrancar para que se recreen si CloudAMQP las borra por inactividad.
- Ningún secreto (`RABBITMQ_URL`, claves del gateway) entra al repositorio; se configuran en Railway y en los secretos de GitHub.
- Modo TDD: sin configurar. Se ejecutan las verificaciones funcionales de cada repositorio.

## Tareas

Ruta de cada tarea: delegada al responsable indicado, en su propia rama. Prioridad: 🔴 imprescindible para la presentación, 🟡 deseable.

### Fase 0: desbloqueo

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-C0 | Mathias | frontend | 🔴 | Agregar `API_PROXY_TARGET` al entorno Preview de Vercel para desbloquear el preview de #112 y #113 |
| H5-M1 | Mathias | specs | 🔴 | ADR nuevo del broker (RabbitMQ en CloudAMQP, eventos, colas, reintentos y DLQ) que modifica a ADR-0010 (no lo reemplaza); actualizar ADR-0011. Redactada el 2026-11-24 como ADR-0030 |
| H5-G1 | Sebastian | specs | 🔴 | ADR de API Management: elección del gateway, despliegue, rutas, rate limit, autenticación y publicación de OpenAPI |

### Fase 1: en paralelo

#### A. CI/CD y revisión de seguridad

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-C1 | David | backend, frontend | 🔴 | Hacer bloqueantes `pip-audit` y `pnpm audit` (quitar `\|\| echo`), con lista de excepciones justificadas |
| H5-C2 | Sebastian | backend | 🔴 | DAST con OWASP ZAP baseline contra el stack levantado en CI y reporte como artefacto |
| H5-C3 | Mathias | backend, frontend | 🟡 | Entorno `production` en GitHub con aprobación requerida (CI-12) y deploy de producción por Actions **desde `development`**, con smoke y rollback. Implementación: [frontend#139](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/139) |
| H5-C4 | David | backend, frontend | 🟡 | Protección de rama: `enforce_admins=true` y revisión de code owners |
| H5-C5 | David | specs | 🔴 | Pasar ADR-0024 a "Aceptada" y actualizar el diagrama del pipeline con los pasos de seguridad |

#### B. Pruebas de integración

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-I1 | Sonny | backend | 🔴 | Pruebas de contrato de los clientes de Seguridad G7, Productos G6, Despacho G2 y Ventas G5 contra sus contratos publicados |
| H5-I2 | Nikol | frontend | 🔴 | Activar los casos en `test.fixme` del smoke de Playwright |
| H5-I3 | Nikol | specs | 🔴 | `docs/evidencia-hito-5.md`: pruebas de integración, E2E, contrato y evals, con enlaces a las ejecuciones de CI |
| H5-E1 | Sonny | backend | 🔴 | Evals del chatbot en `tests/evals/` contra el LLM real con módulos fake: conversaciones de referencia por spec (búsqueda, recomendación, ofertas, carrito, precios sin inventar, fuera de dominio, datos sensibles, modo degradado). Las aserciones se hacen sobre las herramientas llamadas y los datos devueltos, no sobre el texto exacto. Workflow manual o nocturno, con reporte de casos aprobados |

#### C. Pruebas de performance

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-P1 | Alonso | specs | 🔴 | Definir SLO (latencia p95, tasa de error, throughput) para catálogo, chat y checkout |
| H5-P2 | Alonso | backend | 🔴 | Scripts de k6 para catálogo, chat y checkout contra el stack local o de CI con módulos fake. La corrida con RabbitMQ en Docker pasa a H5-P5 |
| H5-P3 | Alonso | backend | 🟡 | Workflow manual de k6 en GitHub Actions y reporte con resultados frente a los SLO |
| H5-P4 | Diego | frontend | 🟡 | Lighthouse CI con presupuesto de rendimiento y accesibilidad |
| H5-P5 | Mathias | backend, specs | 🔴 | Agregar RabbitMQ en Docker y el consumidor a la corrida de k6 (`performance.yml`) y registrar el resultado en `docs/slo-performance.md`. Depende de H5-M2 y H5-M3. Issue: [backend#168](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/168) |

#### D. API Management y mecanismo asíncrono

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-G2 | Sebastian | backend, frontend | 🔴 | Desplegar el gateway definido en H5-G1 delante del backend y enrutar el frontend a través de él, con prueba de integración que verifique el paso por el gateway |
| H5-G3 | Sebastian | backend | 🟡 | Mover el rate limit y la publicación de OpenAPI al gateway |
| H5-M2 | Mathias | backend | 🔴 | Cuenta de CloudAMQP y `RABBITMQ_URL` en Railway; el worker del outbox publica los eventos en RabbitMQ |
| H5-M3 | Mathias | backend | 🔴 | Consumidor de notificaciones como proceso separado (servicio o comando propio en Railway), con healthcheck y prueba de integración contra RabbitMQ en CI |
| H5-M4 | Mathias | specs | 🔴 | Evidencia del flujo asíncrono: diagrama, logs y prueba con el broker caído en la que el outbox retiene y luego publica |

#### Cierre de funcionalidades

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-R1 | Mathias | backend, frontend | 🔴 | Revisar, aprobar y mergear SPEC-17 y el comentario CSAT de SPEC-24 (backend #150, frontend #113) |
| H5-R2 | Mathias | backend, frontend | 🔴 | Revisar, aprobar y mergear SPEC-19 y SPEC-20 (backend #149, frontend #112) |
| H5-R3 | Mathias | specs | 🟡 | Revisar, aprobar y mergear specs #36 (Postventa G5) y #30 (exportación de OpenAPI) |

#### Revisión del frontend

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-F1 | Diego | frontend | 🔴 | Evaluación integral del frontend: recorrer todos los flujos, validar que pantallas, textos y datos coinciden con las specs y el backend, revisar el diseño (consistencia visual, responsive, accesibilidad, estados de carga, vacíos y error) y aplicar las mejoras, con un PR por módulo |

### Fase 2: integración y presentación

| ID | Responsable | Repositorio | Prioridad | Tarea |
|---|---|---|---|---|
| H5-Q1 | Nikol | specs | 🔴 | Casos de prueba del Hito 5 y validación del DoD |
| H5-X1 | Mathias | backend, frontend | 🔴 | Verificar el flujo completo en producción sobre `development` (gateway, broker y consumidor). **No** se promueve `development` a `main`: `main` es un placeholder de un commit con solo `README.md` desde el 2026-11-26. Implementación: [backend#183](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/183) |

## Criterios de aceptación

- Un PR con una vulnerabilidad de dependencias conocida o un hallazgo alto de ZAP no puede mergearse sin una excepción justificada.
- Las pruebas de contrato fallan en CI si un cliente deja de coincidir con el contrato publicado del otro grupo.
- Existe un reporte de k6 con resultados frente a los SLO definidos.
- Existe un reporte de evals del chatbot con los casos aprobados por spec; ningún caso muestra precios o datos que no provengan de las herramientas.
- Los hallazgos de la evaluación del frontend están corregidos o registrados como pendientes justificados.
- Todo el tráfico del frontend al backend pasa por el gateway.
- Un pago publica un evento en RabbitMQ y el consumidor, en un proceso distinto, lo procesa. Con el broker caído el evento queda en el outbox y se publica cuando vuelve.

## Verificaciones aplicables

- Backend: `ruff check .`, `mypy src`, `pytest`, `python scripts/check_modules.py` y `python scripts/export_openapi.py --check`.
- Frontend: `pnpm modules:check`, `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`.
- Specs: `npx @fission-ai/openspec validate --specs`.
- E2E: Playwright contra producción antes de la presentación.

## Riesgos

- CloudAMQP es un servicio externo más que puede fallar en la presentación. Mitigación: el outbox retiene los eventos.
- Una corrida de carga contra CloudAMQP agota la cuota mensual. Mitigación: performance solo contra RabbitMQ local.
- Los adjuntos (SPEC-23) viven en un volumen de Railway; se pierden si el servicio se recrea, como ocurrió con la cuenta anterior.
- No conviene desplegar justo antes de la presentación (un deploy reinicia el worker y el consumidor).
- El gateway agrega un salto de red y otro punto de falla delante del backend.
- Plazo corto (6 días desde el desglose): la fase 0 (ADR del broker y del gateway) bloquea H5-M2, H5-M3, H5-G2 y H5-G3.

## Progreso

- 2026-11-22: auditoría del estado para el Hito 5 y desglose de tareas. Verificado en Railway que solo Ventas está en fake. Decisión del broker: RabbitMQ en CloudAMQP. Reasignación: CI/CD y seguridad (H5-C1 a H5-C5) pasa a David; RabbitMQ (H5-M1 a H5-M4) pasa a Mathias. Pruebas de contrato (H5-I1) pasan a Sonny y ZAP (H5-C2) a Sebastian. Mathias revisa los PR abiertos al 2026-11-22 (H5-R1 a H5-R3); los autores corrigen lo que pida la revisión. Se agregan las evals del chatbot (H5-E1, Sonny) y la evaluación del frontend (H5-F1, Diego); el guion de la presentación no se trata como tarea.
- 2026-11-22: **H5-C0 hecha**. `API_PROXY_TARGET` agregada al entorno Preview de Vercel; los previews de #112 y #113 se volvieron a desplegar y ambos PR tienen los 13 checks en verde. Los previews usan el backend de producción, porque Railway tiene un solo entorno.
- 2026-11-24: **H5-P1 hecha** en [`docs/slo-performance.md`](../../docs/slo-performance.md): SLO de latencia p95, tasa de error y throughput para catálogo, chat y checkout, tomados de los RNF de las specs. **H5-P2 y H5-P3 en revisión** en el backend (rama `feat/h5-p2-k6-performance`): scripts de k6 en `tests/performance/k6/`, workflow manual `performance.yml` y `LLM_PROVIDER=fake` (`ScriptedLLMProvider`, rechazado en producción) para medir el chat sin OpenAI. Corrida local de 2 min por flujo: los tres cumplen todos los SLO (p95 máximo 259 ms, en el pago; 0 % de errores). Limitaciones: el checkout se mide en serie porque el fake de Seguridad tiene un solo cliente activo, y RabbitMQ entra en la corrida cuando lleguen H5-M2 y H5-M3.

- 2026-11-24: **H5-M1 redactada** (ADR-0030 nuevo; ADR-0010 y ADR-0011 actualizados con una sección de actualización; índice de ADR y nota en `c4.md`). Commit pendiente de confirmación del usuario. **H5-R1, H5-R2 y H5-R3 hechas**: backend #149 y #150 y frontend #112 y #113 mergeados; specs #36 mergeado y #30 cerrado.

- 2026-11-25: **H5-C5 hecha**. ADR-0024 pasa a **Aceptada** con fecha 2026-11-25; el índice de ADR y el conteo de `docs/arquitectura/README.md` quedan alineados. El diagrama `docs/diagrams/pipeline-ci-cd.{excalidraw,svg}` se rehízo con los jobs en vigor: lint/typecheck, unitarias, integración con migraciones, OpenAPI, module boundaries, Trivy + hadolint, SonarCloud, dependency-review, `pip-audit`/`pnpm audit` (advisory) y E2E; CodeQL, secret scanning con push protection y Dependabot van en la banda transversal. DAST con OWASP ZAP queda marcado como pendiente (H5-C2). Verificado con `python scripts/check_links.py` y `npx @fission-ai/openspec validate --specs`.

- 2026-11-25: **H5-C1 hecha**. `pip-audit` bloqueante en backend #162 (excepción puntual `PYSEC-2026-1845` de pytest, documentada) y `pnpm audit` bloqueante en frontend #134 (sin excepciones vigentes). **H5-C3 parcial, asignada a Mathias**: entorno `G3-Chatbot / production` creado en frontend con revisores Mathias y David; backend ya lo tenía; implementación del deploy por Actions en [frontend#139](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/139). El deploy de Vercel sigue fuera de GitHub Actions, así que la aprobación del entorno aún no bloquea el despliegue. **H5-C4 hecha**: `CODEOWNERS` solo `@MathiasTL` y `@Ankarmin`; ruleset “Code owners con bypass Mathias/David” exige 1 aprobación + code owner review al resto, con bypass `pull_request` para Mathias/David. Los checks siguen obligatorios (`enforce_admins=true`, `strict=true`); el bypass permite mergear sus PRs sin otra aprobación, no autoaprobarse. **H5-C5 hecha** (ver entrada anterior); el diagrama ya refleja `pip-audit` y `pnpm audit` como bloqueantes tras H5-C1.

- 2026-11-25: **Nueva tarea H5-P5, asignada a Mathias**: la corrida de k6 con RabbitMQ en Docker sale de H5-P2, porque depende del relay y el consumidor de H5-M2 y H5-M3, que son de Mathias y aún no existen. Así H5-P2 se cierra con los scripts y la corrida sin broker (backend #167, specs #57). Implementación en [backend#168](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/168).

- 2026-11-26: **Auditoría de alineación y limpieza de docs.** `main` quedó como placeholder de un único commit con solo `README.md` en backend, frontend y specs; `development` es la rama por defecto y la que despliega producción. Se corrigieron las referencias que aún promovían `development` a `main` (H5-X1, H5-C3, ADR-0020, ADR-0028, C4, runbook de adjuntos, privacidad y flujo de trabajo). H5-I2 se verifica hecha (no quedan `test.fixme`); H5-P2 queda hecha con la corrida local y H5-P3 queda implementada pero sin corrida registrada en Actions. Los pendientes reales se enlazan por issue en **Estado actual**; M5 sigue abierto y S4 se cerró el 2026-11-26.

- 2026-11-26: **H5-M3 (código) y H5-P5 hechas.** Backend #197 mergeó el consumidor RabbitMQ como proceso separado, el handler compartido, el healthcheck y los reintentos/DLX; también agregó RabbitMQ 4.1 y el consumidor a `performance.yml`. La corrida 45887721116 cumple los SLO con 1533 eventos consumidos, 0 reintentos/DLQ/fallos y checkout a 12,77 compras/s; el resultado quedó en `docs/slo-performance.md` (#78) y el consumidor en el C4 (#79). Falta el despliegue operativo del consumidor en Railway y el cambio de producción a `broker` (H5-M3/#177).

- 2026-11-26: **H5-C2 hecha.** Backend #210 agregó el job DAST con OWASP ZAP baseline/OpenAPI safe scan, reportes HTML/JSON/MD como artefacto, resumen en el Step Summary y gate bloqueante de alertas High integrado en el check `test`. El gate exige que toda excepción `IGNORE` esté documentada en `docs/seguridad/zap-exceptions.md`; además falla si ZAP no completa el escaneo.

- 2026-11-26: **H5-G1 redactada (en revisión en PR #81, issue #59).** [ADR-0031](../../docs/arquitectura/adr/ADR-0031-api-gateway-kong-oss.md) documenta Kong OSS en modo DB-less (`kong.yml`) en Railway delante del backend, con enmienda a ADR-0023 (`API_PROXY_TARGET` → Kong), actualización del índice de ADR, conteo en `docs/arquitectura/README.md` y nota en `c4.md`. Queda pendiente de aprobación y merge para cerrar H5-G1 y habilitar formalmente H5-G2 y H5-G3.

- 2026-11-27: **H5-Q1 e H5-I3 (documento base).** Se crean [`docs/casos-prueba-hito-5.md`](../../docs/casos-prueba-hito-5.md) con la matriz de casos por flujo y validación del DoD, y [`docs/evidencia-hito-5.md`](../../docs/evidencia-hito-5.md) con la evidencia de CI, integración, E2E, performance, mecanismo asíncrono y producción. Los contratos (#174), evals (#175) y Lighthouse (#156) quedan enlazados como pendientes; H5-I3 se actualiza cuando se cierren. #64 se cierra como supersedido (#96, frontend #162, backend #219).

## Siguiente paso

1. H5-M3: desplegar el consumidor como servicio Railway y pasar producción a `broker` cuando `/health` esté sano ([backend#177](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/177)); después H5-M4 ([specs#63](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/63)). H5-P5 ya está cerrada con el run 45887721116 y el SLO actualizado.
2. H5-G1: ADR de API Management ([specs#59](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/59)); después H5-G2/G3 ([backend#178](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/178), [#179](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/179); [frontend#142](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/142)).
3. H5-I1 (contratos) y H5-E1 (evals): [backend#174](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/174), [#175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175). La matriz de casos y la evidencia base ya están en `docs/casos-prueba-hito-5.md` y `docs/evidencia-hito-5.md`; se actualizan al cerrar contratos/evals.
4. H5-P4 (Lighthouse) y H5-F1 (evaluación integral): [frontend#144](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/144), [#145](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/145); H5-C3 (deploy por Actions desde `development`): [frontend#139](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/issues/139).
5. SPEC-23/L2: bucket y variables ([specs#53](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/53)); fail-closed ya implementado en backend #198.
6. H5-X1: verificar producción sobre `development` ([backend#183](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/183)).
