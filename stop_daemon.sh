#!/data/data/com.termux/files/usr/bin/bash
echo "[*] Zastavuji InLoopID daemon procesy..."

# Zastavení Frontendu (Vite)
if [ -f "logs/frontend.pid" ]; then
    kill $(cat logs/frontend.pid) 2>/dev/null && echo "[+] Frontend zastaven."
    rm -f logs/frontend.pid
fi

# Zastavení Waitress API
if [ -f "backend/waitress.pid" ]; then
    kill $(cat backend/waitress.pid) 2>/dev/null && echo "[+] Waitress API zastaveno."
    rm -f backend/waitress.pid
fi

# Zastavení Celery workeru
if [ -f "logs/celery.pid" ]; then
    kill $(cat logs/celery.pid) 2>/dev/null && echo "[+] Celery worker zastaven."
    rm -f logs/celery.pid
fi

# Zastavení Redis serveru
if pgrep -x "redis-server" > /dev/null; then
    redis-cli shutdown > /dev/null 2>&1 && echo "[+] Redis server vypnut."
fi

echo "[SUCCESS] Všechny procesy na pozadí jsou čistě ukončeny."
