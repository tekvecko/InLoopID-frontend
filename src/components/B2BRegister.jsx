import React, { useState } from 'react';
import { Building, Key, CheckCircle, Copy, ArrowRight, AlertTriangle, CreditCard, Check, Zap } from 'lucide-react';
import { generateRSAKeyPair, exportPublicKeyJWK, exportPrivateKeyJWK, encryptKeystore } from '../utils/cryptoEngine';

const BACKEND_URL = `http://${window.location.hostname}:5000/api/v1`;

export const B2BRegister = () => {
  const [step, setStep] = useState(1);
  const [selectedPlan, setSelectedPlan] = useState('standard');
  const [formData, setFormData] = useState({ company_name: '', ico: '', admin_email: '' });
  const [status, setStatus] = useState('idle'); 
  const [generatedKey, setGeneratedKey] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [error, setError] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    setStatus('generating');
    setError(null);
    setStep(3);

    // KOREKTNÍ SLUGIFIKACE: Zachová text, odstraní háčky/čárky a převede na bezpečný URL formát
    const baseSlug = formData.company_name
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '') || 'firma'; // Fallback pro případ čistě symbolických názvů
      
    const generatedTenantId = `${baseSlug}-${Math.floor(1000 + Math.random() * 9000)}`;
    setTenantId(generatedTenantId);

    const newMasterKey = Array.from(window.crypto.getRandomValues(new Uint8Array(16))).map(b => b.toString(16).padStart(2, '0')).join('');
    setGeneratedKey(newMasterKey);

    try {
      await new Promise(resolve => setTimeout(resolve, 1500)); // Stripe Mock

      const encKeys = await generateRSAKeyPair();
      const pubJwk = await exportPublicKeyJWK(encKeys.publicKey);
      const privJwk = await exportPrivateKeyJWK(encKeys.privateKey);
      const { iv, encryptedBlob } = await encryptKeystore({ privateKey: privJwk }, newMasterKey, "HR_SALT");

      const response = await fetch(`${BACKEND_URL}/b2b/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            ...formData, tenant_id: generatedTenantId, subscription_plan: selectedPlan,
            public_key_jwk: JSON.stringify(pubJwk), encrypted_private_key: encryptedBlob, private_key_iv: iv 
        })
      });

      if (response.ok) { 
          setStatus('success'); 
      } else {
          // BEZPEČNÉ PARSOVÁNÍ CHYBY Z BACKENDU
          let errorMsg = "Neznámá chyba serveru.";
          try {
             const data = await response.json();
             errorMsg = data.error || errorMsg;
          } catch (parseErr) {
             errorMsg = `Kritická chyba backendu (Status: ${response.status})`;
          }
          setError(errorMsg); 
          setStep(2); 
          setStatus('idle');
      }
    } catch (err) { 
        // SKUTEČNÁ KRYPTOGRAFICKÁ NEBO SÍŤOVÁ CHYBA
        setError(`Systémová chyba: ${err.message}`); 
        setStep(2); 
        setStatus('idle'); 
    }
  };

  const copyToClipboard = () => { navigator.clipboard.writeText(generatedKey); alert("Klíč zkopírován!"); };

  if (step === 1) {
    return (
      <div className="min-h-screen p-6 bg-slate-950 flex flex-col justify-center items-center text-white">
        <div className="text-center mb-12">
           <h2 className="text-3xl font-extrabold text-white mb-4">Zvolte ochranu pro Vaši firmu</h2>
           <p className="text-slate-400">Přeneste rizika GDPR a pracovněprávních sporů na naši technologii.</p>
        </div>
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl w-full">
           <div onClick={() => setSelectedPlan('standard')} className={`cursor-pointer rounded-3xl p-8 border-2 transition-all duration-300 ${selectedPlan === 'standard' ? 'bg-blue-950 border-blue-500 shadow-xl shadow-blue-900/20 transform -translate-y-2' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}>
             <h3 className="text-2xl font-bold text-white mb-2">Standard</h3>
             <div className="flex items-baseline gap-2 mb-6"><span className="text-4xl font-extrabold">2 990 Kč</span><span className="text-slate-400">/ měsíc</span></div>
             <ul className="space-y-4 mb-8">
               <li className="flex items-center gap-3"><Check size={20} className="text-blue-400"/> Až 50 zaměstnanců</li>
               <li className="flex items-center gap-3"><Check size={20} className="text-blue-400"/> ZK Kryptografický Trezor</li>
             </ul>
             <button onClick={() => setStep(2)} className={`w-full py-4 rounded-xl font-bold transition-colors ${selectedPlan === 'standard' ? 'bg-blue-600 text-white hover:bg-blue-500' : 'bg-slate-800 text-slate-300'}`}>Zvolit Standard</button>
           </div>
           <div onClick={() => setSelectedPlan('enterprise')} className={`cursor-pointer relative rounded-3xl p-8 border-2 transition-all duration-300 ${selectedPlan === 'enterprise' ? 'bg-blue-950 border-blue-500 shadow-xl shadow-blue-900/20 transform -translate-y-2' : 'bg-slate-900 border-slate-800 hover:border-slate-700'}`}>
             {selectedPlan === 'enterprise' && <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-widest"><Zap size={12} className="inline mr-1"/> Doporučeno</div>}
             <h3 className="text-2xl font-bold text-white mb-2">Enterprise</h3>
             <div className="flex items-baseline gap-2 mb-6"><span className="text-4xl font-extrabold">9 990 Kč</span><span className="text-slate-400">/ měsíc</span></div>
             <ul className="space-y-4 mb-8">
               <li className="flex items-center gap-3"><Check size={20} className="text-emerald-400"/> Neomezeně zaměstnanců</li>
               <li className="flex items-center gap-3"><Check size={20} className="text-emerald-400"/> Plně automatizovaný Candidate-Driven nástup</li>
             </ul>
             <button onClick={() => setStep(2)} className={`w-full py-4 rounded-xl font-bold transition-colors ${selectedPlan === 'enterprise' ? 'bg-blue-600 text-white hover:bg-blue-500' : 'bg-slate-800 text-slate-300'}`}>Zvolit Enterprise</button>
           </div>
        </div>
      </div>
    );
  }

  if (step === 2) {
      return (
        <div className="min-h-screen p-6 bg-slate-950 flex justify-center items-center text-white">
          <div className="max-w-xl w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
            <button onClick={() => setStep(1)} className="text-blue-400 text-sm font-bold mb-6 hover:text-blue-300">&larr; Zpět na výběr tarifu</button>
            <div className="flex items-center gap-4 mb-8"><Building size={40} className="text-blue-500" /><div><h2 className="text-2xl font-bold">Fakturační údaje</h2><p className="text-sm text-slate-400">Tarif: <strong className="text-blue-400 uppercase">{selectedPlan}</strong></p></div></div>
            {error && <div className="mb-6 p-4 bg-rose-950 text-rose-400 border border-rose-900 rounded-xl flex items-center gap-2 text-sm"><AlertTriangle size={16}/> {error}</div>}
            <form onSubmit={handleRegister} className="space-y-6">
              <div><label className="text-xs text-slate-400 font-bold block mb-2 uppercase">Název Společnosti</label><input type="text" required value={formData.company_name} onChange={e => setFormData({...formData, company_name: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-white outline-none focus:border-blue-500" /></div>
              <div><label className="text-xs text-slate-400 font-bold block mb-2 uppercase">IČO</label><input type="text" required value={formData.ico} onChange={e => setFormData({...formData, ico: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-white outline-none focus:border-blue-500" /></div>
              <div><label className="text-xs text-slate-400 font-bold block mb-2 uppercase">E-mail administrátora</label><input type="email" required value={formData.admin_email} onChange={e => setFormData({...formData, admin_email: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-white outline-none focus:border-blue-500" /></div>
              <div className="pt-4 border-t border-slate-800">
                 <button type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold flex justify-center items-center gap-3"><CreditCard size={20} /> Přejít k platbě a vygenerovat Trezor</button>
              </div>
            </form>
          </div>
        </div>
      );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen p-6 bg-slate-950 flex justify-center items-center text-white">
        <div className="max-w-2xl w-full bg-blue-950 border border-blue-900 rounded-3xl p-8 shadow-2xl animate-fade-in text-center">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-900/50 text-blue-400 rounded-full mb-6"><CheckCircle size={40} /></div>
          <h2 className="text-3xl font-bold mb-4">Platba přijata. Vítejte v InLoopID!</h2>
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 mb-8 text-left">
            <h3 className="text-rose-400 font-bold flex items-center gap-2 mb-4"><AlertTriangle size={20}/> ULOŽTE SI TENTO ŠIFROVACÍ KLÍČ</h3>
<button onClick={() => {
  const blob = new Blob([JSON.stringify({masterKey: generatedKey, tenant: tenantId})], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "InLoopID_Backup.json";
  a.click();
}} className="w-full mb-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm font-bold transition-colors">Stáhnout bezpečný záložní soubor</button>
            <p className="text-sm text-slate-300 mb-4">Toto je hlavní dešifrovací heslo pro Vaši HR agendu. <b>Server ho nezná a neumíme ho obnovit.</b></p>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex justify-between items-center">
               <code className="text-blue-400 font-mono text-lg">{generatedKey}</code>
               <button onClick={copyToClipboard} className="text-slate-400 hover:text-white"><Copy size={24}/></button>
            </div>
          </div>
          <div className="flex gap-4"><a href="/hr" className="w-full py-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold text-center flex justify-center items-center gap-2">Přejít do HR Velína <ArrowRight size={20}/></a></div>
        </div>
      </div>
    );
  }

  return (
      <div className="min-h-screen p-6 bg-slate-950 flex flex-col justify-center items-center text-white">
          <div className="w-16 h-16 border-4 border-blue-900 border-t-blue-500 rounded-full animate-spin mb-6"></div>
          <h2 className="text-2xl font-bold mb-2">Zpracovávám platbu...</h2>
          <p className="text-blue-400">Probíhá generování armádní Zero-Knowledge kryptografie.</p>
      </div>
  );
};
