"""Permitted operator projections for authenticated Hermes Desktop clients.

Hermes authorizes the connection and scopes the call to this plugin's profile.
This is a trusted coordinator surface, not participant login or a vote API.
"""
import os
import re

from . import expiry, outbox, policy


def register(ctx, allowed_users, readiness):
    def invoke(params, *, session_id=None, **kwargs):
        if not isinstance(params, dict):
            return {"status": "error", "message": "Invalid request."}
        action = params.get("action", "board")
        owner = str(ctx.get_config("owner_id", ""))
        people = [str(x) for x in ctx.get_config("participants", [])]
        allowed = allowed_users()
        try:
            if action == "board":
                ready = readiness(ctx)
                runtime = ctx.state.get("telegram_runtime", {})
                return {"status": "ok", "readiness": ready,
                        "decisions": policy.history(owner, 50)["decisions"] if owner in allowed else [],
                        "expiry_presets": list(expiry.PRESETS), "default_expiry": "24h",
                        "native_adapter_loaded": runtime.get("origin") == "hermes-telegram" and runtime.get("pid") == os.getpid(),
                        "access": "Authenticated Hermes operator; individual responses are not returned."}
            if action == "create":
                ready = readiness(ctx)
                if ready["status"] == "BLOCKED":
                    return {"status": "blocked", "message": "Complete the two-account setup in your terminal first.", "issues": ready["issues"]}
                duration = expiry.product_duration(params.get("expires", "24h"))
                identifier = policy.create(owner, people, title=params.get("title", ""),
                                           description=params.get("description", ""), expires_in=duration)
                return {"status": "created", "decision": policy.details(identifier, owner)}
            identifier = params.get("round_id")
            if not isinstance(identifier, str) or not re.fullmatch(r"[0-9a-f]{12}", identifier):
                return {"status": "error", "message": "Choose a valid decision."}
            if owner not in allowed:
                return {"status": "denied", "message": "The coordinator is not currently authorized."}
            if action == "detail":
                return {"status": "ok", "decision": policy.details(identifier, owner),
                        "delivery": outbox.status(identifier, owner)}
            if action == "cancel":
                return policy.cancel(identifier, owner, allowed)
            if action == "retry":
                return outbox.retry_blocked(identifier, owner, allowed)
            return {"status": "error", "message": "This operation is not available."}
        except (TypeError, ValueError):
            return {"status": "error", "message": "Check the title, description and supported expiry duration."}
        except Exception:
            # Native RPC otherwise returns exception text: never expose storage paths or data.
            return {"status": "error", "message": "The decision could not be saved or loaded. Check local storage and retry."}

    ctx.register_rpc("operator", invoke)
