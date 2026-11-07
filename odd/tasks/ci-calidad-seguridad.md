# CI/CD con calidad, seguridad y pruebas

## Objetivo

Llevar el pipeline de los dos repositorios de "compila y pasa tests" a un **gate de calidad real**: que mida errores, seguridad, cobertura, calidad estructural (code smells, duplicación, complejidad) y flujos críticos, con un único check requerido que bloquee merge y despliegue. Todo el stack propuesto es de coste cero porque los tres repositorios son **públicos**.

## Estado actual (verificado el 2026-11-07)

### Lo que ya funciona

- **Gate único** en ambos repos: `test` (backend) y `check` (frontend) como único check requerido, con jobs paralelos detrás ([#88](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/88) y [#61](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/pull/61)).
- **Backend**: `Lint` (ruff), `Unit tests`, `Export OpenAPI` (artifact), `Migrations and integration tests` (PostgreSQL 18, migraciones up/down/up).
- **Frontend**: `Lint and type check`, `Unit tests`, `Build`.
- **Deploy condicionado**: Railway con *Wait for CI* y pre-deploy `alembic upgrade head`; Vercel con *Deployment Checks* que exige `check`.
- **Ramas protegidas**: `main` y `development`, PR + 1 aprobación + check requerido + descarte de aprobaciones con commits nuevos.

### Hallazgos

| Falta | Consecuencia hoy |
|---|---|
| `permissions`, `concurrency`, `timeout-minutes` | Token con permisos de más, runs viejos que no se cancelan, jobs que pueden colgarse 6 h |
| SAST (CodeQL) | Vulnerabilidades de código no detectadas |
| SCA (Dependabot, Dependency Review, audits) | CVE en `requirements.txt`/`pnpm-lock.yaml` sin aviso |
| Secret scanning / push protection | Un secreto commiteado no se bloquea |
| Cobertura | No se sabe si una PR baja la calidad de tests |
| **Calidad estructural** (Sonar) | Code smells, duplicación, complejidad y deuda técnica no se miden |
| Contenedor | `Dockerfile` sin hadolint/Trivy |
| E2E | `tests/e2e/smoke.spec.ts` tiene 7 `test.fixme` y ningún workflow ejecuta Playwright |
| Contrato | El `openapi.json` se exporta pero no se valida ni se compara |
| Deploy | Sin aprobación de entorno ni smoke post-deploy ni rollback probado |

## Alcance

- Workflows de ambos repositorios y configuración de seguridad de GitHub.
- Medición de calidad, seguridad, cobertura y E2E.
- Documentación de umbrales y criterios de aceptación.

**Fuera de alcance:** mutation testing, DAST completo, SBOM firmado, escaneo de Kubernetes, SonarQube self-hosted y cobertura global al 90 %.

## Stack: qué mide cada herramienta

| Dimensión | Herramienta | Coste | Gate |
|---|---|---|---|
| Estilo y errores obvios | `ruff` (backend), ESLint (frontend) | 0 | Bloqueante |
| Tipos | `mypy` gradual (backend), `tsc` (frontend) | 0 | Bloqueante |
| Bugs, vulnerabilidades, code smells, duplicación, complejidad, deuda | **SonarCloud** | 0 (repos públicos) | Bloqueante en código nuevo |
| Seguridad semántica (SAST) | **CodeQL** | 0 (repos públicos) | Bloqueante en `high`/`critical` |
| Dependencias | Dependabot + Dependency Review + `pip-audit`/`pnpm audit` | 0 | Dependency Review bloqueante; audits advisory al inicio |
| Secretos | GitHub Secret Scanning + Push Protection | 0 | Bloqueante |
| Contenedor | **Trivy** + **hadolint** | 0 | Bloqueante en `CRITICAL` |
| Comportamiento | pytest/Vitest + cobertura | 0 | Cobertura con trinquete |
| Flujos críticos | Playwright E2E | 0 | Bloqueante (fase 3) |
| Contrato API | `openapi-spec-validator` (+ `oasdiff` en fase posterior) | 0 | Bloqueante |

## Quality gate

Regla **Clean as You Code**: el gate se aplica al **código nuevo**, no al legado, para no bloquear el ritmo.

| Condición (código nuevo) | Umbral |
|---|---|
| Cobertura de líneas nuevas | ≥ 80 % |
| Duplicación | ≤ 3 % |
| Bugs / vulnerabilidades | 0 |
| Security hotspots revisados | 100 % |
| Deuda técnica nueva | ≤ 5 % del tiempo de desarrollo |
| Cobertura global | Nunca por debajo del baseline (trinquete) |

El baseline se fija el día que se active la medición y sube por hito, no de golpe.

## Pipeline objetivo

### Backend

| Job | Mide | Bloqueante |
|---|---|---|
| `lint` | ruff | Sí |
| `types` | mypy (gradual, `src/domain` y `src/application` primero) | Sí |
| `unit` | pytest + `pytest-cov` → `coverage.xml` | Sí |
| `openapi` | exporta y valida `openapi.json` | Sí |
| `integration` | PG18 + migraciones up/down/up | Sí |
| `security` | `pip-audit` | Advisory → bloqueante |
| `docker` | hadolint + Trivy (filesystem e imagen) | Bloqueante en `CRITICAL` |
| `sonar` | SonarCloud con `coverage.xml` | Sí (quality gate) |
| **`test`** | **gate** que exige todo lo anterior | Sí |

### Frontend

| Job | Mide | Bloqueante |
|---|---|---|
| `lint` | ESLint + `eslint-plugin-sonarjs` | Sí |
| `types` | `tsc --noEmit` | Sí |
| `unit` | Vitest + cobertura (`lcov.info`) | Sí |
| `build` | Next build | Sí |
| `e2e` | Playwright (flujos críticos) | Sí (fase 3) |
| `security` | `pnpm audit` | Advisory → bloqueante |
| `sonar` | SonarCloud con `lcov.info` | Sí (quality gate) |
| **`check`** | **gate** que exige todo lo anterior | Sí |

### Transversal

- **CodeQL** (Python + TypeScript) en push/PR + semanal.
- **Dependency Review** en PRs.
- **Secret scanning + push protection** (Settings).
- **Dependabot** semanal: pip, pnpm, github-actions, docker.
- `permissions: contents: read`, `concurrency` con `cancel-in-progress`, `timeout-minutes` en todos los workflows.
- Escaneo programado semanal además del de PR.

## Fases y tareas

### Fase 0 — Higiene del pipeline

| ID | Tarea | Responsable | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| CI-01 | `permissions`, `concurrency`, `timeout-minutes`, Dependabot, CODEOWNERS, plantilla de PR | David | 1–2 h | Un push cancela el run anterior; ningún job pasa de 15 min; Dependabot abre PRs |
| CI-02 | Medir cobertura sin bloquear (`pytest-cov`, `@vitest/coverage-v8`) y subir artifact | David | 1 h | El reporte se descarga del run |

### Fase 1 — Calidad estática

| ID | Tarea | Responsable | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| CI-03 | `mypy` gradual + `eslint-plugin-sonarjs` | David | 2–3 h | `types` en verde y sin `ignore` nuevos |
| CI-04 | SonarCloud: org/proyecto, `SONAR_TOKEN`, `sonar-project.properties`, job y quality gate | David (código) + Mathias (secreto/admin) | 2–3 h | Un PR con code smell nuevo o cobertura nueva < 80 % queda en rojo con comentario de Sonar |

### Fase 2 — Seguridad

| ID | Tarea | Responsable | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| CI-05 | CodeQL (workflow, Python + TypeScript) | David | 1 h | Hallazgos en la pestaña Security |
| CI-06 | Dependency Review + `pip-audit` + `pnpm audit` | David | 1–2 h | PR con dependencia vulnerable conocida bloqueado |
| CI-07 | Secret scanning + push protection (Settings) | Mathias | 15 min | Un secreto en un push se bloquea |
| CI-08 | Trivy + hadolint en el Dockerfile del backend | David | 1–2 h | Sin `CRITICAL` en la imagen |
| CI-09 | Validar `openapi.json` antes de subirlo | David | 30 min | Esquema inválido rompe el job |

### Fase 3 — Pruebas

| ID | Tarea | Responsable | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| CI-10 | Activar los 7 E2E de Playwright en CI (datos semilla, artifacts, retry) | Nikol + David | 1–2 días | Flujo de checkout roto rompe el PR; E2E < 10 min |
| CI-11 | Gate de cobertura con trinquete (baseline y subida por hito) | David | 2 h | La cobertura no puede bajar del baseline |

### Fase 4 — Despliegue y gobierno

| ID | Tarea | Responsable | Esfuerzo | Criterio de aceptación |
|---|---|---|---|---|
| CI-12 | Environment `production` con aprobación + smoke post-deploy + rollback documentado | Mathias + David | 1 día | Deploy requiere aprobación; smoke falla → alerta y reversión < 5 min |
| CI-13 | Protección de rama con Code Owners y conversaciones resueltas; escaneo semanal; métricas | Mathias | 1 h | Ramas protegidas con las nuevas reglas; reporte semanal |

## Requisitos de secretos y permisos

| Necesito | Quién | Cómo |
|---|---|---|
| `SONAR_TOKEN` (secreto de repo) | Mathias (admin) | `gh secret set SONAR_TOKEN --repo …` o UI |
| Org/proyecto en SonarCloud | Mathias | Crear org y proyectos con la cuenta del equipo |
| Secret scanning + push protection | Mathias | Settings → Code security |
| Dependabot alerts + Code scanning | Mathias | Settings → Code security |
| Environment `production` con aprobación | Mathias | Settings → Environments |
| Code Owners + conversaciones resueltas en protección de rama | Mathias | Settings → Branches |

> David es `maintain`, no `admin`: puede mergear y configurar workflows, pero no secretos ni ajustes de seguridad del repositorio.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| SonarCloud recibe el código (tercero) | Los repos son públicos; si no se acepta, self-hosted o solo CodeQL |
| Ruido inicial por el legado | *Clean as You Code* + baseline, nunca gate global al 90 % |
| Pipeline más lento | Jobs paralelos, cache de dependencias, `concurrency` y timeouts |
| Duplicar SAST (Sonar + CodeQL + Bandit + Semgrep) | Stack curado: Sonar (calidad) + CodeQL (semántico); sin Bandit/Semgrep |
| E2E inestables | Datos semilla deterministas, `retries: 1`, artifacts de traza, cuarentena etiquetada |
| mypy sobre todo el legado | Adopción gradual por capas (`domain` → `application` → `adapters`) |

## Métricas de éxito

- Cobertura global por encima del baseline y subiendo por hito.
- 0 bugs y 0 vulnerabilidades nuevas en Sonar.
- 0 secretos commiteados.
- 0 dependencias con CVE alta sin resolver.
- Duración del pipeline < 10 min (p95).
- Tasa de flaky < 2 %.
- Tiempo de recuperación tras un deploy fallido < 5 min.

## Progreso

- 2026-11-07: plan creado a partir de la auditoría del pipeline de los dos repositorios. Sin implementación todavía.
- 2026-11-07: **Fase 0 y Fase 2 implementadas** en los PR [#98](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/98) (backend) y [#64](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/pull/64) (frontend), con CI en verde: permisos mínimos, `concurrency`, timeouts, cobertura como artifact, Dependabot, CODEOWNERS, plantilla de PR, CodeQL, `pip-audit`/`pnpm audit` (advisory), hadolint y validación del OpenAPI. **Dependency Review** quedó diferido: exige el **Dependency Graph**, que es un ajuste de admin (`Settings → Code security`). **Fase 1** pendiente de que existan los proyectos en SonarCloud (el token ya está como secreto en ambos repos; la org `taller-sw-web` no tiene proyectos y el usuario es `Members`).

## Siguiente paso

1. Revisar y aceptar el [ADR-0024](../../docs/arquitectura/adr/ADR-0024-calidad-y-seguridad-en-el-pipeline.md).
2. Implementar la Fase 0 (CI-01 y CI-02) en un PR por repositorio.
3. Pedir a Mathias los accesos de la sección de secretos y permisos.
