"""Telegram Bot API client implemented with the Python standard library."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TelegramClient:
    """Send messages and acknowledge callback queries through Telegram."""
    def __init__(self, token, session=None, timeout=30):
        if not token: raise ValueError("TELEGRAM_BOT_TOKEN is required")
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = session
        self.timeout = timeout

    def call(self, method, payload=None):
        body = json.dumps(payload or {}).encode("utf-8")
        request = Request(f"{self.base_url}/{method}", data=body, headers={"Content-Type": "application/json"})
        try:
            if self.session:
                response = self.session.post(request.full_url, data=body, headers=dict(request.header_items()), timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
            else:
                with urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"Telegram API {method} returned HTTP {exc.code}") from None
        except URLError:
            raise RuntimeError(f"Telegram API {method} transport failed") from None
        except Exception:
            # Avoid propagating request-library errors that may include the token URL.
            raise RuntimeError(f"Telegram API {method} request failed") from None
        if not data.get("ok"): raise RuntimeError(f"Telegram API {method} failed")
        return data.get("result")

    def send(self, chat_id, text, keyboard=None):
        payload = {"chat_id": chat_id, "text": text}
        if keyboard: payload["reply_markup"] = {"inline_keyboard": keyboard}
        return self.call("sendMessage", payload)

    def answer_callback(self, callback_id, text="Done"):
        return self.call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

    def updates(self, offset=None, timeout=20):
        return self.call("getUpdates", {"offset": offset, "timeout": timeout, "allowed_updates": ["message", "callback_query"]})
