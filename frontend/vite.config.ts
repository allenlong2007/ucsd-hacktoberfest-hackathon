import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Relative base so the built app works from any path (GitHub Pages, a subfolder, etc.).
export default defineConfig({
  plugins: [react()],
  base: './',
})
