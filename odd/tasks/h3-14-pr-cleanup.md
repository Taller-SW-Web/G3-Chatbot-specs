# H3-14 PR cleanup (backend #43, frontend #21)

## Objective
Close the remaining review findings on Diego's H3-14 session PRs so both can be merged into `development`.

## Why
Re-review on 2026-10-16 found the security and architecture items resolved, but some blocking items were still open. The team lead decided to finish them directly on Diego's branches instead of another review round. The SPEC-24 rating commit (014319d) and the sidebar commit (dd5c7bb) are accepted inside #21 as a declared visual prototype.

## Scope
- Backend branch `feature/h3-14-session-auth` (PR #43).
- Frontend branch `feature/h3-14-session-auth` (PR #21).
- Out of scope: cart merge on login and `accionPendiente` handling (SPEC-03 Req. 3 and 4), declared as deferred in both PR bodies. SPEC-24 CSAT submission stays with its owner.

## Constraints
- Push directly to Diego's branches (authorized 2026-10-16). Every commit and push needs user confirmation.
- No force push; integrate `development` with a merge commit.
- Code and docs in English; PR text in neutral Spanish.

## TDD
Mode: not configured (no project or session setting). Ordinary functional checks: backend `pytest -q`, frontend lint, typecheck and tests.

## Tasks
- [x] B-1 Merge `development` into backend branch and resolve the `problem.py` / `module_errors.py` conflict (single `ModuleUnavailableError` definition). Route: delegated (backend writer).
- [x] B-2 Forward `canal` on login to Security; clear the challenge cookie on the MFA 403 path. Route: delegated (backend writer).
- [x] F-1 Refresh only on an invalid-token 401; exclude `/sesion/mfa/*` from refresh. Route: delegated (frontend writer).
- [x] F-2 Interceptor tests: single replay, no loop on `/sesion/refresh`, logout when refresh fails. Route: delegated (frontend writer).
- [x] P-1 PR #43 body with deferred scope.
- [x] P-2 PR #21 conventional title and body: deferred scope, SPEC-24 and sidebar as visual prototype.

## Acceptance criteria
- Backend PR #43 mergeable, suite green including JWT/JWKS tests.
- Frontend PR #21 lint, typecheck and tests green.
- Both PR bodies declare the deferred scope.

## Progress
- 2026-10-16: document created; writers launched.
- 2026-10-16: B-1, B-2, F-1, F-2 done in scratchpad worktrees (uncommitted). Backend `pytest -q`: 562 passed, 38 skipped. Frontend: lint 0 errors (3 pre-existing warnings), typecheck clean, 38 tests passed. F-1 keys refresh on `401 TOKEN_INVALIDO` (inicio-sesion spec.md:134). B-2 adds optional `canal` to login (not named in SPEC-03 for login; mirrors `/sesion/mfa/solicitar`). Commits pending user confirmation.
- 2026-10-16: committed and pushed with user confirmation. Backend 4caebcc (merge, B-1) and 1a3bb07 (B-2) on feature/h3-14-session-auth. Frontend 920cd96 (F-1, F-2). PR #43 body and PR #21 title/body updated (P-1, P-2). Both PRs MERGEABLE.
- 2026-10-16: David's backend #46 re-reviewed (ownership check, ports, 409 VARIANTE_REQUERIDA) and approved; #46 combined with #43 had no conflicts, 567 tests passed. Approved #46, #43, #21 and squash-merged in order: backend #46 (7550f84), backend #43 (dd3cb2f), frontend #21 (65523eb). CI on `development` green in both repos.

## Next step
Done. Follow-ups: unify MODULO_NO_DISPONIBLE vs SERVICIO_NO_DISPONIBLE; SPEC-03 deferred scope (cart merge on login, accionPendiente); SPEC-24 CSAT with its owner.
