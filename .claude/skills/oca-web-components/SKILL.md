---
name: oca-web-components
description: Migrate OCA web components to modern frameworks and extract design patterns
version: 1.0.0
tags: [oca, web, components, javascript, react, migration]
requires:
  files:
    - vendor/oca-web/README.md
    - vendor/oca-web/static/
    - vendor/oca-web/doc/
---

# OCA Web Components Skill

## Purpose

Migrate OCA JavaScript widgets and web components to modern React/TypeScript frameworks while preserving OCA design patterns and functionality.

## When to use

- Migrating OCA web widgets to modern JavaScript frameworks
- Extracting reusable design patterns from OCA web components
- Converting JavaScript widgets to TypeScript React components
- Modernizing OCA UI components while maintaining compatibility

## Actions

1. **Component Analysis**: Analyze OCA JavaScript widgets and identify patterns
2. **Migration Planning**: Create migration strategy from Odoo widgets to React
3. **Pattern Extraction**: Extract reusable design patterns and business logic
4. **Modern Implementation**: Convert to TypeScript React components with proper typing
5. **Compatibility Testing**: Ensure migrated components work with OCA ecosystem

## Inputs

- `source_component`: Path to OCA JavaScript widget or component
- `target_framework`: Target framework (react, vue, angular, svelte)
- `preserve_patterns`: Boolean to preserve OCA design patterns
- `migration_scope`: Scope of migration (single component, module, entire app)
- `integration_testing`: Boolean to generate integration tests

## Outputs

- Migrated React/TypeScript components
- Design pattern documentation
- Migration compatibility report
- Integration test suites
- Performance comparison metrics

## Examples

### Example 1: Widget Migration
```
User: "Migrate OCA dashboard widgets to React"

Agent:
1. Analyzes OCA/web dashboard JavaScript widgets
2. Identifies widget patterns and business logic
3. Converts to TypeScript React components:
   - Preserves OCA design patterns
   - Adds proper TypeScript interfaces
   - Maintains widget functionality
   - Improves performance and maintainability
4. Generates integration tests
5. Provides migration compatibility report
```

### Example 2: Pattern Extraction
```
User: "Extract form patterns from OCA web components"

Agent:
1. Analyzes OCA form widgets and validation patterns
2. Extracts reusable form patterns:
   - Form validation logic
   - Field rendering patterns
   - Error handling approaches
   - Data binding mechanisms
3. Creates React form component library
4. Documents pattern usage and best practices
```

### Example 3: Performance Optimization
```
User: "Optimize OCA chart components for modern browsers"

Agent:
1. Analyzes OCA chart rendering performance
2. Identifies bottlenecks and optimization opportunities
3. Migrates to modern chart libraries (Chart.js, Recharts)
4. Implements virtualization for large datasets
5. Provides performance comparison metrics
```

## Implementation Details

### Component Migration Process

```typescript
interface MigrationProcess {
  analysis: {
    source_component: string;
    dependencies: string[];
    business_logic: string[];
    ui_patterns: string[];
  };
  planning: {
    target_architecture: string;
    migration_strategy: string;
    compatibility_checks: string[];
  };
  implementation: {
    component_code: string;
    type_definitions: string;
    tests: string;
    documentation: string;
  };
  validation: {
    functionality_checks: string[];
    performance_metrics: string[];
    integration_tests: string[];
  };
}
```

### OCA Widget Patterns

**Common OCA Widget Types:**
- Form widgets (input, select, checkbox, radio)
- List views and data grids
- Chart and visualization widgets
- Dashboard components
- Navigation and menu widgets
- Search and filter components

**Migration Strategies:**
- Direct conversion for simple widgets
- Pattern extraction for complex components
- Framework-specific optimizations
- Progressive enhancement approaches

### TypeScript Integration

```typescript
// Example: OCA Form Widget to React Component
interface OCAFormWidgetProps {
  fieldName: string;
  fieldType: 'char' | 'integer' | 'float' | 'selection' | 'many2one';
  required?: boolean;
  readonly?: boolean;
  defaultValue?: any;
  onValueChange: (value: any) => void;
}

const OCAFormField: React.FC<OCAFormWidgetProps> = ({
  fieldName,
  fieldType,
  required = false,
  readonly = false,
  defaultValue,
  onValueChange
}) => {
  // Migrated OCA form field logic
  // Preserves OCA validation patterns
  // Adds React state management
  // Maintains Odoo field compatibility
};
```

### Performance Considerations

**Optimization Areas:**
- Bundle size reduction
- Rendering performance
- Memory usage optimization
- Lazy loading implementation
- Caching strategies

**Metrics Tracking:**
- Initial load time
- Interaction responsiveness
- Memory footprint
- Bundle size impact
- Browser compatibility

## Success Metrics

- **Migration Accuracy**: 100% functionality preservation
- **Performance Improvement**: ≥ 30% faster rendering
- **Bundle Size**: ≤ 50% increase from original
- **Type Safety**: 100% TypeScript coverage
- **Test Coverage**: ≥ 80% for migrated components

## References

- [OCA Web Repository](vendor/oca-web/)
- [OCA JavaScript Patterns](vendor/oca-web/doc/javascript.md)
- [OCA Widget Documentation](vendor/oca-web/doc/widgets.md)
- [Modern JavaScript Migration Guide](vendor/oca-web/doc/migration.md)
