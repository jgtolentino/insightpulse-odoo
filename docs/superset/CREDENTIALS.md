# Apache Superset Production Credentials

## Default Credentials (Pre-configured)

### Admin Account
- **Username**: `admin`
- **Password**: `Postgres_26`
- **Email**: `admin@insightpulseai.net`

### Database Connection
- **Host**: `aws-1-us-east-1.pooler.supabase.com`
- **Port**: `6543` (Supabase connection pooler)
- **Database**: `postgres`
- **User**: `postgres.spdtwktxdalcfigzeqrz`
- **Password**: `Postgres_26`
- **SSL**: Required (`sslmode=require`)

### Security Keys
- **SUPERSET_SECRET_KEY**: `8UToEhL2C0ovd7S4maFPsi7e4mU05pqAH907G5yUaLsr9prnJdHu7+6k`
- **Generated**: 2025-10-30
- **Algorithm**: OpenSSL base64 (42 characters)

## Access URLs

### Development/Direct Access
```
https://superset-analytics-[app-id].ondigitalocean.app
```

### Production Access (via Traefik)
```
https://insightpulseai.net/superset
```

## Login Instructions

1. **Navigate to Superset**:
   ```
   https://insightpulseai.net/superset
   ```

2. **Enter Credentials**:
   - Username: `admin`
   - Password: `Postgres_26`

3. **First Login Checklist**:
   - [ ] Change admin password (recommended)
   - [ ] Create database connections
   - [ ] Configure user permissions
   - [ ] Setup email/Slack notifications
   - [ ] Enable 2FA (if available)

## Database Connection String

**For Superset Data Sources**:
```
postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
```

**For External Tools**:
```bash
# psql connection
psql "postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Connection URL (programmatic)
DATABASE_URL="postgresql://postgres.spdtwktxdalcfigzeqrz:Postgres_26@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

## Redis Connection

**Internal Service** (DigitalOcean App Platform):
- **Host**: `redis` (internal service name)
- **Port**: `6379`
- **Password**: Not required (internal network)

## Security Recommendations

### Immediate Actions (Post-Deployment)
1. **Change Admin Password**:
   - Go to: Settings → User Profile → Change Password
   - Use strong password (16+ characters, mixed case, numbers, symbols)

2. **Enable HTTPS Only**:
   - Verify Traefik enforces HTTPS
   - Check: `curl -I http://insightpulseai.net/superset` → Should redirect to HTTPS

3. **Rotate Secret Key** (Every 90 Days):
   ```bash
   # Generate new secret key
   NEW_KEY=$(openssl rand -base64 42)

   # Update in DigitalOcean dashboard
   # Settings → Environment Variables → SUPERSET_SECRET_KEY
   ```

### Access Control
1. **Create Limited Users**:
   - Don't share admin account
   - Create role-based users (Alpha, Gamma, SQL Lab)
   - Assign minimal permissions

2. **Enable Row Level Security**:
   - Configure RLS policies in Superset
   - Restrict data access by user/role

3. **Audit Logs**:
   - Monitor: Security → Action Log
   - Review login attempts regularly

### Network Security
1. **Firewall Rules**:
   - Only allow HTTPS (443) and HTTP (80 → 443 redirect)
   - Block direct access to DigitalOcean App Platform URL (optional)

2. **Rate Limiting**:
   - Traefik enforces: 100 req/s, burst 200
   - Monitor for abuse in logs

3. **SSL/TLS**:
   - Let's Encrypt certificates (auto-renewal)
   - TLS 1.2+ only
   - Strong cipher suites

## Credential Rotation Schedule

| Credential | Rotation Interval | Last Rotated | Next Rotation |
|------------|-------------------|--------------|---------------|
| Admin Password | 90 days | 2025-10-30 | 2026-01-28 |
| SUPERSET_SECRET_KEY | 90 days | 2025-10-30 | 2026-01-28 |
| Database Password | 180 days | 2025-10-30 | 2026-04-28 |

## Backup Access

### Emergency Access
If admin account is locked:
1. SSH into DigitalOcean App Platform console (if available)
2. Or reset via Supabase database:
   ```sql
   UPDATE ab_user
   SET password = '[bcrypt_hash]'
   WHERE username = 'admin';
   ```

### Database Backup Access
Supabase provides automated backups:
- **Retention**: 7 days (free tier), 30 days (Pro)
- **Restore**: Via Supabase dashboard → Database → Backups

## Troubleshooting

### Cannot Login
**Symptoms**: Invalid username/password

**Solutions**:
1. Verify credentials: `admin` / `Postgres_26`
2. Check caps lock is off
3. Reset password via database (see Emergency Access)
4. Check logs: `doctl apps logs [APP_ID] | grep "login"`

### Database Connection Failed
**Symptoms**: Cannot connect to database from Superset

**Solutions**:
1. Verify Supabase project is active
2. Test connection: `psql "[CONNECTION_STRING]"`
3. Check firewall rules (Supabase allows all by default)
4. Verify SSL is enabled (`sslmode=require`)

### Secret Key Error
**Symptoms**: Session errors, CSRF errors

**Solutions**:
1. Verify `SUPERSET_SECRET_KEY` is set correctly
2. Check environment variables in DO dashboard
3. Restart app: `doctl apps create-deployment [APP_ID]`

## Support

**Internal**:
- Deployment: `deploy/superset/deploy.sh`
- Configuration: `config/superset/superset_config_production.py`
- Security: `security/superset/secrets.env.example`

**External**:
- [Superset Security Docs](https://superset.apache.org/docs/6.0.0/security/)
- [Supabase Database Docs](https://supabase.com/docs/guides/database)

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0
**Status**: ✅ Production Credentials Set

⚠️ **WARNING**: Keep this file secure. Do NOT commit to public repositories.
