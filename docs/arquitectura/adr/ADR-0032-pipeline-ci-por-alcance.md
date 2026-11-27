# ADR-0032: Pipeline de CI por alcance, costo y evidencia

## Estado

Aceptada

## Fecha

2026-11-27

## Contexto

[ADR-0024](ADR-0024-calidad-y-seguridad-en-el-pipeline.md) dejó un pipeline con un gate único por repositorio (`test` en backend, `check` en frontend), jobs paralelos y SonarCloud con *Clean as You Code*. El pipeline funciona, pero corre los jobs caros en cada PR: E2E del frontend (~25 min), DAST y gateway-integration del backend (~20 min cada uno), además de validadores repartidos en varios jobs que repiten `checkout` e instalación.

Los tres repositorios son públicos y usan runners estándar de GitHub. La suite real es corta: 132 archivos de test unitario backend, 13 de integración y 92 archivos / 561 tests unitarios frontend; los pipelines completos tardan 2–4 minutos. El problema no es la duración de los tests, sino el costo de los jobs de runtime y el trabajo que se ejecuta cuando un PR solo toca documentación.

GitHub no tiene el `rules: changes` por job de GitLab ni pipelines hijos generados en runtime. Tampoco hay Nx en el frontend: el build de Next.js es monolítico y no se puede compilar “solo el módulo tocado”.

## Decisión

El pipeline se organiza por **alcance calculado una vez** y **orden de costo**:

- Un job `scope` (segundos, sin dependencias del proyecto) calcula el diff contra el merge-base de `development`, cuenta borrados y renames, mapea rutas a módulos, cierra el DAG de `modules.manifest.json` hacia dependientes y publica booleanos (`run_unit`, `run_integration`, `run_dast`, …). Si no puede resolver la base o el diff queda vacío en un PR/push, usa alcance completo: falla por exceso, nunca por defecto.
- `validate` ejecuta todos los validadores bloqueantes en un solo job y falla al final, con `validation-report.txt` como evidencia durante 90 días.
- Los tests unitarios corren completos y en un solo job. No se fragmentan: la suite es corta y los shards añadirían más overhead que ahorro.
- Los tests de integración usan una **matriz dinámica** con `fromJSON`: solo se crean los shards con algo que ejecutar (`mod_catalog`, `mod_chat`, `mod_checkout`, `mod_orders`, `core`). Cada shard levanta su propio PostgreSQL 18 y RabbitMQ; la cobertura se combina después con `coverage combine`.
- Los jobs de runtime caros (E2E, DAST, gateway-integration) corren en `push` a `development`, en el schedule semanal o en un PR etiquetado `ci:full`; añadir la etiqueta relanza el workflow. No bloquean el PR por defecto.
- SonarCloud analiza el PR de forma nativa. **No** se crean ramas `mr-<IID>` ni se limita `sonar.inclusions` por PR: el análisis de PR ya está acotado al *new code* y las inclusiones dinámicas ocultarían problemas entre archivos. Además del quality gate de la UI, el pipeline consulta los issues nuevos y, cuando la API expone las medidas de *new code* al token del proyecto, exige cobertura ≥ 80 % y duplicación ≤ 3 %. **Falla cerrado**: en PR ante severidad `MINOR` o superior; en `push` a `development` ante `CRITICAL`/`BLOCKER`, para no bloquear el deploy por deuda `MAJOR` heredada. Si la API no responde o falta el token, el job falla. Un cambio en `sonar-project.properties` requiere la etiqueta `ci:sonar-config` y revisión de un owner. La cobertura global de la UI sigue siendo el gate principal hasta que el quality gate incluya `new_coverage`.
- Un job `notify` publica (o actualiza) un comentario en el PR cuando el pipeline falla, con los jobs fallidos y un extracto de cada log.
- La cobertura mantiene el trinquete actual: 85 % backend y 80/74/78/80 frontend, con subida por módulo cuando se toque. No se adopta un 100 % global.

Los nombres `test` (backend) y `check` (frontend) se conservan porque son los checks requeridos de `development`, junto con los checks de CodeQL (`Analyze (python)` y `Analyze (javascript-typescript)`). El agregador falla si un job que el alcance pidió no terminó en `success`; un job omitido a propósito no cuenta como aprobado. `development` de specs exige el check `OpenSpec y enlaces`, rama actualizada, conversación resuelta y no permite force push ni borrado; `enforce_admins` queda activo.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Copiar el pipeline hijo dinámico de GitLab | GitHub no lo soporta sin `workflow_dispatch` y un PAT; rompe la semántica de checks requeridos. La matriz dinámica cubre el caso |
| `paths:` a nivel de workflow | GitHub solo permite `paths` a nivel de workflow, no por job; un workflow omitido no reporta el check requerido y el PR queda bloqueado o sin la señal esperada. Por eso el alcance se calcula dentro del workflow |
| Fragmentar los tests unitarios en 4–8 shards | Suites de 2–4 minutos: el arranque de runner, la instalación y la fusión de cobertura cuestan más de lo que ahorran |
| `nx affected` | No hay Nx y `next build` no se puede dividir por módulo |
| Cobertura 100 % global | Bloquearía el legado y incentivaría tests sin valor; se mantiene *Clean as You Code* + trinquete |
| Ramas `mr-<IID>` de Sonar con `sonar.inclusions` | Duplica el análisis nativo de PR de SonarCloud y fragmenta el histórico |
| DAST y E2E en cada PR | 20–25 minutos por PR para checks que no cambian con un diff de documentación o de un módulo aislado; la etiqueta `ci:full` permite forzarlos |

## Consecuencias

**Positivas**

- Un PR de documentación no gasta runners en tests, Docker, Sonar ni E2E.
- El PR paga solo los jobs que su diff justifica; los caros quedan en `development` y en el schedule.
- Todos los errores de validación llegan en un solo reporte y quedan como evidencia.
- El alcance es código probado (`scripts/ci/scope.py`, `scope.mjs`) con tests unitarios, no una convención oral.

**Negativas y riesgos aceptados**

- Un PR puede mergear sin DAST/E2E; se compensa con el pipeline de `development`, el schedule semanal y la etiqueta `ci:full`.
- Los PRs de fork no reciben `SONAR_TOKEN`: el job de Sonar falla y un maintainer debe ejecutar el análisis en una rama del repo base antes de mergear. Los PRs de forks requieren aprobación de maintainer (`all_external_contributors`).
- Las acciones están fijadas por SHA y el repositorio exige SHA pinning; una actualización de acción pasa por Dependabot o un PR explícito.
- El workflow y los scripts de alcance viajan en el PR, así que un PR malicioso podría intentar debilitar el gate. La defensa es la revisión obligatoria de code owners, la protección de rama y ejecutar los helpers con token (`sonar`, `notify`) desde el commit base cuando existe. No se usa `pull_request_target` para ejecutar código del PR. El PR que introduce los helpers los ejecuta por primera vez (bootstrap); después, la copia del base es la única que recibe tokens. `workflow_dispatch` solo se permite en `development`.
- El cálculo de alcance es código que mantener; si el merge-base falla, el pipeline se vuelve completo y más lento, pero no se salta gates.
- La matriz de integración multiplica los servicios (PostgreSQL y RabbitMQ por shard). En este repositorio son 5 shards como máximo y solo cuando el alcance los pide.
- La cobertura de integración se combina en un job extra; si un shard falla, el merge y Sonar se omiten y el agregador falla.

## Referencias

- `.github/workflows/ci.yml` de `G3-Chatbot-backend` y `G3-Chatbot-frontend`.
- `G3-Chatbot-backend/scripts/ci/scope.py` y `G3-Chatbot-frontend/scripts/ci/scope.mjs`.
- [`docs/ci-pipeline.md`](../../ci-pipeline.md) — operación, etiquetas y comandos locales.
- [ADR-0024](ADR-0024-calidad-y-seguridad-en-el-pipeline.md) — gate de calidad y seguridad que esta decisión conserva.
