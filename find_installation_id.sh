#!/bin/bash
# Find GitHub App Installation ID
# Usage: ./find_installation_id.sh /path/to/private-key.pem

PRIVATE_KEY_FILE="${1:-private-key.pem}"

if [ ! -f "$PRIVATE_KEY_FILE" ]; then
    echo "❌ Private key file not found: $PRIVATE_KEY_FILE"
    echo "Usage: $0 /path/to/private-key.pem"
    exit 1
fi

# Generate JWT token
JWT=$(python3 -c "
import jwt
import time

with open('$PRIVATE_KEY_FILE', 'r') as f:
    private_key = f.read()

payload = {
    'iat': int(time.time()),
    'exp': int(time.time()) + 600,
    'iss': 2191216
}

print(jwt.encode(payload, private_key, algorithm='RS256'))
")

echo "🔍 Fetching installations for App ID: 2191216"
echo ""

# Get installations
curl -s -H "Authorization: Bearer $JWT" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/app/installations | jq -r '.[] | "ID: \(.id) | Account: \(.account.login) | Type: \(.account.type)"'

echo ""
echo "Copy the ID number and use it as GITHUB_INSTALLATION_ID"
