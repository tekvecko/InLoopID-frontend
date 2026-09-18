#!/usr/bin/env python3
import os

fp = os.path.expanduser("~/InloopID/frontend/src/components/LandingPage.jsx")

if os.path.exists(fp):
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Import komponenty
    if "ComplianceDashboard" not in content:
        import_stmt = "import { ComplianceDashboard } from './ComplianceDashboard';\n"
        content = content.replace("import React,", import_stmt + "import React,")

    # 2. Vložení ovládacího stavu a tlačítka nahoru do hlavičky (nebo navigace)
    # Rychlý hack: Pokud renderujeme LandingPage, vložíme tam i tuto komponentu podmíněně.
    # Upozornění: Toto je "non-invasive" regex injektáž.
    if "setShowCompliance" not in content:
        content = content.replace("const LandingPage = () => {", "const LandingPage = () => {\n  const [showCompliance, setShowCompliance] = React.useState(false);\n")
        
        button_html = """
        <div className="absolute top-4 right-4 z-50">
            <button onClick={() => setShowCompliance(!showCompliance)} className="bg-emerald-900/40 hover:bg-emerald-800 text-emerald-400 border border-emerald-700 px-4 py-2 rounded-xl font-bold text-sm transition-all shadow-lg">
                {showCompliance ? 'Zpět na portál' : 'Vstup pro Auditory (DPO)'}
            </button>
        </div>
        """
        content = content.replace('<div className="min-h-screen', button_html + '\n<div className="min-h-screen')
        
        render_logic = """
        {showCompliance ? (
            <div className="pt-20 px-4 max-w-7xl mx-auto"><ComplianceDashboard /></div>
        ) : (
        """
        content = content.replace('<main className="max-w-7xl', render_logic + '<main className="max-w-7xl')
        
        # Uzavření podmínky na konci souboru (před exportem)
        content = content.replace('</div>\n  );\n};', '</div>\n        )}\n    </div>\n  );\n};')

    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("[+] Tlačítko pro Auditory a ComplianceDashboard úspěšně vloženo na LandingPage.")
else:
    print("[-] Soubor LandingPage.jsx nenalezen.")
