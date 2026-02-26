import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import legacy from '@vitejs/plugin-legacy'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    legacy({
      targets: ['defaults', 'safari >= 12', 'iOS >= 12'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime'],
      renderLegacyChunks: true,
      polyfills: [
        'es.array.iterator',
        'es.promise',
        'es.object.assign',
        'es.promise.finally'
      ]
    })
  ],
  build: {
    target: ['es2015', 'safari12'],
    cssTarget: ['safari12']
  },
  server: {
    host: '0.0.0.0', // Exponer en toda la red
    port: 5175,
    // Proxy para desarrollo - en producción IIS maneja esto
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
        // No reescribir la ruta, el BE ya espera /api
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
      }
    }
  }
})
