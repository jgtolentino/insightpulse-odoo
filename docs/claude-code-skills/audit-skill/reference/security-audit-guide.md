# Security Audit Reference Guide

Comprehensive guide for conducting security audits on Odoo installations, focusing on common vulnerabilities and their remediation.

## Table of Contents

1. [Credential Management](#credential-management)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Protection](#data-protection)
4. [API Security](#api-security)
5. [Configuration Security](#configuration-security)
6. [Dependency Security](#dependency-security)

## Credential Management

### Hardcoded Secrets Detection

**Search Patterns**:
```bash
# Find hardcoded passwords
grep -rn "password\s*=\s*['\"][^'\"]*['\"]" . --include="*.py" --include="*.conf" --include="*.yaml"

# Find API keys
grep -rn "api[_-]key\s*=\s*['\"]" . --include="*.py" --include="*.env"

# Find tokens
grep -rn "token\s*=\s*['\"][a-zA-Z0-9]" . --include="*.py"

# Find database credentials
grep -rn "db_password\|db_passwd\|database_password" . --include="*.conf" --include="*.py"

# Find AWS/Cloud credentials
grep -rn "aws_access_key\|aws_secret\|ACCESS_KEY" . --include="*.py" --include="*.yaml"

# Find Base64 encoded secrets
grep -rn "[A-Za-z0-9+/]{40,}={0,2}" . --include="*.py" | grep -i "key\|secret\|password"
```

### Environment Variable Migration

**Before (Insecure)**:
```python
# config/odoo.conf
admin_passwd = admin123
db_password = mysecretpassword

# models/config.py
OPENAI_API_KEY = "sk-1234567890abcdef"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**After (Secure)**:
```python
# config/odoo.conf
admin_passwd = %(ODOO_ADMIN_PASSWORD)s
db_password = %(ODOO_DB_PASSWORD)s

# models/config.py
import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
```

**Docker Compose Secrets**:
```yaml
# docker-compose.yml
services:
  odoo:
    environment:
      - ODOO_ADMIN_PASSWORD=${ODOO_ADMIN_PASSWORD}
      - ODOO_DB_PASSWORD=${ODOO_DB_PASSWORD}
    secrets:
      - openai_api_key
      - supabase_key

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  supabase_key:
    file: ./secrets/supabase_key.txt
```

### Secret Rotation Strategy

**Rotation Schedule**:
- **Critical secrets** (admin passwords, root keys): Every 30 days
- **Service tokens** (API keys): Every 90 days
- **Development secrets**: After any suspected exposure
- **Production secrets**: Immediate rotation after exposure

**Rotation Process**:
```bash
#!/bin/bash
# rotate-secrets.sh

# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Update in secret manager
aws secretsmanager update-secret \
    --secret-id odoo/admin-password \
    --secret-string "$NEW_SECRET"

# 3. Update application
docker exec odoo odoo-bin shell -c "
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.users'].browse(SUPERUSER_ID).write({'password': '$NEW_SECRET'})
    env.cr.commit()
"

# 4. Verify new secret works
curl -u admin:$NEW_SECRET http://localhost:8069/web/database/list

# 5. Revoke old secret (after verification)
echo "Old secret revoked on $(date)" >> secret-rotation.log
```

## Authentication & Authorization

### Access Control Validation

**Check Missing Security Rules**:
```python
# scripts/check-access-rules.py
import odoorpc

odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('odoo_db', 'admin', 'password')

models_without_access = []

for model in odoo.env['ir.model'].search([]):
    model_data = odoo.env['ir.model'].browse(model)
    
    # Check if model has access rules
    access_count = odoo.env['ir.model.access'].search_count([
        ('model_id', '=', model)
    ])
    
    if access_count == 0 and not model_data.transient:
        models_without_access.append(model_data.model)
        print(f"⚠️  Model {model_data.model} has no access rules")

print(f"\n📊 Summary: {len(models_without_access)} models without access rules")
```

**Verify Record Rules (RLS)**:
```python
# Check for models with sensitive data but no record rules
sensitive_patterns = ['partner', 'user', 'employee', 'salary', 'payment', 'invoice']

for pattern in sensitive_patterns:
    models = odoo.env['ir.model'].search([('model', 'like', pattern)])
    
    for model_id in models:
        model = odoo.env['ir.model'].browse(model_id)
        rule_count = odoo.env['ir.rule'].search_count([
            ('model_id', '=', model_id)
        ])
        
        if rule_count == 0:
            print(f"⚠️  Sensitive model {model.model} has no record rules (RLS)")
```

### Authentication Hardening

**Multi-Factor Authentication (MFA)**:
```python
# addons/custom/auth_mfa/models/res_users.py
from odoo import models, fields, api
import pyotp
import qrcode
import io
import base64

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    mfa_enabled = fields.Boolean(string='MFA Enabled', default=False)
    mfa_secret = fields.Char(string='MFA Secret', copy=False)
    
    def generate_mfa_secret(self):
        """Generate TOTP secret for MFA"""
        self.mfa_secret = pyotp.random_base32()
        return self.mfa_secret
    
    def verify_mfa_token(self, token):
        """Verify MFA token"""
        if not self.mfa_enabled or not self.mfa_secret:
            return True
        
        totp = pyotp.TOTP(self.mfa_secret)
        return totp.verify(token, valid_window=1)
```

**Session Security**:
```python
# Configure secure sessions
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_EXPIRE_SECONDS = 3600  # 1 hour

# Implement session timeout
class ResUsers(models.Model):
    _inherit = 'res.users'
    
    last_activity = fields.Datetime(string='Last Activity')
    
    @api.model
    def check_session_validity(self):
        """Check if session is still valid based on activity"""
        timeout = datetime.now() - timedelta(hours=1)
        
        if self.last_activity and self.last_activity < timeout:
            self.env['ir.http'].session_logout()
            raise SessionExpiredError("Session expired due to inactivity")
```

## Data Protection

### Encryption at Rest

**Field-Level Encryption**:
```python
# addons/custom/data_encryption/models/encrypted_field.py
from cryptography.fernet import Fernet
import os

class EncryptedField:
    """Mixin for field-level encryption"""
    
    @staticmethod
    def get_encryption_key():
        """Get encryption key from environment"""
        key = os.environ.get('FIELD_ENCRYPTION_KEY')
        if not key:
            raise ValueError("FIELD_ENCRYPTION_KEY not set")
        return key.encode()
    
    def encrypt_value(self, value):
        """Encrypt a field value"""
        if not value:
            return value
        
        fernet = Fernet(self.get_encryption_key())
        encrypted = fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value):
        """Decrypt a field value"""
        if not encrypted_value:
            return encrypted_value
        
        fernet = Fernet(self.get_encryption_key())
        decoded = base64.b64decode(encrypted_value.encode())
        decrypted = fernet.decrypt(decoded)
        return decrypted.decode()

class Partner(models.Model):
    _inherit = 'res.partner'
    
    ssn_encrypted = fields.Char(string='SSN (Encrypted)')
    
    @api.model
    def create(self, vals):
        if 'ssn' in vals:
            encryptor = EncryptedField()
            vals['ssn_encrypted'] = encryptor.encrypt_value(vals.pop('ssn'))
        return super().create(vals)
```

### Data Masking for Non-Production

**PII Anonymization**:
```python
# scripts/anonymize-database.py
"""
Anonymize PII data for non-production environments
"""

anonymization_rules = {
    'res.partner': {
        'email': lambda: f'user{random.randint(1000,9999)}@example.com',
        'phone': lambda: f'+1-555-{random.randint(1000,9999)}',
        'vat': lambda: None,
    },
    'res.users': {
        'login': lambda: f'user{random.randint(1000,9999)}',
        'password': lambda: 'demo',
    },
    'hr.employee': {
        'identification_id': lambda: f'EMP{random.randint(10000,99999)}',
        'passport_id': lambda: None,
        'bank_account_id': lambda: None,
    }
}

def anonymize_database(odoo):
    """Apply anonymization rules"""
    for model_name, fields in anonymization_rules.items():
        records = odoo.env[model_name].search([])
        
        for record_id in records:
            record = odoo.env[model_name].browse(record_id)
            update_vals = {}
            
            for field_name, generator in fields.items():
                update_vals[field_name] = generator()
            
            record.write(update_vals)
            
        print(f"✓ Anonymized {len(records)} records in {model_name}")
```

## API Security

### Rate Limiting

**Implement Rate Limiting**:
```python
# addons/custom/api_security/controllers/rate_limit.py
from collections import defaultdict
from datetime import datetime, timedelta
from odoo import http
from odoo.http import request

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            'default': {'requests': 100, 'window': 60},  # 100 req/min
            'auth': {'requests': 5, 'window': 60},       # 5 req/min for auth
            'api': {'requests': 1000, 'window': 3600},   # 1000 req/hour for API
        }
    
    def is_allowed(self, identifier, limit_type='default'):
        """Check if request is allowed"""
        now = datetime.now()
        limit_config = self.limits.get(limit_type, self.limits['default'])
        
        # Clean old requests
        window_start = now - timedelta(seconds=limit_config['window'])
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[identifier]) >= limit_config['requests']:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

rate_limiter = RateLimiter()

class APIController(http.Controller):
    
    @http.route('/api/v1/data', type='json', auth='user', methods=['GET'])
    def get_data(self, **kwargs):
        """Rate-limited API endpoint"""
        identifier = request.httprequest.remote_addr
        
        if not rate_limiter.is_allowed(identifier, 'api'):
            return {
                'error': 'Rate limit exceeded',
                'retry_after': 60
            }
        
        # Process request
        return {'data': 'response'}
```

### API Authentication

**JWT Token Authentication**:
```python
# addons/custom/api_security/controllers/jwt_auth.py
import jwt
import datetime
from odoo import http
from odoo.http import request

class JWTAuth:
    """JWT authentication for API endpoints"""
    
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    ALGORITHM = 'HS256'
    TOKEN_EXPIRY = 3600  # 1 hour
    
    @classmethod
    def generate_token(cls, user_id, email):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=cls.TOKEN_EXPIRY),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
    
    @classmethod
    def verify_token(cls, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

class APIController(http.Controller):
    
    @http.route('/api/v1/auth/login', type='json', auth='none', methods=['POST'])
    def login(self, email, password):
        """Login endpoint that returns JWT token"""
        # Authenticate user
        uid = request.session.authenticate(request.db, email, password)
        
        if not uid:
            return {'error': 'Invalid credentials'}
        
        # Generate token
        user = request.env['res.users'].browse(uid)
        token = JWTAuth.generate_token(uid, user.login)
        
        return {
            'token': token,
            'expires_in': JWTAuth.TOKEN_EXPIRY
        }
    
    @http.route('/api/v1/protected', type='json', auth='none', methods=['GET'])
    def protected_endpoint(self, **kwargs):
        """Protected endpoint requiring JWT token"""
        auth_header = request.httprequest.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'error': 'Missing or invalid authorization header'}
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = JWTAuth.verify_token(token)
            # Process authenticated request
            return {'data': 'protected resource', 'user_id': payload['user_id']}
        except ValueError as e:
            return {'error': str(e)}
```

## Configuration Security

### Production Security Checklist

```yaml
# production-security-checklist.yaml
security_checklist:
  
  odoo_configuration:
    - name: "Debug mode disabled"
      check: "grep -q 'debug_mode = False' config/odoo.conf"
      severity: critical
    
    - name: "Admin password is strong"
      check: "grep -q 'admin_passwd = ${ODOO_ADMIN_PASSWORD}' config/odoo.conf"
      severity: critical
    
    - name: "Database filter enabled"
      check: "grep -q 'dbfilter' config/odoo.conf"
      severity: high
    
    - name: "List databases disabled"
      check: "grep -q 'list_db = False' config/odoo.conf"
      severity: medium
  
  docker_security:
    - name: "Running as non-root user"
      check: "docker inspect odoo | jq '.[0].Config.User' | grep -v 'root'"
      severity: high
    
    - name: "Health check configured"
      check: "docker inspect odoo | jq '.[0].Config.Healthcheck'"
      severity: medium
    
    - name: "Resource limits set"
      check: "docker inspect odoo | jq '.[0].HostConfig.Memory'"
      severity: medium
  
  network_security:
    - name: "HTTPS enabled"
      check: "curl -I https://example.com | grep -q 'HTTP/2 200'"
      severity: critical
    
    - name: "TLS 1.3 enforced"
      check: "nmap --script ssl-enum-ciphers -p 443 example.com"
      severity: high
    
    - name: "Security headers present"
      check: "curl -I https://example.com | grep -q 'X-Frame-Options'"
      severity: medium
  
  database_security:
    - name: "SSL connections required"
      check: "psql -c 'SHOW ssl' | grep -q 'on'"
      severity: high
    
    - name: "Connection limits set"
      check: "psql -c 'SHOW max_connections' | grep -q '[0-9]'"
      severity: medium
    
    - name: "Password encryption enabled"
      check: "psql -c 'SHOW password_encryption' | grep -q 'scram-sha-256'"
      severity: high
```

### Automated Security Scanning

```bash
#!/bin/bash
# scripts/security-scan.sh

echo "🔍 Running comprehensive security scan..."

# 1. Scan for secrets
echo -e "\n📝 Scanning for hardcoded secrets..."
trufflehog git file://. --json > /tmp/secrets-scan.json
SECRET_COUNT=$(jq '. | length' /tmp/secrets-scan.json)
echo "Found $SECRET_COUNT potential secrets"

# 2. Python security scan
echo -e "\n🐍 Scanning Python code for vulnerabilities..."
bandit -r addons/ -f json -o /tmp/bandit-report.json
BANDIT_ISSUES=$(jq '[.results[] | select(.issue_severity=="HIGH" or .issue_severity=="CRITICAL")] | length' /tmp/bandit-report.json)
echo "Found $BANDIT_ISSUES high/critical issues"

# 3. Dependency vulnerabilities
echo -e "\n📦 Checking dependencies for vulnerabilities..."
safety check --json > /tmp/safety-report.json
VULN_DEPS=$(jq '.vulnerabilities | length' /tmp/safety-report.json)
echo "Found $VULN_DEPS vulnerable dependencies"

# 4. SAST with Semgrep
echo -e "\n🔬 Running static analysis with Semgrep..."
semgrep --config=auto addons/ --json > /tmp/semgrep-report.json
SEMGREP_ISSUES=$(jq '[.results[] | select(.extra.severity=="ERROR")] | length' /tmp/semgrep-report.json)
echo "Found $SEMGREP_ISSUES critical issues"

# 5. Docker security scan
echo -e "\n🐳 Scanning Docker images..."
trivy image insightpulse-odoo:latest --severity HIGH,CRITICAL --format json > /tmp/trivy-report.json
DOCKER_VULNS=$(jq '[.Results[].Vulnerabilities[] | select(.Severity=="HIGH" or .Severity=="CRITICAL")] | length' /tmp/trivy-report.json)
echo "Found $DOCKER_VULNS high/critical Docker vulnerabilities"

# Generate summary
echo -e "\n📊 Security Scan Summary"
echo "========================"
echo "Secrets exposed: $SECRET_COUNT"
echo "Code vulnerabilities: $BANDIT_ISSUES"
echo "Vulnerable dependencies: $VULN_DEPS"
echo "SAST issues: $SEMGREP_ISSUES"
echo "Docker vulnerabilities: $DOCKER_VULNS"

TOTAL_ISSUES=$((SECRET_COUNT + BANDIT_ISSUES + VULN_DEPS + SEMGREP_ISSUES + DOCKER_VULNS))
echo -e "\nTotal critical issues: $TOTAL_ISSUES"

if [ $TOTAL_ISSUES -gt 0 ]; then
    echo "❌ Security scan FAILED - remediation required"
    exit 1
else
    echo "✅ Security scan PASSED"
    exit 0
fi
```

## Dependency Security

### Vulnerability Scanning

```bash
# Check Python dependencies
safety check --full-report

# Check npm dependencies (if any)
npm audit --json

# Check Docker base image
trivy image python:3.11-slim

# Generate SBOM (Software Bill of Materials)
syft packages dir:. -o spdx-json > sbom.json

# Scan SBOM for vulnerabilities
grype sbom:sbom.json
```

### Dependency Update Strategy

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"
    
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

## Compliance

### GDPR Compliance Checklist

- [ ] Data inventory completed
- [ ] Privacy policy published
- [ ] Consent management implemented
- [ ] Right to erasure (RTBF) implemented
- [ ] Data portability enabled
- [ ] Data breach notification procedure
- [ ] DPO (Data Protection Officer) appointed
- [ ] Privacy by design implemented
- [ ] Regular data protection audits

### License Compliance

```bash
# Check license compatibility
pip-licenses --format=json --with-urls > licenses.json

# Verify LGPL-3.0 compliance
find addons/ -name "*.py" -exec head -10 {} \; | grep -c "LGPL-3"

# Check for proprietary dependencies
jq '.[] | select(.License != "LGPL-3.0" and .License != "MIT" and .License != "Apache-2.0")' licenses.json
```

## Continuous Security Monitoring

### CI/CD Security Gates

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r addons/ -ll
      
      - name: Run Safety
        run: |
          pip install safety
          safety check
      
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'CRITICAL,HIGH'
```

---

**Last Updated**: 2025-11-01
**Maintainer**: InsightPulse Security Team
