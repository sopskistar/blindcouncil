"""Supporting regressions with actual Hermes SQLite storage and synthetic IDs.

No Telegram network, native gateway, real account or human action is exercised.
Run through probes/run_supporting_tests.py to select the existing managed runtime
and give every test its own disposable home, separate from the user's live setup.
"""
import concurrent.futures
from contextlib import closing
import json
import io
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

from blindcouncil import evidence, lifecycle, policy, register
from plugins.plugin_storage import plugin_data_dir

OWNER = "10001"
SECOND = "10002"
PEOPLE = [OWNER, SECOND]


class PolicyRegressionTests(unittest.TestCase):
    def setUp(self):
        parent = Path(os.environ["BLINDCOUNCIL_TEST_ROOT"]).resolve()
        self.temporary = tempfile.TemporaryDirectory(prefix="case-", dir=parent)
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        os.environ["HERMES_HOME"] = str(self.home)
        self.store = plugin_data_dir("blindcouncil") / "data.db"
        self.assertTrue(self.store.is_relative_to(parent))
        self.assertNotEqual(self.home.name, "isolated-home")

    def round(self, offset=0):
        identifier = policy.create(OWNER, PEOPLE)
        for index, person in enumerate(PEOPLE):
            policy.bind(identifier, person, person, offset + 101 + index)
        return identifier

    def vote(self, identifier, person=OWNER, choice="yes", **kwargs):
        message = 101 if person == OWNER else 102
        return policy.decide(identifier, person, person, message, choice, PEOPLE, **kwargs)

    def count(self, table, identifier):
        self.assertIn(table, {"votes", "receipts", "receipt_origins"})
        with policy.database() as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {table} WHERE round_id=?", (identifier,)).fetchone()[0]

    def test_all_policy_combinations_in_both_response_orders(self):
        for choices in [("yes", "yes"), ("yes", "no"), ("no", "yes"), ("no", "no")]:
            for order in [PEOPLE, list(reversed(PEOPLE))]:
                with self.subTest(choices=choices, order=order):
                    identifier = self.round()
                    mapping = dict(zip(PEOPLE, choices))
                    self.vote(identifier, order[0], mapping[order[0]])
                    self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})
                    self.vote(identifier, order[1], mapping[order[1]])
                    expected = "approved" if choices == ("yes", "yes") else "rejected"
                    self.assertEqual(policy.aggregate(identifier, OWNER), {"status": expected})

    def test_unauthorized_actor_cannot_use_a_valid_delivery(self):
        identifier = self.round()
        result = policy.decide(identifier, "99999", OWNER, 101, "yes", PEOPLE)
        self.assertEqual(result, {"status": "denied"})
        self.assertEqual(self.count("votes", identifier), 0)

    def test_revoked_allowlist_membership_blocks_then_can_be_restored(self):
        identifier = self.round()
        self.vote(identifier)
        denied = policy.decide(identifier, SECOND, SECOND, 102, "yes", [OWNER])
        self.assertEqual(denied, {"status": "denied"})
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})
        self.assertEqual(self.vote(identifier, SECOND), {"status": "recorded"})
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})

    def test_wrong_private_chat_is_denied_without_mutation(self):
        identifier = self.round()
        result = policy.decide(identifier, SECOND, OWNER, 101, "yes", PEOPLE)
        self.assertEqual(result, {"status": "denied"})
        self.assertEqual(self.count("votes", identifier), 0)

    def test_cross_round_message_binding_is_rejected(self):
        first = self.round()
        second = self.round(offset=1000)
        self.assertEqual(self.vote(second), {"status": "denied"})
        self.assertEqual(self.count("votes", first), 0)
        self.assertEqual(self.count("votes", second), 0)

    def test_unknown_round_cannot_store_a_vote_or_receipt(self):
        self.round()
        identifier = "nonexistent-decision"
        result = self.vote(identifier, callback_id="synthetic-receipt", update_id=1)
        self.assertEqual(result, {"status": "denied"})
        self.assertEqual(self.count("votes", identifier), 0)
        self.assertEqual(self.count("receipts", identifier), 0)

    def test_invalid_choice_is_rejected(self):
        identifier = self.round()
        self.assertEqual(self.vote(identifier, choice="approve-as-model"), {"status": "denied"})
        self.assertEqual(self.count("votes", identifier), 0)

    def test_duplicate_cannot_replace_the_first_answer_or_receipt(self):
        identifier = self.round()
        self.vote(identifier, callback_id="synthetic-first", update_id=1, origin="synthetic-sdk")
        result = self.vote(identifier, choice="no", callback_id="synthetic-retry", update_id=2)
        self.assertEqual(result, {"status": "duplicate"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT choice FROM votes WHERE round_id=?", (identifier,)).fetchall(), [("yes",)])
            self.assertEqual(conn.execute("SELECT callback_id FROM receipts WHERE round_id=?", (identifier,)).fetchall(), [("synthetic-first",)])
        self.assertEqual(self.count("receipt_origins", identifier), 1)

    def test_concurrent_conflicting_retries_commit_only_the_winner(self):
        identifier = self.round()
        barrier = threading.Barrier(8)
        def submit(index):
            choice = "yes" if index % 2 == 0 else "no"
            barrier.wait(timeout=10)
            return choice, self.vote(identifier, choice=choice)["status"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(submit, range(8)))
        winners = [choice for choice, status in results if status == "recorded"]
        self.assertEqual(len(winners), 1)
        self.assertEqual(sum(status == "duplicate" for _, status in results), 7)
        with policy.database() as conn:
            stored = conn.execute("SELECT choice FROM votes WHERE round_id=?", (identifier,)).fetchone()[0]
        self.assertEqual(stored, winners[0])

    def test_concurrent_distinct_participants_and_retries_resolve_once(self):
        identifier = self.round()
        barrier = threading.Barrier(8)
        def submit(index):
            person = PEOPLE[index % 2]
            barrier.wait(timeout=10)
            return self.vote(identifier, person, "yes")["status"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(submit, range(8)))
        self.assertEqual(results.count("recorded"), 2)
        self.assertEqual(results.count("duplicate"), 6)
        self.assertEqual(self.count("votes", identifier), 2)
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})

    def test_receipt_storage_failure_rolls_back_the_vote_and_recovers(self):
        identifier = self.round()
        with policy.database() as conn:
            conn.execute("""CREATE TRIGGER force_receipt_failure BEFORE INSERT ON receipts
                BEGIN SELECT RAISE(ABORT, 'supporting test: forced receipt failure'); END""")
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                self.vote(identifier, callback_id="synthetic-failure", update_id=1)
            for table in ["votes", "receipts", "receipt_origins"]:
                self.assertEqual(self.count(table, identifier), 0)
            self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})
        finally:
            with policy.database() as conn:
                conn.execute("DROP TRIGGER force_receipt_failure")
        self.assertEqual(self.vote(identifier, callback_id="synthetic-recovery", update_id=2), {"status": "recorded"})

    def test_aggregate_output_is_restricted_to_the_owner_and_contains_no_answers(self):
        identifier = self.round()
        self.vote(identifier)
        self.vote(identifier, SECOND)
        for viewer in [SECOND, "99999", ""]:
            self.assertEqual(policy.aggregate(identifier, viewer), {"status": "denied"})
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})

    def test_synthetic_receipts_cannot_pass_the_native_callback_audit(self):
        identifier = self.round()
        for index, person in enumerate(PEOPLE):
            self.vote(identifier, person, callback_id=f"synthetic-{index}", update_id=index,
                      origin="synthetic-sdk", native_pid=os.getpid())
        settings = {"owner_id": OWNER, "participants": PEOPLE}
        context = SimpleNamespace(get_config=lambda key, default=None: settings.get(key, default))
        result = evidence(context, identifier)
        self.assertEqual(result["native_receipt_count"], 0)
        self.assertEqual(result["callback_identity_gate"], "BLOCKED")
        self.assertFalse(result["individual_votes_exported"])
        self.assertFalse(result["participant_ids_exported"])

    def test_legacy_rows_survive_additive_schema_and_remain_unclassified(self):
        identifier = "legacy-synthetic-round"
        with closing(sqlite3.connect(self.store)) as conn, conn:
            conn.executescript("""CREATE TABLE rounds (id TEXT PRIMARY KEY,owner TEXT,participants TEXT);
                CREATE TABLE votes(round_id TEXT,user_id TEXT,choice TEXT,PRIMARY KEY(round_id,user_id));
                CREATE TABLE receipts(round_id TEXT,user_id TEXT,callback_id TEXT,update_id INTEGER,
                PRIMARY KEY(round_id,user_id));""")
            conn.execute("INSERT INTO rounds VALUES (?,?,?)", (identifier, OWNER, json.dumps(PEOPLE)))
            for index, person in enumerate(PEOPLE):
                conn.execute("INSERT INTO votes VALUES (?,?,?)", (identifier, person, "yes"))
                conn.execute("INSERT INTO receipts VALUES (?,?,?,?)", (identifier, person, f"legacy-{index}", index))
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})
        settings = {"owner_id": OWNER, "participants": PEOPLE}
        result = evidence(SimpleNamespace(get_config=lambda key, default=None: settings.get(key, default)), identifier)
        self.assertEqual(result["receipt_count"], 2)
        self.assertEqual(result["synthetic_or_unclassified_receipts"], 2)
        self.assertEqual(result["callback_identity_gate"], "BLOCKED")

    def test_pending_and_resolved_state_recover_in_fresh_python_processes(self):
        identifier = self.round()
        self.vote(identifier)
        code = ("import json,sys; from blindcouncil.policy import aggregate; "
                "print(json.dumps(aggregate(sys.argv[1],sys.argv[2])))")
        def recover():
            result = subprocess.run([sys.executable, "-c", code, identifier, OWNER],
                                    capture_output=True, text=True, check=True, timeout=30)
            return json.loads(result.stdout)
        self.assertEqual(recover(), {"status": "pending"})
        self.vote(identifier, SECOND)
        self.assertEqual(recover(), {"status": "approved"})

    def test_cancellation_preserves_vote_receipt_and_rejects_later_response(self):
        identifier = self.round()
        self.vote(identifier, SECOND, callback_id="accepted-before-cancel", update_id=1)
        with policy.database() as conn:
            before = conn.execute("SELECT * FROM receipts WHERE round_id=?", (identifier,)).fetchall()
        self.assertEqual(policy.cancel(identifier, OWNER, PEOPLE), {"status": "cancelled"})
        self.assertEqual(self.vote(identifier, callback_id="after-cancel", update_id=2), {"status": "cancelled"})
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "cancelled"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT * FROM receipts WHERE round_id=?", (identifier,)).fetchall(), before)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (identifier,)).fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT outcome FROM callback_attempts WHERE callback_id='after-cancel'").fetchone()[0], "cancelled")

    def test_cancellation_requires_currently_allowlisted_owner(self):
        identifier = self.round()
        for actor, permitted in [(SECOND, PEOPLE), ("99999", PEOPLE), (OWNER, [SECOND])]:
            self.assertEqual(policy.cancel(identifier, actor, permitted), {"status": "denied"})
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})

    def test_cancellation_is_idempotent_and_cannot_replace_approved_or_rejected(self):
        cancelled = self.round()
        for _ in range(2):
            self.assertEqual(policy.cancel(cancelled, OWNER, PEOPLE), {"status": "cancelled"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM decision_events WHERE round_id=? AND event_type='cancelled'", (cancelled,)).fetchone()[0], 1)
        for second_choice, expected in [("yes", "approved"), ("no", "rejected")]:
            identifier = self.round()
            self.vote(identifier)
            self.vote(identifier, SECOND, second_choice)
            self.assertEqual(policy.cancel(identifier, OWNER, PEOPLE), {"status": expected})

    def test_expiry_enforced_at_boundary_without_new_vote_and_event_repeats(self):
        with patch.object(lifecycle, "now", return_value=1000):
            identifier = policy.create(OWNER, PEOPLE, expires_in=10)
            policy.bind(identifier, OWNER, OWNER, 101)
            self.vote(identifier, callback_id="before-expiry", update_id=1)
        policy.bind(identifier, SECOND, SECOND, 102)
        with patch.object(lifecycle, "now", return_value=1010):
            self.assertEqual(self.vote(identifier, SECOND, callback_id="at-expiry", update_id=2), {"status": "expired"})
            self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "expired"})
            self.assertEqual(policy.cancel(identifier, OWNER, PEOPLE), {"status": "expired"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM decision_events WHERE round_id=? AND event_type='expired'", (identifier,)).fetchone()[0], 1)
        self.assertEqual(self.count("votes", identifier), 1)
        self.assertEqual(self.count("receipts", identifier), 1)

    def test_terminal_approval_stays_approved_after_original_deadline(self):
        with patch.object(lifecycle, "now", return_value=1000):
            identifier = self.round()
            self.vote(identifier)
            self.vote(identifier, SECOND)
        with patch.object(lifecycle, "now", return_value=1000000):
            self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})

    def test_invalid_decision_inputs_do_not_create_rounds(self):
        for settings in [{"title": ""}, {"title": "x" * 201}, {"description": "x" * 4001},
                         {"expires_in": 0}, {"expires_in": -1}, {"expires_in": float("nan")},
                         {"expires_in": float("inf")}, {"expires_in": float("-inf")}, {"expires_in": True},
                         {"expires_in": 604801}]:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                policy.create(OWNER, PEOPLE, **settings)
        for participants in [[OWNER, OWNER], [OWNER, "-2"], [OWNER, "2.0"], [OWNER]]:
            with self.assertRaises(ValueError):
                policy.create(OWNER, participants)
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM rounds").fetchone()[0], 0)

    def test_practical_expiry_durations_preserve_exact_timestamp_in_fresh_process(self):
        created = 2000000000.123456
        identifiers = []
        expected = []
        for duration in [900, 3600, 86400, 259200, 604800]:
            with patch.object(lifecycle, "now", return_value=created):
                identifier = policy.create(OWNER, PEOPLE, expires_in=duration)
            identifiers.append(identifier)
            expected.append([created, created + duration])
            with policy.database() as conn:
                stored = conn.execute("SELECT created_at,expires_at FROM round_lifecycle WHERE round_id=?", (identifier,)).fetchone()
                self.assertEqual(stored, (created, created + duration))
        code = """import json,sys
from blindcouncil.policy import database
with database() as conn:
    result=[list(conn.execute('SELECT created_at,expires_at FROM round_lifecycle WHERE round_id=?',(identifier,)).fetchone()) for identifier in json.loads(sys.argv[1])]
print(json.dumps(result))
"""
        recovered = subprocess.run([sys.executable, "-c", code, json.dumps(identifiers)], capture_output=True, text=True, check=True, timeout=30)
        self.assertEqual(json.loads(recovered.stdout), expected)

    def test_normal_default_is_24_hours_and_short_expiry_is_explicit(self):
        created = 2000000000.123456
        with patch.object(lifecycle, "now", return_value=created):
            normal = policy.create(OWNER, PEOPLE)
            short_test = policy.create(OWNER, PEOPLE, expires_in=30)
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT expires_at FROM round_lifecycle WHERE round_id=?", (normal,)).fetchone()[0], created + 86400)
            self.assertEqual(conn.execute("SELECT expires_at FROM round_lifecycle WHERE round_id=?", (short_test,)).fetchone()[0], created + 30)

    def test_callback_audit_records_denial_and_transport_retries_idempotently(self):
        identifier = self.round()
        for _ in range(2):
            self.vote(identifier, callback_id="same-telegram-update", update_id=1, origin="synthetic-sdk")
        policy.decide(identifier, SECOND, SECOND, 999, "yes", PEOPLE,
                      callback_id="wrong-message", update_id=2, origin="synthetic-sdk")
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM callback_attempts WHERE round_id=?", (identifier,)).fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT outcome,reason FROM callback_attempts WHERE callback_id='wrong-message'").fetchone(), ("denied", "message_binding_or_choice"))
        self.assertEqual(self.count("votes", identifier), 1)

    def test_concurrent_cancel_and_second_response_choose_a_valid_terminal_state(self):
        identifier = self.round()
        self.vote(identifier)
        barrier = threading.Barrier(2)
        def submit():
            barrier.wait(timeout=10)
            return self.vote(identifier, SECOND)["status"]
        def cancel():
            barrier.wait(timeout=10)
            return policy.cancel(identifier, OWNER, PEOPLE)["status"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            vote_future = pool.submit(submit)
            cancel_future = pool.submit(cancel)
            vote_result, cancel_result = vote_future.result(), cancel_future.result()
        state = policy.aggregate(identifier, OWNER)["status"]
        self.assertIn((state, vote_result, cancel_result), [("approved", "recorded", "approved"), ("cancelled", "cancelled", "cancelled")])
        self.assertEqual(self.count("votes", identifier), 2 if state == "approved" else 1)

    def test_future_schema_is_rejected_without_database_mutation(self):
        identifier = self.round()
        with closing(sqlite3.connect(self.store)) as conn, conn:
            conn.execute("PRAGMA user_version=99")
            before = list(conn.iterdump())
        with self.assertRaisesRegex(RuntimeError, "newer schema"):
            policy.cancel(identifier, OWNER, PEOPLE)
        with closing(sqlite3.connect(self.store)) as conn:
            self.assertEqual(list(conn.iterdump()), before)

    def test_native_sdk_routing_supporting_probe(self):
        from blindcouncil import wire
        from blindcouncil.sdk_probe import probe
        context = SimpleNamespace()
        with patch("blindcouncil.allowed_users", return_value=set(PEOPLE)):
            result = probe(context, wire)
        self.assertEqual(result["real_telegram_api_calls"], 0)
        self.assertEqual(result["passed"], 11)

    def test_revoked_participant_cannot_add_a_response_on_bound_invitation(self):
        identifier = self.round()
        for _ in range(2):
            self.assertEqual(policy.revoke(identifier, OWNER, SECOND, PEOPLE), {"status": "revoked"})
        result = self.vote(identifier, SECOND, callback_id="revoked-response", update_id=1, origin="synthetic-sdk")
        self.assertEqual(result, {"status": "denied"})
        self.assertEqual(self.count("votes", identifier), 0)
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT reason FROM callback_attempts WHERE callback_id='revoked-response'").fetchone()[0], "participant_revoked")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM decision_events WHERE round_id=? AND event_type='participant_revoked'", (identifier,)).fetchone()[0], 1)
        self.vote(identifier)
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "pending"})

    def test_revocation_requires_allowlisted_owner_and_current_participant(self):
        identifier = self.round()
        for actor, participant, permitted in [(SECOND, OWNER, PEOPLE), (OWNER, "99999", PEOPLE),
                                              (OWNER, SECOND, [SECOND]), (OWNER, OWNER, PEOPLE)]:
            self.assertEqual(policy.revoke(identifier, actor, participant, permitted), {"status": "denied"})
        self.assertEqual(self.vote(identifier, SECOND), {"status": "recorded"})

    def test_revocation_does_not_rewrite_past_responses_or_terminal_outcomes(self):
        identifier = self.round()
        self.vote(identifier, SECOND, callback_id="accepted-before-revocation", update_id=1)
        with policy.database() as conn:
            before = conn.execute("SELECT * FROM receipts WHERE round_id=?", (identifier,)).fetchall()
        self.assertEqual(policy.revoke(identifier, OWNER, SECOND, PEOPLE), {"status": "revoked"})
        self.vote(identifier)
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "approved"})
        self.assertEqual(policy.revoke(identifier, OWNER, SECOND, PEOPLE), {"status": "approved"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("SELECT * FROM receipts WHERE round_id=?", (identifier,)).fetchall(), before)

    def test_schema_v1_upgrade_preserves_cancelled_state_and_original_receipt(self):
        identifier = self.round()
        self.vote(identifier, SECOND, callback_id="v1-receipt", update_id=1)
        policy.cancel(identifier, OWNER, PEOPLE)
        with policy.database() as conn:
            conn.execute("DROP TABLE participant_revocations")
            conn.execute("PRAGMA user_version=1")
        self.assertEqual(policy.aggregate(identifier, OWNER), {"status": "cancelled"})
        with policy.database() as conn:
            self.assertEqual(conn.execute("PRAGMA user_version").fetchone()[0], lifecycle.SCHEMA_VERSION)
            self.assertEqual(conn.execute("SELECT callback_id FROM receipts WHERE round_id=?", (identifier,)).fetchone()[0], "v1-receipt")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (identifier,)).fetchone()[0], 1)

    def test_incompatible_runtime_gets_clear_error_before_partial_registration(self):
        context = SimpleNamespace(register_platform_handler=lambda *args: self.fail("partial registration"))
        with self.assertRaisesRegex(RuntimeError, "supervised plugin tasks"):
            register(context)

    def cli_handler(self):
        handlers = []
        context = SimpleNamespace(register_platform_handler=lambda *args: None,
                                  spawn_task=lambda *args, **kwargs: None,
                                  register_cli_command=lambda *args, **kwargs: handlers.append(kwargs["handler_fn"]))
        register(context)
        return handlers[0]

    def test_developer_cli_probes_cannot_pollute_a_normal_or_secret_bearing_home(self):
        handler = self.cli_handler()
        for action in ["probe", "sdk-probe"]:
            with patch.dict(os.environ):
                os.environ.pop("BLINDCOUNCIL_TEST_ROOT", None)
                with self.assertRaisesRegex(SystemExit, "No probe data"):
                    handler(SimpleNamespace(action=action))
        (self.home / ".env").touch()
        with self.assertRaisesRegex(SystemExit, "No probe data"):
            handler(SimpleNamespace(action="probe"))
        self.assertFalse(self.store.exists())

    def test_explicit_isolated_developer_probe_remains_available(self):
        handler = self.cli_handler()
        output = io.StringIO()
        with patch("sys.stdout", output):
            handler(SimpleNamespace(action="probe"))
        result = json.loads(output.getvalue())
        self.assertEqual(result["passed"], 10)
        self.assertEqual(result["telegram_api_calls_made"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
