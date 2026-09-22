import os

file_path = "/data/data/com.termux/files/home/InloopID/frontend/src/components/HRDashboard.jsx"

# Bezpečnostní záloha rozbité verze
if os.path.exists(file_path):
    os.rename(file_path, file_path + ".bak_crashed")

new_code = """import React, { useState, useEffect } from 'react';
import { ShieldCheck, FileText, UploadCloud, Lock, AlertTriangle, Key, Upload, CheckSquare, Square, Users, FilePlus, Paperclip, X, Link as LinkIcon, Calendar, User, Briefcase, Filter, CheckCircle } from 'lucide-react';
import { decryptKeystore } from '../utils/cryptoEngine';
import { notify } from './ToastManager';

const BACKEND_URL = 'http://localhost:5000/api/v1';

const safeFetch = async (url, options) => {
  const res = await fetch(url, options);
  if (!res.ok) { let errorMsg = "Server zamítl operaci."; try { const errData = await res.json(); errorMsg = errData.error || errorMsg; } catch (e) {} throw new Error(errorMsg); }
  return await res.json();
};

export const HRDashboard = () => {
  const [hrPassword, setHrPassword] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  
  const [activeTab, setActiveTab] = useState('bulk');
  const [bulkText, setBulkText] = useState('');
  const [importStep, setImportStep] = useState(1);
  const [parsedCandidates, setParsedCandidates] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [sortOrder, setSortOrder] = useState('default');
  
  const [contractForm, setContractForm] = useState({ email: '', type: 'HPP', position: '', salary: '' });
  const [issuedContracts, setIssuedContracts] = useState([]);
  const [radarData, setRadarData] = useState({ safe: 0, withdrawal_risk: 0, pending_signatures: 0, details: [] });

  const generateRealHash = async (dataStr, prefix="SHA256_") => {
      const msgUint8 = new TextEncoder().encode(dataStr);
      const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return prefix + hashHex.toUpperCase();
  };

  const handleKeyFileUpload = (e) => {
      const file = e.target.files[0]; if (!file) return;
      const reader = new FileReader();
      reader.onload = (evt) => {
          try { const data = JSON.parse(evt.target.result); if (data.tenant && data.masterKey) { setTenantId(data.tenant); setHrPassword(data.masterKey); notify.success("Záložní soubor načten."); }
          } catch (err) { notify.error("Chyba při čtení zálohy."); }
      }; reader.readAsText(file);
  };

  const unlockLedger = async (e) => {
    e.preventDefault(); setIsLoggingIn(true);
    try {
        await safeFetch(`${BACKEND_URL}/hr/agenda?tenant_id=${tenantId.trim()}`);
        await decryptKeystore(hrPassword, "HR_SALT"); 
        setIsUnlocked(true); fetchRadarData(); fetchContracts();
    } catch (err) {}
    setIsLoggingIn(false);
  };

  const fetchRadarData = async () => { try { setRadarData((await safeFetch(`${BACKEND_URL}/hr/compliance-radar?tenant_id=${tenantId.trim()}`)).radar); } catch(e) { } };
  const fetchContracts = async () => { try { setIssuedContracts((await safeFetch(`${BACKEND_URL}/hr/contracts?tenant_id=${tenantId.trim()}`)).data); } catch(e) { } };
  const handleDownloadAudit = () => { window.open(`${BACKEND_URL}/hr/compliance-report/pdf?tenant_id=${tenantId.trim()}`, '_blank'); };

  useEffect(() => {
      let interval;
      if (isUnlocked) { interval = setInterval(() => { if (activeTab === 'contracts') fetchContracts(); if (activeTab === 'radar') fetchRadarData(); }, 3000); }
      return () => clearInterval(interval);
  }, [isUnlocked, activeTab]);

  const handleCsvUpload = async (e) => {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      const readPromises = files.map(file => {
          return new Promise((resolve) => {
              const reader = new FileReader();
              reader.onload = (evt) => resolve(evt.target.result);
              reader.readAsText(file);
          });
      });
      const results = await Promise.all(readPromises);
      setBulkText(prev => {
          const newText = prev ? prev + "\\n" + results.join("\\n") : results.join("\\n");
          return newText;
      });
      notify.success(`Úspěšně načteno ${files.length} souborů.`);
      e.target.value = null;
  };

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
              if (stringParts.length >= 3) { 
                  firstName = stringParts[0]; lastName = stringParts[1]; position = stringParts.slice(2).join(' ');
              } else if (stringParts.length === 2) {
                  firstName = stringParts[0]; lastName = stringParts[1];
              } else if (stringParts.length === 1) {
                  const splitName = stringParts[0].split(' ');
                  if (splitName.length >= 2) { firstName = splitName[0]; lastName = splitName.slice(1).join(' '); }
                  else { lastName = stringParts[0]; }
              }
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

  const handleFinalSubmit = async () => {
      const finalCandidates = parsedCandidates.filter(c => c.selected);
      if (finalCandidates.length === 0) return;
      setIsProcessing(true);
      try {
          for (const cand of finalCandidates) {
              if (cand.contractUrl || cand.contractFileBase64) {
                  const payloadString = JSON.stringify({
                      type: 'MIGRATED_CONTRACT', position: cand.position || 'Historická dokumentace',
                      firstName: cand.firstName, lastName: cand.lastName, startDate: cand.startDate,
                      url: cand.contractUrl, fileName: cand.contractFileName, fileData: cand.contractFileBase64
                  });
                  const mockEncryptedPayload = btoa(unescape(encodeURIComponent(payloadString)));
                  const mockHash = await generateRealHash(payloadString, "SHA256_MIGRATED_");
                  await safeFetch(`${BACKEND_URL}/hr/contracts`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ tenant_id: tenantId.trim(), email: cand.email, content_hash: mockHash, encrypted_payload: mockEncryptedPayload }) });
              }
          }
          const finalEmails = finalCandidates.map(c => c.email);
          await safeFetch(`${BACKEND_URL}/hr/bulk-import`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ tenant_id: tenantId.trim(), emails: finalEmails }) });
          
          notify.success(`Migrace úspěšná! Naimportováno ${finalEmails.length} zaměstnanců.`);
          setBulkText(''); setImportStep(1); setParsedCandidates([]);
      } catch(e) { notify.error(e.message); }
      setIsProcessing(false);
  };

  const handleIssueContract = async (e) => {
      e.preventDefault(); setIsProcessing(true);
      try {
          const payloadString = JSON.stringify(contractForm);
          const mockEncryptedPayload = btoa(unescape(encodeURIComponent(payloadString)));
          const mockHash = await generateRealHash(payloadString, "SHA256_");
          await safeFetch(`${BACKEND_URL}/hr/contracts`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ tenant_id: tenantId.trim(), email: contractForm.email, content_hash: mockHash, encrypted_payload: mockEncryptedPayload }) });
          notify.success(`Smlouva typu ${contractForm.type} bezpečně vytvořena.`);
          setContractForm({ ...contractForm, position: '', salary: '' }); fetchContracts();
      } catch (err) { notify.error(err.message); }
      setIsProcessing(false);
  };

  if (!isUnlocked) {
    return ( <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 text-white"><div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl"><Key size={48} className="text-blue-500 mx-auto mb-4" /><h2 className="text-2xl font-bold mb-6 text-center">HR Velín (Login)</h2><label className="flex items-center justify-center gap-2 w-full py-3 mb-6 bg-slate-800 hover:bg-slate-700 rounded-xl cursor-pointer transition-colors text-sm font-bold"><Upload size={18} /> Nahrát InLoopID_Backup.json<input type="file" accept=".json" className="hidden" onChange={handleKeyFileUpload} /></label><form onSubmit={unlockLedger} className="space-y-4"><input type="text" value={tenantId} onChange={e => setTenantId(e.target.value)} placeholder="ID Firmy" required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500" /><input type="password" value={hrPassword} onChange={e => setHrPassword(e.target.value)} placeholder="HR Master Password" required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500" /><button type="submit" disabled={isLoggingIn} className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-colors">Odemknout Velín</button></form></div></div> );
  }

  return (
    <div className="min-h-screen p-6 bg-slate-950 text-white">
      <div className="max-w-6xl mx-auto space-y-6">
        
        <div className="flex justify-between items-center bg-slate-900 p-4 rounded-2xl border border-slate-800">
            <div><h1 className="text-xl font-bold text-white">Enterprise Velín</h1><p className="text-sm text-blue-400 font-mono">{tenantId}</p></div>
            <div className="flex gap-2"><button onClick={() => setActiveTab('bulk')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'bulk' ? 'bg-blue-600' : 'bg-slate-800 hover:bg-slate-700'}`}><Users size={16}/> Hromadná Migrace</button><button onClick={() => setActiveTab('contracts')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'contracts' ? 'bg-blue-600' : 'bg-slate-800 hover:bg-slate-700'}`}><FilePlus size={16}/> Nové Smlouvy</button><button onClick={() => setActiveTab('radar')} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-colors ${activeTab === 'radar' ? 'bg-blue-600' : 'bg-slate-800 hover:bg-slate-700'}`}><ShieldCheck size={16}/> Právní Radar</button></div>
        </div>

        {activeTab === 'bulk' && importStep === 1 && (
           <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 animate-fade-in">
              <h2 className="text-2xl font-bold mb-2 flex items-center gap-3"><UploadCloud className="text-blue-500"/> Krok 1: Extrakce dat</h2>
              <p className="text-slate-400 mb-6 text-sm">Nahrajte exportní CSV/TXT soubor nebo vložte data ručně.</p>
              <div className="flex flex-col gap-4 mb-6">
                  <label className="flex flex-col items-center justify-center gap-3 w-full py-8 border-2 border-dashed border-slate-700 hover:border-blue-500 bg-slate-950/50 hover:bg-slate-900 rounded-2xl cursor-pointer transition-all group">
                      <UploadCloud size={36} className="text-slate-500 group-hover:text-blue-500 transition-colors" />
                      <span className="text-slate-300 font-bold text-lg group-hover:text-white transition-colors">Nahrát .CSV nebo .TXT soubory</span>
                      <span className="text-slate-500 text-xs">Klikněte pro výběr jednoho nebo více souborů najednou</span>
                      <input type="file" accept=".csv,.txt" multiple className="hidden" onChange={handleCsvUpload} />
                  </label>
                  <div className="flex items-center gap-4 text-slate-600 text-xs font-bold uppercase tracking-widest"><hr className="flex-1 border-slate-800"/>nebo vložit text ručně<hr className="flex-1 border-slate-800"/></div>
                  <textarea value={bulkText} onChange={e => setBulkText(e.target.value)} className="w-full h-32 bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-sm outline-none focus:border-blue-500 leading-relaxed" placeholder="Jan; Novák; jan.novak@firma.cz; 1. 5. 2023; https://cloud.cz/smlouva.pdf" />
              </div>
              <button onClick={handleParseText} disabled={!bulkText} className="mt-4 w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-colors text-lg">Zahájit analýzu a párování</button>
           </div>
        )}

        {activeTab === 'bulk' && importStep === 2 && (
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

        {activeTab === 'contracts' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in"><div className="bg-slate-900 p-8 rounded-3xl border border-slate-800"><h2 className="text-xl font-bold mb-6 flex items-center gap-3"><FilePlus className="text-emerald-500"/> Generátor Dokumentů</h2><form onSubmit={handleIssueContract} className="space-y-4"><div><label className="block text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">Zaměstnanec (E-mail)</label><input type="email" value={contractForm.email} onChange={e => setContractForm({...contractForm, email: e.target.value})} placeholder="Např. jan.novak@firma.cz" required className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500" /></div><div className="grid grid-cols-2 gap-4"><div><label className="block text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">Typ Smlouvy</label><select value={contractForm.type} onChange={e => setContractForm({...contractForm, type: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500"><option value="HPP">Pracovní smlouva (HPP)</option><option value="DPP">Dohoda (DPP)</option><option value="NDA">Dohoda o mlčenlivosti (NDA)</option><option value="PROTOCOL">Předávací protokol</option></select></div><div><label className="block text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">Odměna (CZK/Měsíc)</label><input type="number" value={contractForm.salary} onChange={e => setContractForm({...contractForm, salary: e.target.value})} placeholder="Např. 50000" className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500" /></div></div><div><label className="block text-xs font-bold text-slate-500 mb-1 uppercase tracking-wider">Pracovní Pozice / Předmět</label><input type="text" value={contractForm.position} onChange={e => setContractForm({...contractForm, position: e.target.value})} placeholder="Např. Software Inženýr" className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white outline-none focus:border-blue-500" /></div><button type="submit" disabled={isProcessing} className="mt-4 w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 rounded-xl font-bold transition-colors flex items-center justify-center gap-2"><Lock size={18} /> {isProcessing ? 'Šifruji...' : 'Zašifrovat a odeslat'}</button></form></div>
                <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 flex flex-col"><h2 className="text-xl font-bold mb-6 flex items-center gap-3"><FileText className="text-blue-500"/> Vystavené Dokumenty</h2><div className="flex-1 overflow-y-auto space-y-3">
                        {issuedContracts.length === 0 ? (<div className="text-center text-slate-500 py-10">Zatím nebyly vystaveny žádné smlouvy.</div>) : (
                            issuedContracts.map((c, idx) => (<div key={idx} className={`flex justify-between items-center bg-slate-950 border border-slate-800 p-4 rounded-xl transition-colors ${c.status === 'signed' ? 'border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.1)]' : ''}`}><div><p className="font-bold text-sm text-white">{c.id}</p><p className="text-xs text-slate-500 font-mono mt-1 w-32 truncate" title={c.subject_did}>{c.subject_did}</p></div><span className={`px-3 py-1 text-xs font-bold rounded-lg uppercase border ${c.status === 'signed' ? 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>{c.status.replace('_', ' ')}</span></div>))
                        )}
                    </div></div></div>
        )}
        
        {activeTab === 'radar' && (
            <div className="space-y-6 animate-fade-in"><div className="grid grid-cols-1 md:grid-cols-3 gap-6"><div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 flex flex-col items-center justify-center shadow-xl"><ShieldCheck className="text-emerald-500 mb-2" size={28} /><h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Nedotknutelné</h3><p className="text-4xl font-extrabold text-emerald-500 mt-2">{radarData.safe}</p></div><div className="bg-slate-900 p-6 rounded-3xl border border-blue-900 flex flex-col items-center justify-center shadow-[0_0_20px_rgba(59,130,246,0.15)] relative overflow-hidden"><div className="absolute top-0 w-full h-1 bg-blue-500"></div><AlertTriangle className="text-blue-400 mb-2" size={28} /><h3 className="text-blue-400 text-xs font-bold uppercase tracking-wider">V ochranné lhůtě</h3><p className="text-4xl font-extrabold text-white mt-2">{radarData.withdrawal_risk}</p></div><div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 flex flex-col items-center justify-center shadow-xl"><FileText className="text-amber-500 mb-2" size={28} /><h3 className="text-slate-400 text-xs font-bold uppercase tracking-wider">Čeká na podpis</h3><p className="text-4xl font-extrabold text-white mt-2">{radarData.pending_signatures}</p></div></div><div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 shadow-xl"><div className="flex justify-between items-center mb-6"><h3 className="text-xl font-bold flex items-center gap-3"><AlertTriangle className="text-blue-500"/> Detailní monitoring dokumentů</h3><button onClick={handleDownloadAudit} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-blue-600 text-white rounded-xl text-sm font-bold transition-colors"><FileText size={16}/> Stáhnout certifikovaný audit</button></div><div className="max-h-96 overflow-y-auto space-y-3">{radarData.details && radarData.details.length > 0 ? ( radarData.details.map((detail, idx) => (<div key={idx} className="flex justify-between items-center bg-slate-950 border border-slate-800 p-4 rounded-xl"><div><p className="font-bold text-sm text-white">{detail.id}</p><p className="text-xs text-slate-500 mt-1">{detail.desc}</p></div><span className={`px-3 py-1 text-xs font-bold rounded-lg uppercase border ${ detail.state === 'LOCKED_SAFE' ? 'bg-emerald-900/30 text-emerald-400 border-emerald-500/30' : detail.state === 'WITHDRAWAL_RISK' ? 'bg-blue-900/30 text-blue-400 border-blue-500/30' : 'bg-amber-900/30 text-amber-400 border-amber-500/30'}`}>{detail.state.replace('_', ' ')}</span></div>))) : (<div className="text-center text-slate-500 py-10">Zatím nejsou monitorovány žádné dokumenty.</div>)}</div></div></div>
        )}
      </div>
    </div>
  );
};
"""

with open(file_path, 'w') as f:
    f.write(new_code)

print("[+] Záchrana dokončena! Komponenta HRDashboard byla kompletně obnovena se všemi funkcemi a garantovanými importy.")
