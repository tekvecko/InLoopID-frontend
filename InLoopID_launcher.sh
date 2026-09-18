#!/data/data/com.termux/files/usr/bin/bash

echo "====================================================="
echo " INLOOPID ENTERPRISE - INFRASTRUCTURE LAUNCHER"
echo "====================================================="

# Zajištění bezpečného ukončení procesů
cleanup() {
    echo -e "\n[Systém] Přijat signál k ukončení. Zastavuji služby..."
    kill $(jobs -p) 2>/dev/null || true
    echo "[Systém] Infrastruktura InLoopID byla bezpečně vypnuta."
    exit 0
}
trap cleanup SIGINT SIGTERM

# 1. Start Backendu (Produkční WSGI server)
if [ -d "$HOME/InloopID/backend" ]; then
    echo "[Systém] Inicializuji backend server (Port 5000)..."
    cd "$HOME/InloopID/backend"
    python3 start_prod.py &
else
    echo "[Chyba] Adresář backendu nenalezen."
    exit 1
fi

# 2. Start Frontendu (Vite Dev Server s podporou sítě)
if [ -d "$HOME/InloopID/frontend" ]; then
    echo "[Systém] Inicializuji frontend server (Port 5173)..."
    cd "$HOME/InloopID/frontend"
    npm run dev -- --host
else
    echo "[Chyba] Adresář frontendu nenalezen."
    exit 1
fi
