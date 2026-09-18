#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - KRIZOVÁ OBNOVA FRONTENDU (LANDINGPAGE.JSX)"
echo "=========================================================="

LATEST_BACKUP=$(ls -t ~/InLoopID_FullSnapshot_*.tar.gz | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "[!] KRITICKÁ CHYBA: Nebyla nalezena záloha InLoopID_FullSnapshot!"
    exit 1
fi

echo "[*] 1/2 Rozbaluji nepoškozený LandingPage.jsx ze zálohy..."
tar -xzf "$LATEST_BACKUP" -C ~/ InloopID/frontend/src/components/LandingPage.jsx

echo "[*] 2/2 Aplikuji precizní injektáž (izolováno na hlavní komponentu)..."
python3 << 'PY_EOF'
import os
import re

fp = os.path.expanduser("~/InloopID/frontend/src/components/LandingPage.jsx")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Bezpečné vložení importu na začátek
if "ComplianceDashboard" not in content:
    content = "import { ComplianceDashboard } from './ComplianceDashboard';\n" + content

# 2. Striktní izolace komponenty LandingPage
target_def = "export const LandingPage = () => {"
parts = content.split(target_def)

if len(parts) == 2:
    pre_landing = parts[0]
    landing_code = parts[1]

    # Vložení stavové proměnné
    state_def = "\n  const [showCompliance, setShowCompliance] = React.useState(false);\n"
    landing_code = state_def + landing_code

    # Vložení absolutního tlačítka do hlavního obalu
    btn = """
      <div className="absolute top-4 right-4 z-50">
          <button onClick={() => setShowCompliance(!showCompliance)} className="bg-emerald-900/80 hover:bg-emerald-800 text-emerald-400 border border-emerald-700 px-4 py-2 rounded-xl font-bold text-sm transition-all shadow-lg backdrop-blur-md">
              {showCompliance ? 'Zpět na portál' : 'Vstup pro Auditory (DPO)'}
          </button>
      </div>
"""
    landing_code = landing_code.replace('<div className="min-h-screen', f'<div className="min-h-screen relative">{btn}', 1)

    # Obalení hlavní (<main>) sekce ternárním operátorem
    main_replacement = '{showCompliance ? (\n        <div className="pt-24 px-4 max-w-7xl mx-auto relative z-10"><ComplianceDashboard /></div>\n      ) : (\n        <main'
    landing_code = landing_code.replace('<main', main_replacement, 1)

    # Bezpečné uzavření ternárního operátoru na úplném konci souboru pomocí Regexu
    landing_code = re.sub(r'</div>\s*\)\s*;\s*}\s*;?\s*$', '</div>\n      )}\n    </div>\n  );\n};', landing_code)

    # Zpětné složení souboru
    content = pre_landing + target_def + landing_code

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)
PY_EOF

echo "[*] Obnova dokončena. Struktura JSX je zacelena."
echo "=========================================================="
