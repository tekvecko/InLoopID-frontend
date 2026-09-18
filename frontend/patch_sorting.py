import re
import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha
with open(file_path + ".bak_sorting", 'w') as f:
    f.write(content)

# 2. Přidání chybějících ikonek (Briefcase pro pozici, Filter pro řazení)
if "Briefcase" not in content[:content.find("from 'lucide-react'")]:
    content = re.sub(r"import \{([^}]+)\} from 'lucide-react';", r"import {\1, Briefcase, Filter} from 'lucide-react';", content)

# 3. Přidání stavu pro řazení
state_pattern = r"const \[isProcessing, setIsProcessing\] = useState\(false\);"
new_state = "const [isProcessing, setIsProcessing] = useState(false);\n  const [sortOrder, setSortOrder] = useState('default');"
content = content.replace(state_pattern, new_state)

# 4. Nahrazení Parseru a Helperů (Až po FinalSubmit)
parser_pattern = r"(?<=// --- SUPER CHYTRÝ PARSER).*?(?=const handleFinalSubmit = async \(\) => \{)"
new_logic = """ (Jména, E-mail, Datum, URL) ---
  const handleParseText = () => {
      const lines = bulkText.split(/\\r?\\n/).filter(line => line.trim().length > 0);
      const results = [];
      const seenEmails = new Set();

      lines.forEach((line) => {
          const cols = line.split(/[\\t;,]/).map(c => c.trim().replace(/^"|"$/g, ''));
          let foundEmail = null; let foundUrl = null; let foundDate = null;
          let stringParts = [];

          cols.forEach(col => { 
              if (/^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,6}$/.test(col)) foundEmail = col.toLowerCase();
              else if (/^https?:\\/\\//.test(col)) foundUrl = col;
              else if (/\\b(\\d{1,2}\\.\\s?\\d{1,2}\\.\\s?\\d{4}|\\d{4}-\\d{2}-\\d{2})\\b/.test(col)) foundDate = col;
              else if (col.length > 1 && !/^\\d+$/.test(col)) stringParts.push(col); 
          });

          if (foundEmail && !seenEmails.has(foundEmail)) {
              seenEmails.add(foundEmail);
              
              let firstName = ''; let lastName = ''; let position = '';
              // Záchrana pozice do samostatné proměnné
              if (stringParts.length >= 3) { 
                  firstName = stringParts[0]; lastName = stringParts[1]; position = stringParts.slice(2).join(' ');
              } else if (stringParts.length === 2) {
                  firstName = stringParts[0]; lastName = stringParts[1];
              } else if (stringParts.length === 1) {
                  const splitName = stringParts[0].split(' ');
                  if (splitName.length >= 2) { firstName = splitName[0]; lastName = splitName.slice(1).join(' '); }
                  else { lastName = stringParts[0]; }
              }

              // ID generujeme, aby řazení nerozbilo updaty políček
              results.push({ 
                  id: Date.now().toString(36) + Math.random().toString(36).substring(2),
                  email: foundEmail, firstName, lastName, position, startDate: foundDate || '', 
                  selected: true, contractUrl: foundUrl || '', contractFileName: '', contractFileBase64: '' 
              });
          }
      });
      setParsedCandidates(results); setImportStep(2); setSortOrder('default');
  };

  const handleAttachFile = (id, e) => {
      const file = e.target.files[0]; if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
          setParsedCandidates(prev => prev.map(c => c.id === id ? { ...c, contractFileName: file.name, contractFileBase64: evt.target.result, contractUrl: '' } : c));
      }; reader.readAsDataURL(file);
  };

  const updateCand = (id, field, value) => { 
      setParsedCandidates(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c)); 
  };

  // --- LOGIKA ŘAZENÍ ---
  const getProbScore = (c) => (!c.firstName || !c.lastName || !c.startDate || !c.email || (!c.contractUrl && !c.contractFileName)) ? 1 : 0;
  
  const parseDateVal = (d) => {
      if (!d) return 0;
      let p = d.split(/[. -]/).filter(Boolean);
      if (p.length === 3) return p[0].length === 4 ? new Date(p[0], p[1]-1, p[2]).getTime() : new Date(p[2], p[1]-1, p[0]).getTime();
      return 0;
  };

  const getSortedCandidates = () => {
      let arr = [...parsedCandidates];
      switch(sortOrder) {
          case 'lastName_asc': return arr.sort((a,b) => a.lastName.localeCompare(b.lastName));
          case 'lastName_desc': return arr.sort((a,b) => b.lastName.localeCompare(a.lastName));
          case 'email_asc': return arr.sort((a,b) => a.email.localeCompare(b.email));
          case 'email_desc': return arr.sort((a,b) => b.email.localeCompare(a.email));
          case 'date_desc': return arr.sort((a,b) => parseDateVal(b.startDate) - parseDateVal(a.startDate));
          case 'date_asc': return arr.sort((a,b) => parseDateVal(a.startDate) - parseDateVal(b.startDate));
          case 'pos_asc': return arr.sort((a,b) => a.position.localeCompare(b.position));
          case 'pos_desc': return arr.sort((a,b) => b.position.localeCompare(a.position));
          case 'prob_first': return arr.sort((a,b) => getProbScore(b) - getProbScore(a));
          case 'prob_last': return arr.sort((a,b) => getProbScore(a) - getProbScore(b));
          default: return arr;
      }
  };

  """
content = re.sub(parser_pattern, lambda m: new_logic, content, flags=re.DOTALL)

# 5. Nahrazení Krok 2 UI (Přidání filtru, pozice a varovných stylů)
ui_pattern = r"\{activeTab === 'bulk' && importStep === 2 && \(\s*<div className=\"bg-slate-900.*?(?=\{/\* TAB 2)"
new_ui = """{activeTab === 'bulk' && importStep === 2 && (
            <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 animate-fade-in">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                    <h2 className="text-2xl font-bold flex items-center gap-3"><CheckCircle className="text-emerald-500"/> Krok 2: Připojení smluv a validace dat</h2>
                    <div className="flex items-center gap-4 w-full md:w-auto">
                        <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-3 focus-within:border-blue-500">
                            <Filter size={16} className="text-slate-400" />
                            <select value={sortOrder} onChange={e => setSortOrder(e.target.value)} className="bg-transparent text-sm font-bold text-white outline-none px-3 py-2 cursor-pointer appearance-none">
                                <option value="default">Výchozí řazení</option>
                                <option value="prob_first">Problémové &rarr; Bezproblémů</option>
                                <option value="prob_last">Bezproblémů &rarr; Problémové</option>
                                <option value="lastName_asc">Příjmení A &rarr; Z</option>
                                <option value="lastName_desc">Příjmení Z &rarr; A</option>
                                <option value="email_asc">E-mail A &rarr; Z</option>
                                <option value="email_desc">E-mail Z &rarr; A</option>
                                <option value="pos_asc">Pozice A &rarr; Z</option>
                                <option value="pos_desc">Pozice Z &rarr; A</option>
                                <option value="date_desc">Nástup: Nejnovější</option>
                                <option value="date_asc">Nástup: Nejstarší</option>
                            </select>
                        </div>
                        <button onClick={() => setImportStep(1)} className="text-blue-400 font-bold hover:text-white transition-colors text-sm whitespace-nowrap">&larr; Zpět</button>
                    </div>
                </div>
                
                <div className="max-h-[550px] overflow-y-auto space-y-4 mb-6 pr-2">
                    {getSortedCandidates().map((cand) => {
                        const hasProblem = getProbScore(cand) > 0;
                        return (
                        <div key={cand.id} className={`p-5 rounded-2xl border transition-colors ${!cand.selected ? 'bg-slate-950/50 border-slate-800 opacity-50' : hasProblem ? 'bg-rose-950/20 border-rose-900/50' : 'bg-slate-950 border-slate-700'}`}>
                            <div className="flex items-start gap-4 mb-4">
                                <button onClick={() => updateCand(cand.id, 'selected', !cand.selected)} className="mt-1">
                                    {cand.selected ? <CheckSquare className="text-blue-500" size={24}/> : <Square className="text-slate-600" size={24}/>}
                                </button>
                                
                                <div className="grid grid-cols-1 md:grid-cols-5 gap-3 w-full">
                                    <div className={`flex bg-slate-900 border rounded-lg overflow-hidden focus-within:border-blue-500 ${!cand.firstName ? 'border-rose-500/50' : 'border-slate-800'}`}>
                                        <div className="bg-slate-800 px-3 flex items-center"><User size={14} className="text-slate-400"/></div>
                                        <input type="text" value={cand.firstName} onChange={(e) => updateCand(cand.id, 'firstName', e.target.value)} placeholder="Jméno" className="w-full bg-transparent px-3 py-2 text-sm outline-none font-bold" />
                                    </div>
                                    <div className={`flex bg-slate-900 border rounded-lg overflow-hidden focus-within:border-blue-500 ${!cand.lastName ? 'border-rose-500/50' : 'border-slate-800'}`}>
                                        <div className="bg-slate-800 px-3 flex items-center"><User size={14} className="text-slate-400"/></div>
                                        <input type="text" value={cand.lastName} onChange={(e) => updateCand(cand.id, 'lastName', e.target.value)} placeholder="Příjmení" className="w-full bg-transparent px-3 py-2 text-sm outline-none font-bold" />
                                    </div>
                                    <div className="flex bg-slate-900 border border-slate-800 rounded-lg overflow-hidden focus-within:border-blue-500">
                                        <div className="bg-slate-800 px-3 flex items-center"><Briefcase size={14} className="text-slate-400"/></div>
                                        <input type="text" value={cand.position} onChange={(e) => updateCand(cand.id, 'position', e.target.value)} placeholder="Pozice" className="w-full bg-transparent px-3 py-2 text-sm outline-none" />
                                    </div>
                                    <div className={`flex bg-slate-900 border rounded-lg overflow-hidden focus-within:border-blue-500 ${!cand.startDate ? 'border-rose-500/50' : 'border-slate-800'}`}>
                                        <div className="bg-slate-800 px-3 flex items-center"><Calendar size={14} className="text-slate-400"/></div>
                                        <input type="text" value={cand.startDate} onChange={(e) => updateCand(cand.id, 'startDate', e.target.value)} placeholder="Nástup (DD.MM.RRRR)" className="w-full bg-transparent px-3 py-2 text-sm outline-none" />
                                    </div>
                                    <div className={`flex bg-slate-900 border rounded-lg overflow-hidden focus-within:border-blue-500 ${!cand.email ? 'border-rose-500/50' : 'border-slate-800'}`}>
                                        <div className="bg-slate-800 px-3 flex items-center"><span className="text-slate-400 font-bold text-xs">@</span></div>
                                        <input type="email" value={cand.email} onChange={(e) => updateCand(cand.id, 'email', e.target.value)} placeholder="E-mail" className="w-full bg-transparent px-3 py-2 text-sm outline-none font-mono text-slate-300" />
                                    </div>
                                </div>
                            </div>
                            
                            {cand.selected && (
                                <div className="pl-10 space-y-2">
                                    <label className={`text-xs font-bold uppercase tracking-wider ${(!cand.contractUrl && !cand.contractFileName) ? 'text-rose-400' : 'text-slate-500'}`}>Historická smlouva {(!cand.contractUrl && !cand.contractFileName) && '(Chybí!)'}</label>
                                    <div className="flex items-center gap-3">
                                        <div className={`flex-1 flex items-center bg-slate-900 border rounded-xl px-3 focus-within:border-blue-500 transition-colors ${(!cand.contractUrl && !cand.contractFileName) ? 'border-rose-900/50' : 'border-slate-700'}`}>
                                            <LinkIcon size={16} className="text-slate-500" />
                                            <input type="text" placeholder="URL odkaz na cloud..." value={cand.contractUrl} onChange={(e) => updateCand(cand.id, 'contractUrl', e.target.value)} disabled={!!cand.contractFileName} className="w-full bg-transparent px-3 py-2 text-sm outline-none disabled:opacity-50" />
                                        </div>
                                        <span className="text-slate-500 text-sm font-bold">NEBO</span>
                                        <label className={`cursor-pointer px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 border transition-colors ${cand.contractFileName ? 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30' : 'bg-slate-800 text-white border-slate-700 hover:bg-slate-700'}`}>
                                            <Paperclip size={16}/> {cand.contractFileName ? cand.contractFileName : 'Nahrát soubor'}
                                            <input type="file" className="hidden" accept=".pdf,.doc,.docx,.txt" onChange={(e) => handleAttachFile(cand.id, e)} />
                                        </label>
                                        {cand.contractFileName && ( <button onClick={() => { updateCand(cand.id, 'contractFileName', ''); updateCand(cand.id, 'contractFileBase64', ''); }} className="text-rose-400 hover:text-rose-300 p-2"><X size={18}/></button> )}
                                    </div>
                                </div>
                            )}
                        </div>
                    )})}
                </div>
                <button onClick={handleFinalSubmit} disabled={isProcessing} className="w-full py-5 bg-emerald-600 hover:bg-emerald-500 rounded-xl font-bold transition-colors text-lg flex items-center justify-center gap-2">
                    <Lock size={20} /> {isProcessing ? 'Šifruji a migruji data...' : 'Zapsat údaje a odeslat pozvánky'}
                </button>
            </div>
        )}
        
        """
content = re.sub(ui_pattern, lambda m: new_ui, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Dokončeno! Filtr řazení, vizualizace chyb a pozice úspěšně přidány.")
