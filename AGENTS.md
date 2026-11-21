# AGENTS.md — Reglas de trabajo del Canal Chatbot

Este repositorio es la **fuente de verdad de las especificaciones**. No contiene código de aplicación:
el backend vive en `../G3-Chatbot-backend` y el frontend en `../G3-Chatbot-frontend`. Estas reglas
aplican a cualquier agente o persona que trabaje en los tres repositorios.

## 1. Orden de lectura obligatorio

Antes de tocar código, lee en este orden:

1. `openspec/specs/<capacidad>/spec.md` — **qué** debe hacer la capacidad. Es la fuente de verdad del
   comportamiento.
2. `openspec/specs/<capacidad>/design.md` — **cómo** se integra: endpoints propios y de otros módulos,
   componentes, tablas y errores.
3. `docs/arquitectura/modularizacion.md` — a qué módulo pertenece y qué puede importar.
4. `../G3-Chatbot-backend/src/modules/mod_<id>/MODULE.md` y
   `../G3-Chatbot-frontend/src/modules/mod-<id>/MODULE.md` — superficie pública y rutas del módulo.
5. El ADR que corresponda en `docs/arquitectura/adr/`.

Si la spec no existe, no está claro a qué módulo pertenece o contradice el código, **detente y
resuélvelo en la spec antes de implementar**. No inventes comportamiento en el código.

## 2. Normas no negociables

1. **Siempre se lee la spec del módulo antes de tocar código.**
2. **Si el código avanza sin estar en la spec, la spec se actualiza en el mismo PR.** El *spec delta*
   es obligatorio: no se deja para un PR posterior ni se documenta solo en el mensaje del commit.
3. **Revisar coherencia antes de mergear.** Lo nuevo no puede contradecir specs previas, estados ya
   cerrados (por ejemplo `PAGADO`, `ENTREGADO`, `ANULADO`, `CONVERTED`), decisiones de ADR ni
   contratos publicados. Si hay conflicto, se marca la decisión y se actualiza la spec o el ADR; no se
   silencia.
4. **Un PR/MR por módulo.** El PR declara el `mod-*` que toca y no modifica archivos de otro módulo.
   `shared/` solo entra con la etiqueta `cross-modulo` y revisión del owner de plataforma.
5. **No se toca el interior de otro módulo.** Solo `public.py` / `public.ts` y las capacidades
   registradas. Las fronteras las verifican los gates, no la buena voluntad.
6. **No se commitean secretos.** `.env`, tokens, claves y credenciales quedan fuera del diff.
7. **El contrato manda.** Un endpoint nuevo va primero al `design.md` y a `docs/openapi.json`; el
   adapter del frontend y su `module.manifest.ts` se actualizan en el mismo cambio.

## 3. Flujo de trabajo

```text
spec → implementación → tests → contrato → PR por módulo → revisión de coherencia → merge
```

| Paso | Qué se hace | Artefacto |
|---|---|---|
| 1. Spec | Se lee y, si hace falta, se actualiza `spec.md` | `openspec/specs/<capability>/spec.md` |
| 2. Diseño | Se actualiza `design.md` con rutas, payloads, estados y errores | `design.md` |
| 3. Implementación | Backend y frontend, cada uno en su módulo | `src/modules/mod_*` |
| 4. Tests | Unitarios, integración y contrato; un caso por escenario tocado | `tests/` |
| 5. Contrato | `export_openapi.py`, `modules:sync`, manifiesto del frontend | `docs/openapi.json`, `registry.generated.ts` |
| 6. PR | Un módulo, diff pequeño, checklist completa | GitHub PR |
| 7. Coherencia | Se compara con specs previas, estados cerrados y ADR | Revisión |
| 8. Merge | CI verde y revisión aprobada | `main` / `development` |

El detalle operativo, la Definition of Done y la checklist de PR están en
[`docs/flujo-de-trabajo.md`](docs/flujo-de-trabajo.md).

## 4. Definition of Done

Un cambio está terminado cuando:

- [ ] La spec (`spec.md`) y el diseño (`design.md`) describen el comportamiento real.
- [ ] El código está en el módulo correcto y no importa el interior de otro módulo.
- [ ] Los tests nuevos cubren los escenarios tocados y el CI está en verde.
- [ ] `python scripts/check_modules.py` (backend) y `pnpm modules:check` (frontend) pasan.
- [ ] `docs/openapi.json` está actualizado y validado; el manifiesto del frontend también.
- [ ] La revisión de coherencia no encontró contradicciones con specs previas, estados cerrados o ADR.
- [ ] No hay secretos en el diff y la documentación afectada está actualizada.

## 5. Checklist de PR

- [ ] El PR declara un solo `mod-*` (o `cross-modulo` si toca `shared/`).
- [ ] La spec o el `design.md` se actualizaron en este mismo PR (o se explica por qué no aplica).
- [ ] Se revisó que no se contradicen specs previas ni estados ya cerrados.
- [ ] Tests nuevos o ajustados; CI en verde.
- [ ] `check_modules` / `modules:check` en verde.
- [ ] `docs/openapi.json` y `registry.generated.ts` regenerados si cambió el contrato.
- [ ] Sin secretos, sin dependencias nuevas sin justificar, sin cambios fuera del módulo.

## 6. Mapa rápido de módulos

| id | Backend | Frontend | Specs |
|---|---|---|---|
| `mod-auth` | `mod_auth` | `mod-auth` | SPEC-01..04 |
| `mod-catalog` | `mod_catalog` | `mod-catalog` | SPEC-06..10 |
| `mod-cart` | `mod_cart` | `mod-cart` | SPEC-10, 11, 13 |
| `mod-shipping` | `mod_shipping` | `mod-shipping` | SPEC-12, 18 |
| `mod-checkout` | `mod_checkout` | `mod-checkout` | SPEC-12, 14, 15, 24 |
| `mod-orders` | `mod_orders` | `mod-orders` | SPEC-15..18, 24 |
| `mod-postventa` | `mod_postventa` | `mod-postventa` | SPEC-19..22, 24 |
| `mod-chat` | `mod_chat` | `mod-chat` | SPEC-05, 23, 24 |

El DAG y las reglas de import están en [`docs/arquitectura/modularizacion.md`](docs/arquitectura/modularizacion.md).
La auditoría vigente de specs contra código está en [`docs/auditoria-specs-2026-11.md`](docs/auditoria-specs-2026-11.md).

## 7. Comandos de verificación

Backend (`../G3-Chatbot-backend`):

```bash
python scripts/check_modules.py
python scripts/export_openapi.py --check
pytest
ruff check .
mypy src
```

Frontend (`../G3-Chatbot-frontend`):

```bash
pnpm modules:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Specs (este repo):

```bash
npx @fission-ai/openspec validate --specs
```

> `--strict` no se usa: el formato híbrido escribe los escenarios con Gherkin en español
> (`DADO`/`CUANDO`/`ENTONCES`) y el validador estricto exige `WHEN`/`THEN` en inglés. El comando sin
> `--strict` valida las 24 specs y deja los avisos de Gherkin como advertencia, no como error.
