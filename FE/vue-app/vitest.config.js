import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.js'],
    include: ['tests/**/*.spec.js'],
    // Each test starts fresh — no leaking mocks between files.
    clearMocks: true,
    restoreMocks: true,
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
})
