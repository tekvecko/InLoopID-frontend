#!/usr/bin/env bash
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${PROJECT_ROOT}/.logs"

echo "[*] Zastavuji předprodukční stack InLoopID..."

if [ -f "${LOG_DIR}/backend.pid" ]; then
    kill $(cat "${LOG_DIR}/backend.pid") 2>/dev/null || true
    rm -f "${LOG_DIR}/backend.pid"
    echo "[+] Backend zastaven."
fi

pkill -f "vite preview" 2>/dev/null || true
echo "[+] Frontend zastaven."

echo "[+] Hotovo."
