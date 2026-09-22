/**
 * Centrální konfigurace pro InLoopID frontend.
 * Využívá Vite proměnné prostředí (musí začínat prefixem VITE_).
 */
export const API_BASE_URL = 
  import.meta.env.VITE_API_URL || `http://${window.location.hostname}:5000/api/v1`;

export const APP_VERSION = '1.0.0';
