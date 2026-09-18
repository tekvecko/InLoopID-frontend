#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "====================================================="
echo " KOMPILACE KRYPTOGRAFIE (S EXPLICITNÍM RUST TERČEM)"
echo "====================================================="

echo "[1/4] Pročišťuji případné zbytky po selhání..."
pip uninstall cryptography pyopenssl maturin -y 2>/dev/null || true

echo "[2/4] Zajišťuji systémové závislosti (Termux struktura)..."
pkg install clang rust binutils openssl libffi pkg-config make python -y

echo "[3/4] Konfiguruji prostředí pro kompilaci Rustu na Androidu..."
# Toto je kritický krok, který opravuje chybu 'rlib'
export CARGO_BUILD_TARGET="$(rustc -Vv | grep 'host' | awk '{print $2}')"
echo "Cílová architektura striktně nastavena na: $CARGO_BUILD_TARGET"

echo "[4/4] Zahajuji tvrdou kompilaci (MŮŽE TRVAT 5 AŽ 10 MINUT)..."
# Parametr --no-binary zaručí kompilaci přímo pro Váš Moto G84 procesor
pip install cryptography pyOpenSSL --no-binary cryptography

echo "====================================================="
echo " KOMPILACE ÚSPĚŠNĚ DOKONČENA"
echo "====================================================="
