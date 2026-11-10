# Active gate: genuine two-account Telegram callbacks

Current phase: **remaining genuine negative/lifecycle tests**. Local setup is complete; do not rerun it. Real two-account Approve/Approve, duplicate protection, Approve/Reject and native restart recovery have evidence. Earlier synthetic tests remain separate and cannot establish a live pass.

Completed rounds: `38378f7fbe90` APPROVED (two receipts); `6917ad5b2a4e` CANCELLED after the user's mistaken Account 2 approval (one receipt preserved); `cb54bed1b2b7` REJECTED (two distinct native receipts, unchanged after restart). Current process is recorded in HANDOFF.md.

**Cancelled late callback LIVE PASS**: native attempt at November 9 17:04:45 UTC, still one response/receipt and unchanged fingerprint; do not repeat. Evidence: `evidence/recovery-20261110/cancelled-late-callback-audit.json`.

**Expired late callback LIVE PASS:** `f79effc48d29`, zero votes/receipts, native expired attempt; all four terminal states persisted through actual restart/schema v2 migration.

**Scoped callback gates complete:** f5b02a4352bb had genuine wrong-message and revoked-participant denials, both with zero accepted votes/receipts and pending state at audit. The supported CLI then cancelled that completed test round, preserving both native attempts/revocation. No pending click. Next P1 notification reliability/recovery requires isolated tests and a deliberate actual-gateway exercise after validated deployment. Do not rerun passing rounds; global unallowlisted third-account test has not been performed.

The general setup/initial-approval checklist below is retained for new installations. Do not repeat completed tests in the current workspace.

## One-time local setup

In your own WSL terminal:

```bash
cd /home/sopski/projectresearch/hermes-feasibility-20261109
python3 probes/setup_live_telegram.py
```

The helper runs Hermes's official Telegram setup wizard, then the plugin's operator configuration command. Choose Telegram; enter a BotFather token locally or use Hermes's managed-bot QR flow. Explicitly allowlist both actual account IDs. Decline service installation/start for this test. Exit the wizard, then enter account 1's numeric ID as owner and account 2's distinct numeric ID. Never paste the bot token into chat or pass it in command-line arguments. A dedicated test bot avoids interfering with an existing poller.

The helper confines configuration to `isolated-home`, restricts `.env` to mode 600 and does not record input. Neither the plugin nor this helper reads the bot token; Hermes owns it. Open the configured bot from each actual account and press Start. Tell Codex that setup is complete, without secret values.

## Native run and clicks

Codex will verify `blindcouncil readiness`, then run the official foreground `hermes gateway run` using `probes/hermes_local.py`. No independent polling client or synthetic transport may be used for this gate.

1. Account 1 sends `/bcprobe` to the bot. Both private chats must receive their own request.
2. Account 1 presses Approve. Its acknowledgement must say `Response recorded privately.`
3. Account 2 presses Approve in **its own private request**. Its acknowledgement must be the same. The owner must receive APPROVED after both responses.
4. Press account 2's button again. It must be treated as a duplicate, with only two stored responses.
5. Codex audits that round with `blindcouncil evidence --round-id <id>`. Both configured identities must have distinct stored callback receipts marked as arriving through the native Hermes Telegram factory; no individual vote or raw participant ID is exported by this command.
6. Restart the actual gateway and re-audit the round. Then create another round and repeat with Approve from account 1 and Reject from account 2; expect REJECTED after both responses.

For a genuine unauthorized-user test without a third account, a later round can run with a temporarily stricter process-local Telegram allowlist excluding account 2, then verify its genuine tap is refused without changing the vote count. Never edit the user’s .env/config for this test. Stop the one poller before switching process settings and restore the normal process after the negative test. The wrapper and dispatch behavior must be verified first. This has not yet been run.

Factory/receipt origin metadata supports auditing, but it is not independent proof of human interaction. Verify the running native gateway and actual button presses as well. Missing configuration, a failed startup or absent second-account callback leaves the gate BLOCKED.
