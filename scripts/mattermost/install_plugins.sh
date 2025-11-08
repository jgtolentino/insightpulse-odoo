#!/usr/bin/env bash
set -euo pipefail

: "${MM_BASE_URL:?set MM_BASE_URL (e.g., https://chat.insightpulseai.net)}"
: "${MM_ADMIN_TOKEN:?set MM_ADMIN_TOKEN (Mattermost admin PAT)}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PLUGINS_YAML="${ROOT}/third_party/mattermost/plugins.yaml"

need() { command -v "$1" >/dev/null 2>&1 || { echo "missing: $1"; exit 1; }; }
need jq
need python3
need curl

# Read YAML to JSON via Python (no PyYAML dependency)
plugins_json="$(python3 - <<'PY' "$PLUGINS_YAML"
import sys, json, re
# super lightweight yaml parser for simple key: value lists
data = {"plugins":[]}
cur = None
for line in open(sys.argv[1], encoding="utf-8"):
    s=line.strip()
    if not s or s.startswith("#"): continue
    if s.startswith("plugins:"):
        continue
    if s.startswith("- "):
        if cur: data["plugins"].append(cur)
        cur={}
        s=s[2:].strip()
        if s:
            k,v=s.split(":",1); cur[k.strip()]=v.strip().strip('"').strip("'")
        continue
    if ":" in s and cur is not None:
        k,v=s.split(":",1)
        cur[k.strip()]=v.strip().strip('"').strip("'")
if cur: data["plugins"].append(cur)
print(json.dumps(data))
PY
)"

api() {
  local method="$1"; shift
  local path="$1"; shift
  curl -fsSL -X "$method" \
    -H "Authorization: Bearer ${MM_ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    "${MM_BASE_URL}${path}" "$@"
}

echo "== Marketplace availability =="
api GET "/api/v4/plugins/marketplace?filter=&server_version=" >/dev/null || {
  echo "Marketplace endpoint not reachable. Enable Marketplace in System Console."
  exit 1
}

echo "== Installing/enabling plugins =="
count=$(echo "$plugins_json" | jq '.plugins | length')
for i in $(seq 0 $((count-1))); do
  id=$(echo "$plugins_json" | jq -r ".plugins[$i].id")
  ver=$(echo "$plugins_json" | jq -r ".plugins[$i].version")
  ena=$(echo "$plugins_json" | jq -r ".plugins[$i].enabled")
  echo "-> $id@$ver (enabled=$ena)"
  # Install from marketplace (requires id + version)
  api POST "/api/v4/plugins/marketplace" \
    --data "{\"id\":\"${id}\",\"version\":\"${ver}\"}" >/dev/null || true
  # Enable if requested
  if [ "$ena" = "true" ]; then
    api POST "/api/v4/plugins/${id}/enable" >/dev/null || true
  fi
done

echo "== Installed plugins =="
api GET "/api/v4/plugins" | jq '{active: .active | map(.id), inactive: .inactive | map(.id)}'
echo "done."
