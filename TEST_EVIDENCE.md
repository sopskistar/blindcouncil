# BlindCouncil test evidence and commands

Evidence categories: **HERMES LOCAL** = real Hermes loading/dispatch/storage/CLI, **SYNTHETIC** = supporting fixture identities or in-memory PTB transport, **LIVE** = genuine external delivery/callback/user action, **PLANNED** = unexecuted. Do not collapse these categories into a single PASS.

## Verified history

| Evidence | Category | Actual result / limitation |
|---|---|---|
| `evidence/runtime.json`, `version-managed.stdout.log` | HERMES LOCAL | Official source `2c955c3…`, Hermes `vgit.2c955c3`, PM Python 3.14.9 |
| `evidence/blindcouncil-policy-final.stdout.log` | HERMES LOCAL + SYNTHETIC IDs | 10 policy cases passed; unauthorized/allowlist/message/duplicate/unanimity/mixed/access checks |
| `evidence/blindcouncil-restart-final.stdout.log` | HERMES LOCAL + SYNTHETIC round | Fresh process recovered approved aggregate; not a live Telegram gateway restart |
| `evidence/telegram-gate/live-gate-preparation-sdk.stdout.log` | SYNTHETIC PTB | 6 cases passed; in-memory Bot API and scripted Updates; zero real Telegram calls |
| `evidence/telegram-gate/synthetic-receipt-rejection.stdout.log` | HERMES LOCAL | 2 synthetic receipts, 0 native; callback gate BLOCKED as intended |
| `evidence/telegram-gate/live-gate-doctor.stdout.log` | HERMES LOCAL | Doctor exit 0; plugin loaded/registered |
| `evidence/telegram-gate/validator.stdout.log` | HERMES LOCAL validation | Exit 0; safe scan, capability declarations matched; native factory in-process only |
| `evidence/telegram-gate/readiness.stdout.log` | HERMES LOCAL preflight | Exit 2; fixture IDs/missing explicit allowlist; correctly BLOCKED at that time |
| `evidence/policy-regressions-20261109-r2/result.json`, `stderr.log` | SYNTHETIC supporting tests + real Hermes SQLite | **15 passed** in separate per-test homes; production source unchanged; temporary state removed |
| `evidence/policy-regressions-20261109/stderr.log` | Initial supporting run | 15 passed with an unclosed legacy-fixture connection warning; fixture fixed, warning absent in r2; original log retained |
| `evidence/packaging-inspection-20261109/result.json` | Read-only inspection | Prototype manifest/entrypoint/README present; no license, supported release floor or dependency declarations; final publication not ready |
| `evidence/blindcouncil-sdk.stderr.log` | SYNTHETIC initial failure | Test transport lacked PTB `read_timeout`; fixed, later runs passed; failure preserved |
| `REPORT.md`, `evidence/summary.json` | Historical feasibility | TraceFork CONDITIONAL; model A/B absent; all native capture/model limitations retained |

Historical ledgers: `evidence/commands.jsonl` and `evidence/telegram-gate/commands.jsonl` contain exact argv, timestamps, environment overrides, exit codes and transcript paths. Original logs may contain trailing whitespace from Hermes and must not be “polished.” The original integrity manifest is a historical snapshot, not a claim that subsequently edited source hashes never change.

## Current live evidence

**LIVE two-account Approve/Approve PASS:** round `38378f7fbe90`, both real private deliveries, first native receipt observed PENDING, second native receipt APPROVED. Official audit: two native receipts, two configured distinct identities matched, zero synthetic receipts. The user corroborated actual button presses and the owner result notification. Evidence: `evidence/native-telegram-20261109/round-1-approved-summary.json`, `round-1-first-vote.stdout.log`, `round-1-two-votes.stdout.log`, `round-1-user-confirmation.json`. Readiness and real native factory/polling startup are also recorded there. A single approved host-context gateway remains running.

**LIVE duplicate protection PASS:** original approved round remains two responses/two receipts; user saw the duplicate acknowledgement and observed no extra result message. This notification observation is user-confirmed, not an outgoing-ledger guarantee. Evidence: `round-1-duplicate-summary.json`.

**LIVE Approve/Reject PASS:** `cb54bed1b2b7` was pending with Account 1's single native response, then Account 2 genuinely rejected. Two native receipts match both distinct configured identities, callback/update IDs differ, aggregate REJECTED, and user confirmed Account 1's actual final notification. Evidence: `round-3-first-response-summary.json`, `round-3-rejected-audit.stdout.log`, `round-3-rejected-summary.json`. One duplicate attempt before rejection is preserved in `round-3-attempt-audit.json`; it added no vote. User reports no intentional extra taps; cause is unverified.

**HERMES LOCAL cancellation / real restart PASS:** mistaken incomplete round `6917ad5b2a4e` had Account 2's one genuine approval and remained pending. Graceful native restart and transactional schema-v1 migration preserved its and the earlier approved round's exact receipt fingerprints. Registered CLI cancellation changed only the incomplete round to CANCELLED, preserving its response/receipt. Private backup is ignored; .env/config hashes unchanged. Evidence: `lifecycle-deployment.json`, `runtime-restart.json`, `preservation-after-restart.json`, `round-2-cancel.stdout.log`, `preservation-after-cancel.json`. The genuine late cancelled callback is now verified in the recovery section below; real expiry remains pending.

No complete MVP/all-tests PASS is claimed. Receipt metadata is corroborated with actual gateway/user actions; it is not independent proof. REJECTED round restart persistence also PASS: `round-3-after-restart-audit.stdout.log`, `round-3-after-restart-summary.json`, `rejection-runtime-restart.json`; exact receipts unchanged, still two responses/REJECTED. Genuine unauthorized/wrong-message callbacks and remaining lifecycle gates are unverified.

Required LIVE cases: approve/approve → APPROVED; approve/reject → REJECTED; unauthorized → DENIED; duplicate → unchanged count; wrong decision/message → DENIED; expiry/cancel → no new vote; native restart → persisted decision. Expiry/cancel are implemented with supporting tests and real operator cancellation; actual late-button rejection remains unverified. Detailed clicks: `LIVE_GATE.md`. Record each native process start/stop, round, sanitized result and corroborating actual user action when it happens. Raw actor IDs/choices/private logs remain local, not public Git artifacts.

## Reproduction commands

From the project root, using the existing selected runtime:

```bash
python3 probes/hermes_local.py --version
python3 probes/hermes_local.py plugins doctor "$PWD/blindcouncil" --ci
python3 probes/hermes_local.py plugins validate "$PWD/blindcouncil" --install-deps
python3 probes/hermes_local.py blindcouncil readiness
python3 probes/hermes_local.py gateway status
```

Readiness intentionally exits 2 until real configuration is ready. It never establishes a live pass. **Do not rerun setup now:** it is complete and one native gateway is active (current process in HANDOFF.md). Follow LIVE_GATE.md; do not start a second poller or blindly replace an existing service.

Evidence recorder example (choose a new name and new directory):

```bash
python3 probes/run_evidence.py --evidence-dir evidence/master-checkpoint doctor plugins doctor "$PWD/blindcouncil" --ci
```

Do not record the interactive wizard/token input. Do not print the complete composed PM environment. Never overwrite prior transcripts or append new phases into the original feasibility ledger. Sanitize real service evidence before committing; keep real configurations/participant data ignored.

## Supporting tests: isolated from setup

Existing CLI `probe` and `sdk-probe` mutate their current plugin database. They must not be run against the live user-configured home during setup. `probes/run_supporting_tests.py` uses PM's selected interpreter/dependencies with distinct temporary per-test homes, a minimal credential-free child environment and no Telegram calls. It only reads committed PM environment metadata for runtime selection; the tests do not load live configuration. Output directories must be new.

Earlier supporting command (preserved):

```bash
python3 probes/run_supporting_tests.py --evidence-dir evidence/policy-regressions-20261109-r2
```

The recorded result is exit 0 with 15 test methods, including eight policy combination/order subcases within one method. Source SHA-256 values, selected interpreter and logs are in `result.json`; this is not native Telegram evidence. A future rerun must choose a different directory.

Coverage now exercised: all yes/no combinations in both response orders; unauthorized actor; allowlist revocation/restoration; wrong private chat/cross-round message/unknown round/invalid choice; immutable duplicate answer/receipt; eight competing submissions for one actor; concurrent submissions/retries from both actors; forced receipt-trigger storage failure with full vote/receipt rollback and recovery; owner-only aggregate; no promotion of synthetic/legacy receipt origins; legacy data preserved under additive schema; fresh-process pending then approved reads. The expected DELETE-to-WAL notice is emitted for the temporary legacy database, not the live home.

Latest supporting command:

```bash
python3 probes/run_supporting_tests.py --evidence-dir evidence/lifecycle-regressions-20261109-r1
```

**25 tests PASS**, actual Hermes SQLite, synthetic IDs/temp homes, zero real Telegram API calls or live configuration loading. Adds cancellation authorization/idempotency/receipt preservation/late rejection, expiry boundary, terminal stability, input validation, audited transport retries, cancel/response race and future-schema rejection; includes eight in-memory PTB routing cases. The legacy fixture's WAL notice remains scoped to temporary storage. Logs/source hashes: `evidence/lifecycle-regressions-20261109-r1/`.

Official updated-source checks, both exit 0:

```bash
python3 probes/run_evidence.py --evidence-dir evidence/native-telegram-20261109 lifecycle-doctor plugins doctor /home/sopski/projectresearch/hermes-feasibility-20261109/blindcouncil --ci
python3 probes/run_evidence.py --evidence-dir evidence/native-telegram-20261109 lifecycle-validation plugins validate /home/sopski/projectresearch/hermes-feasibility-20261109/blindcouncil --install-deps
```

Actual correction/preservation commands:

```bash
python3 probes/audit_preservation.py after-restart
python3 probes/run_evidence.py --evidence-dir evidence/native-telegram-20261109 round-2-cancel blindcouncil cancel --round-id 6917ad5b2a4e
python3 probes/audit_preservation.py after-cancel
```

Those evidence paths are already populated: **do not rerun with the same names**. Remaining P1 coverage: native lifecycle/revocation, outbox retry/duplicate/crash handling, notification migrations and install/remove/update. Supporting tests do not promote a live gate.

## Packaging, UI and production gates

PLANNED: clean install/removal/compatibility in disposable homes; declared dependencies/version floor/license; final reviewed source tree Doctor and catalog validation. Passing prototype validation is not a catalog admission.

PLANNED after P0: genuine Desktop/Webapp interactions, actual served URL/authentication/Windows browser access, screenshot and browser tests, keyboard/focus/privacy/light-dark/responsive/reduced-motion checks. No graphical app URL is currently verified.

PLANNED after real workflow: real video capture, inspected MP4 duration/resolution, security/reliability demonstration and approved submission evidence in `docs/SUBMISSION.md`.


## November 10 recovery

- Cancelled-round real late tap **LIVE PASS**: `evidence/recovery-20261110/cancelled-late-callback-audit.json`. Native cancelled outcome at November 9 17:04:45 UTC; one existing response/receipt unchanged. User confirmed actual alert before the usage limit. No repeat tap requested.
- Existing native gateway still running at PID 2517893: `gateway-status.stdout.log` and new command ledger in that directory. No new poller started.
- Interrupted assertion diagnosis: `interrupted-assertion-diagnosis.json`. Source whitespace check exit 0. Inline scanner's delivery-ID query included synthetic fixtures, causing three false positives. Correct query uses corroborated native accepted receipts; no source/test fixture deletion or secret suppression.
- New scanner: `probes/review_public_changes.py`, four regression tests in `tests/test_public_review.py`. Initial boundary-case failure and failed scan preserved (`scanner-first-run-failure.json`, `public-review.json`). Corrected four tests PASS (`scanner-regressions-r2.*`), public scan PASS (`public-review-r2.json`), installed Python sources still match, no token file read/private ID exported.
- Real expiry, revoked allowlist and wrong-message live tests remain pending. Do not promote scanner/supporting results into those gates.


## November 10 expiry and security preparation

- **LIVE expiry PASS**: `evidence/live-negative-20261110/expiry-before-late-tap.json` records 30-second persisted deadline, both real requests and zero votes; `expiry-late-callback-audit.json` records native expired attempt after deadline, zero accepted votes/receipts, user-confirmed alert.
- **Actual gateway restart + schema v2 persistence PASS**: four-round snapshots before/after preserve APPROVED/CANCELLED/REJECTED/EXPIRED and original fingerprints. Public stop, private backup/config-unchanged deployment and new PID 3403576/native session 25349 recorded there.
- **29 supporting policy/security tests PASS**: `evidence/negative-gate-regressions-20261110-r1/`, including eleven in-memory PTB command/routing cases. Covers revocation permissions/idempotency/private receipt preservation and v1→v2 migration. No synthetic result is a live negative callback.
- **Official Doctor + validator exit 0** on security source: `negative-gates-{doctor,validation}.stdout.log`; in-process-only and undeclared version/dependency floor remain disclosed.
- Wrong-message and decision-revoked participant genuine callback tests pending. Global Telegram allowlist was not edited; a future live revocation pass must be labelled decision authorization, not global allowlist or a third unallowlisted account.


## Configurable expiry and new capability scope — November 10

- Fresh genuine security round f5b02a4352bb is pending with two native private requests, no votes/accepted receipts and no revocation. Its normal default is exactly **86400 seconds**, stored expiry Nov 11 09:42:26.965001 UTC. Evidence: `evidence/live-negative-20261110/security-round-initial-audit.json`. Owner diagnostic message genuinely delivered to Account 2; actual diagnostic-button denial still awaiting user action/audit.
- `python3 probes/run_supporting_tests.py --evidence-dir evidence/expiry-config-regressions-20261110-r1`: **31 supporting methods PASS**, no live configuration/Telegram calls. New coverage: numeric durations corresponding to 15 minutes/1 hour/24 hours/3 days/7 days; exact stored timestamps recovered in a fresh process; explicit 24-hour default versus 30-second test override; invalid finite/range/type inputs. Existing validation supports those durations; preset controls remain planned for finished UX.
- Action-Bound Approval Enforcement requirement persisted as ACT-01/02 in master plan/roadmap. **Not implemented or tested**; ordinary result notifications are not evidence of guarded action execution. No Hermes-wide enforcement or exactly-once external action claim.


## Genuine wrong-message denial and scoped revocation — November 10

- **LIVE wrong-message denial PASS**, round f5b02a4352bb: user pressed the separate diagnostic once from Account 2, native attempt at 09:49:31 UTC denied `message_binding_or_choice`. Original invitation messages untouched, state PENDING, zero accepted votes/receipts. `evidence/live-negative-20261110/wrong-message-live-audit.json`.
- **HERMES LOCAL scoped revocation PASS**: registered `blindcouncil revoke --round-id f5b02a4352bb` exit 0/revoked, recorded in `security-round-revoke.*` and command ledger. `revocation-before-original-tap.json` verifies only Account 2's decision permission revoked; owner unaffected, zero accepted responses. This does not edit the global Telegram allowlist or authenticate a third unallowlisted account.
- Read-only four-completed-round comparison against the earlier restart snapshot passes in `four-completed-rounds-after-security-revocation.json`. No additional restart occurred for this comparison; the helper's equality flag compares prior state/count/fingerprint.
- **PENDING real test:** Account 2 presses Approve once on its ORIGINAL bound invitation after revocation. Require native `participant_revoked` denial/no vote, not merely a synthetic test or local permission row.


## Genuine revoked-participant denial — November 10

**LIVE PASS:** `revoked-participant-live-audit.json` records native callback at 09:52:54 UTC denied `participant_revoked`, corroborated by Account 2's actual original-invitation press/alert. State at audit PENDING; zero votes/accepted receipts; only Account 2 revoked. Wrong-message attempt preserved. Scope: decision authorization, not a global-allowlist/third-account test.

Then supported operator cancellation exit 0; `security-round-close.*` and `security-round-closed-audit.json` confirm CANCELLED, zero votes/receipts, both native denial attempts and revocation row retained. No historical evidence deleted. This completes scoped P0 callback gates and opens P1 reliability; it is not a complete product/package/submission PASS.


## Notification reliability implementation and genuine recovery — Nov10

- **52 supporting tests PASS**, final prepared environment/source: `evidence/outbox-regressions-20261110-r3/`. Covers queue/rollback/leases/concurrency/network/rate-limit/Forbidden retries, persistent error history and deliberately demonstrated uncertain-send duplicate possibility. Initial51/r2 tests preserved; PTB retry_after deprecation and temporary-fixture WAL notice retained.
- Final official checks in `evidence/notification-reliability-20261110/outbox-{doctor,validation}-final.*` exit0. Initial validator returned0 with dependency preparation warning; preserved and resolved by explicit Hermes PM preparation (r1 sandbox DNS failure, approved r2 success, installed closure success). No security-setting edit/raw pip/uv call. PTB22.8 pin matches core. MIT license added.
- **LIVE native queue recovery PASS**: 27cf6925d334 created via loaded Hermes CLI with gateway stopped, two queued invites/zero attempts/bindings. Native restart then sent both/committed bindings; user confirmed both private requests. First real response pending/no result jobs, second genuine distinct configured response APPROVED and both participants received final aggregate. Both result jobs API-confirmed/attempt1. `queued-before-start.json`, `invites-after-start.json`, `recovery-round-first-response.json`, `recovery-round-approved.json`, official audit/runtime.
- One additional native duplicate attempt appears; user reports no intentional extra taps. Preserved in `recovery-callback-attempt-observation.json`, cause unverified; no extra vote/logical result work. No exactly-once guarantee.
- Old terminal states/fingerprints and security denials/revocation unchanged through schema3; historical terminal notifications not replayed. Private backup/config-hash checks preserved, no secret/config contents exported.
- **LIVE blocked-bot delivery failure PASS**: Account2 blocked bot, then new11b50f663677 created15m. Actual native Forbidden → durably blocked Account2 invite, owner invite sent once, zero votes/receipts. `blocked-delivery-live-evidence.json` saved before unblock request, including owner binding fingerprint and failure events. Recovery remains PENDING until unblocked partner actual retry succeeds.


## Final genuine blocked-bot recovery

Old11b50f663677 expired before recovery; `retry-request-after-expiry.json` records correct obsolete invitation/no false pending claim. Full record hash before/after fresh test confirms no changes to old expired evidence.

Fresh **ac4e9f1d4090**: `fresh-24h-deadline-before-delivery.json` proves86400s and zero attempts before startup. `fresh-24h-blocked-failure.json` records real Forbidden and owner sent once. Registered CLI targeted retry queued1 job; `fresh-24h-recovered-api-audit.json` proves correct bindings, partner cumulative attempts2, owner1/same binding, original error/retry events and exact deadline retained, pending/zero votes. `fresh-24h-human-confirmed-recovery.json`: user confirmed partner arrived/no owner duplicate. **LIVE PASS**. Then `fresh-24h-test-close.*` / `fresh-24h-closed-audit.json`: cleanup CANCELLED, zero votes/receipts, both terminal notifications sent/error history retained. No previously completed round modified.

Source-only packaging guards: **55 supporting methods PASS** in `evidence/packaging-hardening-20261110/`, including accidental live-profile synthetic-probe prevention and clear missing-interface failure. Worker/vote logic unchanged. Current primary gateway still prior guard-less version pending controlled reload; no extra Telegram test needed for these registration-only changes.


## Current distribution milestone — November10 12:30 UTC

The clean local distribution now lives at `release/blindcouncil`, separate local Git branch main, latest editorial SHA ea1a0a5eafa328f383aa189a2eaa171bdbf68317 (use its Git HEAD for newer work). This is the canonical source for future product changes; preserve research source/history as the proven prototype. No external remote/push/PR exists.

The judge-first README was audited against actual source/evidence and five requested public READMEs, rewritten in its own README-only commit, and verified42 relative links plus both official external doc destinations. No submitted/frozen artifact was modified. Full standards are preserved in release docs/README_AUDIT.md; publisher must keep proof links current as milestones complete.

Real official pinned install/enable/load/remove/reinstall passed on the original Hermes source. Every fixture database record retained the same hash. Removal clears plugin settings; the first post-reinstall status was correctly DENIED until coordinator fixture configuration was restored, then approved state read back. This corrects any shorthand claim that reinstalled access was automatic. Correct update command refused silently moving an immutable pin; explicit repin moved only a README commit, not a schema migration. Initial invalid --yes command and sandboxDNS failures retained. Clean root validator passed with dependencies prepared and scan safe after network retry. Evidence: evidence/distribution-lifecycle-20261110 and release docs/evidence/installer-lifecycle-20261110.

Current release compatibility test is running in a separate credential-free packaging-tests/release-home using official v0.23.1 worktree vendor/hermes-v0.23.1 SHA3b421578588243f920886e6fe79a6faa87ea026e. Original gateway core checkout remains unchanged at2c955c3. Check package install tool session32746; do not declare release-floor PASS until actual enable/load/checks finish. No Telegram polling in packaging homes. Native gateway remains hostPID3582313/session68057 on original isolated-home.

Design skills have been read for next phase. Impeccable context ran once in the final folder, actual init workflow captured already-confirmed master-plan product answers in release PRODUCT.md/.impeccable/INIT_RECORD.md. No UI code or DESIGN.md exists yet; no paid image call, redundant package or new questions. New-work/craft-floor/real references/officialSDK and screenshots remain required. Use public ctx.register_rpc + host.request if suitable: existing official docs support sessionless authorized operator calls, avoiding private backend imports. This is only an investigated candidate, not an implemented RPC/UI feature.

Next exact work: finish v0.23.1 install/55-test/Doctor/validator proof; truthful requires_hermes floor. Commit packaging/status/evidence. Then implement narrowly scoped official SDK UI, verify actual auth/loopback/Windows browser access, prepare stable publication for explicit approval without waiting for optional branding/video. All future requirements and ACT-01/02 stay planned/deferred. No manual Telegram action pending.


## Native-interface recovery checkpoint — November10 14:30UTC

Canonical distribution is now on `native-interface`, based on validated commit68014680360001a66f13ee5c9b489aa4d7e3a16e, which remains on main. Source changes were preserved: operator_rpc.py and official ctx.register_rpc registration passed63 supporting methods on actual Hermes SQLite with synthetic context/transport. desktop/plugin.js exists and passes node syntax checking; its real functional/browser gate is NOT passed. Fixed the notification retry control to read actual notifications rather than a nonexistent counts field. No policy/vote/worker mutation was made for the UI.

Official v0.23.1 Webapp renderer built successfully after network retry, at vendor/hermes-v0.23.1/apps/desktop/dist-webapp. New credential-free UI gateway **hostPID3914614 / toolsession23038**, home packaging-tests/release-home, native command from probes/ui_runtime.py run. It has synthetic allowlist10003/10004 but NO bot token, so no competing Telegram poller. Existing native Telegram gatewayPID3582313/session68057 was left untouched. A documented development symlink links the final package into the UI home; prior Git-installed tree preserved privately at packaging-tests/release-home/backups/installed-before-ui. Only this test home's webapp.enabled was changed.

Host-context public status confirms `Serving at http://127.0.0.1:9120`. Playwright through official one-use CLI sign-in loaded the real host shell, but initially remained on Connecting/Backend offline. A real Capabilities click was blocked by the host overlay; never force-clicked or patched it. Diagnostic work is active, not a UI PASS. Private browser profile/evidence/logs stay ignored inside packaging-tests/release-home; no sign-in credential is printed. Browser helper passes the launch URL only by stdin, strips URL diagnostics and captures failures. Needs actual connection resolution, normal user enable toggle and real operator RPC/browser actions before UI promotion.

Read README_EDITORIAL_STANDARD.md on both trees. Original final candidate6801468 still contains no UI; prepared catalog metadata pins it. No publication approval has been received, no external remote/push/PR exists. Earlier asynchronous approval question is not answered by the user's resume prompt; re-review/update pin after UI changes and ask approval when ready. GitHub auth metadata is available for sopskistar; a public exact-name repository search returned0, snapshot catalog had no BlindCouncil collision. Not trademark clearance.

Exact next step: inspect the real gateway-connection diagnostic result, solve the documented Webapp auth/connection setup without core patches or paid calls, enable the unified UI via Hermes' own controls, test onboard/create/detail/cancel/history/error/expiry and privacy. Source test profile currently has no configured participants, so expected onboarding first. Then configure ONLY synthetic local IDs in this token-free home for supporting UI tests. Primary genuine data requires a controlled deployment/reload plan, preserving configuration/DB/evidence and one poller. UI source is not deployed to primary.

Unfinished design/video/publication and all future master-plan requirements remain preserved. No model inference, paid resource, public binding, fake live callback or final video claim.


## Actual native Webapp browser workflow — November10

Official one-use authentication and native sidebar loading succeeded without model credentials using the host’s normal provider-later option. Actual Webapp create/cancel/history flow passed; stored one-hour exact deadline and zero votes/receipts corroborated in clean docs/evidence/native-ui-20261110/browser-and-storage-proof.json. This is actual Hermes UI/RPC/SQLite with explicitly synthetic participants in a token-free profile, not genuine Telegram interaction. Auth-negative probe saw an anonymous connection error/no result; exact HTTP auth rejection classification remains to verify before promoting that security gate. No static mockups/forged votes were used.


## Native interface, capability audit and preserved primary upgrade — November10 15:45UTC

- Actual reviewed code ce16860051836f9a92a50dae7079df6d42c2ecde: configuration reads moved inside RPC error boundary;64 supporting methods pass in clean docs/evidence/operator-rpc-tests-20261110-r2. No Telegram network/model call in this suite.
- Real native browser/RPC/SQLite token-free create/cancel/history/default24h/five presets/selected1h proof: clean docs/evidence/native-ui-20261110/browser-and-storage-proof.json. Focused blank-title errors/aria-invalid,1440/768/390 viewport fit and anonymous protected API401: browser-auth-responsive-proof.json.
- Controlled primary commands: python3 probes/hermes_local.py gateway stop; python3 probes/ui_runtime.py stop; python3 probes/hermes_current.py plugins install file:///home/sopski/projectresearch/hermes-feasibility-20261109/release/blindcouncil --ref ce16860051836f9a92a50dae7079df6d42c2ecde --enable --yes-deps; python3 probes/hermes_current.py config set webapp.enabled true; python3 probes/primary_ui_gate.py run. Private source/DB backups retained. Loopback default127.0.0.1:9120 verified before start.
- python3 probes/ui_browser.py primary-native-history-r3 --primary --action primary-history: actual authenticated native interface reads five existing genuine rounds, all states/counts match, no numeric participant IDs visible, native adapter loaded,0page errors. No new votes/callbacks. Earlier driver failures preserved privately: r1 fresh Desktop opt-in missing; r2 ambiguous sidebar/catalog button locator; r3 uses normal enable and unambiguous sidebar navigation, no renderer patch or force-click.
- python3 probes/primary_ui_gate.py audit --name after-native-browser: every DB record hash unchanged from before stop/install/start/browser; credential-file metadata unchanged; all non-Webapp config unchanged. Public proof evidence/primary-native-ui-20261110/after-native-browser.json, copied clean docs/evidence/native-ui-20261110. Public snapshot checks original four genuine terminal rounds/receipt counts/fingerprints after release.
- Official final-code Doctor and validate --install-deps PASS, dependencies prepared: research distribution-lifecycle native-reviewed-validator-r3 and operator-rpc-hardened-doctor; clean copies in docs/evidence/native-ui-20261110. Official core SHA3b421578588243f920886e6fe79a6faa87ea026e. Factory remains in-process only.
- Scope audit:0 agent tools,1policy,0 action grants/executors. ACT-01 investigation is documentation only; no action-authorizer test passes. Public tool/storage interfaces are feasible candidates, while model access/genuine descriptor approvals/denial tests remain future gates. Full contrast/theme review, Windows confirmation, publication and video remain open.
