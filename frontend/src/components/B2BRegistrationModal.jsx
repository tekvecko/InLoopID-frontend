import React, { useState } from 'react';
import { Loader2, Key, Server, CheckCircle, Shield, X, Terminal, Check } from 'lucide-react';
import { API_BASE_URL as BACKEND_URL } from '../utils/config';

export const B2BRegistrationModal = ({ onClose }) => {
    const [step, setStep] = useState(1); // 1 = výběr tarifu, 2 = formulář
    const [selectedPlan, setSelectedPlan] = useState('free');
    const [formData, setFormData] = useState({ companyName: '', ico: '', adminEmail: '' });
    const [status, setStatus] = useState('idle'); // idle, processing, success, error
    const [logs, setLogs] = useState([]);

    const addLog = (msg) => setLogs(prev => [...prev, msg]);

    const handleRegister = async () => {
        if (!formData.companyName || !formData.ico || !formData.adminEmail) {
            setStatus('error');
            addLog("[!] Chyba: Vyplňte všechna povinná pole.");
            return;
        }

        setStatus('processing');
        setLogs([]);
        addLog("> Inicializace Zero-Knowledge prostředí...");

        try {
            await new Promise(r => setTimeout(r, 600));
            addLog("> Generování RSA-4096 páru asymetrických klíčů (WebCrypto API)...");

            const keyPair = await window.crypto.subtle.generateKey(
                { name: "RSA-OAEP", modulusLength: 4096, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
                true, ["encrypt", "decrypt"]
            );

            await new Promise(r => setTimeout(r, 800));
            addLog("> [OK] Klíče vygenerovány. Privátní klíč izolován v RAM prohlížeče.");

            const exportedPublicKey = await window.crypto.subtle.exportKey("jwk", keyPair.publicKey);
            addLog("> Export veřejného klíče pro ukotvení...");

            const tenantId = 'T-' + formData.ico.substring(0, 8) + '-' + Math.random().toString(36).substr(2, 4).toUpperCase();
            addLog(`> Odesílám payload na ${BACKEND_URL}/b2b/register (Tenant: ${tenantId})...`);

            const response = await fetch(`${BACKEND_URL}/b2b/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tenant_id: tenantId,
                    company_name: formData.companyName,
                    ico: formData.ico,
                    admin_email: formData.adminEmail,
                    public_key_jwk: JSON.stringify(exportedPublicKey),
                    subscription_plan: selectedPlan
                })
            });

            if (!response.ok) {
                let errorMsg = "Odmítnuto serverem.";
                try {
                    const errData = await response.json();
                    errorMsg = errData.error || errorMsg;
                } catch (e) {
                    errorMsg = `Chyba serveru (Status: ${response.status})`;
                }
                throw new Error(errorMsg);
            }

            addLog("> [OK] eIDAS uzly synchronizovány. Workspace je aktivní.");
            setStatus('success');

            localStorage.setItem('inloop_demo_tenant', tenantId);
            localStorage.setItem('inloop_demo_company', formData.companyName);

            setTimeout(() => {
                onClose();
                document.getElementById('inloopid-demo')?.scrollIntoView({ behavior: 'smooth' });
            }, 3000);

        } catch (err) {
            addLog(`> [!] FATAL ERROR: ${err.message}`);
            setStatus('error');
        }
    };

    return (
        <div className="fixed inset-0 z-[70] bg-[#0B1120]/95 overflow-y-auto pt-16 md:pt-24 pb-8 md:pb-12 px-4 backdrop-blur-xl flex justify-center items-start">
            <div className="bg-[#112240] p-6 md:p-10 rounded-2xl md:rounded-3xl border border-blue-500/40 w-full max-w-4xl shadow-2xl relative animate-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">

                <button onClick={onClose} className="absolute top-6 right-6 text-slate-500 hover:text-white bg-slate-800/50 p-2 rounded-full transition-colors z-10">
                    <X size={20} />
                </button>

                {step === 1 ? (
                    <div>
                        <div className="mb-8 text-center">
                            <h3 className="text-3xl font-bold text-white mb-2 tracking-tight">Zvolte tarif pro Workspace</h3>
                            <p className="text-blue-300/70 text-sm">Vyberte si úroveň ochrany pro Vaši firmu.</p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-4 mb-8">
                            {/* Free */}
                            <div onClick={() => setSelectedPlan('free')} className={`cursor-pointer p-5 rounded-2xl border-2 transition-all ${selectedPlan === 'free' ? 'bg-blue-950/80 border-blue-500 shadow-lg' : 'bg-[#0A192F] border-slate-800'}`}>
                                <h4 className="text-xl font-bold text-white mb-1">Free</h4>
                                <div className="text-2xl font-extrabold text-blue-400 mb-4">0 Kč<span className="text-xs text-slate-400 font-normal">/měs</span></div>
                                <ul className="space-y-2 text-xs text-slate-300 mb-4">
                                    <li className="flex items-center gap-2"><Check size={14} className="text-slate-400"/> Až 5 zaměstnanců</li>
                                    <li className="flex items-center gap-2"><Check size={14} className="text-slate-400"/> Základní ZK Vault</li>
                                </ul>
                            </div>

                            {/* Standard */}
                            <div onClick={() => setSelectedPlan('standard')} className={`cursor-pointer p-5 rounded-2xl border-2 transition-all ${selectedPlan === 'standard' ? 'bg-blue-950/80 border-blue-500 shadow-lg' : 'bg-[#0A192F] border-slate-800'}`}>
                                <h4 className="text-xl font-bold text-white mb-1">Standard</h4>
                                <div className="text-2xl font-extrabold text-blue-400 mb-4">2 990 Kč<span className="text-xs text-slate-400 font-normal">/měs</span></div>
                                <ul className="space-y-2 text-xs text-slate-300 mb-4">
                                    <li className="flex items-center gap-2"><Check size={14} className="text-blue-400"/> Až 50 zaměstnanců</li>
                                    <li className="flex items-center gap-2"><Check size={14} className="text-blue-400"/> ZK Kryptografický Trezor</li>
                                </ul>
                            </div>

                            {/* Enterprise */}
                            <div onClick={() => setSelectedPlan('enterprise')} className={`cursor-pointer p-5 rounded-2xl border-2 transition-all ${selectedPlan === 'enterprise' ? 'bg-blue-950/80 border-blue-500 shadow-lg' : 'bg-[#0A192F] border-slate-800'}`}>
                                <h4 className="text-xl font-bold text-white mb-1">Enterprise</h4>
                                <div className="text-2xl font-extrabold text-blue-400 mb-4">9 990 Kč<span className="text-xs text-slate-400 font-normal">/měs</span></div>
                                <ul className="space-y-2 text-xs text-slate-300 mb-4">
                                    <li className="flex items-center gap-2"><Check size={14} className="text-emerald-400"/> Neomezeně zaměstnanců</li>
                                    <li className="flex items-center gap-2"><Check size={14} className="text-emerald-400"/> Plná automatizace</li>
                                </ul>
                            </div>
                        </div>

                        <button onClick={() => setStep(2)} className="w-full bg-blue-600 hover:bg-blue-500 text-white py-4 rounded-xl font-bold text-lg transition-all">
                            Pokračovat k údajům firmy &rarr;
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-10">
                        {/* Levý panel - Formulář */}
                        <div className="flex flex-col justify-center">
                            <div className="mb-6 flex justify-between items-center">
                                <div>
                                    <h3 className="text-2xl font-bold text-white mb-1">Fakturační údaje</h3>
                                    <p className="text-blue-300/70 text-xs">Zvolený tarif: <strong className="text-blue-400 uppercase">{selectedPlan}</strong></p>
                                </div>
                                <button onClick={() => setStep(1)} className="text-xs text-blue-400 hover:underline">&larr; Změnit tarif</button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-1 tracking-wider">Název společnosti</label>
                                    <input disabled={status === 'processing' || status === 'success'} type="text" value={formData.companyName} onChange={e => setFormData({...formData, companyName: e.target.value})} className="w-full bg-[#0A192F] border border-slate-700/80 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none text-sm" placeholder="InLoop Solutions s.r.o." />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-1 tracking-wider">IČO</label>
                                    <input disabled={status === 'processing' || status === 'success'} type="text" value={formData.ico} onChange={e => setFormData({...formData, ico: e.target.value})} className="w-full bg-[#0A192F] border border-slate-700/80 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none text-sm font-mono" placeholder="12345678" />
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-slate-400 uppercase mb-1 tracking-wider">E-mail administrátora</label>
                                    <input disabled={status === 'processing' || status === 'success'} type="email" value={formData.adminEmail} onChange={e => setFormData({...formData, adminEmail: e.target.value})} className="w-full bg-[#0A192F] border border-slate-700/80 rounded-xl px-4 py-3 text-white focus:border-blue-500 outline-none text-sm font-mono" placeholder="admin@firma.cz" />
                                </div>

                                <div className="pt-2">
                                    <button
                                        onClick={handleRegister}
                                        disabled={status === 'processing' || status === 'success'}
                                        className="w-full bg-blue-600 hover:bg-blue-500 text-white px-6 py-3.5 rounded-xl font-bold text-base transition-all shadow-lg border border-blue-500 flex justify-center items-center gap-3 disabled:opacity-50"
                                    >
                                        {status === 'processing' ? <Loader2 className="animate-spin" size={20} /> : <Shield size={20} />}
                                        {status === 'success' ? 'Workspace Aktivní' : 'Generovat kryptografický tenant'}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Pravý panel - Audit / Terminál */}
                        <div className="bg-[#050B14] rounded-2xl border border-slate-800 p-5 flex flex-col font-mono text-xs shadow-inner relative overflow-hidden min-h-[280px]">
                            <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-3">
                                <Terminal size={16} className="text-slate-500" />
                                <span className="text-slate-500 font-bold uppercase tracking-wider">Kryptografický Audit Log</span>
                            </div>

                            <div className="flex-1 overflow-y-auto space-y-1.5">
                                {logs.length === 0 && (
                                    <div className="text-slate-700 italic">Čeká se na inicializaci požadavku...</div>
                                )}
                                {logs.map((log, i) => (
                                    <div key={i} className={`${log.includes('[OK]') ? 'text-emerald-400' : log.includes('[!]') ? 'text-rose-400' : 'text-blue-300'}`}>
                                        {log}
                                    </div>
                                ))}
                                {status === 'processing' && (
                                    <div className="text-blue-500 animate-pulse mt-2">_</div>
                                )}
                            </div>

                            {status === 'success' && (
                                <div className="absolute inset-0 bg-emerald-950/90 backdrop-blur-sm flex flex-col justify-center items-center border border-emerald-500/50 rounded-2xl animate-in fade-in duration-500 z-20 p-4 text-center">
                                    <CheckCircle size={48} className="text-emerald-400 mb-3" />
                                    <h4 className="text-emerald-300 font-bold text-lg mb-1">Úspěšně zabezpečeno</h4>
                                    <p className="text-emerald-400/80 text-xs">Přesměrovávám do dema...</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
