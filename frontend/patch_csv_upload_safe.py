import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Povinná záloha pro případný rollback
with open(file_path + ".bak_csv", 'w') as f:
    f.write(content)

# 2. Vložení nové JavaScriptové logiky pro čtení lokálních souborů
func_insert = """
  // --- LOKÁLNÍ ČTENÍ CSV SOUBORŮ ---
  const handleCsvUpload = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
          setBulkText(evt.target.result);
          notify.success("Soubor úspěšně načten. Můžete zkontrolovat data.");
      };
      reader.readAsText(file);
  };

  // --- SUPER CHYTRÝ PARSER (Jména, E-mail, Datum, URL) ---"""

if "// --- SUPER CHYTRÝ PARSER (Jména, E-mail, Datum, URL) ---" in content:
    content = content.replace("  // --- SUPER CHYTRÝ PARSER (Jména, E-mail, Datum, URL) ---", func_insert)
else:
    print("[-] Chyba: Nemohu najít místo pro logiku parseru.")

# 3. Přepis starého (rozbitého) UI za novou vizuální Dropzone
old_ui = """<p className="text-slate-400 mb-4 text-sm">Nahrajte CSV soubor nebo vložte data ručně.</p>
              <label className="flex items-center justify-center gap-3 w-full py-4 mb-4 bg-slate-800 hover:bg-slate-700 border-2 border-dashed border-slate-600 rounded-xl cursor-pointer transition-colors text-blue-400 font-bold">
                  <UploadCloud size={20}/> Vybrat CSV soubor z disku
                  <input type="file" accept=".csv,.txt" className="hidden" onChange={handleFileUpload} />
              </label>
              <textarea value={bulkText} onChange={e => setBulkText(e.target.value)} className="w-full h-40 bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-sm outline-none focus:border-blue-500 leading-relaxed" placeholder="Jan; Novák; jan.novak@firma.cz; 1. 5. 2023; https://cloud.cz/smlouva.pdf" />"""

new_ui = """<p className="text-slate-400 mb-6 text-sm">Nahrajte exportní CSV/TXT soubor nebo vložte data ručně.</p>
              
              <div className="flex flex-col gap-4 mb-6">
                  <label className="flex flex-col items-center justify-center gap-3 w-full py-8 border-2 border-dashed border-slate-700 hover:border-blue-500 bg-slate-950/50 hover:bg-slate-900 rounded-2xl cursor-pointer transition-all group">
                      <UploadCloud size={36} className="text-slate-500 group-hover:text-blue-500 transition-colors" />
                      <span className="text-slate-300 font-bold text-lg group-hover:text-white transition-colors">Nahrát .CSV nebo .TXT export</span>
                      <span className="text-slate-500 text-xs">Klikněte pro výběr souboru z vašeho zařízení</span>
                      <input type="file" accept=".csv,.txt" className="hidden" onChange={handleCsvUpload} />
                  </label>
                  
                  <div className="flex items-center gap-4 text-slate-600 text-xs font-bold uppercase tracking-widest">
                      <hr className="flex-1 border-slate-800"/>nebo vložit text ručně<hr className="flex-1 border-slate-800"/>
                  </div>
                  
                  <textarea value={bulkText} onChange={e => setBulkText(e.target.value)} className="w-full h-32 bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-sm outline-none focus:border-blue-500 leading-relaxed" placeholder="Jan; Novák; jan.novak@firma.cz; 1. 5. 2023; https://cloud.cz/smlouva.pdf" />
              </div>"""

if old_ui in content:
    content = content.replace(old_ui, new_ui)
    with open(file_path, 'w') as f:
        f.write(content)
    print("[+] Hotovo: Chybějící logika opravena a nová Dropzone zóna úspěšně přidána.")
else:
    print("[-] Chyba: Nemohu najít původní UI část pro nahrazení.")

