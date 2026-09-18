#!/bin/bash

echo "=== INLOOPID: Údržba a Záloha ==="

# 1. ČIŠTĚNÍ PROJEKTU
echo "[*] Krok 1: Provádím čištění dočasných souborů..."
find ~/InloopID -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find ~/InloopID -type f -name "*.bak_*" -delete 2>/dev/null
echo "[+] Čištění dokončeno (odstraněny cache a staré .bak soubory)."

# 2. PŘÍPRAVA ZÁLOHY
echo "[*] Krok 2: Připravuji komprimovanou zálohu..."
mkdir -p ~/backups
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$HOME/backups/InloopID_Backup_$TIMESTAMP.tar.gz"

# 3. VYTVOŘENÍ ARCHIVU (bez zbytečných složek)
tar -czf "$BACKUP_FILE" --exclude='node_modules' --exclude='.git' -C "$HOME" InloopID

# Zjištění velikosti zálohy
FILE_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)

echo "[+] ZÁLOHA ÚSPĚŠNÁ!"
echo "    -> Umístění: $BACKUP_FILE"
echo "    -> Velikost: $FILE_SIZE"
echo "================================="
