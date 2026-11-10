# BlindCouncil — authoritative master plan

Specification accepted: November 9, 2026. The user's complete master build specification and current-status update supersede omissions in earlier summaries. `BUILD_REQUIREMENTS.md` remains preserved and is reconciled below. No requirement is silently dropped: unfinished MVP requirements are PLANNED or BLOCKED; later features are explicitly DEFERRED in `ROADMAP.md`.

## 1. Product and trust model

**Private decisions. Shared outcomes.** BlindCouncil is a privacy-conscious native Hermes plugin for coordinating authorized human responses through authenticated messaging, persistent state and deterministic rules. It is more than a poll: it must enforce participant-specific permissions, controlled disclosure, auditability and recovery, with a real Hermes graphical experience.

MVP: exactly two authorized Telegram accounts and unanimous approval. The owner is currently also one participant. The user owns both test accounts: two account identities are not evidence of independent humans. AI-facing commands may create/view permitted decisions but must not submit, invent, overwrite or impersonate votes. No model inference is required by the policy engine.

Trusted: the gateway operator, host OS, Hermes core and installed in-process plugin code. The operator can read the local SQLite responses and could modify storage. Authentication through Telegram and API permissions do not make storage tamper-proof or protect against an authorized host administrator. Do not claim end-to-end encryption, zero knowledge, independent-human consensus, or tamper-proof storage. Additional Hermes tools with separately authorized host access remain outside this plugin's API boundary.

## 2. Execution gates and scope

| Priority | Required outcome | Gate |
|---|---|---|
| P0 | Two genuine Telegram identities produce native callbacks; identity/message checks, basic unanimity and persistence | PASS for scoped two-account integration: genuine approval/rejection/duplicate/cancel/expiry/restart, wrong-message and decision-revoked denials, and blocked-bot delivery recovery verified; global third-account rejection remains supporting-only |
| P1 | Complete MVP lifecycle, security, notifications, failure recovery, installation and validation | Implement after P0; supporting isolated tests/docs/packaging may proceed independently |
| P2 | Official Hermes Desktop/Webapp UX, onboarding, branding, clean distribution tree and catalog preparation | No extensive visual/UI implementation before P0; preserve functionality |
| P3 | Genuine footage, verified MP4, X draft and submission package | Requires working real workflow; publication requires explicit user approval |
| P4 | Additional policies, platforms, integrations and infrastructure | Deferred unless P0–P3 are secure and time remains |

Do not build everything immediately. Do not needlessly rebuild TraceFork or proven BlindCouncil work. Cut optional features before testing or submission requirements. No unrelated website, hosted database or SaaS architecture is needed.

## 3. Existing implementation versus intended architecture

Actual source: `blindcouncil/__init__.py` registers the native Telegram factory and operator CLI; `policy.py` implements two-person policy using Hermes `plugin_db()`; `sdk_probe.py` is an explicitly synthetic PTB routing test. `probes/hermes_local.py` runs official Hermes with PM's selected runtime and the disposable profile. Local setup and receipt-audit tools already exist and must be reused.

Intended layers, using documented interfaces only:

1. Native Hermes tool/command and official Desktop/Webapp extension surfaces expose permission-filtered creation, status and history.
2. The official Telegram adapter supplies trusted transport identities to a prefix-scoped plugin callback factory. No independent poller and no core patching.
3. A deterministic, versioned policy/lifecycle layer validates actor, delivery binding, authorization and state inside transactions.
4. Hermes-supported plugin storage persists decisions, private responses, events, delivery bindings and notification work.
5. A durable notification worker/outbox retries delivery with honest duplicate semantics; it does not decide policy or impersonate responses.

Native Telegram callbacks, versioned lifecycle storage, pending cancellation and lazy expiry now exist with scoped evidence in PROJECT_STATUS.md. A durable outbox and owner CLI creation/status/history now exist; native UI and complete product surface remain unfinished.

## 4. P0 live Telegram requirements and acceptance

| ID | Requirement | Acceptance evidence |
|---|---|---|
| INT-01 | Reuse an isolated Hermes profile; token remains in Hermes-owned local secret configuration | Native gateway uses the experiment home; no token in output, logs, Git or recordings |
| INT-02 | Securely register two distinct authorized numeric Telegram identities | Local configuration plus actual callbacks from each configured account; IDs entered locally, not requested in chat |
| INT-03 | Create a round and send each participant a separate interactive private request | Genuine native SDK deliveries with persisted decision/chat/message bindings |
| INT-04 | Receive real scoped callbacks | Human button presses reach `ctx.register_platform_handler("telegram", factory)`; prefix remains `blindcouncil:` |
| INT-05 | Authenticate user, decision and message server-side | Actor comes from `query.from_user.id`, matches membership/current allowlist and delivery; callback payload is not identity proof |
| INT-06 | Approve + Approve = APPROVED | Two genuine accepted receipts and deterministic aggregate, with no individual answers disclosed |
| INT-07 | Approve + Reject = REJECTED | A second real round with both identities; rejection prevents approval |
| INT-08 | Unknown/unauthorized actor = DENIED | Supporting synthetic coverage plus a real controlled authorization-negative test; do not invent a third participant |
| INT-09 | Duplicate = no additional vote; wrong decision/message = DENIED | Immutable response count and negative callback evidence; clearly label synthetic versus real transport |
| INT-10 | Restart preserves decision and receipts | Stop/restart actual gateway and recover the same completed or pending decision |
| INT-11 | Authorized aggregate notification | Both currently authorized participants receive aggregate only; genuine delivery to both verified |

`LIVE_GATE.md` is the operational checklist. Receipt origin/PID metadata is observability, not independent proof of a human or a security boundary. A native gateway must actually be running and real humans must press the buttons. Earlier synthetic receipts cannot satisfy P0.

The user confirmed **local setup complete**; readiness, native Telegram connection and a genuine two-account Approve/Approve round are now verified. Current remaining gate details belong in `PROJECT_STATUS.md`/`HANDOFF.md`. Do not overwrite/sync/edit private configuration or ask for the same information again. Give precise beginner-friendly Telegram clicks only when needed. Never request a bot token in chat.

## 5. P1 core lifecycle and policy

| ID | Requirement | MVP acceptance |
|---|---|---|
| CORE-01 | Create decision, add authorized participants, title and description | Validated owner/coordinator creates a durable, clearly named two-person round |
| CORE-02 | Select supported policy | Explicit two-person unanimous policy and policy version; future policies are not required |
| CORE-03 | Send requests and track participant progress | Binding persisted safely before actionable buttons; pending/responded progress does not reveal choices |
| CORE-04 | Accept responses and resolve | Exactly one immutable response per authorized participant; approval requires both yes; any no prevents approval |
| CORE-05 | Pending state | Incomplete round cannot become APPROVED; current collect-both timing is preserved until explicitly changed |
| CORE-06 | Cancel unresolved decision | Authorized cancellation is a distinct terminal state; later callbacks add no vote |
| CORE-07 | Expire unresolved decision | Persisted UTC deadline enforced server-side, including after restart; no vote after expiry |
| CORE-07a | Configurable practical expiry | Normal default 24 hours; finished creation UX offers 15 minutes, 1 hour, 24 hours, 3 days and 7 days. Validate finite supported durations and preserve the exact stored UTC expiry across reads/restarts. Keep explicitly labelled short test durations (such as 30 seconds) out of normal presets/defaults. |
| CORE-08 | Status and permitted history | Authorized callers see only allowed status/progress/aggregate; no other participant's individual answer |
| CORE-09 | Controlled disclosure and outcome recipients | Explicit permission rules for owner/participants/agent; support authorized aggregate notifications, not implicit public access |

Persist: decision ID; title/description; policy name/version; authorized participant IDs/roles; restricted individual responses; aggregate result; creation/expiry timestamps; lifecycle events and audit metadata. Use schema versioning, safe migrations and transactions. Schema v2 now uses a transactional additive migration, preserving legacy rows and leaving unknown historical creation/deadline NULL. Notification state and complete recovery migrations remain unfinished.

| ID | Reliability/security requirement | Acceptance |
|---|---|---|
| REL-01 | Repeated and concurrent callbacks | Transactional idempotent mutations; conflicting races cannot overwrite a vote or resolve twice inconsistently |
| REL-02 | Network/message failures | Durable notification state and understandable retryable failures; no false successful delivery |
| REL-03 | Restart recovery | Pending rounds, terminal results and unfinished deliveries recover without lost or fabricated responses |
| REL-04 | Missing/revoked participants and expired invitations | Current permission/state checks reject ineligible callbacks without mutation |
| REL-05 | Duplicate notifications | Honest retry behavior with idempotency where supported; no unsupported exactly-once claim |
| REL-06 | Storage errors and invalid transitions | Atomic rollback; safe errors; terminal states remain terminal |
| SEC-01 | Server-side identity and permissions | Never trust model arguments or callback text to authenticate a voter |
| SEC-02 | Restricted output | Agent tools/UI/API/logs cannot leak private responses to unauthorized viewers |
| SEC-03 | Least authority and secret hygiene | No tokens in decision DB; no direct credential-file access; respect Hermes native authorization |
| SEC-04 | Honest trust/security disclosures | Documentation matches actual code and tested guarantees; no core/private renderer patches |
| PKG-01 | Installation, removal and compatibility | Clean dedicated plugin installs/loads/removes in disposable homes with truthful tested version/dependency metadata |
| PKG-02 | Doctor/catalog checks | Official Doctor and validation pass on the exact reviewed final tree; findings disclosed |

Current gaps: finished history/create UI, blocked-notification recovery proof and complete packaging. Durable notification queue/CLI history/create and participant-wide aggregate delivery now exist with scoped live evidence. Delivery now binds before keyboard attachment; acknowledgement failure does not suppress a committed result attempt. Validated title/description storage, pending cancellation, lazy expiry and schema v2 exist with supporting tests; genuine late cancelled/expired taps and their restart persistence pass. Concurrency/rollback/cancel-race cases are tested, but notification/crash/packaging recovery remains unfinished. Do not claim the complete MVP shipped.

### Action-Bound Approval Enforcement — PLANNED, not implemented or tested

BlindCouncil should eventually authorize a specifically bound Hermes action after its policy is satisfied, rather than merely collect responses. This is an additional product capability, not a claim about current enforcement. Finish genuine integration tests, reliability, packaging/validation and required submission deliverables first; defer the extension if it threatens those gates.

For an optional hackathon demonstration, evaluate one safe action through a documented Hermes interface: send a predeclared announcement to the configured owner's private Telegram chat using the native application supplied to the official platform-handler factory. Existing native messaging works, but the action-binding/authorization mechanism does not exist yet. Do not treat an ordinary aggregate notification as proof of this capability.

Acceptance criteria (ACT-01):

- Before requesting responses, persist a versioned immutable action descriptor and canonical digest covering action kind, exact recipient/resource scope, normalized arguments/content, decision ID, policy version and authorization validity deadline. Present an understandable action summary for participants' informed approval.
- A plugin-owned deterministic executor checks current authorization/state and the exact descriptor. Pending, rejected, cancelled or expired decisions grant no authority. An approved outcome authorizes only its bound action within the grant's validity; it must not enable a substituted tool, recipient, content, arguments, resource or decision.
- Atomically claim a single-use grant and record execution state to reject replay, concurrent consumption and cross-decision reuse, including after restart. Preserve audit events. If remote execution becomes uncertain after a crash/timeout, fail closed and require explicit recovery/new authorization; do not promise exactly-once external delivery.
- Exercise a real safe action through the documented interface, plus genuine non-approved denial and regression tests for substitution, replay, expiration, concurrency and crash recovery. Fixture-only tests cannot establish the live action demonstration.
- Preserve Hermes's own permissions/approval controls; never bypass them or patch core. Scope claims to actions routed through this plugin's guarded executor. Other Hermes tools, plugins and an authorized host operator remain outside that boundary: **Hermes-wide enforcement is not implemented or claimed**.

Current status: **PLANNED/EVALUATION only; no grant schema, guarded executor, real action-bound test or Hermes-wide coverage**. Track ACT-01/ACT-02 in ROADMAP.md and preserve status in HANDOFF.md across accounts.

## 6. P2 graphical experience and local access

Investigate the current official Desktop Plugin SDK and https://hermes-agent.nousresearch.com/docs/user-guide/desktop. Primary UI is official Hermes Desktop/Webapp, backed by genuine plugin data. Never modify private renderer state, core markup or internal stores.

Investigate `hermes webapp`, `hermes webapp --status`, configuration, local authentication and plugin loading. The user mentioned `http://127.0.0.1:9120`; this is a candidate default, **not a verified running URL**. Verify the actual served interface and authentication. Explain actual Windows-browser access to the WSL service and verify it, including required user participation. Bind locally only; no public exposure without an approved security design.

UI acceptance: overview; create decision; active detail; participant pending/responded status; pending/approved/rejected indicators; permitted history; expiry/cancel states; visible aggregate; error/empty/loading states; connection/gateway status; short onboarding. Real interactions and data, privacy-aware permissions, keyboard navigation, proper focus, contrast, responsive behavior and reduced motion. Inspect light/dark modes where practical. No static mockup may be presented as product evidence.

## 7. Naming, branding and skills

Keep **BlindCouncil** unless marketplace, public repository and obvious brand-name conflict research gives a compelling alternative. Any rename updates manifest, callbacks, README, metadata, tests and branding together. Positioning: trust, confidentiality, human coordination, clear decisions and professional reliability.

Read actual installed Creative Studio guidance, Hallmark, Impeccable, UI UX Pro Max, Brand Identity Studio and Frontend Motion Design when applicable. Read Hackathon Video Studio and Remotion before production. Use shared `~/hackathon-creative-studio` and `~/hackathon-video-studio`; dependencies must belong to the final project. Do not invent skill interfaces or assume a named skill exists without discovery.

Impeccable: follow its installed context/init instructions; initialize only in the final BlindCouncil project folder. `$impeccable init`, audit, critique, polish, bolder and distill are skill requests, not guessed shell commands. Apply only commands that improve the surface. No design command has run during P0.

Reference research where accessible: 21st.dev, Mobbin, React Bits, Magic UI, beUI, 60fps.design and suitable professional examples. Use free/suitably licensed assets. Aim for Linear/Apple Notes clarity: simple purpose, architecture, design, implementation; UX, DX and agent experience must improve without breaking behavior. Avoid generic AI SaaS, meaningless metrics, oversized gradients, decorative/excessive cards and buzzwords.

Deliverables: final name; original logo; icon-only mark; light/dark variants; typography; palette; favicon where relevant; Open Graph and social preview; README hero; marketplace screenshots; consistent demo-video identity. Motion may clarify creation, participant updates, pending-to-approved, rejection/cancel, confirmation, onboarding, panels/navigation. Keep it subtle, performant and accessible. Rerun functional tests after visual changes.

## 8. Onboarding and documentation

Explain installation, supported Hermes releases, Telegram setup, explicit approved-user configuration, invitations, creation, policy resolution, privacy/trust limits, recovery, troubleshooting, retention/deletion, guided demo and FAQs. Do not make the user infer architecture from a raw source tree. UI and docs must not overstate privacy.

## 9. Distribution, GitHub and catalog

Final dedicated repository belongs to **sopskistar**; do not publish the mixed research repository. Preserve its original evidence locally. Prepare a clean final tree, license, README, install/setup/security/architecture/troubleshooting documentation, genuine screenshots/examples, relevant tests, truthful manifest/capabilities/dependencies and tested minimum supported Hermes release.

Run `hermes plugins doctor . --ci` and `hermes plugins validate . --install-deps` from the final plugin directory using the selected isolated environment. Consult https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/catalog-submission. Pin the exact reviewed 40-character source SHA. A stable validated plugin's catalog PR must not be delayed for optional polish. Opened is not merged.

**Explicit user approval is required before publishing code, creating an external PR/submission, posting to X or deploying.** Prepare the concrete reviewable result first, then identify approval/account-authentication needs. Do not infer permission from the roadmap's desired eventual deliverables.

## 10. Video and submission

User-stated event information, to verify against current official instructions before submission: deadline November 11, 2026, 5 PM EST = 22:00 UTC = 23:00 WAT; prize pool $20,000, first place $10,000; judging usefulness, reliability, polish and creativity, with capability beyond an ordinary prompt/skill.

Produce a genuine MP4 under 90 seconds; target 75–85 seconds. Codex owns preparation, capture, editing, rendering and verification, using actual installed Hackathon Video Studio, Remotion and applicable design/motion guidance. Playwright may capture the real UI. Story: sensitive decision needing two approvals → prompting alone cannot enforce the controls → Hermes creates round → each actual account receives/responds → identity and deterministic policy resolve → Desktop shows genuine aggregate → real duplicate/authorization reliability test → usefulness/installability. No fabricated app states, callback evidence or results; clearly label illustration. Readable captions/UI, deliberate typography/pacing/transitions, useful sound and accurate privacy claims. Inspect final rendered file, duration, resolution and media path.

Prepare X post tagging **@NousResearch**; do not publish without approval. Required final package: working plugin; successful official validation; public repo; valid catalog PR with exact source SHA; under-90-second video; approved X post; official submission form https://form.typeform.com/to/FwJLvOln. Verify exact link fields/rules rather than assuming what “both links” means. Save links, approval state and evidence in `docs/SUBMISSION.md`. Never submit externally without user approval.

## 11. Optional site and future architecture

No separate Vercel site is needed for this product vision or initial distribution; verify marketplace rules when preparing admission. Only consider an informational/demo site after the working installable plugin and required submission assets. Do not introduce Neon, hosted auth/database or other dependencies just for presentation. An always-on Telegram listener is not a conventional Vercel serverless handler. Secrets remain with the Hermes gateway host. Document suitable future team hosting separately; do not provision paid resources without approval.

All additional policies, communications, governance, UX, integrations and infrastructure are retained with individual acceptance criteria/statuses in `ROADMAP.md`. They are not promises for this hackathon.

## 12. Evidence and recovery discipline

Read `AGENTS.md`, `PROJECT_STATUS.md`, `HANDOFF.md`, `DECISIONS.md`, `ROADMAP.md` and `TEST_EVIDENCE.md` at resume. Repository files, source and actual evidence outrank stale chat assumptions. Document conflicts, preserve working behavior, and never silently discard requirements.

After each meaningful milestone: update status, handoff, roadmap and evidence; commit verified source/docs locally; identify the next exact task. Before account/usage interruption, save state instead of starting an unfinished feature. Handoff must include path, branch/latest commit reference, implementation, actual tests, running processes, secret-free environment setup, blockers, exact next step, test commands and unfinished master-plan IDs. Never require the user to repeat this specification.

## 13. Reconciliation with earlier requirements

`BUILD_REQUIREMENTS.md` remains the earlier phase summary; this document expands it without removing requirements. Older Phase A/H names map to priorities P0–P3 above. TraceFork remains preserved and CONDITIONAL; BlindCouncil is the selected project. Older “notify owner only” is actual prototype behavior; the latest requirement for authorized participant aggregate notifications is planned under CORE-09. The prior no-GitHub stage is now a publication approval gate, not a mandate to abandon distribution. The earlier under-90-second requirement is refined to a 75–85-second target. User setup is complete; no repeat setup request is appropriate.


## November 10 checkpoint: native reliability gate complete

Genuine blocked delivery and targeted recovery for ac4e9f1d4090 passed with API/database audit plus user confirmation. Zero votes were accepted, original Forbidden retained, owner delivery unchanged, exact 24-hour deadline preserved. Supported cleanup then cancelled only this completed test round. Schema v3 durable notification work and native recovery are implemented and proven; older chronological gap descriptions above are historical, superseded by PROJECT_STATUS.md and TEST_EVIDENCE.md. Current remaining P1 gate is final distribution installation/removal/compatibility and exact-tree validation.

The dedicated distribution is being prepared locally at `release/blindcouncil/` inside this existing workspace. Preserve the research repository and all original evidence; never publish it wholesale. Once committed, the clean tree becomes the canonical distribution source. No external publication has been authorized.
