import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        // En Docker: utilise 'api' (nom du service), sinon localhost
        target: process.env.VITE_API_TARGET || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Split vendor chunks for better caching
          if (id.includes('node_modules')) {
            if (id.includes('react-dom')) {
              return 'vendor-react-dom'
            }
            if (id.includes('react-router')) {
              return 'vendor-router'
            }
            if (id.includes('react')) {
              return 'vendor-react'
            }
            if (id.includes('date-fns')) {
              return 'vendor-date-fns'
            }
            if (id.includes('axios')) {
              return 'vendor-axios'
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons'
            }
          }
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 500,
  },
})
