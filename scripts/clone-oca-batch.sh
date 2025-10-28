#!/usr/bin/env bash
cd insightpulse_odoo/addons/oca
for repo in stock-logistics-workflow project helpdesk manufacture web server-tools reporting-engine contract hr crm fieldservice quality-control maintenance dms queue timesheet website; do
  if [[ ! -d "$repo" ]]; then
    echo "=== Cloning $repo ==="
    git clone --depth 1 https://github.com/OCA/$repo.git -b 19.0 2>&1 | head -3
  else
    echo "=== Skipping $repo (already exists) ==="
  fi
done
echo "Done!"
