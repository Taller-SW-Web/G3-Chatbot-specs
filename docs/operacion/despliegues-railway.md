# Runbook: despliegues en Railway con Wait for CI

> **Estado verificado el 2026-11-27.** Este documento describe cómo se comporta **Wait for CI** en el
> entorno `production` de Railway, cómo diagnosticar un deployment `SKIPPED` y cómo recuperarlo sin
> desactivar el gate. No afirma que todos los servicios tengan la misma configuración: se revisa servicio
> por servicio con `railway environment config -e production --json`.
>
> Alcance: despliegues de `G3-Chatbot-backend` y `G3-Chatbot-consumer` en Railway. No cubre Vercel,
> la base de datos ni el broker; esos viven en sus propios runbooks.

## 1. Configuración actual

| Elemento | Estado (2026-11-27) |
|---|---|
| Rama desplegada | `development`; `main` es un placeholder de un commit y no se promueve |
| `source.checkSuites` | `true` en el entorno `production` de API y consumidor |
| Checks requeridos por la protección de rama | `test` + `Analyze (python)` ([ci-pipeline.md](../ci-pipeline.md)) |
| Comportamiento de Railway | Espera **todos** los check suites del commit, no solo los requeridos |
| Timeout de Railway | Si los workflows no terminan en ~2 h, el deployment puede quedar `SKIPPED` |
| Verificación post-deploy | `.github/workflows/verify-production.yml` (health y OpenAPI) |

## 2. Qué significa WAITING y SKIPPED

- `WAITING`: Railway creó el deployment y espera a que terminen los check suites de GitHub del commit.
- `SKIPPED`: al menos un check suite del commit terminó en fallo, o Railway agotó el timeout. El
  deployment no publica la imagen.
- Un workflow **programado** (por ejemplo `Daily production smoke` → `Production health`) se asocia al
  commit que era HEAD cuando se disparó. Si falla, “envenena” ese commit aunque el fallo sea externo al
  código desplegado.

Ejemplo real: el commit `5b670e8` quedó `SKIPPED` el 2026-11-26 porque el run programado
`Production health` falló sobre ese HEAD; el check `test` estaba verde.

## 3. Diagnóstico

1. Identifica el commit y el deployment:
   ```bash
   gh api repos/Taller-SW-Web/G3-Chatbot-backend/deployments?per_page=5 \
     --jq '.[] | [.id,.environment,.ref,.created_at] | @tsv'
   ```
2. Lista los check suites del commit:
   ```bash
   gh api repos/Taller-SW-Web/G3-Chatbot-backend/commits/<sha>/check-runs \
     --jq '.check_runs[] | [.name,.status,.conclusion] | @tsv'
   ```
3. Compara con el HEAD actual de `development`:
   ```bash
   git fetch origin development
   git log -1 --format='%H %s' origin/development
   ```

## 4. Recuperación

**Caso A — el commit sigue siendo el HEAD de `development` y el fallo era transitorio o externo:**

1. Relanza el workflow que falló, no el deployment:
   ```bash
   gh workflow run smoke.yml --repo Taller-SW-Web/G3-Chatbot-backend --ref development
   ```
2. Espera a que el check suite termine en verde.
3. Redespliega el mismo commit desde Railway (Deployments → Redeploy) o deja que el siguiente push
   lo haga.

**Caso B — `development` ya avanzó:**

No relances el check del commit viejo: un `workflow_dispatch` evalúa el HEAD actual y el check rojo
queda pegado al commit anterior. Despliega un commit posterior; el deployment nuevo evaluará sus
propios check suites.

**Caso C — el deployment quedó `SKIPPED` por timeout de 2 h:**

Vuelve a lanzar el deployment del commit actual cuando los workflows estén verdes. Si el timeout se
repite, revisa la cola de runners y la duración de `test`/CodeQL antes de tocar Wait for CI.

## 5. Rollback de Wait for CI

Desactivar Wait for CI es una **excepción de plataforma**, no una operación normal. Requiere aprobación
del owner de plataforma y debe registrarse en el issue o PR que la justifica.

1. Revisa la configuración actual:
   ```bash
   railway environment config -e production --json
   ```
2. En Railway, servicio → **Settings → Source → Wait for CI**, desactívalo solo para el servicio
   afectado.
3. Despliega y verifica `/health` y `/openapi.json`.
4. Vuelve a activarlo en cuanto el gate vuelva a estar verde; no lo dejes apagado.

## 6. Referencias

- [`ci-pipeline.md`](../ci-pipeline.md) — checks requeridos, full mode y gates.
- `G3-Chatbot-backend/.github/workflows/smoke.yml` — smoke programado de producción.
- `G3-Chatbot-backend/.github/workflows/verify-production.yml` — verificación post-deploy.
- Backend [#221](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/221) — activación de Wait for CI en el consumidor.
- [`evidencia-mecanismo-asincrono.md`](../evidencia-mecanismo-asincrono.md) — evidencia del outbox y del incidente.
