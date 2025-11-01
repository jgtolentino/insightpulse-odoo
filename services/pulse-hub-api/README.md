# pulse-hub-api

Backend API service for handling GitHub App webhooks for the pulse-hub application.

## Features

- GitHub webhook signature verification
- Event processing for installations, push, pull requests, and issues
- Supabase integration for event storage
- Health check endpoint

## Endpoints

- `GET /health` - Health check endpoint
- `POST /webhook` - GitHub webhook handler

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Set up Supabase tables (see Database Setup below)

4. Run development server:
```bash
npm run dev
```

## Database Setup

Create the following tables in Supabase:

### github_webhooks
```sql
CREATE TABLE github_webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  delivery_id TEXT NOT NULL UNIQUE,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_webhooks_event_type ON github_webhooks(event_type);
CREATE INDEX idx_github_webhooks_received_at ON github_webhooks(received_at);
```

### github_installations
```sql
CREATE TABLE github_installations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  installation_id BIGINT NOT NULL UNIQUE,
  account_login TEXT NOT NULL,
  account_type TEXT NOT NULL,
  action TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_github_installations_account ON github_installations(account_login);
```

## Deployment

This service is designed to be deployed to DigitalOcean App Platform as a service component alongside the pulse-hub static site.

## Environment Variables

See `.env.example` for required environment variables.

## GitHub App Configuration

Make sure your GitHub App webhook URL points to:
```
https://your-app-url.ondigitalocean.app/webhook
```

And set a webhook secret in your GitHub App settings.
