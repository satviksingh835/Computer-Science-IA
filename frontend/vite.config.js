import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy API calls to Flask running on port 5000
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      // Proxy static assets and export endpoints to Flask
      '/static': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/login': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/create_class': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/add_student': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/mark_attendance': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/remove_student': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      '/export': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      }
    }
  }
})
