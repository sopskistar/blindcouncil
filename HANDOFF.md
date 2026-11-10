# BlindCouncil recovery handoff

Updated November 10, 2026, 15:45 UTC. Read AGENTS.md, PROJECT_MASTER_PLAN.md, PROJECT_STATUS.md, ROADMAP.md, DECISIONS.md, TEST_EVIDENCE.md and the capability audit. Do not repeat passing Telegram tests or restart the project.

## 1. Exact project and Git

Research: /home/sopski/projectresearch/hermes-feasibility-20261109, branch master. Canonical product: /home/sopski/projectresearch/hermes-feasibility-20261109/release/blindcouncil, separate Git repo, branch native-interface. Query git rev-parse HEAD in each for the exact latest documentation checkpoint; a file cannot name its own future commit. Last reviewed runtime commit is ce16860051836f9a92a50dae7079df6d42c2ecde. Main still preserves68014680360001a66f13ee5c9b489aa4d7e3a16e. Research parent deliberately ignores release/. Commit both repositories separately. Never publish mixed research/private runtime.

No remote/public repo/push/catalogPR/X/form/deployment exists, and no publication approval is received. Target account sopskistar; prior read-only account auth available. Prepared catalog metadata must be updated to the latest reviewed full SHA after checks, not reused6801468 blindly.

## 2. Implemented and tested

Native Telegram factory/scoped callbacks; deterministic two-person collect-both unanimity; current allowlist/membership/message/revocation checks; transactional immutable responses/receipts; schema3 metadata/events; exact UTC expiry/default24h/presets15m1h24h3d7d; cancellation; durable invitation/result outbox/leases/retries/blocked history; native owned worker with supplied bot; operator CLI/RPC and official SDK interface.

Genuine rounds:38378f7fbe90 APPROVED;6917ad5b2a4e CANCELLED(one original vote);cb54bed1b2b7 REJECTED;f79effc48d29 EXPIRED(zero);f5b02a4352bb real message/revocation denials(zero), then cancelled;27cf6925d334 actual queued/restart recovery and two real approvals/both aggregate deliveries;ac4e9f1d4090 real Forbidden/unblock/targeted retry with human confirmation, then supported cancellation.11b50f663677 expired before recovery, never revived; its blocked Account2 terminal-result job is intentionally NOT retried. Two owned accounts do not prove independent humans.

64 supporting methods passed on official v0.23.1; actual SQLite, synthetic transport/identities/context, temporary homes. Real installer remove/reinstall retained data but cleared settings; coordinator was reconfigured before access recovered. Doctor and dependency-prepared validation pass; in-process only. No claims beyond tested scope.

Browser: real Hermes one-use auth/native SDK route/RPC/SQLite creation, five durations/default24h/1h exact deadline, cancel confirmation/KeepPending/cancel/history; anonymous HTTP401; focused validation; desktop/tablet/phone fit. Token-free profile for mutations. Actual genuine primary history reads all four terminal types/counts with no numeric identities and no new callbacks. Zero page errors. Manual Windows access, full contrast/theme review and final branding still open.

## 3. Running processes and environment

**Live primary gateway hostPID4048414 / toolsession5614**, command python3 probes/primary_ui_gate.py run. Official source vendor/hermes-v0.23.1 SHA3b421578588243f920886e6fe79a6faa87ea026e; isolated-home. It serves Telegram AND authenticated Webapp at http://127.0.0.1:9120. Do not start another poller. OldPID3582313 and token-free WebappPID3914614 stopped via official profile lifecycle; do not assume sessions/PIDs persist—verify status in host context before any lifecycle operation.

Managed Python3.14.9, PTB22.8; existing PM metadata under runtime/primary home. Original vendor/hermes-agent remains2c955c3a8c0bf8f52cbfad13ed3215ade4eb6f94 as preserved source. Use probes/hermes_current.py for current primary CLI, not the old wrapper. PM owns dependencies; never rawpip/uv/recreate environments reflexively.

Token/actual IDs/allowlist remain private and unchanged. Only webapp.enabled was enabled through official CLI. Private backup isolated-home/backups/native-ui-20261110 contains DB and previous plugin source. Current installed exact Git pin ce16860051836f9a92a50dae7079df6d42c2ecde; later documentation changes do not hot-update installed code. Audit after deployment/browser confirms every DB record unchanged (hash e6f360a6f330dccb7156e527f379196067c7138b1ed09abb95ce2750dbfef4b8), .env metadata unchanged, non-Webapp configuration unchanged. Never copy/reset secret settings or rerun setup. Raw logs/browser profiles are private; no credential URL/token in tool output/Git.

Packaging homes packaging-tests/home and packaging-tests/release-home have no bot token. UI helper currently assumes port9120; the primary gateway owns that port, so do NOT start the old token-free UI runtime while it runs. Browser actions with --primary are restricted to read-only history/auth/capture. No live mutating developer probes.

## 4. Exact next step and publication

Inspect latest Git status, finish/check the updated docs and media evidence, then create a reviewed full-SHA publication candidate/catalog draft. Ask explicit approval for public repository creation/push and catalogPR. No external publication before approval. Do not delay stable catalog publication for optional branding. OpenedPR is not merged. New source means a new validation/pin review.

For the user to open the genuine interface, in their Ubuntu terminal:

    cd /home/sopski/projectresearch/hermes-feasibility-20261109
    python3 probes/hermes_current.py webapp --no-open

Open the printed private one-use link in the Windows browser within60seconds. Never paste it into chat. In Capabilities→Plugins search BlindCouncil and enable Desktop, then choose its sidebar entry. If provider setup appears choose the normal provider-later option; no model is needed. Bare localhost is not authentication. Do not bind publicly to fix a relay issue.

Then finish original identity/assets/native polish with installed skills; produce genuine under90s MP4; prepare X @NousResearch and Typeform after approval. Current UI is functional, not a finished brand/demo. Real Telegram GUI footage may need user capture; existing authentic callback evidence must be labelled as evidence, never fabricated app states.

## 5. Resume checks

Primary read-only status: python3 probes/hermes_current.py gateway status ; python3 probes/hermes_current.py webapp --status (run separately). Host context is needed; sandbox PID/socket restrictions can hide a real gateway. Never --replace/delete locks.

Primary data comparison: python3 probes/primary_ui_gate.py audit --name NEW-UNUSED-NAME. No existing evidence name overwrite. Read-only browser: python3 probes/ui_browser.py NEW-UNUSED-NAME --primary --action primary-history. Private capture credentials pass only stdin.

From final package:

    python3 scripts/test.py --hermes-source ../../vendor/hermes-v0.23.1 --runtime-home ../../packaging-tests/release-home --runtime-dir ../../runtime --evidence-dir docs/evidence/NEW-UNUSED-NAME

From research root:

    python3 probes/package_cli.py --name NEW --source vendor/hermes-v0.23.1 --profile packaging-tests/release-home plugins doctor /home/sopski/projectresearch/hermes-feasibility-20261109/release/blindcouncil --ci
    python3 probes/package_cli.py --name NEW2 --source vendor/hermes-v0.23.1 --profile packaging-tests/release-home plugins validate /home/sopski/projectresearch/hermes-feasibility-20261109/release/blindcouncil --install-deps

Rerun only after changes/failures/unresolved concerns. DNS/socket failures require normal tool escalation; preserve failures and retries. Latest clean proof is native-reviewed-validator-r3. Earlier r1/r2 browser failures were missing opt-in and ambiguous test locator, not lost data or fabricated pass.

## 6. Unfinished master requirements

ACT-01/02: investigated, **NOT implemented/tested**. Zero registered agent tools/grants/executors. Candidate release_note.v1 uses exact immutable descriptor/participants/policy/deadline and an atomic single-use claim before fixed plugin-owned file creation. Fail closed on all non-approved/mismatch/replay/expired/uncertain cases; no middleware/global interception. Full model-initiated proof requires real authorized access; billable/unavailable credentials remain blocked. Required publication/demo precede this optional spike. See docs/ACTION_BOUND_APPROVAL.md.

P2 final native design/logo/light-dark/accessibility, manual Windows confirmation, remaining media; P3 public repo/catalogPR/video/X/form; P4 majority/quorum/veto/multi-stage/delegation/channels/audit exports/templates/team/org workflows and all POL/COM/GOV/UX/APP/INF rows remain preserved in ROADMAP.md. No requirement silently dropped. No paid inference/resources, public binding or fake human/model evidence.

Deadline verified from organizer announcement: November11,2026 17:00EST=22:00UTC=23:00WAT. Form reachability/final fields need final check. Update status/handoff/evidence/roadmap and commit safe progress before account interruption.
