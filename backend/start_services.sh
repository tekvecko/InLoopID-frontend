#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$HOME/InloopID/backend"
RUN_DIR="$PROJECT_DIR/run"
VENV_PATH="$PROJECT_DIR/venv"

REDIS_PID="$RUN_DIR/redis.pid"
CELERY_PID="$RUN_DIR/celery.pid"
FLASK_PID="$RUN_DIR/flask.pid"

REDIS_LOG="$RUN_DIR/redis.log"
CELERY_LOG="$RUN_DIR/celery.log"
FLASK_LOG="$RUN_DIR/flask.log"

mkdir -p "$RUN_DIR"

is_running() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file" 2>/dev/null || true)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

activate_venv() {
    if [ -d "$VENV_PATH" ]; then
        # shellcheck disable=SC1091
        source "$VENV_PATH/bin/activate"
    else
        echo "[ERROR] Virtuální prostředí nebylo nalezeno v $VENV_PATH!" >&2
        exit 1
    fi
}

start_services() {
    echo "=== Spouštění služeb InloopID ==="
    activate_venv
    cd "$PROJECT_DIR"

    # 1. Redis Server
    if pgrep -f "redis-server" > /dev/null; then
        echo "[INFO] Redis server již běží na pozadí."
        pgrep -f "redis-server" | head -n 1 > "$REDIS_PID"
    else
        echo "[START] Spouštím Redis server..."
        nohup redis-server --daemonize yes --pidfile "$REDIS_PID" --logfile "$REDIS_LOG" > /dev/null 2>&1 &
        sleep 1.5
        if pgrep -f "redis-server" > /dev/null; then
            pgrep -f "redis-server" | head -n 1 > "$REDIS_PID"
            echo "[OK] Redis spuštěn (PID: $(cat "$REDIS_PID"))."
        else
            echo "[FAIL] Chyba při spuštění Redis serveru. Zkontroluj $REDIS_LOG." >&2
        fi
    fi

    # 2. Celery Worker
    if is_running "$CELERY_PID"; then
        echo "[INFO] Celery worker již běží (PID: $(cat "$CELERY_PID"))."
    else
        echo "[START] Spouštím Celery worker..."
        source "$VENV_PATH/bin/activate" && cd "$PROJECT_DIR" && nohup celery -A celery_app:celery worker --loglevel=info -P solo > "$CELERY_LOG" 2>&1 &
        echo $! > "$CELERY_PID"
        sleep 2
        if is_running "$CELERY_PID"; then
            echo "[OK] Celery worker spuštěn (PID: $(cat "$CELERY_PID"))."
        else
            echo "[FAIL] Chyba při spuštění Celery workeru. Zkontroluj $CELERY_LOG." >&2
        fi
    fi

    # 3. Flask API
    # Pojistka: uvolnění portu 5001, pokud ještě visí
    fuser -k 5001/tcp 2>/dev/null || true

    echo "[START] Spouštím Flask API..."
    nohup python3 app.py > "$FLASK_LOG" 2>&1 &
    echo $! > "$FLASK_PID"
    sleep 2
    if is_running "$FLASK_PID" || pgrep -f "python3 app.py" > /dev/null; then
        pgrep -f "python3 app.py" | head -n 1 > "$FLASK_PID"
        echo "[OK] Flask API spuštěno (PID: $(cat "$FLASK_PID"))."
    else
        echo "[FAIL] Chyba při spuštění Flask API. Zkontroluj $FLASK_LOG." >&2
    fi

    echo "=== Operace dokončena ==="
}

stop_services() {
    echo "=== Zastavování služeb InloopID ==="

    # Zastavení Flask + uvolnění portu 5001
    fuser -k 5001/tcp 2>/dev/null || true
    if is_running "$FLASK_PID"; then
        kill "$(cat "$FLASK_PID")" 2>/dev/null || true
        rm -f "$FLASK_PID"
    fi
    pkill -f "python3 app.py" 2>/dev/null || true

    # Zastavení Celery
    if is_running "$CELERY_PID"; then
        kill "$(cat "$CELERY_PID")" 2>/dev/null || true
        rm -f "$CELERY_PID"
    fi
    pkill -f "celery -A celery_app:celery" 2>/dev/null || true

    # Zastavení Redis
    if is_running "$REDIS_PID"; then
        kill "$(cat "$REDIS_PID")" 2>/dev/null || true
        rm -f "$REDIS_PID"
    fi
    pkill -f "redis-server" 2>/dev/null || true

    echo "=== Všechny služby byly zastaveny ==="
}

status_services() {
    echo "=== Stav služeb InloopID ==="

    if pgrep -f "redis-server" > /dev/null; then
        echo "Redis server:  BĚŽÍ (PID: $(pgrep -f "redis-server" | head -n 1))"
    else
        echo "Redis server:  NEBĚŽÍ"
    fi

    if is_running "$CELERY_PID"; then
        echo "Celery worker: BĚŽÍ (PID: $(cat "$CELERY_PID"))"
    else
        echo "Celery worker: NEBĚŽÍ"
    fi

    if is_running "$FLASK_PID" || pgrep -f "python3 app.py" > /dev/null; then
        echo "Flask API:     BĚŽÍ (PID: $(pgrep -f "python3 app.py" | head -n 1))"
    else
        echo "Flask API:     NEBĚŽÍ"
    fi
}

case "${1:-status}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        status_services
        ;;
    *)
        echo "Použití: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
