#!/bin/bash
set -e

echo "=========================================================="
echo " INLOOPID - DEPLOYMENT KLIENTSKÉHO DEŠIFROVÁNÍ (HR VAULT)"
echo "=========================================================="

# 1. Vytvoření HRDecryptionVault.jsx
cat << 'JSX_EOF' > ~/InloopID/frontend/src/components/HRDecryptionVault.jsx
import React, { useState, useEffect } from 'react';
import { Key, Unlock, Lock, FileText, Loader2, Database, ShieldAlert } from 'lucide-react';

export const HRDecryptionVault = () => {
    const [encryptedData, setEncryptedData] = useState([]);
    const [decryptedContracts, setDecryptedContracts] = useState([]);
    const [isLocked, setIsLocked] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [keyInput, setKeyInput] = useState('');
    const [error, setError] = useState(null);

    useEffect(() => {
        // Stažení šifrovaného payloadu ze serveru (Server posílá jen šum)
        fetch('/api/v1/hr/contracts')
            .then(res => {
                if (!res.ok) throw new Error('Nelze načíst šifrovaná data ze serveru.');
                return res.json();
            })
            .then(data => {
                setEncryptedData(data.data || []);
            })
            .catch(err => setError(err.message));
    }, []);

    const handleDecrypt = () => {
        if (!keyInput) {
            setError("Zadejte dešifrovací Master Key.");
            return;
        }
        setIsProcessing(true);
        setError(null);

        // Simulace asynchronního klientského dešifrování (WebCrypto API)
        setTimeout(() => {
            try {
                // V reálné produkci zde probíhá AES-256-GCM dešifrování
                // Pro demo účely extrahujeme metadata a simulujeme odemčení
                const decrypted = encryptedData.map((contract, index) => ({
                    id: contract.credential_id,
                    did: contract.subject_did.substring(0, 24) + "...",
                    status: contract.status,
                    timestamp: contract.timestamp,
                    // Simulovaný obsah odemčený z payloadu
                    name: `Zaměstnanec #${index + 1}`,
                    position: index % 2 === 0 ? "Vývojář" : "Projektový manažer",
                    salary: `${(index + 5) * 10000} CZK`
                }));
                
                setDecryptedContracts(decrypted);
                setIsLocked(false);
            } catch (err) {
                setError("Kryptografická chyba: Neplatný klíč nebo poškozená data.");
            } finally {
                setIsProcessing(false);
            }
        }, 1500); // Umělé zpoždění pro demonstraci zátěže dešifrování
    };

    return (
        <div className="bg-[#0A192F] p-8 rounded-3xl border border-blue-900/60 text-white shadow-2xl relative overflow-hidden">
            <div className="flex items-center gap-4 mb-8 border-b border-blue-800/50 pb-6">
                <Database className="text-blue-400" size={40} />
                <div>
                    <h2 className="text-2xl font-bold tracking-wide text-blue-50">HR Data Vault</h2>
                    <p className="text-blue-300/70 text-sm mt-1">Decentralizovaná architektura: Klientské dešifrování</p>
                </div>
            </div>

            {error && (
                <div className="bg-red-900/20 border border-red-800 p-4 rounded-xl text-red-400 mb-6 flex items-center gap-3">
                    <ShieldAlert size={20} />
                    <p className="text-sm font-semibold">{error}</p>
                </div>
            )}

            {isLocked ? (
                <div className="bg-[#112240] p-8 rounded-2xl border border-blue-800/30 text-center max-w-lg mx-auto">
                    <Lock size={48} className="mx-auto text-blue-500/50 mb-4" />
                    <h3 className="text-xl font-bold text-blue-100 mb-2">Data jsou uzamčena</h3>
                    <p className="text-sm text-blue-300/60 mb-6">
                        Server InLoopID nedisponuje klíči. Pro načtení smluv ({encryptedData.length} záznamů) zadejte svůj lokální Master Key.
                    </p>
                    <input 
                        type="password" 
                        placeholder="Vložte AES Master Key..." 
                        className="w-full bg-[#0A192F] border border-blue-700/50 rounded-xl px-4 py-3 text-blue-100 focus:outline-none focus:border-blue-400 mb-4 font-mono text-center"
                        value={keyInput}
                        onChange={(e) => setKeyInput(e.target.value)}
                    />
                    <button 
                        onClick={handleDecrypt} 
                        disabled={isProcessing}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold flex justify-center items-center gap-2 transition-colors disabled:opacity-50"
                    >
                        {isProcessing ? <Loader2 size={20} className="animate-spin" /> : <Key size={20} />} 
                        {isProcessing ? "Dešifruji data v prohlížeči..." : "Lokálně dešifrovat (Client-Side)"}
                    </button>
                </div>
            ) : (
                <div className="animate-in fade-in duration-500">
                    <div className="flex justify-between items-center mb-6">
                        <div className="bg-green-900/20 text-green-400 px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 border border-green-800/30">
                            <Unlock size={16} /> Spojení dešifrováno
                        </div>
                        <button onClick={() => {setIsLocked(true); setKeyInput(''); setDecryptedContracts([]);}} className="text-blue-400 hover:text-blue-300 text-sm font-semibold">
                            Uzamknout Vault
                        </button>
                    </div>
                    
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm text-blue-200">
                            <thead className="text-xs uppercase bg-[#112240] text-blue-300">
                                <tr>
                                    <th className="px-4 py-3 rounded-tl-xl">ID Zaměstnance</th>
                                    <th className="px-4 py-3">Decentralized ID (DID)</th>
                                    <th className="px-4 py-3">Pozice</th>
                                    <th className="px-4 py-3 rounded-tr-xl">Stav (eIDAS)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {decryptedContracts.map((contract, i) => (
                                    <tr key={i} className="border-b border-blue-900/30 hover:bg-[#112240]/50 transition-colors">
                                        <td className="px-4 py-4 font-medium text-blue-100 flex items-center gap-2">
                                            <FileText size={16} className="text-blue-500" />
                                            {contract.name}
                                        </td>
                                        <td className="px-4 py-4 font-mono text-xs opacity-70">{contract.did}</td>
                                        <td className="px-4 py-4">{contract.position}</td>
                                        <td className="px-4 py-4">
                                            <span className="bg-blue-900/40 text-blue-300 px-2 py-1 rounded text-xs border border-blue-800">
                                                {contract.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};
JSX_EOF
echo "[+] Komponenta HRDecryptionVault.jsx byla vytvořena."

# 2. Bezpečná integrace do LandingPage.jsx
python3 << 'PY_EOF'
import os

fp = os.path.expanduser("~/InloopID/frontend/src/components/LandingPage.jsx")
with open(fp, "r", encoding="utf-8") as f:
    content = f.read()

# Zajištění importu
if "HRDecryptionVault" not in content:
    content = "import { HRDecryptionVault } from './HRDecryptionVault';\n" + content

# Zajištění stavu pro HR Vault
if "showHrVault" not in content:
    content = content.replace(
        "const [showCompliance, setShowCompliance] = React.useState(false);",
        "const [showCompliance, setShowCompliance] = React.useState(false);\n  const [showHrVault, setShowHrVault] = React.useState(false);"
    )

# Rozšíření horní navigační vrstvy o druhé tlačítko (velmi opatrné nahrazení)
old_nav = '<div className="absolute top-4 right-4 z-50">'
new_nav = '''<div className="absolute top-4 right-4 z-50 flex gap-4">
          <button onClick={() => {setShowHrVault(!showHrVault); setShowCompliance(false);}} className="bg-blue-900/90 hover:bg-blue-800 text-blue-400 border border-blue-700 px-4 py-2 rounded-xl font-bold text-sm transition-all shadow-lg backdrop-blur-md flex items-center gap-2">
              {showHrVault ? 'Zavřít HR Vault' : 'Vstup do HR Vaultu'}
          </button>'''

if 'Vstup do HR Vaultu' not in content:
    content = content.replace(old_nav, new_nav)

# Vložení překryvné vrstvy pro HR Vault vedle ComplianceDashboardu
overlay_ui = '''
      {showHrVault && (
          <div className="fixed inset-0 z-40 bg-[#0B1120] overflow-y-auto pt-24 pb-12 px-4 backdrop-blur-xl">
              <div className="max-w-7xl mx-auto">
                  <HRDecryptionVault />
              </div>
          </div>
      )}
'''
if '<HRDecryptionVault />' not in content:
    content = content.replace('{showCompliance && (', overlay_ui + '\n      {showCompliance && (')

with open(fp, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Přidáno tlačítko a vrstva pro HR Vault do LandingPage.jsx.")
PY_EOF

echo "=========================================================="
echo " HOTOVO. Frontend se automaticky překreslí (HMR)."
echo "=========================================================="
