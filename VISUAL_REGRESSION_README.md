# Visual Regression Testing

Comprehensive visual regression testing infrastructure for preventing visual bugs and ensuring UI consistency.

## Overview

This repository implements visual regression testing following [Ant Design's methodology](https://ant.design/docs/blog/visual-regression/), using:

- **Playwright** - Browser automation and screenshot capture
- **jest-image-snapshot** - Pixel-perfect image comparison
- **GitHub Actions** - Automated CI/CD integration

## Quick Start

### 1. Install Dependencies

```bash
npm install
npx playwright install chromium
```

### 2. Generate Initial Baselines

```bash
# Start dev server (in another terminal)
npm run dev

# Generate baseline screenshots
npm run visual:baseline
```

This creates baseline screenshots in `__image_snapshots__/baseline/`

### 3. Run Visual Tests

```bash
npm run visual:test
```

This compares current screenshots with baselines and fails if differences are detected.

## NPM Scripts

| Script | Description |
|--------|-------------|
| `visual:test` | Run visual regression tests |
| `visual:baseline` | Generate baseline screenshots |
| `visual:update-baseline` | Alias for baseline generation |
| `visual:compare` | Compare screenshots and generate report |
| `visual:report` | Generate HTML report from diffs |
| `visual:upload` | Upload artifacts to cloud storage |

## Directory Structure

```
insightpulse-odoo/
├── .github/workflows/
│   ├── visual-regression-pr.yml          # PR checks
│   ├── visual-regression-baseline.yml    # Baseline updates
│   └── visual-regression-report.yml      # Report generation
│
├── tests/
│   └── shared/
│       └── imageTest.tsx                 # Test utilities
│
├── scripts/visual-regression/
│   ├── capture-baselines.ts              # Baseline generation
│   ├── compare-screenshots.ts            # Image comparison
│   ├── generate-report.js                # HTML report generator
│   └── upload-to-storage.ts              # Cloud upload
│
├── __image_snapshots__/
│   ├── baseline/                         # Baseline screenshots (committed)
│   ├── current/                          # Latest test screenshots (ignored)
│   └── diff/                             # Diff images (ignored)
│
├── playwright.config.ts                   # Playwright configuration
├── visual-regression.config.json          # Component registry
└── VISUAL_REGRESSION_README.md           # This file
```

## Writing Visual Tests

### Basic Test

```typescript
import { test } from '@playwright/test';
import { runVisualTest } from '../shared/imageTest';

test('homepage visual test', async ({ page }) => {
  await runVisualTest(page, {
    identifier: 'homepage-desktop',
    url: '/',
    threshold: 0.1,
  });
});
```

### Multi-Viewport Test

```typescript
import { test } from '@playwright/test';
import { runMultiViewportTest } from '../shared/imageTest';

test('responsive layout', async ({ page }) => {
  await runMultiViewportTest(page, {
    url: '/components/layout',
    threshold: 0.1,
  });
});
```

### Component-Specific Test

```typescript
import { test } from '@playwright/test';
import { runVisualTest, VIEWPORTS } from '../shared/imageTest';

test('button variants', async ({ page }) => {
  await runVisualTest(page, {
    identifier: 'button-variants',
    url: '/components/button',
    selector: '[data-testid="button-showcase"]',
    viewport: VIEWPORTS.desktop,
    threshold: 0.05,
  });
});
```

## CI/CD Integration

### Pull Request Workflow

When you create a PR:

1. CI runs visual regression tests
2. If differences detected:
   - ❌ Check fails
   - 📸 Diff screenshots uploaded as artifacts
   - 💬 PR comment posted with preview
3. If no differences:
   - ✅ Check passes

### Updating Baselines

When visual changes are intentional:

```bash
# 1. Review the diffs
npm run visual:test
npm run visual:report  # Open visual-report.html

# 2. Update baselines if changes are expected
npm run visual:update-baseline

# 3. Commit updated baselines
git add __image_snapshots__/baseline/
git commit -m "chore: update visual baselines for new button design"
git push
```

### Baseline Auto-Update on Main

When PRs are merged to `main`:
- Baselines automatically regenerate
- Updated baselines are committed back to repo
- Ensures baselines stay in sync with production

## Configuration

### Component Registry

Edit `visual-regression.config.json` to register components:

```json
{
  "components": [
    {
      "name": "homepage",
      "url": "/",
      "viewports": ["desktop", "tablet", "mobile"],
      "fullPage": true
    }
  ]
}
```

### Threshold Configuration

Adjust comparison sensitivity:

```typescript
// Strict (0.01% = critical UI)
threshold: 0.01

// Normal (0.1% = most components)
threshold: 0.1

// Relaxed (0.5% = charts/animations)
threshold: 0.5
```

### Hide Dynamic Content

Mask timestamps, animations, etc:

```typescript
await runVisualTest(page, {
  identifier: 'dashboard',
  url: '/dashboard',
  hideSelectors: [
    '[data-testid="timestamp"]',
    '.loading-spinner',
  ],
});
```

## Best Practices

### ✅ Do

- Test critical user-facing components
- Test responsive layouts across viewports
- Test theme variations (light/dark)
- Commit baselines to version control
- Review diffs before updating baselines
- Use consistent CI environment (Docker)

### ❌ Don't

- Test frequently changing content (timestamps, news feeds)
- Test random/dynamic data
- Test third-party embedded content
- Update baselines without review
- Run tests on different OS than CI
- Ignore visual regression failures

## Troubleshooting

### "Screenshots don't match but look identical"

**Cause:** Platform-specific font rendering

**Solution:**
```bash
# Run tests in Docker matching CI environment
docker run -v $(pwd):/app -w /app mcr.microsoft.com/playwright:v1.40.0 npm run visual:test
```

### "Tests pass locally but fail in CI"

**Cause:** Different browser versions or OS

**Solution:**
- Pin Playwright version in package.json
- Use same browser in local and CI
- Enable font rendering flags in playwright.config.ts

### "Too many false positives"

**Cause:** Anti-aliasing or minor rendering differences

**Solution:**
```typescript
// Increase threshold slightly
threshold: 0.15  // from 0.1

// Or mask problematic elements
hideSelectors: ['.problematic-element']
```

### "Baselines outdated after dependency update"

**Cause:** Library updated component styling

**Solution:**
```bash
# Review and update all baselines
npm run visual:update-baseline
git add __image_snapshots__/baseline/
git commit -m "chore: update baselines after dependency update"
```

## Cloud Storage (Optional)

Upload visual regression artifacts to cloud storage:

### AWS S3

```bash
export VISUAL_STORAGE_PROVIDER=s3
export VISUAL_STORAGE_BUCKET=my-bucket
export VISUAL_STORAGE_REGION=us-east-1
export VISUAL_STORAGE_ACCESS_KEY=xxx
export VISUAL_STORAGE_SECRET_KEY=xxx

npm run visual:upload
```

### Azure Blob Storage

```bash
export VISUAL_STORAGE_PROVIDER=azure
export VISUAL_STORAGE_CONTAINER=visual-regression
export AZURE_STORAGE_CONNECTION_STRING=xxx

npm run visual:upload
```

### Local Storage

```bash
# Default - copies to public/visual-regression
npm run visual:upload
```

## Examples

See `tests/shared/imageTest.tsx` for comprehensive examples including:

- Full-page screenshots
- Component-specific screenshots
- Multi-viewport testing
- Theme variation testing
- Custom selector testing

## Resources

### Documentation
- [Ant Design Visual Regression](https://ant.design/docs/blog/visual-regression/)
- [Playwright Screenshots](https://playwright.dev/docs/screenshots)
- [jest-image-snapshot](https://github.com/americanexpress/jest-image-snapshot)

### Skills
- `.claude/skills/visual-regression-testing/SKILL.md` - Full skill documentation
- `.claude/skills/agent-capabilities/SKILL.md` - Agent capabilities reference
- `.claude/skills/webapp-testing/SKILL.md` - Web testing utilities

## Support

For issues or questions:
1. Check this README
2. Review skill documentation in `.claude/skills/`
3. Check GitHub workflow logs
4. Open an issue

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-11-13
**Methodology:** Ant Design Visual Regression Testing
