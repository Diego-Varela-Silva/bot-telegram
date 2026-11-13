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
    await client.start()  # pede telefone, codigo e (se tiver) a senha de 2 etapas
    try:
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
