#!/usr/bin/env bash
set -euo pipefail

echo "==> Spouštím audit Termux prostředí a projektu..."

# Cílová složka stažených souborů v Androidu (Termux symlink nebo přímá cesta)
DOWNLOAD_DIR="$HOME/storage/downloads"
if [ ! -d "$DOWNLOAD_DIR" ]; then
    DOWNLOAD_DIR="/storage/emulated/0/Download"
fi

if [ ! -d "$DOWNLOAD_DIR" ]; then
    echo "CHYBA: Složka Downloads není dostupná. Spustil jsi 'termux-setup-storage'?" >&2
    exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$DOWNLOAD_DIR/inloopid_termux_audit_$TIMESTAMP.txt"

{
    echo "=================================================="
    echo " InLoopID & Termux Environment Audit Report"
    echo " Generováno: $(date)"
    echo " Zařízení: Motorola Moto G86 (MediaTek Dimensity 7300)"
    echo "=================================================="
    echo ""

    echo "[1] SYSTÉMOVÉ INFORMACE"
    echo "--------------------------------------------------"
    uname -a
    echo "Termux Prefix: ${PREFIX:-N/A}"
    echo ""

    echo "[2] AKTUÁLNÍ ADRESÁŘ A GIT STATUS"
    echo "--------------------------------------------------"
    echo "Pracovní adresář: $(pwd)"
    if [ -d ".git" ]; then
        echo "--- Git Status ---"
        git status -s
        echo ""
        echo "--- Poslední commity ---"
        git log -n 5 --oneline
        echo ""
        echo "--- Remote ---"
        git remote -v
    else
        echo "Aktuální adresář není git repozitář."
    fi
    echo ""

    echo "[3] STRUKTURA PROJEKTU"
    echo "--------------------------------------------------"
    if command -v tree >/dev/null 2>&1; then
        tree -L 2 --dirsfirst -I 'target|.git|__pycache__'
    else
        find . -maxdepth 2 -not -path '*/.*' -not -path './target*'
    fi
    echo ""

    echo "[4] DOSTUPNÉ VÝVOJOVÉ NÁSTROJE (TOOLCHAIN)"
    echo "--------------------------------------------------"
    rustc --version 2>&1 || echo "rustc: nenalezeno"
    cargo --version 2>&1 || echo "cargo: nenalezeno"
    python3 --version 2>&1 || echo "python3: nenalezeno"
    pkg list-installed 2>/dev/null | grep -E 'rust|python|git|build-essential' || true

    echo ""
    echo "=================================================="
    echo " Konec reportu"
    echo "=================================================="
} > "$OUTPUT_FILE"

echo "==> Hotovo! Výsledek byl uložen do: $OUTPUT_FILE"
