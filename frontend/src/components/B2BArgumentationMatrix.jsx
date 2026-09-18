import React, { useState } from 'react';
import { X, ShieldAlert, Scale, UserX, ServerCrash, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react';

export const B2BArgumentationMatrix = ({ onClose }) => {
    const [openTab, setOpenTab] = useState(0);

    const argumentsData = [
        {
            icon: <ShieldAlert size={24} className="text-blue-400" />,
            title: "Eliminace GDPR rizik a likvidačních pokut",
            target: "Pro DPO a Právní oddělení",
            objection: "Ukládat HR data do cloudu je obrovské riziko pro osobní údaje.",
            fact: "Podle bodu 26 odůvodnění GDPR se principy ochrany OÚ nevztahují na anonymizované informace.",
            math: "Architektura využívá klientské AES-256-GCM šifrování. Backend přijímá pouze šifrovaný šum (ciphertext). Master klíče nikdy neopustí zařízení.",
            conclusion: "Při kompromitaci databáze hacker nezíská osobní údaje. Nevzniká ohlašovací povinnost vůči ÚOOÚ a je matematicky vyloučeno uložení pokuty (až 4 % obratu)."
        },
        {
            icon: <Scale size={24} className="text-emerald-400" />,
            title: "Absolutní nezpochybnitelnost u soudu",
            target: "Pro Auditory a oddělení Compliance",
            objection: "Jak prokážeme, že zaměstnanec smlouvu skutečně podepsal v daném znění?",
            fact: "Databázový záznam (např. v SAP) může DBA s právy UPDATE kdykoliv zpětně a nezjistitelně upravit.",
            math: "InLoopID každý úkon asymetricky podepíše a ukotví pomocí kvalifikovaného časového razítka (eIDAS nařízení EU č. 910/2014).",
            conclusion: "Důkazní břemeno se obrací. Poskytujeme kryptografický důkaz platný u soudů napříč celou EU, nezávislý na důvěře v IT infrastrukturu."
        },
        {
            icon: <UserX size={24} className="text-rose-400" />,
            title: "Eliminace vnitřní hrozby (Insider Threat)",
            target: "Pro CISO a Bezpečnostní ředitele",
            objection: "Největší riziko úniku dat představují naši vlastní IT administrátoři.",
            fact: "Administrátoři tradičních systémů mají absolutní přístup k datům (tzv. 'God Mode').",
            math: "WebCrypto API provádí kryptografické operace striktně v izolované paměti prohlížeče (Zero-Knowledge na straně serveru).",
            conclusion: "I s nejvyšším oprávněním (root) nemůže administrátor číst smlouvy. Architektura matematicky znemožňuje existenci super-uživatele."
        },
        {
            icon: <ServerCrash size={24} className="text-purple-400" />,
            title: "Garantovaná kontinuita provozu",
            target: "Pro Risk Management",
            objection: "Co když ztratíme heslo? Přijdeme o celou HR agendu?",
            fact: "Tradiční symetrické šifrování znamená: ztráta hesla = ztráta databáze.",
            math: "Implementováno prahové sdílení tajemství (Shamir's Secret Sharing). Matematický polynom rozděluje hlavní klíč do N nezávislých fragmentů (např. představenstvo).",
            conclusion: "Klíč nelze ztratit chybou jednoho člověka a nelze jej kompromitovat únosem. Matematika garantuje bezpečnost i vysokou dostupnost."
        }
    ];

    return (
        <div className="fixed inset-0 z-[80] bg-[#050B14]/95 overflow-y-auto pt-16 pb-12 px-4 backdrop-blur-xl flex justify-center items-start">
            <div className="bg-[#0A192F] p-6 md:p-10 rounded-3xl border border-blue-500/30 w-full max-w-4xl shadow-2xl relative animate-in slide-in-from-bottom-10 duration-300 max-h-[90vh] overflow-y-auto custom-scrollbar">
                
                <button onClick={onClose} className="absolute top-6 right-6 text-slate-500 hover:text-white bg-[#112240] p-2 rounded-full transition-colors z-10 border border-slate-700">
                    <X size={20} />
                </button>

                <div className="mb-10 pr-10">
                    <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">Argumentační Matice pro C-Level</h2>
                    <p className="text-blue-300/80">
                        Nevyvratitelná fakta a matematické základy Zero-Knowledge architektury InLoopID, připravené pro B2B akvizici.
                    </p>
                </div>

                <div className="space-y-4">
                    {argumentsData.map((arg, idx) => (
                        <div key={idx} className="bg-[#112240] border border-blue-900/50 rounded-2xl overflow-hidden transition-all duration-300">
                            <button 
                                onClick={() => setOpenTab(openTab === idx ? -1 : idx)}
                                className="w-full text-left p-5 flex items-center justify-between hover:bg-blue-900/20 transition-colors"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="bg-[#0A192F] p-3 rounded-xl border border-blue-800/50">
                                        {arg.icon}
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-blue-50">{arg.title}</h3>
                                        <span className="text-xs font-mono text-blue-400 uppercase tracking-wider">{arg.target}</span>
                                    </div>
                                </div>
                                {openTab === idx ? <ChevronUp className="text-blue-400" /> : <ChevronDown className="text-slate-500" />}
                            </button>
                            
                            {openTab === idx && (
                                <div className="p-6 border-t border-blue-900/50 bg-[#0B1120] animate-in fade-in duration-300">
                                    <div className="space-y-6">
                                        <div>
                                            <h4 className="text-slate-500 text-xs font-bold uppercase tracking-wider mb-2">Běžná námitka klienta</h4>
                                            <p className="text-slate-300 italic border-l-2 border-slate-600 pl-3">"{arg.objection}"</p>
                                        </div>
                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="bg-blue-950/30 p-4 rounded-xl border border-blue-900/50">
                                                <h4 className="text-blue-400 text-xs font-bold uppercase tracking-wider mb-2">Výchozí Fakt</h4>
                                                <p className="text-sm text-blue-100/80 leading-relaxed">{arg.fact}</p>
                                            </div>
                                            <div className="bg-emerald-950/30 p-4 rounded-xl border border-emerald-900/50">
                                                <h4 className="text-emerald-400 text-xs font-bold uppercase tracking-wider mb-2">Aplikovaná Matematika</h4>
                                                <p className="text-sm text-emerald-100/80 leading-relaxed">{arg.math}</p>
                                            </div>
                                        </div>
                                        
                                        <div className="bg-blue-600/10 p-5 rounded-xl border border-blue-500/30 flex gap-4 items-start">
                                            <CheckCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={20} />
                                            <div>
                                                <h4 className="text-blue-300 text-sm font-bold mb-1">Nevyvratitelný závěr (Prodejní argument)</h4>
                                                <p className="text-sm text-blue-50 leading-relaxed">{arg.conclusion}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
                
            </div>
        </div>
    );
};
