#!/bin/bash
BASE_DIR="$HOME/InloopID"
VENV_PYTHON="$BASE_DIR/backend/venv/bin/python3"
mkdir -p "$BASE_DIR/logs"

if [ ! -f "$VENV_PYTHON" ]; then
    VENV_PYTHON="python3"
fi

# 1. Redis
if ! redis-cli ping >/dev/null 2>&1; then
    redis-server --daemonize yes
    echo "[+] Redis spuštěn."
else
    echo "[+] Redis již běží."
fi

# 2. Celery Worker (nutný --pool=solo pro Termux)
cd "$BASE_DIR/backend" || exit 1
PYTHONPATH="$BASE_DIR/backend" nohup "$VENV_PYTHON" -m celery -A celery_app.celery worker --pool=solo --loglevel=info > "$BASE_DIR/logs/celery.log" 2>&1 &
echo $! > "$BASE_DIR/logs/celery.pid"
echo "[+] Celery worker spuštěn (PID: $(cat "$BASE_DIR/logs/celery.pid"))."

# 3. Waitress API
nohup "$VENV_PYTHON" app.py > "$BASE_DIR/logs/waitress.log" 2>&1 &
echo $! > "$BASE_DIR/logs/waitress.pid"
echo "[+] Waitress API spuštěno (PID: $(cat "$BASE_DIR/logs/waitress.pid"))."

# 4. Frontend Vite
cd "$BASE_DIR/frontend" || exit 1
nohup npx vite --host > "$BASE_DIR/logs/frontend.log" 2>&1 &
echo $! > "$BASE_DIR/logs/frontend.pid"
cd "$BASE_DIR" || exit 1
echo "[+] Frontend (React/Vite) spuštěn."

echo "[SUCCESS] Všechny služby byly nastartovány!"
