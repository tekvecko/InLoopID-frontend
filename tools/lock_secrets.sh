#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ENV_FILE="$HOME/InloopID/.env"

if [ -f "$ENV_FILE" ]; then
    chmod 600 "$ENV_FILE"
    echo "[Bezpečnost] Oprávnění pro .env uzamčena na 600 (čtení/zápis pouze pro vlastníka)."
else
    echo "[Varování] Soubor .env nebyl nalezen."
fi
