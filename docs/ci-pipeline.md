# Pipeline de CI en GitHub

Este documento describe el pipeline vigente de los tres repositorios y cómo operarlo. La decisión está en [ADR-0032](arquitectura/adr/ADR-0032-pipeline-ci-por-alcance.md); el gate de herramientas y seguridad sigue en [ADR-0024](arquitectura/adr/ADR-0024-calidad-y-seguridad-en-el-pipeline.md).

## Reglas comunes

- **Un check requerido por repo:** `test` en backend, `check` en frontend. El job agregador corre siempre (`if: always()`) y falla si un job que el alcance pidió no terminó en `success`. Un job omitido a propósito no cuenta como aprobado.
- **Cancelación:** `concurrency.cancel-in-progress` cancela el run anterior de la misma rama o PR.
- **Alcance:** un job `scope` calcula el diff contra el merge-base de `development`, mapea rutas a módulos y cierra el DAG de `modules.manifest.json` hacia dependientes. Si no puede resolver la base, ejecuta todo.
- **Etiqueta `ci:full`:** fuerza el alcance completo y los jobs caros en un PR (`dast`, `gateway-integration`, `e2e`).
- **Schedule semanal:** lunes 08:00 UTC backend, 09:00 UTC frontend. Corre todo, incluido `pip-audit`/`pnpm audit` y los E2E.
- **Sin secretos nuevos:** `SONAR_TOKEN` ya existe en backend y frontend; `GITHUB_TOKEN` es automático. No se usan tokens de GitLab, Nexus ni registry.

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
- Si el gate falla, `scripts/ci/sonar_gate_report.py` (backend) o `sonar-gate-report.mjs` (frontend) consulta la API y publica condiciones e issues en el job summary y en un artefacto.
- El gate recomendado para bloquear todo lo nuevo es: cobertura de *new code* ≥ 80 %, duplicación ≤ 3 %, 0 blocker/critical/major y hotspots revisados al 100 %. Se configura en la UI de SonarCloud; el pipeline no lo crea.

## Comandos locales

Backend:

```bash
python scripts/ci/scope.py --base origin/development --json
python scripts/ci/run_validators.py
python scripts/ci/run_validators.py --list
```

Frontend:

```bash
node scripts/ci/scope.mjs --base origin/development --json
node scripts/ci/run-validators.mjs
node scripts/ci/run-validators.mjs --list
```

## Artefactos y retención

| Artefacto | Retención |
|---|---|
| `validation-report` | 90 días |
| `coverage-unit` / `coverage-frontend` | 7 días (por defecto) |
| `coverage-integration` | 7 días (por defecto) |
| `sonar-gate-report` | 30 días |
| `ci-failure-report` | 30 días |
| `dast-zap-report` | 7 días (por defecto) |
| `playwright-artifacts` | 7 días |

## Cuándo forzar el pipeline completo

- Cambios en `src/shared/**`, migraciones, `modules.manifest.json`, `requirements.txt`, `pnpm-lock.yaml`, configuración de build/test o workflows: el `scope` ya fuerza alcance completo.
- Cambios en `gateway/**`, Docker o contratos que quieras validar contra el stack real: agrega la etiqueta `ci:full` al PR.
- Antes de un release: ejecuta el workflow manualmente con `full: true` o espera el schedule.
