import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on the current mode (development, production, etc.) 
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      allowedHosts: ['miraveja.127.0.0.1.nip.io'],
      port: parseInt(env.VITE_PORT) || 3000,
      strictPort: true,
      hmr: {
        protocol: 'ws',
        host: 'miraveja.127.0.0.1.nip.io',
        port: 3000,
        clientPort: 3000,
      },
      proxy: {
        [env.VITE_API_BASE_PATH]: {
          target: env.VITE_API_URL,
          changeOrigin: true,
          secure: env.VITE_DEVELOPMENT !== 'true',
          ws: true,
        },
      },
      watch: {
        usePolling: true,
        interval: 100,
      },
    },
    // Set the base URL for the application
    // This should match the VITE_FRONTEND_BASE_PATH environment variable
    base: env.VITE_FRONTEND_BASE_PATH ? `${env.VITE_FRONTEND_BASE_PATH}/` : '/',
  }
});
