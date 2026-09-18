#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "====================================================="
echo " OPRAVA KRYPTOGRAFICKÉHO STACKU"
echo "====================================================="

echo "[1/2] Instaluji nativní, předkompilované jádro pro Termux..."
pkg install python-cryptography -y

echo "[2/2] Instaluji komunikační vrstvu přes pip..."
pip install pyOpenSSL

echo "====================================================="
echo " OPRAVA DOKONČENA"
echo "====================================================="
