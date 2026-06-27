import os
import logging
import requests

log = logging.getLogger(__name__)


def send(msg: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"},
            timeout=10,
        )
        if not resp.ok:
            log.warning("[net-monitor] Telegram API error %s: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        log.warning("[net-monitor] Failed to send Telegram alert: %s", exc)


def alert_down(name: str, check_type: str, detail: str):
    send(f"🔴 *DOWN* — {name}\nType: `{check_type}`\nTarget: `{detail}`")


def alert_up(name: str, check_type: str, detail: str):
    send(f"🟢 *UP* — {name} is back online\nType: `{check_type}`\nTarget: `{detail}`")
