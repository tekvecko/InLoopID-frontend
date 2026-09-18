import React, { useState } from 'react';
import { Building, ShieldCheck, Key, CheckCircle, Copy, ArrowRight, AlertTriangle } from 'lucide-react';
import { generateRSAKeyPair, exportPublicKeyJWK, exportPrivateKeyJWK, encryptKeystore } from '../utils/cryptoEngine';

const BACKEND_URL = 'http://localhost:5000/api/v1';

export const B2BRegister = () => {
  const [formData, setFormData] = useState({ company_name: '', ico: '', admin_email: '' });
  const [status, setStatus] = useState('form'); 
  const [generatedKey, setGeneratedKey] = useState('');
  const [tenantId, setTenantId] = useState('');
  const [error, setError] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    setStatus('generating');
    setError(null);

    const generatedTenantId = formData.company_name.toLowerCase().replace(/[^a-z0-9]/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '') + '-' + Math.floor(1000 + Math.random() * 9000);
    setTenantId(generatedTenantId);

    const newMasterKey = Array.from(window.crypto.getRandomValues(new Uint8Array(16))).map(b => b.toString(16).padStart(2, '0')).join('');
    setGeneratedKey(newMasterKey);

    try {
      const encKeys = await generateRSAKeyPair();
      const pubJwk = await exportPublicKeyJWK(encKeys.publicKey);
      const privJwk = await exportPrivateKeyJWK(encKeys.privateKey);
      
      const { iv, encryptedBlob } = await encryptKeystore({ privateKey: privJwk }, newMasterKey, "HR_SALT");

      const response = await fetch(`${BACKEND_URL}/b2b/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, tenant_id: generatedTenantId, public_key_jwk: JSON.stringify(pubJwk), encrypted_private_key: encryptedBlob, private_key_iv: iv })
      });

      if (response.ok) { setStatus('success'); } else {
        const data = await response.json(); setError(data.error); setStatus('form');
      }
    } catch (err) { setError("Kryptografická chyba."); setStatus('form'); }
  };

  const copyToClipboard = () => { navigator.clipboard.writeText(generatedKey); alert("Klíč zkopírován!"); };

  if (status === 'success') {
    return (
      <div className="min-h-screen p-6 bg-slate-900 flex justify-center items-center text-white">
        <div className="max-w-2xl w-full bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-2xl animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-emerald-900/30 text-emerald-400 rounded-full mb-6"><CheckCircle size={40} /></div>
          <h2 className="text-3xl font-bold mb-4">Vítejte v InLoopID Enterprise!</h2>
          <p className="text-slate-400 mb-8">Nyní můžete začít zvát kandidáty přes odkaz: <br/><code className="text-indigo-400">/join/{tenantId}</code></p>
          <div className="bg-rose-900/20 border border-rose-900/50 rounded-2xl p-6 mb-8 text-left">
            <h3 className="text-rose-400 font-bold flex items-center gap-2 mb-4"><AlertTriangle size={20}/> TENTO KLÍČ NIKDY NEOPUSTIL VÁŠ PROHLÍŽEČ</h3>
            <p className="text-sm text-slate-300 mb-4">Toto je hlavní dešifrovací heslo pro agendu. Uložte si ho!</p>
            <div className="bg-slate-950 border border-slate-700 p-4 rounded-xl flex justify-between items-center">
               <code className="text-emerald-400 font-mono text-lg">{generatedKey}</code>
               <button onClick={copyToClipboard} className="text-slate-400 hover:text-white"><Copy size={24}/></button>
            </div>
          </div>
          <div className="flex gap-4"><a href="/hr" className="flex-1 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold text-center flex justify-center items-center gap-2">Přejít do HR Velína <ArrowRight size={20}/></a></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 bg-slate-900 flex justify-center items-center text-white">
      <div className="max-w-xl w-full bg-slate-800 border border-slate-700 rounded-3xl p-8 shadow-2xl">
        <div className="flex items-center gap-4 mb-8"><Building size={40} className="text-indigo-400" /><div><h2 className="text-2xl font-bold">Registrace Firmy</h2><p className="text-sm text-slate-400">Vytvořte si Zero-Knowledge HR systém.</p></div></div>
        {error && <div className="mb-6 p-4 bg-rose-900/20 text-rose-400 border border-rose-900/50 rounded-xl flex items-center gap-2 text-sm"><AlertTriangle size={16}/> {error}</div>}
        <form onSubmit={handleRegister} className="space-y-6">
          <div><label className="text-xs text-slate-400 font-bold block mb-2 uppercase">Název Společnosti</label><input type="text" required value={formData.company_name} onChange={e => setFormData({...formData, company_name: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 text-white outline-none" /></div>
          <div><label className="text-xs text-slate-400 font-bold block mb-2 uppercase">E-mail administrátora</label><input type="email" required value={formData.admin_email} onChange={e => setFormData({...formData, admin_email: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-4 text-white outline-none" /></div>
          <button type="submit" disabled={status === 'generating'} className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-bold flex justify-center items-center gap-3 mt-8">{status === 'generating' ? 'Generuji Zero-Knowledge prostředí...' : <><Key size={20} /> Vytvořit Firemní Trezor</>}</button>
        </form>
      </div>
    </div>
  );
};
