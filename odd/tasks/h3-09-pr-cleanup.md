# H3-09 PR cleanup (backend #47, frontend #26)

## Objective
Close the blocking review findings on Sebastián's H3-09 PRs (customer registration and email verification, SPEC-01 and SPEC-02) so both can be merged into `development`.

## Why
Review on 2026-10-16 found two blockers in each PR. The team must move on to phase 2, so the team lead decided to fix the blockers directly on Sebastián's branches, comment on the PRs and merge, instead of another review round.

## Scope
- Backend branch `feature/h3-09-auth` (PR #47).
- Frontend branch `feature/h3-09-auth` (PR #26).
- Out of scope (left as follow-ups in the PR comments): X-Forwarded-For trust on the public backend URL, neutral 409 detail in the BFF, unused `SecurityServiceTokenProvider` (skew 30 s vs 60 s, no lock), rate limiter eviction, weak fake `verify_mfa`, BFF field naming vs spec, 429 `SOLICITUD_EN_CURSO` copy, swallowed policy fetch error, accessibility details, component tests.

## Constraints
- Push directly to Sebastián's branches (authorized 2026-10-16). Every commit and push needs user confirmation.
- No force push; integrate `development` with a merge commit.
- Code and docs in English; UI copy and PR text in neutral Spanish (no voseo).

## TDD
Mode: not configured (no project or session setting). Ordinary functional checks: backend `pytest -q`, frontend lint, typecheck and tests.

## Tasks
- [x] B-1 Forward Security `400 VALIDACION` `errores[{campo, mensaje}]` and `422 POLITICA_INCUMPLIDA` detail through the BFF register endpoint (SPEC-01 "Errores de validación del servidor", "Política incumplida en el servidor"). Route: delegated (backend writer).
- [x] B-2 Fake Security login answers `401 CREDENCIALES_INVALIDAS` for unverified accounts, matching SPEC-02 Req. 3. Route: delegated (backend writer).
- [x] B-3 Merge `development` (5eb5213) into the backend branch. Route: delegated (backend writer).
- [x] F-1 Merge `development` into the frontend branch; resolve the `ChatbotApiAxiosAdapter.ts` import conflict. Route: delegated (frontend writer).
- [x] F-2 Block register submit while the fetched password policy is not met (SPEC-01 "Contraseña que no cumple la política"). Route: delegated (frontend writer).
- [x] F-3 Offer "Iniciar sesión" on `409 CORREO_NO_DISPONIBLE` (SPEC-01 "Correo no disponible"). Route: delegated (frontend writer).
- [x] F-4 Map server `errores[{campo, mensaje}]` and 422 policy detail to the form fields, matching B-1. Route: delegated (frontend writer).
- [x] P-1 Comment on #47 and #26 with the fixes and follow-ups; approve and squash-merge backend #47, then frontend #26.

## Acceptance criteria
- Backend PR #47 mergeable, `pytest -q` green.
- Frontend PR #26 mergeable, lint, typecheck and tests green.
- New tests cover B-1, B-2, F-2, F-3, F-4.

## Progress
- 2026-10-16: document created; writers launched.
- 2026-10-16: B-1..B-3 and F-1..F-4 done in scratchpad worktrees (branch `h3-09-fix`). Merge commits created locally, not pushed: backend c528c80, frontend 7e22d33 (import conflict in `ChatbotApiAxiosAdapter.ts`: kept `passwordPolicy` and `mapearHistorial`, dropped `MOCK_MENSAJES`). B-1 maps Security `nombres`/`apellidos` to `firstName`/`lastName` (inferred from `security_client.register`; no Security contract defines `campo`) and scrubs the submitted password from messages. Backend `pytest -q --ignore=tests/unit/test_jwt_validator.py`: 614 passed, 38 skipped (local venv lacks `cryptography`; CI installs it). Frontend: typecheck clean, lint 0 errors, vitest 267 passed, build OK. Fix commits pending user confirmation.

- 2026-10-16: committed and pushed with user confirmation. Backend 6c71a83 (B-1), 2858897 (B-2) on top of merge c528c80; frontend 7c8043b (F-2..F-4) on top of merge 7e22d33. CI green on both PRs. Review mode (RDD) off globally, no native review. Approved with follow-up comments and squash-merged: backend #47 (fd30846), frontend #26 (bac0839).

## Next step
Done. Follow-ups listed in the PR #47 and #26 approval comments.
