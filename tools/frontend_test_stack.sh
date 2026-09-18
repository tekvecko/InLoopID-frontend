#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "[Systém] Spouštím diagnostiku a čištění frontend stacku..."

cd ~/InloopID/frontend || { echo "[Chyba] Adresář frontend nenalezen!"; exit 1; }

echo "[Systém] Čistím Vite cache pro odstranění chyb kompilace..."
rm -rf node_modules/.vite
rm -rf dist

echo "[Systém] Zajišťuji instalaci chybějících závislostí..."
npm install

echo "[Systém] Spouštím vývojový server (naslouchá na lokální síti)..."
npm run dev -- --host
