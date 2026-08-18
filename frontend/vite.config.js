// Vite configuration for MTEJA AI React frontend
// Handles development server, build, and path aliases
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 5173, host: true },
})
