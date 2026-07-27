import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  appType: 'spa',
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/mcp': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  preview: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/mcp': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})