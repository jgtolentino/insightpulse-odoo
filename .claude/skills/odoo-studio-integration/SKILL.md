---
name: odoo-studio-integration
description: Leverage Odoo Studio for no-code/low-code customization and rapid application development
version: 1.0.0
tags: [odoo, studio, nocode, lowcode, customization, rapid-development]
requires:
  files:
    - superclaude/knowledge/STYLE_GUIDE.md
    - superclaude/knowledge/PM_STANDARDS.md
---

# Odoo Studio Integration Skill

## Purpose

Utilize Odoo Studio's powerful no-code/low-code platform for rapid application customization, business process automation, and user interface enhancements without traditional development.

## When to use

- Rapid prototyping and MVP development
- Business process automation without coding
- Custom field and view modifications
- Workflow automation and approval processes
- Report and dashboard customization
- Mobile app customization
- Integration with existing OCA modules

## Actions

1. **Studio Analysis**: Analyze business requirements for Studio feasibility
2. **No-Code Implementation**: Design and implement solutions using Studio interface
3. **Custom Field Management**: Create and configure custom fields and relationships
4. **View Customization**: Modify forms, lists, kanban, and calendar views
5. **Automation Design**: Build workflows, actions, and business rules
6. **Report Generation**: Create custom reports and dashboards
7. **Mobile Optimization**: Customize mobile interfaces and workflows

## Inputs

- `business_requirements`: Description of customization needs
- `target_models`: Odoo models to customize
- `automation_level`: Level of automation needed (basic, intermediate, advanced)
- `ui_requirements`: User interface customization specifications
- `integration_needs`: Integration with other modules or systems

## Outputs

- Studio customization specifications
- Step-by-step implementation guides
- Custom field and view configurations
- Workflow automation designs
- Mobile optimization recommendations
- Integration patterns with existing modules

## Examples

### Example 1: Custom CRM Pipeline
```
User: "Create a custom CRM pipeline for real estate leads"

Agent:
1. Analyzes real estate lead management requirements
2. Designs Studio customization:
   - Custom fields: Property Type, Budget Range, Location Preference
   - Pipeline stages: Lead → Qualified → Property Match → Viewing → Offer → Closed
   - Automated actions: Email templates for each stage
   - Kanban view with property images and status
3. Generates Studio implementation guide:
   - Step 1: Enable Studio on CRM module
   - Step 2: Create custom fields in lead model
   - Step 3: Customize pipeline stages and colors
   - Step 4: Configure automated email templates
   - Step 5: Customize kanban view with images
4. Provides testing and validation steps
```

### Example 2: Expense Approval Workflow
```
User: "Build an expense approval workflow with multi-level approval"

Agent:
1. Designs multi-level approval workflow:
   - Employee submits expense → Manager approval → Finance approval → Payment
   - Custom fields: Expense Category, Receipt Upload, Approval Comments
   - Automated notifications at each stage
   - Approval thresholds based on amount
2. Creates Studio implementation:
   - Custom model for expense approvals
   - Automated actions for routing and notifications
   - Custom reports for expense tracking
   - Mobile interface for receipt upload
3. Generates workflow documentation and user training
```

### Example 3: Project Management Dashboard
```
User: "Create a custom project dashboard with KPIs"

Agent:
1. Designs project dashboard with Studio:
   - Custom KPIs: Budget vs Actual, Timeline Progress, Resource Utilization
   - Interactive charts and graphs
   - Custom filters and grouping options
   - Real-time status updates
2. Implements using Studio features:
   - Custom computed fields for KPIs
   - Graph views with custom aggregations
   - Dashboard layout with multiple views
   - Automated data refresh
3. Provides user training and maintenance guide
```

## Odoo Studio Features Integration

### Core Studio Capabilities

#### 1. Custom Fields
- **Field Types**: Text, Integer, Float, Boolean, Selection, Date, DateTime, Binary, Many2one, Many2many, One2many
- **Advanced Options**: Required, Readonly, Default values, Domain filters, Help text
- **Computed Fields**: Python expressions for dynamic values
- **Related Fields**: Link fields across models

#### 2. View Customization
- **Form Views**: Add sections, groups, tabs, buttons, smart buttons
- **List Views**: Add columns, filters, group by options, default sort
- **Kanban Views**: Custom cards, colors, progress bars, images
- **Calendar Views**: Event customization, color coding, date ranges
- **Graph Views**: Chart types, dimensions, measures, filters
- **Pivot Views**: Row/column grouping, measures, filters

#### 3. Automation & Actions
- **Server Actions**: Automated workflows and business logic
- **Automated Actions**: Time-based or event-triggered actions
- **Email Templates**: Dynamic email content with field placeholders
- **Button Actions**: Custom buttons with specific behaviors

#### 4. Reports & Dashboards
- **Custom Reports**: QWeb reports with custom layouts
- **Dashboard Views**: Multiple view integration on single screen
- **KPIs & Metrics**: Real-time performance indicators
- **Export Options**: PDF, Excel, CSV formats

### Integration Patterns

#### With OCA Modules
```python
# Example: Integration with OCA HR modules
studio_customizations = {
    'hr_employee': {
        'custom_fields': [
            'skills_matrix': 'many2many to skills model',
            'performance_score': 'computed field from reviews',
            'training_certifications': 'one2many to certifications'
        ],
        'views': [
            'form_view': 'add skills and performance sections',
            'kanban_view': 'show performance indicators'
        ]
    }
}
```

#### With Existing Custom Modules
```python
# Integration with custom modules
integration_points = {
    'data_synchronization': 'Sync Studio custom fields with module data',
    'business_logic': 'Extend module functionality with Studio workflows',
    'ui_enhancement': 'Improve user experience with Studio views',
    'reporting': 'Combine module data with Studio reports'
}
```

## Implementation Guidelines

### Best Practices

#### 1. Field Naming Conventions
- **Prefix**: Use `x_` for custom fields (e.g., `x_custom_field`)
- **Descriptive**: Clear, business-meaningful names
- **Consistent**: Follow Odoo naming conventions
- **Documented**: Include help text and descriptions

#### 2. View Design Principles
- **User-Centric**: Design for end-user workflows
- **Consistent**: Maintain visual consistency across views
- **Performant**: Optimize for loading speed and responsiveness
- **Accessible**: Follow accessibility guidelines

#### 3. Workflow Automation
- **Simple First**: Start with basic automation, then complex
- **Error Handling**: Include validation and error messages
- **Testing**: Test workflows thoroughly before deployment
- **Documentation**: Document automation logic and triggers

### Technical Considerations

#### Performance Optimization
- **Field Indexing**: Index frequently searched fields
- **Computed Fields**: Optimize computation logic
- **View Optimization**: Limit fields and complexity in views
- **Data Volume**: Consider large dataset performance

#### Security & Access Control
- **Field Security**: Restrict sensitive field access
- **Record Rules**: Implement record-level security
- **Group Permissions**: Assign features to appropriate groups
- **Audit Trail**: Track changes and access

## Success Metrics

### Implementation Success
- **Development Time**: 70-90% faster than traditional development
- **User Adoption**: ≥ 80% user satisfaction with customizations
- **Business Value**: Measurable improvement in process efficiency
- **Maintenance**: Reduced maintenance overhead compared to code

### Quality Metrics
- **Performance**: Page load times < 3 seconds
- **Usability**: Intuitive user interface and workflows
- **Reliability**: 99% uptime for automated processes
- **Scalability**: Support for growing data and user volumes

## References

- [Odoo Studio Documentation](https://www.odoo.com/app/studio-features)
- [Odoo Studio Best Practices](https://www.odoo.com/documentation/16.0/applications/studio.html)
- [OCA Integration Patterns](vendor/oca-web/doc/integration.md)
- [Studio API Reference](https://www.odoo.com/documentation/16.0/developer/reference/studio.html)

## Migration & Upgrade Considerations

### Version Compatibility
- **Odoo Version**: Ensure Studio features compatible with target version
- **Module Dependencies**: Check compatibility with OCA modules
- **Custom Code**: Plan for potential conflicts with existing customizations

### Data Migration
- **Field Migration**: Plan for custom field data preservation
- **View Compatibility**: Ensure views work across versions
- **Workflow Continuity**: Maintain business process continuity

### Backup & Recovery
- **Regular Backups**: Schedule Studio customization backups
- **Export Configurations**: Export Studio configurations for recovery
- **Testing**: Test recovery procedures regularly
