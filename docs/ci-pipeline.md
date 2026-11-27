# Pipeline de CI en GitHub

Este documento describe el pipeline vigente de los tres repositorios y cómo operarlo. La decisión está en [ADR-0032](arquitectura/adr/ADR-0032-pipeline-ci-por-alcance.md); el gate de herramientas y seguridad sigue en [ADR-0024](arquitectura/adr/ADR-0024-calidad-y-seguridad-en-el-pipeline.md).

## Reglas comunes

- **Un check requerido por repo:** `test` en backend, `check` en frontend. El job agregador corre siempre (`if: always()`) y falla si un job que el alcance pidió no terminó en `success`. Un job omitido a propósito no cuenta como aprobado.
- **Cancelación:** un push nuevo a un PR cancela el run anterior. Los runs de `push` y `schedule` no se cancelan entre sí: el semanal debe terminar aunque llegue un push.
- **Alcance:** un job `scope` calcula el diff contra el merge-base de `development`, cuenta también borrados y renames, mapea rutas a módulos y cierra el DAG de `modules.manifest.json` hacia dependientes. Si no puede resolver la base, ejecuta todo.
- **Etiqueta `ci:full`:** fuerza el alcance completo y los jobs caros en un PR (`dast`, `gateway-integration`, `e2e`, audit). Añadirla relanza el workflow (`labeled` está en los triggers).
- **Schedule semanal:** lunes 08:00 UTC backend, 09:00 UTC frontend. Corre todo, incluido `pip-audit`/`pnpm audit` y los E2E.
- **Sin secretos nuevos:** `SONAR_TOKEN` ya existe en backend y frontend; `GITHUB_TOKEN` es automático. No se usan tokens de GitLab, Nexus ni registry.
- **Sonar sin token:** si un PR necesita Sonar y no hay `SONAR_TOKEN`, el job falla. Los PRs de fork no reciben secretos: un maintainer debe ejecutar el análisis en una rama del repo base antes de mergear. Para Dependabot, configura el Dependabot secret `SONAR_TOKEN`.
- **Ramas protegidas:** `development` exige el check `test` (backend), `check` (frontend) u `OpenSpec y enlaces` (specs), con rama actualizada, conversación resuelta y sin force push; `enforce_admins` está activo. Los PRs de forks requieren aprobación de un maintainer (`all_external_contributors`).
- **Supply-chain:** todas las acciones están fijadas por SHA y la organización exige SHA pinning (`sha_pinning_required=true`).

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
        └─ sonar (cobertura + quality gate) ── test (agregador)
notify (si falla, comenta el PR)
```

- Los shards de integración se generan con `fromJSON(needs.scope.outputs.integration_shards)`; si el alcance es un solo módulo, se crea un solo leg. El shard `core` ejecuta todos los `tests/integration/test_*.py` raíz.
- `coverage-merge` combina los `.coverage.<shard>` con `coverage combine` y publica `coverage-integration.xml`.
- SonarCloud analiza el PR de forma nativa; no hay ramas `mr-<IID>`.

## Frontend

```text
scope
  ├─ validate (eslint, tsc, modules:check + contrato OpenAPI)
  ├─ unit-tests (561 tests, cobertura)
  ├─ build (next build)
  ├─ security (lockfile, package.json, schedule o ci:full)
  ├─ e2e (push, schedule o label ci:full)
  ├─ dependency-review (PR)
  └─ specs (PR)
        └─ sonar ── check (agregador)
notify (si falla, comenta el PR)
```

No hay `nx affected`: el build de Next.js es monolítico y el alcance solo decide si corre. El job `validate` agrupa `eslint`, `tsc` y `modules:check`; `pnpm test` vive en `unit-tests`, no en `validate`.

## Specs

`validate` ejecuta OpenSpec y `scripts/check_links.py`. Si falla en un PR, `notify` publica (o actualiza) un comentario con el enlace al run.

## SonarCloud

- El escaneo espera el quality gate (`sonar.qualitygate.wait=true`) y el workflow lo fuerza con `-Dsonar.qualitygate.wait=true`, para que un PR no pueda desactivarlo editando `sonar-project.properties`.
- Además, el pipeline tiene un **gate estricto propio**: consulta `/api/issues/search` y, cuando SonarCloud expone las medidas de *new code* al token del proyecto, exige cobertura ≥ 80 % y duplicación ≤ 3 %. Falla si el PR introduce un issue `MINOR` o superior. En `push` a `development` el umbral de issues es `CRITICAL` para no tumbar el deploy por deuda `MAJOR` heredada; los `CRITICAL`/`BLOCKER` sí bloquean. Si la API no responde o falta el token, **falla cerrado**. La cobertura global de la UI sigue siendo el gate principal mientras no se añada `new_coverage` al quality gate de SonarCloud.
- Un cambio en `sonar-project.properties` requiere la etiqueta `ci:sonar-config` (revisión de un owner). Sin ella, el job falla.
- Para bloquear también los `INFO` en PR, cambia `threshold=MINOR` por `threshold=INFO` en el workflow. El default `MINOR` evita bloquear hallazgos puramente informativos.
- Si el gate falla, el helper (desde el commit base cuando existe) publica condiciones e issues en el job summary y en `sonar-gate-reports` (30 días).

## Verificación local (para colaboradores)

El CI calcula el alcance: un PR que solo toca documentación no ejecuta tests, Docker ni Sonar. Un PR de código ejecuta lo que su diff justifica. Para forzar todo en un PR, agrega la etiqueta `ci:full`.

Backend:

```bash
# Reproduce el job `validate` (ruff, mypy, módulos, OpenAPI, import)
python scripts/ci/run_validators.py

# Qué va a correr el CI para tu rama (con el mismo evento que un PR)
python scripts/ci/scope.py --base origin/development --event pull_request --json

# `pytest` vive en el job `unit-tests`, no en `validate`:
pytest tests/unit -q

# Integración: PostgreSQL 18 + RabbitMQ locales
alembic upgrade head
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_test \
RABBITMQ_TEST_URL=amqp://guest:guest@localhost:5672/ \
pytest tests/integration -q
```

En PowerShell:

```powershell
$env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_test"
$env:RABBITMQ_TEST_URL="amqp://guest:guest@localhost:5672/"
pytest tests/integration -q
```

Frontend:

```bash
# Reproduce el job `validate` (eslint + tsc + modules:check + tests de scope)
OPENAPI_PATH=../G3-Chatbot-backend/docs/openapi.json \
  node scripts/ci/run-validators.mjs

# Qué va a correr el CI para tu rama (con el mismo evento que un PR)
node scripts/ci/scope.mjs --base origin/development --event pull_request --json
```

En PowerShell, define `OPENAPI_PATH` en una línea aparte antes de invocar Node.

> **Windows:** el test `test_consumer_entrypoint.py::test_sigterm_stops_the_consumer_and_returns_cleanly` falla en Windows porque `asyncio` no implementa `add_signal_handler` allí; el CI usa Ubuntu. Para reproducir el CI en Windows, usa WSL o deselecciona ese test:
>
> `pytest tests/unit -q --deselect tests/unit/test_consumer_entrypoint.py::test_sigterm_stops_the_consumer_and_returns_cleanly`

No necesitas `SONAR_TOKEN` localmente: Sonar se ejecuta solo en CI. Tampoco necesitas credenciales de Railway, Vercel ni del broker; los tests de integración usan contenedores locales.

## Artefactos y retención

| Artefacto | Retención |
|---|---|
| `validation-report` | 90 días |
| `coverage-unit` / `coverage-frontend` | 7 días |
| `coverage-integration` | 7 días |
| `sonar-gate-reports` | 30 días |
| `ci-failure-report` | 30 días |
| `dast-zap-report` | 7 días |
| `playwright-artifacts` | 7 días |

## Cuándo forzar el pipeline completo

- Cambios en `src/shared/**`, migraciones, `modules.manifest.json`, `requirements.txt`, `pnpm-lock.yaml`, configuración de build/test o workflows: el `scope` ya fuerza alcance completo.
- Cambios en `gateway/**`, Docker o contratos que quieras validar contra el stack real: agrega la etiqueta `ci:full` al PR (relanza el workflow).
- Antes de un release: ejecuta el workflow manualmente (`workflow_dispatch` siempre corre completo) o espera el schedule.
- `main` es un placeholder de un commit: no se promueve ni se despliega desde ahí. Los checks de `main` existen solo para bloquear PRs accidentales.
