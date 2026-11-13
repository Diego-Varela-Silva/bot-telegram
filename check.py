"""Versao "polling" para GitHub Actions: busca mensagens novas desde a ultima execucao e avisa.

Usa a busca global do Telegram (uma consulta por variacao de palavra-chave) e confirma
cada resultado com a mesma regex do monitor.py. O horario da ultima verificacao fica
em state.json (guardado entre execucoes pelo cache do Actions).
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon.sessions import StringSession

from monitor import build_pattern, message_link, send_bot_message

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
log = logging.getLogger("check")

STATE_FILE = "state.json"
DEFAULT_KEYWORDS = "apple watch,mac book"


def search_terms(keywords: str) -> set[str]:
    """'apple watch' -> {'apple watch', 'applewatch'} (a busca do Telegram e por palavra)."""
    terms = set()
    for kw in keywords.split(","):
        kw = " ".join(kw.split()).lower()
        if kw:
            terms.add(kw)
            terms.add(kw.replace(" ", ""))
    return terms


def load_since(lookback: int) -> float:
    try:
        with open(STATE_FILE) as f:
            return float(json.load(f)["last_ts"])
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError):
        return time.time() - lookback


async def run() -> int:
    keywords = os.environ.get("KEYWORDS") or DEFAULT_KEYWORDS
    pattern = build_pattern(keywords)
    bot_token = os.environ["BOT_TOKEN"]
    notify_chat_id = os.environ["NOTIFY_CHAT_ID"]
    bot_id = int(bot_token.split(":", 1)[0])
    lookback = int(os.environ.get("LOOKBACK_SECONDS") or 3600)

    since = load_since(lookback)
    now = time.time()
    since_dt = datetime.fromtimestamp(since, timezone.utc)
    now_dt = datetime.fromtimestamp(now, timezone.utc)

    client = TelegramClient(
        StringSession(os.environ["TG_SESSION"]), int(os.environ["API_ID"]), os.environ["API_HASH"]
    )
    await client.connect()
    if not await client.is_user_authorized():
        log.error("TG_SESSION invalida ou expirada: gere de novo com gerar_sessao.py")
        return 1
    if await client.is_bot():
        log.error("TG_SESSION e de um bot; gere de novo com gerar_sessao.py usando seu telefone")
        return 1

    found = {}
    async with client:
        for term in search_terms(keywords):
            async for msg in client.iter_messages(None, search=term, limit=200):
                if msg.date <= since_dt:
                    break  # resultados vem do mais novo para o mais antigo
                if msg.date > now_dt or msg.out or msg.chat_id == bot_id:
                    continue
                if msg.raw_text and pattern.search(msg.raw_text):
                    found[(msg.chat_id, msg.id)] = msg

        failures = 0
        for msg in sorted(found.values(), key=lambda m: m.date):
            chat = await msg.get_chat()
            sender = await msg.get_sender()
            chat_name = getattr(chat, "title", None) or getattr(chat, "first_name", None) or "?"
            sender_name = (
                getattr(sender, "first_name", None) or getattr(sender, "title", None) or "?"
            ) if sender else "?"
            match = pattern.search(msg.raw_text).group(0)
            body = f"🔔 \"{match}\" em {chat_name}\n👤 {sender_name}\n\n{msg.raw_text[:3000]}"
            link = message_link(chat, msg.chat_id, msg.id)
            if link:
                body += f"\n\n{link}"
            try:
                await asyncio.to_thread(send_bot_message, bot_token, notify_chat_id, body)
            except Exception:
                failures += 1
                log.exception("Falha ao enviar um alerta")

    log.info("Mensagens encontradas: %d, falhas de envio: %d", len(found), failures)
    if failures:
        return 1  # nao avanca o checkpoint: a proxima execucao tenta de novo

    with open(STATE_FILE, "w") as f:
        json.dump({"last_ts": now}, f)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
