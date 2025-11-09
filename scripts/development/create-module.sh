#!/bin/bash
# scripts/development/create-module.sh
# Script to create new Odoo custom modules following OCA guidelines

set -e

MODULE_NAME=$1
MODULE_PATH="odoo/modules/$MODULE_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if module name is provided
if [ -z "$MODULE_NAME" ]; then
    echo -e "${RED}❌ Error: Module name required${NC}"
    echo "Usage: ./create-module.sh my_module_name"
    exit 1
fi

# Check if module already exists
if [ -d "$MODULE_PATH" ]; then
    echo -e "${RED}❌ Error: Module $MODULE_NAME already exists${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Creating module: $MODULE_NAME${NC}"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$MODULE_PATH"/{models,views,security,data,static/description,static/src/js,tests,controllers}

# Create __init__.py files
echo "📝 Creating __init__.py files..."
cat > "$MODULE_PATH/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-

from . import models
from . import controllers
EOF

cat > "$MODULE_PATH/models/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-

# from . import your_model
EOF

cat > "$MODULE_PATH/controllers/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-

# from . import main
EOF

cat > "$MODULE_PATH/tests/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-

# from . import test_your_model
EOF

# Create __manifest__.py
echo "📝 Creating __manifest__.py..."
MODULE_TITLE=$(echo "$MODULE_NAME" | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g')
cat > "$MODULE_PATH/__manifest__.py" << EOF
# -*- coding: utf-8 -*-
{
    'name': '$MODULE_TITLE',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Module description',
    'description': """
        $MODULE_TITLE
        ==============
        
        Long description of the module goes here.
        
        Features:
        ---------
        * Feature 1
        * Feature 2
        * Feature 3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
EOF

# Create security/ir.model.access.csv
echo "🔒 Creating security rules..."
cat > "$MODULE_PATH/security/ir.model.access.csv" << EOF
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
EOF

# Create views/menu.xml
echo "👁️  Creating views..."
cat > "$MODULE_PATH/views/menu.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Your views and menu items here -->
    
    <!-- Example:
    <menuitem
        id="menu_${MODULE_NAME}_root"
        name="$MODULE_TITLE"
        sequence="10"/>
    -->
</odoo>
EOF

# Create README.md
echo "📚 Creating README.md..."
cat > "$MODULE_PATH/README.md" << EOF
# $MODULE_TITLE

## Description

[Brief description of what this module does]

## Features

* Feature 1: Description
* Feature 2: Description
* Feature 3: Description

## Installation

1. Install module dependencies (if any)
2. Update module list in Odoo
3. Install \`$MODULE_NAME\`

\`\`\`bash
# Via Odoo shell
make shell
>>> self.env['ir.module.module'].search([('name','=','$MODULE_NAME')]).button_immediate_install()
\`\`\`

## Configuration

1. Go to [Menu Location]
2. Configure [Setting]
3. Set up [Feature]

## Usage

### [Use Case 1]

1. Step 1
2. Step 2
3. Step 3

### [Use Case 2]

1. Step 1
2. Step 2
3. Step 3

## Technical Details

### Models

* \`model.name\` - Description

### Views

* Tree view: List of records
* Form view: Detail view
* Search view: Filters and groupings

### Business Logic

[Explanation of key business logic]

## Testing

\`\`\`bash
# Run module tests
python -m pytest odoo/modules/$MODULE_NAME/tests/ -v
\`\`\`

## Known Issues

* Issue 1 (if any)
* Issue 2 (if any)

## Roadmap

* Planned feature 1
* Planned feature 2

## Credits

**Author**: [Your Name]
**Maintainer**: InsightPulse AI
**License**: LGPL-3.0

## Support

* GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
* Email: support@insightpulseai.net
EOF

# Create static/description/index.html
echo "🎨 Creating module description..."
cat > "$MODULE_PATH/static/description/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>$MODULE_TITLE</title>
</head>
<body>
    <section class="oe_container">
        <div class="oe_row oe_spaced">
            <h2 class="oe_slogan">$MODULE_TITLE</h2>
            <h3 class="oe_slogan">Brief module description</h3>
        </div>
    </section>

    <section class="oe_container oe_dark">
        <div class="oe_row oe_spaced">
            <h2>Features</h2>
            <ul>
                <li>Feature 1</li>
                <li>Feature 2</li>
                <li>Feature 3</li>
            </ul>
        </div>
    </section>
</body>
</html>
EOF

# Create a sample model (commented out)
echo "📦 Creating sample model template..."
cat > "$MODULE_PATH/models/sample.py.template" << EOF
# -*- coding: utf-8 -*-
# Uncomment and rename this file to use

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SampleModel(models.Model):
    """Sample model description."""
    
    _name = '$MODULE_NAME.sample'
    _description = 'Sample Model'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Sample field'
    )
    
    description = fields.Text(
        string='Description'
    )
    
    active = fields.Boolean(
        default=True,
        string='Active'
    )
    
    @api.constrains('name')
    def _check_name(self):
        """Validate name field."""
        for record in self:
            if not record.name:
                raise ValidationError("Name cannot be empty")
EOF

# Create a sample test (commented out)
echo "🧪 Creating sample test template..."
cat > "$MODULE_PATH/tests/test_sample.py.template" << EOF
# -*- coding: utf-8 -*-
# Uncomment and rename this file to use

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestSampleModel(TransactionCase):
    """Test sample model."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.SampleModel = self.env['$MODULE_NAME.sample']

    def test_create_sample(self):
        """Test sample creation."""
        sample = self.SampleModel.create({
            'name': 'Test Sample',
            'description': 'Test Description',
        })
        
        self.assertEqual(sample.name, 'Test Sample')
        self.assertEqual(sample.description, 'Test Description')
        self.assertTrue(sample.active)

    def test_name_constraint(self):
        """Test name validation."""
        with self.assertRaises(ValidationError):
            self.SampleModel.create({
                'name': '',
            })
EOF

echo ""
echo -e "${GREEN}✅ Module $MODULE_NAME created successfully!${NC}"
echo ""
echo -e "${YELLOW}📁 Location: $MODULE_PATH/${NC}"
echo ""
echo "Next steps:"
echo "1. Edit $MODULE_PATH/__manifest__.py to update module metadata"
echo "2. Create your models in $MODULE_PATH/models/"
echo "3. Add views in $MODULE_PATH/views/"
echo "4. Update security rules in $MODULE_PATH/security/ir.model.access.csv"
echo "5. Write tests in $MODULE_PATH/tests/"
echo ""
echo "To install the module:"
echo "  make shell"
echo "  >>> self.env['ir.module.module'].search([('name','=','$MODULE_NAME')]).button_immediate_install()"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
