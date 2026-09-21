#!/usr/bin/env bash

SESSION="inloopid"
BACKEND_DIR="$HOME/InloopID/backend"

# Pokud už session existuje, ukončíme ji pro čistý start
tmux kill-session -t $SESSION 2>/dev/null || true

# 1. Vytvoření nové tmux session (Okno 1: Redis Server)
tmux new-session -d -s $SESSION -n "stack" -c "$BACKEND_DIR"
tmux send-keys -t $SESSION "redis-server" C-m

# 2. Vertikální rozdělení -> Pravé okno (Okno 2: Flask API)
tmux split-window -h -t $SESSION -c "$BACKEND_DIR"
tmux send-keys -t $SESSION "source venv/bin/activate && python app.py" C-m

# 3. Horizontální rozdělení pravé strany -> Pravé dole (Okno 3: Celery Worker)
tmux split-window -v -t $SESSION -c "$BACKEND_DIR"
tmux send-keys -t $SESSION "source venv/bin/activate && python -m celery -A celery_app worker --loglevel=info -P solo" C-m

# 4. Horizontální rozdělení levé strany -> Levé dole (Okno 4: Testovací terminál)
tmux select-pane -t $SESSION.0
tmux split-window -v -t $SESSION -c "$BACKEND_DIR"
tmux send-keys -t $SESSION "source venv/bin/activate" C-m

# Vyrovnání velikostí panelů na pravidelnou mřížku 2x2
tmux select-layout -t $SESSION tiled

# Připojení k tmux session
tmux attach-session -t $SESSION
