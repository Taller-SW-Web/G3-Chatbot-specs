# G7 Security integration

## Objective
Align our Seguridad (G7) integration with G7's real backend so customer registration, login, MFA, session and profile work with `MODULES_MODE=http` against `https://g7-auth-service.onrender.com/api/v1`.

## Problem
Our `SecurityClient`, its respx mocks and the Prism seed were written against an early mock contract. An audit on 2026-11-03 of `Taller-SW-Web/Modulo-de-Seguridad-Backend` (branch `develop`) found that real tokens are rejected (fixed issuer `auth-service`) and that registration, login, MFA verification, email resend, addresses and password policy use different field names or shapes. The client also sends `client_secret` as a header on every request, which would leak the secret to a real host.

## Why
Hito 4 requires authentication on screens and APIs; production still runs `MODULES_MODE=fake`. Leaving fake mode needs a client that matches the real service.

## Verified facts (2026-11-03)
- Discovery `GET /api/v1/auth/.well-known/openid-configuration`: issuer `https://g7-auth-service.onrender.com/api/v1/auth`, `jwks_uri` `.../api/v1/auth/.well-known/jwks.json`, RS256.
- Access token claims: `iss` (env `AUTH_ISSUER`), `sub`, `email`, `roles` (list, role `CLIENTE` exists in `R__catalogo_autorizacion.sql`), `permisos`, `tipo: "acceso"`, `iat`, `exp`, `jti`; no `aud`.
- `CanalOrigen` enum: `WEB, CHATBOT, RETAIL, MARKETPLACE`.
- Login `{correo, contrasena}`; MFA verify `{challengeToken, codigo}` (`[0-9]{6}`); resend `{correo}`.
- Register `{correo, contrasena, nombres, apellidos, celular (^\+51[0-9]{9}$), aceptaTerminos, canalOrigen}` -> 201 `{id, estado}`; 409 `CORREO_NO_DISPONIBLE`, 422 `POLITICA_INCUMPLIDA` with `errores[{regla, esperado}]`, 400 `VALIDACION`.
- Addresses `GET /usuarios/{id}/direcciones` -> `{"direcciones": [...]}`.
- Password policy `GET /password/politica` -> `{longitudMinima, requiereMayuscula, requiereMinuscula, requiereDigito, requiereCaracterEspecial, rechazaComunes, rechazaDatosPersonales, historial, caducidadDiasAdmin}`.
- `/auth/me` exposes `tipoDocumento` and `documentoEnmascarado` (no `ultimoDocumento`).
- New error codes: 403 `PASSWORD_CADUCADA`, 410 `OTP_EXPIRADO`, 401 `OTP_INTENTOS_AGOTADOS`, 401 `CODIGO_INVALIDO` (`intentosRestantes`).
- Introspection needs a service Bearer token with scope `tokens:introspeccion`.
- Unchanged and correct: verify email, OTP request, refresh, logout, JWKS path, problem+json parsing, service token (`POST /auth/token`, form-urlencoded).

## Scope
- Backend repo `G3-Chatbot-backend`, branch `fix/g7-security-integration` from `origin/development`.
- Frontend repo `G3-Chatbot-frontend` (registration form and password policy).
- Specs repo `G3-Chatbot-specs` docs.
- Out of scope: service token for Productos/Ventas/Despacho clients (P7), `X-Correlation-Id` format (P8), other modules' adapters.

## Constraints
- Commits only after explicit user confirmation.
- Artifacts in English; Spanish only where the contract uses Spanish field names.
- Starting point for T1: local stash `wip: configurable issuer + login dual fields (pre-G7 integration)`; its `jwt_validator.py` change is obsolete (development already delegates to `provide_access_token_validator`) and its dual-field login body is replaced by T2.

## Tasks
- [x] T1 Configurable issuer: `SECURITY_EXPECTED_ISSUER` setting, `expected_issuer` in `JwksTokenValidator`, wired in `container.py`; tests. Route: delegated (backend writer, 2+ files).
- [x] T2 Request field names (login, MFA verify, resend) and remove the `client_secret` mock header. Route: delegated.
- [x] T3 Registration: mandatory `nombres`, `apellidos`, `aceptaTerminos`, `celular` format, `id` response, 422 `POLITICA_INCUMPLIDA`. Route: delegated.
- [x] T4 Addresses `direcciones` key, password policy shape, `/auth/me` document fields, new error codes, introspection with service token. Route: delegated.
- [x] T5 Respx mocks, helpers and Prism seed aligned to the real contract. Route: delegated.
- [x] T8 Per-module modes: `SECURITY_MODE`, `PRODUCTS_MODE`, `SALES_MODE`, `DISPATCH_MODE` override `MODULES_MODE` so integrations switch one at a time. Route: inline (settings + mechanical container swap). Branch `feat/per-module-modes` stacked on `fix/g7-security-integration`. Checks: `ruff check .` passed, unit 675 passed. Commit `fbda7c4`, PR #58 stacked on #57 (CI only runs on PRs to development/main, so it runs after #57 merges and #58 is retargeted). `.env.template` not updated: the file is outside the agent's permissions.
- [x] T6 Frontend: terms checkbox, `+51` phone validation, password policy fields. Route: delegated (frontend writer).
- [x] T7 Specs: `contratos-integracion.md`, `inicio-sesion/spec.md` L166, ADR-0009 (issuer, `SERVICIO_INTEGRACION`). Route: delegated or inline depending on size.
- [x] T10 Codex review fix (2026-11-05), frontend #32: password policy rule identifiers. The frontend only maps `LONGITUD_MINIMA`/`MAYUSCULA`, while the #57 fixture uses `longitudMinima`/`requiereMayuscula`. Confirm the real G7 shape (Modulo-de-Seguridad-Backend) and align fixture, BFF and frontend. Route: delegated (writer, 2 repos).
- [x] T11 Codex review fix, backend #57 + frontend #32: G7 400 `VALIDACION` field names (`correo`, `celular`, `contrasena`, `aceptaTerminos`) are not mapped to form fields in `sesion.ts`. Route: delegated (same writer).
- [x] T12 Codex review fix, backend #58: refuse fake Seguridad in production unless explicitly enabled for a demo, and flag `SALES_MODE`/`DISPATCH_MODE` as having no HTTP adapter yet. Route: delegated (same writer).
- [ ] T9 Forward the customer's IP (`X-Forwarded-For`) and `User-Agent` from the BFF to Seguridad on login, registration and MFA calls, for G7's attempt log and audit. Blocked until G7 accepts it. Take the IP from the hop added by the trusted proxy (Vercel/Railway), not the client-supplied first value. Today `rate_limiter.client_ip` reads `X-Forwarded-For` only for the local rate limit; nothing is forwarded to G7.

## Acceptance criteria
- Backend unit tests and `ruff check .` pass; CI `test` job green.
- Every request body and parsed response in `security_client.py` matches the verified facts above.
- No request sends `client_secret` outside `POST /auth/token`.
- Frontend `lint`, `typecheck`, `test`, `build` pass.

## Checks
- TDD: not configured (same as hito-3). Functional checks: backend `ruff check .` and `python -m pytest tests/unit` (integration tests run in CI with PostgreSQL); frontend `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`.

## Delivery
- Strategy: ask-on-risk. Forecast: about 400 to 600 authored lines across backend and frontend; backend and frontend ship as separate PRs to `development`.

## Progress
- 2026-11-03: audit done, branch `fix/g7-security-integration` created from `origin/development` (793fbc1 + #55).
- 2026-11-03: T1-T5 done by one delegated backend writer (17 files, +490/-121). Parent fix after readback: an empty `SECURITY_CLIENT_SECRET` no longer breaks the whole Seguridad client in `http` mode; it only disables introspection (customer endpoints are public or use the holder token).
- Verification (parent spot check): `ruff check .` -> All checks passed; `python -m pytest tests/unit -q` -> 669 passed. Integration tests not run locally (no PostgreSQL; CI runs them). `ruff format` not enforced by CI and not applied to avoid unrelated churn.
- Backend contract for the frontend: registration phone accepts `^(\+51)?[0-9]{9}$` (normalized to +51); 422 `POLITICA_INCUMPLIDA` returns one `errores` row per rule `{campo, mensaje, regla, esperado}`; `/sesion/politica-contrasena` adds the Spanish policy fields and keeps the English aliases; login can answer 403 `PASSWORD_CADUCADA`; MFA `OTP_EXPIRADO` is exposed as 410 `CODIGO_VENCIDO`; `OTP_INTENTOS_AGOTADOS` and `CODIGO_INVALIDO` keep their codes.
- Backend commit: `036dd10` on `fix/g7-security-integration`, PR #57 to `development`. RDD off (global), ordinary checks only.

- 2026-11-03: T6 done by a delegated frontend writer on frontend branch `fix/g7-security-integration` (9 files, +148/-22): phone `^(\+51)?[0-9]{9}$` with hint, G7 rule ids (`LONGITUD_MINIMA`, `MAYUSCULA`, `MINUSCULA`, `DIGITO`, `CARACTER_ESPECIAL`, `CONTRASENA_COMUN`, `DATOS_PERSONALES`, `YA_UTILIZADA`) mapped to Spanish messages, policy reads Spanish fields with alias fallback (min length no longer hardcoded to 8), `PASSWORD_CADUCADA` message. Checks: `pnpm lint` 0 errors (4 pre-existing warnings), `pnpm typecheck` clean, `pnpm build` ok (writer); `pnpm test` under Node 22 (CI version) 298 passed (parent). Under local Node 26, 13 pre-existing tests fail from Node's experimental `localStorage`; environmental. Frontend commit `70a68f8`, PR #32 (frontend) to `development`.
- 2026-11-03: T7 done by a delegated docs writer (8 docs, issuer from configuration/discovery, A4 `SERVICIO_INTEGRACION` withdrawn, new Seguridad error codes). Parent correction: `/sesion/perfil` keeps exposing `ultimoDocumento {tipo, numeroEnmascarado}`, now sourced from `/auth/me` `tipoDocumento`/`documentoEnmascarado` with checkout fallback. Check: `rg 'auth-service|SERVICIO_INTEGRACION'` leaves only the G7 URL and withdrawn mentions. Specs commit pending user confirmation (direct to main).

- 2026-11-03: PO review of the G7 request. Confirmed: lockout is per account (fingerprint is an HMAC of the wrong password), IP and User-Agent are only logged and audited; `ventas:*` grants belong to `api-ventas` and `postventa:*` to `api-postventa`; `scope` is optional and space-separated. Request message updated with the one-token-per-API question, the deployed SHA, the production issuer confirmation and the notice that the chatbot does not consume `seguridad.usuarios` events. T9 added, pending G7's answer.

- 2026-11-05: T10-T12 done by one delegated writer. Commits (pushed): backend #57 `a77d24a`, backend #58 `8188ae1`, frontend #32 `f8be4d6`. Merged as admin 2026-11-05: backend #57 `565ff10`, frontend #32 `552be5d`, per-module modes via #61 `0037289` (#58 was auto-closed when its base branch was deleted; replaced by #61). Pending: `APP_ENV`/`ALLOW_FAKE_SECURITY` in backend `.env.template` (manual). G7 source (`develop`): `GET /password/politica` fields are `longitudMinima`, `requiereMayuscula`, ... (`credencial/adapter/in/web/PoliticaPasswordResponse.java`), so the fixture for that endpoint was already right. The 422 `errores[].regla` ids are the enum `ReglaPassword` (`credencial/application/dto/ReglaPassword.java`): `LONGITUD_MINIMA, MAYUSCULA, MINUSCULA, DIGITO, CARACTER_ESPECIAL, CONTRASENA_COMUN, DATOS_PERSONALES, YA_UTILIZADA`; `esperado` only on `LONGITUD_MINIMA` (`PoliticaPasswordService.java`, `RegistroController.java`). Real defect: our `_field_errors` dropped rows without `esperado`, and the 422 mock used camelCase ids. Fixed in backend worktree `wt-57` (branch `fix/g7-security-integration`): parser keeps `{regla}`, router omits `esperado` when absent, fixtures/tests use real ids. Frontend already mapped all 8 ids; added tests only.
- T11: G7 400 `VALIDACION` `errores[].campo` are `correo, contrasena, nombres, apellidos, celular, aceptaTerminos, canalOrigen` (`RegistroController.validar`). Normalized in the BFF (`SECURITY_FIELD_TO_BFF` in `session_router.py`) so the frontend keeps one vocabulary; tests per field. Frontend test covers the six BFF names.
- T12 (branch `feat/per-module-modes`): `Settings.app_env` (`APP_ENV`, default `development`) + `allow_fake_security` (`ALLOW_FAKE_SECURITY`); fake Seguridad with `APP_ENV=production|prod` raises at settings load unless opted in. Startup warns that sales/dispatch have no HTTP adapter. No auto-detection from `RAILWAY_ENVIRONMENT_NAME`, so current prod (`MODULES_MODE=fake`, no `APP_ENV`) keeps booting. `.env.template` not edited (denied by permissions).
- Checks: backend #57 worktree `ruff check .` clean, `pytest tests/unit -q` 677 passed; backend #58 `ruff check .` clean, 682 passed; frontend `pnpm lint` 0 errors (4 pre-existing warnings), `pnpm typecheck` clean, `pnpm test` 300 passed under Node 22 (Node 26 fails 14 localStorage tests, environmental).

## Next step
Send the updated request to G7. Merge backend #57 then #58 (retargeted), frontend #32. T9 after G7 answers.
