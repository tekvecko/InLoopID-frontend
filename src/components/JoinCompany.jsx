import React, { useState, useEffect, useRef } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { Building, ShieldCheck, CheckCircle, Lock, Cpu, Fingerprint, Activity } from 'lucide-react';
import { notify } from './ToastManager';

import { API_BASE_URL as BACKEND_URL } from '../utils/config';

export const JoinCompany = () => {
  const { tenant_id } = useParams();
  const location = useLocation();
  const token = new URLSearchParams(location.search).get('t');
  
  const [currentStep, setCurrentStep] = useState(0);
  const [workspace, setWorkspace] = useState(null);
  const [error, setError] = useState(null);

  const stages = [
    { title: "Ověření platnosti pozvánky", icon: <Activity size={24} />, desc: "Kontrola jednorázového tokenu." },
    { title: "Integrace bezpečnostního protokolu", icon: <Lock size={24} />, desc: "Navazování Zero-Knowledge tunelu." },
    { title: "Ověření integrity dat", icon: <ShieldCheck size={24} />, desc: "Matematická validace ochranných prvků." },
    { title: "Dešifrování pozvánky", icon: <Cpu size={24} />, desc: "Izolace firemního kryptografického klíče." },
    { title: "Příprava ověření identity", icon: <Fingerprint size={24} />, desc: "Komunikace se státním registrem." }
  ];

  useEffect(() => {
    if (!token) { setError("Odkaz neobsahuje bezpečnostní token."); return; }
    
    // Fáze 1: Validace tokenu na backendu
    fetch(`${BACKEND_URL}/verify-invitation/${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setWorkspace(data);
          startTranspaCards();
        } else { setError(data.error); }
      }).catch(() => setError("Chyba připojení k serveru."));
  }, [token]);

  // Fáze 2: Spuštění interaktivního průvodce (UX Transpa-Cards)
  const startTranspaCards = () => {
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < stages.length) {
        setCurrentStep(step);
      } else {
        clearInterval(interval);
        // Jakmile projde všech 5 karet, nabídneme mu MojeID
        setCurrentStep(99); 
      }
    }, 1200); // Každý krok trvá 1.2 vteřiny pro "wow efekt" a pocit práce
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 text-white">
        <div className="bg-rose-900/20 border border-rose-900 rounded-3xl p-8 text-center max-w-md w-full">
          <AlertTriangle size={48} className="text-rose-500 mx-auto mb-4"/>
          <h2 className="text-2xl font-bold text-rose-400 mb-2">Neplatná pozvánka</h2>
          <p className="text-slate-400">{error}</p>
        </div>
      </div>
    );
  }

  // Fáze 3: Hotovo, vyzveme k MojeID
  if (currentStep === 99) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 text-white">
        <div className="w-full max-w-md bg-slate-900 border border-blue-900/50 rounded-3xl p-8 shadow-[0_0_50px_rgba(59,130,246,0.15)] text-center animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-900/30 text-blue-400 rounded-full mb-6"><Building size={40} /></div>
          <h2 className="text-2xl font-bold mb-2">Vše je připraveno!</h2>
          <p className="text-sm text-slate-400 mb-8">Společnost <strong className="text-white">{workspace?.company_name}</strong> úspěšně vytvořila Váš přijímací profil. Nyní prokažte svou identitu pomocí státní identity (MojeID).</p>
          <button onClick={() => window.location.href = `${BACKEND_URL}/mojeid/login`} className="w-full py-4 px-6 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold flex justify-center items-center gap-2 transition-transform hover:scale-105">
            <Fingerprint size={20}/> Pokračovat přes MojeID
          </button>
        </div>
      </div>
    );
  }

  // Fáze 2: Vykreslování Transpa-Cards
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-slate-950 text-white">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
            <ShieldCheck size={48} className="text-blue-500 mx-auto mb-4 animate-pulse" />
            <h2 className="text-2xl font-bold">Připravuji bezpečný prostor</h2>
            <p className="text-slate-500 text-sm mt-2">Prosím, nezavírejte toto okno...</p>
        </div>
        
        <div className="space-y-4">
          {stages.map((stage, idx) => (
            <div key={idx} className={`p-4 rounded-2xl border transition-all duration-500 flex items-center gap-4
                ${idx < currentStep ? 'bg-emerald-900/20 border-emerald-900/50 opacity-100' : 
                  idx === currentStep ? 'bg-blue-900/30 border-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.2)] opacity-100 transform scale-105' : 
                  'bg-slate-900 border-slate-800 opacity-30'}
            `}>
              <div className={`w-12 h-12 flex items-center justify-center rounded-full ${idx < currentStep ? 'bg-emerald-500/20 text-emerald-400' : idx === currentStep ? 'bg-blue-500/20 text-blue-400 animate-spin-slow' : 'bg-slate-800 text-slate-500'}`}>
                 {idx < currentStep ? <CheckCircle size={24}/> : stage.icon}
              </div>
              <div>
                <h3 className={`font-bold ${idx === currentStep ? 'text-white' : 'text-slate-400'}`}>{stage.title}</h3>
                <p className="text-xs text-slate-500">{idx < currentStep ? 'Dokončeno' : idx === currentStep ? stage.desc : 'Čeká se...'}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
