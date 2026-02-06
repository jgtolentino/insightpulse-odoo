# Colima Setup Guide for Odoo 19 Development

This guide helps you set up a fast, deterministic Odoo 19 development environment using Colima on Apple Silicon.

## Prerequisites

- macOS with Apple Silicon (M1/M2/M3)
- Homebrew installed
- Colima and Docker CLI installed

## Install Required Tools

```bash
# Install Colima and Docker CLI
brew install colima docker docker-compose

# Install Docker credential helper (optional but recommended)
brew install docker-credential-helper
```

## Start Colima with Optimized Settings

```bash
# Stop any existing Colima instance
colima stop --force || true
colima delete || true

# Start with Apple Virtualization Framework and virtiofs for fast file sharing
colima start \
  --cpu 4 \
  --memory 8 \
  --disk 60 \
  --vm-type=vz \
  --mount-type=virtiofs \
  --network-address
```

### Settings Explained

- `--cpu 4`: Allocate 4 CPU cores (adjust based on your machine)
- `--memory 8`: Allocate 8GB RAM (minimum for Odoo + PostgreSQL)
- `--disk 60`: 60GB disk space
- `--vm-type=vz`: Use Apple Virtualization Framework (faster than QEMU)
- `--mount-type=virtiofs`: Use virtiofs for fast file sharing (better than sshfs/9p)
- `--network-address`: Enable network address assignment

## Start Odoo 19 Development Stack

```bash
# From repository root
./scripts/dev_up_odoo19.sh
```

This script will:
1. Pull Docker images (odoo:19.0-20260119, postgres:16-alpine, pgadmin4)
2. Compute and store digest pins in `runtime/dev/.env.odoo19`
3. Start the stack with Docker Compose
4. Verify Odoo is reachable

## Access Points

- **Odoo**: http://localhost:8069
- **pgAdmin**: http://localhost:5050 
  - Email: admin@admin.com
  - Password: admin

## Common Operations

### View Logs

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml logs -f web
docker compose --env-file .env.odoo19 -f compose.odoo19.yml logs -f db
```

### Stop Stack

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml down
```

### Clean All Data (Fresh Start)

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml down -v
```

### Restart Single Service

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml restart web
```

### Shell Access

```bash
# Odoo container
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml exec web bash

# PostgreSQL container
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml exec db psql -U odoo
```

## Troubleshooting

### Colima Not Starting

```bash
# Check Colima status
colima status

# View Colima logs
colima logs

# Reset Colima completely
colima delete --force
colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz --mount-type=virtiofs
```

### Slow File Access

If file access is slow:
1. Ensure you're using `--mount-type=virtiofs` (fastest on Apple Silicon)
2. Check that Colima is using `vm-type=vz` (Apple Virtualization)
3. Restart Colima if needed

### Docker Command Not Found

```bash
# Set Docker context to Colima
docker context use colima

# Verify connection
docker ps
```

### Port Already in Use

```bash
# Find what's using port 8069
lsof -i :8069

# Stop conflicting service or change port in compose.odoo19.yml
```

### Permission Issues

The setup uses proper permissions (`u+rwX,go+rX`) instead of `chmod 777`. If you encounter permission issues:

```bash
# Fix config directory
chmod -R u+rwX,go+rX config

# Fix addons directory
chmod -R u+rwX,go+rX addons
```

## Performance Tips

1. **Use virtiofs**: Fastest mount type on Apple Silicon
2. **Allocate enough RAM**: 8GB minimum, 12GB+ recommended for production-like workloads
3. **Use SSD**: Keep Colima VM on SSD for best performance
4. **Avoid file watchers**: Disable file watching in IDEs for mounted volumes if possible
5. **Use volumes for data**: PostgreSQL and Odoo data use Docker volumes (fast)

## Updating Image Pins

To update to a newer Odoo version:

```bash
# 1. Edit the pin file
echo "odoo:19.0-20260201" > ops/pins/odoo_19.tag.txt

# 2. Re-compute digests
./scripts/pin_images.sh

# 3. Restart stack
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml up -d
```

## Resources

- [Colima Documentation](https://github.com/abiosoft/colima)
- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [PostgreSQL 16 Documentation](https://www.postgresql.org/docs/16/)
