import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = '';

export function MojeIdCallback() {
    const [statusText, setStatusText] = useState('Ověřování identity přes MojeID / BankID...');
    const [step, setStep] = useState('verifying'); // verifying, passkey_enrollment, success
    const [userEmail, setUserEmail] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const handleCallback = async () => {
            const urlParams = new URLSearchParams(window.location.search);
            const code = urlParams.get('code') || 'mock_mojeid_code_999';

            try {
                // 1. Dokončení MojeID / BankID autentizace
                const res = await fetch(`${BACKEND_URL}/api/v1/auth/mojeid/callback`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });
                
                const data = await res.json();
                
                // Pro účely robustního demo flow vezmeme email z odpovědi nebo fallback
                const email = data.email || data.user_email || 'zamestnanec@inloopid.cz';
                setUserEmail(email);

                // 2. Kontrola, zda uživatel již má zaregistrované Passkey
                const pkStatusRes = await fetch(`${BACKEND_URL}/api/v1/passkey/status/${encodeURIComponent(email)}`);
                const pkStatusData = await pkStatusRes.json();

                if (pkStatusData.has_passkey) {
                    setStatusText('Identita ověřena. Přesměrování do trezoru...');
                    setStep('success');
                    setTimeout(() => navigate('/employee-dashboard'), 1500);
                } else {
                    // 3. Vynucení registrace Passkey!
                    setStatusText('MojeID ověřeno. Pro pokračování je vyžadováno nastavení Passkey (biometrie).');
                    setStep('passkey_enrollment');
                }

            } catch (err) {
                console.error(err);
                setErrorMessage('Chyba při komunikaci se serverem: ' + err.message);
                setStep('error');
            }
        };

        handleCallback();
    }, [navigate]);

    const handleRegisterPasskey = async () => {
        setErrorMessage('');
        setStatusText('Připravuji biometrickou výzvu (WebAuthn)...');

        try {
            // A. Získání Challenge z backendu
            const chalRes = await fetch(`${BACKEND_URL}/api/v1/passkey/register-challenge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: userEmail })
            });
            const chalData = await chalRes.json();

            if (!chalRes.ok) {
                throw new Error(chalData.error || 'Nelze získat Passkey challenge.');
            }

            const options = chalData.options;

            // Konverze base64url stringů na Uint8Array pro WebAuthn API
            const binChallenge = Uint8Array.from(atob(options.challenge.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
            const binUserId = Uint8Array.from(atob(options.user.id.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));

            const publicKeyCredentialCreationOptions = {
                ...options,
                challenge: binChallenge,
                user: {
                    ...options.user,
                    id: binUserId
                }
            };

            setStatusText('Prosím, přiložte otisk prstu nebo potvrďte biometrii...');

            // B. Vyvolání nativního WebAuthn API prohlížeče (otisk prstu / FaceID / HW klíč)
            const credential = await navigator.credentials.create({
                publicKey: publicKeyCredentialCreationOptions
            });

            setStatusText('Ověřuji Passkey klíč na serveru...');

            // C. Serializace credential pro odeslání
            const credentialPayload = {
                id: credential.id,
                rawId: btoa(String.fromCharCode(...new Uint8Array(credential.rawId))),
                type: credential.type,
                response: {
                    clientDataJSON: btoa(String.fromCharCode(...new Uint8Array(credential.response.clientDataJSON))),
                    attestationObject: btoa(String.fromCharCode(...new Uint8Array(credential.response.attestationObject)))
                }
            };

            // D. Odeslání ověření na backend
            const verifyRes = await fetch(`${BACKEND_URL}/api/v1/passkey/register-verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: userEmail, credential: credentialPayload })
            });

            const verifyData = await verifyRes.json();

            if (verifyRes.ok && verifyData.verified) {
                setStatusText('Passkey úspěšně zaregistrován! Vstupuji do trezoru...');
                setStep('success');
                setTimeout(() => navigate('/employee-dashboard'), 1500);
            } else {
                throw new Error(verifyData.error || 'Ověření Passkey selhalo.');
            }

        } catch (err) {
            console.error(err);
            setErrorMessage('Biometrická registrace selhala nebo byla zrušena: ' + err.message);
            setStep('passkey_enrollment');
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-white">
            <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl text-center">
                
                {step === 'verifying' && (
                    <div>
                        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
                        <h2 className="text-xl font-bold mb-2">Autentizace probíhá</h2>
                        <p className="text-slate-400">{statusText}</p>
                    </div>
                )}

                {step === 'passkey_enrollment' && (
                    <div>
                        <div className="w-16 h-16 bg-blue-600/20 text-blue-400 rounded-2xl flex items-center justify-center mx-auto mb-6 text-3xl">
                            🔒
                        </div>
                        <h2 className="text-xl font-bold mb-2">Vyžadováno nastavení Passkey</h2>
                        <p className="text-slate-400 mb-6 text-sm">
                            Pro maximální zabezpečení vašeho účtu a přístupu k citlivým dokumentům je nutné si po ověření přes MojeID svázat účet s biometrickým klíčem (otisk prstu / zámek zařízení).
                        </p>
                        {errorMessage && (
                            <div className="mb-4 p-3 bg-red-950/50 border border-red-800 text-red-300 text-xs rounded-xl">
                                {errorMessage}
                            </div>
                        )}
                        <button
                            onClick={handleRegisterPasskey}
                            className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2"
                        >
                            <span>🔑</span> Zaregistrovat Passkey (Otisk prstu)
                        </button>
                    </div>
                )}

                {step === 'success' && (
                    <div>
                        <div className="w-16 h-16 bg-emerald-600/20 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto mb-6 text-3xl">
                            ✓
                        </div>
                        <h2 className="text-xl font-bold mb-2">Vše je připraveno</h2>
                        <p className="text-emerald-400 text-sm font-medium">{statusText}</p>
                    </div>
                )}

                {step === 'error' && (
                    <div>
                        <div className="w-16 h-16 bg-red-600/20 text-red-400 rounded-2xl flex items-center justify-center mx-auto mb-6 text-3xl">
                            ✕
                        </div>
                        <h2 className="text-xl font-bold mb-2">Chyba ověření</h2>
                        <p className="text-red-400 text-sm mb-6">{errorMessage}</p>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-6 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-sm font-medium"
                        >
                            Zkusit znovu
                        </button>
                    </div>
                )}

            </div>
        </div>
    );
}
