#!/bin/bash

# Cílová cesta do Android složky Download
DOWNLOAD_DIR="/storage/emulated/0/Download"
OUTPUT_FILE="$DOWNLOAD_DIR/inloopid_frontend_export.txt"

# Kontrola, zda existuje přístup k úložišti
if [ ! -d "$DOWNLOAD_DIR" ]; then
    echo "CHYBA: Složka $DOWNLOAD_DIR neexistuje!"
    echo "Ujisti se, že máš v Termuxu povolené úložiště příkazem: termux-setup-storage"
    exit 1
fi

echo "Generuji export projektu do $OUTPUT_FILE ..."

# Začátek zápisu do souboru
{
    echo "===================================================="
    echo " INLOOPID FRONTEND - PROJEKTOVÝ EXPORT"
    echo " Vygenerováno: $(date)"
    echo "===================================================="
    echo ""

    echo "--- 1. STRUKTURA ADRESÁŘŮ ---"
    if command -v tree &> /dev/null; then
        tree -I 'node_modules|dist|.git'
    else
        find . -maxdepth 3 -not -path '*/.*' -not -path './node_modules*'
    fi
    echo ""

    echo "--- 2. package.json ---"
    if [ -f "package.json" ]; then
        cat package.json
    else
        echo "Soubor nenalezen."
    fi
    echo ""

    echo "--- 3. vite.config.js ---"
    if [ -f "vite.config.js" ]; then
        cat vite.config.js
    else
        echo "Soubor nenalezen."
    fi
    echo ""

    echo "--- 4. ZDROJOVÉ SOUBORY (SRC) ---"
    for file in $(find src -type f); do
        echo "===================================================="
        echo " SOUBOR: $file"
        echo "===================================================="
        cat "$file"
        echo -e "\n\n"
    done

} > "$OUTPUT_FILE"

echo "HOTOVO! Soubor byl úspěšně uložen do: $OUTPUT_FILE"
