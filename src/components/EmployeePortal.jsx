import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { ShieldCheck, Fingerprint, Lock, FileText, CheckCircle, Clock, Eye, AlertCircle, LogOut, User, RefreshCw } from 'lucide-react';

import { API_BASE_URL as BACKEND_URL } from '../utils/config';
import { initiateIdentityRecovery } from '../utils/mojeidAuth';

export const EmployeePortal = () => {
    const location = useLocation();
    const [token, setToken] = useState(null);
    const [vaultData, setVaultData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [errorMsg, setErrorMsg] = useState('');
    const [isRecovering, setIsRecovering] = useState(false);

    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        let currentToken = queryParams.get('mojeid_token') || localStorage.getItem('employee_token');

        if (currentToken) {
            setToken(currentToken);
            localStorage.setItem('employee_token', currentToken);
            fetchVault(currentToken);
            window.history.replaceState({}, document.title, "/employee");
        } else {
            setIsLoading(false);
        }
    }, [location]);

    const fetchVault = async (jwt) => {
        try {
            const res = await fetch(`${BACKEND_URL}/employee/vault-v2`, {
                headers: { 'Authorization': `Bearer ${jwt}` }
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Neplatná odpověď serveru');

            const parsedDocs = data.documents.map(doc => {
                let parsed = {};
                try { parsed = JSON.parse(decodeURIComponent(escape(atob(doc.encrypted_payload)))); } catch (e) {}
                return { ...doc, parsed };
            });

            setVaultData({ ...data, documents: parsedDocs });
            setErrorMsg('');
        } catch (err) {
            setErrorMsg(err.message);
            localStorage.removeItem('employee_token');
            setToken(null);
        } finally {
            setIsLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('employee_token');
        window.location.reload();
    };

    const handleRecoveryClick = async () => {
        try {
            setIsRecovering(true);
            const res = await initiateIdentityRecovery();
            if (res.redirect_url) {
                window.location.href = res.redirect_url;
            } else {
                throw new Error('Server nevrátil URL pro obnovu přístupu.');
            }
        } catch (err) {
            setErrorMsg(err.message || 'Nepodařilo se spustit obnovu identity.');
            setIsRecovering(false);
        }
    };

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleString('cs-CZ', {
            day: '2-digit', month: 'long', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-slate-50"><div className="animate-spin text-blue-600"><Clock size={40}/></div></div>;

    if (!token) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-50 text-slate-900">
                {errorMsg && (
                    <div className="max-w-md w-full bg-rose-50 border border-rose-200 text-rose-700 p-4 rounded-2xl mb-6 shadow-sm flex items-start gap-3 animate-fade-in">
                        <AlertCircle size={24} className="flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="font-bold text-sm">Chyba autentizace</p>
                            <p className="text-xs">{errorMsg}</p>
                        </div>
                    </div>
                )}
                <div className="max-w-md w-full bg-white rounded-3xl p-10 shadow-2xl border border-slate-100 text-center space-y-6">
                    <div className="w-20 h-20 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto shadow-sm border border-blue-100 mb-2">
                        <Fingerprint size={40} />
                    </div>
                    <h2 className="text-3xl font-black tracking-tight text-slate-900">Váš Osobní Trezor</h2>
                    <p className="text-slate-600 text-base leading-relaxed">
                        Přihlaste se pomocí své bankovní identity nebo MojeID. Získáte bezpečný přístup ke svým pracovním smlouvám.
                    </p>
                    <a href={`${BACKEND_URL}/mojeid/login`} className="block w-full py-4 mt-4 bg-[#005AA8] hover:bg-[#004A8B] text-white rounded-xl font-bold text-lg transition-transform hover:-translate-y-0.5 shadow-lg flex items-center justify-center gap-3">
                        <Fingerprint size={20} /> Přihlásit přes e-Identitu
                    </a>
                    
                    {/* Sekce pro obnovu při ztrátě zařízení */}
                    <div className="pt-4 border-t border-slate-100 mt-6">
                        <button 
                            onClick={handleRecoveryClick}
                            disabled={isRecovering}
                            className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-semibold text-sm transition-colors flex items-center justify-center gap-2"
                        >
                            <RefreshCw size={16} className={isRecovering ? "animate-spin" : ""} /> 
                            {isRecovering ? 'Inicializace obnovy...' : 'Ztracené zařízení / Obnovit přístup'}
                        </button>
                    </div>

                    <div className="text-xs text-slate-400 flex items-center justify-center gap-1 mt-4">
                        <Lock size={12}/> Chráněno šifrováním lokálního zařízení
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
                <div className="bg-white rounded-[2rem] p-8 border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-6">
                        <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center border border-blue-200">
                            <User size={32} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-black text-slate-900">{vaultData?.name}</h1>
                            <p className="text-slate-500 font-medium">{vaultData?.email}</p>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold rounded-xl transition-colors flex items-center gap-2">
                        <LogOut size={18}/> Odhlásit se
                    </button>
                </div>

                <h2 className="text-2xl font-black text-slate-800 flex items-center gap-3 pl-4">
                    <FileText className="text-blue-600"/> Vaše dokumenty
                </h2>

                {vaultData?.documents?.length === 0 ? (
                    <div className="bg-white rounded-3xl p-12 text-center border border-slate-200 shadow-sm">
                        <ShieldCheck size={64} className="mx-auto text-slate-300 mb-4"/>
                        <h3 className="text-xl font-bold text-slate-600">Váš trezor je zatím prázdný</h3>
                        <p className="text-slate-500 mt-2">Nemáte zde žádné aktivní ani čekající smlouvy.</p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {vaultData?.documents.map((doc, i) => (
                            <div key={i} className="bg-white rounded-[2rem] border border-slate-200 shadow-md overflow-hidden">
                                <div className="p-8 border-b border-slate-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-50/50">
                                    <div>
                                        <div className="flex items-center gap-3 mb-2">
                                            <h3 className="text-xl font-black text-slate-900">
                                                {doc.parsed.type === 'HPP' ? 'Pracovní smlouva' : (doc.parsed.type || 'Smlouva')}
                                            </h3>
                                            <span className="bg-blue-100 text-blue-800 text-xs font-black px-3 py-1 rounded-full uppercase tracking-wider">
                                                {doc.parsed.position || 'Dokument'}
                                            </span>
                                        </div>
                                        <p className="text-slate-500 font-medium">Vystaveno: {formatDate(doc.created_at)}</p>
                                    </div>
                                    <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-2 rounded-xl flex items-center gap-2 font-bold text-sm">
                                        <CheckCircle size={18}/> {doc.status === 'signed' ? 'Platná a podepsaná' : 'Zpracovává se'}
                                    </div>
                                </div>

                                <div className="grid md:grid-cols-2">
                                    <div className="p-8 border-r border-slate-100">
                                        <h4 className="text-sm font-black text-slate-400 uppercase tracking-widest mb-6">Základní informace</h4>
                                        <div className="space-y-4">
                                            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                                <p className="text-xs font-bold text-slate-500 uppercase mb-1">Místo výkonu</p>
                                                <p className="font-bold text-slate-800">{doc.parsed.workLocation || '-'}</p>
                                            </div>
                                            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                                <p className="text-xs font-bold text-slate-500 uppercase mb-1">Odměna</p>
                                                <p className="font-bold text-emerald-600 text-lg">{doc.parsed.salary || '-'} CZK</p>
                                            </div>
                                            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                                <p className="text-xs font-bold text-slate-500 uppercase mb-1">Den nástupu</p>
                                                <p className="font-bold text-slate-800">{doc.parsed.startDate || '-'}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-8 bg-blue-50/30">
                                        <h4 className="text-sm font-black text-blue-900 uppercase tracking-widest mb-6 flex items-center gap-2">
                                            <Eye size={18}/> Kdo a kdy smlouvu viděl?
                                        </h4>
                                        <p className="text-sm text-slate-600 mb-6 leading-relaxed">
                                            Systém automaticky zaznamenává, kdykoliv zástupce HR oddělení otevře tento dokument. Máte tak naprostou kontrolu nad svými osobními údaji.
                                        </p>

                                        {doc.access_history && doc.access_history.length > 0 ? (
                                            <div className="space-y-3 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
                                                {doc.access_history.map((timestamp, idx) => (
                                                    <div key={idx} className="bg-white border border-blue-100 p-4 rounded-xl flex items-center gap-4 shadow-sm">
                                                        <div className="bg-blue-100 p-2 rounded-lg text-blue-600"><Clock size={20}/></div>
                                                        <div>
                                                            <p className="font-bold text-slate-800 text-sm">Zobrazeno HR oddělením</p>
                                                            <p className="text-xs text-slate-500">{formatDate(timestamp)}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="bg-white border border-slate-200 p-6 rounded-xl text-center shadow-sm">
                                                <ShieldCheck size={32} className="mx-auto text-emerald-500 mb-3"/>
                                                <p className="font-bold text-slate-800">Smlouvu zatím nikdo neotevřel.</p>
                                                <p className="text-xs text-slate-500 mt-1">Vaše data jsou aktuálně uzamčena v šifrovaném stavu.</p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
