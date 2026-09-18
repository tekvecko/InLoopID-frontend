#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "[1/3] Čistím vše, co pip rozbil..."
pip uninstall cryptography pyopenssl maturin -y 2>/dev/null || true

echo "[2/3] Instaluji binární jádro z APT (zaručeně funkční)..."
pkg install python-cryptography -y

echo "[3/3] Instaluji pyOpenSSL bez kontroly závislostí (TOTO JE KLÍČOVÉ)..."
# Flag --no-deps je zásadní - říká pipu: "Nesahej na cryptography, tu už mám"
pip install pyOpenSSL --no-deps

echo "====================================================="
echo " ZÁVĚREČNÝ TEST:"
python3 -c "import cryptography; import OpenSSL; print('IMPORT OK - JEDEME!')"
echo "====================================================="
