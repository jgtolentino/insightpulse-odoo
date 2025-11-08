# InsightPulse Apps Routing

## Overview

This module customizes the Odoo 19 Community Edition Apps interface to route app installations to a local catalog instead of the Odoo.com store. It removes enterprise upsell UI elements and ensures a clean, self-hosted experience.

## Features

- **Local App Catalog**: Routes app browsing and installation to local/custom catalog
- **Hide Upsell UI**: Removes enterprise edition promotional elements
- **Clean Interface**: Provides distraction-free app management
- **Self-Hosted First**: Optimized for fully self-hosted deployments

## Installation

1. Ensure dependencies are installed: `base`, `web`
2. Update the module list
3. Install "InsightPulse Apps Routing" from the Apps menu

The module applies automatically upon installation.

## Configuration

The module sets system parameters via `data/ir_config_parameter.xml` to:

- Redirect Apps menu to local catalog
- Disable Odoo.com store integration
- Hide enterprise upgrade prompts

## Use Cases

This module is ideal for:

- **Self-Hosted Deployments**: Organizations using fully self-hosted Odoo instances
- **Enterprise Alternatives**: Companies using OCA modules instead of Enterprise licenses
- **Clean UI**: Teams wanting focused app management without external store distractions

## Technical Details

### Module Structure

```
ip_apps_routing/
├── __init__.py
├── __manifest__.py
├── data/
│   └── ir_config_parameter.xml
├── models/
│   └── (routing logic)
├── static/
│   └── src/
│       └── (UI customizations)
└── views/
    └── web_assets.xml
```

### Configuration Parameters

The module modifies these system parameters:

- App store URL routing
- Enterprise feature flags
- UI element visibility

## Compatibility

- **Version**: 19.0.1.0.0
- **Odoo Version**: 19.0 Community Edition
- **License**: LGPL-3

## Benefits

Using this module as part of the InsightPulse AI stack saves **$4,728/year** by leveraging OCA community modules instead of Enterprise licenses while maintaining professional functionality.

## Author

**InsightPulse AI**

Website: https://insightpulseai.net

## Support

For issues or questions, contact:
- Email: support@insightpulseai.com
- GitHub: https://github.com/jgtolentino/insightpulse-odoo

## Related Modules

This module works alongside:
- `custom_theme`: Unified branding across InsightPulse services
- OCA community modules: Enterprise-grade features without licensing costs

## License

LGPL-3 - See LICENSE file for details
