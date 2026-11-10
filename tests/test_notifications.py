"""Supporting queue/recovery regressions: real Hermes SQLite, synthetic IDs and transport only."""
import asyncio
import concurrent.futures
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from telegram.error import BadRequest, Forbidden, NetworkError, RetryAfter
from blindcouncil import expiry, lifecycle, outbox, policy
from blindcouncil.notification_worker import process_one

OWNER, SECOND = "10001", "10002"
PEOPLE = {OWNER, SECOND}


class SyntheticBot:
    def __init__(self):
        self.sent, self.edited = [], []
        self.fail_send, self.fail_edit = [], []
        self.uncertain_send_once = False

    async def send_message(self, chat_id, text, **kwargs):
        if self.fail_send:
            raise self.fail_send.pop(0)
        message = SimpleNamespace(chat_id=int(chat_id), message_id=1000 + len(self.sent))
        self.sent.append((message, text))
        if self.uncertain_send_once:
            self.uncertain_send_once = False
            raise NetworkError("synthetic lost acknowledgement after remote delivery")
        return message

    async def edit_message_reply_markup(self, chat_id, message_id, reply_markup):
        with policy.database() as conn:
            binding = conn.execute("SELECT 1 FROM deliveries WHERE chat_id=? AND message_id=?", (str(chat_id), message_id)).fetchone()
        assert binding, "Actionable keyboard appeared before a durable delivery binding"
        self.edited.append((chat_id, message_id))
        if self.fail_edit:
            raise self.fail_edit.pop(0)
        return True


class NotificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="notifications-", dir=os.environ["BLINDCOUNCIL_TEST_ROOT"])
        self.addCleanup(self.temp.cleanup)
        os.environ["HERMES_HOME"] = self.temp.name

    def create(self, **kwargs):
        return policy.create(OWNER, [OWNER, SECOND], **kwargs)

    def query(self, statement, args=()):
        with policy.database() as conn:
            return conn.execute(statement, args).fetchall()

    def process(self, bot, allowed=PEOPLE):
        return asyncio.run(process_one(bot, allowed))

    def drain(self, bot, allowed=PEOPLE):
        for _ in range(30):
            if not self.process(bot, allowed):
                return
        self.fail("Synthetic queue did not reach idle")

    def resolve(self, identifier, second="yes"):
        for index, person in enumerate([OWNER, SECOND]):
            policy.bind(identifier, person, person, 101 + index)
            policy.decide(identifier, person, person, 101 + index, "yes" if index == 0 else second, PEOPLE,
                          callback_id=f"fixture-{identifier}-{index}", update_id=index, origin="synthetic-sdk")

    def test_creation_and_invitation_enqueue_are_atomic(self):
        with policy.database() as conn:
            conn.execute("""CREATE TRIGGER fail_second_invite BEFORE INSERT ON notification_outbox
                WHEN NEW.user_id='10002' BEGIN SELECT RAISE(ABORT,'synthetic enqueue failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.create()
        for table in ["rounds", "round_lifecycle", "decision_events", "notification_outbox"]:
            self.assertEqual(self.query(f"SELECT COUNT(*) FROM {table}")[0][0], 0)

    def test_resolution_enqueues_one_aggregate_per_participant_and_duplicate_adds_none(self):
        identifier = self.create()
        self.resolve(identifier)
        self.assertEqual(policy.decide(identifier, SECOND, SECOND, 102, "no", PEOPLE), {"status": "duplicate"})
        self.assertEqual(self.query("SELECT kind,state,COUNT(*) FROM notification_outbox GROUP BY kind,state"), [("invite", "obsolete", 2), ("result", "queued", 2)])
        bot = SyntheticBot()
        self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertEqual({str(message.chat_id) for message, _ in bot.sent}, PEOPLE)
        self.assertTrue(all("APPROVED" in text and "yes" not in text for _, text in bot.sent))
        self.assertEqual(len(bot.edited), 0)

    def test_failed_result_enqueue_rolls_back_second_vote_receipt_and_resolution(self):
        identifier = self.create()
        for index, person in enumerate([OWNER, SECOND]):
            policy.bind(identifier, person, person, 101 + index)
        policy.decide(identifier, OWNER, OWNER, 101, "yes", PEOPLE, callback_id="first", update_id=1)
        with policy.database() as conn:
            conn.execute("""CREATE TRIGGER fail_result BEFORE INSERT ON notification_outbox
                WHEN NEW.kind='result' BEGIN SELECT RAISE(ABORT,'synthetic result failure'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            policy.decide(identifier, SECOND, SECOND, 102, "yes", PEOPLE, callback_id="second", update_id=2)
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})
        self.assertEqual(self.query("SELECT COUNT(*) FROM votes")[0][0], 1)
        self.assertEqual(self.query("SELECT COUNT(*) FROM receipts")[0][0], 1)
        self.assertEqual(self.query("SELECT kind,state,COUNT(*) FROM notification_outbox GROUP BY kind,state"), [("invite", "queued", 2)])

    def test_concurrent_workers_cannot_claim_same_current_lease(self):
        self.create()
        barrier = threading.Barrier(8)
        def claim(_):
            barrier.wait(timeout=10)
            return outbox.claim()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            claimed = [job for job in pool.map(claim, range(8)) if job]
        self.assertEqual(len(claimed), 2)
        self.assertEqual(len({job["id"] for job in claimed}), 2)

    def test_expired_lease_recovers_and_old_worker_cannot_overwrite_new_lease(self):
        with patch.object(lifecycle, "now", return_value=1000):
            self.create()
            old = outbox.claim()
            outbox.claim()
        with patch.object(lifecycle, "now", return_value=1059):
            self.assertIsNone(outbox.claim())
        with patch.object(lifecycle, "now", return_value=1061):
            recovered = outbox.claim()
            self.assertEqual(recovered["id"], old["id"])
            self.assertNotEqual(recovered["lease_token"], old["lease_token"])
            self.assertFalse(outbox.finish(old, "sent"))
            self.assertTrue(outbox.finish(recovered, "sent"))

    def test_network_failure_keeps_invitation_durable_and_retry_sends_it(self):
        bot = SyntheticBot()
        bot.fail_send = [NetworkError("synthetic offline")]
        with patch.object(lifecycle, "now", return_value=1000):
            self.create()
            self.process(bot)
            self.assertEqual(self.query("SELECT state,last_error FROM notification_outbox ORDER BY id LIMIT 1")[0], ("queued", "NetworkError"))
            self.drain(bot)
        with patch.object(lifecycle, "now", return_value=1010):
            self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertEqual(len(bot.edited), 2)
        self.assertEqual(self.query("SELECT COUNT(*) FROM deliveries")[0][0], 2)

    def test_keyboard_retry_reuses_bound_message_instead_of_resending(self):
        bot = SyntheticBot()
        bot.fail_edit = [NetworkError("synthetic attachment failure")]
        with patch.object(lifecycle, "now", return_value=1000):
            self.create()
            self.process(bot)
            self.assertEqual(self.query("SELECT COUNT(*) FROM deliveries")[0][0], 1)
            self.drain(bot)
        with patch.object(lifecycle, "now", return_value=1010):
            self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertEqual(len(bot.edited), 3)

    def test_cancellation_suppresses_unsent_invitations_and_sends_aggregate_only(self):
        identifier = self.create()
        policy.cancel(identifier, OWNER, PEOPLE)
        bot = SyntheticBot()
        self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertTrue(all("CANCELLED" in text for _, text in bot.sent))
        self.assertEqual(bot.edited, [])

    def test_expiry_sweep_is_idempotent_and_does_not_attach_late_buttons(self):
        with patch.object(lifecycle, "now", return_value=1000):
            identifier = self.create(expires_in=30)
        with patch.object(lifecycle, "now", return_value=1030):
            self.assertEqual(outbox.expire_due(), 1)
            self.assertEqual(outbox.expire_due(), 0)
            bot = SyntheticBot()
            self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertTrue(all("EXPIRED" in text for _, text in bot.sent))
        self.assertEqual(bot.edited, [])
        self.assertEqual(self.query("SELECT COUNT(*) FROM votes")[0][0], 0)

    def test_revoked_recipient_is_not_contacted_and_status_leaks_no_ids(self):
        identifier = self.create()
        policy.revoke(identifier, OWNER, SECOND, PEOPLE)
        bot = SyntheticBot()
        self.drain(bot)
        self.assertEqual(len(bot.sent), 1)
        self.assertEqual(str(bot.sent[0][0].chat_id), OWNER)
        result = outbox.status(identifier, OWNER)
        self.assertIn("recipient_not_authorized", result["error_codes"])
        self.assertNotIn(SECOND, json.dumps(result))
        self.assertEqual(outbox.status(identifier, SECOND), {"status": "denied"})

    def test_forbidden_recipient_can_be_retried_without_replaying_sent_jobs(self):
        identifier = self.create()
        bot = SyntheticBot()
        bot.fail_send = [Forbidden("synthetic blocked bot")]
        self.drain(bot)
        self.assertEqual(outbox.retry_blocked(identifier, SECOND, PEOPLE), {"status": "denied"})
        self.assertEqual(outbox.retry_blocked(identifier, OWNER, PEOPLE)["retried_notifications"], 1)
        self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertEqual(outbox.retry_blocked(identifier, OWNER, PEOPLE)["retried_notifications"], 0)
        self.assertEqual(self.query("SELECT attempts FROM notification_outbox ORDER BY id LIMIT 1")[0][0], 2)
        self.assertIn("Forbidden", outbox.status(identifier, OWNER)["historical_error_codes"])

    def test_repeated_keyboard_attachment_acknowledges_existing_bound_message(self):
        self.create()
        bot = SyntheticBot()
        bot.fail_edit = [BadRequest("Message is not modified")]
        self.drain(bot)
        self.assertEqual(len(bot.sent), 2)
        self.assertEqual(self.query("SELECT state,message_id FROM notification_outbox ORDER BY id LIMIT 1")[0], ("sent", 1000))

    def test_rate_limit_keeps_job_queued_until_server_delay(self):
        bot = SyntheticBot()
        bot.fail_send = [RetryAfter(30)]
        with patch.object(lifecycle, "now", return_value=1000):
            self.create()
            self.drain(bot)
        self.assertEqual(len(bot.sent), 1)
        with patch.object(lifecycle, "now", return_value=1029):
            self.assertFalse(self.process(bot))
        with patch.object(lifecycle, "now", return_value=1031):
            self.drain(bot)
        self.assertEqual(len(bot.sent), 2)

    def test_unknown_send_ack_can_duplicate_delivery_but_not_logical_job(self):
        identifier = self.create()
        self.resolve(identifier, "no")
        bot = SyntheticBot()
        bot.uncertain_send_once = True
        with patch.object(lifecycle, "now", return_value=2000000000):
            self.drain(bot)
        with patch.object(lifecycle, "now", return_value=2000000010):
            self.drain(bot)
        self.assertEqual(len(bot.sent), 3)  # Honest external uncertainty; no exactly-once claim.
        self.assertEqual(self.query("SELECT COUNT(*) FROM notification_outbox WHERE kind='result'")[0][0], 2)

    def test_queued_work_is_visible_in_a_fresh_process(self):
        self.create()
        code = "from blindcouncil.policy import database\nwith database() as c: print(c.execute(\"SELECT COUNT(*) FROM notification_outbox WHERE state='queued'\").fetchone()[0])"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True, timeout=30)
        self.assertEqual(result.stdout.strip(), "2")

    def test_v2_upgrade_never_replays_historical_terminal_messages(self):
        identifier = self.create()
        self.resolve(identifier)
        with policy.database() as conn:
            before = conn.execute("SELECT * FROM receipts ORDER BY user_id").fetchall()
            conn.execute("DROP TABLE notification_outbox")
            conn.execute("PRAGMA user_version=2")
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})
        self.assertEqual(self.query("SELECT COUNT(*) FROM notification_outbox")[0][0], 0)
        self.assertEqual(self.query("SELECT * FROM receipts ORDER BY user_id"), before)
        self.create()
        self.assertEqual(self.query("SELECT COUNT(*) FROM notification_outbox")[0][0], 2)

    def test_product_expiry_presets_and_private_details_history(self):
        self.assertEqual([expiry.product_duration(value) for value in expiry.PRESETS], [900, 3600, 86400, 259200, 604800])
        self.assertEqual(expiry.product_duration(), 86400)
        for invalid in ["30s", "8d", 30, None, [], True]:
            with self.assertRaises(ValueError):
                expiry.product_duration(invalid)
        identifier = self.create(title="Review release", description="Synthetic public fixture")
        self.assertEqual(policy.details(identifier, SECOND), {"status": "denied"})
        self.assertEqual(policy.history(SECOND)["decisions"], [])
        self.assertEqual(policy.history(OWNER)["decisions"][0]["round_id"], identifier)
        self.assertFalse(policy.details(identifier, OWNER)["individual_answers_included"])
        with self.assertRaises(ValueError):
            self.create(title="x" * 200, description="y" * 3500)
