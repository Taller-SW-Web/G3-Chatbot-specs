# Logical data model — Chatbot channel

## Objective
Turn the table-level data model (`docs/modelo-datos.md`) and the conceptual ERD (`docs/diagrams/mer-conceptual.*`) into a PostgreSQL 18 logical model: keys, types, constraints, FK delete behavior and query-driven indexes, plus a crow's-foot ERD.

## Problem / why
The backend is greenfield (SQLAlchemy 2 + Alembic, ADR-0001) and `modelo-datos.md` has gaps that would leak into migrations: missing `creado_en`/`actualizado_en`, `outbox` without timing columns, `devolucion_ref.evidencia_refs` duplicating `evidencia.devolucion_id`, a provisional idempotency key on `notificacion`, and no stated indexes.

## Scope
- In: logical model in `docs/modelo-datos.md`, logical ERD `docs/diagrams/mer-logico.excalidraw` + `.svg`.
- Out: DDL / Alembic migrations (physical phase), retention TTLs (open ⚠️ in `docs/conversacion/privacidad.md`).

## Constraints and decisions
- PostgreSQL 18; `uuid DEFAULT uuidv7()` PKs (user decision, 2026-09-25).
- CARRITO 1:N CHECKOUT, retries allowed (user decision, 2026-09-25).
- `reclamo_ref.pedido_id` / `devolucion_ref.pedido_id` are NOT FKs: claims/returns pick orders from Ventas (`creacion-reclamo/design.md:12`, `solicitud-devolucion-cambio/design.md:12`), which may not exist in `pedido_ref`.
- Artifacts in neutral Spanish, matching the existing specs repo.
- TDD: not applicable (documentation-only work); checks are structural readback.

## Tasks
- [x] T1 — Rewrite `docs/modelo-datos.md` as logical model (route: inline, single file, design resolved in session).
- [x] T2 — Crow's-foot logical ERD in Excalidraw, export `.excalidraw` + `.svg` (route: inline, generator in session scratchpad).

## Acceptance criteria
- Every table has PK, NOT NULL/CHECK/UNIQUE rules, FK `ON DELETE` choice, and indexes justified by a named query.
- Every query from the specs mapping has an index or an explicit "scan is fine" note.
- Diagram renders without truncated text or overlaps; matches the document.

## Progress
- Engram mirror `odd/modelo-logico-datos/tasks`: PENDING (ambiguous_project between g3-chatbot-backend/frontend; resync once resolved).
- 2026-09-25: exploration done (query patterns, stack, inconsistencies). Document created.
- 2026-09-25: T1 done. Evidence: per-table structural check (timestamps vs insert-only, FK ON DELETE) passed for 13 tables. Accepted changes: FTS moved from `conversacion` to `mensaje.busqueda` + `conversacion.titulo_busqueda`; dropped `checkout.pedido_id` and `devolucion_ref.evidencia_refs`; `notificacion` key fixed as UNIQUE (pedido_id, numero_reenvio) + CHECK; open-cart uniqueness includes EN_CHECKOUT; one live checkout per cart via partial unique index; outbox timing columns added.
- 2026-09-25: T2 done. Evidence: overlap check passed, screenshot reviewed (no truncation/crossings), exported `docs/diagrams/mer-logico.excalidraw` + `.svg`.
- Next: user review; then physical model (DDL + Alembic) in backend repo.

## Delivery
- Commit pending user confirmation (user rule). Branch: `docs/capa-producto`.
- Proposed: `docs(datos): add logical data model and ERD diagrams`.
