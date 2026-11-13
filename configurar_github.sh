#!/usr/bin/env bash
# Cadastra os secrets do GitHub Actions a partir do .env e da sessao do Telegram.
# Rode no seu terminal (o login pede telefone e codigo): ./configurar_github.sh
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] || { echo "Crie o .env primeiro (cp .env.example .env)"; exit 1; }

# Le uma chave do .env sem executar o arquivo (valores podem ter espacos/aspas)
env_get() {
  grep -E "^[[:space:]]*$1[[:space:]]*=" .env | tail -1 | cut -d= -f2- \
    | sed -E "s/^[[:space:]]+//; s/[[:space:]]+\$//; s/^[\"'](.*)[\"']\$/\1/"
}
API_ID=$(env_get API_ID)
API_HASH=$(env_get API_HASH)
BOT_TOKEN=$(env_get BOT_TOKEN)
NOTIFY_CHAT_ID=$(env_get NOTIFY_CHAT_ID)
KEYWORDS=$(env_get KEYWORDS)
for v in API_ID API_HASH BOT_TOKEN NOTIFY_CHAT_ID; do
  [ -n "${!v}" ] || { echo "Falta $v no .env"; exit 1; }
done

if [ ! -f tg_session.txt ]; then
  .venv/bin/python gerar_sessao.py
fi

gh secret set API_ID --body "$API_ID"
gh secret set API_HASH --body "$API_HASH"
gh secret set BOT_TOKEN --body "$BOT_TOKEN"
gh secret set NOTIFY_CHAT_ID --body "$NOTIFY_CHAT_ID"
gh secret set TG_SESSION < tg_session.txt
gh variable set KEYWORDS --body "${KEYWORDS:-apple watch,mac book}"

rm -f tg_session.txt
echo "Pronto. Teste agora com: gh workflow run monitor.yml && gh run watch"
