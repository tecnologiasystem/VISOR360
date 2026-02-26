import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Config para Nueva Data (puerto 5176 -> backend 8003)
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@/api': '/src/api.nueva.js',
      '@/services/apiService': '/src/services/apiService.nueva.js'
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5176,
  }
})
