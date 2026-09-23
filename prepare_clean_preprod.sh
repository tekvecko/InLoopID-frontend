#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR=".preprod_archive_${TIMESTAMP}"

echo "[*] Vytvářím archivační složku: ${ARCHIVE_DIR}"
mkdir -p "${ARCHIVE_DIR}/root" "${ARCHIVE_DIR}/backend" "${ARCHIVE_DIR}/frontend" "${ARCHIVE_DIR}/patches"

echo "[*] Archivuji dočasné a záložní soubory z kořenového adresáře..."
find . -maxdepth 1 -type f \( \
    -name "*.bak*" -o \
    -name "*.fixed*" -o \
    -name "*.patch" -o \
    -name "*.tmp" -o \
    -name "*.corrupted" -o \
    -name "*.log" -o \
    -name "run_output.txt" -o \
    -name "optimization_run.txt" \
\) -exec mv {} "${ARCHIVE_DIR}/root/" \;

echo "[*] Archivuji jednoúčelové patch skripty..."
find . -maxdepth 1 -type f -name "patch_*.py" -exec mv {} "${ARCHIVE_DIR}/patches/" \;

echo "[*] Archivuji zálohy a logy z backendu..."
if [ -d "backend" ]; then
    find backend/ -maxdepth 1 -type f \( -name "*.bak*" -o -name "*.corrupted" -o -name "*.log" -o -name "*.error_bak" \) -exec mv {} "${ARCHIVE_DIR}/backend/" \; 2>/dev/null || true
    find backend/ -maxdepth 1 -type f -name "patch_*.py" -exec mv {} "${ARCHIVE_DIR}/patches/" \; 2>/dev/null || true
fi

echo "[*] Archivuji zálohy a logy z frontendu a komponent..."
if [ -d "frontend" ]; then
    find frontend/ -maxdepth 1 -type f \( -name "*.bak*" -o -name "*.log" \) -exec mv {} "${ARCHIVE_DIR}/frontend/" \; 2>/dev/null || true
    find frontend/ -maxdepth 1 -type f -name "patch_*.py" -exec mv {} "${ARCHIVE_DIR}/patches/" \; 2>/dev/null || true
    find frontend/src/components/ -maxdepth 1 -type f -name "*.bak*" -exec mv {} "${ARCHIVE_DIR}/frontend/" \; 2>/dev/null || true
    find frontend/src/utils/ -maxdepth 1 -type f -name "*.bak*" -exec mv {} "${ARCHIVE_DIR}/frontend/" \; 2>/dev/null || true
fi

echo "[*] Čistím Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "[+] Úklid dokončen. Archivované soubory jsou uloženy v: ${ARCHIVE_DIR}"
echo "[*] Spouštím kontrolu integrity..."
if [ -f "verify_integrity.py" ]; then
    python3 verify_integrity.py || echo "[!] Varování: verify_integrity.py zachytil odchylky."
fi
