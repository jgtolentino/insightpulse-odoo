#!/usr/bin/env node
/**
 * Baseline Screenshot Generator
 *
 * Generates baseline screenshots for all registered components/pages
 * Usage: npm run visual:baseline
 */

import { chromium, Browser, Page } from 'playwright';
import { generateBaseline, VIEWPORTS, VisualTestConfig } from '../../tests/shared/imageTest';
import path from 'path';
import fs from 'fs';

interface ComponentConfig {
  name: string;
  url: string;
  selector?: string;
  viewports?: Array<keyof typeof VIEWPORTS>;
  fullPage?: boolean;
  waitForSelector?: string;
}

/**
 * Component registry - Add your components here
 */
const COMPONENTS: ComponentConfig[] = [
  // Example configurations
  {
    name: 'homepage',
    url: '/',
    viewports: ['desktop', 'tablet', 'mobile'],
    fullPage: true,
  },
  {
    name: 'about',
    url: '/about',
    viewports: ['desktop'],
    fullPage: true,
  },
  // Add more components...
];

/**
 * Auto-discover components from routes (optional enhancement)
 */
async function discoverComponents(): Promise<ComponentConfig[]> {
  // This could be enhanced to auto-discover from:
  // - src/pages directory structure
  // - Storybook stories
  // - Component documentation
  // - Route configuration files

  const discovered: ComponentConfig[] = [];

  // Example: Read from a component registry file
  const registryPath = path.join(process.cwd(), 'visual-regression.config.json');
  if (fs.existsSync(registryPath)) {
    const registry = JSON.parse(fs.readFileSync(registryPath, 'utf-8'));
    discovered.push(...registry.components);
  }

  return discovered;
}

/**
 * Generate baselines for a single component across viewports
 */
async function generateComponentBaselines(
  page: Page,
  component: ComponentConfig
): Promise<void> {
  console.log(`\n📸 Generating baselines for: ${component.name}`);

  const viewports = component.viewports || ['desktop'];

  for (const viewportName of viewports) {
    const viewport = VIEWPORTS[viewportName];

    const config: VisualTestConfig = {
      identifier: `${component.name}-${viewportName}`,
      url: component.url,
      selector: component.selector,
      viewport,
      fullPage: component.fullPage,
      waitForSelector: component.waitForSelector,
    };

    try {
      await generateBaseline(page, config);
      console.log(`  ✅ ${viewportName}: ${config.identifier}`);
    } catch (error) {
      console.error(`  ❌ ${viewportName} failed:`, error);
    }
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('🎨 Visual Regression Baseline Generator\n');
  console.log('====================================\n');

  let browser: Browser | null = null;

  try {
    // Launch browser
    console.log('🚀 Launching browser...');
    browser = await chromium.launch({
      headless: true,
    });

    const page = await browser.newPage();

    // Merge registered and discovered components
    const discoveredComponents = await discoverComponents();
    const allComponents = [...COMPONENTS, ...discoveredComponents];

    console.log(`\n📋 Found ${allComponents.length} components to process\n`);

    // Generate baselines for each component
    for (const component of allComponents) {
      await generateComponentBaselines(page, component);
    }

    // Generate summary
    const summaryPath = path.join(
      process.cwd(),
      '__image_snapshots__',
      'baseline',
      'BASELINE_SUMMARY.md'
    );

    const summary = `# Visual Regression Baseline Summary

Generated: ${new Date().toISOString()}
Components: ${allComponents.length}

## Components

${allComponents.map(c => `- **${c.name}**: ${c.url}`).join('\n')}

## Viewports

${Object.entries(VIEWPORTS).map(([name, size]) =>
  `- **${name}**: ${size.width}x${size.height}`
).join('\n')}

## Next Steps

1. Review generated baselines in \`__image_snapshots__/baseline/\`
2. Commit baselines to version control: \`git add __image_snapshots__/baseline/\`
3. Run visual regression tests: \`npm run visual:test\`
`;

    fs.writeFileSync(summaryPath, summary);
    console.log(`\n✅ Baseline generation complete!`);
    console.log(`📄 Summary written to: ${summaryPath}\n`);

  } catch (error) {
    console.error('\n❌ Error generating baselines:', error);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { main as generateAllBaselines };
