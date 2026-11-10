# Action-bound approval: investigated, not implemented

BlindCouncil is intended as a human authorization and decision engine. Telegram is the first authenticated human response channel. Today the plugin coordinates decisions; an APPROVED aggregate grants **no execution authority**. There are zero agent tools and zero protected executors. This investigation does not promote ACT-01 to implemented or tested.

## Smallest safe candidate

An agent could request one `release_note.v1` operation: release exact bounded plain text as a file in a fixed plugin-owned directory. The public [tool and storage APIs](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins) support registering the request/status/execute tools and obtaining `plugin_data_dir("blindcouncil")`. No shell command, arbitrary path, recipient, URL or general tool name would be accepted. The protected boundary would be **this plugin's artifact writer only**. Other Hermes filesystem tools and the trusted host operator remain outside it.

Proposed tools, not current registrations:

| Tool | Proposed behavior |
|---|---|
| Request authorization | Validate bounded text, snapshot configured participants and policy, create an immutable versioned descriptor and exact deadline, atomically persist the decision/binding before any invitation can be sent. Return ID/fingerprint and aggregate only. |
| Check authorization | Return permitted progress/state and grant status, never individual choices. |
| Execute approved note | Reconstruct and compare the exact descriptor, check current permissions and unexpired approved state, claim a single-use grant transactionally, then exclusively create the one fixed output file. |

The descriptor must cover decision/request ID, action version, exact UTF-8 text, fixed destination kind, participant snapshot, policy version and validity deadline. Human requests must display the exact understandable action before accepting responses. Reject unrenderable/control-character input rather than consent to one visual representation and execute different bytes. Do not retrofit any existing approved round into a grant.

## Fail-closed contract

The executor has a single guarded route to the file effect. Unknown/unbound decisions, missing or unreadable storage, exceptions, pending/rejected/cancelled/expired states, expired grants, parameter/digest substitution, changed participants/permissions, revoked membership, cross-decision/profile reuse and already-claimed grants all return structured denials without opening the output file.

An atomic claim precedes the file write; concurrent executions cannot both claim it. Exclusive creation disallows overwrite. A crash after claiming is **uncertain/consumed**, not permission to retry automatically. SQLite and a filesystem effect do not form one atomic transaction; accept lost execution after a crash rather than risk duplicate authority. Record audit/recovery state and require a new approval where certainty cannot be recovered. Never claim exactly-once effects.

An approved historical decision can remain APPROVED past its response deadline. The executor must independently check grant validity, rather than equating historical approval with permanent permission.

## Hermes API findings

The reviewed v0.23.1 plugin surface documents `ctx.register_tool`, `ctx.dispatch_tool`, `plugin_db` and `plugin_data_dir`. `dispatch_tool` retains the host's normal approval/redaction/budget pipeline; it is not authorization by itself. Public `ctx.session_surface()` reports a calling surface; a surface label is not independent human identity. The first candidate should accept trusted local coordinator sessions only and deny unknown/messaging callers unless an authenticated coordinator mapping is designed. Model-supplied owner IDs must never select authority.

Middleware is unnecessary here. Hermes' fail-open execution middleware must never decide whether the file-writing branch runs. A custom approval transport or an aggregate notification also cannot substitute for exact action binding and single-use execution.

## Required evidence and current decision

No fundamental public-API blocker was found for the narrow boundary. Implementation remains deferred behind the required UI, reviewed catalog candidate and genuine video. No grant schema, writer, registered action tools or real action-bound human test currently exists.

Before promotion, require registered-tool loading through actual Hermes; all denial/substitution/replay/concurrency/crash cases; restart persistence; a real harmless artifact; and genuine two-account approval of that specific descriptor. A registered-tool dispatch or CLI call is not proof that a Hermes model initiated the request. Real agent initiation needs authorized model access; unavailable or potentially billable access remains BLOCKED without approval. Never use fixture model outputs to fill that gap.

ACT-01 retains the earlier predeclared Telegram-announcement alternative, but uncertain remote acknowledgement and worker integration make it more complex than a fixed local note. ACT-02 preserves additional guarded integrations. All policies/channels/teams/organizational workflows remain in [ROADMAP.md](../ROADMAP.md).
