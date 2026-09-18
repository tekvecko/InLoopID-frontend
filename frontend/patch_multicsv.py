import os
import re

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha
with open(file_path + ".bak_multicsv", 'w') as f:
    f.write(content)

# 2. OPRAVA BÍLÉ STRÁNKY: Vrácení chybějící ikony CheckCircle do importů
if "CheckCircle" not in content[:content.find("from 'lucide-react'")]:
    content = re.sub(r"import \{([^}]+)\} from 'lucide-react';", r"import {\1, CheckCircle} from 'lucide-react';", content)

# 3. VYLEPŠENÍ: Přepis funkce pro paralelní čtení více souborů
old_func = """  const handleCsvUpload = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
          setBulkText(evt.target.result);
          notify.success("Soubor úspěšně načten. Můžete zkontrolovat data.");
      };
      reader.readAsText(file);
  };"""

new_func = """  const handleCsvUpload = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      
      // Vytvoříme pole asynchronních čtení pro každý soubor
      const readPromises = files.map(file => {
          return new Promise((resolve) => {
              const reader = new FileReader();
              reader.onload = (evt) => resolve(evt.target.result);
              reader.readAsText(file);
          });
      });
      
      // Počkáme na načtení všech souborů
      const results = await Promise.all(readPromises);
      
      // Sloučíme je a přidáme k již existujícímu textu
      setBulkText(prev => {
          const newText = prev ? prev + "\\n" + results.join("\\n") : results.join("\\n");
          return newText;
      });
      
      notify.success(`Úspěšně načteno ${files.length} souborů.`);
      e.target.value = null; // Reset inputu pro další použití
  };"""

content = content.replace(old_func, new_func)

# 4. Úprava HTML inputu a popisků pro Multi-File
old_input = '<input type="file" accept=".csv,.txt" className="hidden" onChange={handleCsvUpload} />'
new_input = '<input type="file" accept=".csv,.txt" multiple className="hidden" onChange={handleCsvUpload} />'
content = content.replace(old_input, new_input)

old_span = '<span className="text-slate-300 font-bold text-lg group-hover:text-white transition-colors">Nahrát .CSV nebo .TXT export</span>'
new_span = '<span className="text-slate-300 font-bold text-lg group-hover:text-white transition-colors">Nahrát .CSV nebo .TXT soubory</span>'
content = content.replace(old_span, new_span)

old_hint = '<span className="text-slate-500 text-xs">Klikněte pro výběr souboru z vašeho zařízení</span>'
new_hint = '<span className="text-slate-500 text-xs">Klikněte pro výběr jednoho nebo více souborů najednou</span>'
content = content.replace(old_hint, new_hint)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Hotovo: Pád aplikace opraven a nahrávání více souborů (multiple) bylo aktivováno!")
