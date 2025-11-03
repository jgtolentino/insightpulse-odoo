# InsightPulse Connection Manager

Supabase-style connection UI for managing your InsightPulse AI infrastructure.

## Features

✅ **Unified Connection Management**
- Manage all your connections in one place
- Supabase, Odoo, Superset, MCP servers, PostgreSQL, APIs

✅ **Auto-Generated Configuration**
- Connection strings
- Environment variables (.env format)
- Docker Compose snippets
- Copy-to-clipboard functionality

✅ **Connection Testing & Monitoring**
- Test connections with one click
- Monitor connection health
- Track active connection counts

✅ **Beautiful Kanban Interface**
- Inspired by Supabase's connection UI
- Color-coded by connection type
- Visual status indicators

## Installation

1. Clone or copy this module to your Odoo addons directory:
   ```bash
   cp -r insightpulse_connection_manager /path/to/odoo/addons/
   ```

2. Update your Odoo Apps list:
   - Go to Apps
   - Click "Update Apps List"

3. Install the module:
   - Search for "InsightPulse Connection Manager"
   - Click "Install"

## Usage

### View Connections

Navigate to: **InsightPulse AI > Connection Manager**

You'll see pre-configured connections for:
- Production Supabase database
- Apache Superset dashboard
- Odoo 19 ERP database
- MCP servers (Notion, Google Drive)
- PostgreSQL development instance

### Add New Connection

1. Click "Create" button
2. Fill in connection details:
   - Connection Name
   - Connection Type (Supabase, Odoo, Superset, etc.)
   - Server details (URL, port, database name)
   - Authentication (username, password, API key)
3. Click "Save"

### Test Connection

1. Open a connection record
2. Click "Test Connection" button
3. View test results in the status bar

### Copy Configuration

Each connection provides:

1. **Connection String tab**: Full connection URI
2. **Environment Variables tab**: .env format
3. **Docker Compose tab**: Service definition snippet

Use the copy buttons in Kanban view for quick access.

## Configuration for Your Environment

### Supabase Connection

Update the default Supabase connection with your credentials:
- Base URL: `db.spdtwktxdalcfigzeqrz.supabase.co`
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: Your Supabase password

### Odoo Database Connection

If using a different Odoo database:
- Base URL: Your Postgres host
- Port: `5432`
- Database: Your database name (e.g., `odoo19`)
- Username: `odoo`
- Password: Your Odoo database password

### Apache Superset

Configure your Superset instance:
- Base URL: Your Superset host
- Port: `8088` (default)
- Username: `admin`
- Password: Your admin password

## Integration with Finance SSC

This module is designed for Finance Shared Service Center operations:

- **BIR Compliance**: Connection to databases storing BIR forms (1601-C, 2550Q, 1702-RT)
- **Multi-Agency Operations**: Manage connections for RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB agencies
- **Month-End Closing**: Connect to systems tracking closing tasks and schedules
- **Dashboard Integration**: Link to Superset for compliance dashboards

## Security Notes

- Passwords and API keys are stored securely in Odoo's database
- Use SSL/TLS connections for production environments
- Regularly rotate credentials
- Limit access using Odoo's access control groups

## Cost Savings

By using this self-hosted connection manager:
- **No vendor lock-in**: Own your infrastructure
- **Zero licensing costs**: Open-source solution
- **Integrated workflow**: All connections in one place

## Support

- Project: [InsightPulse AI](https://insightpulseai.net)
- Documentation: [odoboo-workspace](https://github.com/jgtolentino/insightpulse-odoo)

## License

LGPL-3.0

---

**Built for Finance Shared Service Centers managing multi-agency operations with self-hosted infrastructure.**
