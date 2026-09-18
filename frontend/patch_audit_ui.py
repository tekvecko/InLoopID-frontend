import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha souboru před změnou
with open(file_path + ".bak_audit", 'w') as f:
    f.write(content)

# 2. Vložení spouštěcí funkce
insert_func = """  const fetchContracts = async () => { try { setIssuedContracts((await safeFetch(`${BACKEND_URL}/hr/contracts?tenant_id=${tenantId.trim()}`)).data); } catch(e) { } };

  const handleDownloadAudit = () => {
      window.open(`${BACKEND_URL}/hr/compliance-report/pdf?tenant_id=${tenantId.trim()}`, '_blank');
  };
"""
content = content.replace(
    "const fetchContracts = async () => { try { setIssuedContracts((await safeFetch(`${BACKEND_URL}/hr/contracts?tenant_id=${tenantId.trim()}`)).data); } catch(e) { } };", 
    insert_func
)

# 3. Vložení samotného tlačítka do UI
old_header = """<h3 className="text-xl font-bold mb-6 flex items-center gap-3"><AlertTriangle className="text-blue-500"/> Detailní monitoring dokumentů</h3>"""
new_header = """<div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold flex items-center gap-3"><AlertTriangle className="text-blue-500"/> Detailní monitoring dokumentů</h3>
                        <button onClick={handleDownloadAudit} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-blue-600 text-white rounded-xl text-sm font-bold transition-colors">
                            <FileText size={16}/> Stáhnout certifikovaný audit
                        </button>
                    </div>"""
content = content.replace(old_header, new_header)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Tlačítko Auditu vloženo do Právního Radaru.")
