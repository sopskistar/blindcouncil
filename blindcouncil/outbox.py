"""Durable logical notifications. No network, credentials, or private output here."""
import json
import secrets

TABLES = (
    """CREATE TABLE IF NOT EXISTS notification_outbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,round_id TEXT NOT NULL,user_id TEXT NOT NULL,
        kind TEXT NOT NULL CHECK(kind IN ('invite','result')),
        state TEXT NOT NULL CHECK(state IN ('queued','leased','sent','blocked','obsolete')),
        attempts INTEGER NOT NULL DEFAULT 0,next_attempt REAL NOT NULL,
        lease_token TEXT,lease_until REAL,last_error TEXT,message_id INTEGER,
        created_at REAL NOT NULL,updated_at REAL NOT NULL,
        UNIQUE(round_id,user_id,kind))""",
    "CREATE INDEX IF NOT EXISTS notification_ready ON notification_outbox(state,next_attempt,lease_until)",
    """CREATE TABLE IF NOT EXISTS notification_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,notification_id INTEGER NOT NULL,
        outcome TEXT NOT NULL,error_code TEXT,occurred_at REAL NOT NULL)""",
)


def enqueue_invites(conn, identifier, people, stamp):
    for person in people:
        _enqueue(conn, identifier, person, "invite", stamp)


def enqueue_result(conn, identifier, stamp):
    # Called only on a NEW terminal transition, never while importing old terminal rows.
    row = conn.execute("SELECT participants FROM rounds WHERE id=?", (identifier,)).fetchone()
    if row is None:
        raise RuntimeError("Notification decision is missing")
    conn.execute("""UPDATE notification_outbox SET state='obsolete',updated_at=?
        WHERE round_id=? AND kind='invite' AND state IN ('queued','leased','blocked')""", (stamp, identifier))
    for person in json.loads(row[0]):
        _enqueue(conn, identifier, person, "result", stamp)


def _enqueue(conn, identifier, person, kind, stamp):
    conn.execute("""INSERT OR IGNORE INTO notification_outbox
        (round_id,user_id,kind,state,next_attempt,created_at,updated_at)
        VALUES (?,?,?,'queued',?,?,?)""", (identifier, str(person), kind, stamp, stamp, stamp))


def claim():
    from . import lifecycle, policy
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        stamp = lifecycle.now()
        row = conn.execute("""SELECT id,round_id,user_id,kind,attempts FROM notification_outbox
            WHERE (state='queued' AND next_attempt<=?) OR (state='leased' AND lease_until<=?)
            ORDER BY id LIMIT 1""", (stamp, stamp)).fetchone()
        if row is None:
            return None
        token = secrets.token_hex(16)
        conn.execute("""UPDATE notification_outbox SET state='leased',attempts=attempts+1,
            lease_token=?,lease_until=?,updated_at=? WHERE id=?""", (token, stamp + 60, stamp, row[0]))
        conn.execute("INSERT INTO notification_events(notification_id,outcome,occurred_at) VALUES (?,'leased',?)", (row[0], stamp))
        return dict(zip(("id", "round_id", "user_id", "kind", "attempts", "lease_token"),
                        (*row[:4], row[4] + 1, token)))


def view(job, allowed):
    """Check lease, current permissions and lifecycle before touching the native client."""
    from . import lifecycle, policy
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        lease = conn.execute("SELECT state,lease_token FROM notification_outbox WHERE id=?", (job["id"],)).fetchone()
        if lease != ("leased", job["lease_token"]):
            return None
        row = conn.execute("""SELECT r.participants,l.title,l.description,l.expires_at
            FROM rounds r JOIN round_lifecycle l ON l.round_id=r.id WHERE r.id=?""", (job["round_id"],)).fetchone()
        if row is None:
            raise RuntimeError("Notification decision metadata is missing")
        state = lifecycle.state(conn, job["round_id"])
        revoked = conn.execute("SELECT 1 FROM participant_revocations WHERE round_id=? AND user_id=?",
                               (job["round_id"], job["user_id"])).fetchone()
        binding = conn.execute("SELECT chat_id,message_id FROM deliveries WHERE round_id=? AND user_id=?",
                               (job["round_id"], job["user_id"])).fetchone()
        return {"state": state, "title": row[1], "description": row[2], "expires_at": row[3],
                "authorized": job["user_id"] in {str(x) for x in allowed}
                    and job["user_id"] in json.loads(row[0]) and not revoked,
                "binding": binding}


def finish(job, state, *, message_id=None, error=None, delay=0):
    from . import lifecycle, policy
    if state not in {"queued", "sent", "blocked", "obsolete"}:
        raise ValueError("Invalid notification state")
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        stamp = lifecycle.now()
        changed = conn.execute("""UPDATE notification_outbox SET state=?,message_id=COALESCE(?,message_id),
            last_error=?,next_attempt=?,lease_token=NULL,lease_until=NULL,updated_at=?
            WHERE id=? AND state='leased' AND lease_token=?""",
            (state, message_id, error, stamp + delay, stamp, job["id"], job["lease_token"])).rowcount == 1
        if changed:
            conn.execute("INSERT INTO notification_events(notification_id,outcome,error_code,occurred_at) VALUES (?,?,?,?)",
                         (job["id"], state, error, stamp))
        return changed


def save_binding(job, chat, message):
    """A retry reuses the first durable message. Extra uncertain sends never get buttons."""
    from . import policy
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        lease = conn.execute("SELECT state,lease_token FROM notification_outbox WHERE id=?", (job["id"],)).fetchone()
        if lease != ("leased", job["lease_token"]):
            return False
        conn.execute("INSERT OR IGNORE INTO deliveries VALUES (?,?,?,?)",
                     (job["round_id"], job["user_id"], str(chat), int(message)))
        return True


def expire_due():
    from . import lifecycle, policy
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        identifiers = conn.execute("""SELECT round_id FROM round_lifecycle
            WHERE state='pending' AND expires_at IS NOT NULL AND expires_at<=? LIMIT 100""", (lifecycle.now(),)).fetchall()
        for (identifier,) in identifiers:
            lifecycle.state(conn, identifier)
        return len(identifiers)


def status(identifier, owner):
    from . import policy
    if policy.aggregate(identifier, owner)["status"] == "denied":
        return {"status": "denied"}
    with policy.database() as conn:
        rows = conn.execute("SELECT kind,state,COUNT(*) FROM notification_outbox WHERE round_id=? GROUP BY kind,state", (identifier,)).fetchall()
        errors = conn.execute("SELECT DISTINCT last_error FROM notification_outbox WHERE round_id=? AND last_error IS NOT NULL", (identifier,)).fetchall()
        past_errors = conn.execute("""SELECT DISTINCT e.error_code FROM notification_events e
            JOIN notification_outbox n ON n.id=e.notification_id WHERE n.round_id=? AND e.error_code IS NOT NULL""", (identifier,)).fetchall()
    return {"notifications": [{"kind": r[0], "state": r[1], "count": r[2]} for r in rows],
            "error_codes": sorted(r[0] for r in errors), "historical_error_codes": sorted(r[0] for r in past_errors),
            "exactly_once_delivery": False}


def retry_blocked(identifier, owner, allowed):
    from . import lifecycle, policy
    with policy.database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT owner FROM rounds WHERE id=?", (identifier,)).fetchone()
        if row is None or row[0] != str(owner) or str(owner) not in {str(x) for x in allowed}:
            return {"status": "denied"}
        stamp = lifecycle.now()
        jobs = conn.execute("SELECT id FROM notification_outbox WHERE round_id=? AND state='blocked'", (identifier,)).fetchall()
        count = conn.execute("""UPDATE notification_outbox SET state='queued',next_attempt=?,
            last_error=NULL,updated_at=? WHERE round_id=? AND state='blocked'""", (stamp, stamp, identifier)).rowcount
        for (job_id,) in jobs:
            conn.execute("INSERT INTO notification_events(notification_id,outcome,occurred_at) VALUES (?,'retry_requested',?)", (job_id, stamp))
        if count:
            lifecycle.event(conn, identifier, "notification_retry_requested", str(owner))
        return {"status": "queued", "retried_notifications": count}
