import React, { useState, useEffect } from 'react';
import { Lock, Cpu, ShieldCheck } from 'lucide-react';

export const GlobalCryptoOverlay = () => {
    const [isActive, setIsActive] = useState(false);
    const [rawText, setRawText] = useState('');
    const [displayText, setDisplayText] = useState('');
    const [phase, setPhase] = useState(0); // 0: Idle, 1: Raw, 2: Scrambling, 3: Locked

    useEffect(() => {
        let scrambleInterval;
        let p1Timeout, p2Timeout, p3Timeout;

        const handleStart = (e) => {
            const payload = e.detail.payload || '{"status": "initializing..."}';
            setRawText(payload);
            setDisplayText(payload);
            setIsActive(true);
            setPhase(1); // Ukážeme čistý text

            // Fáze 2: Začátek šifrování (Scrambling) po 600ms
            p1Timeout = setTimeout(() => {
                setPhase(2);
                const chars = '0123456789ABCDEF!@#$%^&*()';
                let iteration = 0;
                
                scrambleInterval = setInterval(() => {
                    setDisplayText(prev => 
                        prev.split('').map((char, index) => {
                            if (index < iteration) return char; // Necháme plynule mizet
                            return chars[Math.floor(Math.random() * chars.length)];
                        }).join('')
                    );
                    iteration += payload.length / 30; // Rychlost průchodu
                }, 40);
            }, 600);

            // Fáze 3: Uzamčeno (AES-GCM hotovo) po 2.2 vteřinách
            p2Timeout = setTimeout(() => {
                clearInterval(scrambleInterval);
                setPhase(3);
                // Ukážeme finální hex blob
                setDisplayText("U2FsdGVkX1+zT8x...[AES-256-GCM-SECURED]...9fA==");
            }, 2200);

            // Fáze 0: Skrytí komponenty po 3.2 vteřinách
            p3Timeout = setTimeout(() => {
                setIsActive(false);
                setPhase(0);
            }, 3200);
        };

        window.addEventListener('inloop:crypto-start', handleStart);
        return () => {
            window.removeEventListener('inloop:crypto-start', handleStart);
            clearInterval(scrambleInterval);
            clearTimeout(p1Timeout);
            clearTimeout(p2Timeout);
            clearTimeout(p3Timeout);
        };
    }, []);

    if (!isActive) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-[#050B14]/90 backdrop-blur-md flex flex-col justify-center items-center p-8">
            <div className="w-full max-w-3xl">
                
                <div className="flex items-center gap-4 mb-6">
                    {phase === 1 && <Cpu size={32} className="text-blue-500 animate-pulse" />}
                    {phase === 2 && <Cpu size={32} className="text-emerald-500 animate-spin" />}
                    {phase === 3 && <ShieldCheck size={32} className="text-emerald-400" />}
                    
                    <div>
                        <h2 className="text-xl font-bold text-white uppercase tracking-widest">
                            {phase === 1 && "Příprava Zero-Knowledge Payloadu"}
                            {phase === 2 && "Generování AES-256-GCM Obálky"}
                            {phase === 3 && "Kryptograficky Uzamčeno"}
                        </h2>
                        <p className="text-blue-400/60 text-sm font-mono mt-1">WebCrypto API | RAM Execution Only</p>
                    </div>
                </div>

                <div className={`p-6 rounded-2xl border font-mono text-sm break-all transition-colors duration-300 h-64 overflow-hidden relative shadow-2xl
                    ${phase === 1 ? 'bg-[#0A192F] border-blue-800/50 text-blue-200' : ''}
                    ${phase === 2 ? 'bg-[#0A192F] border-emerald-500 text-emerald-400 shadow-[0_0_30px_rgba(16,185,129,0.2)]' : ''}
                    ${phase === 3 ? 'bg-[#05101A] border-emerald-800 text-emerald-600' : ''}
                `}>
                    {phase === 3 && (
                        <div className="absolute inset-0 flex flex-col justify-center items-center bg-[#050B14]/60 backdrop-blur-sm animate-in fade-in zoom-in duration-300">
                            <Lock size={64} className="text-emerald-400 mb-4 drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]" />
                            <span className="text-emerald-300 font-bold tracking-widest text-lg">AES-256-GCM SECURED</span>
                        </div>
                    )}
                    {displayText}
                </div>
            </div>
        </div>
    );
};
