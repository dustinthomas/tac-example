import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['src/__tests__/**/*.spec.ts'],
    setupFiles: ['src/__tests__/setup.ts'],
    globals: true,
  },
})
