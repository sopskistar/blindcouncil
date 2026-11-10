"""Scanner regressions; fixture values only, no live configuration or network."""
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from probes.review_public_changes import findings, native_actor_ids


class PublicReviewTests(unittest.TestCase):
    def test_historical_fixtures_are_not_classified_as_native_identities(self):
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.executescript("""CREATE TABLE receipts(round_id,user_id,callback_id);
                CREATE TABLE receipt_origins(round_id,user_id,origin);
                INSERT INTO receipts VALUES ('fixture','10001','fixture-callback');
                INSERT INTO receipt_origins VALUES ('fixture','10001','synthetic-sdk');
                INSERT INTO receipts VALUES ('native-test','123456789','test-callback');
                INSERT INTO receipt_origins VALUES ('native-test','123456789','hermes-telegram');""")
            identities = native_actor_ids(conn)
        self.assertEqual(identities, {"123456789"})
        self.assertEqual(findings('people = ["10001", "10002"]', identities), [])
        self.assertIn("private native participant identifier", findings('actor="123456789"', identities))

    def test_numeric_boundaries_avoid_hash_and_longer_number_false_positives(self):
        self.assertEqual(findings("01234567890", {"123456789"}), [])
        self.assertTrue(findings("id: 123456789", {"123456789"}))

    def test_token_patterns_fail_without_exposing_the_matched_value(self):
        sample = "987654" + ":" + "THIS_IS_A_TEST_STRING_1234567890"
        issues = findings("https://api.telegram.org/bot" + sample + "/getMe", set())
        self.assertIn("credential-bearing Telegram URL", issues)
        self.assertIn("token-shaped value", issues)
        self.assertNotIn(sample, str(issues))

    def test_only_exact_nonsecret_sdk_fixture_is_exempt_from_token_shape(self):
        self.assertEqual(findings("777000:SYNTHETIC_NO_VALID_BOT_TOKEN", set()), [])
        self.assertTrue(findings("777001" + ":" + "SYNTHETIC_NO_VALID_BOT_TOKEN", set()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
