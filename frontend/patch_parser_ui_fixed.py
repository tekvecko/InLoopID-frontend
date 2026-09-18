import re
import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Nový JavaScriptový kód parseru
parser_pattern = r"const handleParseText = \(\) => \{.*?(?=\s*const handleAttachFile =)"
new_parser = """const handleParseText = () => {
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
              else if (col.length > 1 && !/^\\d+$/.test(col)) stringParts.push(col); // Ignorujeme čistá čísla jako ID
          });

          if (foundEmail && !seenEmails.has(foundEmail)) {
              seenEmails.add(foundEmail);
              
              let firstName = ''; let lastName = '';
              // Zastavíme vysavač: vezmeme jen první dva textové sloupce
              if (stringParts.length >= 2) { 
                  firstName = stringParts[0]; 
                  lastName = stringParts[1]; 
              }
              else if (stringParts.length === 1) {
                  const splitName = stringParts[0].split(' ');
                  if (splitName.length >= 2) { firstName = splitName[0]; lastName = splitName.slice(1).join(' '); }
                  else { lastName = stringParts[0]; }
              }

              results.push({ email: foundEmail, firstName, lastName, startDate: foundDate || '', selected: true, contractUrl: foundUrl || '', contractFileName: '', contractFileBase64: '' });
          }
      });
      setParsedCandidates(results); setImportStep(2);
  };"""

# 2. BEZPEČNÉ NAHRAZENÍ pomocí lambda funkce
content = re.sub(parser_pattern, lambda m: new_parser, content, flags=re.DOTALL)

# 3. Změna statického rozpisu emailu na editovatelný input s ikonkou @
ui_pattern = r"<div className=\"flex items-center px-2\">\s*<span className=\"font-mono text-sm text-slate-400 truncate\" title=\{cand\.email\}>\{cand\.email\}</span>\s*</div>"
new_ui = """<div className="flex bg-slate-900 border border-slate-800 rounded-lg overflow-hidden focus-within:border-blue-500">
                                        <div className="bg-slate-800 px-3 flex items-center"><span className="text-slate-400 font-bold text-xs">@</span></div>
                                        <input type="email" value={cand.email} onChange={(e) => updateCand(idx, 'email', e.target.value)} placeholder="E-mail" className="w-full bg-transparent px-3 py-2 text-sm outline-none font-mono text-slate-300" />
                                    </div>"""

content = re.sub(ui_pattern, lambda m: new_ui, content)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Úspěšně dokončeno: Parser je nyní přesnější a e-mail plně editovatelný!")
