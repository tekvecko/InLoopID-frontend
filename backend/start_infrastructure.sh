#!/bin/bash

echo "[Systém] Zahajuji start architektury InLoopID..."

# 1. Start interního backendu (uzamčen na localhost)
export FLASK_APP=app.py
flask run --host=127.0.0.1 --port=5000 > backend_internal.log 2>&1 &
BACKEND_PID=$!
echo "[Systém] Interní aplikační vrstva inicializována (PID: $BACKEND_PID, Port: 5000)"

# Čekání na stabilizaci soketu
sleep 2

# 2. Start Security Gateway
python3 api_gateway.py > gateway_public.log 2>&1 &
GATEWAY_PID=$!
echo "[Systém] API Gateway inicializována (PID: $GATEWAY_PID, Port: 8080)"

echo "[Systém] Infrastruktura je plně operační. Frontend musí směrovat požadavky výhradně na port 8080."
echo "[Systém] Pro bezpečné ukončení procesů stiskněte CTRL+C."

# Graceful shutdown handler
trap "echo -e '\n[Systém] Přijat signál k ukončení. Ukončuji procesy...'; kill $BACKEND_PID $GATEWAY_PID; exit 0" INT
wait
