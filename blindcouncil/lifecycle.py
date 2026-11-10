"""Versioned, additive lifecycle storage. No transport or model decisions live here."""
import json
import time
from . import outbox

SCHEMA_VERSION = 3

TABLES = (
    "CREATE TABLE IF NOT EXISTS rounds (id TEXT PRIMARY KEY, owner TEXT NOT NULL, participants TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS deliveries (round_id TEXT NOT NULL,user_id TEXT NOT NULL,chat_id TEXT NOT NULL,message_id INTEGER NOT NULL,PRIMARY KEY(round_id,user_id))",
    "CREATE TABLE IF NOT EXISTS votes (round_id TEXT NOT NULL,user_id TEXT NOT NULL,choice TEXT NOT NULL,PRIMARY KEY(round_id,user_id))",
    "CREATE TABLE IF NOT EXISTS receipts (round_id TEXT NOT NULL,user_id TEXT NOT NULL,callback_id TEXT NOT NULL,update_id INTEGER,PRIMARY KEY(round_id,user_id))",
    "CREATE TABLE IF NOT EXISTS receipt_origins (round_id TEXT NOT NULL,user_id TEXT NOT NULL,origin TEXT NOT NULL,native_pid INTEGER,PRIMARY KEY(round_id,user_id))",
    """CREATE TABLE IF NOT EXISTS round_lifecycle (
        round_id TEXT PRIMARY KEY REFERENCES rounds(id), title TEXT NOT NULL, description TEXT NOT NULL,
        policy_name TEXT NOT NULL, policy_version INTEGER NOT NULL,
        state TEXT NOT NULL CHECK(state IN ('pending','approved','rejected','expired','cancelled')),
        created_at REAL, expires_at REAL, legacy_imported INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE IF NOT EXISTS decision_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,round_id TEXT NOT NULL,event_type TEXT NOT NULL,
        occurred_at REAL NOT NULL,actor_id TEXT)""",
    """CREATE TABLE IF NOT EXISTS callback_attempts (
        callback_id TEXT PRIMARY KEY,round_id TEXT NOT NULL,outcome TEXT NOT NULL,reason TEXT NOT NULL,
        origin TEXT NOT NULL,update_id INTEGER,received_at REAL NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS participant_revocations (
        round_id TEXT NOT NULL,user_id TEXT NOT NULL,revoked_at REAL NOT NULL,
        PRIMARY KEY(round_id,user_id))""",
) + outbox.TABLES


def now():
    return time.time()


def initialize(conn):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        raise RuntimeError("BlindCouncil database belongs to a newer schema; no changes made")
    if version == SCHEMA_VERSION:
        return
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise RuntimeError("BlindCouncil database belongs to a newer schema; no changes made")
        for statement in TABLES:
            conn.execute(statement)
        for (identifier,) in conn.execute("SELECT id FROM rounds").fetchall():
            choices = [row[0] for row in conn.execute("SELECT choice FROM votes WHERE round_id=?", (identifier,))]
            state = "pending" if len(choices) != 2 else ("approved" if all(x == "yes" for x in choices) else "rejected")
            # Unknown historical creation times remain NULL; migration never invents timestamps or replays votes.
            conn.execute("""INSERT OR IGNORE INTO round_lifecycle VALUES
                (?, 'Legacy decision', '', 'two_person_unanimous', 1, ?, NULL, NULL, 1)""", (identifier, state))
        conn.execute(f"PRAGMA user_version={SCHEMA_VERSION}")


def event(conn, identifier, kind, actor=None):
    conn.execute("INSERT INTO decision_events(round_id,event_type,occurred_at,actor_id) VALUES (?,?,?,?)",
                 (identifier, kind, now(), actor))


def state(conn, identifier):
    row = conn.execute("SELECT state,expires_at FROM round_lifecycle WHERE round_id=?", (identifier,)).fetchone()
    if row is None:
        raise RuntimeError("Decision lifecycle metadata is missing")
    value, deadline = row
    if value == "pending" and deadline is not None and now() >= deadline:
        changed = conn.execute("UPDATE round_lifecycle SET state='expired' WHERE round_id=? AND state='pending'",
                               (identifier,)).rowcount
        if changed:
            event(conn, identifier, "expired")
            outbox.enqueue_result(conn, identifier, now())
        return "expired"
    return value


def attempt(conn, identifier, outcome, *, callback_id=None, update_id=None, origin="unclassified", reason=""):
    if callback_id is None:
        return {"status": outcome}
    conn.execute("INSERT OR IGNORE INTO callback_attempts VALUES (?,?,?,?,?,?,?)",
                 (str(callback_id), identifier, outcome, reason, origin, update_id, now()))
    return {"status": outcome}


def transition(conn, identifier, value, actor=None):
    changed = conn.execute("UPDATE round_lifecycle SET state=? WHERE round_id=? AND state='pending'",
                           (value, identifier)).rowcount
    if changed:
        event(conn, identifier, value, actor)
        if value in {"approved", "rejected", "cancelled", "expired"}:
            outbox.enqueue_result(conn, identifier, now())
    return changed
