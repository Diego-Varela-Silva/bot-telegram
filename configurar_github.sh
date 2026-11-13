#!/usr/bin/env bash
# Cadastra os secrets do GitHub Actions a partir do .env e da sessao do Telegram.
# Rode no seu terminal (o login pede telefone e codigo): ./configurar_github.sh
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] || { echo "Crie o .env primeiro (cp .env.example .env)"; exit 1; }
set -a; source .env; set +a

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
