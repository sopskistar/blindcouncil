# Native Desktop and Webapp

BlindCouncil adds an opt-in page, sidebar entry and command-palette action through the official Hermes Desktop SDK. It reads the same decisions as the CLI through `plugin.blindcouncil.operator`, registered with `ctx.register_rpc`. It is an authenticated **operator** interface, not participant login and not a vote-submission endpoint.

## Open it locally

After installing and configuring the plugin in your selected Hermes profile:

```bash
hermes config set webapp.enabled true
hermes gateway restart
hermes webapp --status
hermes webapp --no-open
```

Keep only one Telegram gateway poller running for the bot. If your existing gateway already serves the Webapp, omit the restart. Keep the default loopback bind. The last command prints a private one-use sign-in link: open it within 60 seconds and do not share or record it. A bare address does not sign you in. See the [official Webapp guide](https://hermes-agent.nousresearch.com/docs/user-guide/desktop).

In Hermes, open **Capabilities → Plugins**, search for **BlindCouncil**, and enable its Desktop half. Then choose **BlindCouncil** in the sidebar. A fresh browser profile may need this opt-in. If no inference provider is configured, Hermes' normal **I'll choose a provider later** option allows the decision interface to work without purchasing or calling a model. A host-level “inference unavailable” indicator is separate from BlindCouncil's gateway connection.

From Windows with the gateway in WSL, open the private link printed in your Ubuntu terminal in your Windows browser. Automated WSL browser access has passed; manual Windows relay/authentication confirmation remains outstanding. Do not solve a relay problem by exposing the gateway publicly.

## Available workflow

- Overview/history and detail read actual permitted plugin records.
- **New decision** collects a title, optional context and one of 15 minutes, 1 hour, 24 hours, 3 days or 7 days. Default: 24 hours. The exact stored UTC deadline remains visible.
- Progress shows the number of responses and message bindings. Individual answers and numeric account IDs are not returned.
- Pending decisions can be cancelled after confirmation; cancellation preserves existing responses. Approved, rejected, cancelled and expired states are distinct.
- Notification status shows logical invitation/result jobs. Retry queues blocked work only. Read the message kind and state before retrying: an expired invitation must not become a fresh request, and a blocked terminal-result job is separate work.
- Loading, setup, empty, connection and error states provide recovery guidance. Creating a round while delivery is unavailable can queue requests; an adapter-loaded indicator does not certify Telegram network health.

This interface uses native theme tokens and controls, scoped styles and reduced-motion handling. It does not patch Hermes' renderer. Final branding, exhaustive contrast/theme review and video assets are unfinished.

On narrow screens the history precedes the selected detail, so a long history requires scrolling to its result. A separate compact detail navigation is a future UX refinement; responsive width checks alone do not certify the complete mobile experience.

## Evidence

[Create/cancel/history and exact stored expiry](evidence/native-ui-20261110/browser-and-storage-proof.json) use actual Hermes browser/RPC/SQLite with explicitly synthetic participants in a token-free home. [Authentication and responsive checks](evidence/native-ui-20261110/browser-auth-responsive-proof.json) include anonymous HTTP401, focused form errors and desktop/tablet/phone geometry. [Genuine history](evidence/native-ui-20261110/primary-history-proof.json) verifies existing real Telegram outcomes after a controlled release upgrade. Viewing old outcomes is not a new Telegram callback test.
