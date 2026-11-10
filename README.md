# BlindCouncil

**Private decisions. Shared outcomes.**

BlindCouncil is a native Hermes Agent plugin for two-person approvals through private Telegram requests. Both authorized accounts must approve. A deterministic policy, rather than an AI response, determines the result.

Real Telegram callbacks are checked against the sender, current allowlist, decision membership and original private message. Responses survive gateway restarts. A durable notification queue retries recoverable failures and retains blocked-delivery history.

## Current release

Version 0.1.0 is a locally verified release candidate. Public GitHub publication and catalog submission are pending owner approval. The operator CLI and native Telegram integration work; the Desktop interface and demo video are still planned. No screenshots or simulated integrations are presented as completed features.

Tested with official Hermes source `2c955c3a8c0bf8f52cbfad13ed3215ade4eb6f94` (`vgit.2c955c3`), Python 3.14.9 and python-telegram-bot 22.8. BlindCouncil requires the official native platform-handler and supervised-task APIs and runs **in process**. Compatibility with older Hermes releases has not been established.

## Install and configure

Use a recent official Hermes installation with Telegram support. Install this repository at an explicitly reviewed 40-character commit:

```bash
hermes plugins install <GIT_URL> --ref <REVIEWED_40_CHARACTER_SHA> --enable --yes-deps
```

These placeholders are intentional until publication. `--yes-deps` consents to Hermes preparing the declared Python dependency; review it first. Interactive installation can ask instead. Hermes owns dependency management.

1. Run `hermes gateway setup` in your own terminal. Configure **one Telegram bot** and explicitly allowlist both participant IDs. Keep its token in Hermes' local secret configuration.
2. Both accounts must open that same bot and press **Start**. A bot cannot initiate a private conversation with an account that has not started it.
3. Run `hermes blindcouncil configure`. Enter the two distinct numeric account IDs locally. Account 1 is the coordinator and also a participant. No bot token is requested by this command.
4. Run `hermes blindcouncil readiness`, then start your usual `hermes gateway run`. Run only one gateway poller for the bot.

The commands use your selected Hermes home/profile. For an experiment, set `HERMES_HOME` to a dedicated home before installation and setup. Do not copy an unrelated profile's secrets or change its settings.

## Make a decision

```bash
hermes blindcouncil create \
  --title "Approve the release checklist" \
  --description "Both reviewers must confirm that the checklist is complete." \
  --expires 24h
hermes blindcouncil status --round-id ROUND_ID
hermes blindcouncil history --limit 20
```

Each participant receives a separate private request with **Approve** and **Reject** buttons. One accepted response leaves the round PENDING. After both respond, two approvals produce APPROVED; a rejection produces REJECTED. Responses are immutable. This release collects both responses before resolving, including when the first response is a rejection.

Normal expiry choices are `15m`, `1h`, `24h`, `3d` and `7d`; the default is **24 hours**. The exact UTC deadline is persisted once and is never extended by a restart or retry. Short `/bcprobe expire SECONDS` durations exist solely for explicit integration tests.

```bash
hermes blindcouncil cancel --round-id ROUND_ID
hermes blindcouncil notifications --round-id ROUND_ID
hermes blindcouncil retry-notifications --round-id ROUND_ID
```

Inspect notification status before retrying. Retry queues only blocked work for that round. After expiry or cancellation an old invitation cannot be revived; a blocked terminal result is a different kind of message. Transient failures retry automatically with bounded backoff. Unblock the bot and press Start before retrying a Forbidden delivery. See [notification recovery](docs/NOTIFICATIONS.md).

## Privacy and authority

- Participants receive private requests and authorized aggregate outcomes. Operator CLI outputs expose progress and aggregates, not individual answers or account IDs.
- Two-person unanimity can permit someone to **infer** another person's answer from their own answer and the aggregate. This is controlled disclosure, not cryptographic secrecy.
- The trusted gateway operator, host and installed in-process code can access the local database. This is not end-to-end encryption, zero knowledge or tamper-proof storage.
- Two Telegram accounts prove distinct authenticated account identities, not two independent humans.
- BlindCouncil does **not** currently authorize or block other Hermes actions. Action-bound enforcement is planned. No Hermes-wide enforcement is claimed.
- Telegram may deliver duplicates after an uncertain network acknowledgement. Database mutations and logical notification work are idempotent; exactly-once external delivery is not promised.

Read [security and data handling](SECURITY.md) before using sensitive decisions.

## Verification and development

Genuine two-account approval/rejection, duplicate protection, cancellation, expiry, wrong-message denial, participant revocation, restart persistence, queued delivery recovery and a real blocked-bot failure/retry were exercised through the native Hermes gateway. Selected sanitized original evidence is in [docs/evidence](docs/evidence/PROVENANCE.json). Supporting tests use synthetic identities and transport and are labelled separately.

```bash
hermes plugins doctor . --ci
hermes plugins validate . --install-deps
python3 scripts/test.py --help
```

The test runner reuses an existing Hermes-managed environment and creates temporary credential-free test homes. It never starts Telegram polling or loads the live profile's secret file. See [architecture](docs/ARCHITECTURE.md), [troubleshooting](docs/TROUBLESHOOTING.md), and [project status](PROJECT_STATUS.md). All unfinished requirements remain in the [master plan](PROJECT_MASTER_PLAN.md) and [roadmap](ROADMAP.md).

MIT licensed. No paid model API, hosted database, independent Telegram bot service, MCP server or Vercel deployment is required.
