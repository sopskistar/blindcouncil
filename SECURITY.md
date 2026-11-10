# Security and data handling

BlindCouncil trusts Hermes, the gateway host/operator, Telegram and installed in-process plugin code. It verifies Telegram callback identities and permissions at its own decision boundary. It cannot prevent a host administrator or another authorized tool from reading or modifying files.

## Data and disclosure

The plugin stores decision titles/descriptions, participant numeric IDs, individual immutable responses, original message bindings, callback/update identifiers, lifecycle events, exact deadlines and delivery/error history in Hermes plugin SQLite storage. It does not store or read the Telegram bot token. Hermes supplies the existing native SDK client.

The local coordinator is trusted to create decisions and see permitted history/progress/aggregates. A coordinator is also one of the two participants. Their local CLI is an operator interface, not a remote login mechanism. Configure it only on a trusted host.

Invitations are private Telegram messages. Only currently authorized participants receive aggregate notifications. The API does not return individual answers. However, two-person unanimity and knowledge of one's own answer can reveal the other's answer by inference. Telegram's own data handling also applies. Do not describe this as encrypted voting, zero knowledge or anonymous consensus.

## Authentication and mutation

The sender comes from the genuine SDK update, never from callback text. Accepting a response requires current explicit allowlisting, membership, a non-revoked invitation, the original private recipient/message binding, a valid choice and an active deadline/state. A database transaction protects concurrent submissions. An already recorded response cannot be overwritten by a duplicate or different choice.

Callbacks use only the `blindcouncil:` namespace. Hermes normal buttons remain owned by Hermes. Developer probes require a separate test home and refuse a home containing a secret file. These guards reduce accidents; they are not a sandbox against a trusted operator.

## Reliability limits

Database state and logical notification work commit together. Delivery leases recover after crashes, but a crash after Telegram accepted a message and before local acknowledgement can produce a duplicate on retry. Neither exactly-once Telegram delivery nor cryptographic audit authenticity is promised. Permanent failures remain visible and require an explicit retry after correcting setup. A delayed callback cannot revive a cancelled/expired decision.

Revoking a participant blocks future responses. Previously accepted responses remain immutable and are not retroactively deleted or invalidated. Cancel an unresolved round if a membership change makes its existing consent unsuitable.

## Retention, backups and deletion

There is no automatic retention purge in 0.1.0. Records stay in the selected `HERMES_HOME` plugin data directory until the operator intentionally deletes them. Plugin removal should retain data; the exact tested installer behavior is recorded in release evidence. Do not infer secure deletion from removing code.

For backup, stop the gateway and other writers first, then copy the plugin data directory using restrictive permissions. Keep backups private: they contain account IDs and responses. Restore only into a compatible isolated profile and verify state before reconnecting the bot. SQLite WAL/SHM files may exist while writers run; copying only an active database file is not a reliable backup.

For intentional full deletion, stop writers, identify the selected profile's BlindCouncil data path and remove only that plugin's data and private backups after confirming the scope. This destroys history and recovery state. Hermes' unrelated configurations, credentials and other plugin data must remain untouched. This release provides no claim of forensic erasure.

## Reporting

Do not include bot tokens, numeric participant IDs, private responses, secret configuration or raw credential-bearing HTTP URLs in public issues or recordings. Until a private reporting channel is published, send a minimal sanitized description to the repository owner and request a private route for sensitive details.
