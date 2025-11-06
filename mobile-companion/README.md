# InsightPulse Expense Companion

**Expo (Native + Web/PWA)** mobile companion app for receipt capture and expense submission.

## Architecture

```
User captures receipt → Supabase Storage (private bucket with RLS)
                     ↓
               Edge Function (notify-odoo)
                     ↓
          Mints signed URL (15-min TTL)
                     ↓
         Notifies Odoo /api/v1/receipts/pull
                     ↓
            Odoo pulls via signed URL
                     ↓
           OCR processing + expense creation
```

## Features

- **Cross-Platform**: iOS, Android, and Web/PWA from single codebase
- **Supabase Auth**: Magic link email + OAuth (Google/Apple on web)
- **Secure Storage**: Expo Secure Store for native, localStorage for web
- **Private File Storage**: Supabase Storage with Row Level Security (RLS)
- **Signed URLs**: 15-minute TTL for secure file access
- **Edge Functions**: Serverless Deno functions for Odoo integration
- **PWA Support**: Installable web app with offline capabilities

## Prerequisites

- Node.js 18+ and npm
- Supabase CLI (`npm install -g supabase`)
- Expo CLI (`npm install -g expo-cli` or use npx)
- Supabase project with:
  - Database with `receipts` table (see `supabase/sql/001_receipts.sql`)
  - Storage bucket `receipts` (private, RLS enabled)
  - Edge Function `notify-odoo` (see `supabase/functions/notify-odoo/`)

## Setup

### 1. Install Dependencies

```bash
cd mobile-companion
npm install
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp ../.env.example .env
```

Required variables:
- `EXPO_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `EXPO_PUBLIC_SUPABASE_ANON_KEY` - Your Supabase anon/public key
- `ODOO_BASE_URL` - Your Odoo instance URL
- `ODOO_API_TOKEN` - Odoo API bot token

### 3. Setup Supabase Database

```bash
# Login to Supabase
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Push database migrations
supabase db push
```

This creates:
- `receipts` table with RLS policies
- Storage bucket `receipts` (private)
- Storage RLS policies for user isolation

### 4. Deploy Edge Functions

```bash
cd ..
make supabase-deploy
```

Or manually:
```bash
supabase functions deploy notify-odoo --no-verify-jwt
```

Set environment variables for Edge Function:
```bash
supabase secrets set ODOO_BASE_URL=https://insightpulseai.net
supabase secrets set ODOO_API_TOKEN=your_odoo_bot_token
```

## Development

### Run Locally

**Native (iOS/Android)**:
```bash
npm start
# Press 'i' for iOS or 'a' for Android
```

**Web**:
```bash
npm run web
```

**PWA Build**:
```bash
npm run build:web
npm run serve
# Open http://localhost:3000
```

### Project Structure

```
mobile-companion/
├── src/
│   ├── supabase/
│   │   └── client.ts          # Supabase client with Expo Secure Store
│   ├── api/
│   │   └── receipts.ts        # Receipt upload API
│   └── screens/
│       ├── LoginScreen.tsx    # Supabase Auth (magic link + OAuth)
│       └── ReviewScreen.tsx   # Receipt review and submission
├── app.json                    # Expo configuration
├── package.json
└── README.md
```

## Deployment

### Web/PWA (GitHub Pages)

```bash
# Build PWA
npm run build:web

# Deploy to GitHub Pages
# (see .github/workflows/gh-pages.yml)
```

Access at: `https://yourusername.github.io/insightpulse-odoo/`

### Native (EAS Build)

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure project
eas build:configure

# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

## Testing

### Test Magic Link Login

1. Start app: `npm start`
2. Enter email address
3. Click "Send Magic Link"
4. Check email for magic link
5. Click link (opens app and authenticates)

### Test Receipt Upload

1. Login with magic link
2. Capture or select receipt photo
3. Review and submit
4. Check Supabase Dashboard:
   - Storage: `receipts` bucket should have file
   - Database: `receipts` table should have metadata
   - Edge Functions logs: Should show notify-odoo execution
5. Check Odoo: Expense should be created

## Troubleshooting

### Magic Link Not Working

- Check Supabase Auth settings → Email templates
- Verify email provider (SMTP) is configured
- Check redirect URLs in Supabase Auth settings

### Upload Fails

- Check Supabase Storage RLS policies
- Verify user is authenticated
- Check Edge Function logs in Supabase Dashboard
- Verify Odoo API endpoint is accessible

### Edge Function Errors

```bash
# View function logs
supabase functions logs notify-odoo

# Test function locally
supabase functions serve

# Invoke function manually
curl -X POST \
  https://YOUR_PROJECT_REF.supabase.co/functions/v1/notify-odoo \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_path":"test.jpg","user_id":"uuid","file_name":"test.jpg","mime_type":"image/jpeg","file_size":12345}'
```

## Makefile Targets

From project root:

```bash
make supabase-login      # Login to Supabase CLI
make supabase-link       # Link local project
make supabase-push       # Push database migrations
make supabase-deploy     # Deploy Edge Functions
make web                 # Build and serve PWA
```

## License

See main project LICENSE file.
