# pulser-hub MCP Server (Node/TypeScript)

**Model Context Protocol (MCP) server** for Odoo operations via XML-RPC.

## 🏗️ Architecture

- **Runtime**: Node.js 20 (TypeScript)
- **Framework**: Fastify + WebSocket
- **Protocol**: Model Context Protocol (MCP SDK)
- **Odoo Integration**: XML-RPC via undici (HTTP client)
- **Platform**: DigitalOcean App Platform

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your Odoo credentials

# Build TypeScript
npm run build

# Start server
npm start
```

Server runs at: `http://localhost:8080`

### Development Mode (with auto-reload)

```bash
npm run dev
```

### Docker

```bash
# Build image
docker build -t pulser-hub-mcp .

# Run container
docker run -p 8080:8080 \
  -e ODOO_URL=https://your-odoo.com \
  -e ODOO_DB=your_db \
  -e ODOO_USER=your_user \
  -e ODOO_PASSWORD=your_password \
  pulser-hub-mcp
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/healthz` | GET | Health check (returns `{"ok": true}`) |
| `/ws` | WebSocket | MCP protocol endpoint |

## 🔧 Environment Variables

### Required (Odoo Configuration)

```bash
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_database_name
ODOO_USER=your_odoo_username
ODOO_PASSWORD=your_odoo_password
```

### Optional (Server Configuration)

```bash
PORT=8080                    # Server port (auto-set by DO App Platform)
HOST=0.0.0.0                 # Server host
NODE_ENV=production          # Node environment
LOG_LEVEL=info               # Logging level (debug, info, warn, error)
```

## 🛠️ MCP Tools

The server exposes the following MCP tools for Odoo operations:

### 1. `odoo.health`

Check Odoo connection health and authentication.

```json
{
  "name": "odoo.health",
  "arguments": {}
}
```

**Response**:
```json
{
  "uid": 2,
  "status": "ok",
  "message": "Connected to Odoo successfully"
}
```

### 2. `odoo.search_read`

Search and read Odoo records.

```json
{
  "name": "odoo.search_read",
  "arguments": {
    "model": "res.partner",
    "domain": [["is_company", "=", true]],
    "fields": ["name", "email", "phone"],
    "limit": 10,
    "offset": 0
  }
}
```

**Response**: Array of records matching the search criteria.

### 3. `odoo.create`

Create a new Odoo record.

```json
{
  "name": "odoo.create",
  "arguments": {
    "model": "res.partner",
    "values": {
      "name": "New Company",
      "email": "contact@newcompany.com",
      "is_company": true
    }
  }
}
```

**Response**:
```json
{
  "id": 123,
  "created": true
}
```

### 4. `odoo.write`

Update existing Odoo records.

```json
{
  "name": "odoo.write",
  "arguments": {
    "model": "res.partner",
    "ids": [123, 456],
    "values": {
      "phone": "+1234567890"
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "updated": 2
}
```

### 5. `odoo.unlink`

Delete Odoo records.

```json
{
  "name": "odoo.unlink",
  "arguments": {
    "model": "res.partner",
    "ids": [123]
  }
}
```

**Response**:
```json
{
  "success": true,
  "deleted": 1
}
```

## 🚀 DigitalOcean App Platform Deployment

### Prerequisites

1. **Install `doctl`**: [DigitalOcean CLI](https://docs.digitalocean.com/reference/doctl/how-to/install/)
2. **Authenticate**: `doctl auth init`
3. **Set environment variables** in DigitalOcean dashboard

### Deployment Methods

**Option 1: Via Dashboard**

1. Go to: https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Select GitHub repository: `jgtolentino/insightpulse-odoo`
4. Configure:
   - **Source Directory**: `services/mcp-server`
   - **Dockerfile Path**: `services/mcp-server/Dockerfile`
   - **HTTP Port**: `8080`
   - **Health Check Path**: `/healthz`
5. Set environment variables (see below)
6. Deploy

**Option 2: Via `doctl` CLI**

```bash
# Create app from spec
doctl apps create --spec services/mcp-server/app.yaml

# Get app ID
APP_ID=$(doctl apps list --format ID,Name --no-header | grep "pulser-hub-mcp" | awk '{print $1}')

# Monitor deployment
doctl apps logs $APP_ID --follow
```

**Option 3: Update Existing App**

```bash
# Update app spec
doctl apps update $APP_ID --spec services/mcp-server/app.yaml

# Force rebuild
doctl apps create-deployment $APP_ID --force-rebuild
```

### Setting Environment Variables in DigitalOcean

1. Go to: **Apps** → **pulser-hub-mcp** → **Settings** → **Environment Variables**
2. Add the following **SECRET** variables:
   - `ODOO_URL` = `https://your-odoo-instance.com`
   - `ODOO_DB` = `your_database_name`
   - `ODOO_USER` = `your_odoo_username`
   - `ODOO_PASSWORD` = `your_odoo_password`
3. Set scope: **RUN_AND_BUILD_TIME**
4. Click **Save** → App will automatically redeploy

## ✅ Post-Deployment Verification

### 1. Check Health

```bash
# Get app URL
APP_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)

# Test health check
curl -f $APP_URL/healthz
# Expected: {"ok":true,"service":"pulser-hub-mcp","timestamp":"..."}
```

### 2. Test Odoo Connection

```bash
# Test via MCP WebSocket client (example with wscat)
npm install -g wscat

wscat -c wss://$APP_URL/ws

# Send MCP request:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "odoo.health",
    "arguments": {}
  }
}

# Expected response:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "uid": 2,
    "status": "ok",
    "message": "Connected to Odoo successfully"
  }
}
```

### 3. Check Logs

```bash
# Real-time logs
doctl apps logs $APP_ID --follow

# Build logs
doctl apps logs $APP_ID --type build

# Runtime logs
doctl apps logs $APP_ID --type run
```

## 🐛 Troubleshooting

### Deployment Fails

**Symptom**: Build fails or app exits immediately after deploy.

**Common Causes**:
1. Missing `ODOO_*` environment variables
2. TypeScript compilation errors
3. Missing dependencies in package.json

**Solutions**:
```bash
# Check build logs
doctl apps logs $APP_ID --type build

# Verify env vars are set
doctl apps get $APP_ID | grep ODOO

# Force rebuild
doctl apps create-deployment $APP_ID --force-rebuild
```

### Health Check Fails

**Symptom**: App shows "Unhealthy" status in dashboard.

**Common Causes**:
1. Wrong health check path (should be `/healthz`, not `/health`)
2. Server not binding to `$PORT` environment variable
3. Server crashed due to missing Odoo credentials

**Solutions**:
```bash
# Check runtime logs
doctl apps logs $APP_ID --type run

# Verify health check path
curl -v https://your-app-url.ondigitalocean.app/healthz

# Check if server is listening
doctl apps logs $APP_ID | grep "listening on"
```

### Odoo Tools Return Errors

**Symptom**: `odoo.health` or other tools fail with authentication errors.

**Common Causes**:
1. Invalid Odoo credentials
2. Odoo URL not accessible from DigitalOcean
3. Firewall blocking XML-RPC requests

**Solutions**:
```bash
# Test Odoo connectivity from local machine
curl -X POST https://your-odoo.com/xmlrpc/2/common \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?><methodCall><methodName>version</methodName></methodCall>'

# Verify credentials work in Odoo web interface
# Check Odoo server logs for authentication attempts
```

## 📊 Monitoring

### DigitalOcean App Platform Insights

- **CPU Usage**: Monitor in dashboard
- **Memory Usage**: Should stay under 512MB (basic-xxs tier)
- **Request Throughput**: Track WebSocket connections
- **Response Times**: Monitor health check latency

### Custom Metrics

Add logging to track:
- MCP tool call frequency
- Odoo API response times
- Error rates per tool

## 🔐 Security

### Best Practices

1. ✅ **Never commit secrets** to repository
2. ✅ **Use DigitalOcean Secrets** for sensitive env vars
3. ✅ **Enable HTTPS** (automatic on DO App Platform)
4. ✅ **Rotate credentials** regularly
5. ✅ **Use read-only Odoo user** if possible
6. ✅ **Implement rate limiting** (via Traefik or Fastify plugin)
7. ✅ **Monitor logs** for suspicious activity

### Odoo User Permissions

Create a dedicated Odoo user for MCP with minimal permissions:

1. Go to Odoo: **Settings** → **Users & Companies** → **Users**
2. Create user: `mcp_service`
3. Set **Access Rights**: Read-only access to models you need
4. Use this user's credentials in `ODOO_USER` and `ODOO_PASSWORD`

## 📝 Development

### Project Structure

```
services/mcp-server/
├── src/
│   ├── server.ts       # Main Fastify server + WebSocket
│   └── odoo.ts         # Odoo XML-RPC client + MCP tools
├── dist/               # Compiled JavaScript (generated)
├── package.json        # Node dependencies
├── tsconfig.json       # TypeScript configuration
├── Dockerfile          # Multi-stage Node build
├── app.yaml            # DigitalOcean App Platform spec
├── .env.example        # Environment variable template
└── README.md           # This file
```

### Adding New MCP Tools

1. Add tool definition to `tools` array in `src/odoo.ts`
2. Implement handler in `handlers` object
3. Use Zod for input validation
4. Test locally before deploying

Example:

```typescript
// In src/odoo.ts

// Add tool definition
{
  name: 'odoo.my_custom_tool',
  description: 'Description of what this tool does',
  inputSchema: {
    type: 'object',
    properties: {
      myParam: { type: 'string', description: 'Parameter description' }
    },
    required: ['myParam']
  }
}

// Add handler
'odoo.my_custom_tool': async (args) => {
  const schema = z.object({
    myParam: z.string(),
  });

  const params = schema.parse(args);

  // Your implementation here
  const result = await client.execute('my.model', 'my_method', [params.myParam]);

  return result;
}
```

## 📚 Resources

- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [MCP SDK for TypeScript](https://github.com/modelcontextprotocol/typescript-sdk)
- [Odoo External API](https://www.odoo.com/documentation/17.0/developer/reference/external_api.html)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)
- [Fastify Documentation](https://fastify.dev/)

## 🤝 Support

For issues related to:
- **MCP Server**: Open issue in this repository
- **Odoo Integration**: Check Odoo server logs
- **DigitalOcean Deployment**: Check App Platform docs or open support ticket

---

**Status**: ✅ Production Ready (Node/TypeScript)
**Version**: 1.0.0
**Last Updated**: November 2, 2025
