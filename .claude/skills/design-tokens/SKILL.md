---
name: design-tokens
description: Extract and transform design tokens from SCSS/CSS to modern design systems (Tailwind, CSS Variables, Design Tokens Spec)
version: 1.0.0
tags: [design-tokens, scss, tailwind, css-variables, theming]
---

# Design Tokens Extraction Skill

## Purpose

Extract design tokens from legacy stylesheets (SCSS, CSS) and transform them into:

- **Design Tokens Spec** (JSON format)
- **Tailwind CSS** configuration
- **CSS Custom Properties** (CSS variables)
- **TypeScript** type definitions

Target: **100% token coverage** - zero hardcoded values in components.

## When to Use This Skill

Activate when:

- Migrating from SCSS/CSS to Tailwind CSS
- Creating a design system from existing styles
- Need to extract reusable design tokens
- Building a component library with theming support

## Token Categories

### Colors

```scss
// Input (SCSS)
$o-brand-primary: #875A7B;
$o-brand-secondary: #4C4C4C;
$o-success: #28a745;
$o-warning: #ffc107;
$o-danger: #dc3545;
$o-info: #17a2b8;

// Output (tokens.json)
{
  "colors": {
    "brand": {
      "primary": {"value": "#875A7B", "type": "color"},
      "secondary": {"value": "#4C4C4C", "type": "color"}
    },
    "status": {
      "success": {"value": "#28a745", "type": "color"},
      "warning": {"value": "#ffc107", "type": "color"},
      "danger": {"value": "#dc3545", "type": "color"},
      "info": {"value": "#17a2b8", "type": "color"}
    }
  }
}
```

### Spacing

```scss
// Input (SCSS)
$o-spacing-xs: 4px;
$o-spacing-sm: 8px;
$o-spacing-md: 16px;
$o-spacing-lg: 24px;
$o-spacing-xl: 32px;

// Output (tokens.json)
{
  "spacing": {
    "xs": {"value": "0.25rem", "type": "dimension"},
    "sm": {"value": "0.5rem", "type": "dimension"},
    "md": {"value": "1rem", "type": "dimension"},
    "lg": {"value": "1.5rem", "type": "dimension"},
    "xl": {"value": "2rem", "type": "dimension"}
  }
}
```

### Typography

```scss
// Input (SCSS)
$o-font-family-base: 'Roboto', sans-serif;
$o-font-size-xs: 12px;
$o-font-size-sm: 14px;
$o-font-size-base: 16px;
$o-font-size-lg: 18px;
$o-font-size-xl: 24px;
$o-font-weight-normal: 400;
$o-font-weight-bold: 700;
$o-line-height-base: 1.5;

// Output (tokens.json)
{
  "typography": {
    "fontFamily": {
      "base": {"value": "'Roboto', sans-serif", "type": "fontFamily"}
    },
    "fontSize": {
      "xs": {"value": "0.75rem", "type": "dimension"},
      "sm": {"value": "0.875rem", "type": "dimension"},
      "base": {"value": "1rem", "type": "dimension"},
      "lg": {"value": "1.125rem", "type": "dimension"},
      "xl": {"value": "1.5rem", "type": "dimension"}
    },
    "fontWeight": {
      "normal": {"value": "400", "type": "fontWeight"},
      "bold": {"value": "700", "type": "fontWeight"}
    },
    "lineHeight": {
      "base": {"value": "1.5", "type": "number"}
    }
  }
}
```

### Borders

```scss
// Input (SCSS)
$o-border-radius-sm: 4px;
$o-border-radius-md: 8px;
$o-border-radius-lg: 12px;
$o-border-width: 1px;
$o-border-color: #dee2e6;

// Output (tokens.json)
{
  "borders": {
    "radius": {
      "sm": {"value": "0.25rem", "type": "dimension"},
      "md": {"value": "0.5rem", "type": "dimension"},
      "lg": {"value": "0.75rem", "type": "dimension"}
    },
    "width": {
      "default": {"value": "1px", "type": "dimension"}
    },
    "color": {
      "default": {"value": "#dee2e6", "type": "color"}
    }
  }
}
```

### Shadows

```scss
// Input (SCSS)
$o-box-shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
$o-box-shadow-md: 0 2px 4px rgba(0,0,0,0.1);
$o-box-shadow-lg: 0 4px 8px rgba(0,0,0,0.15);

// Output (tokens.json)
{
  "shadows": {
    "sm": {"value": "0 1px 2px rgba(0,0,0,0.05)", "type": "shadow"},
    "md": {"value": "0 2px 4px rgba(0,0,0,0.1)", "type": "shadow"},
    "lg": {"value": "0 4px 8px rgba(0,0,0,0.15)", "type": "shadow"}
  }
}
```

## Tailwind CSS Integration

### Generate Tailwind Config

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';
import tokens from './tokens.json';

export default {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: tokens.colors.brand.primary.value,
        secondary: tokens.colors.brand.secondary.value,
        success: tokens.colors.status.success.value,
        warning: tokens.colors.status.warning.value,
        danger: tokens.colors.status.danger.value,
        info: tokens.colors.status.info.value,
      },
      spacing: {
        xs: tokens.spacing.xs.value,
        sm: tokens.spacing.sm.value,
        md: tokens.spacing.md.value,
        lg: tokens.spacing.lg.value,
        xl: tokens.spacing.xl.value,
      },
      fontSize: {
        xs: tokens.typography.fontSize.xs.value,
        sm: tokens.typography.fontSize.sm.value,
        base: tokens.typography.fontSize.base.value,
        lg: tokens.typography.fontSize.lg.value,
        xl: tokens.typography.fontSize.xl.value,
      },
      fontFamily: {
        sans: [tokens.typography.fontFamily.base.value],
      },
      fontWeight: {
        normal: tokens.typography.fontWeight.normal.value,
        bold: tokens.typography.fontWeight.bold.value,
      },
      lineHeight: {
        base: tokens.typography.lineHeight.base.value,
      },
      borderRadius: {
        sm: tokens.borders.radius.sm.value,
        DEFAULT: tokens.borders.radius.md.value,
        lg: tokens.borders.radius.lg.value,
      },
      boxShadow: {
        sm: tokens.shadows.sm.value,
        DEFAULT: tokens.shadows.md.value,
        lg: tokens.shadows.lg.value,
      },
    },
  },
  plugins: [],
} satisfies Config;
```

### Usage in Components

**Before (hardcoded)**:

```tsx
<button style={{
  backgroundColor: '#875A7B',
  padding: '16px',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
}}>
```

**After (token-based)**:

```tsx
<button className="bg-primary p-md rounded shadow">
```

## CSS Custom Properties

### Generate CSS Variables

```css
/* styles/tokens.css */
:root {
  /* Colors */
  --color-primary: #875a7b;
  --color-secondary: #4c4c4c;
  --color-success: #28a745;
  --color-warning: #ffc107;
  --color-danger: #dc3545;
  --color-info: #17a2b8;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-family-base: 'Roboto', sans-serif;
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.5rem;
  --font-weight-normal: 400;
  --font-weight-bold: 700;
  --line-height-base: 1.5;

  /* Borders */
  --border-radius-sm: 0.25rem;
  --border-radius-md: 0.5rem;
  --border-radius-lg: 0.75rem;
  --border-width: 1px;
  --border-color: #dee2e6;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.15);
}
```

### Usage

```css
.button {
  background-color: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}
```

## TypeScript Type Definitions

### Generate Types

```typescript
// types/tokens.ts
export interface DesignTokens {
  colors: {
    brand: {
      primary: string;
      secondary: string;
    };
    status: {
      success: string;
      warning: string;
      danger: string;
      info: string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  typography: {
    fontFamily: {
      base: string;
    };
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
    };
    fontWeight: {
      normal: number;
      bold: number;
    };
    lineHeight: {
      base: number;
    };
  };
  borders: {
    radius: {
      sm: string;
      md: string;
      lg: string;
    };
    width: {
      default: string;
    };
    color: {
      default: string;
    };
  };
  shadows: {
    sm: string;
    md: string;
    lg: string;
  };
}

export const tokens: DesignTokens = require('./tokens.json');
```

## Extraction Algorithm

### Step 1: Parse SCSS Files

```typescript
import * as sass from 'sass';

function parseSCSSVariables(file: string): Map<string, string> {
  const content = fs.readFileSync(file, 'utf-8');
  const variables = new Map<string, string>();

  // Match SCSS variables: $variable-name: value;
  const regex = /\$([a-zA-Z0-9_-]+):\s*([^;]+);/g;
  let match;

  while ((match = regex.exec(content)) !== null) {
    const [, name, value] = match;
    variables.set(name, value.trim());
  }

  return variables;
}
```

### Step 2: Categorize Tokens

```typescript
function categorizeToken(name: string, value: string): TokenCategory {
  // Color detection
  if (/color|bg|background|foreground|text/.test(name) || /^#[0-9a-fA-F]{3,8}$/.test(value)) {
    return 'colors';
  }

  // Spacing detection
  if (/spacing|padding|margin|gap/.test(name) || /^\d+(px|rem|em)$/.test(value)) {
    return 'spacing';
  }

  // Typography detection
  if (/font|text|line-height|letter-spacing/.test(name)) {
    return 'typography';
  }

  // Border detection
  if (/border|radius/.test(name)) {
    return 'borders';
  }

  // Shadow detection
  if (/shadow|elevation/.test(name)) {
    return 'shadows';
  }

  return 'other';
}
```

### Step 3: Transform Values

```typescript
function transformValue(value: string, type: TokenType): string {
  // Convert px to rem (16px base)
  if (type === 'dimension' && value.endsWith('px')) {
    const px = parseFloat(value);
    return `${px / 16}rem`;
  }

  // Normalize color formats
  if (type === 'color') {
    // Convert rgb() to hex
    // Convert hsl() to hex
    // Validate hex format
    return normalizeColor(value);
  }

  return value;
}
```

### Step 4: Generate Output

```typescript
function generateTokens(variables: Map<string, string>): DesignTokens {
  const tokens: DesignTokens = {
    colors: {},
    spacing: {},
    typography: {},
    borders: {},
    shadows: {},
  };

  for (const [name, value] of variables) {
    const category = categorizeToken(name, value);
    const type = inferTokenType(value);
    const transformedValue = transformValue(value, type);

    // Build nested structure
    const path = name.split('-');
    setNestedValue(tokens[category], path, {
      value: transformedValue,
      type: type,
    });
  }

  return tokens;
}
```

## Validation Rules

### Token Completeness

```typescript
const requiredTokens = {
  colors: ['primary', 'secondary', 'success', 'warning', 'danger', 'info'],
  spacing: ['xs', 'sm', 'md', 'lg', 'xl'],
  typography: ['fontFamily.base', 'fontSize.base'],
};

function validateTokens(tokens: DesignTokens): ValidationResult {
  const missing = [];

  for (const [category, required] of Object.entries(requiredTokens)) {
    for (const path of required) {
      if (!getNestedValue(tokens[category], path.split('.'))) {
        missing.push(`${category}.${path}`);
      }
    }
  }

  return {
    valid: missing.length === 0,
    missing: missing,
  };
}
```

### Token Naming Convention

```typescript
const namingRules = {
  colors: /^[a-z]+(-[a-z]+)*$/, // kebab-case
  spacing: /^(xs|sm|md|lg|xl|\d+)$/,
  typography: /^[a-z]+([A-Z][a-z]+)*$/, // camelCase
};

function validateNaming(tokens: DesignTokens): string[] {
  const violations = [];

  for (const [category, pattern] of Object.entries(namingRules)) {
    const names = getAllTokenNames(tokens[category]);
    for (const name of names) {
      if (!pattern.test(name)) {
        violations.push(`${category}.${name} violates naming convention`);
      }
    }
  }

  return violations;
}
```

## Function Signature

```typescript
async function extract_design_tokens(
  archive_url: string,
  theme_hint?: string
): Promise<{
  tokens_url: string;
  tailwind_config_url: string;
  css_variables_url: string;
  types_url: string;
}> {
  // 1. Download and extract
  const archive = await downloadArchive(archive_url);
  const scssFiles = extractSCSSFiles(archive, theme_hint);

  // 2. Parse and extract variables
  const variables = new Map<string, string>();
  for (const file of scssFiles) {
    const fileVars = parseSCSSVariables(file);
    variables = new Map([...variables, ...fileVars]);
  }

  // 3. Categorize and transform
  const tokens = generateTokens(variables);

  // 4. Validate
  const validation = validateTokens(tokens);
  if (!validation.valid) {
    throw new Error(`Missing required tokens: ${validation.missing.join(', ')}`);
  }

  // 5. Generate outputs
  const tokens_json = JSON.stringify(tokens, null, 2);
  const tailwind_config = generateTailwindConfig(tokens);
  const css_variables = generateCSSVariables(tokens);
  const types = generateTypeScript(tokens);

  // 6. Upload and return URLs
  return {
    tokens_url: await upload('tokens.json', tokens_json),
    tailwind_config_url: await upload('tailwind.config.ts', tailwind_config),
    css_variables_url: await upload('tokens.css', css_variables),
    types_url: await upload('tokens.ts', types),
  };
}
```

## Best Practices

### ✅ DO

- Use semantic token names (primary, not color1)
- Convert px to rem for scalability
- Organize tokens hierarchically
- Include all token types (colors, spacing, typography, borders, shadows)
- Generate TypeScript types for type safety
- Validate token completeness

### ❌ DON'T

- Use generic names (color1, spacing1)
- Mix units (px, rem, em in same category)
- Flatten token structure
- Skip validation
- Hardcode values in components
- Ignore design system conventions

## Success Criteria

- [ ] 100% token coverage (zero hardcoded values)
- [ ] All token categories present
- [ ] Semantic naming conventions followed
- [ ] Tailwind config generated
- [ ] CSS variables generated
- [ ] TypeScript types generated
- [ ] Tokens validated successfully
- [ ] Components use tokens exclusively

## References

- [Design Tokens Specification](https://design-tokens.github.io/community-group/)
- [Tailwind CSS Configuration](https://tailwindcss.com/docs/configuration)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [SCSS Documentation](https://sass-lang.com/documentation)
