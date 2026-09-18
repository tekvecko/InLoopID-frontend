import re

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# Záloha
with open(file_path + ".bak_file_input", 'w') as f:
    f.write(content)

# Najdeme sekci Krok 1 a vložíme tam nahrávání
old_krok1 = """<h2 className="text-2xl font-bold mb-2 flex items-center gap-3"><UploadCloud className="text-blue-500"/> Krok 1: Extrakce dat</h2>
              <p className="text-slate-400 mb-6 text-sm">Vložte data (např. export z Excelu). Parser automaticky najde Jména, Nástup, E-mail a Odkaz na smlouvu.</p>
              <textarea value={bulkText} onChange={e => setBulkText(e.target.value)}"""

new_krok1 = """<h2 className="text-2xl font-bold mb-2 flex items-center gap-3"><UploadCloud className="text-blue-500"/> Krok 1: Extrakce dat</h2>
              <p className="text-slate-400 mb-4 text-sm">Nahrajte CSV soubor nebo vložte data ručně.</p>
              <label className="flex items-center justify-center gap-3 w-full py-4 mb-4 bg-slate-800 hover:bg-slate-700 border-2 border-dashed border-slate-600 rounded-xl cursor-pointer transition-colors text-blue-400 font-bold">
                  <UploadCloud size={20}/> Vybrat CSV soubor z disku
                  <input type="file" accept=".csv,.txt" className="hidden" onChange={handleFileUpload} />
              </label>
              <textarea value={bulkText} onChange={e => setBulkText(e.target.value)}"""

content = content.replace(old_krok1, new_krok1)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] CSV upload zóna úspěšně obnovena.")
