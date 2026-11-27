# Evidencia del Hito 5

> Tarea **H5-I3** de [`odd/tasks/hito-5.md`](../odd/tasks/hito-5.md), issue [#61](https://github.com/Taller-SW-Web/G3-Chatbot-specs/issues/61).
> Fecha de corte: **2026-11-27** (UTC). Entorno de referencia: `development` en backend, frontend y specs; producción sobre `development`.

Este documento reúne la evidencia verificable del Hito 5. No repite los casos: la matriz operativa está en [`casos-prueba-hito-5.md`](casos-prueba-hito-5.md). Cuando una sección aún no tiene evidencia, se indica el issue que la va a producir; no se marca como cumplida.

## 1. Resumen

| Entregable | Estado | Evidencia |
|---|---|---|
| CI/CD y seguridad | ✅ | Backend #210 (DAST), #212/#214/#215 (CI); frontend #152; specs #220; runs de `development` |
| Pruebas de integración y E2E | ✅ | Backend y frontend CI; `tests/integration`, `tests/e2e` |
| Pruebas de contrato G7/G6/G2/G5 | ✅ | `tests/contract/`, job bloqueante `contract`; backend #226–#229, run 46050322098 |
| Evals del chatbot | ✅ | Backend #230; primera corrida real 7/9 con fallos documentados en #175, [run 46073219673](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/46073219673); follow-up #258 |
| Performance | ✅ | [`slo-performance.md`](slo-performance.md), run 45887721116 |
| Lighthouse y accesibilidad | ✅ | Frontend #180, job `lighthouse`, run 46048924659 |
| API Management | 🟡 | ADR-0031 y código #211/#214 mergeados; despliegue #178/#179 |
| Mecanismo asíncrono | ✅ | [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md); #215 mergeado |
| Casos de prueba y DoD | ✅ | [`casos-prueba-hito-5.md`](casos-prueba-hito-5.md) |
| Producción | 🟡 | Backend `/health` 200; gateway y cierre operativo #178/#179 |

## 2. CI/CD y seguridad

| Evidencia | Enlace |
|---|---|
| Backend `development`: lint, tipos, unitarias, contrato, integración, OpenAPI, módulos, DAST, Trivy, Sonar y gate `test` | [run 46050322098](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/46050322098) · `11a25be` |
| Frontend `development`: lint/typecheck, unitarias, Lighthouse, E2E, build, módulos, Sonar y Vercel | [run 46048924659](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/46048924659) · `a99886e` |
| Specs `development`: OpenSpec y enlaces | [run 45936461820](https://github.com/Taller-SW-Web/G3-Chatbot-specs/actions/runs/45936461820) · `c4340c5` |
| DAST con OWASP ZAP y gate de alertas High | Backend #210, job `DAST (OWASP ZAP)` |
| Ruleset y CODEOWNERS en backend/frontend | H5-C4, ADR-0024; `.github/CODEOWNERS` |

La protección de rama de backend y frontend exige el check `test`/`check`, 1 aprobación y code owner review; specs #220 restringe los PRs a Mathias y David.

## 3. Integración backend

| Suite | Archivos representativos | Resultado |
|---|---|---|
| PostgreSQL real | `tests/integration/mod_catalog/`, `tests/integration/mod_chat/`, `tests/integration/mod_checkout/`, `tests/integration/mod_orders/` | Job `Migrations and integration tests` en verde |
| RabbitMQ | `tests/integration/test_outbox_consumer_rabbitmq.py`, `test_rabbitmq_outbox_publisher.py` | Job de integración en verde; cubre publicación, consumo, reintentos y reconexión |
| Kong | `tests/integration/test_gateway_kong.py` | Job `Gateway integration (Kong OSS)` en verde; cubre `/health`, `/api/v1`, SSE, adjuntos, 1 MB/6 MB, OpenAPI y rate limit |

## 4. E2E frontend

| Suite | Qué cubre | Evidencia |
|---|---|---|
| `tests/e2e/smoke.spec.ts` | Flujo principal: catálogo, carrito, checkout, pedido y postventa | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), job `E2E` |
| `tests/e2e/chat.real.spec.ts` | Chat, SSE e historial | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), job `E2E` |
| `tests/e2e/home.spec.ts` | Home, ofertas y navegación | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), job `E2E` |
| `tests/e2e/gateway.spec.ts` | Mismo origen y cabeceras del gateway cuando `PLAYWRIGHT_VERIFY_GATEWAY=true` | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), job `E2E`; verificación manual contra Vercel en #142 |
| `tests/e2e/mobile-first.spec.ts` | Viewports móviles y zonas táctiles | [run 45925602758](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/45925602758), job `E2E` |

Los E2E corren con los módulos externos en `fake` (ADR-0022) y sin LLM real; los recorridos contra el entorno real están en `chat.real.spec.ts` y en la verificación manual de #142/#183.

## 5. Performance

| Evidencia | Enlace |
|---|---|
| SLO y resultados de k6 | [`slo-performance.md`](slo-performance.md) |
| Corrida con RabbitMQ y consumidor (H5-P5) | [run 45887721116](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/45887721116) |
| Resultado | 1533 eventos consumidos, 0 reintentos/DLQ/fallos; checkout 12,77 compras/s |

Lighthouse CI (H5-P4) corre en el gate `check` con el preset móvil y presupuestos bloqueantes de LCP, CLS, peso JS/total y accesibilidad, más TBT como proxy de INP. La excepción de CI 4800/350 está aprobada y documentada en [`rendimiento-lighthouse.md`](../../G3-Chatbot-frontend/docs/rendimiento-lighthouse.md). Evidencia: frontend #180, [run 46048924659](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/actions/runs/46048924659), job `Lighthouse CI`; el reporte se publica como artefacto `lighthouse-reports`.

## 6. Mecanismo asíncrono

La evidencia completa está en [`evidencia-mecanismo-asincrono.md`](evidencia-mecanismo-asincrono.md):

- Diagrama outbox → RabbitMQ → consumidor.
- Pago `PED-2026-00094` publicado y consumido en procesos separados; `message_id` coincide con la fila del outbox.
- Prueba con el broker caído: el outbox retiene y publica al volver, sin perder eventos.
- Corrección de reconexión del consumidor en backend #215, mergeada y desplegada; logs de `consumer_started` y `event=consumed`.

## 7. Contratos y evals

Contratos G7/G6/G2/G5: cerrados con backend #226–#229. `tests/contract/` fija los OpenAPI publicados con hash en `contracts.lock.json`, los clientes se prueban con `respx` y el job `contract` es bloqueante dentro de `test`; el drift semanal vive en `contract-drift.yml`. Evidencia: [run 46050322098](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/46050322098), job `Contract tests`.

Evals: la suite y el workflow están en `development` (backend #230): 9 casos, reporte `evals-report.json`, corrida manual o nocturna. `LLM_API_KEY` está configurada en el environment `evals` (backend #245).

| Corrida | Modelo | Resultado |
|---|---|---|
| [run 46073219673](https://github.com/Taller-SW-Web/G3-Chatbot-backend/actions/runs/46073219673) (commit `11a25be`) | `gpt-6-luna` (el de producción) | 7/9 aprobados. Ninguna respuesta inventa precios, stock ni datos |
| run 46072770923 | `gpt-4o-mini` (default del workflow) | Descartada: todas las llamadas al LLM fallaron y el chat cayó en modo degradado |

Fallos de la corrida válida, documentados caso por caso en [backend #175](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/175):

1. `test_search_reference_conversation`: el modelo eligió `recomendar_productos` (con `talla: 42`) en vez de `buscar_productos`.
2. `test_prices_are_only_quoted_from_tool_data`: buscó el producto pero no llamó a `ver_detalle_producto`; no citó ningún precio.

Ambos son de elección de herramienta, no de datos inventados. El default incompatible del workflow y los casos degradados que pasan como aprobados se siguen en [backend #258](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/258).

## 8. Producción

| Verificación | Resultado |
|---|---|
| `GET https://g3-chatbot-backend.up.railway.app/health` | `200` |
| Backend y consumer en Railway | Ambos `Online`; consumer sin dominio público |
| Gateway Kong | Código mergeado (#211/#214); falta desplegar/verificar (#178/#179) |
| Adjuntos | `ATTACHMENT_STORAGE=local` sobre volumen; el cierre operativo y el checklist están en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27); specs #53 quedó como tracking documental cerrado |

## 9. Limitaciones conocidas

- **Evals**: la corrida real da 7/9; los 2 fallos son de elección de herramienta (backend #175). El workflow debe correr con `llm_model=gpt-6-luna` hasta cerrar backend #258.
- **Lighthouse** ya está en el gate `check` (H5-P4 cerrado, frontend #180); la deuda de LCP/TBT en CI sigue en frontend #164.
- **Gateway** no está desplegado en Railway; H5-G2/G3 no están operativos.
- **Adjuntos** en producción usan almacenamiento local y volumen efímero; el cierre operativo y el checklist están en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27).
- **SMTP** no está configurado en producción; los correos usan `FakeEmailSender`.
- **Módulos externos** se simulan con `fake` en CI y en la demo; las pruebas reales con G5/G6/G7 se registran aparte.

## 10. Cómo reproducir

```bash
# Backend
pytest tests/unit -q
pytest tests/integration -q
python scripts/check_modules.py
python scripts/export_openapi.py --check

# Frontend
pnpm test
pnpm test:e2e
pnpm modules:check
pnpm build

# Specs
python scripts/check_links.py
npx --yes @fission-ai/openspec validate --specs
```

Las corridas de CI enlazadas en §2 son la referencia para el Hito 5; las locales sirven para reproducir un caso concreto.
