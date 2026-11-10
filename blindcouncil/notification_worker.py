"""Owned native Telegram delivery worker. Uses the application's existing bot, never a poller."""
import asyncio
import datetime
import logging

from . import outbox

LOG = logging.getLogger(__name__)


def invite_text(identifier, view):
    deadline = datetime.datetime.fromtimestamp(view["expires_at"], datetime.timezone.utc).isoformat() if view["expires_at"] else "not recorded for this legacy round"
    text = (f"BlindCouncil {identifier}\n{view['title']}\n\n{view['description']}\n\n"
            f"Policy: two-person unanimous approval.\nIndividual responses are not displayed; the aggregate may allow inference.\nExpires: {deadline}")
    if len(text.encode("utf-16-le")) // 2 > 4096:
        raise ValueError("Invitation exceeds Telegram text limit")
    return text


async def process_one(bot, allowed_users):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.error import BadRequest, Forbidden, RetryAfter, TelegramError
    job = outbox.claim()
    if job is None:
        return False
    bound_message = None
    def allowed():
        return allowed_users() if callable(allowed_users) else allowed_users
    try:
        view = outbox.view(job, allowed())
        if view is None:
            return True
        if not view["authorized"]:
            outbox.finish(job, "blocked", error="recipient_not_authorized")
            return True
        if job["kind"] == "invite":
            if view["state"] != "pending":
                outbox.finish(job, "obsolete")
                return True
            if view["binding"] is None:
                sent = await bot.send_message(chat_id=int(job["user_id"]), text=invite_text(job["round_id"], view), parse_mode=None)
                if not outbox.save_binding(job, sent.chat_id, sent.message_id):
                    return True
            # Recheck permission/state after send; actionable buttons need a committed binding.
            view = outbox.view(job, allowed())
            if view is None:
                return True
            if not view["authorized"] or view["state"] != "pending":
                outbox.finish(job, "obsolete")
                return True
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Approve", callback_data=f"blindcouncil:{job['round_id']}:yes"),
                                              InlineKeyboardButton("Reject", callback_data=f"blindcouncil:{job['round_id']}:no")]])
            chat, message = view["binding"]
            bound_message = message
            await bot.edit_message_reply_markup(chat_id=int(chat), message_id=message, reply_markup=keyboard)
            outbox.finish(job, "sent", message_id=message)
        else:
            state = view["state"]
            if state not in {"approved", "rejected", "cancelled", "expired"}:
                outbox.finish(job, "blocked", error="result_not_terminal")
                return True
            suffix = " (two responses, unanimous policy)." if state in {"approved", "rejected"} else ". No further responses accepted."
            sent = await bot.send_message(chat_id=int(job["user_id"]), text=f"BlindCouncil {job['round_id']}: {state.upper()}{suffix}", parse_mode=None)
            outbox.finish(job, "sent", message_id=sent.message_id)
    except RetryAfter as exc:
        value = exc.retry_after
        delay = value.total_seconds() if hasattr(value, "total_seconds") else float(value)
        outbox.finish(job, "queued", error="rate_limited", delay=max(1, delay))
    except BadRequest as exc:
        if job["kind"] == "invite" and bound_message is not None and "message is not modified" in str(exc).lower():
            outbox.finish(job, "sent", message_id=bound_message)
        else:
            outbox.finish(job, "blocked", error="BadRequest")
    except Forbidden:
        outbox.finish(job, "blocked", error="Forbidden")
    except TelegramError as exc:
        if job["attempts"] >= 8:
            outbox.finish(job, "blocked", error="retry_limit_reached")
        else:
            outbox.finish(job, "queued", error=type(exc).__name__, delay=min(300, 2 ** job["attempts"]))
    except ValueError:
        outbox.finish(job, "blocked", error="invalid_notification")
    return True


async def run(application, allowed_users):
    while True:
        try:
            if not application.running:
                await asyncio.sleep(1)
                continue
            outbox.expire_due()
            handled = await process_one(application.bot, allowed_users)
            await asyncio.sleep(0.1 if handled else 1)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            # Never log exception text/URLs/recipient identifiers. A failed DB check cannot send.
            LOG.warning("BlindCouncil delivery worker retrying after %s", type(exc).__name__)
            await asyncio.sleep(2)
