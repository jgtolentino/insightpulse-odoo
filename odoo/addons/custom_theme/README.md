# InsightPulseAI Custom Theme

## Overview

This module provides unified branding and theming for the InsightPulse Odoo 18 ERP instance. It applies consistent design tokens, colors, and visual identity across both backend and frontend interfaces.

## Features

- **Unified Branding**: Consistent colors and design across all InsightPulse services
- **Custom Color Palette**:
  - Primary Color: `#1455C7` (InsightPulse Blue)
  - Secondary Color: `#111827` (Dark Gray)
  - Accent Color: `#F97316` (Orange)
- **Multi-Service Consistency**: Matches branding with:
  - Odoo ERP
  - Mattermost Chat
  - Apache Superset
  - n8n Automation
- **Backend & Frontend**: Applies to both Odoo backend and portal frontend

## Installation

1. Ensure dependencies are installed: `web`, `portal`
2. Update the module list
3. Install "InsightPulseAI Custom Theme" from the Apps menu

## Configuration

Theme configuration is managed through:

- **Branding Specification**: `config/branding_theme.json`
- **Desired State**: `config/odoo18_desired_state.json`

The theme automatically applies when the module is installed.

## Technical Details

### Module Structure

```
custom_theme/
├── __init__.py
├── __manifest__.py
├── static/
│   └── src/
│       └── css/
│           └── odoo_custom_theme.css
└── views/
    └── templates.xml
```

### Assets

CSS assets are loaded in both backend and frontend contexts:

- `web.assets_backend`: Backend theme styling
- `web.assets_frontend`: Portal and website theme styling

## Version

- **Version**: 18.0.1.0.0
- **Odoo Version**: 18.0 Community Edition
- **License**: LGPL-3

## Author

**InsightPulseAI**

Website: https://insightpulseai.net

## Support

For issues or questions, contact:
- Email: support@insightpulseai.com
- GitHub: https://github.com/jgtolentino/insightpulse-odoo

## License

LGPL-3 - See LICENSE file for details
