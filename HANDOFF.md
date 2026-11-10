# BlindCouncil handoff — current checkpoint

Updated November10,2026 12:35UTC. Do not restart research or repeat passing Telegram tests.

## Paths, Git and source of truth

Research: /home/sopski/projectresearch/hermes-feasibility-20261109, branch master. Last completed recovery milestone31eb31f; current exact commit is `git rev-parse HEAD`.

Canonical distribution: /home/sopski/projectresearch/hermes-feasibility-20261109/release/blindcouncil, separate branch main. Initial package01b227d367b2743deff799ce330aff80dc6d8589; README-only editorial milestoneea1a0a5eafa328f383aa189a2eaa171bdbf68317. Current exact SHA is that repository's Git HEAD. No external remote/publication. Parent ignores release/ deliberately; commit both repos independently.

Read AGENTS, PROJECT_MASTER_PLAN, PROJECT_STATUS, ROADMAP, DECISIONS, TEST_EVIDENCE, BUILD_REQUIREMENTS and LIVE_GATE. Full requirements are preserved in both trees. Original research/TraceFork/report/evidence stays intact. Only final distribution gets future product changes; research prototype is preserved rather than silently rebuilt.

## Implemented and actually tested

Version0.1.0/schema3, seven Python modules, official native platform factory/scoped callbacks, operator CLI, deterministic collect-both two-person unanimity, server-side identity/message/current-allowlist/membership/revocation/state checks, immutable transactional responses, exact expiry/default24h/presets, cancellation, additive migrations, durable notification outbox/leases/retries/blocked errors/history. Native owned task uses supplied app.bot, no independent poller/token access/model call.

Genuine rounds:38378f7fbe90 APPROVED;6917ad5b2a4e CANCELLED(one original response, real late denial);cb54bed1b2b7 REJECTED;f79effc48d29 EXPIRED(zero responses);f5b02a4352bb wrong-message+revocation denials(zero), then CANCELLED.27cf6925d334 native queued delivery/restart recovery, two genuine approvals and aggregate delivery to both. ac4e9f1d4090 genuine Forbidden/retry recovery with exact24h deadline/zero votes/no owner duplicate, human confirmed, then supported cancellation. Original11b50f663677 expired before recovery and was never resurrected; all rows/failure evidence preserved, blocked Account2 terminal-result job intentionally untouched. Do not retry it silently.

Installer proof: real install/enable/load/remove/reinstall retained all synthetic fixture DB records exactly. Removal clears plugin settings; post-reinstall status DENIED until synthetic coordinator restored, then APPROVED recovered. Correct update command refuses silently moving immutable pin. Explicit source repin moved README only, not schema. Failed initial--yes command and sandboxDNS warnings retained. No fixture data or fake allowlist entered the live home.

Official v0.23.1 worktree SHA3b421578588243f920886e6fe79a6faa87ea026e: actual install/enable/load, Doctor,55 supporting tests and final validator with dependencies prepared PASS. PTB22.8 matches core. Final manifest floor>=0.23.1; in-process only. Original live gateway remains earlier2c955c3; do not claim it was upgraded or repeat-clicked on new release.

## Processes/environment without secrets

Native live gateway hostPID3582313, toolsession68057, command `python3 probes/hermes_local.py gateway run`, connected11:22UTC. Use host context for lifecycle (sandbox PID namespace may hide it); never --replace/delete locks/start a second poller. No Webapp/desktop process exists.

Official original source vendor/hermes-agent remains2c955c3a8c0bf8f52cbfad13ed3215ade4eb6f94. New release is separate vendor/hermes-v0.23.1. ManagedPython3.14.9/OpenAISDK2.54/PTB22.8; Node22.23.1/pnpm available. Original .env/config/two realIDs remain private under isolated-home; no credential copying, reset, setup rerun or ID question. Private backups remain ignored0700/0600. Deployed plugin lacks new registration/developer-probe guards; worker/policy match. Final manifest/loader not deployed to live gateway yet.

Packaging profiles: packaging-tests/home and packaging-tests/release-home, no tokens/.env. Do NOT start Telegram there. Helper probes/package_cli.py selects read-only original PM metadata, then targets a specific credential-free home/source. PM owns dependencies, never rawpip/uv. All install/test/validator sessions ended; fetch housekeeping session30161 may still be active, check before cleanup. No pending human action.

## Exact next step

Commit reviewed packaging/evidence/status milestone in both repositories, then build small official SDK UI in canonical release only. Use documented ctx.register_rpc+host.request for permitted operator projections/creation/cancel/retry; no vote-submission RPC and no ownerID supplied as authentication. Gateway authenticates operator clients; participant auth stays Telegram. Verify native gateway RPC/auth through actual Hermes, not only mocked handlers.

Initialize/build only in final folder. Impeccable context has run once and init captures confirmed user/master answers in PRODUCT.md; do not rerun context or repeat known interview questions. Its CLI init/audit/critique names are skill workflows, not guessed engine subcommands. Native SDK theme/controls are authoritative; actual new-work/craft-floor read and notes in docs/DESIGN_REFERENCES.md/.hallmark/preflight.json. No UI code/DESIGN.md, rastercomp or paidimage call yet. For actual UI edits reload relevant craft-floor and SDK signatures. Frontend work uses premium-ui-design+Hallmark+Impeccable+ui-ux-pro-max+visualQA; rendered screenshots and real interactions required. Later motion/branding/video use their actual installed instructions.

No source floor/policy change may be casually hotcopied while the live gateway runs. Before live UI deployment, prepare controlled reload/backup/config-preservation plan and record source/runtime provenance. A separate credential-free UI gateway may be used first only without the bot token; label fixture data honestly. User already authorized genuine local Webapp setup/auth, but never print one-use sign-in tokens or bind publicly.

## Resume commands

From research root:
`python3 probes/package_cli.py --name UNIQUE --source vendor/hermes-v0.23.1 --profile packaging-tests/release-home plugins doctor /absolute/release/blindcouncil --ci`
`python3 probes/package_cli.py --name UNIQUE --source vendor/hermes-v0.23.1 --profile packaging-tests/release-home plugins validate /absolute/release/blindcouncil --install-deps`

From final repo:
`python3 scripts/test.py --hermes-source ../../vendor/hermes-v0.23.1 --runtime-home ../../packaging-tests/release-home --runtime-dir ../../runtime --evidence-dir docs/evidence/NEW-UNUSED-NAME`

Only rerun meaningful checks after changes/failures. Preserve outputs; raw upstream log whitespace is evidence, not source lint failure. No existing evidence name overwritten. Research helpers package_snapshot.py and prior native audit tools remain reusable.

## Blockers and unfinished vision

No live Telegram scenario pending. Native graphical UI/auth/browser checks, final naming/logo/assets, public GitHub/catalog, actual screenshot/video capture and all submission links unfinished. External publication requires explicit approval; current plugin tree is concrete/reviewable, not yet public. Account auth may be required later. No genuine footage has been fabricated; actual Telegram capture may need human participation when scheduled.

Readmaster/roadmap for all P4 features and ACT-01/02: action binding/grant/executor are unimplemented/untested. No Hermes-wide/cryptographic/exactly-once claims. Before ending each substantial session update status/handoff/roadmap/evidence and commit safe changes in both repos. User-stated and primary-announcement deadline Nov11 17:00EST=22:00UTC=23:00WAT; officialform access still needs final check. No code/PR/X/form/deployment without approval.


## Native-interface recovery checkpoint — November10 14:30UTC

Canonical distribution is now on `native-interface`, based on validated commit68014680360001a66f13ee5c9b489aa4d7e3a16e, which remains on main. Source changes were preserved: operator_rpc.py and official ctx.register_rpc registration passed63 supporting methods on actual Hermes SQLite with synthetic context/transport. desktop/plugin.js exists and passes node syntax checking; its real functional/browser gate is NOT passed. Fixed the notification retry control to read actual notifications rather than a nonexistent counts field. No policy/vote/worker mutation was made for the UI.

Official v0.23.1 Webapp renderer built successfully after network retry, at vendor/hermes-v0.23.1/apps/desktop/dist-webapp. New credential-free UI gateway **hostPID3914614 / toolsession23038**, home packaging-tests/release-home, native command from probes/ui_runtime.py run. It has synthetic allowlist10003/10004 but NO bot token, so no competing Telegram poller. Existing native Telegram gatewayPID3582313/session68057 was left untouched. A documented development symlink links the final package into the UI home; prior Git-installed tree preserved privately at packaging-tests/release-home/backups/installed-before-ui. Only this test home's webapp.enabled was changed.

Host-context public status confirms `Serving at http://127.0.0.1:9120`. Playwright through official one-use CLI sign-in loaded the real host shell, but initially remained on Connecting/Backend offline. A real Capabilities click was blocked by the host overlay; never force-clicked or patched it. Diagnostic work is active, not a UI PASS. Private browser profile/evidence/logs stay ignored inside packaging-tests/release-home; no sign-in credential is printed. Browser helper passes the launch URL only by stdin, strips URL diagnostics and captures failures. Needs actual connection resolution, normal user enable toggle and real operator RPC/browser actions before UI promotion.

Read README_EDITORIAL_STANDARD.md on both trees. Original final candidate6801468 still contains no UI; prepared catalog metadata pins it. No publication approval has been received, no external remote/push/PR exists. Earlier asynchronous approval question is not answered by the user's resume prompt; re-review/update pin after UI changes and ask approval when ready. GitHub auth metadata is available for sopskistar; a public exact-name repository search returned0, snapshot catalog had no BlindCouncil collision. Not trademark clearance.

Exact next step: inspect the real gateway-connection diagnostic result, solve the documented Webapp auth/connection setup without core patches or paid calls, enable the unified UI via Hermes' own controls, test onboard/create/detail/cancel/history/error/expiry and privacy. Source test profile currently has no configured participants, so expected onboarding first. Then configure ONLY synthetic local IDs in this token-free home for supporting UI tests. Primary genuine data requires a controlled deployment/reload plan, preserving configuration/DB/evidence and one poller. UI source is not deployed to primary.

Unfinished design/video/publication and all future master-plan requirements remain preserved. No model inference, paid resource, public binding, fake live callback or final video claim.


Latest real browser result: official one-use sign-in succeeded, and the host connection completed. The unconfigured model-provider onboarding was deferred using its normal “choose a provider later” button; no paid model/provider was configured. Native Capabilities/Plugins screen loads, zero page errors in these checks. BlindCouncil desktop half is genuinely copied from the linked package. Plugin enablement and its functional screen still need verification; no UI PASS yet. Private captures stay in packaging-tests/release-home/browser-evidence. Current development branch native-interface commit4668036; main6801468 remains unchanged and no publication approved.


Latest product audit: docs/CAPABILITY_AUDIT.md records0 agent-facing tools and0 protected action executors. Product vision is a human authorization/decision engine, not a Telegram-only poll. Action-bound fixed release-note artifact is feasible through public tool/storage APIs but remains planned/untested; no middleware/global enforcement claim. Required UI/validation/catalog/demo precede the timeboxed enhancement spike. Current genuine browser create/cancel/history proof is docs/evidence/native-ui-20261110/browser-and-storage-proof.json in the clean package. Existing native Telegram tests are not repeated. No publishing approval received.
