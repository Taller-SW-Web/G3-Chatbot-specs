# Audit 2026-11 fixes

## Objective
Fix the findings of the 2026-11-21 three-repo audit (specs 34, backend 27, frontend 18 findings).

## Baselines
specs main 059069f, backend development b7e59bf, frontend development 7432d46.

## Constraints
- Backend/frontend: branch `fix/audit-wave-0-1` from `development`; specs: direct to main.
- No commit/push/PR without explicit user confirmation. Conventional commits, no AI attribution.
- Remote/ops actions (Railway, Vercel, Supabase dashboards) are out of scope for agents; listed as ops follow-ups.
- TDD mode: not configured; every work unit ships with the proving test named in the plan (regression test first where feasible).
- Artifacts in English; Spanish docs in neutral Spanish (no voseo).

## Batch 1 (route: delegated direct, one writer per repo, parallel across repos)
- [x] BE-0.1 Payment replay truthfulness + STOCK_INSUFICIENTE/ERROR_VENTAS mapping (BE-AUD-01, 05)
- [x] BE-1.1 Production-safe settings (BE-AUD-06, 07, 14, 25, 26)
- [x] BE-1.2 Payment row lock + atomic attempt cap (BE-AUD-03)
- [x] BE-1.3 ExpirarCheckouts sweeper + Ventas cancellation (BE-AUD-04)
- [x] BE-1.4 Supabase Storage attachment adapter (BE-AUD-02)
- [x] BE-1.7 /health/ready with DB check (BE-AUD-16)
- [x] FE-0.2 Logout calls POST /sesion/logout, clears persisted state (FE-AUD-02, 05 part)
- [x] FE-0.3 Safe `destino` redirect (FE-AUD-03)
- [x] FE-1.5 Security headers + CSP Report-Only (FE-AUD-01)
- [x] FE-1.6 Build guard for API_PROXY_TARGET + README (FE-AUD-07)
- [x] SP-0.5 Contract error table: replay semantics + new codes (SPEC-AUD-09 part)
- [x] SP-2.1 Resolve contradictions aligned to implemented behaviour (SPEC-AUD-08, 11, 12, 14, 26)
- [x] SP-1.4 Document attachments storage + GET /chat/adjuntos/archivo (SPEC-AUD-01, 10)
- [x] SP-2.2 Archive alinear-specs-* changes; ADR-0015 superseded note (SPEC-AUD-02, 04, 33)

## Batch 2 (after batch 1 commits)
Waves 2 and 3 of the consolidated plan (BE 2.7-2.10, 3.3, 3.6; FE 2.4-2.6, 3.2, 3.4, 3.5, 3.8; SPECS 2.3, 3.1, 3.7).

## Ops follow-ups (user)
- Confirm Railway APP_ENV=production, MODO_QA unset, COOKIE_SECURE=true (BE-AUD-06).
- Create Supabase Storage private bucket + set ATTACHMENT_STORAGE vars after BE-1.4 merges.
- Set API_PROXY_TARGET on Vercel (already required) before FE-1.6 deploy.

## Progress / evidence
- Engram mirror: pending (ambiguous project in workspace root).
- 2026-11-21 FE batch 1 done on fix/audit-wave-0-1 (uncommitted, commit pending user confirmation): typecheck pass, lint 0 errors/4 baseline warnings, test 784/785 (known checkModules.test.ts:166), modules:check pass, build pass. Parent spot check: 3 new test files 43/43 pass. Open: CSP uses 'unsafe-inline' (nonces would make static routes dynamic), img-src https:, no report-uri.
- 2026-11-21 SPECS batch 1 done (uncommitted, archive moves staged via git mv; commit pending user confirmation): 42 files +295/-80; link check on touched files: only 2 pre-existing broken anchors (SPEC-AUD-16); no voseo. Decisions aligned to backend code (dup return = pedido+motivo+lineas, OTP sliding, chat_rt/chat_chg Strict, chat_sid Lax). Ventas deltas not re-applied (baseline newer). Open: ATTACHMENT_STORAGE pending BE-1.4, Idempotency-Key + different forzar, issue #9 reply, casos-prueba-hito-4 regen.
- 2026-11-21 BE batch 1 done on fix/audit-wave-0-1 (uncommitted, commit pending user confirmation): 21 files +647/-117 plus 8 new; pytest unit+integration 1369 passed / 63 skipped (PG18 integration incl. new payment concurrency test and migration NOT run: no docker, local PG 16); ruff pass; check_modules OK; alembic 1 head 20261122_mod_chk_one_approved; openapi check 47 paths. Parent spot check: unit 1367 passed. RISK: production settings guard refuses boot if Railway APP_ENV=production with unsafe values; verify Railway vars before merging. Supabase adapter only tested with mocked transport.
- 2026-11-21 Batch 1 commits (local, not pushed):
  - backend fix/audit-wave-0-1: cd434ff (BE-0.1), 5f469fd (BE-1.1, includes all .env.template hunks), 386f892 (BE-1.2), f303629 (BE-1.3), 3f64fa0 (BE-1.7), e4faadf (BE-1.4). Checks: pytest unit+integration on postgres:18 1432 passed; alembic up/down/up OK, 1 head; ruff, check_modules, openapi --check pass. Pending user confirmation: staged test fix `test(mod-checkout): expect atomic attempt cap to return None at the limit`.
  - frontend fix/audit-wave-0-1: 0136cca (FE-0.2), c441e71 (FE-0.3), 9f1395a (FE-1.6), 768e89e (FE-1.5). Checks: typecheck, modules:check, build pass; lint 0 errors/4 warnings; test 785/785 with the uncommitted checkModules fix. E2E not run. Pending user confirmation: `test(shared): make checkModules allowlist test self-contained`.
  - specs main: commits listed in git log after this entry (SP-0.5, SP-2.1, SP-1.4, SP-2.2 + this document).
- Next step: user decides push/PRs; ops checks of Railway vars before merging backend; then batch 2.
