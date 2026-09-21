#!/usr/bin/env bash
set -euo pipefail

# Vyčištění kontaminujících proměnných prostředí Pythonu
unset PYTHONPATH
unset PYTHONHOME
export PYTHONPATH=""

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
LOG_DIR="${PROJECT_ROOT}/.logs"

mkdir -p "${LOG_DIR}"

echo "[*] Kontrola a spuštění Redis serveru..."
if ! pgrep -x "redis-server" > /dev/null; then
    if command -v redis-server &>/dev/null; then
        redis-server --daemonize yes
        echo "[+] Redis server spuštěn."
    else
        echo "[!] redis-server není nainstalován. Nainstalujte jej pomocí: apt update && apt install -y redis-server"
        exit 1
    fi
else
    echo "[+] Redis server již běží."
fi

echo "[*] Příprava backendu..."
cd "${BACKEND_DIR}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --quiet -r requirements.txt

export FLASK_APP=app.py
export FLASK_DEBUG=0
export REDIS_URL="redis://localhost:6379/0"

echo "[*] Spouštím backend na portu 5050..."
nohup "${BACKEND_DIR}/venv/bin/gunicorn" -w 2 -b 127.0.0.1:5050 app:app > "${LOG_DIR}/backend.log" 2>&1 &
BACKEND_PID=$!
echo "${BACKEND_PID}" > "${LOG_DIR}/backend.pid"

echo "[*] Příprava a build frontendu..."
cd "${FRONTEND_DIR}"
if [ ! -d "node_modules" ]; then
    npm ci || npm install
fi

echo "[*] Sestavuji produkční verzi React/Vite..."
npm run build

echo "[*] Spouštím frontend na portu 5173..."
nohup npx vite preview --port 5173 --host 0.0.0.0 > "${LOG_DIR}/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "${FRONTEND_PID}" > "${LOG_DIR}/frontend.log.pid"

echo ""
echo "=================================================="
echo "   InLoopID Předprodukční verze úspěšně spuštěna!"
echo "=================================================="
echo " App Frontend:  http://localhost:5173"
echo " API Backend:   http://localhost:5050"
echo " Logy uloženy:  ${LOG_DIR}/"
echo "=================================================="
echo " Pro zastavení stacku spusťte: ./stop_preprod_native.sh"
