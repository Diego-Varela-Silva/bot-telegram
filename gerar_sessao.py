"""Faz login na sua conta (pede telefone e codigo) e salva a sessao em texto em tg_session.txt.

Esse texto vira o secret TG_SESSION no GitHub. Ele da acesso total a sua conta:
nao compartilhe, e apague o arquivo depois de cadastrar o secret.
"""

import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main() -> None:
    client = TelegramClient(StringSession(), int(os.environ["API_ID"]), os.environ["API_HASH"])
    # Pede so o telefone (nunca token de bot), depois o codigo e, se tiver, a senha de 2 etapas
    await client.start(phone=lambda: input("Seu telefone com DDI (ex.: +5511999999999): "))
    try:
        if await client.is_bot():
            raise SystemExit("Isso e uma sessao de bot. Use o seu numero de telefone.")
        with open("tg_session.txt", "w") as f:
            f.write(client.session.save())
    finally:
        await client.disconnect()
    print("Sessao salva em tg_session.txt")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.umask(0o077)
    load_dotenv()
    asyncio.run(main())
