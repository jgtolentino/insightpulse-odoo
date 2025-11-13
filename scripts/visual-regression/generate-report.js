#!/usr/bin/env node
/**
 * Visual Regression HTML Report Generator
 *
 * Generates an interactive HTML report for visual regression testing results
 * Usage: node scripts/visual-regression/generate-report.js
 */

const fs = require('fs');
const path = require('path');

/**
 * Generate HTML report from comparison results
 */
function generateHTMLReport(diffDir, outputPath) {
  const diffFiles = fs.existsSync(diffDir)
    ? fs.readdirSync(diffDir).filter(f => f.endsWith('.png'))
    : [];

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Visual Regression Report</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f5f5;
      padding: 20px;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 30px;
    }

    h1 {
      font-size: 32px;
      margin-bottom: 10px;
      color: #1890ff;
    }

    .summary {
      background: #f0f2f5;
      padding: 20px;
      border-radius: 6px;
      margin: 20px 0;
    }

    .summary-stat {
      display: inline-block;
      margin-right: 30px;
      font-size: 16px;
    }

    .summary-stat strong {
      color: #1890ff;
      font-size: 24px;
      display: block;
    }

    .status-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 600;
      margin-left: 10px;
    }

    .status-pass {
      background: #52c41a;
      color: white;
    }

    .status-fail {
      background: #ff4d4f;
      color: white;
    }

    .diff-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 20px;
      margin-top: 30px;
    }

    .diff-item {
      border: 1px solid #d9d9d9;
      border-radius: 6px;
      overflow: hidden;
      transition: all 0.3s;
    }

    .diff-item:hover {
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transform: translateY(-2px);
    }

    .diff-item h3 {
      background: #fafafa;
      padding: 12px 16px;
      font-size: 16px;
      border-bottom: 1px solid #d9d9d9;
    }

    .diff-images {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 1px;
      background: #d9d9d9;
    }

    .diff-image {
      position: relative;
      background: white;
      padding: 8px;
    }

    .diff-image img {
      width: 100%;
      height: auto;
      display: block;
      border-radius: 4px;
    }

    .diff-image label {
      display: block;
      text-align: center;
      font-size: 12px;
      color: #666;
      margin-top: 8px;
      font-weight: 500;
    }

    .no-diffs {
      text-align: center;
      padding: 60px 20px;
      color: #52c41a;
      font-size: 18px;
    }

    .no-diffs svg {
      width: 64px;
      height: 64px;
      margin-bottom: 20px;
    }

    .timestamp {
      color: #8c8c8c;
      font-size: 14px;
      margin-top: 10px;
    }

    .comparison-slider {
      position: relative;
      width: 100%;
      height: 300px;
      overflow: hidden;
      border-radius: 4px;
    }

    .comparison-slider img {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      object-fit: contain;
    }

    .slider-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 50%;
      height: 100%;
      overflow: hidden;
      z-index: 1;
    }

    .slider-handle {
      position: absolute;
      top: 0;
      left: 50%;
      width: 4px;
      height: 100%;
      background: #1890ff;
      cursor: ew-resize;
      z-index: 2;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🎨 Visual Regression Report</h1>
    <p class="timestamp">Generated: ${new Date().toISOString()}</p>

    <div class="summary">
      <div class="summary-stat">
        <strong>${diffFiles.length}</strong>
        <span>Differences Found</span>
      </div>
      ${diffFiles.length === 0
        ? '<span class="status-badge status-pass">All Tests Passed</span>'
        : '<span class="status-badge status-fail">Regressions Detected</span>'}
    </div>

    ${diffFiles.length === 0 ? `
      <div class="no-diffs">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p>No visual differences detected. All screenshots match baselines!</p>
      </div>
    ` : `
      <div class="diff-grid">
        ${diffFiles.map(file => {
          const name = path.basename(file, '.png');
          const baselinePath = `../baseline/${file}`;
          const currentPath = `../current/${file}`;
          const diffPath = `../diff/${file}`;

          return `
            <div class="diff-item">
              <h3>${name}</h3>
              <div class="diff-images">
                <div class="diff-image">
                  <img src="${baselinePath}" alt="Baseline">
                  <label>Baseline</label>
                </div>
                <div class="diff-image">
                  <img src="${currentPath}" alt="Current">
                  <label>Current</label>
                </div>
                <div class="diff-image">
                  <img src="${diffPath}" alt="Diff">
                  <label>Diff</label>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `}
  </div>

  <script>
    // Add interactive comparison slider (future enhancement)
    console.log('Visual regression report loaded');
  </script>
</body>
</html>`;

  fs.writeFileSync(outputPath, html);
  console.log(`✅ HTML report generated: ${outputPath}`);
}

// Main execution
function main() {
  const diffDir = path.join(process.cwd(), '__image_snapshots__', 'diff');
  const outputPath = path.join(process.cwd(), 'visual-report.html');

  if (!fs.existsSync(diffDir)) {
    console.log('No diff directory found. Creating empty report.');
  }

  generateHTMLReport(diffDir, outputPath);
}

if (require.main === module) {
  main();
}

module.exports = { generateHTMLReport };
