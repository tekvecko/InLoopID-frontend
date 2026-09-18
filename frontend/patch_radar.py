import re

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

with open(file_path, 'r') as f:
    content = f.read()

# 1. Záloha souboru
with open(file_path + ".bak_radar", 'w') as f:
    f.write(content)

# 2. Bezpečné přidání chybějící ikony FileSignature do importů (pokud tam není)
if 'FileSignature' not in content:
    content = re.sub(
        r"import \{([^}]+)\} from 'lucide-react';", 
        r"import {\1, FileSignature} from 'lucide-react';", 
        content
    )

# 3. Nalezení a přepis starého, osekaného Radaru
old_radar_pattern = r"\{activeTab === 'radar' && \(\<div className=\"grid grid-cols-3 gap-6 animate-fade-in\"\>.*?\</div\>\)\}"

new_radar_code = """{activeTab === 'radar' && (
            <div className="space-y-6 animate-fade-in">
                {/* Vrchní KPI Karty */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 flex flex-col items-center justify-center shadow-xl">
                        <ShieldCheck className="text-emerald-500 mb-2" size={28} />
                        <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Nedotknutelné</h3>
                        <p className="text-4xl font-extrabold text-emerald-500 mt-2">{radarData.safe}</p>
                    </div>
                    <div className="bg-slate-900 p-6 rounded-3xl border border-blue-900 flex flex-col items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.15)] relative overflow-hidden">
                        <div className="absolute top-0 w-full h-1 bg-blue-500"></div>
                        <AlertTriangle className="text-blue-400 mb-2" size={28} />
                        <h3 className="text-blue-400 text-xs font-bold uppercase tracking-wider">V ochranné lhůtě</h3>
                        <p className="text-4xl font-extrabold text-white mt-2">{radarData.withdrawal_risk}</p>
                    </div>
                    <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 flex flex-col items-center justify-center shadow-xl">
                        <FileSignature className="text-amber-500 mb-2" size={28} />
                        <h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Čeká na podpis</h3>
                        <p className="text-4xl font-extrabold text-white mt-2">{radarData.pending_signatures}</p>
                    </div>
                </div>

                {/* Seznam monitorovaných dokumentů */}
                <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-xl">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-3"><AlertTriangle className="text-blue-500"/> Detailní monitoring dokumentů</h3>
                    <div className="max-h-96 overflow-y-auto space-y-3">
                        {radarData.details && radarData.details.length > 0 ? (
                            radarData.details.map((detail, idx) => (
                                <div key={idx} className="flex justify-between items-center bg-slate-950 border border-slate-800 p-4 rounded-xl">
                                    <div>
                                        <p className="font-bold text-sm text-white">{detail.id}</p>
                                        <p className="text-xs text-slate-500 mt-1">{detail.desc}</p>
                                    </div>
                                    <span className={`px-3 py-1 text-xs font-bold rounded-lg uppercase border ${
                                        detail.state === 'LOCKED_SAFE' ? 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30' :
                                        detail.state === 'WITHDRAWAL_RISK' ? 'bg-blue-900/30 text-blue-400 border-blue-500/30' :
                                        'bg-amber-900/30 text-amber-400 border-amber-500/30'
                                    }`}>
                                        {detail.state.replace('_', ' ')}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <div className="text-center text-slate-500 py-10">Zatím nejsou monitorovány žádné dokumenty.</div>
                        )}
                    </div>
                </div>
            </div>
        )}"""

content = re.sub(old_radar_pattern, new_radar_code, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("[+] Právní Radar úspěšně aktualizován. Zkontroluj prohlížeč.")
