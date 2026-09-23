import React, { useState, useEffect } from 'react';

export default function HRContracts() {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);
  const [formData, setFormData] = useState({
    email: 'jan.novak@firma.cz',
    name: 'Jan Novák',
    position: 'Senior Developer',
    clearance_level: 'STANDARD'
  });

  const fetchContracts = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/hr/contracts');
      const json = await res.json();
      if (json.status === 'success') {
        setContracts(json.data);
      }
    } catch (err) {
      console.error('Chyba při načítání smluv:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, []);

  const handleCreateContract = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const mockPayload = JSON.stringify({
        name: formData.name,
        position: formData.position,
        created: new Date().toISOString()
      });
      const encoder = new TextEncoder();
      const data = encoder.encode(mockPayload);
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const contentHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

      const res = await fetch('/api/v1/hr/contracts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          name: formData.name,
          position: formData.position,
          clearance_level: formData.clearance_level,
          content_hash: contentHash,
          encrypted_payload: btoa(mockPayload),
          iv: 'iv_mock_123',
          wrapped_key: 'key_mock_abc'
        })
      });

      const json = await res.json();
      if (res.ok) {
        fetchContracts();
      } else {
        alert('Chyba: ' + (json.error || json.message));
      }
    } catch (err) {
      alert('Chyba při vytváření smlouvy: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (credentialId) => {
    try {
      setLoading(true);
      const res = await fetch(`/api/v1/hr/contracts/${credentialId}/approve`, {
        method: 'POST'
      });
      const json = await res.json();
      if (res.ok) {
        setTimeout(fetchContracts, 1500);
      } else {
        alert('Chyba při schvalování: ' + json.message);
      }
    } catch (err) {
      alert('Chyba: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getBadgeClass = (status) => {
    switch (status) {
      case 'ISSUED': return 'bg-green-100 text-green-800 border-green-300';
      case 'PROCESSING': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'FAILED': return 'bg-red-100 text-red-800 border-red-300';
      default: return 'bg-amber-100 text-amber-800 border-amber-300';
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">HR Správa Pracovních Smluv</h1>
          <p className="text-sm text-gray-500">Dezentrální emise Verifiable Credentials s eIDAS kotvením</p>
        </div>
        <button
          onClick={fetchContracts}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-md border transition"
        >
          {loading ? 'Načítám...' : 'Obnovit'}
        </button>
      </div>

      {/* Formulář pro novou smlouvu */}
      <div className="bg-white p-5 rounded-lg border shadow-sm">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Vytvořit novou smlouvu</h2>
        <form onSubmit={handleCreateContract} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="email"
            placeholder="Email zaměstnance"
            value={formData.email}
            onChange={e => setFormData({ ...formData, email: e.target.value })}
            className="p-2 border rounded-md text-sm"
            required
          />
          <input
            type="text"
            placeholder="Jméno a příjmení"
            value={formData.name}
            onChange={e => setFormData({ ...formData, name: e.target.value })}
            className="p-2 border rounded-md text-sm"
            required
          />
          <input
            type="text"
            placeholder="Pozice"
            value={formData.position}
            onChange={e => setFormData({ ...formData, position: e.target.value })}
            className="p-2 border rounded-md text-sm"
            required
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-md text-sm transition"
          >
            Zašifrovat a vytvořit
          </button>
        </form>
      </div>

      {/* Tabulka smluv */}
      <div className="bg-white rounded-lg border shadow-sm overflow-hidden">
        <table className="w-full text-left border-collapse text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="p-3 font-semibold text-gray-600">Kredenciál ID</th>
              <th className="p-3 font-semibold text-gray-600">Subjekt DID</th>
              <th className="p-3 font-semibold text-gray-600">Stav</th>
              <th className="p-3 font-semibold text-gray-600">TSA Stav</th>
              <th className="p-3 font-semibold text-gray-600">Akce</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {contracts.length === 0 ? (
              <tr>
                <td colSpan="5" className="p-4 text-center text-gray-400">Žádné smlouvy nenalezeny</td>
              </tr>
            ) : (
              contracts.map((c) => (
                <tr key={c.credential_id} className="hover:bg-gray-50">
                  <td className="p-3 font-mono text-xs text-indigo-600">{c.credential_id}</td>
                  <td className="p-3 font-mono text-xs">{c.subject_did}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold border ${getBadgeClass(c.status)}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="p-3 text-xs text-gray-500">{c.tsa_status || 'N/A'}</td>
                  <td className="p-3 space-x-2">
                    {c.status === 'PENDING_SIGNATURE' && (
                      <button
                        onClick={() => handleApprove(c.credential_id)}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-3 py-1 rounded transition"
                      >
                        Schválit a Vystavit VC
                      </button>
                    )}
                    <button
                      onClick={() => setSelectedContract(c)}
                      className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded border"
                    >
                      Detail
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal pro detail */}
      {selectedContract && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-xl w-full space-y-4">
            <h3 className="text-lg font-bold border-b pb-2">Detail VC Kotvy: {selectedContract.credential_id}</h3>
            <div className="space-y-2 text-xs font-mono bg-gray-50 p-3 rounded border overflow-x-auto">
              <p><strong>Subject DID:</strong> {selectedContract.subject_did}</p>
              <p><strong>Content Hash:</strong> {selectedContract.content_hash}</p>
              <p><strong>Proof Signature:</strong> {selectedContract.proof_signature || 'Čeká na emisi'}</p>
              <p><strong>Timestamped At:</strong> {selectedContract.timestamped_at || 'Čeká na emisi'}</p>
            </div>
            <div className="text-right">
              <button
                onClick={() => setSelectedContract(null)}
                className="bg-gray-800 text-white text-xs px-4 py-2 rounded hover:bg-gray-700"
              >
                Zavřít
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
