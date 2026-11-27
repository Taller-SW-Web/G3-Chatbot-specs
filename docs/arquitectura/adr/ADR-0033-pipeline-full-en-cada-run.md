# ADR-0033: Pipeline full en cada run

## Estado

Aceptada

## Fecha

2026-11-27

## Contexto

[ADR-0032](ADR-0032-pipeline-ci-por-alcance.md) optimizó el costo: el job `scope` decidía qué jobs corrían y los caros (DAST, gateway, E2E, Docker, audit) quedaban fuera de los PRs salvo `ci:full`. El equipo comprobó que esa optimización ocultaba señales: los PRs mostraban jobs `skipped` y no era evidente si el pipeline estaba completo o si un gate se había omitido.

El costo real del pipeline full en este proyecto es asumible: con la suite actual, los jobs caros corren en paralelo y el PR completo tarda unos minutos, no los 20–25 min del diseño original.

## Decisión

El pipeline corre **full en cada PR y push**:

- `scope` sigue calculando el diff, los módulos y `sonar_sources_changed`, pero se invoca con `full=true`: no decide qué jobs corren.
- Todos los jobs de código se ejecutan en cada evento: validate, unit, integración con todos los shards, coverage-merge, Docker/Trivy, audit, DAST, gateway, Sonar y build/E2E en frontend.
- `specs` y `dependency-review` son gates de PR. En `push` corren igualmente y terminan verdes con un no-op explícito, para no aparecer como `skipped`.
- `notify` corre siempre: en fallo publica/actualiza el comentario; en éxito actualiza el mismo comentario a “CI recuperado”.
- `ci:full` deja de ser necesario para forzar los jobs caros; se conserva por compatibilidad.
- `workflow_dispatch` sigue limitado a `development` en backend/frontend.

Los gates de Sonar, cobertura, CodeQL, branch protection, SHA pinning y aprobación de forks de ADR-0032/ADR-0024 no cambian.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Mantener el alcance de ADR-0032 | El equipo pidió ver todos los jobs en cada PR; los `skipped` se confundían con gates no ejecutados |
| Depender de `ci:full` manual | Requiere una acción adicional en cada PR y se olvida; el PR queda incompleto |
| Jobs no-op para los caros | Mostrarían verde sin ejecutar la verificación; es peor que un `skipped` honesto |
| Full solo en `development` y alcance en PR | Mantiene el problema de visibilidad en el PR, que es donde se revisa |

## Consecuencias

**Positivas**

- Cada PR muestra todos los gates ejecutados; no hay ambigüedad entre “no aplica” y “no corrió”.
- Un PR de documentación también valida Docker, Sonar, DAST y gateway, así que una regresión de infraestructura se detecta antes del merge.
- `notify` deja el PR limpio al recuperarse.

**Negativas y riesgos aceptados**

- Todos los PRs consumen más minutos de runner y tardan más que el modo por alcance.
- El pipeline deja de ahorrar en PRs docs-only; es una decisión explícita de visibilidad/rigor.
- Los jobs de PR (`specs`, `dependency-review`) tienen un no-op en push; no validan nada ahí, solo evitan el `skipped`.
- Si en el futuro el costo vuelve a doler, se puede revertir `full=true` en `scope.py`/`scope.mjs` sin cambiar los gates.

## Referencias

- `G3-Chatbot-backend/scripts/ci/scope.py` y `G3-Chatbot-frontend/scripts/ci/scope.mjs`.
- `.github/workflows/ci.yml` de backend y frontend.
- [`docs/ci-pipeline.md`](../../ci-pipeline.md).
- [ADR-0032](ADR-0032-pipeline-ci-por-alcance.md) — diseño por alcance que esta decisión reemplaza en la ejecución.
