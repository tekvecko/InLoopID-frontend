#!/usr/bin/env bash
set -e

PROJECT_ROOT="$HOME/InloopID"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=== [1/4] Kontrola a spuštění Redis ==="
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes
    echo "✓ Redis server spuštěn jako démon."
else
    echo "✓ Redis server již běží."
fi

echo "=== [2/4] Spuštění Celery Workeru ==="
cd "$BACKEND_DIR"
nohup python3 -m celery -A celery_app.celery worker -n worker1@%h --loglevel=info > "$BACKEND_DIR/celery.log" 2>&1 &
CELERY_PID=$!
echo "✓ Celery worker spuštěn na pozadí (PID: $CELERY_PID, log: backend/celery.log)"

echo "=== [3/4] Spuštění Flask API Backend ==="
nohup ./venv/bin/python app.py > "$BACKEND_DIR/flask.log" 2>&1 &
FLASK_PID=$!
echo "✓ Flask backend spuštěn na pozadí (PID: $FLASK_PID, log: backend/flask.log)"

if [ -d "$FRONTEND_DIR" ]; then
    echo "=== [4/4] Spuštění Frontend Dev Serveru ==="
    cd "$FRONTEND_DIR"
    nohup npm run dev > "$FRONTEND_DIR/vite.log" 2>&1 &
    FRONTEND_PID=$!
    echo "✓ Frontend spuštěn na pozadí (PID: $FRONTEND_PID, log: frontend/vite.log)"
fi

echo "=========================================="
echo " Všechny služby InloopID byly spuštěny!"
echo "=========================================="
