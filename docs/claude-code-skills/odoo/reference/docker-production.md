# Docker Production Configuration

## docker-compose.yml Structure

- Odoo 19 container (4 workers, 2 cron threads)
- PostgreSQL 15 or Supabase
- Nginx reverse proxy
- Certbot for SSL

## Security

- Database manager blocked
- SSL with modern ciphers
- Rate limiting
- Security headers (HSTS, CSP, X-Frame-Options)
