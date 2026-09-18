import React, { useState, useEffect } from 'react';
import { ShieldCheck, FileText } from 'lucide-react';

export const ComplianceDashboard = () => {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Získání kryptografických dat pro auditora z našeho nového API
        fetch('/api/v1/compliance/health-report')
            .then(res => {
                if (!res.ok) throw new Error('API Endpoint neodpovídá. Je backend spuštěn?');
                return res.json();
            })
            .then(data => {
                setReport(data.report);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="p-8 text-emerald-500 font-mono text-sm animate-pulse">Generuji kryptografický audit...</div>;
    if (error) return <div className="p-8 text-red-500 bg-red-900/20 rounded-xl">Chyba spojení s auditním API: {error}</div>;

    return (
        <div className="bg-[#0B1120] p-8 rounded-3xl border border-emerald-900/50 text-white shadow-2xl relative">
            <div className="flex items-center gap-4 mb-8 border-b border-slate-800 pb-6">
                <ShieldCheck className="text-emerald-500" size={40} />
                <div>
                    <h2 className="text-2xl font-bold tracking-wide">Enterprise Compliance Portál</h2>
                    <p className="text-slate-400 text-sm mt-1">Read-only rozhraní pro Risk Management a auditory</p>
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                    <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Expozice dat</div>
                    <div className="text-2xl font-bold text-emerald-400">{report.metrics.data_exposure_risk}</div>
                </div>
                <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                    <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Ukotvené dokumenty (eIDAS)</div>
                    <div className="text-2xl font-bold text-blue-400">{report.metrics.total_anchored_documents}</div>
                </div>
                <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                    <div className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Pokusy o narušení integrity</div>
                    <div className="text-2xl font-bold text-slate-300">{report.metrics.cryptographic_breaches_detected}</div>
                </div>
            </div>

            <div className="bg-emerald-900/20 p-6 rounded-2xl text-emerald-300/80 text-sm border border-emerald-900/30">
                <div className="flex items-start gap-3">
                    <FileText size={20} className="text-emerald-500 flex-shrink-0 mt-1" />
                    <div>
                        <strong className="text-emerald-400">Právní doložka (Non-repudiation):</strong><br/>
                        {report.legal_disclaimer}<br/><br/>
                        <strong className="text-emerald-400">Certifikační standard:</strong> {report.certification_standard}<br/>
                        <strong className="text-emerald-400">Čas auditu (UTC):</strong> <span className="font-mono">{report.audit_timestamp}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
