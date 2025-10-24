---
name: odoo-migration
description: End-to-end Odoo module migration to NestJS API + Next.js UI with pixel-perfect visual parity
version: 1.0.0
tags: [migration, odoo, nestjs, nextjs, architecture]
---

# Odoo Migration Skill

## Purpose

Convert Odoo modules (Python/QWeb/SCSS/JS) into a modern monorepo architecture:

- **API**: NestJS + Prisma + PostgreSQL
- **UI**: Next.js + Tailwind CSS + shadcn/ui
- **Shared**: Design tokens + Component library

**Target**: SSIM ≥ 0.98 for pixel-perfect visual parity

## When to Use This Skill

Activate when:

- User requests "migrate Odoo module to NestJS/Next.js"
- Converting legacy Odoo apps to modern stack
- Need to preserve exact visual appearance (SSIM validation)
- Extracting Odoo business logic to standalone API

## Migration Workflow

### Phase 1: Analysis & Extraction (Parallel)

```
repo_fetch(repo, ref) → archive_url
├─> qweb_to_tsx(archive_url, theme_hint?) → {tokens_url, pieces[]}
├─> odoo_model_to_prisma(archive_url) → {prisma_url}
└─> asset_migrator(archive_url) → {asset_map_url}
```

**Actions**:

1. Clone Odoo repository and extract module
2. Parse QWeb templates → React/TSX components
3. Extract SCSS variables → design tokens
4. Convert Odoo models → Prisma schema
5. Migrate static assets (images, fonts, icons)

### Phase 2: Scaffolding

```
nest_scaffold(prisma_schema) → {bundle_url}
```

**Actions**:

1. Generate NestJS controllers from Prisma models
2. Create CRUD endpoints with validation
3. Set up authentication middleware
4. Configure database connections

### Phase 3: Visual Validation

```
visual_diff(baseline_url, candidate_url) → {ssim, lpips, passes}
```

**Actions**:

1. Deploy baseline Odoo UI (screenshot)
2. Deploy migrated Next.js UI (screenshot)
3. Compare using SSIM/LPIPS algorithms
4. **Pass**: SSIM ≥ 0.98, LPIPS ≤ 0.02
5. **Fail**: Iterate qweb_to_tsx with hints (max 3 retries)

### Phase 4: Bundle & Report

```
bundle_emit(pieces[]) → {bundle_url, report}
```

**Actions**:

1. Package all generated code
2. Create migration report (SSIM scores, changed assets, notes)
3. Generate next steps documentation
4. Emit final bundle.zip

## Critical Rules

### Visual Parity Requirements

```yaml
thresholds:
  ssim_minimum: 0.98
  lpips_maximum: 0.02
  retry_limit: 3

validation_points:
  - Desktop (1920x1080)
  - Tablet (768x1024)
  - Mobile (375x812)
```

### Design Token Extraction

```scss
// Odoo SCSS
$primary-color: #875A7B;
$font-family-base: 'Roboto', sans-serif;
$spacing-unit: 8px;

// ↓ Convert to ↓

// tokens.json
{
  "colors": {"primary": "#875A7B"},
  "fonts": {"base": "'Roboto', sans-serif"},
  "spacing": {"unit": "0.5rem"}
}

// ↓ Map to ↓

// Tailwind CSS
--color-primary: #875A7B;
--font-base: 'Roboto', sans-serif;
--spacing-unit: 0.5rem;
```

### Code Quality Standards

- **TypeScript**: Strict mode, no `any` types
- **Linting**: ESLint + Prettier
- **Testing**: Jest unit tests for business logic
- **API Contracts**: OpenAPI/Swagger documentation
- **Database**: Prisma migrations, seeded data

## Error Recovery Strategies

### SSIM < 0.98 (Visual Mismatch)

```typescript
if (ssim < 0.98) {
  hints = generate_visual_hints(diff_image);
  // Example hints:
  // - "Increase border-radius on primary buttons"
  // - "Adjust padding in sidebar navigation"
  // - "Match font-weight for headings"

  retry_count++;
  if (retry_count <= 3) {
    pieces = qweb_to_tsx(archive_url, hints);
    ssim = visual_diff(baseline, updated);
  } else {
    return {
      status: 'needs-work',
      reason: 'Could not achieve SSIM ≥ 0.98 after 3 attempts',
      current_ssim: ssim,
      hints: hints,
    };
  }
}
```

### Missing Dependencies

```typescript
if (missing_models.length > 0) {
  warning = `Missing Odoo models: ${missing_models.join(', ')}`;
  suggestion = 'Add these models to Prisma schema manually';
  // Continue with partial migration
}
```

### Asset Migration Failures

```typescript
if (failed_assets.length > 0) {
  for (const asset of failed_assets) {
    log_warning(`Failed to migrate: ${asset.path}`);
    log_warning(`Reason: ${asset.error}`);
    // Provide fallback URLs or placeholders
  }
}
```

## Output Contract

### Success Response

```json
{
  "status": "success",
  "bundle_url": "https://storage.example.com/migrations/bundle-abc123.zip",
  "report": {
    "ssim": 0.987,
    "lpips": 0.015,
    "changed_assets": ["logo.svg → public/assets/logo.svg", "styles.scss → styles/globals.css"],
    "notes": [
      "All 12 models converted successfully",
      "3 QWeb templates → TSX components",
      "Visual parity achieved on all viewports"
    ]
  },
  "next_steps": [
    "Extract bundle.zip to your monorepo",
    "Run `npm install` in /apps/api and /apps/web",
    "Configure DATABASE_URL in .env",
    "Run Prisma migrations: `npx prisma migrate dev`",
    "Start dev servers: `npm run dev`"
  ]
}
```

### Needs Work Response

```json
{
  "status": "needs-work",
  "bundle_url": "https://storage.example.com/migrations/bundle-abc123.zip",
  "report": {
    "ssim": 0.94,
    "lpips": 0.08,
    "changed_assets": [...],
    "notes": [
      "SSIM below threshold (0.94 < 0.98)",
      "Primary issue: Button border-radius mismatch",
      "Secondary issue: Sidebar padding incorrect"
    ]
  },
  "next_steps": [
    "Manual adjustment needed for button styles",
    "Review /apps/web/components/Button.tsx",
    "Adjust border-radius from 6px to 8px",
    "Re-run visual diff after changes"
  ]
}
```

## Monorepo Structure

```
monorepo/
├── apps/
│   ├── api/                   # NestJS backend
│   │   ├── src/
│   │   │   ├── modules/       # Generated from Odoo models
│   │   │   ├── prisma/        # Database schema
│   │   │   └── main.ts
│   │   └── package.json
│   └── web/                   # Next.js frontend
│       ├── app/               # App router
│       ├── components/        # TSX from QWeb
│       ├── styles/            # Tailwind + tokens
│       └── package.json
├── packages/
│   └── ui/                    # Shared component library
│       ├── components/        # Button, Input, etc.
│       ├── tokens.json        # Design tokens
│       └── tailwind.config.ts
└── package.json               # Workspace root
```

## Example Invocation

```typescript
// User request:
"Migrate the Odoo HR module from github.com/odoo/odoo/addons/hr
to NestJS + Next.js. Use the Odoo 18 theme for visual baseline."

// Agent execution:
const archive = await repo_fetch("odoo/odoo", "18.0");
const [tsx, prisma, assets] = await Promise.all([
  qweb_to_tsx(archive, "odoo-18-theme"),
  odoo_model_to_prisma(archive),
  asset_migrator(archive)
]);
const nest_bundle = await nest_scaffold(prisma);
const baseline_url = "https://odoo.example.com/hr";
const candidate_url = await deploy_preview(tsx);
const validation = await visual_diff(baseline_url, candidate_url);

if (validation.ssim >= 0.98) {
  const bundle = await bundle_emit([tsx, nest_bundle, assets]);
  return {
    status: "success",
    bundle_url: bundle.url,
    report: {
      ssim: validation.ssim,
      lpips: validation.lpips,
      changed_assets: assets.map,
      notes: ["Migration successful"]
    },
    next_steps: ["Download bundle", "Run npm install", "Configure .env"]
  };
}
```

## Quality Checklist

Before marking migration complete:

- [ ] SSIM ≥ 0.98 on all viewports (desktop, tablet, mobile)
- [ ] LPIPS ≤ 0.02 for color/structure fidelity
- [ ] All Odoo models converted to Prisma schema
- [ ] All QWeb templates converted to TSX components
- [ ] All SCSS variables extracted to design tokens
- [ ] All static assets migrated (images, fonts, icons)
- [ ] NestJS API compiles without errors
- [ ] Next.js UI builds successfully
- [ ] TypeScript strict mode passes
- [ ] All critical user flows functional
- [ ] Database migrations generated
- [ ] API documentation generated (Swagger)
- [ ] README with setup instructions included

## Common Pitfall Avoidance

### Pitfall 1: Hardcoded Styles

**Wrong**:

```tsx
<button className="bg-[#875A7B] rounded-[8px]">
```

**Right**:

```tsx
<button className="bg-primary rounded-lg">
```

### Pitfall 2: Missing Odoo Context

**Wrong**:

```typescript
// Direct field mapping
name: user.name;
```

**Right**:

```typescript
// Preserve Odoo computed fields
get fullName() {
  return `${this.firstName} ${this.lastName}`;
}
```

### Pitfall 3: Incomplete Visual Testing

**Wrong**:

```typescript
// Only test desktop
visual_diff(baseline, candidate);
```

**Right**:

```typescript
// Test all viewports
await Promise.all([
  visual_diff(baseline_desktop, candidate_desktop),
  visual_diff(baseline_tablet, candidate_tablet),
  visual_diff(baseline_mobile, candidate_mobile),
]);
```

## Success Metrics

Track these KPIs:

- Migration time (target: <30 minutes per module)
- Visual parity score (target: SSIM ≥ 0.98)
- Code quality (target: 0 TypeScript errors, 0 lint warnings)
- Test coverage (target: ≥ 80% for business logic)
- Bundle size (target: Next.js first load < 200KB)
- API response time (target: P95 < 200ms)

## References

- [Odoo Developer Documentation](https://www.odoo.com/documentation)
- [NestJS Documentation](https://docs.nestjs.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [SSIM Paper](https://ieeexplore.ieee.org/document/1284395)
- [Design Tokens Spec](https://design-tokens.github.io/community-group/)
