import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Configure Vite to compile the React TypeScript frontend.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
