/**
 * Visual Regression Testing Utilities
 *
 * This module provides utilities for capturing and comparing screenshots
 * for visual regression testing, following Ant Design's methodology.
 *
 * @see https://ant.design/docs/blog/visual-regression/
 */

import { test, expect, Page } from '@playwright/test';
import { toMatchImageSnapshot } from 'jest-image-snapshot';
import path from 'path';
import fs from 'fs';

// Extend Playwright's expect with jest-image-snapshot matcher
expect.extend({ toMatchImageSnapshot });

/**
 * Configuration for visual regression testing
 */
export interface VisualTestConfig {
  /** Component or page identifier */
  identifier: string;
  /** URL to test (relative or absolute) */
  url: string;
  /** Selector to screenshot (if not full page) */
  selector?: string;
  /** Whether to capture full page */
  fullPage?: boolean;
  /** Custom viewport size */
  viewport?: { width: number; height: number };
  /** Threshold for pixel difference (0-1) */
  threshold?: number;
  /** Selectors to hide before screenshot (e.g., timestamps, animations) */
  hideSelectors?: string[];
  /** Wait for specific selector before screenshot */
  waitForSelector?: string;
  /** Additional wait time in ms */
  waitTime?: number;
  /** Whether to mask dynamic content */
  maskDynamicContent?: boolean;
}

/**
 * Default configuration
 */
const defaultConfig: Partial<VisualTestConfig> = {
  fullPage: false,
  threshold: 0.1, // 0.1% pixel difference tolerance
  hideSelectors: [],
  maskDynamicContent: true,
};

/**
 * Common selectors for dynamic content that should be hidden/masked
 */
const DYNAMIC_CONTENT_SELECTORS = [
  '[data-testid="timestamp"]',
  '[data-testid="date"]',
  '.timestamp',
  '.date-time',
  '[class*="animation"]',
  '[class*="loading"]',
];

/**
 * Baseline directory structure
 */
export const SNAPSHOT_DIRS = {
  baseline: path.join(process.cwd(), '__image_snapshots__', 'baseline'),
  current: path.join(process.cwd(), '__image_snapshots__', 'current'),
  diff: path.join(process.cwd(), '__image_snapshots__', 'diff'),
};

/**
 * Ensure snapshot directories exist
 */
export function ensureSnapshotDirs(): void {
  Object.values(SNAPSHOT_DIRS).forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
}

/**
 * Prepare page for screenshot by hiding dynamic content
 */
async function preparePage(
  page: Page,
  config: VisualTestConfig
): Promise<void> {
  // Wait for network to be idle
  await page.waitForLoadState('networkidle');

  // Wait for custom selector if specified
  if (config.waitForSelector) {
    await page.waitForSelector(config.waitForSelector, { timeout: 10000 });
  }

  // Hide dynamic content selectors
  const selectorsToHide = [
    ...(config.hideSelectors || []),
    ...(config.maskDynamicContent ? DYNAMIC_CONTENT_SELECTORS : []),
  ];

  if (selectorsToHide.length > 0) {
    await page.addStyleTag({
      content: `
        ${selectorsToHide.join(', ')} {
          visibility: hidden !important;
        }
      `,
    });
  }

  // Disable animations for consistent screenshots
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `,
  });

  // Additional wait time if specified
  if (config.waitTime) {
    await page.waitForTimeout(config.waitTime);
  }
}

/**
 * Capture and compare screenshot for visual regression testing
 */
export async function runVisualTest(
  page: Page,
  config: VisualTestConfig
): Promise<void> {
  const finalConfig = { ...defaultConfig, ...config };

  // Ensure directories exist
  ensureSnapshotDirs();

  // Set viewport if specified
  if (finalConfig.viewport) {
    await page.setViewportSize(finalConfig.viewport);
  }

  // Navigate to URL
  const url = finalConfig.url.startsWith('http')
    ? finalConfig.url
    : `http://localhost:5173${finalConfig.url}`;
  await page.goto(url);

  // Prepare page for screenshot
  await preparePage(page, finalConfig);

  // Capture screenshot
  let screenshot: Buffer;
  if (finalConfig.selector) {
    const element = page.locator(finalConfig.selector);
    await element.waitFor({ state: 'visible' });
    screenshot = await element.screenshot();
  } else {
    screenshot = await page.screenshot({
      fullPage: finalConfig.fullPage,
    });
  }

  // Compare with baseline
  expect(screenshot).toMatchImageSnapshot({
    customSnapshotsDir: SNAPSHOT_DIRS.baseline,
    customDiffDir: SNAPSHOT_DIRS.diff,
    customSnapshotIdentifier: finalConfig.identifier,
    failureThreshold: finalConfig.threshold,
    failureThresholdType: 'percent',
  });

  // Save current screenshot for debugging
  const currentPath = path.join(
    SNAPSHOT_DIRS.current,
    `${finalConfig.identifier}.png`
  );
  fs.writeFileSync(currentPath, screenshot);
}

/**
 * Generate baseline screenshot (for baseline creation/update)
 */
export async function generateBaseline(
  page: Page,
  config: VisualTestConfig
): Promise<void> {
  const finalConfig = { ...defaultConfig, ...config };

  // Ensure directories exist
  ensureSnapshotDirs();

  // Set viewport if specified
  if (finalConfig.viewport) {
    await page.setViewportSize(finalConfig.viewport);
  }

  // Navigate to URL
  const url = finalConfig.url.startsWith('http')
    ? finalConfig.url
    : `http://localhost:5173${finalConfig.url}`;
  await page.goto(url);

  // Prepare page for screenshot
  await preparePage(page, finalConfig);

  // Capture screenshot
  let screenshot: Buffer;
  if (finalConfig.selector) {
    const element = page.locator(finalConfig.selector);
    await element.waitFor({ state: 'visible' });
    screenshot = await element.screenshot();
  } else {
    screenshot = await page.screenshot({
      fullPage: finalConfig.fullPage,
    });
  }

  // Save as baseline
  const baselinePath = path.join(
    SNAPSHOT_DIRS.baseline,
    `${finalConfig.identifier}.png`
  );
  fs.writeFileSync(baselinePath, screenshot);

  console.log(`✅ Generated baseline: ${finalConfig.identifier}`);
}

/**
 * Multi-viewport testing helper
 */
export const VIEWPORTS = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1920, height: 1080 },
  desktopWide: { width: 2560, height: 1440 },
};

/**
 * Test component across multiple viewports
 */
export async function runMultiViewportTest(
  page: Page,
  baseConfig: Omit<VisualTestConfig, 'identifier' | 'viewport'>
): Promise<void> {
  for (const [name, viewport] of Object.entries(VIEWPORTS)) {
    await runVisualTest(page, {
      ...baseConfig,
      identifier: `${baseConfig.url.replace(/\//g, '-')}-${name}`,
      viewport,
    });
  }
}

/**
 * Example test using the utilities
 */
test.describe('Example Visual Regression Tests', () => {
  test('homepage - desktop', async ({ page }) => {
    await runVisualTest(page, {
      identifier: 'homepage-desktop',
      url: '/',
      viewport: VIEWPORTS.desktop,
      threshold: 0.1,
    });
  });

  test('component - button variants', async ({ page }) => {
    await runVisualTest(page, {
      identifier: 'button-variants',
      url: '/components/button',
      selector: '[data-testid="button-showcase"]',
      threshold: 0.05,
    });
  });

  test('responsive - all viewports', async ({ page }) => {
    await runMultiViewportTest(page, {
      url: '/components/layout',
      threshold: 0.1,
    });
  });
});

/**
 * Baseline generation script
 * Run with: npx playwright test --grep @baseline
 */
test.describe('Baseline Generation @baseline', () => {
  test.skip(({ }, testInfo) => {
    // Skip in normal test runs
    return !process.env.GENERATE_BASELINE;
  });

  test('generate all baselines', async ({ page }) => {
    // Define all components/pages to generate baselines for
    const configs: VisualTestConfig[] = [
      { identifier: 'homepage', url: '/', fullPage: true },
      { identifier: 'about', url: '/about', fullPage: true },
      // Add more pages/components here
    ];

    for (const config of configs) {
      await generateBaseline(page, config);
    }
  });
});
