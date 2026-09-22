import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle2, AlertCircle, KeyRound } from 'lucide-react';
import { API_BASE_URL as BACKEND_URL } from '../utils/config';
import { generateRSAKeyPair, generateSigningKeyPair, exportPublicKeyJWK } from '../utils/cryptoEngine';
import { saveIdentity } from '../utils/idbStorage';

export const MojeIdCallback = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [status, setStatus] = useState('verifying'); // 'verifying' | 'rekeying' | 'success' | 'error'
    const [message, setMessage] = useState('Ověřování výsledku z MojeID...');

    useEffect(() => {
        const processCallback = async () => {
            const queryParams = new URLSearchParams(location.search);
            const authCode = queryParams.get('code');
            const state = queryParams.get('state');
            const isRecovery = queryParams.get('mode') === 'recovery';

            if (!authCode && !state) {
                setStatus('error');
                setMessage('Chybí autorizační parametry v URL.');
                return;
            }

            try {
                if (isRecovery) {
                    setStatus('rekeying');
                    setMessage('Ověření úspěšné. Generuji nové kryptografické klíče a WebAuthn Passkey...');

                    // 1. Vygenerování nového páru klíčů na novém zařízení
                    const encKeys = await generateRSAKeyPair();
                    const signKeys = await generateSigningKeyPair();
                    const jwk = await exportPublicKeyJWK(encKeys.publicKey);
                    const newDid = `did:key:z${btoa(jwk.n).substring(0, 16)}`;

                    // 2. Dokončení recovery na backendu
                    const res = await fetch(`${BACKEND_URL}/auth/recovery/complete`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            code: authCode,
                            state: state,
                            new_did_uri: newDid,
                            public_key_jwk: jwk
                        })
                    });

                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Dokončení obnovy identity selhalo.');

                    // 3. Uložení nových klíčů do lokální IndexedDB
                    await saveIdentity(newDid, encKeys, signKeys, jwk);
                    if (data.employee_token) {
                        localStorage.setItem('employee_token', data.employee_token);
                    }

                    setStatus('success');
                    setMessage('Přístup byl úspěšně obnoven! Přesměrovávám do portálu...');
                    setTimeout(() => navigate('/employee'), 2000);
                } else {
                    // Bežný Step-up callback (podpis / schválení)
                    const res = await fetch(`${BACKEND_URL}/auth/mojeid/callback`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ code: authCode, state: state })
                    });

                    const data = await res.json();
                    if (!res.ok) throw new Error(data.error || 'Ověření výzvy selhalo.');

                    setStatus('success');
                    setMessage('Transakce byla úspěšně ověřena přes MojeID.');
                    setTimeout(() => navigate('/employee'), 2000);
                }
            } catch (err) {
                setStatus('error');
                setMessage(err.message || 'Nastala chyba při zpracování odpovědi z MojeID.');
            }
        };

        processCallback();
    }, [location, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-900 p-6 text-white">
            <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-3xl p-8 text-center space-y-6 shadow-2xl">
                {status === 'verifying' && (
                    <>
                        <Loader2 size={48} className="animate-spin text-blue-400 mx-auto" />
                        <h2 className="text-xl font-bold">Ověřuji identitu</h2>
                    </>
                )}

                {status === 'rekeying' && (
                    <>
                        <KeyRound size={48} className="animate-pulse text-amber-400 mx-auto" />
                        <h2 className="text-xl font-bold">Obnova Passkey klíčů</h2>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <CheckCircle2 size={48} className="text-emerald-400 mx-auto" />
                        <h2 className="text-xl font-bold text-emerald-400">Hotovo</h2>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <AlertCircle size={48} className="text-rose-400 mx-auto" />
                        <h2 className="text-xl font-bold text-rose-400">Chyba ověření</h2>
                    </>
                )}

                <p className="text-slate-300 text-sm leading-relaxed">{message}</p>
            </div>
        </div>
    );
};
