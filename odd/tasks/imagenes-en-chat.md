# Image attachments in chat (LLM vision) — SPEC-23

## Objective
Let the customer attach images to a chat message and have the LLM analyze them (for example "I am looking for shoes like these", or "this is the defect"), inside the current course scope. Audio stays out of scope.

## Problem / why
Today the LLM only receives text: images exist only as return evidence uploaded to Ventas (SPEC-21), `motor-conversacion` lists voice as out of scope, `busqueda-filtrado` lists image search as out of scope, and `docs/conversacion/privacidad.md` states that evidence never reaches the LLM. The team decided (2026-09-26) to include image understanding, using `gpt-6-luna` (OpenAI) and Supabase (free tier) for the database.

## Decisions (user, 2026-09-26)
- Images are analyzed by the LLM (vision), not only stored as evidence.
- Audio / voice: stays out of scope.
- LLM: `gpt-6-luna` behind the existing `LLMProvider` port (ADR-0005). Vision support and image token cost of this model are NOT verified: record as open question and risk.
- Database: Supabase free tier. PostgreSQL 18 on Supabase is NOT confirmed (the data model relies on native `uuidv7()`): record as open question, do not change the data model for it.
- Chat images need their own storage (the model provider does not act as storage; OpenAI retains API inputs 30 days for abuse monitoring). Use a private Supabase Storage bucket behind an `AttachmentStorage` port; the database keeps only references.

## Design defaults for the writer (change only with a reason)
- Limits: up to 3 images per message, `image/jpeg`, `image/png`, `image/webp`, max 5 MB each (aligned with SPEC-21). No PDF in chat.
- New spec: `openspec/specs/adjuntos-imagenes-chat/` (`spec.md` + `design.md`), SPEC-23, group Transversal, area `CNV`, epic EP-02, Hito 4 (after the Hito 3 core).
- The backend sends the image to the LLM as base64 read from storage; never a signed URL, never a public URL.
- The chat shows thumbnails in the history through short-lived signed URLs issued by the backend.
- Images share the same 12-message context window as text.
- No automatic redaction of sensitive content inside images: show a notice before the first upload and document the residual risk in `privacidad.md`.
- If the configured model has no vision support or the LLM fails: `DegradedMode` answers that the image could not be analyzed and keeps the text flow working.
- Retention of chat attachments: open item aligned with the 90-day conversation auto-archive; do not invent a TTL as decided.
- Image-based product search is the LLM turning the image into text criteria for the existing search tools (SPEC-06), not a visual-similarity engine.
- Artifacts in neutral professional Spanish (matching the specs repo); no voseo.

## Scope
- In: new SPEC-23, edits to SPEC-05 and SPEC-06 notes, new ADR-0019 plus amendments to ADR-0005/0006, data model table, product layer (epics, stories, traceability, scope, rules, privacy, integration contracts), diagrams.
- Out: audio, PDF in chat, visual-similarity search, automatic image redaction, application code.

## Route declaration
- Trigger: 10+ non-trivial documents (writer trigger). Route: delegated direct, one writer at a time (W1: T1–T3, W2: T4–T6), parent verifies with structural readback and `rg` consistency checks.

## Tasks
- [x] T1 — Create `openspec/specs/adjuntos-imagenes-chat/spec.md` and `design.md` (SPEC-23), using `solicitud-devolucion-cambio` as the format template. Evidence: spec.md and design.md created under `openspec/specs/adjuntos-imagenes-chat/`.
- [x] T2 — Update SPEC-05 (`motor-conversacion` spec + design): message with attachments, LLM receives images, degraded mode, rate limits; keep voice out of scope. Clarify the SPEC-06 "image search" exclusion. Evidence: `motor-conversacion` spec and design plus `busqueda-filtrado` spec updated with SPEC-23 cross references.
- [x] T3 — Add ADR-0019 (images as LLM input, storage, privacy) and amend ADR-0005 / ADR-0006 and the ADR index; update `docs/arquitectura/c4.md` if a new container/port appears. Evidence: ADR-0019 created; ADR-0005 and ADR-0006 amended; ADR index, c4.md and arquitectura README updated.
- [x] T4 — `docs/modelo-datos.md`: new `adjunto` table (message-level attachment reference) with keys, constraints, ON DELETE, indexes; update open items. Evidence: `adjunto` table, ER block and 2 open items added to modelo-datos.md; clarifying notes added to ADR-0013 and solicitud-devolucion-cambio spec; design.md column/index summary aligned (actualizado_en, index set).
- [x] T5 — Update `docs/diagrams/mer-conceptual.*` and `mer-logico.*` (backup the `.excalidraw` files to `~/.excalidraw-backups/ChatbotTaller/` first; export `.excalidraw` + `.svg`).
    - Evidence: ADJUNTO added to both MERs (conceptual: entity, 4 attributes, `sube`/`lleva` relationships; logical: 12-column table, 2 crow's-foot FKs, mensaje link dashed). 13 -> 14 entities/tables vs backups, no existing element changed except the logical title moved up; both `.svg` regenerated and visually checked. Commit pending user confirmation.
- [x] T6 — Product layer: `docs/producto/epicas.md` (EP-02 counts), `historias/EP-02-conversacion.md` (new stories), `trazabilidad.md`, `alcance.md` (scope, risks, open questions), `reglas-negocio.md`, `docs/conversacion/privacidad.md`, `docs/conversacion/intenciones.md` if needed, `docs/contratos-integracion.md`, README spec index and totals. Evidence: EP-02 now 19 stories / 94 pts (HU-CNV-14..19, RN-CNV-22..29); epicas, historias, trazabilidad, alcance, reglas-negocio, producto/README, privacidad, intenciones note, D-16, kpis, flujos, contratos-integracion (section 2.1.1 + 2 error codes) and root README updated.
- [x] T7 — Consistency check: `rg` for stale statements ("22 specs", "no llega al LLM", text-only context, totals of stories/points) and fix. Evidence: totals recomputed by script (23 specs, 109 requirements, 325 scenarios, 105 stories, 419 pts, 162 rules); anchors and RN references verified; no voseo found in touched files; remaining "22 specs" only inside ADR-0018 and c4.md open item quoting the old README.

## Acceptance criteria
- SPEC-23 has requirements with scenarios, non-functional requirements, and a design with a task breakdown, in the same structure as the other specs.
- No document still says the LLM never receives images, or counts 22 specs / 99 stories / 385 points without the update.
- Open questions (model vision support, PostgreSQL 18 on Supabase, retention) are recorded, not silently decided.
- No voseo or Rioplatense slang in any artifact.

## Progress
- 2026-09-26: exploration done; document created. Engram mirror `odd/imagenes-en-chat/tasks`: see Delivery/mirror note.

## Verification
- TDD: not applicable (documentation-only work). Checks: structural readback of every touched file and `rg` consistency checks (T7). Native review: the user declined review for the previous candidate; this candidate is assessed again when it exists.

## Delivery
- Forecast: about 800–1200 authored changed lines (docs). Delivery strategy: `ask-on-risk` (default); nothing is pushed.
- Commit pending user confirmation (user rule). Branch: `docs/capa-producto`.
- Proposed message: `docs(chat): add image attachments with LLM vision (SPEC-23)`.
