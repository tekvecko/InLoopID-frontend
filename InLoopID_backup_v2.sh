#!/bin/bash

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$HOME/InloopID"
BACKUP_DIR="$HOME/InloopID_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
# Změna názvu zálohy na V2 pro jasné odlišení
BACKUP_FILE="$BACKUP_DIR/InLoopID_V2_Multisig_${TIMESTAMP}.tar.gz"

echo -e "${BLUE}=== InLoopID Protocol: Údržba a Záloha V2 ===${NC}"

# 1. ČIŠTĚNÍ
echo -e "${YELLOW}[*] Zahajuji čištění dočasných souborů a logů...${NC}"
cd "$PROJECT_DIR"

# Odstranění aplikačních logů
rm -f backend/*.log
rm -f frontend/*.log

# Odstranění zkompilovaného Python balastu
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null

# Odstranění Vite cache
rm -rf frontend/node_modules/.vite 2>/dev/null

echo -e "${GREEN}[+] Čištění prostředí dokončeno.${NC}"

# 2. ZÁLOHA
echo -e "${YELLOW}[*] Komprimuji projekt do záložního archivu...${NC}"
mkdir -p "$BACKUP_DIR"

# Vytvoření čisté zálohy
tar -czf "$BACKUP_FILE" \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    -C "$HOME" InloopID

echo -e "${GREEN}[+] Záloha V2 úspěšně vytvořena a uložena zde:${NC}"
echo -e "${BLUE}$BACKUP_FILE${NC}"
echo -e "${BLUE}==========================================${NC}"
