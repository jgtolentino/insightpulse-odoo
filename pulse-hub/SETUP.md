# pulse.hub Quick Setup Guide

## Prerequisites

- Node.js 18+ installed
- GitHub account
- GitHub OAuth App created

## Step-by-Step Setup

### 1. Create GitHub OAuth App

1. Visit: https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   ```
   Application name: pulse.hub
   Homepage URL: http://localhost:3000
   Authorization callback URL: http://localhost:3000/callback
   ```
4. Click "Register application"
5. Copy your **Client ID**

### 2. Configure Environment

```bash
cd pulse-hub
cp .env.example .env
```

Edit `.env`:
```env
VITE_GITHUB_CLIENT_ID=your_client_id_here
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/callback
```

### 3. Install & Run

```bash
npm install
npm run dev
```

Open http://localhost:3000

## First Use

1. **Select Scopes**: Choose which permissions AI assistants will have
2. **Connect**: Click "Connect with GitHub" and authorize
3. **Configure AI**:
   - For Claude: Copy config to `~/.config/claude/claude_desktop_config.json`
   - For ChatGPT: Use the OpenAPI schema in Custom GPT Actions
   - For API: Use the direct examples
4. **Select Repos**: Choose which repositories to grant access to

## Troubleshooting

### "Client ID not found" error
- Check your `.env` file has the correct `VITE_GITHUB_CLIENT_ID`
- Restart the dev server after changing `.env`

### OAuth callback fails
- Verify callback URL in GitHub OAuth App settings matches `.env`
- Check for typos in the redirect URI

### Dark mode not working
- Click the sun/moon icon in the header
- Check browser developer tools for errors

## Production Deployment

### Environment Variables

Set these in your hosting platform:
```env
VITE_GITHUB_CLIENT_ID=your_production_client_id
VITE_GITHUB_REDIRECT_URI=https://your-domain.com/callback
```

### Build

```bash
npm run build
```

Deploy the `dist/` directory to your hosting platform.

### Update GitHub OAuth App

Update your OAuth app settings:
- Homepage URL: `https://your-domain.com`
- Authorization callback URL: `https://your-domain.com/callback`

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Enable CORS properly
- [ ] Keep dependencies updated
- [ ] Don't commit `.env` file
- [ ] Use minimal scopes needed
- [ ] Monitor API rate limits

## Need Help?

- Check the main [README.md](./README.md)
- Open an issue on GitHub
- Review GitHub OAuth documentation: https://docs.github.com/en/apps/oauth-apps
