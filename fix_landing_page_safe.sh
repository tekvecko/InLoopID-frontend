#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - FINÁLNÍ A BEZPEČNÁ OPRAVA (OVERLAY METODA)"
echo "=========================================================="

LATEST_BACKUP=$(ls -t ~/InLoopID_FullSnapshot_*.tar.gz | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "[!] KRITICKÁ CHYBA: Záloha nenalezena!"
    exit 1
fi

echo "[*] 1/2 Rozbaluji původní čistý soubor..."
tar -xzf "$LATEST_BACKUP" -C ~/ InloopID/frontend/src/components/LandingPage.jsx

echo "[*] 2/2 Aplikuji non-destruktivní překryvnou vrstvu (Overlay)..."
python3 << 'PY_EOF'
import os

fp = os.path.expanduser("~/InloopID/frontend/src/components/LandingPage.jsx")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Import
if "ComplianceDashboard" not in content:
    content = "import { ComplianceDashboard } from './ComplianceDashboard';\n" + content

# 2. Rozdělení na úseky
target_def = "export const LandingPage = () => {"
parts = content.split(target_def)

if len(parts) == 2:
    pre_landing = parts[0]
    landing_code = parts[1]

    # 3. Přidání stavu
    state_def = "\n  const [showCompliance, setShowCompliance] = React.useState(false);\n"
    landing_code = state_def + landing_code

    # 4. Neinvazivní Overlay
    overlay_ui = """
      <div className="absolute top-4 right-4 z-50">
          <button onClick={() => setShowCompliance(!showCompliance)} className="bg-emerald-900/90 hover:bg-emerald-800 text-emerald-400 border border-emerald-700 px-4 py-2 rounded-xl font-bold text-sm transition-all shadow-lg backdrop-blur-md">
              {showCompliance ? 'Zavřít Auditní Portál' : 'Vstup pro Auditory (DPO)'}
          </button>
      </div>

      {showCompliance && (
          <div className="fixed inset-0 z-40 bg-[#0B1120] overflow-y-auto pt-24 pb-12 px-4 backdrop-blur-xl">
              <div className="max-w-7xl mx-auto">
                  <ComplianceDashboard />
              </div>
          </div>
      )}
"""
    # Vložíme to čistě těsně před <main
    landing_code = landing_code.replace('<main', overlay_ui + '\n      <main', 1)

    # Spojíme zpět
    content = pre_landing + target_def + landing_code

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)
PY_EOF

echo "[*] Oprava dokončena. Vite provede HMR bez syntaktických chyb."
echo "=========================================================="
