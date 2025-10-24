---
name: qweb-to-react
description: Convert Odoo QWeb templates to React/TSX components with design token extraction
version: 1.0.0
tags: [qweb, react, tsx, templates, conversion]
---

# QWeb to React Conversion Skill

## Purpose

Transform Odoo QWeb XML templates into modern React/TSX components while:

- Preserving exact visual appearance (pixel parity)
- Extracting design tokens from inline styles and SCSS
- Maintaining component hierarchy and data flow
- Generating type-safe TypeScript interfaces

## When to Use This Skill

Activate when:

- Converting Odoo templates to React components
- Need to extract design tokens from Odoo themes
- Migrating QWeb directives to React hooks
- Preserving visual parity during frontend rewrites

## QWeb → React Mapping

### Template Directives

| QWeb Directive | React Equivalent                                   | Notes                      |
| -------------- | -------------------------------------------------- | -------------------------- |
| `t-if`         | `{condition && <Component/>}`                      | Conditional rendering      |
| `t-foreach`    | `{items.map(item => ...)}`                         | Iteration                  |
| `t-set`        | `const varName = value`                            | Variable assignment        |
| `t-esc`        | `{value}`                                          | Safe text interpolation    |
| `t-raw`        | `<div dangerouslySetInnerHTML={{__html: value}}/>` | **Unsafe!** Sanitize first |
| `t-att-`       | `{...props}`                                       | Dynamic attributes         |
| `t-attf-`      | Template literals                                  | String interpolation       |
| `t-call`       | `<SubComponent/>`                                  | Component composition      |
| `t-field`      | `<Field {...fieldProps}/>`                         | Odoo field widget          |

### Example Conversion

**Odoo QWeb**:

```xml
<template id="hr_employee_card">
  <div class="card" t-att-data-id="employee.id">
    <t t-if="employee.image">
      <img t-att-src="employee.image" alt="Employee Photo"/>
    </t>
    <div class="card-body">
      <h3 t-esc="employee.name"/>
      <p t-esc="employee.job_title"/>
      <t t-foreach="employee.skills" t-as="skill">
        <span class="badge" t-esc="skill.name"/>
      </t>
    </div>
  </div>
</template>
```

**React/TSX**:

```tsx
interface Employee {
  id: number;
  image?: string;
  name: string;
  job_title: string;
  skills: Array<{ name: string }>;
}

export function EmployeeCard({ employee }: { employee: Employee }) {
  return (
    <div className="card" data-id={employee.id}>
      {employee.image && <img src={employee.image} alt="Employee Photo" />}
      <div className="card-body">
        <h3>{employee.name}</h3>
        <p>{employee.job_title}</p>
        {employee.skills.map((skill, index) => (
          <span key={index} className="badge">
            {skill.name}
          </span>
        ))}
      </div>
    </div>
  );
}
```

## Design Token Extraction

### SCSS Variable Discovery

**Input (Odoo SCSS)**:

```scss
// o_web_enterprise/static/src/scss/_variables.scss
$o-brand-primary: #875a7b;
$o-brand-secondary: #4c4c4c;
$o-border-radius: 8px;
$o-spacing-base: 16px;
$o-font-size-base: 14px;
$o-font-family: 'Roboto', sans-serif;
$o-box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
```

**Output (Design Tokens)**:

```json
{
  "colors": {
    "brand": {
      "primary": "#875A7B",
      "secondary": "#4C4C4C"
    }
  },
  "borders": {
    "radius": {
      "default": "8px"
    }
  },
  "spacing": {
    "base": "16px"
  },
  "typography": {
    "fontSize": {
      "base": "14px"
    },
    "fontFamily": {
      "base": "'Roboto', sans-serif"
    }
  },
  "shadows": {
    "default": "0 2px 4px rgba(0,0,0,0.1)"
  }
}
```

**Tailwind CSS Config**:

```typescript
// tailwind.config.ts
import tokens from './tokens.json';

export default {
  theme: {
    extend: {
      colors: {
        primary: tokens.colors.brand.primary,
        secondary: tokens.colors.brand.secondary,
      },
      borderRadius: {
        DEFAULT: tokens.borders.radius.default,
      },
      spacing: {
        base: tokens.spacing.base,
      },
      fontSize: {
        base: tokens.typography.fontSize.base,
      },
      fontFamily: {
        sans: [tokens.typography.fontFamily.base],
      },
      boxShadow: {
        DEFAULT: tokens.shadows.default,
      },
    },
  },
};
```

### Inline Style Extraction

**Before**:

```tsx
<div style={{
  backgroundColor: '#875A7B',
  padding: '16px',
  borderRadius: '8px'
}}>
```

**After**:

```tsx
<div className="bg-primary p-base rounded">
```

## Component Patterns

### Odoo Widget → React Component

**Odoo Many2One Widget**:

```xml
<field name="employee_id" widget="many2one"/>
```

**React Component**:

```tsx
import { Combobox } from '@/components/ui/combobox';

interface Many2OneProps {
  value: { id: number; name: string } | null;
  options: Array<{ id: number; name: string }>;
  onChange: (value: { id: number; name: string } | null) => void;
  label?: string;
}

export function Many2One({ value, options, onChange, label }: Many2OneProps) {
  return (
    <Combobox
      value={value}
      options={options}
      onChange={onChange}
      placeholder={label || 'Select an option'}
      searchable
    />
  );
}
```

### Odoo List View → React Table

**Odoo List**:

```xml
<tree string="Employees">
  <field name="name"/>
  <field name="job_title"/>
  <field name="department_id"/>
</tree>
```

**React Table**:

```tsx
import { DataTable } from '@/components/ui/data-table';
import { ColumnDef } from '@tanstack/react-table';

interface Employee {
  id: number;
  name: string;
  job_title: string;
  department_id: { id: number; name: string };
}

const columns: ColumnDef<Employee>[] = [
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'job_title',
    header: 'Job Title',
  },
  {
    accessorKey: 'department_id.name',
    header: 'Department',
  },
];

export function EmployeeTable({ data }: { data: Employee[] }) {
  return <DataTable columns={columns} data={data} />;
}
```

## State Management Migration

### Odoo RPC → React Query

**Odoo RPC Call**:

```javascript
rpc
  .query({
    model: 'hr.employee',
    method: 'search_read',
    args: [[['active', '=', true]]],
    kwargs: {
      fields: ['name', 'job_title'],
      limit: 50,
    },
  })
  .then((employees) => {
    // Handle data
  });
```

**React Query**:

```tsx
import { useQuery } from '@tanstack/react-query';

function useEmployees() {
  return useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const response = await fetch('/api/employees?active=true&limit=50');
      return response.json();
    },
  });
}

export function EmployeeList() {
  const { data: employees, isLoading, error } = useEmployees();

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {employees.map((emp) => (
        <EmployeeCard key={emp.id} employee={emp} />
      ))}
    </div>
  );
}
```

## Asset Handling

### Static Asset Migration

**Odoo Asset Path**:

```
/web/static/src/img/logo.svg
/hr/static/src/img/employee-placeholder.png
/web_enterprise/static/src/scss/primary_variables.scss
```

**Next.js Public Path**:

```
/public/assets/logo.svg
/public/assets/employee-placeholder.png
/styles/tokens/variables.css
```

**Asset Map Output**:

```json
{
  "images": {
    "/web/static/src/img/logo.svg": "/public/assets/logo.svg",
    "/hr/static/src/img/employee-placeholder.png": "/public/assets/employee-placeholder.png"
  },
  "styles": {
    "/web_enterprise/static/src/scss/primary_variables.scss": "/styles/tokens/variables.css"
  },
  "fonts": {
    "/web/static/src/fonts/lato.woff2": "/public/fonts/lato.woff2"
  }
}
```

## Conversion Algorithm

### Step 1: Parse QWeb Template

```typescript
function parseQWeb(template: string): QWebAST {
  const parser = new DOMParser();
  const doc = parser.parseFromString(template, 'text/xml');
  return traverseQWebNodes(doc.documentElement);
}
```

### Step 2: Extract Design Tokens

```typescript
function extractTokens(scssFiles: string[]): DesignTokens {
  const tokens: DesignTokens = {
    colors: {},
    spacing: {},
    typography: {},
    borders: {},
    shadows: {},
  };

  for (const file of scssFiles) {
    const content = readFile(file);
    const variables = parseSCSSVariables(content);

    for (const [name, value] of Object.entries(variables)) {
      const category = categorizeToken(name);
      tokens[category][name] = value;
    }
  }

  return tokens;
}
```

### Step 3: Generate React Components

```typescript
function generateTSX(ast: QWebAST, tokens: DesignTokens): TSXOutput {
  const component = {
    imports: generateImports(ast),
    interface: generateInterface(ast),
    component: generateComponentBody(ast, tokens),
  };

  return {
    code: renderComponent(component),
    tokens_url: uploadTokens(tokens),
  };
}
```

### Step 4: Apply Visual Hints (if SSIM < 0.98)

```typescript
function applyVisualHints(ast: QWebAST, hints: string[]): QWebAST {
  // Example hint: "Increase border-radius on primary buttons"
  for (const hint of hints) {
    if (hint.includes('border-radius') && hint.includes('button')) {
      ast = adjustButtonRadius(ast, extractValue(hint));
    }
    if (hint.includes('padding') && hint.includes('sidebar')) {
      ast = adjustSidebarPadding(ast, extractValue(hint));
    }
    // ... more hint patterns
  }
  return ast;
}
```

## Quality Validation

### Component Linting

```typescript
// Generated component must pass:
// 1. TypeScript type checking
// 2. ESLint rules
// 3. Prettier formatting
// 4. React best practices (hooks, keys, etc.)

const validation = {
  typescript: tsc --noEmit,
  eslint: eslint 'src/**/*.{ts,tsx}',
  prettier: prettier --check 'src/**/*.{ts,tsx}',
  react: 'eslint-plugin-react-hooks',
};
```

### Visual Regression Testing

```typescript
// Compare rendered output pixel-by-pixel
const ssim = await compareImages(
  baseline_screenshot, // Odoo QWeb rendered
  candidate_screenshot // React component rendered
);

if (ssim < 0.98) {
  const hints = generateVisualHints(diff_image);
  // Retry conversion with hints
}
```

## Function Signature

```typescript
async function qweb_to_tsx(
  archive_url: string,
  theme_hint?: string
): Promise<{
  tokens_url: string;
  pieces: Array<{
    component_name: string;
    tsx_code: string;
    interface_code: string;
    style_imports: string[];
  }>;
}> {
  // 1. Download and extract archive
  const archive = await downloadArchive(archive_url);
  const templates = extractQWebTemplates(archive);
  const scssFiles = extractSCSSFiles(archive, theme_hint);

  // 2. Extract design tokens
  const tokens = extractTokens(scssFiles);

  // 3. Convert each template
  const pieces = templates.map((template) => {
    const ast = parseQWeb(template);
    const tsx = generateTSX(ast, tokens);
    return tsx;
  });

  // 4. Upload tokens and return
  const tokens_url = await uploadTokens(tokens);

  return { tokens_url, pieces };
}
```

## Error Handling

### Missing Template Dependencies

```typescript
if (missingTemplates.length > 0) {
  throw new Error(`Missing QWeb templates: ${missingTemplates.join(', ')}`);
}
```

### Unsupported QWeb Directives

```typescript
const unsupportedDirectives = ['t-js', 't-debug', 't-log'];
for (const directive of unsupportedDirectives) {
  if (template.includes(directive)) {
    console.warn(`Unsupported directive: ${directive} - manual conversion needed`);
  }
}
```

### SCSS Parsing Failures

```typescript
try {
  const tokens = parseSCSSVariables(file);
} catch (error) {
  console.warn(`Failed to parse ${file}: ${error.message}`);
  // Continue with default tokens
}
```

## Output Example

```typescript
{
  "tokens_url": "https://storage.example.com/tokens/abc123.json",
  "pieces": [
    {
      "component_name": "EmployeeCard",
      "tsx_code": "export function EmployeeCard({ employee }: { employee: Employee }) { ... }",
      "interface_code": "interface Employee { id: number; name: string; ... }",
      "style_imports": ["@/styles/tokens/colors", "@/styles/tokens/spacing"]
    },
    {
      "component_name": "EmployeeTable",
      "tsx_code": "export function EmployeeTable({ employees }: { employees: Employee[] }) { ... }",
      "interface_code": "interface Employee { ... }",
      "style_imports": ["@/styles/tokens/typography"]
    }
  ]
}
```

## Best Practices

### ✅ DO

- Extract all SCSS variables to design tokens
- Use semantic token names (primary, secondary, not color1, color2)
- Preserve component hierarchy from QWeb
- Generate TypeScript interfaces for props
- Use Tailwind utility classes mapped to tokens
- Test each component independently

### ❌ DON'T

- Hardcode colors, spacing, or other design values
- Use `dangerouslySetInnerHTML` without sanitization
- Skip TypeScript interfaces (no `any` types)
- Flatten component structure unnecessarily
- Ignore QWeb directives (convert all)
- Mix inline styles with Tailwind classes

## Common Patterns

### Form Field Conversion

**QWeb**:

```xml
<field name="name" required="1" placeholder="Enter name"/>
```

**React**:

```tsx
<Input
  name="name"
  required
  placeholder="Enter name"
  value={formData.name}
  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
/>
```

### Conditional Classes

**QWeb**:

```xml
<div t-att-class="'card ' + ('active' if record.active else 'inactive')">
```

**React**:

```tsx
<div className={`card ${record.active ? 'active' : 'inactive'}`}>
```

### Dynamic Attributes

**QWeb**:

```xml
<a t-attf-href="/employee/{{employee.id}}" t-att-title="employee.name">
```

**React**:

```tsx
<a href={`/employee/${employee.id}`} title={employee.name}>
```

## Success Criteria

- [ ] All QWeb directives converted to React equivalents
- [ ] All SCSS variables extracted to tokens.json
- [ ] Tailwind config generated from tokens
- [ ] TypeScript interfaces for all component props
- [ ] No hardcoded design values in JSX
- [ ] Component renders without errors
- [ ] Passes TypeScript type checking
- [ ] Passes ESLint/Prettier validation
- [ ] Visual parity: SSIM ≥ 0.98

## References

- [QWeb Template Engine](https://www.odoo.com/documentation/18.0/developer/reference/frontend/qweb.html)
- [React Documentation](https://react.dev)
- [Design Tokens Specification](https://design-tokens.github.io)
- [Tailwind CSS Configuration](https://tailwindcss.com/docs/configuration)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
