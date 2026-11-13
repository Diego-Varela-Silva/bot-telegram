"""Faz login na sua conta (pede telefone e codigo) e salva a sessao em texto em tg_session.txt.

Esse texto vira o secret TG_SESSION no GitHub. Ele da acesso total a sua conta:
nao compartilhe, e apague o arquivo depois de cadastrar o secret.
"""

import os

from dotenv import load_dotenv
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.umask(0o077)
load_dotenv()

with TelegramClient(StringSession(), int(os.environ["API_ID"]), os.environ["API_HASH"]) as client:
    with open("tg_session.txt", "w") as f:
        f.write(client.session.save())

print("Sessao salva em tg_session.txt")
