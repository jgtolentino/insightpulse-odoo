# Troubleshooting Guide

Common issues and solutions for InsightPulse Odoo platform.

## Odoo Issues

### Odoo won't start
**Symptoms**: Container exits immediately or won't start

**Solutions**:
1. Check database connection:
   ```bash
   docker compose logs postgres-odoo
   ```
2. Verify environment variables in .env
3. Check port conflicts (8069)
4. Review Odoo logs:
   ```bash
   docker compose logs odoo
   ```

### Module not loading
**Symptoms**: Custom module doesn't appear in Apps menu

**Solutions**:
1. Verify module in addons path:
   ```bash
   docker compose exec odoo ls /opt/odoo/custom/addons/
   ```
2. Update apps list: Settings → Apps → Update Apps List
3. Check manifest.py syntax
4. Restart Odoo:
   ```bash
   docker compose restart odoo
   ```

### Database migration errors
**Symptoms**: Errors during Odoo upgrade

**Solutions**:
1. Backup database first
2. Use `--stop-after-init` flag for dry run
3. Review migration logs
4. Restore from backup if needed

## Docker Issues

### Port already in use
**Symptoms**: Error binding to port 8069

**Solutions**:
```bash
# Find process using port
lsof -i :8069

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Disk space issues
**Symptoms**: Docker build fails with "no space left on device"

**Solutions**:
```bash
# Clean up Docker
docker system prune -a

# Remove unused volumes
docker volume prune

# Check disk usage
df -h
```

### Permission denied
**Symptoms**: Cannot write to mounted volumes

**Solutions**:
```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) odoo/addons/

# Or use Docker user mapping in docker-compose.yml
```

## CI/CD Issues

### Spec guard failing
**Symptoms**: spec-guard.yml workflow fails

**Solutions**:
1. Run validation locally:
   ```bash
   python scripts/validate_spec.py
   ```
2. Check for missing docs files
3. Verify platform_spec.json syntax
4. Ensure all referenced files exist

### Deployment failed
**Symptoms**: cd-odoo-prod.yml fails

**Solutions**:
1. Check GitHub Secrets are set
2. Verify DigitalOcean droplet is accessible
3. Review deployment logs
4. SSH to droplet and check manually

### Tests failing
**Symptoms**: ci-odoo.yml fails

**Solutions**:
1. Run tests locally:
   ```bash
   docker compose exec odoo python -m pytest
   ```
2. Check test dependencies
3. Review test logs
4. Fix failing tests before pushing

## Database Issues

### Connection refused
**Symptoms**: Odoo can't connect to PostgreSQL

**Solutions**:
1. Verify PostgreSQL is running:
   ```bash
   docker compose ps postgres-odoo
   ```
2. Check connection string in .env
3. Verify network connectivity:
   ```bash
   docker compose exec odoo ping postgres-odoo
   ```

### Migration stuck
**Symptoms**: Supabase migration hangs

**Solutions**:
1. Check migration logs
2. Verify database not locked
3. Kill long-running queries
4. Retry migration

## OAuth Issues

### Login redirect fails
**Symptoms**: OAuth redirect to Google fails

**Solutions**:
1. Verify OAuth credentials in spec/platform_spec.json
2. Check authorized redirect URIs in Google Console
3. Ensure domains match exactly (https://erp.insightpulseai.net)
4. Clear browser cookies and retry

### Session expired
**Symptoms**: Frequent re-authentication required

**Solutions**:
1. Check session timeout settings
2. Verify cookie domain configuration
3. Review OAuth token expiry

## Performance Issues

### Slow page loads
**Symptoms**: Odoo pages load slowly

**Solutions**:
1. Check resource usage:
   ```bash
   docker stats
   ```
2. Optimize database queries
3. Enable caching
4. Review Odoo logs for slow queries

### High memory usage
**Symptoms**: Docker container uses excessive memory

**Solutions**:
1. Limit container memory in docker-compose.yml
2. Optimize Odoo configuration
3. Review memory-intensive modules

## BIR Compliance Issues

### Form generation fails
**Symptoms**: BIR forms (2307, 2316) not generating

**Solutions**:
1. Verify immutable accounting records
2. Check audit trail completeness
3. Review tax calculation logic
4. Validate company TIN configuration

## Support

- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Documentation**: https://jgtolentino.github.io/insightpulse-odoo/
- **Odoo Community**: https://www.odoo.com/forum
- **OCA Guidelines**: https://github.com/OCA

## Next Steps

- Review [Architecture](../architecture.md)
- Check [Deployment Guide](../deployments/overview.md)
- See [CI/CD Workflows](workflows-ci-cd.md)
