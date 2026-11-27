# Pipeline de CI en GitHub

Este documento describe el pipeline vigente de los tres repositorios y cómo operarlo. La decisión está en [ADR-0032](arquitectura/adr/ADR-0032-pipeline-ci-por-alcance.md); el gate de herramientas y seguridad sigue en [ADR-0024](arquitectura/adr/ADR-0024-calidad-y-seguridad-en-el-pipeline.md).

## Reglas comunes

- **Un check requerido por repo:** `test` en backend, `check` en frontend. El job agregador corre siempre (`if: always()`) y falla si un job que el alcance pidió no terminó en `success`. Un job omitido a propósito no cuenta como aprobado.
- **Cancelación:** `concurrency.cancel-in-progress` cancela el run anterior de la misma rama o PR.
- **Alcance:** un job `scope` calcula el diff contra el merge-base de `development`, mapea rutas a módulos y cierra el DAG de `modules.manifest.json` hacia dependientes. Si no puede resolver la base, ejecuta todo.
- **Etiqueta `ci:full`:** fuerza el alcance completo y los jobs caros en un PR (`dast`, `gateway-integration`, `e2e`).
- **Schedule semanal:** lunes 08:00 UTC backend, 09:00 UTC frontend. Corre todo, incluido `pip-audit`/`pnpm audit` y los E2E.
- **Sin secretos nuevos:** `SONAR_TOKEN` ya existe en backend y frontend; `GITHUB_TOKEN` es automático. No se usan tokens de GitLab, Nexus ni registry.
- **Ramas protegidas:** `development` exige el check `test` (backend), `check` (frontend) u `OpenSpec y enlaces` (specs), con rama actualizada, conversación resuelta y sin force push; `enforce_admins` está activo.

## Backend

```text
scope
  ├─ validate (ruff, mypy, módulos, OpenAPI, import-app) ── reporte 90 días
  ├─ unit-tests (suite completa, cobertura)
  ├─ integration-tests (matriz por shard: PostgreSQL + RabbitMQ por leg)
  │     └─ coverage-merge
  ├─ docker (solo si cambia código/Dockerfile)
  ├─ security (solo si cambian requirements; schedule semanal)
  ├─ dast + gateway-integration (push, schedule o label ci:full)
  ├─ dependency-review (PR)
  └─ specs (PR)
        └─ sonar (cobertura + quality gate)
              └─ test (agregador)
notify (si falla, comenta el PR)
```

- Los shards de integración se generan con `fromJSON(needs.scope.outputs.integration_shards)`; si el alcance es un solo módulo, se crea un solo leg.
- `coverage-merge` combina los `.coverage.<shard>` con `coverage combine` y publica `coverage-integration.xml`.
- SonarCloud analiza el PR de forma nativa; no hay ramas `mr-<IID>`.

## Frontend

```text
scope
  ├─ validate (eslint, tsc, modules:check + contrato OpenAPI)
  ├─ unit-tests (91 tests, cobertura)
  ├─ build (next build)
  ├─ security (solo si cambia el lockfile; schedule semanal)
  ├─ e2e (push, schedule o label ci:full)
  ├─ dependency-review (PR)
  └─ specs (PR)
        └─ sonar
              └─ check (agregador)
notify (si falla, comenta el PR)
```

No hay `nx affected`: el build de Next.js es monolítico y el alcance solo decide si corre.

## Specs

`validate` ejecuta OpenSpec y `scripts/check_links.py`. Si falla en un PR, `notify` publica (o actualiza) un comentario con el enlace al run.

## SonarCloud

- El escaneo espera el quality gate (`sonar.qualitygate.wait=true`).
- Además, el pipeline tiene un **gate estricto propio**: consulta `/api/issues/search` y falla si el PR o la rama introduce un issue de severidad `MINOR` o superior. Si la API no responde, **falla cerrado**.
- Para bloquear también los `INFO`, cambia `--fail-on-severity MINOR` por `--fail-on-severity INFO` en el workflow. El default `MINOR` evita bloquear hallazgos puramente informativos.
- Si el gate falla, `scripts/ci/sonar_gate_report.py` (backend) o `sonar-gate-report.mjs` (frontend) publica condiciones e issues en el job summary y en `sonar-gate-reports` (30 días).
- El quality gate de la UI sigue siendo necesario para cobertura de *new code* ≥ 80 %, duplicación ≤ 3 % y hotspots; el gate estricto del pipeline cubre los issues nuevos.

## Verificación local (para colaboradores)

El CI calcula el alcance: un PR que solo toca documentación no ejecuta tests, Docker ni Sonar. Un PR de código ejecuta lo que su diff justifica. Para forzar todo en un PR, agrega la etiqueta `ci:full`.

Backend:

```bash
# Reproduce el job `validate` completo
python scripts/ci/run_validators.py

# Qué va a correr el CI para tu rama
python scripts/ci/scope.py --base origin/development --json

# Suite unitaria y, si tienes PostgreSQL 18 + RabbitMQ locales:
pytest tests/unit -q
alembic upgrade head
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_test \
RABBITMQ_TEST_URL=amqp://guest:guest@localhost:5672/ \
pytest tests/integration -q
```

Frontend:

```bash
# Reproduce el job `validate` (eslint + tsc + modules:check)
OPENAPI_PATH=../G3-Chatbot-backend/docs/openapi.json \
  node scripts/ci/run-validators.mjs

# Qué va a correr el CI para tu rama
node scripts/ci/scope.mjs --base origin/development --json
```

> **Windows:** el test `test_consumer_entrypoint.py::test_sigterm_stops_the_consumer_and_returns_cleanly` falla en Windows porque `asyncio` no implementa `add_signal_handler` allí; el CI usa Ubuntu. Para reproducir el CI en Windows, usa WSL o deselecciona ese test:
>
> `pytest tests/unit -q --deselect tests/unit/test_consumer_entrypoint.py::test_sigterm_stops_the_consumer_and_returns_cleanly`

No necesitas `SONAR_TOKEN` localmente: Sonar se ejecuta solo en CI. Tampoco necesitas credenciales de Railway, Vercel ni del broker; los tests de integración usan contenedores locales.

## Artefactos y retención

| Artefacto | Retención |
|---|---|
| `validation-report` | 90 días |
| `coverage-unit` / `coverage-frontend` | 7 días (por defecto) |
| `coverage-integration` | 7 días (por defecto) |
| `sonar-gate-reports` | 30 días |
| `ci-failure-report` | 30 días |
| `dast-zap-report` | 7 días (por defecto) |
| `playwright-artifacts` | 7 días |

## Cuándo forzar el pipeline completo

- Cambios en `src/shared/**`, migraciones, `modules.manifest.json`, `requirements.txt`, `pnpm-lock.yaml`, configuración de build/test o workflows: el `scope` ya fuerza alcance completo.
- Cambios en `gateway/**`, Docker o contratos que quieras validar contra el stack real: agrega la etiqueta `ci:full` al PR.
- Antes de un release: ejecuta el workflow manualmente con `full: true` o espera el schedule.
