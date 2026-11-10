"""Supporting RPC boundary tests: real SQLite, synthetic operator context, no gateway."""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from blindcouncil import operator_rpc, policy


class OperatorRpcTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ["BLINDCOUNCIL_TEST_ROOT"])
        self.addCleanup(self.temp.cleanup)
        os.environ["HERMES_HOME"] = self.temp.name
        self.people = ["10003", "10004"]
        self.allowed = set(self.people)
        self.settings = {"owner_id": self.people[0], "participants": self.people}
        methods = {}
        self.ctx = SimpleNamespace(get_config=lambda key, default=None: self.settings.get(key, default),
                                   state={}, register_rpc=lambda name, handler: methods.update({name: handler}))
        operator_rpc.register(self.ctx, lambda: self.allowed, lambda ctx: {"status": "READY_FOR_MANUAL_TEST", "issues": []})
        self.call = methods["operator"]

    def create(self, **kwargs):
        result = self.call({"action": "create", "title": "Release checklist", **kwargs})
        self.assertEqual(result["status"], "created")
        return result["decision"]["round_id"]

    def count(self, table):
        self.assertIn(table, {"rounds", "votes", "receipts"})
        with policy.database() as conn:
            return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_board_and_detail_exclude_ids_and_answers(self):
        identifier = self.create()
        policy.bind(identifier, self.people[0], self.people[0], 11)
        policy.decide(identifier, self.people[0], self.people[0], 11, "yes", self.allowed)
        for request in [{"action": "board"}, {"action": "detail", "round_id": identifier}]:
            result = self.call(request)
            text = json.dumps(result)
            for person in self.people:
                self.assertNotIn(person, text)
            self.assertNotIn('"yes"', text)
            self.assertNotIn('"choice"', text)
        self.assertEqual(self.call({"action": "board"})["decisions"][0]["responded_count"], 1)

    def test_creation_uses_configured_participants_and_exact_default(self):
        identifier = self.create(owner_id="99999", participants=["99999", "88888"])
        with policy.database() as conn:
            owner, people = conn.execute("SELECT owner,participants FROM rounds WHERE id=?", (identifier,)).fetchone()
            created, expires = conn.execute("SELECT created_at,expires_at FROM round_lifecycle WHERE round_id=?", (identifier,)).fetchone()
        self.assertEqual(owner, self.people[0])
        self.assertEqual(json.loads(people), self.people)
        self.assertEqual(expires - created, 86400)

    def test_invalid_creation_never_inserts_a_round(self):
        for change in [{"title": ""}, {"title": "x" * 201}, {"expires": "30s"}, {"expires": float("inf")}, {"description": []}]:
            result = self.call({"action": "create", "title": "Valid", **change})
            self.assertEqual(result["status"], "error")
        self.assertEqual(self.count("rounds"), 0)

    def test_current_owner_revocation_cannot_be_overridden_by_params(self):
        identifier = self.create()
        self.allowed.clear()
        result = self.call({"action": "cancel", "round_id": identifier, "owner_id": self.people[0]})
        self.assertEqual(result["status"], "denied")
        self.assertEqual(policy.aggregate(identifier, self.people[0])["status"], "pending")
        self.assertEqual(self.call({"action": "board"})["decisions"], [])

    def test_no_rpc_can_submit_a_vote(self):
        identifier = self.create()
        for action in ["vote", "decide", "approve", "reject", "bind"]:
            result = self.call({"action": action, "round_id": identifier, "user_id": self.people[1], "choice": "yes"})
            self.assertEqual(result["status"], "error")
        self.assertEqual(self.count("votes"), 0)
        self.assertEqual(self.count("receipts"), 0)

    def test_cancel_uses_policy_and_terminal_state_is_immutable(self):
        identifier = self.create()
        self.assertEqual(self.call({"action": "cancel", "round_id": identifier})["status"], "cancelled")
        self.assertEqual(self.call({"action": "cancel", "round_id": identifier})["status"], "cancelled")
        self.assertEqual(self.count("votes"), 0)

    def test_invalid_identifiers_and_unknown_operations_are_safe(self):
        for identifier in [None, 7, "../secret", "x" * 500, "ABCDEF123456"]:
            self.assertEqual(self.call({"action": "detail", "round_id": identifier})["status"], "error")
        self.assertEqual(self.call([])["status"], "error")
        self.assertEqual(self.count("votes"), 0)

    def test_storage_failure_is_safe_and_does_not_return_exception_text(self):
        with patch.object(policy, "history", side_effect=sqlite3.OperationalError("PRIVATE_PATH_RESPONSE")):
            result = self.call({"action": "board"})
        self.assertEqual(result["status"], "error")
        self.assertNotIn("PRIVATE_PATH_RESPONSE", json.dumps(result))

    def test_configuration_failure_cannot_leak_exception_data_or_create_work(self):
        self.ctx.get_config = lambda *args: (_ for _ in ()).throw(RuntimeError("PRIVATE_CONFIG_VALUE"))
        for action in ["board", "create", "detail", "cancel", "retry"]:
            result = self.call({"action": action, "title": "Valid", "round_id": "abcdef123456"})
            self.assertEqual(result["status"], "error")
            self.assertNotIn("PRIVATE_CONFIG_VALUE", json.dumps(result))
        self.assertEqual(self.count("rounds"), 0)
        self.assertEqual(self.count("votes"), 0)


if __name__ == "__main__":
    unittest.main()
