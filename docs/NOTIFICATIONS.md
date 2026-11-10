# Notification reliability and scope

Status: implemented; 52 supporting tests plus genuine native queued-invitation recovery, approvals and aggregate deliveries to both accounts passed. Real blocked-bot Forbidden failure is preserved; recovery retry remains pending. See PROJECT_STATUS.md/HANDOFF.md for the latest live state.

The plugin uses Hermes-supported SQLite storage and the existing native Telegram application's bot. It starts one owned task through the public installed `PluginContext.spawn_task` method; no separate poller, MCP server, hosted database or external worker is required. The native client is supplied through the [official platform-handler interface](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins#register-native-platform-handlers-any-platform). `PluginContext` and storage helpers are listed in the [public API](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins/public-api); the task lifecycle contract is documented in the installed pinned source's method docstring.

## Persistence and transactions

- Creation and one logical invitation per participant commit in the same transaction.
- A new approved/rejected/cancelled/expired transition and its aggregate notifications commit together. Repeated callbacks/transitions cannot create another logical result job for the same recipient.
- Schema v3 adds notification jobs/events without replaying historical terminal results. Existing decisions, private answers, accepted receipts and origins are retained.
- Requests are initially sent without buttons. Their private message binding is stored before the actionable keyboard is attached. Attachment retries reuse that bound message. An uncertain extra text-only send is not authorized for responses.
- Workers claim a 60-second lease transactionally. Another worker may reclaim expired leases; an old lease cannot overwrite the newer worker's state.
- Automatic retry uses bounded exponential delays for transient Telegram errors, honors rate limits, and blocks after eight transient failures. Permanent errors and unauthorized recipients are blocked immediately. Explicit owner retry preserves cumulative attempts/history; after automatic exhaustion a manual retry permits another attempt, not an erased failure history.
- The worker checks deadlines and current allowlist/decision revocations. Revoked or globally disallowed recipients are not sent new messages. Expiry still checks inside policy transactions even if the worker is stopped.

## Aggregate recipients and privacy

For new transitions, both currently authorized participants receive only the aggregate state. Individual responses are excluded. A two-person unanimous outcome can nevertheless reveal another person's answer by inference; no stronger anonymity/secrecy promise is made. The host operator and other trusted code with host access can read local storage. No end-to-end encryption, zero knowledge, independent-human consensus or tamper-proof storage claim.

## Operator commands

```bash
python3 probes/hermes_local.py blindcouncil create --title "Review release" --description "Approve the proposed release." --expires 24h
python3 probes/hermes_local.py blindcouncil status --round-id ID
python3 probes/hermes_local.py blindcouncil history --limit 20
python3 probes/hermes_local.py blindcouncil notifications --round-id ID
python3 probes/hermes_local.py blindcouncil retry-notifications --round-id ID
```

The fixed owner comes from local plugin settings; these are trusted local operator interfaces, not remote authentication endpoints. Production preset choices are 15m/1h/24h/3d/7d, default 24h. `/bcprobe expire SECONDS` remains the explicit short integration-test path. Title plus description must fit a 3600 UTF-16-unit budget so the full invitation fits Telegram; storage is not silently truncated.

`Forbidden` usually means the recipient blocked the bot or has not started the chat. Ask that participant to unblock/start the bot, then retry blocked notifications. `NetworkError`/`TimedOut` normally remain queued for automatic retry. `recipient_not_authorized` requires reviewing the existing allowlist/decision revocation; retry cannot bypass it. Status returns aggregate counts and safe error codes, never recipient IDs or choices. Detailed retry events remain in private plugin storage.

## Delivery limits

Logical work is deduplicated. Telegram delivery is not exactly-once: a successful remote send followed by a lost acknowledgement or a crash before commit may be retried and appear twice. The supporting regression suite explicitly demonstrates that uncertainty. A duplicate callback itself creates no additional logical result work. Keep these separate in demo/security claims.

The running profile's disabled lazy-install policy is preserved. Developer validation dependency preparation uses an explicit Hermes PM operation, then the official validator is rerun; it does not relax security configuration. Runtime plugin code never invokes this development preparation probe.
