import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
// Performance 2.2.4 - Bundle analyzer
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Performance 2.2.4 - Bundle visualization
    // Run: ANALYZE=true npm run build → opens dist/stats.html
    ...(process.env.ANALYZE
      ? [
          visualizer({
            open: true,
            filename: 'dist/stats.html',
            gzipSize: true,
            brotliSize: true,
          }),
        ]
      : []),
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
          // P.1 - CacheFirst pour assets immuables (uploads)
          // Photos profil, posts, chantiers → cache 30 jours
          {
            urlPattern: /\/api\/uploads\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'uploads-cache',
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 30 * 24 * 60 * 60, // 30 jours
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // P.1 - CacheFirst pour documents immuables (GED)
          // Documents, dossiers → cache 30 jours
          {
            urlPattern: /\/api\/documents\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'documents-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 30 * 24 * 60 * 60, // 30 jours
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // P.2 - Cache court pour données temps réel
          // Planning, dashboard → StaleWhileRevalidate 5min
          {
            urlPattern: /\/api\/(planning|dashboard)\/.*/i,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'api-realtime-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 5 * 60, // 5 minutes
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          // P.3 - NetworkFirst avec timeout pour autres API
          // Fallback cache après 3s de timeout réseau
          {
            urlPattern: /^https:\/\/api\..*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 24 * 60 * 60, // 24h
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
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 24 * 60 * 60, // 24h
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
