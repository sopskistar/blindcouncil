# Architecture

The root native Hermes entry point delegates to `blindcouncil.register`. It registers one official Telegram platform-handler factory and the local `hermes blindcouncil` CLI. There are currently no model tools or model calls.

1. Hermes supplies the existing python-telegram-bot Application to the factory. The plugin adds scoped callbacks and an owner-only integration command, and starts one owned worker through `ctx.spawn_task`.
2. `policy.py` authenticates identity/message/state and executes deterministic two-person unanimity inside transactions. It never accepts a model-submitted vote.
3. `lifecycle.py` maintains schema version 3, additive migration, state transitions, revocations and audit events. Unknown legacy timestamps remain unknown rather than fabricated.
4. `outbox.py` atomically creates unique invitation/result work. Claims have expiring lease tokens. Stale completions cannot overwrite newer work. Terminal transitions obsolete unsent invitations.
5. `notification_worker.py` uses the supplied native bot. It persists a private message binding before attaching actionable buttons. It retries recoverable errors, blocks permanent errors, sweeps expiry and preserves attempt/error history.
6. `plugins.plugin_storage.plugin_db()` supplies persistent SQLite storage under the selected Hermes home. Operator CLI projections return permitted metadata and aggregate progress only.

No independent poller, credential-file reader, private renderer mutation or core monkey patch is needed. The plugin is intentionally in process because its native factory receives the SDK client. This means the plugin is trusted code, not a sandboxed security boundary.

Desktop/Webapp integration is a planned official SDK extension. It must read genuine permitted data and cannot fabricate votes. Action-bound approval enforcement is also planned, with no current authority over other Hermes tools. See the preserved master plan for its single-use exact-action acceptance criteria.
