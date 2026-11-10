"""Deterministic two-person policy. IDs come from Telegram transport, never callback data."""
import json
from contextlib import contextmanager
import secrets
import math
import datetime

from plugins.plugin_storage import plugin_db, plugin_data_dir
from . import expiry, lifecycle, outbox


@contextmanager
def database():
    folder = plugin_data_dir("blindcouncil")
    folder.chmod(0o700)
    conn = plugin_db("blindcouncil")
    try:
        (folder / "data.db").chmod(0o600)
        lifecycle.initialize(conn)
        with conn:
            yield conn
    finally:
        conn.close()


def create(owner, participants, *, title="Two-person decision", description="", expires_in=expiry.DEFAULT):
    people = [str(x) for x in participants]
    owner = str(owner)
    if (len(people) != 2 or len(set(people)) != 2
            or any(not x.isascii() or not x.isdigit() or int(x) <= 0 for x in people) or owner not in people):
        raise ValueError("Need two distinct numeric participant IDs, with owner among them")
    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        raise ValueError("Decision title must contain 1 to 200 characters")
    if not isinstance(description, str) or len(description) > 4000:
        raise ValueError("Decision description must contain at most 4000 characters")
    if len((title.strip() + description).encode("utf-16-le")) // 2 > 3600:
        raise ValueError("Combined title and description exceed the 3600-character Telegram budget")
    if (isinstance(expires_in, bool) or not isinstance(expires_in, (int, float))
            or not math.isfinite(expires_in) or not 0 < expires_in <= expiry.MAXIMUM):
        raise ValueError("Expiry must be between zero and seven days")
    round_id = secrets.token_hex(6)
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO rounds VALUES (?,?,?)", (round_id, owner, json.dumps(people)))
        stamp = lifecycle.now()
        conn.execute("INSERT INTO round_lifecycle VALUES (?,?,?,'two_person_unanimous',1,'pending',?,?,0)",
                     (round_id, title.strip(), description, stamp, stamp + expires_in))
        lifecycle.event(conn, round_id, "created", owner)
        outbox.enqueue_invites(conn, round_id, people, stamp)
    return round_id


def bind(round_id, user, chat, message):
    with database() as conn:
        conn.execute("INSERT INTO deliveries VALUES (?,?,?,?)", (round_id, str(user), str(chat), int(message)))


def decide(round_id, user, chat, message, choice, allowed_users, *, callback_id=None, update_id=None,
           origin="unclassified", native_pid=None):
    user = str(user)
    audit = dict(callback_id=callback_id, update_id=update_id, origin=origin)
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        if user not in {str(x) for x in allowed_users}:
            return lifecycle.attempt(conn, round_id, "denied", reason="not_allowlisted", **audit)
        row = conn.execute("SELECT participants FROM rounds WHERE id=?", (round_id,)).fetchone()
        if row is None or user not in json.loads(row[0]):
            return lifecycle.attempt(conn, round_id, "denied", reason="unknown_round_or_nonparticipant", **audit)
        if conn.execute("SELECT 1 FROM participant_revocations WHERE round_id=? AND user_id=?", (round_id, user)).fetchone():
            return lifecycle.attempt(conn, round_id, "denied", reason="participant_revoked", **audit)
        delivery = conn.execute("SELECT chat_id,message_id FROM deliveries WHERE round_id=? AND user_id=?",
                                (round_id, user)).fetchone()
        if delivery != (str(chat), int(message)) or str(chat) != user or choice not in {"yes", "no"}:
            return lifecycle.attempt(conn, round_id, "denied", reason="message_binding_or_choice", **audit)
        current = lifecycle.state(conn, round_id)
        if current in {"cancelled", "expired"}:
            return lifecycle.attempt(conn, round_id, current, **audit)
        if conn.execute("SELECT 1 FROM votes WHERE round_id=? AND user_id=?", (round_id, user)).fetchone():
            return lifecycle.attempt(conn, round_id, "duplicate", **audit)
        if current != "pending":
            return lifecycle.attempt(conn, round_id, current, **audit)
        conn.execute("INSERT INTO votes VALUES (?,?,?)", (round_id, user, choice))
        if callback_id is not None:
            conn.execute("INSERT INTO receipts VALUES (?,?,?,?)", (round_id, user, str(callback_id), update_id))
            conn.execute("INSERT INTO receipt_origins VALUES (?,?,?,?)", (round_id, user, origin, native_pid))
        choices = [row[0] for row in conn.execute("SELECT choice FROM votes WHERE round_id=?", (round_id,))]
        if len(choices) == 2:
            lifecycle.transition(conn, round_id, "approved" if all(x == "yes" for x in choices) else "rejected")
        return lifecycle.attempt(conn, round_id, "recorded", **audit)


def cancel(round_id, actor, allowed_users):
    actor = str(actor)
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT owner FROM rounds WHERE id=?", (round_id,)).fetchone()
        if row is None or row[0] != actor or actor not in {str(x) for x in allowed_users}:
            return {"status": "denied"}
        current = lifecycle.state(conn, round_id)
        if current == "pending":
            lifecycle.transition(conn, round_id, "cancelled", actor)
            return {"status": "cancelled"}
        return {"status": current}


def revoke(round_id, actor, participant, allowed_users):
    """Owner-only invitation revocation; immutable accepted responses are never rewritten."""
    actor, participant = str(actor), str(participant)
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT owner,participants FROM rounds WHERE id=?", (round_id,)).fetchone()
        if (row is None or row[0] != actor or actor not in {str(x) for x in allowed_users}
                or participant not in json.loads(row[1]) or participant == actor):
            return {"status": "denied"}
        current = lifecycle.state(conn, round_id)
        if current != "pending":
            return {"status": current}
        changed = conn.execute("INSERT OR IGNORE INTO participant_revocations VALUES (?,?,?)",
                               (round_id, participant, lifecycle.now())).rowcount
        if changed:
            lifecycle.event(conn, round_id, "participant_revoked", actor)
        return {"status": "revoked"}


def aggregate(round_id, viewer):
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT owner FROM rounds WHERE id=?", (round_id,)).fetchone()
        if row is None or row[0] != str(viewer):
            return {"status": "denied"}
        return {"status": lifecycle.state(conn, round_id)}


def details(round_id, viewer):
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("""SELECT r.owner,r.participants,l.title,l.description,l.policy_name,
            l.policy_version,l.created_at,l.expires_at FROM rounds r
            JOIN round_lifecycle l ON l.round_id=r.id WHERE r.id=?""", (round_id,)).fetchone()
        if row is None or row[0] != str(viewer):
            return {"status": "denied"}
        state = lifecycle.state(conn, round_id)
        def stamp(value):
            return datetime.datetime.fromtimestamp(value, datetime.timezone.utc).isoformat() if value is not None else None
        return {"round_id": round_id, "status": state, "title": row[2], "description": row[3],
                "policy": row[4], "policy_version": row[5], "participant_count": len(json.loads(row[1])),
                "responded_count": conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (round_id,)).fetchone()[0],
                "bound_invitation_count": conn.execute("SELECT COUNT(*) FROM deliveries WHERE round_id=?", (round_id,)).fetchone()[0],
                "revoked_invitation_count": conn.execute("SELECT COUNT(*) FROM participant_revocations WHERE round_id=?", (round_id,)).fetchone()[0],
                "created_utc": stamp(row[6]), "expires_utc": stamp(row[7]), "individual_answers_included": False}


def history(viewer, limit=20):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("History limit must be between 1 and 100")
    with database() as conn:
        identifiers = [row[0] for row in conn.execute("SELECT id FROM rounds WHERE owner=? ORDER BY rowid DESC LIMIT ?", (str(viewer), limit))]
    decisions = []
    for identifier in identifiers:
        value = details(identifier, viewer)
        if value["status"] != "denied":
            decisions.append({key: value[key] for key in ["round_id", "status", "title", "responded_count", "participant_count", "expires_utc"]})
    return {"decisions": decisions, "individual_answers_included": False}
