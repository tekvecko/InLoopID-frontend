import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/EmployeePortal.jsx"

# Záchranná záloha pro případný rollback
if os.path.exists(file_path):
    os.rename(file_path, file_path + ".bak_reading")

new_code = """import React, { useState, useEffect } from 'react';
import { ShieldCheck, FileText, UserCheck, LogOut, CheckCircle, Database, FileSignature, X, PenTool, ExternalLink, Download, Clock, Eye } from 'lucide-react';
import { notify } from './ToastManager';

const BACKEND_URL = 'http://localhost:5000/api/v1';

export const EmployeePortal = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [employeeData, setEmployeeData] = useState(null);
  const [activeToken, setActiveToken] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isSigning, setIsSigning] = useState(false);

  // --- STAVY PRO PRÁVNÍ LOGIKU ČTENÍ ---
  const [readStatus, setReadStatus] = useState('unread'); 
  const [readCountdown, setReadCountdown] = useState(5);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('mojeid_token');
    if (tokenFromUrl) {
        localStorage.setItem('inloop_mojeid_token', tokenFromUrl);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    checkSession();
  }, []);

  useEffect(() => {
      let interval;
      if (isAuthenticated) { interval = setInterval(() => { checkSession(true); }, 3000); }
      return () => clearInterval(interval);
  }, [isAuthenticated]);

  // --- ODPOČÍTÁVACÍ ČASOVAČ ---
  useEffect(() => {
      let timer;
      if (readStatus === 'reading' && readCountdown > 0) {
          timer = setTimeout(() => setReadCountdown(c => c - 1), 1000);
      } else if (readStatus === 'reading' && readCountdown === 0) {
          setReadStatus('ready');
      }
      return () => clearTimeout(timer);
  }, [readStatus, readCountdown]);

  const checkSession = async (isBackground = false) => {
    const token = localStorage.getItem('inloop_mojeid_token');
    if (!token) { if(!isBackground) setIsLoading(false); return; }
    if (!isBackground) setActiveToken(token);
    try {
        const res = await fetch(`${BACKEND_URL}/employee/vault`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) {
            const data = await res.json();
            setEmployeeData(data); setIsAuthenticated(true);
            setSelectedDoc(prevDoc => {
                if (prevDoc) {
                    const updated = data.documents.find(d => d.id === prevDoc.id);
                    if (updated && updated.status !== prevDoc.status) return updated;
                    return prevDoc;
                }
                return null;
            });
        } else { if(!isBackground) localStorage.removeItem('inloop_mojeid_token'); }
    } catch (e) { if(!isBackground) console.error("Chyba spojení."); }
    if(!isBackground) setIsLoading(false);
  };

  const handleMojeIDLogin = () => { window.location.href = `${BACKEND_URL}/mojeid/login`; };
  const handleLogout = () => { localStorage.removeItem('inloop_mojeid_token'); window.location.reload(); };

  const decryptPayload = (encryptedBase64) => {
      try { return JSON.parse(decodeURIComponent(escape(atob(encryptedBase64)))); }
      catch (e) { return { error: "Obsah dokumentu se nepodařilo rozšifrovat." }; }
  };

  const handleSignContract = async (contractId) => {
      setIsSigning(true);
      try {
          const res = await fetch(`${BACKEND_URL}/employee/sign-contract`, {
              method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${activeToken}` },
              body: JSON.stringify({ contract_id: contractId })
          });
          if (!res.ok) throw new Error("Podpis byl zamítnut.");
          notify.success("Dokument byl úspěšně elektronicky podepsán.");
          setReadStatus('unread'); // Zajištění resetu do budoucna
      } catch (err) { notify.error(err.message); }
      setIsSigning(false);
  };

  // --- FUNKCE PRO VSTUP DO SMLOUVY ---
  const openDocumentView = (doc) => {
      setSelectedDoc(doc);
      setReadStatus('unread');
      setReadCountdown(5);
  };

  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-500 animate-pulse font-mono">Navazuji zabezpečené spojení s InLoopID...</div>;

  if (!isAuthenticated) {
    return ( <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-950 text-white"><div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-10 shadow-2xl text-center"><div className="w-20 h-20 bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-6 border border-blue-500/30"><ShieldCheck size={40} className="text-blue-500" /></div><h2 className="text-3xl font-bold mb-2">Zaměstnanecký Trezor</h2><p className="text-slate-400 mb-8 leading-relaxed">Přístup k pracovněprávním dokumentům je vázán výhradně na Vaši digitální identitu.</p><button onClick={handleMojeIDLogin} className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] flex items-center justify-center gap-3 text-lg"><UserCheck size={24} /> Přihlásit přes MojeID</button></div></div> );
  }

  if (selectedDoc) {
      const docData = decryptPayload(selectedDoc.encrypted_payload);
      const isPending = selectedDoc.status === 'pending_signature';

      return (
          <div className="min-h-screen p-6 bg-slate-950 text-white flex flex-col items-center justify-center animate-fade-in">
              <div className="w-full max-w-2xl bg-slate-900 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden relative">
                  <div className="bg-slate-950 p-6 flex justify-between items-center border-b border-slate-800">
                      <div className="flex items-center gap-3"><FileSignature className="text-blue-500" size={28} /><div><h2 className="text-xl font-bold">Zabezpečený Dokument</h2><p className="text-xs font-mono text-slate-500">{selectedDoc.id}</p></div></div>
                      <button onClick={() => setSelectedDoc(null)} className="text-slate-500 hover:text-white transition-colors bg-slate-800 p-2 rounded-full"><X size={20} /></button>
                  </div>

                  <div className="p-10 space-y-8">
                      {docData.error ? (<div className="text-rose-400 text-center font-bold">{docData.error}</div>) : (
                          <>
                              {docData.type === 'MIGRATED_CONTRACT' ? (
                                  <div className="bg-slate-950 p-8 rounded-3xl border border-slate-800 text-center shadow-inner">
                                      <FileText size={48} className="text-blue-500 mx-auto mb-4" />
                                      <h3 className="text-2xl font-bold text-white mb-2">Historická pracovní smlouva</h3>

                                      <div className="my-6 p-4 bg-slate-900 rounded-xl border border-slate-800 inline-block text-left">
                                         {docData.firstName && <p className="text-slate-300 font-bold mb-1"><span className="text-slate-500 text-sm font-normal mr-2">Zaměstnanec:</span> {docData.firstName} {docData.lastName}</p>}
                                         {docData.startDate && <p className="text-emerald-400 font-bold"><span className="text-slate-500 text-sm font-normal mr-2">Datum nástupu:</span> {docData.startDate}</p>}
                                      </div>

                                      <p className="text-slate-400 mb-6">Tato smlouva byla migrována z předchozího systému. Zde si můžete zobrazit originální dokumentaci.</p>

                                      {/* Schování původních tlačítek, pokud smlouva čeká na podpis */}
                                      {!isPending && (
                                          <div className="flex flex-col gap-4 items-center">
                                              {docData.url && ( <a href={docData.url} target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-slate-800 hover:bg-blue-600 rounded-xl font-bold transition-colors flex items-center gap-3"><ExternalLink size={20}/> Otevřít na firemním cloudu</a> )}
                                              {docData.fileData && ( <a href={docData.fileData} download={docData.fileName || 'smlouva.pdf'} className="px-8 py-4 bg-emerald-600 hover:bg-emerald-500 rounded-xl font-bold transition-colors flex items-center gap-3"><Download size={20}/> Stáhnout připojený soubor</a> )}
                                          </div>
                                      )}
                                  </div>
                              ) : (
                                  <>
                                      <div className="grid grid-cols-2 gap-6"><div className="bg-slate-950 p-5 rounded-2xl border border-slate-800"><p className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-1">Typ dokumentu</p><p className="text-lg text-white font-bold">{docData.type || 'Smlouva'}</p></div><div className="bg-slate-950 p-5 rounded-2xl border border-slate-800"><p className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-1">Pracovní pozice</p><p className="text-lg text-white font-bold">{docData.position || 'Nespecifikováno'}</p></div></div>
                                      <div className="bg-slate-950 p-6 rounded-2xl border border-slate-800 flex items-center justify-between"><div><p className="text-xs uppercase tracking-wider text-slate-500 font-bold mb-1">Sjednaná odměna</p><p className="text-2xl text-emerald-400 font-extrabold">{docData.salary ? `${docData.salary} CZK` : 'Dle dohody'}</p></div><ShieldCheck size={40} className="text-slate-800" /></div>
                                  </>
                              )}
                          </>
                      )}

                      {/* --- DYNAMICKÁ SEKCE PODPISU - SOULAD SE ZÁKONÍKEM PRÁCE --- */}
                      {isPending ? (
                          <div className="mt-8 pt-8 border-t border-slate-800">
                              <p className={`text-sm text-center mb-6 font-bold ${readStatus === 'ready' ? 'text-blue-400' : 'text-slate-400'}`}>
                                  {readStatus === 'unread' ? 'Dle Zákoníku práce ČR je před podpisem nutné seznámit se s obsahem.' :
                                   readStatus === 'reading' ? 'Ponechávám čas na prostudování...' :
                                   'Nyní můžete dokument závazně podepsat pomocí vaší identity MojeID.'}
                              </p>

                              {readStatus === 'unread' && (
                                  <button
                                      onClick={() => {
                                          if (docData.url) { window.open(docData.url, '_blank'); }
                                          else if (docData.fileData) {
                                              const a = document.createElement('a');
                                              a.href = docData.fileData; a.download = docData.fileName || 'smlouva.pdf'; a.click();
                                          }
                                          setReadStatus('reading');
                                      }}
                                      className="w-full py-5 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold text-lg transition-colors flex justify-center items-center gap-3 border border-slate-600"
                                  >
                                      <Eye size={20} /> Zobrazit a přečíst smlouvu
                                  </button>
                              )}

                              {readStatus === 'reading' && (
                                  <button disabled className="w-full py-5 bg-slate-950 border border-slate-800 text-slate-500 rounded-xl font-bold text-lg cursor-not-allowed flex justify-center items-center gap-3">
                                      <Clock size={20} className="animate-pulse" /> Pročítání dokumentu... ({readCountdown}s)
                                  </button>
                              )}

                              {readStatus === 'ready' && (
                                  <button
                                      onClick={() => handleSignContract(selectedDoc.id)}
                                      disabled={isSigning}
                                      className="w-full py-5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 rounded-xl font-bold text-lg transition-all shadow-[0_0_20px_rgba(37,99,235,0.4)] flex justify-center items-center gap-3 animate-fade-in"
                                  >
                                      <PenTool size={20} /> {isSigning ? 'Zapisuji do blockchainu...' : 'Elektronicky Podepsat'}
                                  </button>
                              )}
                          </div>
                      ) : (
                          <div className="mt-8 pt-8 border-t border-slate-800 flex justify-center"><span className="flex items-center gap-2 px-6 py-3 bg-emerald-900/30 text-emerald-400 border border-emerald-500/30 rounded-xl font-bold"><CheckCircle size={20} /> Dokument je již úspěšně podepsán</span></div>
                      )}
                  </div>
              </div>
          </div>
      );
  }

  return (
    <div className="min-h-screen p-6 bg-slate-950 text-white">
       <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
          <div className="flex justify-between items-center bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
             <div className="flex items-center gap-4"><div className="w-14 h-14 bg-emerald-900/30 rounded-full flex items-center justify-center border border-emerald-500/30"><UserCheck size={28} className="text-emerald-500" /></div><div><h1 className="text-2xl font-bold">{employeeData?.name}</h1><p className="text-sm text-emerald-400 flex items-center gap-1"><CheckCircle size={14}/> {employeeData?.email}</p></div></div>
             <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-sm font-bold transition-colors"><LogOut size={16} /> Odhlásit se</button>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl relative overflow-hidden min-h-[400px]">
              <div className="absolute top-0 right-0 p-6 text-slate-800 opacity-20"><Database size={120}/></div>
              <h3 className="text-2xl font-bold text-white mb-6 relative z-10 flex items-center gap-3"><FileText className="text-blue-500" /> Vaše složka</h3>
              {employeeData?.documents && employeeData.documents.length > 0 ? (
                  <div className="space-y-4 relative z-10">
                      {employeeData.documents.map((doc, i) => {
                          const isPending = doc.status === 'pending_signature';
                          return (
                              <div key={i} className="bg-slate-950 border border-slate-800 p-5 rounded-2xl flex items-center justify-between hover:border-blue-500/50 transition-colors">
                                  <div><p className="text-lg font-bold text-white mb-1">Pracovněprávní dokument</p><p className="text-xs font-mono text-slate-500">ID: {doc.id}</p></div>
                                  <div className="flex items-center gap-4"><span className={`px-4 py-1.5 text-xs font-bold rounded-lg uppercase tracking-wide border ${isPending ? 'bg-amber-900/30 text-amber-400 border-amber-500/30' : 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30'}`}>{isPending ? 'Čeká na Váš podpis' : 'Podepsáno'}</span>
                                  <button onClick={() => openDocumentView(doc)} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold text-sm transition-colors">Otevřít</button></div>
                              </div>
                          );
                      })}
                  </div>
              ) : (
                  <div className="text-center mt-16 relative z-10"><FileText size={64} className="text-slate-800 mx-auto mb-6" /><h3 className="text-2xl font-bold text-slate-300 mb-2">Váš trezor je zatím prázdný</h3><p className="text-slate-500 max-w-md mx-auto">Jakmile Vaše HR oddělení připraví smlouvu k podpisu, objeví se zde.</p></div>
              )}
          </div>
       </div>
    </div>
  );
};
"""

with open(file_path, 'w') as f:
    f.write(new_code)

print("[+] Trezor byl aktualizován: Implementována ochranná logika, odpočet a vyčištěna tlačítka před podpisem.")
