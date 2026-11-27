# Pipeline de CI en GitHub

Este documento describe el pipeline vigente de los tres repositorios. La ejecución full está decidida en [ADR-0033](arquitectura/adr/ADR-0033-pipeline-full-en-cada-run.md); el alcance y el costo original siguen explicados en [ADR-0032](arquitectura/adr/ADR-0032-pipeline-ci-por-alcance.md), y el gate de herramientas/seguridad en [ADR-0024](arquitectura/adr/ADR-0024-calidad-y-seguridad-en-el-pipeline.md).

## Reglas comunes

- **Full en cada PR/push:** `scope` calcula el diff solo para el reporte y para `sonar_sources_changed`; no decide qué jobs corren. Todos los jobs de código se ejecutan en cada evento.
- **Checks requeridos:** `test` + `Analyze (python)` en backend; `check` + `Analyze (javascript-typescript)` en frontend; `OpenSpec y enlaces` en specs.
- **Cancelación:** un push nuevo a un PR cancela el run anterior. Los runs de `push` y `schedule` no se cancelan entre sí.
- **Gates de PR:** `specs` y `dependency-review` solo tienen sentido en PR; en `push` corren y terminan verdes con un no-op explícito, para que no aparezcan como `skipped`.
- **Notificación:** `notify` corre siempre. En fallo publica/actualiza el comentario con jobs y logs; en éxito actualiza el mismo comentario a “CI recuperado”.
- **Sonar:** el gate de la UI tiene condiciones globales y de *new code* (cobertura ≥ 80 %, duplicación ≤ 3 %, blocker/critical/major/minor = 0 y hotspots revisados). El pipeline además falla cerrado si el PR toca `src/` y Sonar no publica las medidas de new code.
- **Sin secretos nuevos:** `SONAR_TOKEN` existe en Actions y en Dependabot para backend/frontend; `GITHUB_TOKEN` es automático.
- **Ramas protegidas:** `development` exige los checks anteriores, rama actualizada, conversación resuelta, sin force push/borrado y `enforce_admins`. Los PRs de forks requieren aprobación (`all_external_contributors`).
- **Supply-chain:** todas las acciones están fijadas por SHA y `sha_pinning_required=true`.
- **`workflow_dispatch`:** en backend/frontend solo se permite en `development`; siempre corre full.

## Backend

```text
scope
  ├─ validate (ruff, mypy, módulos, OpenAPI, import) ── reporte 90 días
  ├─ unit-tests (suite completa, cobertura)
  ├─ integration-tests (matriz por shard: PostgreSQL + RabbitMQ por leg)
  │     └─ coverage-merge
  ├─ docker (hadolint, Trivy fs, build backend/gateway, Trivy imágenes)
  ├─ security (pip-audit)
  ├─ dast (OWASP ZAP)
  ├─ gateway-integration (Kong OSS)
  ├─ dependency-review (PR; push no-op)
  ├─ specs (PR; push no-op)
  └─ sonar ── test (agregador)
notify (siempre: fallo o recuperado)
```

- Los shards de integración se generan con `fromJSON(needs.scope.outputs.integration_shards)`. Como el modo es full, se ejecutan todos: `mod_catalog`, `mod_chat`, `mod_checkout`, `mod_orders` y `core`.
- El shard `core` ejecuta todos los `tests/integration/test_*.py` raíz; los tests de Kong se saltan si no hay `GATEWAY_TEST_URL` y el job `gateway-integration` los ejecuta con Kong.
- `coverage-merge` combina los `.coverage.<shard>` y publica `coverage-integration.xml`.
- Docker escanea también la imagen backend, no solo la de gateway.

## Frontend

```text
scope
  ├─ validate (eslint, tsc, modules:check, tests de scope y helpers)
  ├─ unit-tests (561 tests, cobertura)
  ├─ build (next build)
  ├─ security (pnpm audit)
  ├─ e2e (stack real con backend fake)
  ├─ dependency-review (PR; push no-op)
  ├─ specs (PR; push no-op)
  └─ sonar ── check (agregador)
notify (siempre: fallo o recuperado)
```

No hay `nx affected`: el build de Next.js es monolítico. El job `validate` agrupa lint, tipos y `modules:check`; `pnpm test` vive en `unit-tests`.

## Specs

`OpenSpec y enlaces` ejecuta OpenSpec y `scripts/check_links.py`. Si falla en un PR, `notify` publica el enlace al run; en push no hay PR y solo deja evidencia en el summary.

## SonarCloud

- El escaneo espera el quality gate (`-Dsonar.qualitygate.wait=true` pasado por el workflow).
- La UI del gate “G3 Chatbot” tiene condiciones globales y de *new code*: cobertura nueva ≥ 80 %, duplicación nueva ≤ 3 %, blocker/critical/major/minor nuevos = 0 y hotspots nuevos revisados al 100 %.
- El pipeline consulta `/api/issues/search` y `/api/measures/component`; en PR bloquea `MINOR+`, y si el PR toca `src/` exige que Sonar publique `new_lines`/`new_lines_to_cover`; en push usa `CRITICAL` para no bloquear el deploy por deuda `MAJOR` heredada.
- Un cambio en `sonar-project.properties` requiere `ci:sonar-config` y revisión de owner.
- Los helpers con token se ejecutan desde el commit base cuando existe; el PR de bootstrap usa su copia una vez.

## Verificación local (para colaboradores)

El CI corre full: un PR de documentación también ejecuta tests, Docker, DAST, gateway y Sonar. Para reproducir los gates:

Backend:

```bash
python scripts/ci/run_validators.py
pip install openapi-spec-validator==0.9.0
openapi-spec-validator docs/openapi.json
pytest tests/unit -q

# Integración: PostgreSQL 18 + RabbitMQ locales
alembic upgrade head
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chatbot_test \
RABBITMQ_TEST_URL=amqp://guest:guest@localhost:5672/ \
pytest tests/integration -q

# Qué va a correr el CI (siempre full)
python scripts/ci/scope.py --base origin/development --event pull_request --json
```

Frontend:

```bash
OPENAPI_PATH=../G3-Chatbot-backend/docs/openapi.json \
  node scripts/ci/run-validators.mjs
node scripts/ci/scope.mjs --base origin/development --event pull_request --json
```

En PowerShell, define `OPENAPI_PATH` en una línea aparte antes de invocar Node.

> **Windows:** `test_consumer_entrypoint.py::test_sigterm_stops_the_consumer_and_returns_cleanly` falla porque `asyncio` no implementa `add_signal_handler` allí; el CI usa Ubuntu. Usa WSL o deselecciona ese test:
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

## Dependabot y forks

- Los PRs de Dependabot usan el Dependabot secret `SONAR_TOKEN`, configurado en backend y frontend. Si falta, Sonar falla cerrado.
- Los PRs de fork no reciben secretos: el PR original no puede quedar verde; un maintainer recrea el cambio en una rama del repo base, valida ahí y mergea ese PR.
- No se usa `pull_request_target` para ejecutar código del PR con secretos.
