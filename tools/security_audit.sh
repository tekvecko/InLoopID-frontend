#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "============================================="
echo " ZAHUJUJI BEZPEČNOSTNÍ AUDIT ZÁVISLOSTÍ"
echo "============================================="

# Kontrola a instalace pip-audit
if ! command -v pip-audit &> /dev/null; then
    echo "[Systém] Instaluji pip-audit..."
    pip install pip-audit --quiet
fi

echo -e "\n[1/2] Audit Python backendu (pip-audit):"
cd ~/InloopID/backend
# Spuštění auditu s ignorováním varování o zastaralých systémech, zaměření na CVE
pip-audit || echo "[Varování] Byly detekovány zranitelnosti v Python balíčcích!"

echo -e "\n[2/2] Audit Node.js frontendu (npm audit):"
cd ~/InloopID/frontend
# Zobrazení pouze produkčních zranitelností (ignoruje devDependencies)
npm audit --production || echo "[Varování] Byly detekovány zranitelnosti v NPM balíčcích!"

echo -e "\n============================================="
echo " AUDIT DOKONČEN"
echo "============================================="
