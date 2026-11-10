# Capability audit and scoped authorization investigation

Audit timestamp: November10,2026. Product vision: a privacy-conscious deterministic human authorization/decision engine for Hermes. Telegram is the first response channel, not the product boundary. This audit precedes any authorization extension.

| Area | Implemented | Actually verified | Missing/future |
|---|---|---|---|
| Agent-facing tools | None; manifest provides_tools=[] | Doctor/validator registration inventories0 tools | Structured request/status/execute tools and a real model-initiated run |
| Operator surfaces | Native CLI and authenticated operator RPC via ctx.register_rpc; Desktop via host.request |63 supporting methods; actual Hermes browser onboarding/create/24h default/five presets/one-hour choice/cancel confirmation/history; real SQLite audit | Complete responsive/auth-negative/error coverage; deploy UI to genuine history profile |
| Human identity | Native Telegram actor/private-message binding, current allowlist, membership/revocation | Genuine distinct accounts, wrong-message/revoked callback denial, duplicates | Other response channels and organizations |
| Policy | Exactly two participants; collect both; unanimous approve; any no prevents approval | Genuine Approve/Approve and Approve/Reject; supporting permutations/concurrency | Majority, quorum, veto, weights, abstention, multi-stage and delegation |
| Persistence/recovery | Schema3 decisions, immutable responses, deadlines/events, durable notification queue | Real restart, blocked-bot failure/targeted recovery; installer retention and tagged-core checks | Extended exports/retention/teams/backups beyond current scope |
| Action authorization | NOT implemented | No grant, action fingerprint, executor or protected action test exists | ACT-01/02 are planned; an APPROVED aggregate currently grants no execution authority |
| Hermes-wide control | NOT implemented or promised | No enforcement middleware registered | Explicitly outside scope; other tools/host/operator authority remain separate |

## Smallest safe candidate

An agent-callable request tool could bind exactly one `release_note.v1` action: create a bounded plain-text release note in a fixed plugin-owned directory through public plugin_data_dir(). No arbitrary filesystem path, command, recipient, URL or general-purpose tool name is accepted. A separate registered execute tool is the only plugin-owned path that writes that artifact. The public ctx.register_tool API supports this without middleware/core patches. Direct Python/storage is part of the plugin action; do not portray it as blocking arbitrary Hermes write_file/terminal calls.

Before collecting responses, fix a canonical versioned descriptor/digest including exact text, fixed destination/action kind, decision/request identity, original participant snapshot, policy version and validity deadline. Display an understandable exact action summary in the real private requests. No existing completed round may be retrofitted into authorization.

The executor must explicitly return structured denials on pending/rejected/cancelled/expired/unknown/unbound, descriptor mismatch, changed scope/participants, expired grant or replay. Recheck current permissions. Atomically claim a single-use grant before touching the fixed output; exclusive no-overwrite creation prevents substitution of another file. A crash after claiming fails closed as uncertain; never reissue authority automatically or claim exactly-once external effects. An approved decision remains an historical result after its response deadline, but a separate grant validity check must still reject late execution.

Safer API scope for the first release: trusted local/Desktop operator sessions only through documented context identity. Telegram remains the authenticated human response transport; no new participant may gain coordinator authority through a model tool. Inspect public ctx.client/execution identity before adding tool reachability. Preserve Hermes approvals; ordinary approval prompts/transport callbacks do not by themselves prove an exact action grant.

## Feasibility and gates

Documented registration/storage APIs support a narrowly scoped guard; no fundamental API blocker is established. This is research/design, NOT implemented or live-tested action authorization. Current native middleware fail-open behavior must never be the guard. A missing grant or exception must have no path to the file-writing code.

Complete required Desktop/validation/publication preparation first. Timebox an isolated implementation spike afterward; abandon/defer it if it threatens the catalog/video deadline. It must earn: real registered Hermes tool integration, all denials/replay/substitution/concurrency/crash regressions, a harmless actual artifact write and genuine two-account approval of that specific descriptor. A fixture-only pass cannot satisfy the real human gate. A CLI/dispatch_tool invocation is not evidence that an AI model independently initiated the workflow; paid/unavailable model access stays explicitly blocked unless approved.

The earlier owner-only Telegram-announcement candidate remains an alternative, not removed from scope. It has more remote-acknowledgement and native-worker integration complexity than a fixed local artifact, so it is not the first spike choice. No new MCP server or broad action-interception layer is justified.

All future majority/quorum/veto/multi-stage/delegation/channels/audit exports/templates/team roles/organizational workflows remain in ROADMAP.md. No existing functionality or genuine evidence is discarded.
