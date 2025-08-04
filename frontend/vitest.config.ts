import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
    coverage: {
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/test/**',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**',
        'src/vite-env.d.ts',
        'src/main.tsx', // Entry point
        '**/*.test.*',
        '**/*.spec.*',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
        // Component-specific thresholds
        'src/stores/**': {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90,
        },
        'src/pages/**': {
          branches: 75,
          functions: 75,
          lines: 75,
          statements: 75,
        },
        'src/components/**': {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70,
        },
      },
      include: ['src/**/*.{ts,tsx}'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
}); 