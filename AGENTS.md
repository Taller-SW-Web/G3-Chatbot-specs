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
2. **Si el código avanza sin estar en la spec, el cambio de spec viaja en el mismo cambio coordinado.**
   El *spec delta* es obligatorio: PR de código + PR de specs enlazados, o una issue en
   `G3-Chatbot-specs` asignada a `@Ankarmin` y `@MathiasTL` que un owner convierte en PR. Solo
   `@MathiasTL` y `@Ankarmin` abren PRs en este repositorio; el resto no crea ramas ni PRs
   de specs. El PR de código no se mergea hasta que la spec esté en `development`.
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
8. **Un issue no se cierra hasta que su PR esté mergeado.** El cierre cita el PR, el commit y la
   verificación; la referencia es `development`. Un issue puede cerrarse como duplicado, obsoleto o
   no aplicable con justificación, pero no como `completed` si el trabajo sigue en un PR abierto o
   solo está en una rama.

## 3. Flujo de trabajo

```text
spec → implementación → tests → contrato → PR por módulo → revisión de coherencia → merge → cierre del issue
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
| 8. Merge | CI verde y revisión aprobada | `development` (rama por defecto y de producción; `main` es un placeholder de un commit con solo `README.md`) |

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
- [ ] La spec o el `design.md` están actualizados, o existe una issue/PR de specs enlazado abierto por un owner (o se explica por qué no aplica).
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
npx @fission-ai/openspec@2.2.0 validate --specs
```

> `--strict` no se usa: el formato híbrido escribe los escenarios con Gherkin en español
> (`DADO`/`CUANDO`/`ENTONCES`) y el validador estricto exige `WHEN`/`THEN` en inglés. El comando sin
> `--strict` valida las 24 specs y deja los avisos de Gherkin como advertencia, no como error.

## 8. Issues, escalamiento y documentación

Estas reglas aplican a los tres repositorios. Complementan la Regla 8 de §2 (cierre después del merge).

1. **Incoherencia issue ↔ spec.** Si una issue contradice la spec, pide comportamiento que la spec no
   define o mezcla alcance de dos módulos, **detente y no implementes**. Crea una issue en
   `G3-Chatbot-specs` asignada a `@Ankarmin` y `@MathiasTL`, con label `bloqueante` si impide avanzar,
   y enlaza la issue original como bloqueada. Incluye la spec y el requisito afectado, la
   contradicción exacta, el impacto y las opciones. La issue original no se cierra hasta que la
   decisión quede registrada en la spec.

   > **PRs en specs:** solo `@MathiasTL` y `@Ankarmin` abren PRs en
   > `G3-Chatbot-specs`. El resto del equipo reporta el cambio con una issue asignada a
   > `@Ankarmin` y `@MathiasTL`; no abre ramas ni PRs. Un workflow de guardia cierra los PRs de
   > autores no habilitados y deja el enlace a la plantilla de issue.
2. **Duplicados.** Antes de crear una issue, busca una abierta o cerrada. Si ya está resuelta, ciérrala
   con PR/commit/evidencia; si es obsoleta, ciérrala con motivo y enlace al reemplazo. No crees dos
   issues para el mismo trabajo.
3. **Contenido mínimo.** Toda issue debe tener un responsable, contexto, alcance, criterios de
   aceptación verificables y evidencia esperada. Si cruza repos, crea una issue por repo y una de
   coordinación; no dupliques el mismo alcance.
4. **Bloqueo externo.** Si depende de G2/G5/G6/G7, abre la issue en el repo del otro grupo con lo que
   necesitas y sus criterios de cierre, y enlázala desde tu issue. No la repliques en G3.
5. **Ramas y despliegue.** `development` es la rama por defecto y la de producción; `main` es un
   placeholder de un commit con solo `README.md`. Los PR van a `development`; no se promueve ni
   despliega desde `main`.
6. **Higiene del repo compartido.** No reescribas la historia compartida de `development` (force push
   o rebase publicado), no borres tags o ramas sin coordinar y no pegues secretos en issues o PRs.
7. **Documentación sin duplicados.** El estado se actualiza en los documentos existentes:
   `odd/tasks/hito-5.md` para Hito 5, `docs/auditoria-specs-2026-11.md` para specs vs código y
   `docs/slo-performance.md` para performance. No crees un documento paralelo.
