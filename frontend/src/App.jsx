import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { EmployeePortal } from './components/EmployeePortal';
import { HRDashboard } from './components/HRDashboard';
import { B2BRegister } from './components/B2BRegister';
import { JoinCompany } from './components/JoinCompany';
import { ToastManager } from './components/ToastManager';
import { LandingPage } from './components/LandingPage';
import { MojeIdCallback } from './components/MojeIdCallback';
import HRContracts from './components/HRContracts';
import { VerifierPortal } from './components/VerifierPortal';

const GlobalNavigation = () => {
  const location = useLocation();
  if (location.pathname === '/' || location.pathname.startsWith('/auth/')) return null;

  return (
    <nav className="bg-white border-b border-slate-200 p-4">
      <div className="max-w-6xl mx-auto flex justify-between items-center">
        <Link to="/" className="text-slate-900 font-bold text-xl tracking-tight">INLOOP<span className="text-blue-600">ID</span></Link>
        <div className="flex gap-8">
           <Link to="/hr" className="text-sm font-semibold text-slate-600 hover:text-blue-600 transition-colors">Administrační portál</Link>
           <Link to="/hr/contracts" className="text-sm font-semibold text-slate-600 hover:text-blue-600 transition-colors">HR Smlouvy & VC</Link>
           <Link to="/employee" className="text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors">Zaměstnanecký portál</Link>
           <Link to="/verifier" className="text-sm font-semibold text-emerald-600 hover:text-emerald-800 transition-colors">Verifier Gateway</Link>
        </div>
      </div>
    </nav>
  );
};

const SessionGuard = ({ children }) => {
  useEffect(() => {
    let timeout;
    const resetTimeout = () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        const path = window.location.pathname;
        const isWhitelisted = ['/', '/b2b/register', '/hr', '/hr/contracts', '/employee', '/verifier'].includes(path) ||
                              path.startsWith('/auth/') ||
                              path.startsWith('/join/');
        if (!isWhitelisted) {
           alert("Z bezpečnostních důvodů byla relace ukončena.");
           window.location.href = "/";
        }
      }, 15 * 60 * 1000);
    };
    const events = ['mousemove', 'keydown', 'scroll', 'touchstart'];
    events.forEach(e => window.addEventListener(e, resetTimeout));
    resetTimeout();
    return () => {
      events.forEach(e => window.removeEventListener(e, resetTimeout));
      clearTimeout(timeout);
    };
  }, []);
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <ToastManager />
      <SessionGuard>
        <div className="min-h-screen flex flex-col bg-slate-50">
          <GlobalNavigation />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/employee" element={<EmployeePortal />} />
          <Route path="/verifier" element={<VerifierPortal />} />
            <Route path="/hr" element={<HRDashboard />} />
            <Route path="/hr/contracts" element={<HRContracts />} />
            <Route path="/b2b/register" element={<B2BRegister />} />
            <Route path="/join/:tenant_id" element={<JoinCompany />} />
            <Route path="/auth/mojeid/callback" element={<MojeIdCallback />} />
            <Route path="/auth/recovery/callback" element={<MojeIdCallback />} />
            <Route path="/auth/callback" element={<MojeIdCallback />} />
          </Routes>
        </div>
      </SessionGuard>
    </Router>
  );
}

export default App;
