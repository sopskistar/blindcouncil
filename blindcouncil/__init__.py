"""Native two-person decision coordination. No token access or independent polling."""
import json
import os
from pathlib import Path
from gateway.platforms._shared import platform_gate_env
from . import expiry, outbox, policy


def allowed_users():
    # This probe deliberately requires an explicit DM allowlist; no wildcard or allow-all mode.
    return {x.strip() for x in platform_gate_env("TELEGRAM_ALLOWED_USERS").split(",") if x.strip().isdigit()}


async def on_button(update, context):
    from telegram.error import TelegramError
    query = update.callback_query
    if query is None or query.from_user is None or query.message is None:
        return
    parts = (query.data or "").split(":")
    if len(parts) != 3 or parts[0] != "blindcouncil":
        await query.answer("Invalid decision request.")
        return
    user = str(query.from_user.id)
    runtime = context.application.bot_data.get("blindcouncil:runtime", {})
    try:
        outcome = policy.decide(parts[1], user, query.message.chat_id, query.message.message_id,
                                parts[2], allowed_users(), callback_id=query.id, update_id=update.update_id,
                                origin=runtime.get("origin", "unclassified"), native_pid=runtime.get("pid"))
    except Exception:
        # No storage failure is reported as a successful vote; never expose exception URLs or secrets.
        await query.answer("Response could not be saved. Please retry shortly.", show_alert=True)
        return
    replies = {"recorded": "Response recorded privately.", "duplicate": "Your response is already recorded.",
               "denied": "This request is not authorized for this account or message.",
               "cancelled": "This decision was cancelled. No new response was recorded.",
               "expired": "This decision has expired. No new response was recorded.",
               "approved": "This decision is already resolved.", "rejected": "This decision is already resolved."}
    try:
        await query.answer(replies[outcome["status"]], show_alert=outcome["status"] in {"denied", "cancelled", "expired"})
    except TelegramError:
        # A stale acknowledgement cannot roll back a committed vote or prevent a result attempt.
        pass
    # Resolution and logical aggregate notifications commit atomically in policy.decide.
    # The owned native worker delivers them, including after a process restart.


def wire(ctx, application, adapter):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import CallbackQueryHandler, CommandHandler
    runtime = {"origin": "hermes-telegram" if adapter is not None else "synthetic-sdk", "pid": os.getpid()}
    application.bot_data["blindcouncil:runtime"] = runtime
    if adapter is not None:
        ctx.state.set("telegram_runtime", runtime)
        from .notification_worker import run as run_notifications
        previous = application.bot_data.get("blindcouncil:worker")
        if previous is None or previous.done():
            application.bot_data["blindcouncil:worker"] = ctx.spawn_task(
                run_notifications(application, allowed_users), name="blindcouncil:notifications")
    async def start(update, context):
        owner = str(ctx.get_config("owner_id", ""))
        people = [str(x) for x in ctx.get_config("participants", [])]
        caller = str(update.effective_user.id) if update.effective_user else ""
        if (caller != owner or caller not in allowed_users() or update.effective_chat.type != "private"
                or not set(people).issubset(allowed_users())):
            await update.effective_message.reply_text("BlindCouncil owner, participant, or Telegram allowlist configuration is incomplete.")
            return
        arguments = context.args or []
        if arguments and arguments[0] == "cancel" and len(arguments) == 2:
            result = policy.cancel(arguments[1], caller, allowed_users())
            await update.effective_message.reply_text(f"BlindCouncil {arguments[1]}: {result['status'].upper()}.")
            return
        if arguments and arguments[0] == "wrong-message" and len(arguments) == 2:
            identifier = arguments[1]
            if policy.aggregate(identifier, caller)["status"] != "pending":
                await update.effective_message.reply_text("Use an owned pending round for the message-binding diagnostic.")
                return
            second = next(person for person in people if person != owner)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Test message binding", callback_data=f"blindcouncil:{identifier}:yes")]])
            await context.bot.send_message(chat_id=int(second),
                text=f"BlindCouncil security test for {identifier}. This diagnostic copy is intentionally unbound. Press Test message binding; expected DENIED and no response recorded.",
                reply_markup=keyboard)
            await update.effective_message.reply_text(f"Unbound diagnostic sent for {identifier}; the original invitation is unchanged.")
            return
        seconds = 86400
        if arguments:
            if len(arguments) != 2 or arguments[0] != "expire" or not arguments[1].isdigit() or not 1 <= int(arguments[1]) <= 604800:
                await update.effective_message.reply_text("Use /bcprobe, /bcprobe expire SECONDS (1–604800), /bcprobe cancel ROUND_ID, or /bcprobe wrong-message ROUND_ID.")
                return
            seconds = int(arguments[1])
        round_id = policy.create(owner, people, title="Telegram integration test", expires_in=seconds)
        await update.effective_message.reply_text(f"BlindCouncil {round_id} created. Private requests are queued for delivery; duration {seconds} seconds.")
    application.add_handler(CallbackQueryHandler(on_button, pattern=r"^blindcouncil:"))
    application.add_handler(CommandHandler("bcprobe", start))


def readiness(ctx):
    people = [str(x) for x in ctx.get_config("participants", [])]
    owner = str(ctx.get_config("owner_id", ""))
    issues = []
    if len(people) != 2 or len(set(people)) != 2 or any(not x.isdigit() or int(x) <= 0 for x in people):
        issues.append("Configure two distinct positive Telegram user IDs")
    if owner not in people:
        issues.append("Configured owner must be one of the participants")
    if set(people) == {"10001", "10002"}:
        issues.append("Replace the research fixture IDs before the genuine-account test")
    if not people or not set(people).issubset(allowed_users()):
        issues.append("Both participants must be explicitly listed in TELEGRAM_ALLOWED_USERS")
    return {"status": "BLOCKED" if issues else "READY_FOR_MANUAL_TEST", "issues": issues,
            "configured_participant_count": len(people), "credentials_shown": False,
            "live_callback_test_passed": False}


def configure(ctx):
    import sys
    if not sys.stdin.isatty():
        raise SystemExit("Run configure in your own terminal; enter IDs locally, never a bot token here.")
    owner = input("Account 1 / owner Telegram numeric user ID: ").strip()
    second = input("Account 2 Telegram numeric user ID: ").strip()
    if owner == second or any(not x.isdigit() or int(x) <= 0 for x in [owner, second]):
        raise SystemExit("Two distinct positive numeric user IDs are required. Nothing changed.")
    ctx.set_config("owner_id", owner)
    ctx.set_config("participants", [owner, second])
    return readiness(ctx)


def evidence(ctx, round_id):
    owner = str(ctx.get_config("owner_id", ""))
    people = {str(x) for x in ctx.get_config("participants", [])}
    result = policy.aggregate(round_id, owner)
    if result["status"] == "denied":
        return result
    with policy.database() as conn:
        rows = conn.execute("""SELECT r.user_id,r.callback_id,r.update_id,o.origin,o.native_pid
            FROM receipts r LEFT JOIN receipt_origins o USING(round_id,user_id)
            WHERE r.round_id=?""", (round_id,)).fetchall()
        delivered = conn.execute("SELECT COUNT(*) FROM deliveries WHERE round_id=?", (round_id,)).fetchone()[0]
        attempts = conn.execute("SELECT outcome,reason,origin,COUNT(*) FROM callback_attempts WHERE round_id=? GROUP BY outcome,reason,origin", (round_id,)).fetchall()
    native = [row for row in rows if row[3] == "hermes-telegram" and row[1] and row[2] is not None]
    matched = (len(native) == 2 and {row[0] for row in native} == people
               and len({row[1] for row in native}) == 2 and len({row[2] for row in native}) == 2)
    return {"round_id": round_id, "aggregate": result["status"], "bound_deliveries": delivered,
            "receipt_count": len(rows), "native_receipt_count": len(native),
            "two_configured_identities_match": matched,
            "synthetic_or_unclassified_receipts": len(rows) - len(native),
            "audited_callback_attempts": [{"outcome": x[0], "reason": x[1], "origin": x[2], "count": x[3]} for x in attempts],
            "callback_identity_gate": "PASS" if matched else "BLOCKED",
            "scope": "Local receipt audit; verify a real Hermes gateway was running and humans pressed the buttons",
            "individual_votes_exported": False, "participant_ids_exported": False,
            "delivery": outbox.status(round_id, owner)}


def local_probe():
    """Synthetic identities only. This never sends to Telegram."""
    people = ["10001", "10002"]
    round_id = policy.create(people[0], people)
    policy.bind(round_id, people[0], people[0], 101)
    policy.bind(round_id, people[1], people[1], 102)
    outcomes = []
    def check(name, actual, expected):
        assert actual == {"status": expected}, (name, actual)
        outcomes.append({"case": name, "passed": True, "result": actual})
    check("unauthorized", policy.decide(round_id, "99999", "99999", 101, "yes", people), "denied")
    check("gateway_allowlist", policy.decide(round_id, people[1], people[1], 102, "yes", [people[0]]), "denied")
    check("message_binding", policy.decide(round_id, people[1], people[0], 101, "yes", people), "denied")
    check("first_vote", policy.decide(round_id, people[0], people[0], 101, "yes", people), "recorded")
    check("private_pending", policy.aggregate(round_id, people[0]), "pending")
    check("duplicate", policy.decide(round_id, people[0], people[0], 101, "no", people), "duplicate")
    check("second_vote", policy.decide(round_id, people[1], people[1], 102, "yes", people), "recorded")
    check("unanimity", policy.aggregate(round_id, people[0]), "approved")
    check("aggregate_access", policy.aggregate(round_id, people[1]), "denied")
    rejected = policy.create(people[0], people)
    for index, person in enumerate(people):
        policy.bind(rejected, person, person, index + 201)
        policy.decide(rejected, person, person, index + 201, "yes" if index == 0 else "no", people)
    check("mixed_votes", policy.aggregate(rejected, people[0]), "rejected")
    return {"classification": "synthetic-ID deterministic policy tests in a real loaded Hermes plugin",
            "telegram_api_calls_made": 0, "real_second_account_callback": "BLOCKED", "round_id": round_id,
            "cases": outcomes, "passed": len(outcomes)}


def register(ctx):
    if not all(callable(getattr(ctx, name, None)) for name in ("register_platform_handler", "spawn_task", "register_rpc")):
        raise RuntimeError("BlindCouncil requires Hermes native platform handlers, supervised plugin tasks and plugin RPC. Use Hermes >=0.23.1.")
    ctx.register_platform_handler("telegram", lambda application, adapter: wire(ctx, application, adapter))
    from .operator_rpc import register as register_operator
    register_operator(ctx, allowed_users, readiness)
    def setup(parser):
        parser.add_argument("action", choices=["probe", "sdk-probe", "status", "configure", "readiness", "evidence", "cancel", "revoke", "create", "history", "notifications", "retry-notifications"])
        parser.add_argument("--round-id")
        parser.add_argument("--title", default="Two-person decision")
        parser.add_argument("--description", default="")
        parser.add_argument("--expires", choices=list(expiry.PRESETS), default="24h")
        parser.add_argument("--limit", type=int, default=20)
    def run(args):
        if args.action in {"probe", "sdk-probe"}:
            test_root = os.getenv("BLINDCOUNCIL_TEST_ROOT")
            home = Path(os.getenv("HERMES_HOME", "~/.hermes")).expanduser().resolve()
            if (not test_root or not home.is_relative_to(Path(test_root).resolve())
                    or home == Path(test_root).resolve() or (home / ".env").exists()):
                raise SystemExit("Developer probes require an isolated supporting-test home without a secret file. No probe data was created.")
        if args.action == "configure":
            result = configure(ctx)
        elif args.action == "readiness":
            result = readiness(ctx)
        elif args.action == "evidence":
            result = evidence(ctx, args.round_id)
        elif args.action == "create":
            ready = readiness(ctx)
            if ready["status"] == "BLOCKED":
                result = ready
            else:
                owner = str(ctx.get_config("owner_id", ""))
                people = [str(x) for x in ctx.get_config("participants", [])]
                try:
                    identifier = policy.create(owner, people, title=args.title, description=args.description,
                                               expires_in=expiry.product_duration(args.expires))
                except ValueError as exc:
                    raise SystemExit(str(exc))
                result = policy.details(identifier, owner)
                result["creation_status"] = "created_requests_queued"
        elif args.action == "history":
            result = policy.history(ctx.get_config("owner_id", ""), args.limit)
        elif args.action == "notifications":
            result = outbox.status(args.round_id, ctx.get_config("owner_id", ""))
        elif args.action == "retry-notifications":
            result = outbox.retry_blocked(args.round_id, ctx.get_config("owner_id", ""), allowed_users())
        elif args.action == "cancel":
            if not args.round_id:
                raise SystemExit("cancel requires --round-id; nothing changed")
            result = policy.cancel(args.round_id, ctx.get_config("owner_id", ""), allowed_users())
        elif args.action == "revoke":
            owner = str(ctx.get_config("owner_id", ""))
            people = [str(x) for x in ctx.get_config("participants", [])]
            if not args.round_id or len(people) != 2 or owner not in people or len(set(people)) != 2:
                raise SystemExit("revoke requires --round-id and two configured identities; nothing changed")
            participant = next(person for person in people if person != owner)
            result = policy.revoke(args.round_id, owner, participant, allowed_users())
        elif args.action == "sdk-probe":
            from .sdk_probe import probe
            result = probe(ctx, wire)
        elif args.action == "probe":
            result = local_probe()
        else:
            result = policy.details(args.round_id, ctx.get_config("owner_id", ""))
        print(json.dumps(result, indent=2))
        if args.action in {"configure", "readiness", "create"} and result.get("status") == "BLOCKED":
            raise SystemExit(2)
    ctx.register_cli_command("blindcouncil", help="Private two-person decisions and delivery recovery", setup_fn=setup, handler_fn=run)
