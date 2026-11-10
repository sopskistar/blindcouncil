# BlindCouncil roadmap and acceptance criteria

Statuses: **PARTIAL** means a verified subset exists with open acceptance gates. **IMPLEMENTED** means the stated subset exists and has the cited kind of evidence; **BLOCKED** requires an external prerequisite; **PLANNED** is unfinished MVP work; **DEFERRED** is retained future scope. None means a planned test passed. Read `PROJECT_STATUS.md` and `TEST_EVIDENCE.md` for actual outcomes.

## MVP and submission

| ID | Status | Feature / acceptance |
|---|---|---|
| M-01 | IMPLEMENTED | Local plugin loading, native factory registration, baseline policy/storage, setup/readiness/audit scaffolding; actual two-account native approval evidence also exists |
| M-02 | IMPLEMENTED (scoped) | P0 INT-01–11: genuine two-account Approve/Approve now PASS, including distinct configured receipts and actual result delivery. Duplicate and native restart recovery PASS. Fresh rejection round cb54bed1b2b7 PASS including second native restart; wrong-message and decision-revoked participant genuine denials PASS. Global out-of-allowlist third-account negative remains supporting-only. Cancelled/expired taps and persistence pass. Keep evidence separate |
| M-03 | IMPLEMENTED CLI/RPC; UI partial | CORE-01–05: validated two-person creation/policy/request binding/resolution exist; genuine native decisions and actual browser create/cancel flow verified. Remaining UI coverage/deployment tracked under M-09 |
| M-04 | IMPLEMENTED | CORE-06–07: pending-only cancellation/expiry implemented and supporting tests pass; real pending round cancelled without losing its receipt. Genuine cancelled and expired late taps PASS; actual restart preserves both distinct terminal states, original response/receipt counts and fingerprints |
| M-04a | IMPLEMENTED CLI and native graphical controls | CORE-07a: 24-hour normal default; presets 15 minutes, 1 hour, 24 hours, 3 days, 7 days. Existing engine accepts validated finite numeric durations through seven days and stores an exact UTC deadline; CLI and actual browser preset/default selection tested; exact one-hour stored deadline verified. Explicit short integration-test durations remain supported and never become the normal default. |
| M-05 | IMPLEMENTED scoped | CORE-08–09: owner history/progress/aggregate projections and authorized aggregate notifications to both participants; genuine delivery and supporting access/privacy tests. Full native UI coverage remains open |
| M-06 | IMPLEMENTED tested scope | REL-01–06 / SEC-01–04: transactions/concurrency/rollback/current auth/outbox failures/recovery and real negative transport tested. No production security certification or live third-account global-allowlist claim |
| M-07 | IMPLEMENTED | Schema3 additive migrations, immutable receipts, metadata/events and durable outbox recovery verified; legacy unknown timestamps remain NULL and old terminal notifications do not replay |
| M-08 | IMPLEMENTED reviewed candidate | PKG-01–02 real pinned install/enable/load/remove/reinstall/data retention; official v0.23.1 Doctor and dependency-prepared UI/source validation PASS.64 supporting methods PASS; repin final documentation/media tree before publication |
| M-09 | IMPLEMENTED functional subset; manual Windows/visual review open | Official SDK RPC/UI actual browser create/cancel/history/default/presets, HTTP401, focused errors and desktop/tablet/phone fit verified. Primary deployment displays genuine terminal outcomes/counts with all DB records unchanged. Manual Windows access, final contrast/theme/accessibility review remain open |
| M-10 | PLANNED | Collision research, final identity/assets, light/dark and motion where supported; no extensive design until P0 |
| M-11 | PARTIAL | Install/setup/privacy/security/retention/deletion/recovery/troubleshooting docs and actual UI onboarding exist. Final guided demo/FAQ/media must match completed functionality |
| M-12 | PARTIAL; publication approval required | Dedicated local main/native-interface repository, MIT and exact-pin catalog draft exist; no public repository or catalog PR yet |
| M-13 | PLANNED | Genuine 75–85 second MP4, under 90 seconds, two-account flow and real reliability test; rendered file inspected |
| M-14 | PLANNED | Approved X post tagging @NousResearch and official form submission; verify rules, record evidence in docs/SUBMISSION.md |
| M-15 | IMPLEMENTED | Persistent master/status/handoff/decisions/roadmap/evidence/AGENTS records and local checkpoint; future-account recovery commands and all deferred requirements retained |

## Action-Bound Approval Enforcement

| ID | Status | Feature | Acceptance criterion |
|---|---|---|---|
| ACT-01 | INVESTIGATED / DEFERRED until catalog/demo gates secure | One safe bound Hermes action | Immutable versioned action descriptor/digest and participant-readable summary fixed before responses; deterministic guarded executor permits only APPROVED and exact bound scope/arguments within validity. Pending/rejected/cancelled/expired deny. Single-use atomic grant rejects replay/substitution/concurrent and cross-decision reuse across restart. Real documented-interface action plus denial and recovery tests required. Candidate: predeclared owner-only Telegram announcement through native Hermes platform factory. No implementation/test PASS yet. Defer if it threatens integration, validation or submission. |
| ACT-02 | DEFERRED | Additional guarded action integrations | Research each documented interface's authorization/approval and idempotency contracts; add exact scope/content/resource binding, audit and failure/replay tests per action. Never infer Hermes-wide coverage or bypass native approvals; unsupported tools/other plugins/host access remain outside plugin enforcement. |

Do not confuse ordinary aggregate-result notifications with action-bound approval enforcement. Ambiguous remote execution after timeout/crash must fail closed with explicit recovery; no exactly-once claim. This requirement is preserved even if both rows ship after the hackathon.

## Future decision policies

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| POL-01 | DEFERRED | Majority approval | Versioned policy resolves odd/even electorates and ties deterministically in tests and a real multi-account workflow |
| POL-02 | DEFERRED | Configurable quorum | Insufficient responses never resolve approval; quorum/deadline edge cases survive restart |
| POL-03 | DEFERRED | Weighted voting/roles | Authorized configured weights produce reproducible totals; participants cannot change their weight |
| POL-04 | DEFERRED | Required-role / role-based veto | Only the configured required role can veto; rule and audit evidence remain versioned |
| POL-05 | DEFERRED | Custom thresholds | Bounded validated thresholds have documented boundary cases and cannot be overridden by model input |
| POL-06 | DEFERRED | Multi-stage approvals | Stage transitions require the preceding authorized result; repeated events cannot skip stages |
| POL-07 | DEFERRED | Delegated decision authority | Explicit scoped/time-bound delegation is authenticated, revocable and auditable |
| POL-08 | DEFERRED | Abstentions | Abstention semantics for denominator/quorum are explicit and regression-tested |
| POL-09 | DEFERRED | Dynamic participant substitution | Authorized substitution preserves prior audit history and rejects revoked invitations |
| POL-10 | DEFERRED | Decision templates | Validated versioned policy/participant templates instantiate reproducible independent rounds |
| POL-11 | DEFERRED | Configurable disclosure policies | Different viewers receive only explicitly permitted aggregates/progress; cross-role leak tests pass |
| POL-12 | DEFERRED | Time-based escalation policies | Persisted time rules escalate once logically, survive restart and never fabricate votes |

## Communication

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| COM-01 | DEFERRED | Additional messaging platforms | Each uses its documented Hermes adapter and real authenticated callbacks; platform IDs cannot collide |
| COM-02 | DEFERRED | Multi-channel notifications | Authorized per-recipient routing respects privacy and independently retries failures |
| COM-03 | DEFERRED | Deadline reminders | Durable scheduling avoids reminders after termination and recovers correctly after downtime |
| COM-04 | DEFERRED | Escalations | Explicit recipient/rule scope, audit records and idempotent mutations verified under retry |
| COM-05 | DEFERRED | Participant acknowledgement | Delivery acknowledgement and actual decision response remain distinct authenticated states |
| COM-06 | DEFERRED | Optional anonymous feedback | Defined anonymity threat model, no false zero-knowledge claim and verified access controls |
| COM-07 | DEFERRED | Decision summaries | Permission-filtered summaries cannot reveal hidden individual responses or invent rationale |

## Governance

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| GOV-01 | DEFERRED | Organization teams and roles | Team/role membership is scoped, revocable and enforced on every decision API |
| GOV-02 | DEFERRED | Approval policy templates | Versioned organization policies instantiate without silently changing existing rounds |
| GOV-03 | DEFERRED | Decision history search | Search returns only authorized records with clear retention/deletion behavior |
| GOV-04 | DEFERRED | Evidence attachments | Authorized upload/read/delete paths enforce size/type/access and do not send private attachments to models implicitly |
| GOV-05 | DEFERRED | Exportable audit reports | Explicit operator export redacts secrets/private answers according to policy and records provenance |
| GOV-06 | DEFERRED | Compliance-oriented retention controls | Documented retention/deletion and tested cleanup; no unsupported certification/compliance claim |
| GOV-07 | DEFERRED | Consent and access management | Consent scope, revocation and historical access decisions are persisted and regression-tested |

## Additional user experience

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| UX-01 | DEFERRED | Advanced Hermes Desktop workspace | Official SDK only; genuine data, permission-aware views and verified usability beyond MVP |
| UX-02 | DEFERRED | Saved decision templates | Authorized saved drafts/templates create independent rounds without carrying old responses |
| UX-03 | DEFERRED | Guided onboarding tour | New-user task completion verified; dismissible/resumable and keyboard accessible |
| UX-04 | DEFERRED | Richer activity history | Real lifecycle events shown with permission filtering and understandable ordering |
| UX-05 | DEFERRED | Improved mobile-friendly views | Real phone-width and touch interaction checks; no privacy leaks or horizontal obstruction |
| UX-06 | DEFERRED | Keyboard shortcuts | Discoverable conflict-free shortcuts preserve focus and respect editable controls |
| UX-07 | DEFERRED | Further accessibility enhancements | Assistive-technology/user testing extends required MVP contrast/focus/keyboard/reduced-motion baseline |

## Integrations

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| APP-01 | DEFERRED | External task-management systems | Explicitly authorized scoped integration links decisions to real tasks without broad credentials |
| APP-02 | DEFERRED | Calendar-related decisions | Correct timezone/deadline mapping and explicit write approval tested against genuine events |
| APP-03 | DEFERRED | Project approvals | Reusable project workflow maintains per-project membership and audit isolation |
| APP-04 | DEFERRED | Document review workflows | Authorized document/evidence references, version binding and permission-aware review outcomes |
| APP-05 | DEFERRED | Payment/procurement approvals | Decision result is separate from external payment authorization; no autonomous transfer implied or included in MVP |
| APP-06 | DEFERRED | Optional hosted deployment for teams | Proper always-on gateway hosting, authenticated access, secret isolation, recovery and cost approval verified |

## Infrastructure

| ID | Status | Feature | Future acceptance criterion |
|---|---|---|---|
| INF-01 | DEFERRED | Team-specific data isolation | Cross-team/profile denial tests and scoped storage verified under concurrent traffic |
| INF-02 | DEFERRED | Backup and recovery | Restore test recovers versioned state and pending work without exposing token/response data |
| INF-03 | DEFERRED | Encryption/key-management enhancements | Explicit at-rest/in-transit threat model, real key lifecycle and recovery tests; claims match implementation |
| INF-04 | DEFERRED | Optional hosted synchronization | Authenticated conflict handling and privacy/isolation verified; not required for local plugin |
| INF-05 | DEFERRED | Monitoring and health checks | Minimal non-sensitive health signals detect genuine failures; no unsolicited telemetry |
| INF-06 | DEFERRED | Structured exports | Permission-filtered versioned export/import with integrity/compatibility and deletion tests |
| INF-07 | DEFERRED | Extended versioned migrations | Forward/backward compatibility strategy and real restoration fixtures beyond MVP's safe base migration |
| INF-08 | DEFERRED | Optional informational website / future hosting design | Plugin remains standalone; no Vercel/Neon dependency or serverless Telegram listener; explicit publication/cost approval |

Reprioritize only after updating the master plan/status/decisions. Every deferred item remains part of the preserved vision; none is promised for the hackathon.


P1 notification update (Nov10): schema3 outbox, leases, error/retry events, owner status/history/create CLI and both-participant aggregate notifications implemented. 52 supporting methods pass; official Doctor and final catalog validation/dependency preparation pass. **LIVE** queued invitation recovery and two-account approved aggregate deliveries passed in27cf6925d334. **LIVE** blocked-bot Forbidden failure preserved in11b50f663677; unblock/retry confirmation still pending. Install/remove/update compatibility and finished graphical/agent UX remain required. No exactly-once external delivery or action-bound enforcement claim.


Native reliability milestone: fresh24h ac4e9f1d4090 real blocked-bot failure → targeted retry recovered Account2 only; original failure/history/deadline/bindings preserved, no owner duplicate, no votes, human confirmation, supported cleanup. Prior15m11b50f663677 expired and was safely not resurrected. **Delivery recovery LIVE PASS.** Packaging hardening55 supporting methods pass; actual install/remove/update checks are next. Do not repeat passed Telegram scenarios.


November10 packaging update: real native install/enable/load/remove/reinstall and exact fixture record retention verified on pinned research Hermes. Release compatibility test in progress; Desktop/Webapp still planned. Judge-first evidence-linked README completed in clean distribution; publication/screenshots/video remain unfinished. All future rows retained.


Native interface update: documented operator RPC implemented/63 supporting methods passed; official Webapp bundle built; UI source drafted but real browser gate still OPEN (host connecting overlay). Existing completed Telegram scenarios remain PASS and must not be repeated. Actual install/remove/release compatibility PASS; publishing/design/demo still unfinished. No future feature removed.


ACT-01 clarification: investigate fixed plugin-owned release-note artifact as the smallest guarded action, using structured request and fail-closed single-use execution tools. Bind exact parameters/participants/policy/validity before actual consent, deny nonapproved/mismatch/replay/uncertain grants, and prove a harmless real effect. PLANNED/UNIMPLEMENTED/UNTESTED; timeboxed only after required UI/validation/catalog/demo gates. Earlier Telegram-announcement alternative retained. Agent model initiation requires separate real authorized access evidence. All POL/COM/GOV/UX/APP/INF rows remain retained/deferred.


November10 15:45UTC release checkpoint: see PROJECT_STATUS.md for current facts. Final native UI runs with the genuine Telegram gateway on official v0.23.1,64 supporting methods and clean dependency-prepared validation. Manual Windows confirmation, final branding/media/publication/video/form remain outstanding. ACT-01 has no code/grant/live proof: exact release-note candidate and fail-closed acceptance are preserved in docs/ACTION_BOUND_APPROVAL.md. All future POL/COM/GOV/UX/APP/INF policy/channel/export/template/team/organizational requirements above remain retained.
