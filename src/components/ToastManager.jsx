import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

export const ToastManager = () => {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToast = (e) => {
      const id = Date.now() + Math.random();
      setToasts(prev => [...prev, { id, ...e.detail }]);
      
      // Automatické smazání po 5 sekundách
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, 5000);
    };
    
    window.addEventListener('show-toast', handleToast);
    return () => window.removeEventListener('show-toast', handleToast);
  }, []);

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <div className="fixed bottom-4 md:bottom-auto md:top-4 left-1/2 -translate-x-1/2 z-[110] flex flex-col gap-3 pointer-events-none w-full max-w-sm px-4">
      {toasts.map(t => (
        <div key={t.id} className={`relative flex items-start gap-3 px-5 py-4 rounded-2xl shadow-2xl pointer-events-auto transition-all duration-300 border overflow-hidden animate-in slide-in-from-bottom-5 md:slide-in-from-top-5 fade-in zoom-in-95 backdrop-blur-xl
            ${t.type === 'error' ? 'bg-[#11050A]/90 border-rose-900/50 text-rose-200 shadow-[0_10px_40px_-10px_rgba(225,29,72,0.3)]' :
            t.type === 'success' ? 'bg-[#05110A]/90 border-emerald-900/50 text-emerald-200 shadow-[0_10px_40px_-10px_rgba(16,185,129,0.3)]' :
            'bg-[#0A101D]/90 border-blue-900/50 text-blue-200 shadow-[0_10px_40px_-10px_rgba(59,130,246,0.3)]'}`}>
          
          {t.type === 'error' ? <AlertTriangle size={20} className="text-rose-500 shrink-0 mt-0.5" /> :
           t.type === 'success' ? <CheckCircle size={20} className="text-emerald-500 shrink-0 mt-0.5" /> :
           <Info size={20} className="text-blue-500 shrink-0 mt-0.5" />}
          
          <div className="flex-1 text-sm font-medium leading-relaxed pr-6">{t.msg}</div>
          
          <button 
            onClick={() => removeToast(t.id)} 
            className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors outline-none"
            aria-label="Zavřít upozornění"
          >
            <X size={16} />
          </button>

          {/* Progress bar indikátor */}
          <div className="absolute bottom-0 left-0 h-1 bg-white/5 w-full">
             <div className={`h-full ${t.type === 'error' ? 'bg-rose-500' : t.type === 'success' ? 'bg-emerald-500' : 'bg-blue-500'}`} style={{ animation: 'toast-progress 5s linear forwards' }}></div>
          </div>
        </div>
      ))}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes toast-progress {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}} />
    </div>
  );
};

export const notify = {
  error: (msg) => window.dispatchEvent(new CustomEvent('show-toast', {detail: {msg, type: 'error'}})),
  success: (msg) => window.dispatchEvent(new CustomEvent('show-toast', {detail: {msg, type: 'success'}})),
  info: (msg) => window.dispatchEvent(new CustomEvent('show-toast', {detail: {msg, type: 'info'}})),
};
