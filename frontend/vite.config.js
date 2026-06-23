
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    watch: {
      usePolling: true,
      interval: 200,
    },
    proxy: {
      '/analytics': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/options': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/predict': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/feedback': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/feedback/summary': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
