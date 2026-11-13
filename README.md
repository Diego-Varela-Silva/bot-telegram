# bot-telegram

Lê as mensagens de todos os seus chats do Telegram (com a sua conta) e, quando aparece
uma palavra-chave (padrão: **apple watch**, **macbook**), te avisa por um bot, que gera
notificação no iPhone.

## Setup (uma vez)

1. **API da sua conta:** https://my.telegram.org → *API development tools* → anote `api_id` e `api_hash`.
2. **Bot de aviso:** no Telegram, fale com `@BotFather` → `/newbot` → anote o token.
   Depois abra o chat com o seu bot e mande `/start` (senão ele não consegue te escrever).
3. **Seu user id:** mande qualquer mensagem para `@userinfobot` e copie o `Id`.
4. Configure:
   ```bash
   cp .env.example .env   # e preencha os valores
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```
5. Primeira execução (interativa: pede telefone e o código que chega no Telegram):
   ```bash
   .venv/bin/python monitor.py
   ```
   Isso cria `sessao.session`. **Esse arquivo dá acesso total à sua conta** – não compartilhe nem versione.

No iPhone: silencie os grupos que quiser e deixe só o chat do bot com notificação ligada.

## Palavras-chave

Edite `KEYWORDS` no `.env` (separadas por vírgula). Não diferencia maiúsculas, e espaço
casa com espaço, hífen ou nada: `mac book` pega "MacBook", "mac book", "Mac-Book".

## Rodar 24/7 de graça (Oracle Cloud Always Free)

Copie a pasta (incluindo `.env` e `sessao.session`) para a VM, recrie o venv e use
`bot-telegram.service` (instruções no próprio arquivo).

## Rodar de graça no GitHub Actions (repositório privado)

O workflow `.github/workflows/monitor.yml` roda `check.py` a cada 30 min: busca as
mensagens com as palavras-chave desde a última verificação e manda os avisos pelo bot.
Gasta ~1.500 dos 2.000 min/mês gratuitos de um repositório privado. Não é tempo real.

1. Preencha o `.env` (passos 1–3 do Setup acima).
2. No seu terminal: `./configurar_github.sh`. Ele faz o login (telefone + código),
   cadastra os secrets `API_ID`, `API_HASH`, `BOT_TOKEN`, `NOTIFY_CHAT_ID`, `TG_SESSION`
   e a variável `KEYWORDS`.
3. Teste: `gh workflow run monitor.yml && gh run watch`.

Para mudar as palavras: `gh variable set KEYWORDS --body "apple watch,mac book,ipad"`.

Limitação: a busca do Telegram é por palavra, então `check.py` procura cada palavra-chave
com e sem espaço ("mac book" e "macbook"), mas pode não achar grudada em outra
(ex.: "MacBookPro"). O `monitor.py` (tempo real) não tem essa limitação.
