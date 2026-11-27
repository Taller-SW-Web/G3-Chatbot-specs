# Revisión automática de cambios (`review-sentinel`)

> **Estado:** propuesta operativa para el bot `review-sentinel`.
> **Alcance:** PRs y merges de `G3-Chatbot-backend`, `G3-Chatbot-frontend` y `G3-Chatbot-specs`.
> **Regla de oro:** el bot encuentra, explica y abre issues; nunca aprueba, mergea ni pusha código.

## 1. Fuentes de verdad

El bot no inventa criterios. Revisa contra:

- `AGENTS.md` y `docs/flujo-de-trabajo.md` de cada repo.
- `openspec/specs/<capacidad>/spec.md` y `design.md`.
- `docs/contratos-integracion.md`, `docs/openapi.json` y `MODULE.md`.
- `docs/arquitectura/modularizacion.md`, ADR vigentes y `arquitectura-*.md`.
- Checks de CI, CodeQL, SonarCloud, Trivy, ZAP y Lighthouse.
- `pip-audit`, `pnpm audit` y alertas de dependencias.

## 2. Reglas y severidad

### Buenas prácticas (BP)

| ID | Regla | Severidad |
|---|---|---|
| BP-01 | El PR respeta un módulo; `shared/` lleva `cross-modulo` y justificación | P1 |
| BP-02 | No importa `domain/`, `application/` ni `adapters/` de otro módulo | P1 |
| BP-03 | Errores con `problem+json` y `code` estable; no se filtra detalle interno | P1 |
| BP-04 | Tests para la regla/caso nuevo y para el borde HTTP tocado | P2 |
| BP-05 | Sin `TODO` sin dueño/fecha, código muerto, imports rotos o secretos | P2 |
| BP-06 | PR pequeño y con un solo propósito; commits coherentes | P3 |

### Seguridad (SEC)

| ID | Regla | Severidad |
|---|---|---|
| SEC-01 | Sin secretos, tokens, claves ni datos personales en el diff | P0 |
| SEC-02 | Autorización y pertenencia por recurso; sin IDOR | P0 |
| SEC-03 | Validación de entrada y de tipos en el borde | P1 |
| SEC-04 | Dependencia con CVE crítica o high sin justificar | P1 |
| SEC-05 | Logs sin tokens, tarjetas, OTP ni datos sensibles | P0 |
| SEC-06 | Uploads con tipo/tamaño/EXIF controlados y sin path traversal | P1 |
| SEC-07 | Sin SSRF, inyección, deserialización insegura ni comandos sin sanear | P0 |
| SEC-08 | Cabeceras/CSP y cookies no se debilitan sin ADR | P2 |

### Specs (SPEC)

| ID | Regla | Severidad |
|---|---|---|
| SPEC-01 | Todo cambio de comportamiento tiene spec delta o issue/PR de specs enlazado | P1 |
| SPEC-02 | No contradice specs previas, estados cerrados ni ADR | P1 |
| SPEC-03 | Campo, ruta, tag y error nuevos están en `design.md` / contrato | P1 |
| SPEC-04 | Cambio de arquitectura o DAG tiene ADR y actualiza el índice | P1 |
| SPEC-05 | Cada escenario tocado tiene al menos una prueba que lo referencia | P2 |

### Documentación y contrato (DOC)

| ID | Regla | Severidad |
|---|---|---|
| DOC-01 | `docs/openapi.json` regenerado y sin drift | P1 |
| DOC-02 | `docs/contratos-integracion.md` refleja campos y rutas nuevas | P1 |
| DOC-03 | `MODULE.md` actualizado si cambia la superficie pública | P2 |
| DOC-04 | Enlaces relativos y referencias a ADR/specs existen | P2 |
| DOC-05 | README/runbook actualizado si cambia una operación | P3 |

### Sonar y CI (SONAR/CI)

| ID | Regla | Severidad |
|---|---|---|
| SONAR-01 | Quality Gate rojo | P1 |
| SONAR-02 | Issue nueva blocker/critical | P1 |
| SONAR-03 | Cobertura nueva por debajo del umbral del repo | P2 |
| SONAR-04 | Duplicación o complejidad nueva fuera de umbral | P3 |
| CI-01 | Check requerido rojo o skipped | P1 |
| CI-02 | Rama `BEHIND` o sin CI contra `development` | P1 |
| CI-03 | `Closes` usado cuando el issue pide deploy/verificación | P1 |
| CI-04 | Dependencia nueva sin justificar o con auditoría roja | P2 |

## 3. Política de issues

| Caso | Dónde | Asignada a | Labels |
|---|---|---|---|
| Hallazgo de código | Repo del código | Autor del PR | `bot-review`, `seguridad`/`specs`/`docs`/`sonar`/`calidad`, `P0..P3` |
| Falta o contradicción de specs | `G3-Chatbot-specs` | `@MathiasTL` y `@Ankarmin` | `documentation`, `bloqueante` si frena |
| Seguridad explotable o secreto | Security advisory privado o repo privado | Owner del repo | `security`, `P0` |
| P3 / estilo | Solo digest | Nadie | — |

Reglas:

1. **Una issue por hallazgo accionable**, no una por línea.
2. **Fingerprint** `repo:regla:archivo:linea:codigo`; busca issues abiertas antes de crear.
3. Si el hallazgo se corrige antes del merge, comenta y cierra la issue con evidencia.
4. No cierres por “PR mergeado”; cierra cuando el fix esté verificado.
5. No asignes issues de specs a colaboradores: solo a Mathias y David.
6. No publiques detalles de explotación ni secretos en issues públicas.

## 4. Formato de issue

```md
## Hallazgo
- Regla: SEC-03
- Evidencia: `ruta/archivo.py:123`, PR #...
- Severidad: P1
- Por qué importa:

## Fix sugerido

## Criterio de aceptación
- [ ] ...
- [ ] Test/verificación:

## Fingerprint
`repo:SEC-03:ruta/archivo.py:123`
```

## 5. Flujo

1. Recibe PR o workflow terminado.
2. Lee diff, checks y artefactos; no revisa el repo completo.
3. Aplica reglas y descarta falsos positivos.
4. Comenta el PR con el informe.
5. Deduplica y crea/actualiza issues.
6. Publica digest semanal por colaborador.

## 6. Guardrails

- **Nunca** aprueba, mergea, pusha, reinicia servicios ni cambia producción.
- Empieza en **report-only** dos semanas; luego activa P0/P1 y después P2.
- Permisos mínimos: `contents:read`, `issues:write`, `pull-requests:write`, `security-events:read`.
- No lee archivos `.env`, claves ni credenciales; si los encuentra, los redacta.
- Si duda, pregunta al owner; no inventa una regla.

## 7. Criterios de éxito

- Menos de 20 % de falsos positivos en P1.
- Cero issues duplicadas por fingerprint.
- Toda issue tiene evidencia, fix sugerido y criterio de aceptación.
- Ningún PR del bot; el bot no escribe código.
