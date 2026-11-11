import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// The build in dist/ is served by dashboard/app.py on port 8000 (python3 start.py).
export default defineConfig({
  plugins: [vue()],
  build: { chunkSizeWarningLimit: 2000 }, // Element Plus in full; local app, size doesn't matter
})
