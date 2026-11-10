# BlindCouncil current status

Updated November 10, 2026, 15:45 UTC. **Scoped live Telegram/reliability gates pass. The native Webapp now reads the genuine decision history. Submission is unfinished.**

## Product boundary — audited before enhancements

BlindCouncil is intended as a privacy-conscious deterministic human authorization and decision engine for Hermes. Telegram is its first response channel. The current build implements authenticated decision coordination, one policy (exactly two participants, collect both, unanimous approval), operator CLI, authenticated operator RPC and native Desktop/Webapp controls. **Zero agent-facing tools, action grants or protected executors exist. APPROVED does not authorize another Hermes action.** No Hermes-wide guard is claimed.

ACT-01/02 remain planned/deferred while required publication and demo work take priority. The narrow fixed release-note candidate is documented in docs/CAPABILITY_AUDIT.md and docs/ACTION_BOUND_APPROVAL.md; API feasibility is not an implementation pass. Real model initiation also needs authorized model access; no paid inference is approved.

## Verified milestones

- Genuine two-account approval/rejection, distinct transport identities, duplicate denial, wrong-message and revoked-participant denial, cancelled/expired late-response denial, restart persistence. A globally unallowlisted third account is supporting-only.
- Real queued notification recovery and both-account aggregate delivery. Actual Telegram Forbidden, targeted invitation retry after unblock, unchanged 24-hour deadline and human-confirmed partner receipt/no owner duplicate. Prior failed/expired rounds are retained. No additional human test is pending.
- Real pinned installer load/enable/remove/reinstall preserved every fixture DB record. Removal clears settings; access resumed only after fixture coordinator reconfiguration. Immutable-pin update refusal was correctly observed. Explicit repin was README-only, not a schema-upgrade test.
- Official Hermes v0.23.1, SHA3b421578588243f920886e6fe79a6faa87ea026e: actual loader, Doctor, dependency-prepared catalog validation. Native factory is in-process only. PTB22.8; minimum>=0.23.1 is the conservative tested floor.
- **64 supporting methods PASS**, using real Hermes SQLite with synthetic identities/transport/context. Includes RPC configuration/storage error redaction and no agent/RPC vote submission. These are not Telegram callbacks.
- **Real Webapp/RPC/SQLite:** onboarding, create, default24h/five practical durations, selected1h exact stored deadline, pending detail, cancellation confirmation/dismissal, cancellation and history. Token-free test home; no Telegram delivery claimed.
- **Real browser:** focused blank-title error, aria-invalid, 1440/768/390 viewport checks with no product horizontal overflow; anonymous protected API HTTP401. Dark preference produced a dark host background; exhaustive contrast/theme audit remains open.
- **Controlled primary deployment:** original bot gateway stopped through public lifecycle; prior plugin source and DB privately backed up; exact local Git package ce16860051836f9a92a50dae7079df6d42c2ecde installed through official CLI. Only webapp.enabled changed. Every DB record hash, credential-file metadata and non-Webapp configuration stayed unchanged.
- **Genuine history browser gate:**38378f7fbe90 approved, cb54bed1b2b7 rejected,6917ad5b2a4e cancelled,f79effc48d29 expired,ac4e9f1d4090 cancelled match stored states/counts. Participant IDs absent; native adapter loaded; zero page errors. No new callbacks/votes or model calls.

## Repositories and current processes

Research: /home/sopski/projectresearch/hermes-feasibility-20261109, branch master. Canonical product: release/blindcouncil, separate native-interface branch. Validated pre-interface main remains68014680360001a66f13ee5c9b489aa4d7e3a16e; current HEAD includes newer interface/docs. Query each Git HEAD for the exact latest SHA. No remote/public repository/catalogPR exists. Explicit publication approval has not been received.

**One live gateway:** hostPID4048414, toolsession5614, started via python3 probes/primary_ui_gate.py run, official release core, same isolated-home/token/realIDs/allowlist. Webapp verified at http://127.0.0.1:9120. Old TelegramPID3582313 and token-free WebappPID3914614 were stopped. Do not restart unnecessarily or start another bot poller. Private logs/backups/browser sessions remain ignored under isolated-home. The old blocked terminal-result job for11b50f663677 stays untouched.

## Next gates

1. Confirm Windows-browser access using a private one-use link from the user's Ubuntu terminal. Automated WSL authentication and actual UI pass; Windows relay has not been claimed.
2. Finalize exact reviewed source pin/catalog draft and obtain approval for public sopskistar repository + catalogPR. Never wait for optional polish once stable publication is approved.
3. Finish native interface branding/accessibility/theme review, original logo and genuine marketplace screenshots. Basic native UI is functional; final professional design is not certified.
4. Produce/inspect genuine75–85s MP4, always under90s, then prepare X @NousResearch and Typeform. Public posts/submission need separate approval. No video exists yet.
5. Retain action-bound enforcement and all future policies/channels/exports/templates/teams/organizational scope in ROADMAP.md. Do not relabel planned features as shipped.

Evidence: clean docs/evidence/native-ui-20261110 and operator-rpc-tests-20261110-r2; research evidence/primary-native-ui-20261110 and distribution-lifecycle-20261110. Earlier DNS failures, driver/onboarding/strict-locator failures are preserved and explained; later success did not rewrite them. Full native callback evidence remains unchanged. See HANDOFF.md for resume commands.
