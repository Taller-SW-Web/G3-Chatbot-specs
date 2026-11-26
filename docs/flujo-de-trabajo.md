# Flujo de trabajo y rol de las specs

> Norma operativa del Canal Chatbot. El resumen para agentes está en [`AGENTS.md`](../AGENTS.md);
> la arquitectura, en [`arquitectura/modularizacion.md`](arquitectura/modularizacion.md).

## 1. Qué es una spec y qué no

En este repositorio, **spec** significa la pareja `openspec/specs/<capacidad>/spec.md` +
`design.md`:

- `spec.md` describe **comportamiento observable**: propósito, alcance, requisitos con escenarios
  DADO/CUANDO/ENTONCES, requisitos no funcionales y criterio de completitud. No describe clases ni
  carpetas.
- `design.md` describe **cómo se integra**: endpoints propios y de otros módulos, componentes de UI,
  tablas, jobs y desglose de issues.

Las specs **no son documentación de estado del código**. Si el código y la spec difieren, la spec
sigue siendo la fuente de verdad del comportamiento y el código es el que se corrige o el que obliga
a un *spec delta*. La única excepción es una decisión de producto explícita: entonces se actualiza la
spec y se registra la decisión.

Documentos que **no** son specs y no las reemplazan: `docs/producto/` (alcance, épicas, historias,
reglas de negocio), `docs/conversacion/` (persona, flujos, KPIs), `docs/arquitectura/` (C4 y ADR) y
`README.md` (índice y convenciones).

## 2. El ciclo, paso a paso

### Paso 0 — Elegir el módulo

Consulta el mapa de [`modularizacion.md §2`](arquitectura/modularizacion.md#2-los-8-módulos) y el
`MODULE.md` del módulo. Si la capacidad es nueva, se crea el módulo en **ambos** repos con el mismo id;
no se inventa un id distinto ni se mete en `shared/`.

### Paso 1 — Leer la spec antes de tocar código

Lee `spec.md`, `design.md` y el ADR aplicable. Si el cambio no está cubierto, escribe primero el
delta: un requisito nuevo, un escenario nuevo o una corrección de contrato. No empieces por el código.

### Paso 2 — Implementar en el módulo

- Backend: `adapters/http` (DTO y router) → `application` (caso de uso) → `domain` (regla pura) →
  `ports` si hace falta. `module.py` cablea y `public.py` expone solo lo que otro módulo puede usar.
- Frontend: `ports` → `adapters` → `application` → `ui`; el endpoint se declara en
  `module.manifest.ts`. La ruta de `src/app/**/page.tsx` es un wrapper.

Regla de oro: **el caso de uso no importa FastAPI, httpx, SQLAlchemy ni `os.environ`**; el dominio no
importa frameworks. Si necesitas un dato de otro módulo, usa su `public.py` o una capacidad.

### Paso 3 — Tests

Cada escenario tocado tiene al menos una prueba automatizada que lo referencia por nombre. Añade:

- Unitario de la regla pura o del caso de uso.
- Integración del router con el módulo externo mockeado (`respx`) o la base de datos de prueba.
- Contrato: ruta y payload en `tests/unit/shared/api-rutas-contrato.test.ts` si el adapter cambió.

### Paso 4 — Contrato y manifiestos

- Backend: `python scripts/export_openapi.py` y `python scripts/export_openapi.py --check`.
- Frontend: `pnpm modules:sync` y `pnpm modules:check`.
- Si cambió el DAG, actualiza `modules.manifest.json` en ambos repos y la tabla de
  [`modularizacion.md §3`](arquitectura/modularizacion.md#3-dag-de-dependencias).

### Paso 5 — PR por módulo

Un PR toca un solo `mod-*`. Si toca `shared/`, lleva la etiqueta `cross-modulo` y revisión del owner de
plataforma. El PR incluye la spec delta en el mismo diff.

### Paso 6 — Revisión de coherencia

Antes de aprobar, el revisor comprueba:

- [ ] ¿La spec describe lo que hace el código, incluyendo estados, errores y campos?
- [ ] ¿Contradice una spec previa, un estado ya cerrado o un ADR?
- [ ] ¿El módulo es el dueño correcto? ¿Importa el interior de otro módulo?
- [ ] ¿El contrato (OpenAPI, manifiesto, `public.py`/`public.ts`) está actualizado?
- [ ] ¿Los tests cubren los escenarios nuevos y los de borde?
- [ ] ¿Hay secretos o cambios fuera del módulo?

Si hay una decisión de producto pendiente (por ejemplo, si se implementa la verificación de celular o
se retira del contrato), **no se inventa**: se registra en la auditoría o en el issue y se bloquea el
merge hasta que producto decida.

### Paso 7 — Merge

CI verde + revisión aprobada. El merge es squash y el mensaje sigue Conventional Commits
(`feat(mod-cart): ...`, `docs(specs): corrige drift de ...`). `development` es la rama por defecto y la
que despliega producción; debe quedar siempre desplegable. `main` es un placeholder de un commit con
solo `README.md` y no recibe promociones.

### Paso 8 — Cierre del issue

Un issue **no se cierra como completado** hasta que el PR que lo resuelve esté mergeado en
`development` y la verificación o evidencia esté registrada. El comentario de cierre cita el PR, el
commit y la prueba (CI, test o verificación manual). Un PR abierto o una rama con el cambio **no**
justifican el cierre.

Excepciones: duplicado, obsoleto o no aplicable. Se cierran con el motivo explícito y, si corresponde,
el enlace al issue o PR que los reemplaza; nunca con `completed` si el trabajo sigue pendiente.

## 3. El spec delta obligatorio

Un *spec delta* es el cambio mínimo en la spec que refleja el avance del código. Ejemplos:

| Cambio de código | Spec delta |
|---|---|
| Se renombra un campo de respuesta | Actualizar `design.md` y el escenario que lo menciona |
| Se añade un estado o un error | Añadir el estado a la tabla y un escenario de borde |
| Se implementa un requisito que estaba pendiente | Marcar el requisito como cubierto y actualizar el criterio de completitud |
| Se decide no implementar algo | Moverlo a «Fuera de alcance» con la decisión y el motivo |
| Se cambia una ruta o un tag | Actualizar `design.md`, el manifiesto y el OpenAPI |

El delta va en el **mismo PR** que el código. Un PR de código sin delta se rechaza en la revisión de
coherencia, salvo que el cambio sea puramente interno y no altere comportamiento, contrato ni estados.

Un **cambio de comportamiento nuevo** se tramita primero en `openspec/changes/<cambio>/` (propuesta,
specs delta, diseño, tareas, verificación y archivo). Una **corrección de drift** o un avance que ya
existe en el código se aplica directamente a `openspec/specs/` en el mismo PR, porque no cambia el
comportamiento: solo pone la spec al día.

## 4. Un PR por módulo y `shared/`

| Situación | Regla |
|---|---|
| Cambio en un módulo | Un PR, un `mod-*`, sin archivos de otro módulo |
| Cambio que cruza módulos | Se parte en PRs por módulo; si el contrato cambia, primero el PR del módulo dueño |
| Cambio en `shared/` | Etiqueta `cross-modulo` + revisión del owner de plataforma + justificación de por qué no va en un módulo |
| Cambio de un módulo que necesita otro | Se usa `public.py`/`public.ts` o una capacidad; nunca un import profundo |
| Cambio de manifiesto | Un PR de plataforma; actualiza ambos repos si cambia el DAG |

Owners actuales (tomados de los manifiestos):

| Módulo | Owner |
|---|---|
| Todos los módulos | @Taller-SW-Web/chatbot |

La aprobación de PRs la dan los code owners `@MathiasTL` y `@Ankarmin`. El ruleset “Code owners con bypass Mathias/David” exige 1 aprobación + code owner review al resto del equipo; Mathias y David tienen bypass `pull_request` para mergear sus propios PRs sin otra aprobación. Los checks de CI siguen obligatorios para todos (`enforce_admins=true`, `strict=true`). El ownership de módulos sigue siendo del equipo `@Taller-SW-Web/chatbot`.

## 5. Definition of Done

Un cambio está listo cuando:

- [ ] La spec y el diseño describen el comportamiento real, sin contradicciones.
- [ ] El código está en el módulo correcto y las fronteras pasan los gates.
- [ ] Los tests cubren los escenarios tocados y el CI está en verde.
- [ ] OpenAPI y manifiestos están regenerados y validados.
- [ ] La revisión de coherencia está hecha y no hay decisiones de producto abiertas sin registrar.
- [ ] No hay secretos ni cambios fuera del alcance del PR.

## 6. Mantenimiento de la auditoría

La auditoría [`auditoria-specs-2026-11.md`](auditoria-specs-2026-11.md) es el registro vivo del drift
entre specs y código. Se actualiza:

- Cuando se corrige una spec: se cambia el estado a ✅ y se anota el PR.
- Cuando se implementa un hueco: se mueve de «cambios de código pendientes» a «resuelto».
- Cuando producto decide: se anota la decisión y se actualiza la spec en el mismo cambio.
- En cada hito: se revisan las 24 capabilities y se recalculan los conteos.

La regla es simple: **si la auditoría y la spec discrepan, manda la spec; si la spec y el código
discrepan, manda la spec y se corrige el código o se marca la decisión.**
