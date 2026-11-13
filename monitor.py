"""Monitora todas as conversas do Telegram e avisa via bot quando aparecer uma palavra-chave."""

import asyncio
import json
import logging
import os
import re
import urllib.parse
import urllib.request

from dotenv import load_dotenv
from telethon import TelegramClient, events

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("monitor")


def build_pattern(keywords: str) -> re.Pattern:
    """'apple watch,macbook' -> regex que aceita espaco, hifen ou nada entre as palavras."""
    parts = []
    for kw in keywords.split(","):
        words = kw.strip().split()
        if words:
            parts.append(r"[\s\-_]*".join(re.escape(w) for w in words))
    if not parts:
        raise ValueError("KEYWORDS vazio")
    return re.compile("|".join(parts), re.IGNORECASE)


def message_link(chat, chat_id: int, msg_id: int) -> str | None:
    username = getattr(chat, "username", None)
    if username:
        return f"https://t.me/{username}/{msg_id}"
    if str(chat_id).startswith("-100"):  # supergrupo/canal privado
        return f"https://t.me/c/{str(chat_id)[4:]}/{msg_id}"
    return None


def send_bot_message(token: str, chat_id: str, text: str) -> None:
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": "true"}
    ).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    with urllib.request.urlopen(req, timeout=15) as resp:
        if not json.load(resp).get("ok"):
            raise RuntimeError("Bot API retornou ok=false")


def main() -> None:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.umask(0o077)  # arquivo .session so legivel por voce
    load_dotenv()

    api_id = int(os.environ["API_ID"])
    api_hash = os.environ["API_HASH"]
    bot_token = os.environ["BOT_TOKEN"]
    notify_chat_id = os.environ["NOTIFY_CHAT_ID"]
    pattern = build_pattern(os.environ.get("KEYWORDS", "apple watch,mac book"))
    bot_id = int(bot_token.split(":", 1)[0])  # ignora as mensagens do proprio bot (evita loop)

    client = TelegramClient("sessao", api_id, api_hash)

    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        text = event.raw_text or ""
        if event.chat_id == bot_id:
            return
        match = pattern.search(text)
        if not match:
            return

        chat = await event.get_chat()
        sender = await event.get_sender()
        chat_name = getattr(chat, "title", None) or getattr(chat, "first_name", None) or "?"
        sender_name = (
            getattr(sender, "first_name", None) or getattr(sender, "title", None) or "?"
        ) if sender else "?"
        link = message_link(chat, event.chat_id, event.id)

        body = f"🔔 \"{match.group(0)}\" em {chat_name}\n👤 {sender_name}\n\n{text[:3000]}"
        if link:
            body += f"\n\n{link}"

        try:
            await asyncio.to_thread(send_bot_message, bot_token, notify_chat_id, body)
            log.info("Alerta enviado: %r em %s", match.group(0), chat_name)
        except Exception:
            log.exception("Falha ao enviar alerta")

    client.start()  # na primeira vez pede telefone + codigo no terminal
    log.info("Monitorando: %s", pattern.pattern)
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
