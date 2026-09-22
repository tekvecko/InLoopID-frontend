import React, { useState, useEffect } from 'react';
import { pdf } from '@react-pdf/renderer';
import { FileText, Cpu, Server, Database, Building } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import { ContractTemplate } from './ContractTemplate';
import { generateRSAKeyPair, generateSigningKeyPair, generateAESKey, hashDocument, encryptDocument, wrapKey, exportPublicKeyJWK, bufferToBase64 } from '../utils/cryptoEngine';
import { saveIdentity, getAllIdentities } from '../utils/idbStorage';

import { API_BASE_URL as BACKEND_URL } from '../utils/config';

export const ClientDocumentEngine = () => {
  const [status, setStatus] = useState('idle');
  const [walletDid, setWalletDid] = useState(null);
  const [serverLog, setServerLog] = useState([]);
  const [tenantId, setTenantId] = useState('acme_corp'); // SaaS Selector

  useEffect(() => {
    const loadWallet = async () => {
      const identities = await getAllIdentities();
      if (identities.length > 0) setWalletDid(identities[0].did);
    };
    loadWallet();
  }, []);

  const logEvent = (msg) => setServerLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const ensureIdentity = async () => {
    let identities = await getAllIdentities();
    let currentIdentity = identities[0];

    if (!currentIdentity) {
      logEvent('Creating V2 SSI Identity (RSA + ECDSA)...');
      const encKeys = await generateRSAKeyPair();
      const signKeys = await generateSigningKeyPair();
      const jwk = await exportPublicKeyJWK(encKeys.publicKey);
      const didString = `did:key:z${btoa(jwk.n).substring(0, 16)}`; 
      
      await saveIdentity(didString, encKeys, signKeys, jwk);
      currentIdentity = { did: didString, encPublicKey: encKeys.publicKey };
      setWalletDid(didString);
    }

    await fetch(`${BACKEND_URL}/register-identity`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ did_uri: currentIdentity.did, public_key_jwk: "V2_JWK", tenant_id: tenantId })
    });
    return currentIdentity;
  };

  const processDocument = async () => {
    try {
      setStatus('processing');
      setServerLog([]);
      const identity = await ensureIdentity();
      
      const contractData = { employeeName: 'Alice Smith', role: 'Senior Developer', salary: '$120,000' };
      const blob = await pdf(<ContractTemplate {...contractData} />).toBlob();
      const arrayBuffer = await blob.arrayBuffer();
      const sha256Hash = await hashDocument(arrayBuffer);
      const aesKey = await generateAESKey();
      const { iv, encryptedBuffer } = await encryptDocument(arrayBuffer, aesKey);
      const wrappedAesKey = await wrapKey(aesKey, identity.encPublicKey);

      const payload = {
        tenant_id: tenantId,
        credential_id: `urn:uuid:${uuidv4()}`,
        issuer_did: identity.did,
        subject_did: identity.did, // Posíláme sami sobě pro test
        content_hash: sha256Hash,
        proof_signature: `HR_ISSUER_SIG_${Date.now()}`,
        encrypted_payload: bufferToBase64(encryptedBuffer),
        iv: bufferToBase64(iv),
        wrapped_key: bufferToBase64(wrappedAesKey)
      };

      logEvent(`Transmitting to Notary under workspace: ${tenantId}`);
      const response = await fetch(`${BACKEND_URL}/anchor-credential`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        logEvent('✅ SUCCESS: SaaS Credential Anchored.');
        setStatus('complete');
      }
    } catch (error) {
      logEvent(`❌ ERROR: ${error.message}`);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen p-6 bg-slate-900 flex justify-center items-center">
      <div className="w-full max-w-2xl bg-glass backdrop-blur-xl border border-glassBorder rounded-3xl p-8 shadow-2xl">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-3 text-white"><FileText className="text-blue-400" /> HR SaaS Dashboard</h2>
        </div>
        
        <div className="mb-6 flex items-center gap-4 bg-slate-800 p-4 rounded-xl border border-slate-700">
           <Building size={20} className="text-indigo-400" />
           <select 
             value={tenantId} 
             onChange={(e) => setTenantId(e.target.value)}
             className="bg-transparent text-white font-semibold outline-none flex-1"
           >
              <option value="acme_corp">Acme Corporation (Workspace A)</option>
              <option value="globex_inc">Globex Inc. (Workspace B)</option>
           </select>
        </div>

        <button onClick={processDocument} disabled={status === 'processing'} className="w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center justify-center gap-2">
          <Cpu size={20} /> Vydat smlouvu (AES-GCM)
        </button>

        {serverLog.length > 0 && (
          <div className="mt-8 bg-black/40 p-5 rounded-xl border border-slate-700 font-mono text-xs text-slate-400 space-y-2 max-h-64 overflow-y-auto">
            {serverLog.map((log, i) => <div key={i}>{log}</div>)}
          </div>
        )}
      </div>
    </div>
  );
};
