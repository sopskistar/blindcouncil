# Troubleshooting

| Symptom | Check |
|---|---|
| Plugin command missing | Confirm the plugin is installed and enabled in the selected Hermes home. Run Plugin Doctor. A different profile has different config. |
| Missing native API error | Use a recent official Hermes with native platform-handler and supervised-task APIs. Only the source revision in README is tested. |
| Readiness blocked | Configure exactly two distinct positive numeric user IDs; the owner must be one; both must be explicitly allowlisted in Hermes Telegram settings. Do not use wildcard/allow-all mode. |
| No private invitation | Both accounts must Start the same bot. Keep one native gateway running. Inspect `notifications --round-id ...`; creation queues work and does not claim delivery. |
| Forbidden | The recipient may have blocked/not started the bot. Unblock, Start, inspect the round and notification kinds, then retry blocked work only for that round. Error history is retained. |
| Invitation expired before retry | Create a new decision. Do not extend/reset a past deadline or revive its old buttons. The old round/evidence stays terminal. |
| Repeated tap | The first accepted response is immutable. A repeat reports already recorded and adds no vote or logical result work. |
| Not authorized for account or message | Use the original private request on the authorized account. A forwarded/copy/diagnostic message, revoked membership or missing current allowlist must be denied. |
| Could not save response | A storage failure is not acceptance. Check disk access/space and retry after recovery. Do not edit votes by hand. |
| Extra external message after a crash | An uncertain Telegram acknowledgement can lead to another delivery. Check logical state and delivery history; this release does not promise exactly-once transport. |
| Developer probe refuses | Synthetic probes are restricted to explicit temporary test homes. Use the supporting test runner, never disable this guard on a live profile. |

No model provider is needed to run decisions. Never paste a Telegram token into chat/issues or include private configuration in diagnostic output.
