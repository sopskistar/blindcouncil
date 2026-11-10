# Architecture

The root native Hermes entry point delegates to `blindcouncil.register`. It registers one official Telegram platform-handler factory, the local `hermes blindcouncil` CLI and an authenticated operator RPC. There are currently no agent-facing tools or model calls. Telegram is the first human response channel for the broader decision-engine product.

1. Hermes supplies the existing python-telegram-bot Application to the factory. The plugin adds scoped callbacks and an owner-only integration command, and starts one owned worker through `ctx.spawn_task`.
2. `policy.py` authenticates identity/message/state and executes deterministic two-person unanimity inside transactions. It never accepts a model-submitted vote.
3. `lifecycle.py` maintains schema version 3, additive migration, state transitions, revocations and audit events. Unknown legacy timestamps remain unknown rather than fabricated.
4. `outbox.py` atomically creates unique invitation/result work. Claims have expiring lease tokens. Stale completions cannot overwrite newer work. Terminal transitions obsolete unsent invitations.
5. `notification_worker.py` uses the supplied native bot. It persists a private message binding before attaching actionable buttons. It retries recoverable errors, blocks permanent errors, sweeps expiry and preserves attempt/error history.
6. `plugins.plugin_storage.plugin_db()` supplies persistent SQLite storage under the selected Hermes home. Operator CLI projections return permitted metadata and aggregate progress only.
7. `operator_rpc.py` registers `plugin.blindcouncil.operator` through `ctx.register_rpc`. Native `desktop/plugin.js` calls it through SDK `host.request`; its sidebar/page/palette contributions use the official SDK. The gateway authorizes the operator connection and selects the profile. Configuration determines the coordinator; caller parameters cannot impersonate a participant or submit a vote. Storage and configuration exceptions return generic errors.

No independent poller, credential-file reader, private renderer mutation or core monkey patch is needed. The plugin is intentionally in process because its native factory receives the SDK client. This means the plugin is trusted code, not a sandboxed security boundary.

The Desktop/Webapp interface has actual browser/RPC creation, cancellation/history, validation, authentication and responsive evidence, plus read-only inspection of genuine Telegram history after a controlled upgrade. Manual Windows access and final visual polish remain open. [Desktop guide](DESKTOP.md).

[Action-bound approval](ACTION_BOUND_APPROVAL.md) remains investigated/planned. No current grant or protected executor exists and no authority over other Hermes tools is claimed. See the master plan for single-use exact-action acceptance criteria.
