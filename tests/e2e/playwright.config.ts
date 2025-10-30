import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Test Configuration for InsightPulse Odoo
 *
 * Runs comprehensive end-to-end tests simulating real user workflows:
 * - Expense submission and approval
 * - Subscription management
 * - Multi-user role scenarios
 */

export default defineConfig({
  testDir: './specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'html' : 'list',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:8069',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: process.env.CI ? undefined : {
    command: 'docker-compose up odoo',
    url: 'http://localhost:8069/web/health',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
