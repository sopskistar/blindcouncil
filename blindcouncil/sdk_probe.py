"""Real PTB routing with synthetic Updates and an in-memory Bot API transport.

These are SDK integration tests, NOT real Telegram interactions or a live Hermes gateway.
"""
import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch
from . import lifecycle, policy


async def run(ctx, wire):
    from telegram import Update
    from telegram.ext import Application, CallbackQueryHandler
    from telegram.request import BaseRequest

    class SyntheticRequest(BaseRequest):
        calls = []
        sent = []
        @property
        def read_timeout(self):
            return 5.0
        async def initialize(self):
            pass
        async def shutdown(self):
            pass
        async def do_request(self, url, method, request_data=None, **kwargs):
            endpoint = url.rsplit("/", 1)[-1]
            self.calls.append(endpoint)
            if endpoint == "getMe":
                result = {"id": 777000, "first_name": "Synthetic", "is_bot": True,
                          "username": "blindcouncil_synthetic_bot"}
            elif endpoint == "sendMessage":
                params = request_data.parameters
                result = {"message_id": 200 + len(self.sent), "date": 1,
                          "chat": {"id": int(params["chat_id"]), "type": "private"}, "text": params["text"]}
                self.sent.append(result)
            else:
                result = True
            return 200, json.dumps({"ok": True, "result": result}).encode()

    app = (Application.builder().token("777000:SYNTHETIC_NO_VALID_BOT_TOKEN")
           .request(SyntheticRequest()).get_updates_request(SyntheticRequest()).build())
    settings = {"owner_id": "10001", "participants": ["10001", "10002"]}
    fixture_context = SimpleNamespace(get_config=lambda key, default=None: settings.get(key, default))
    wire(fixture_context, app, None)
    fallback_seen = []
    async def fallback(update, context):
        fallback_seen.append(update.callback_query.data)
    app.add_handler(CallbackQueryHandler(fallback))
    await app.initialize()
    round_id = policy.create("10001", ["10001", "10002"])
    policy.bind(round_id, "10001", "10001", 101)
    policy.bind(round_id, "10002", "10002", 102)
    sequence = 0
    results = []
    async def press(user, chat, message, data):
        nonlocal sequence
        sequence += 1
        update = Update.de_json({"update_id": sequence, "callback_query": {
            "id": str(sequence), "from": {"id": user, "is_bot": False, "first_name": "Synthetic"},
            "chat_instance": "synthetic", "data": data,
            "message": {"message_id": message, "date": 1, "chat": {"id": chat, "type": "private"},
                        "text": "Synthetic decision"}}}, app.bot)
        await app.process_update(update)
    def check(name, expected):
        actual = policy.aggregate(round_id, "10001")
        assert actual["status"] == expected, (name, actual)
        results.append({"case": name, "passed": True, "aggregate": actual})
    await press(99999, 10002, 102, f"blindcouncil:{round_id}:yes")
    check("from_user_identity_rejected_even_with_valid_round_and_message", "pending")
    await press(10002, 10001, 101, f"blindcouncil:{round_id}:yes")
    check("wrong_private_message_rejected", "pending")
    await press(10001, 10001, 101, f"blindcouncil:{round_id}:yes")
    check("first_synthetic_identity", "pending")
    await press(10001, 10001, 101, f"blindcouncil:{round_id}:no")
    check("duplicate_does_not_complete_round", "pending")
    await press(10002, 10002, 102, f"blindcouncil:{round_id}:yes")
    check("second_synthetic_identity", "approved")
    await press(10001, 10001, 101, "model:unrelated")
    assert fallback_seen == ["model:unrelated"], fallback_seen
    results.append({"case": "unrelated_prefix_reaches_fallback_handler", "passed": True})
    cancelled = policy.create("10001", ["10001", "10002"])
    policy.bind(cancelled, "10002", "10002", 202)
    policy.cancel(cancelled, "10001", ["10001", "10002"])
    await press(10002, 10002, 202, f"blindcouncil:{cancelled}:yes")
    assert policy.aggregate(cancelled, "10001")["status"] == "cancelled"
    with policy.database() as conn:
        assert conn.execute("SELECT outcome FROM callback_attempts WHERE callback_id=?", (str(sequence),)).fetchone() == ("cancelled",)
        assert conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (cancelled,)).fetchone()[0] == 0
    results.append({"case": "cancelled_callback_no_new_response", "passed": True})
    with patch.object(lifecycle, "now", return_value=1):
        expired = policy.create("10001", ["10001", "10002"], expires_in=1)
    policy.bind(expired, "10002", "10002", 203)
    await press(10002, 10002, 203, f"blindcouncil:{expired}:yes")
    assert policy.aggregate(expired, "10001")["status"] == "expired"
    with policy.database() as conn:
        assert conn.execute("SELECT outcome FROM callback_attempts WHERE callback_id=?", (str(sequence),)).fetchone() == ("expired",)
        assert conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (expired,)).fetchone()[0] == 0
    results.append({"case": "expired_callback_no_new_response", "passed": True})
    async def command(user, text):
        nonlocal sequence
        sequence += 1
        update = Update.de_json({"update_id": sequence, "message": {
            "message_id": sequence + 1000, "date": 1,
            "from": {"id": user, "is_bot": False, "first_name": "Synthetic"},
            "chat": {"id": user, "type": "private"}, "text": text,
            "entities": [{"type": "bot_command", "offset": 0, "length": 8}]}}, app.bot)
        await app.process_update(update)
    await command(10001, "/bcprobe")
    from .notification_worker import process_one
    for _ in range(30):
        if not await process_one(app.bot, {"10001", "10002"}):
            break
    with policy.database() as conn:
        created = conn.execute("SELECT id FROM rounds ORDER BY rowid DESC LIMIT 1").fetchone()[0]
        assert conn.execute("SELECT COUNT(*) FROM deliveries WHERE round_id=?", (created,)).fetchone()[0] == 2
    assert "editMessageReplyMarkup" in SyntheticRequest.calls
    results.append({"case": "native_command_binds_before_attaching_keyboard", "passed": True})
    await command(10001, f"/bcprobe wrong-message {created}")
    diagnostic = SyntheticRequest.sent[-2]
    assert "intentionally unbound" in diagnostic["text"]
    await press(10002, 10002, diagnostic["message_id"], f"blindcouncil:{created}:yes")
    with policy.database() as conn:
        assert conn.execute("SELECT outcome,reason FROM callback_attempts WHERE callback_id=?", (str(sequence),)).fetchone() == ("denied", "message_binding_or_choice")
        assert conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (created,)).fetchone()[0] == 0
    results.append({"case": "unbound_diagnostic_message_cannot_cast_vote", "passed": True})
    await command(10002, f"/bcprobe wrong-message {created}")
    assert "configuration is incomplete" in SyntheticRequest.sent[-1]["text"]
    results.append({"case": "nonowner_cannot_send_security_diagnostic", "passed": True})
    with policy.database() as conn:
        votes = conn.execute("SELECT COUNT(*) FROM votes WHERE round_id=?", (round_id,)).fetchone()[0]
        receipts = conn.execute("SELECT COUNT(*) FROM receipts WHERE round_id=?", (round_id,)).fetchone()[0]
    assert votes == 2
    assert receipts == 2
    await app.shutdown()
    return {"classification": "PTB SDK integration using synthetic Updates and in-memory Bot API; not a live Hermes gateway",
            "round_id": round_id, "distinct_synthetic_votes": votes, "synthetic_callback_receipts": receipts,
            "passed": len(results), "cases": results,
            "in_memory_bot_api_methods": SyntheticRequest.calls,
            "real_telegram_api_calls": 0, "real_second_account_callback": "BLOCKED"}


def probe(ctx, wire):
    return asyncio.run(run(ctx, wire))
