#!/usr/bin/env node
/**
 * Screenshot Comparison Utility
 *
 * Compares current screenshots with baselines and generates diff images
 * Usage: npm run visual:compare
 */

import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import fs from 'fs';
import path from 'path';

interface ComparisonResult {
  identifier: string;
  baselinePath: string;
  currentPath: string;
  diffPath: string;
  pixelDiff: number;
  percentDiff: number;
  passed: boolean;
  dimensions: {
    width: number;
    height: number;
  };
}

interface ComparisonOptions {
  threshold: number; // 0-1, pixel difference threshold
  includeAA: boolean; // Include anti-aliasing detection
}

const DEFAULT_OPTIONS: ComparisonOptions = {
  threshold: 0.1, // 0.1% difference allowed
  includeAA: true,
};

/**
 * Compare two PNG images and generate diff
 */
function compareImages(
  baselinePath: string,
  currentPath: string,
  diffPath: string,
  options: ComparisonOptions = DEFAULT_OPTIONS
): ComparisonResult {
  // Read images
  const baseline = PNG.sync.read(fs.readFileSync(baselinePath));
  const current = PNG.sync.read(fs.readFileSync(currentPath));

  // Check dimensions match
  if (baseline.width !== current.width || baseline.height !== current.height) {
    throw new Error(
      `Image dimensions don't match: baseline (${baseline.width}x${baseline.height}) vs current (${current.width}x${current.height})`
    );
  }

  const { width, height } = baseline;
  const diff = new PNG({ width, height });

  // Compare using pixelmatch
  const pixelDiff = pixelmatch(
    baseline.data,
    current.data,
    diff.data,
    width,
    height,
    {
      threshold: 0.1, // Pixel-level threshold
      includeAA: options.includeAA,
    }
  );

  // Write diff image
  fs.writeFileSync(diffPath, PNG.sync.write(diff));

  // Calculate percentage
  const totalPixels = width * height;
  const percentDiff = (pixelDiff / totalPixels) * 100;

  const passed = percentDiff <= options.threshold;

  return {
    identifier: path.basename(baselinePath, '.png'),
    baselinePath,
    currentPath,
    diffPath,
    pixelDiff,
    percentDiff,
    passed,
    dimensions: { width, height },
  };
}

/**
 * Compare all screenshots in baseline vs current directories
 */
function compareAllScreenshots(
  baselineDir: string,
  currentDir: string,
  diffDir: string,
  options: ComparisonOptions = DEFAULT_OPTIONS
): ComparisonResult[] {
  const results: ComparisonResult[] = [];

  // Ensure diff directory exists
  if (!fs.existsSync(diffDir)) {
    fs.mkdirSync(diffDir, { recursive: true });
  }

  // Get all baseline screenshots
  const baselineFiles = fs.readdirSync(baselineDir).filter(f => f.endsWith('.png'));

  console.log(`\n🔍 Comparing ${baselineFiles.length} screenshots...\n`);

  for (const filename of baselineFiles) {
    const baselinePath = path.join(baselineDir, filename);
    const currentPath = path.join(currentDir, filename);
    const diffPath = path.join(diffDir, filename);

    // Skip if current screenshot doesn't exist
    if (!fs.existsSync(currentPath)) {
      console.warn(`⚠️  No current screenshot for: ${filename}`);
      continue;
    }

    try {
      const result = compareImages(baselinePath, currentPath, diffPath, options);
      results.push(result);

      const status = result.passed ? '✅' : '❌';
      const percent = result.percentDiff.toFixed(4);
      console.log(`${status} ${result.identifier}: ${percent}% different (${result.pixelDiff} pixels)`);

    } catch (error) {
      console.error(`❌ Error comparing ${filename}:`, error);
    }
  }

  return results;
}

/**
 * Generate comparison report
 */
function generateReport(results: ComparisonResult[], outputPath: string): void {
  const passed = results.filter(r => r.passed);
  const failed = results.filter(r => !r.passed);

  const report = `# Visual Regression Comparison Report

Generated: ${new Date().toISOString()}
Total Screenshots: ${results.length}
Passed: ${passed.length}
Failed: ${failed.length}

## Summary

${failed.length === 0 ? '✅ All visual regression tests passed!' : `❌ ${failed.length} test(s) failed`}

${failed.length > 0 ? `## Failed Tests\n\n${failed.map(r => `### ${r.identifier}

- **Pixel Difference**: ${r.pixelDiff.toLocaleString()} pixels
- **Percentage**: ${r.percentDiff.toFixed(4)}%
- **Dimensions**: ${r.dimensions.width}x${r.dimensions.height}
- **Baseline**: \`${r.baselinePath}\`
- **Current**: \`${r.currentPath}\`
- **Diff**: \`${r.diffPath}\`

![Diff](${r.diffPath})
`).join('\n\n')}` : ''}

## All Results

| Screenshot | Status | Pixel Diff | Percentage |
|-----------|--------|-----------|-----------|
${results.map(r => `| ${r.identifier} | ${r.passed ? '✅ Pass' : '❌ Fail'} | ${r.pixelDiff.toLocaleString()} | ${r.percentDiff.toFixed(4)}% |`).join('\n')}
`;

  fs.writeFileSync(outputPath, report);
  console.log(`\n📄 Report generated: ${outputPath}`);
}

/**
 * Main execution
 */
async function main() {
  console.log('🎨 Visual Regression Screenshot Comparison\n');
  console.log('==========================================\n');

  const baselineDir = path.join(process.cwd(), '__image_snapshots__', 'baseline');
  const currentDir = path.join(process.cwd(), '__image_snapshots__', 'current');
  const diffDir = path.join(process.cwd(), '__image_snapshots__', 'diff');

  // Check directories exist
  if (!fs.existsSync(baselineDir)) {
    console.error('❌ Baseline directory not found. Run `npm run visual:baseline` first.');
    process.exit(1);
  }

  if (!fs.existsSync(currentDir)) {
    console.error('❌ Current screenshots directory not found. Run tests first.');
    process.exit(1);
  }

  // Run comparison
  const results = compareAllScreenshots(baselineDir, currentDir, diffDir);

  // Generate report
  const reportPath = path.join(process.cwd(), 'visual-report.md');
  generateReport(results, reportPath);

  // Exit with error if any failed
  const hasFailed = results.some(r => !r.passed);
  if (hasFailed) {
    console.log('\n❌ Visual regression detected. Review the diff images and report.');
    process.exit(1);
  } else {
    console.log('\n✅ All visual regression tests passed!');
    process.exit(0);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { compareImages, compareAllScreenshots, generateReport };
