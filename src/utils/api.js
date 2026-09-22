// Centrální komunikační vrstva InLoopID (Zajišťuje spojení s Flask backendem)
const API_BASE = '/api';

export const api = {
    // Pro získávání dat (např. seznam tenantů, eIDAS certifikáty)
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`[API GET Selhání na ${endpoint}]:`, error);
            throw error;
        }
    },
    
    // Pro odesílání Zero-Knowledge payloadů (šifrované smlouvy)
    async post(endpoint, payload) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`[API POST Selhání na ${endpoint}]:`, error);
            throw error;
        }
    }
};
