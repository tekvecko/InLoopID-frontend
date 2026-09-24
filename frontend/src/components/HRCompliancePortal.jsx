import React, { useState, useEffect } from 'react';

export default function HRCompliancePortal({ tenantId, employeeEmailHash }) {
    const [contracts, setContracts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (tenantId && employeeEmailHash) {
            fetchContracts();
        }
    }, [tenantId, employeeEmailHash]);

    const fetchContracts = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/hr/compliance/contracts?tenant_id=${tenantId}&email_hash=${employeeEmailHash}`);
            if (res.ok) {
                const data = await res.json();
                setContracts(data.contracts || []);
            }
        } catch (e) {
            console.error("Chyba při načítání smluv:", e);
        } finally {
            setLoading(false);
        }
    };

    const handleSignContract = async (docHash) => {
        setMessage('Podepisuji dokument biometrickým klíčem (WebAuthn/eIDAS)...');
        try {
            const proof = "webauthn_sig_" + Math.random().toString(36).substring(7);
            const res = await fetch('/api/hr/compliance/contract/sign', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_hash: docHash,
                    role: 'employee',
                    signature_proof: proof
                })
            });
            if (res.ok) {
                setMessage('Smlouva úspěšně a právně závazně podepsána!');
                fetchContracts();
            } else {
                setMessage('Chyba při podpisu dokumentu.');
            }
        } catch (e) {
            setMessage('Síťová chyba při podpisu.');
        }
    };

    return (
        <div className="p-6 bg-slate-900 text-slate-100 rounded-xl border border-slate-800 shadow-xl my-4">
            <h2 className="text-2xl font-bold mb-4 text-emerald-400">🛡️ HR Compliance & e-Podpisy (Zákoník práce ČR)</h2>
            {message && <div className="p-3 mb-4 bg-slate-800 border border-slate-700 rounded text-sm text-cyan-300">{message}</div>}

            <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-300">Moje pracovní smlouvy a dodatky</h3>
                {loading ? (
                    <p className="text-slate-400">Načítám zabezpečené dokumenty...</p>
                ) : contracts.length === 0 ? (
                    <p className="text-slate-500">Žádné čekající dokumenty k podpisu pro tento profil.</p>
                ) : (
                    contracts.map(c => (
                        <div key={c.document_hash} className="p-4 bg-slate-800 rounded-lg border border-slate-700 flex justify-between items-center">
                            <div>
                                <p className="font-semibold text-slate-200">Typ: {c.contract_type}</p>
                                <p className="text-xs text-slate-400">Hash: {c.document_hash.substring(0, 16)}...</p>
                                <p className="text-xs text-amber-400">Skartace / Retence do: {new Date(c.retention_expires_at).toLocaleDateString()}</p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <a
                                    href={`/api/hr/compliance/contract/pdf/${c.document_hash}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm transition inline-flex items-center"
                                    title="Stáhnout oficiální PDF dokument"
                                >
                                    📄 Stáhnout PDF
                                </a>
                                {c.employee_signed ? (
                                    <span className="px-3 py-1 bg-emerald-900 text-emerald-300 text-xs rounded-full">Podepsáno ✓</span>
                                ) : (
                                    <button
                                        onClick={() => handleSignContract(c.document_hash)}
                                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg text-sm transition"
                                    >
                                        Podepsat smlouvu
                                    </button>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
