#!/bin/bash
# Generate remaining IPAI Slack modules
# This script creates all module scaffolds

cd /home/user/insightpulse-odoo/odoo_addons

# Module definitions
declare -A MODULES=(
    ["ipai_slack_bridge"]="Slack Bridge|Bidirectional Slack integration - OAuth, Events API, sync"
    ["ipai_scim_provisioner"]="SCIM Provisioner|SCIM 2.0 user lifecycle management"
    ["ipai_audit_discovery"]="Audit & eDiscovery|Immutable audit, legal hold, eDiscovery export"
    ["ipai_retention_policies"]="Retention Policies|Per-channel retention, auto-purge, exceptions"
    ["ipai_dlp_guard"]="DLP Guard|Data Loss Prevention - pattern detection, quarantine"
    ["ipai_huddles_webrtc"]="Huddles WebRTC|Jitsi integration for audio/video calls"
    ["ipai_workflow_bot"]="Workflow Bot|Slash commands and workflow automation"
    ["ipai_connect_external"]="External Connect|Guest/partner collaboration spaces"
    ["ipai_search_vector"]="Semantic Search|pgvector-based semantic search"
    ["ipai_files_spaces"]="Files Storage|S3/DO Spaces integration for large files"
)

for module in "${!MODULES[@]}"; do
    IFS='|' read -r name summary <<< "${MODULES[$module]}"

    # Create __init__.py
    cat > "$module/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
from . import models
from . import controllers
EOF

    # Create models/__init__.py
    mkdir -p "$module/models"
    echo "# -*- coding: utf-8 -*-" > "$module/models/__init__.py"

    # Create controllers/__init__.py
    mkdir -p "$module/controllers"
    echo "# -*- coding: utf-8 -*-" > "$module/controllers/__init__.py"

    # Create security/ir.model.access.csv
    mkdir -p "$module/security"
    echo "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink" > "$module/security/ir.model.access.csv"

    # Create README.rst
    cat > "$module/README.rst" << EOF
$name
$(printf '=%.0s' {1..${#name}})

$summary

Installation
------------

Install this module via Odoo Apps or CLI:

.. code-block:: bash

    docker-compose exec odoo /opt/odoo/odoo-bin \\
      -c /etc/odoo/odoo.conf -d odoo19 \\
      -i $module --stop-after-init

Configuration
-------------

See docs/SLACK_ENTERPRISE_MIGRATION.md for full configuration guide.

Bug Tracker
-----------

Bugs are tracked on \`GitHub Issues\`_

.. _GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues

Credits
-------

**Authors:** InsightPulse AI

**Maintainers:** jgtolentino
EOF

    echo "Created scaffold for $module"
done

echo "✅ All module scaffolds created!"
