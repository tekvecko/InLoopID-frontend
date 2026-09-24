import React, { useState } from 'react';
import { ShieldCheck, Lock, ArrowRight, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

export const VerifierPortal = () => {
  const [verifierId, setVerifierId] = useState('Komerční Banka a.s.');
  const [threshold, setThreshold] = useState(35000);
  const [challengeData, setChallengeData] = useState(null);
  
  const [credentialId, setCredentialId] = useState('');
  const [proof, setProof] = useState('');
  const [attributeData, setAttributeData] = useState('');
  
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCreateChallenge = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/verifier/challenge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          verifier_id: verifierId,
          predicate_type: 'salary_threshold',
          threshold: Number(threshold)
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Chyba při vytváření výzvy');
      setChallengeData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPresentation = async (e) => {
    e.preventDefault();
    if (!challengeData) return;
    setLoading(true);
    setError(null);
    setVerificationResult(null);

    try {
      const res = await fetch('/api/v1/verifier/verify-presentation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_nonce: challengeData.challenge_nonce,
          proof,
          credential_id: credentialId,
          attribute_data: attributeData
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Chyba při ověřování prezentace');
      setVerificationResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <ShieldCheck className="text-blue-500 w-8 h-8" /> InLoopID Verifier Gateway
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Bezpečné ověřování mzdových predikátů třetí stranou pomocí Zero-Knowledge důkazů (GDPR & eIDAS compliant).
            </p>
          </div>
          <span className="px-3 py-1 bg-blue-950 text-blue-400 border border-blue-800 rounded-full text-xs font-semibold">
            Zero-Knowledge Zóna
          </span>
        </div>

        {error && (
          <div className="bg-red-950/50 border border-red-800 text-red-200 p-4 rounded-xl flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Krok 1: Vytvoření Challenge */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">1</span>
              Vytvořit výzvu (Verifier Challenge)
            </h2>
            <form onSubmit={handleCreateChallenge} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Název verifikátora (např. Banka)</label>
                <input 
                  type="text" 
                  value={verifierId} 
                  onChange={e => setVerifierId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Minimální čistý příjem (Kč)</label>
                <input 
                  type="number" 
                  value={threshold} 
                  onChange={e => setThreshold(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
              >
                Vygenerovat Challenge <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            {challengeData && (
              <div className="mt-4 p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Challenge aktivní
                </span>
                <div className="text-xs text-slate-400 break-all font-mono">
                  <strong>Nonce:</strong> {challengeData.challenge_nonce}
                </div>
              </div>
            )}
          </div>

          {/* Krok 2: Ověření ZK Proofu */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs">2</span>
              Ověřit ZK Presentation od zaměstnance
            </h2>
            <form onSubmit={handleVerifyPresentation} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Credential ID (VC Anchor)</label>
                <input 
                  type="text" 
                  value={credentialId} 
                  onChange={e => setCredentialId(e.target.value)}
                  placeholder="např. vc-uuid-12345"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">ZK Proof / Commitment řetězec</label>
                <input 
                  type="text" 
                  value={proof} 
                  onChange={e => setProof(e.target.value)}
                  placeholder="kryptografický důkaz"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Atributová data / Hash</label>
                <input 
                  type="text" 
                  value={attributeData} 
                  onChange={e => setAttributeData(e.target.value)}
                  placeholder="hash obsahu smlouvy"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>
              <button 
                type="submit" 
                disabled={loading || !challengeData}
                className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium py-3 rounded-lg text-sm transition-colors flex items-center justify-center gap-2"
              >
                Ověřit důkaz <Lock className="w-4 h-4" />
              </button>
            </form>

            {verificationResult && (
              <div className="mt-4 p-4 bg-slate-950 border border-emerald-900 rounded-xl space-y-2">
                <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-4 h-4" /> Ověření zadáno do fronty
                </span>
                <div className="text-xs text-slate-400 font-mono">
                  Task ID: {verificationResult.task_id}
                </div>
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};
