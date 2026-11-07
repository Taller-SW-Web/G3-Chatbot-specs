# ADR-0024: Pipeline de CI/CD con gate de calidad, seguridad y pruebas

## Estado

Propuesta

## Fecha

2026-11-07

## Contexto

Los tres repositorios son **pÃºblicos**, lo que habilita las herramientas gratuitas de GitHub (CodeQL, Dependabot, Dependency Review, Secret Scanning) y SonarCloud para proyectos pÃºblicos.

El pipeline actual, tras la separaciÃ³n en jobs paralelos de [#88](https://github.com/Taller-SW-Web/G3-Chatbot-backend/pull/88) y [#61](https://github.com/Taller-SW-Web/G3-Chatbot-frontend/pull/61), tiene un **gate Ãºnico** (`test` y `check`) y despliegue condicionado: Railway espera el check y aplica `alembic upgrade head` como pre-deploy; Vercel exige `check` con *Deployment Checks* ([ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md), [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)).

Sin embargo, ese pipeline mide **errores y comportamiento**, no **calidad** ni **seguridad**:

- No hay SAST ni SCA, ni bloqueo de secretos.
- No se mide cobertura ni calidad estructural (code smells, duplicaciÃ³n, complejidad, deuda).
- El `Dockerfile` no se analiza.
- El `openapi.json` se exporta pero no se valida.
- Los 7 E2E de Playwright siguen en `test.fixme` y no corren en CI.
- El despliegue no exige aprobaciÃ³n ni verifica el servicio tras publicar.

Restricciones: equipo de siete personas, tiempo de curso y la regla de no bloquear el ritmo con el legado.

## DecisiÃ³n

El proyecto adopta un **pipeline de calidad y seguridad** con un Ãºnico gate requerido por repositorio que exige, en jobs paralelos:

- **Backend**: `ruff`, `mypy` gradual, `pytest` con cobertura, exportaciÃ³n y **validaciÃ³n** del OpenAPI, migraciones up/down/up e integraciÃ³n con PostgreSQL 18, `pip-audit`, `hadolint` + Trivy y anÃ¡lisis de SonarCloud.
- **Frontend**: ESLint, `tsc`, Vitest con cobertura, build, `pnpm audit`, Playwright E2E y anÃ¡lisis de SonarCloud.
- **Transversal**: CodeQL (Python y TypeScript), Dependency Review, Secret Scanning con push protection, Dependabot semanal, `permissions: contents: read`, `concurrency` con cancelaciÃ³n y `timeout-minutes`.

El **Quality Gate de SonarCloud** se aplica con la regla **Clean as You Code** (cÃ³digo nuevo: cobertura â‰¥ 80 %, duplicaciÃ³n â‰¤ 3 %, 0 bugs/vulnerabilidades nuevas, hotspots revisados, deuda â‰¤ 5 %) y la cobertura global usa un **trinquete** sobre el baseline, nunca un umbral global alto.

LÃ­mites de la decisiÃ³n: no se adopta SonarQube self-hosted, mutation testing, DAST completo, SBOM firmado ni escaneo de Kubernetes. El detalle de fases, tareas y criterios estÃ¡ en [`odd/tasks/ci-calidad-seguridad.md`](../../../odd/tasks/ci-calidad-seguridad.md).

## Alternativas consideradas

| Alternativa | Por quÃ© se descartÃ³ |
|---|---|
| SonarQube self-hosted (Community) | Exige servidor, respaldo y mantenimiento para tres repositorios; SonarCloud es gratis por ser pÃºblicos |
| Solo lint + tests (estado actual) | No mide code smells, duplicaciÃ³n, complejidad, SAST, SCA ni secretos; la deuda queda invisible |
| Semgrep + Bandit + Sonar + CodeQL a la vez | Solapamiento y ruido; el stack curado es Sonar (calidad) + CodeQL (SAST semÃ¡ntico) |
| Gate global de cobertura al 90 % | Bloquea el legado y frena la entrega; se usa *Clean as You Code* + trinquete por hito |
| No medir calidad | La deuda tÃ©cnica y los secretos se descubren en producciÃ³n o en la revisiÃ³n manual |

## Consecuencias

**Positivas**

- Un PR que baja la calidad, agrega una dependencia vulnerable o commitea un secreto queda bloqueado por el mismo gate que ya exige la protecciÃ³n de rama.
- SonarCloud y CodeQL dan visibilidad por PR (decoraciÃ³n y pestaÃ±a Security) sin coste.
- El deploy queda condicionado al gate y verificable con smoke post-deploy.
- La cobertura deja de ser una opiniÃ³n: hay baseline y trinquete.

**Negativas y riesgos aceptados**

- **Dependencia de SonarCloud**: el cÃ³digo se analiza en un tercero. Aceptable porque los repositorios son pÃºblicos; si se rechaza, se cae a self-hosted o solo CodeQL.
- **Pipeline mÃ¡s largo**: se mitiga con jobs paralelos, cachÃ© de dependencias, `concurrency` y timeouts (objetivo < 10 min p95).
- **Ruido inicial del legado**: se mitiga con *Clean as You Code* y mypy gradual.
- **Requiere administraciÃ³n**: `SONAR_TOKEN`, secret scanning, environments y Code Owners los configura un `admin` del repositorio; el implementador es `maintain`.
- **E2E inestables**: se mitigan con datos semilla, `retries: 1`, artifacts de traza y cuarentena etiquetada.

## Referencias

- [`odd/tasks/ci-calidad-seguridad.md`](../../../odd/tasks/ci-calidad-seguridad.md) â€” plan, fases, tareas y criterios de aceptaciÃ³n.
- `.github/workflows/ci.yml` de `G3-Chatbot-backend` y `G3-Chatbot-frontend`.
- [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) â€” despliegue en Railway, Vercel y Supabase.
- [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md) â€” proxy del frontend hacia la API.
- [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) â€” mocks y URLs base parametrizadas (modo por mÃ³dulo).

