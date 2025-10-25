# Development Guide - Live Extension & Port Server

This guide explains how to set up and use the live reload development environment for InsightPulse Odoo.

## 🚀 Quick Start

### Option 1: Docker Development Server (Recommended)

```bash
# Start development environment with live reload
./dev-server.sh

# Or manually:
docker compose -f docker-compose.dev.yml up -d
```

### Option 2: VS Code Live Server Extension

1. **Install VS Code Live Server Extension**
2. **Right-click on `addons` folder** → "Open with Live Server"
3. **Access at**: http://localhost:5500

### Option 3: Node.js Live Server

```bash
# Install dependencies
npm install

# Start live server
npm run dev
# or
npm run watch
```

## 🔧 Development Features

### Live Reload Capabilities

- **Static Files**: CSS, JS, XML files auto-reload on changes
- **Addon Files**: Python files trigger Odoo restart
- **Templates**: XML views update without restart
- **Assets**: Static assets refresh automatically

### Port Configuration

| Service | Port | Purpose |
|---------|------|---------|
| Odoo | 8069 | Main Odoo interface |
| Long Polling | 8072 | Real-time updates |
| Live Server | 3000 | Static file serving with live reload |
| File Watcher | 3001 | Development status API |

## 📁 File Structure

```
insightpulse-odoo/
├── docker-compose.dev.yml    # Development Docker setup
├── dev-server.sh            # Development startup script
├── live-server.conf         # Nginx configuration for live reload
├── package.json             # Node.js dependencies
├── .vscode/
│   ├── settings.json        # VS Code settings
│   └── launch.json          # VS Code launch configurations
└── addons/                  # Your addons (watched for changes)
    ├── custom/
    └── oca/
```

## 🛠️ Development Workflow

### 1. Start Development Environment

```bash
# Start everything
./dev-server.sh

# Or step by step
docker compose -f docker-compose.dev.yml up -d
```

### 2. Access Development Tools

- **Odoo**: http://localhost:8069
- **Live Reload**: http://localhost:3000
- **File Watcher**: http://localhost:3001

### 3. Develop Your Addons

1. **Edit files** in `addons/` directory
2. **Static files** (CSS/JS) reload automatically
3. **Python files** trigger Odoo restart
4. **XML files** update without restart

### 4. Monitor Development

```bash
# View Odoo logs
docker compose -f docker-compose.dev.yml logs -f odoo

# View all logs
docker compose -f docker-compose.dev.yml logs -f
```

## 🔄 Live Reload Configuration

### VS Code Settings

The `.vscode/settings.json` includes:
- Live Server port configuration
- File watching exclusions
- Python development settings
- File associations for Odoo files

### Docker Development Mode

The `docker-compose.dev.yml` includes:
- `--dev=all` - Enables development mode
- `--workers=0` - Single process for debugging
- `--log-level=debug` - Verbose logging
- Volume mounts for live file watching

### Nginx Live Server

The `live-server.conf` provides:
- Static file serving with no-cache headers
- CORS headers for development
- WebSocket support for live reload
- Gzip compression

## 🐛 Troubleshooting

### Live Reload Not Working

1. **Check file permissions**:
   ```bash
   chmod -R 755 addons/
   ```

2. **Restart development server**:
   ```bash
   docker compose -f docker-compose.dev.yml restart
   ```

3. **Check browser console** for WebSocket errors

### Port Conflicts

If ports are in use:

1. **Change ports** in `docker-compose.dev.yml`
2. **Update VS Code settings** in `.vscode/settings.json`
3. **Update package.json** scripts

### File Changes Not Detected

1. **Check volume mounts**:
   ```bash
   docker compose -f docker-compose.dev.yml config
   ```

2. **Verify file watching**:
   ```bash
   # Check if files are being watched
   docker compose -f docker-compose.dev.yml exec odoo ls -la /mnt/extra-addons
   ```

## 📚 Advanced Usage

### Custom Live Reload

You can customize the live reload behavior by modifying:
- `live-server.conf` - Nginx configuration
- `docker-compose.dev.yml` - Container settings
- `.vscode/settings.json` - VS Code configuration

### Development Database

The development environment uses a separate database:
- **Database**: `insightpulse`
- **User**: `odoo`
- **Password**: `odoo`

### Hot Module Replacement

For advanced hot module replacement:
1. Use webpack-dev-server
2. Configure Odoo asset bundling
3. Set up custom build pipeline

## 🚀 Production Deployment

When ready for production:

1. **Use production compose file**:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```

2. **Disable development features**:
   - Remove `--dev=all` flag
   - Set proper worker count
   - Enable production logging

3. **Configure reverse proxy** (Nginx/Caddy)

## 📖 Additional Resources

- [Odoo Development Documentation](https://www.odoo.com/documentation/19.0/developer.html)
- [VS Code Live Server Extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
