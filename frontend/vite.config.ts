import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Obyčejná Vite React konfigurace bez @tailwindcss/vite pluginu,
// protože v3 používá PostCSS (který Vite detekuje automaticky přes postcss.config.js)
export default defineConfig({
  plugins: [react()],
})
