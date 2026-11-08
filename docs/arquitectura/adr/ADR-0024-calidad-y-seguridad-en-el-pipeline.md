# ADR-0024: Pipeline de CI/CD con gate de calidad, seguridad y pruebas

## Estado

Propuesta

## Fecha

2026-11-07

## Contexto

Los tres repositorios son **públicos**, lo que habilita las herramientas gratuitas de GitHub (CodeQL, Dependabot, Dependency Review, Secret Scanning) y SonarCloud para proyectos públicos.

El pipeline actual, tras la separación en jobs paralelos de [#88](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/88) y [#61](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/pull/61), tiene un **gate único** (`test` y `check`) y despliegue condicionado: Railway espera el check y aplica `alembic upgrade head` como pre-deploy; Vercel exige `check` con *Deployment Checks* ([ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md), [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)).

Sin embargo, ese pipeline mide **errores y comportamiento**, no **calidad** ni **seguridad**:

- No hay SAST ni SCA, ni bloqueo de secretos.
- No se mide cobertura ni calidad estructural (code smells, duplicación, complejidad, deuda).
- El `Dockerfile` no se analiza.
- El `openapi.json` se exporta pero no se valida.
- Los 7 E2E de Playwright siguen en `test.fixme` y no corren en CI.
- El despliegue no exige aprobación ni verifica el servicio tras publicar.

Restricciones: equipo de siete personas, tiempo de curso y la regla de no bloquear el ritmo con el legado.

## Decisión

El proyecto adopta un **pipeline de calidad y seguridad** con un único gate requerido por repositorio que exige, en jobs paralelos:

- **Backend**: `ruff`, `mypy` gradual, `pytest` con cobertura, exportación y **validación** del OpenAPI, migraciones up/down/up e integración con PostgreSQL 18, `pip-audit` (consultivo durante la Fase 2), `hadolint` + Trivy y análisis de SonarCloud.
- **Frontend**: ESLint, `tsc`, Vitest con cobertura, build, `pnpm audit` (consultivo durante la Fase 2), Playwright E2E y análisis de SonarCloud.
- **Transversal**: CodeQL (Python y TypeScript), Dependency Review, Secret Scanning con push protection, Dependabot semanal, `permissions: contents: read`, `concurrency` con cancelación y `timeout-minutes`.

El **Quality Gate de SonarCloud** se aplica con la regla **Clean as You Code** (código nuevo: cobertura ≥ 80 %, duplicación ≤ 3 %, 0 bugs/vulnerabilidades nuevas, hotspots revisados, deuda ≤ 5 %) y la cobertura global usa un **trinquete** sobre el baseline, nunca un umbral global alto.

Límites de la decisión: no se adopta SonarQube self-hosted, mutation testing, DAST completo, SBOM firmado ni escaneo de Kubernetes. El detalle de fases, tareas y criterios está en [`odd/tasks/ci-calidad-seguridad.md`](../../../odd/tasks/ci-calidad-seguridad.md).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| SonarQube self-hosted (Community) | Exige servidor, respaldo y mantenimiento para tres repositorios; SonarCloud es gratis por ser públicos |
| Solo lint + tests (estado actual) | No mide code smells, duplicación, complejidad, SAST, SCA ni secretos; la deuda queda invisible |
| Semgrep + Bandit + Sonar + CodeQL a la vez | Solapamiento y ruido; el stack curado es Sonar (calidad) + CodeQL (SAST semántico) |
| Gate global de cobertura al 90 % | Bloquea el legado y frena la entrega; se usa *Clean as You Code* + trinquete por hito |
| No medir calidad | La deuda técnica y los secretos se descubren en producción o en la revisión manual |

## Consecuencias

**Positivas**

- Un PR que baja la calidad, agrega una dependencia vulnerable o commitea un secreto queda bloqueado por el mismo gate que ya exige la protección de rama.
- SonarCloud y CodeQL dan visibilidad por PR (decoración y pestaña Security) sin coste.
- El deploy queda condicionado al gate y verificable con smoke post-deploy.
- La cobertura deja de ser una opinión: hay baseline y trinquete.

**Negativas y riesgos aceptados**

- **Dependencia de SonarCloud**: el código se analiza en un tercero. Aceptable porque los repositorios son públicos; si se rechaza, se cae a self-hosted o solo CodeQL.
- **Pipeline más largo**: se mitiga con jobs paralelos, caché de dependencias, `concurrency` y timeouts (objetivo < 10 min p95).
- **Ruido inicial del legado**: se mitiga con *Clean as You Code* y mypy gradual.
- **Requiere administración**: `SONAR_TOKEN`, secret scanning, environments y Code Owners los configura un `admin` del repositorio; desde el 2026-11-07 el implementador también es `admin`.
- **E2E inestables**: se mitigan con datos semilla, `retries: 1`, artifacts de traza y cuarentena etiquetada.

## Referencias

- [`odd/tasks/ci-calidad-seguridad.md`](../../../odd/tasks/ci-calidad-seguridad.md) — plan, fases, tareas y criterios de aceptación.
- `.github/workflows/ci.yml` de `G3-Chatbot-backend` y `G3-Chatbot-frontend`.
- [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) — despliegue en Railway, Vercel y Supabase.
- [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md) — proxy del frontend hacia la API.
- [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) — mocks y URLs base parametrizadas (modo por módulo).

