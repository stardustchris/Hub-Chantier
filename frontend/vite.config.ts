import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'Hub Chantier',
        short_name: 'HubChantier',
        description: 'Application de gestion de chantiers BTP',
        theme_color: '#3B82F6',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait-primary',
        start_url: '/',
        scope: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          // Endpoints sensibles : jamais en cache (sécurité)
          {
            urlPattern: /\/api\/(auth|pointages|users|feuilles-heures)\/.*/i,
            handler: 'NetworkOnly',
          },
          // Autres endpoints API : cache court (1h) avec NetworkFirst
          {
            urlPattern: /^https:\/\/api\..*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60, // 1 hour (réduit de 24h)
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60, // 1 hour (réduit de 24h)
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
        ],
      },
      devOptions: {
        enabled: false, // Disable in dev mode to avoid issues
      },
    }),
  ],
  server: {
    port: 5173,
    host: '0.0.0.0',
    allowedHosts: true,
    hmr: false,
    watch: {
      ignored: ['**/*'],
    },
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
            if (id.includes('firebase')) {
              return 'vendor-firebase'
            }
            if (id.includes('recharts')) {
              return 'vendor-charts'
            }
            if (id.includes('@tanstack/react-query')) {
              return 'vendor-query'
            }
          }
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 500,
  },
})
