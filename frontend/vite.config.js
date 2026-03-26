import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production'
  
  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: !isProduction,
      minify: 'terser',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom', 'react-router-dom'],
            ui: ['framer-motion'],
            utils: ['axios']
          }
        }
      }
    },
    define: {
      'process.env.API_URL': JSON.stringify(
        isProduction 
          ? process.env.VITE_API_URL || 'https://api.englishspeakingtrainer.com'
          : 'http://localhost:8000'
      )
    }
  }
})