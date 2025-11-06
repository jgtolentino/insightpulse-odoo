# InsightPulse Odoo ERP SaaS + Mobile App Deployment Plan

**Date**: 2025-11-06
**Status**: Ready for Production Deployment
**Total Cost**: $37-50/month
**Deployment Time**: ~2-3 hours (backend), ~2-4 weeks (mobile app completion)

---

## 📊 Current Status Summary

### ✅ READY FOR IMMEDIATE DEPLOYMENT

1. **Odoo ERP Backend** (Production-ready)
   - Odoo 19.0 Community Edition
   - Docker image optimized for DO App Platform
   - Database: Supabase PostgreSQL (configured)
   - Deployment spec: `infra/do/odoo-saas-platform.yaml`
   - CI/CD pipeline: `.github/workflows/deploy-unified.yml`
   - Cost: $5/month (basic-xxs tier)

2. **Apache Superset Analytics** (Production-ready)
   - Multi-service architecture (web, worker, beat, redis)
   - Deployment spec: `infra/do/superset-app.yaml`
   - Integration with Odoo database
   - Cost: $27/month

3. **MCP Coordinator** (Production-ready)
   - FastAPI service
   - Deployment spec: `infra/do/mcp-coordinator.yaml`
   - Cost: $5/month

4. **PaddleOCR Service** (Already deployed)
   - URL: ade-ocr-backend-d9dru.ondigitalocean.app
   - FastAPI + PaddleOCR
   - Cost: $6/month (included in existing droplet)

### ⚠️ NEEDS COMPLETION

1. **Mobile App** (Framework ready, features incomplete)
   - ✅ Project structure created
   - ✅ Dependencies configured
   - ✅ Supabase auth service designed
   - ❌ Screens need implementation (40% complete)
   - ❌ Camera + OCR integration incomplete
   - ❌ Offline sync not implemented
   - ❌ EAS Build not configured
   - ❌ App Store deployment pending
   - Estimated: 2-4 weeks to complete

---

## 🚀 Phase 1: Backend Deployment (Immediate - 2-3 hours)

### Step 1.1: Verify GitHub Secrets (15 minutes)

Required secrets in repository settings (Settings → Secrets → Actions):

```bash
# DigitalOcean
DO_APP_ID=<your-odoo-app-id>              # Get from DO dashboard
DO_ACCESS_TOKEN=dop_v1_xxxxx              # Generate from DO API tokens
DIGITALOCEAN_ACCESS_TOKEN=<same-as-above> # Alias for compatibility

# Supabase
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz # Already configured
SUPABASE_ACCESS_TOKEN=sbp_xxxxx            # Generate from Supabase
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... # From Supabase project

# GitHub Container Registry
CR_PAT=ghp_xxxxx                           # Personal access token with packages:write

# Application passwords
SUPERSET_PASSWORD=<secure-password>        # For Superset admin
RAG_REINDEX_TOKEN=<optional-token>         # For RAG system (optional)
```

**How to get these:**

1. **DO_APP_ID**:
   ```bash
   # Install doctl first
   brew install doctl  # macOS
   # OR
   sudo snap install doctl  # Linux

   # Authenticate
   doctl auth init --access-token <YOUR_DO_TOKEN>

   # List apps (if already created) or create new
   doctl apps list
   # OR create new app
   doctl apps create --spec infra/do/odoo-saas-platform.yaml
   ```

2. **DO_ACCESS_TOKEN**: Go to https://cloud.digitalocean.com/account/api/tokens → Generate New Token

3. **SUPABASE_ACCESS_TOKEN**:
   - Go to https://supabase.com/dashboard/account/tokens
   - Click "Generate new token"
   - Copy and save securely

4. **CR_PAT**:
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `write:packages`, `read:packages`, `delete:packages`

### Step 1.2: Deploy Odoo ERP (30 minutes)

**Option A: Via GitHub Actions (Recommended)**

```bash
# Push to main branch to trigger auto-deployment
git add .
git commit -m "Deploy: Odoo ERP SaaS platform v1.0"
git push origin main

# OR manually trigger workflow
gh workflow run deploy-unified.yml
```

**Option B: Manual Deployment**

```bash
# 1. Build and push Docker image
docker build -t ghcr.io/jgtolentino/insightpulse-odoo:latest .
docker push ghcr.io/jgtolentino/insightpulse-odoo:latest

# 2. Create or update DO app
doctl apps create --spec infra/do/odoo-saas-platform.yaml
# OR if app exists
doctl apps update <APP_ID> --spec infra/do/odoo-saas-platform.yaml

# 3. Create deployment
doctl apps create-deployment <APP_ID>

# 4. Monitor deployment
doctl apps deployments list <APP_ID>
doctl apps logs <APP_ID> --type=DEPLOY --follow
```

**Expected Outcome:**
- Odoo accessible at: https://odoo-saas-platform-xxxxx.ondigitalocean.app
- Health check: https://<app-url>/web/health
- Login: https://<app-url>/web/login
  - Admin password: (from ODOO_ADMIN_PASSWORD env var)

### Step 1.3: Configure DNS (10 minutes)

Add CNAME records to point custom domains:

```bash
# In your DNS provider (Namecheap, Cloudflare, etc.)
CNAME  erp          odoo-saas-platform-xxxxx.ondigitalocean.app
CNAME  superset     superset-analytics-xxxxx.ondigitalocean.app
CNAME  mcp          mcp-coordinator-xxxxx.ondigitalocean.app
```

In DigitalOcean App Platform console:
1. Go to app → Settings → Domains
2. Add custom domain: erp.insightpulseai.net
3. DO automatically provisions SSL certificate (5-10 minutes)

### Step 1.4: Deploy Superset Analytics (30 minutes)

```bash
# Option 1: Via GitHub Actions
gh workflow run deploy-superset.yml

# Option 2: Manual via doctl
doctl apps create --spec infra/do/superset-app.yaml

# Wait for deployment
doctl apps deployments list <SUPERSET_APP_ID>
```

**Post-deployment setup:**

```bash
# 1. Access Superset UI
open https://superset.insightpulseai.net

# 2. Login with credentials
# Username: admin
# Password: (from SUPERSET_PASSWORD secret)

# 3. Configure Odoo database connection
# In Superset UI:
# Settings → Database Connections → + Database
#
# SQLAlchemy URI:
# postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres

# 4. Import pre-built dashboards
cd superset/dashboards
# Upload each JSON file via UI: Settings → Import dashboards
```

### Step 1.5: Deploy MCP Coordinator (20 minutes)

```bash
# Deploy via spec
doctl apps create --spec infra/do/mcp-coordinator.yaml

# Verify health
curl https://mcp.insightpulseai.net/health
```

### Step 1.6: Verify Backend Stack (15 minutes)

```bash
# Run comprehensive health checks
./scripts/health-check.sh

# OR manually verify each service
curl -I https://erp.insightpulseai.net/web/health
curl -I https://superset.insightpulseai.net/health
curl -I https://mcp.insightpulseai.net/health

# Test OCR service
curl -X POST https://ade-ocr-backend-d9dru.ondigitalocean.app/v1/ocr \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/receipt.jpg"}'

# Test Odoo API
curl https://erp.insightpulseai.net/web/database/list
```

---

## 📱 Phase 2: Mobile App Completion (2-4 weeks)

### Step 2.1: Complete Core Screens (Week 1)

**File: `mobile-companion/src/screens/LoginScreen.tsx`**

Need to implement:
- OAuth flow with Odoo (`expo-auth-session`)
- Biometric authentication UI
- Error handling and loading states
- Session persistence with `expo-secure-store`

**File: `mobile-companion/src/screens/CameraScreen.tsx`**

Need to implement:
- Camera permission handling
- Photo capture with `expo-camera`
- Image preview and retake
- Image preprocessing (crop, rotate, enhance)
- Upload to Supabase Storage

**File: `mobile-companion/src/screens/ExpenseFormScreen.tsx`**

Need to implement:
- Form fields (amount, date, category, description)
- Auto-fill from OCR results
- Category picker with policy validation
- Attachment display
- Draft saving (offline mode)
- Submit to Odoo API

**File: `mobile-companion/src/screens/DashboardScreen.tsx`**

Need to implement:
- Recent expenses list
- Statistics cards (pending, approved, total)
- Quick action buttons
- Pull-to-refresh
- Navigation to other screens

### Step 2.2: Implement OCR Integration (Week 1)

**File: `mobile-companion/src/services/ocrService.ts`**

```typescript
import { supabase } from '../supabase/client';
import axios from 'axios';

const OCR_API_URL = 'https://ade-ocr-backend-d9dru.ondigitalocean.app/v1/ocr';

export const scanReceipt = async (imageUri: string) => {
  // 1. Upload to Supabase Storage
  const { data: uploadData, error: uploadError } = await supabase.storage
    .from('receipts')
    .upload(`${Date.now()}.jpg`, imageUri);

  if (uploadError) throw uploadError;

  // 2. Get public URL (15-min signed URL)
  const { data: urlData } = await supabase.storage
    .from('receipts')
    .createSignedUrl(uploadData.path, 900);

  // 3. Send to OCR service
  const response = await axios.post(OCR_API_URL, {
    image_url: urlData.signedUrl,
    language: 'en',
  });

  // 4. Parse OCR results
  return {
    merchant: response.data.merchant_name,
    total: parseFloat(response.data.total_amount),
    date: response.data.transaction_date,
    items: response.data.line_items,
    confidence: response.data.confidence_score,
  };
};
```

### Step 2.3: Implement Offline Sync (Week 2)

**File: `mobile-companion/src/store/syncStore.ts`**

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { create } from 'zustand';

interface PendingExpense {
  id: string;
  localId: string;
  data: ExpenseData;
  timestamp: number;
  synced: boolean;
}

interface SyncStore {
  pendingExpenses: PendingExpense[];
  isOnline: boolean;
  addPendingExpense: (expense: ExpenseData) => Promise<void>;
  syncPendingExpenses: () => Promise<void>;
}

export const useSyncStore = create<SyncStore>((set, get) => ({
  pendingExpenses: [],
  isOnline: true,

  addPendingExpense: async (expense) => {
    const pending: PendingExpense = {
      id: '',
      localId: `local-${Date.now()}`,
      data: expense,
      timestamp: Date.now(),
      synced: false,
    };

    // Save to AsyncStorage
    await AsyncStorage.setItem(
      `pending-expense-${pending.localId}`,
      JSON.stringify(pending)
    );

    set((state) => ({
      pendingExpenses: [...state.pendingExpenses, pending],
    }));

    // Try to sync immediately if online
    if (get().isOnline) {
      await get().syncPendingExpenses();
    }
  },

  syncPendingExpenses: async () => {
    const { pendingExpenses, isOnline } = get();
    if (!isOnline || pendingExpenses.length === 0) return;

    for (const pending of pendingExpenses) {
      try {
        // Submit to Odoo API
        const response = await submitExpenseToOdoo(pending.data);

        // Mark as synced
        pending.synced = true;
        pending.id = response.id;

        // Remove from AsyncStorage
        await AsyncStorage.removeItem(`pending-expense-${pending.localId}`);
      } catch (error) {
        console.error('Sync failed:', error);
        // Keep in queue for retry
      }
    }

    // Update state
    set((state) => ({
      pendingExpenses: state.pendingExpenses.filter((e) => !e.synced),
    }));
  },
}));

// Monitor network status
NetInfo.addEventListener((state) => {
  useSyncStore.setState({ isOnline: state.isConnected ?? false });
  if (state.isConnected) {
    useSyncStore.getState().syncPendingExpenses();
  }
});
```

### Step 2.4: Implement Push Notifications (Week 2)

**File: `mobile-companion/src/services/notificationService.ts`**

```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

export const registerForPushNotifications = async () => {
  if (!Device.isDevice) {
    console.log('Push notifications only work on physical devices');
    return;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    throw new Error('Permission not granted for push notifications');
  }

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id', // From app.json
  });

  // Send token to Odoo backend
  await registerDeviceToken(token.data);

  return token.data;
};

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});
```

### Step 2.5: Add Superset Dashboard Embed (Week 3)

**File: `mobile-companion/src/screens/AnalyticsScreen.tsx`**

```typescript
import { WebView } from 'react-native-webview';
import { useAuthStore } from '../store/authStore';

export const AnalyticsScreen = () => {
  const { user } = useAuthStore();

  // Get guest token from Superset API
  const [guestToken, setGuestToken] = useState('');

  useEffect(() => {
    fetchGuestToken();
  }, []);

  const fetchGuestToken = async () => {
    const response = await fetch('https://superset.insightpulseai.net/api/v1/security/guest_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${user.supersetToken}`,
      },
      body: JSON.stringify({
        user: { username: user.email },
        resources: [{ type: 'dashboard', id: '1' }],
        rls: [{ clause: `user_id = ${user.id}` }],
      }),
    });

    const data = await response.json();
    setGuestToken(data.token);
  };

  return (
    <WebView
      source={{
        uri: `https://superset.insightpulseai.net/superset/dashboard/1/?guest_token=${guestToken}&standalone=1`,
      }}
      style={{ flex: 1 }}
      javaScriptEnabled
    />
  );
};
```

### Step 2.6: Configure EAS Build (Week 3)

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure project
cd mobile-companion
eas build:configure

# This creates eas.json
```

**File: `mobile-companion/eas.json`**

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "ios": {
        "bundleIdentifier": "com.insightpulse.expense"
      },
      "android": {
        "buildType": "aab"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@example.com",
        "ascAppId": "your-app-store-connect-id",
        "appleTeamId": "YOUR_TEAM_ID"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "production"
      }
    }
  }
}
```

### Step 2.7: Build and Test (Week 4)

```bash
# Development build
eas build --profile development --platform all

# Preview build
eas build --profile preview --platform all

# Production build
eas build --profile production --platform all

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

---

## 🧪 Phase 3: Integration Testing (1 week)

### Test Checklist

#### Backend Tests
- [ ] Odoo login works
- [ ] Database connection stable
- [ ] Health checks respond (200 OK)
- [ ] Superset dashboards load
- [ ] OCR service processes receipts
- [ ] MCP coordinator responds

#### Mobile App Tests
- [ ] OAuth login flow completes
- [ ] Camera captures photos
- [ ] OCR extracts receipt data correctly
- [ ] Expense form submits to Odoo
- [ ] Offline mode saves drafts
- [ ] Background sync works when online
- [ ] Push notifications arrive
- [ ] Superset dashboard loads in WebView
- [ ] Biometric auth works (Face ID/Touch ID)

#### End-to-End Tests
1. Mobile app → Camera → OCR → Expense Form → Submit → Odoo backend
2. Odoo backend → Process expense → Update database → Notify user
3. Superset dashboard → Query Odoo database → Display analytics
4. Offline: Save expense → Go online → Auto-sync → Verify in Odoo

---

## 💰 Cost Breakdown

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Odoo ERP | DO App Platform (basic-xxs) | $5 |
| Superset Web | DO App Platform (basic-xs) | $12 |
| Superset Worker | DO App Platform (basic-xxs) | $5 |
| Superset Beat | DO App Platform (basic-xxs) | $5 |
| Superset Redis | DO App Platform (basic-xxs) | $5 |
| MCP Coordinator | DO App Platform (basic-xxs) | $5 |
| PaddleOCR | DO Droplet (existing) | $6 |
| Supabase Database | Free tier | $0 |
| Expo/EAS Build | Free tier | $0 |
| **TOTAL** | | **$43/month** |

---

## 🎯 Next Actions

### Immediate (Today)
1. Set up GitHub Secrets
2. Deploy Odoo ERP backend
3. Configure DNS
4. Verify health checks

### This Week
1. Deploy Superset analytics
2. Deploy MCP coordinator
3. Test backend integration
4. Begin mobile app implementation

### Next 2-4 Weeks
1. Complete mobile app screens
2. Implement OCR integration
3. Add offline sync
4. Configure EAS Build
5. Submit to App Stores

---

## 📚 Documentation References

- Deployment Architecture: `infra/UNIFIED_DEPLOYMENT_ARCHITECTURE.md`
- Mobile App Specification: `infra/mobile/MOBILE_APP_SPECIFICATION.md`
- DO Secrets Setup: `infra/do/SECRETS_SETUP.md`
- DNS Configuration: `infra/DNS_CONFIGURATION.md`
- CI/CD Pipeline: `.github/workflows/deploy-unified.yml`

---

## ⚠️ Important Notes

1. **Database Password**: Change `ODOO_DB_PASSWORD` in production
2. **Admin Password**: Change `ODOO_ADMIN_PASSWORD` to strong password
3. **Secrets**: NEVER commit secrets to git
4. **Backups**: Set up automated backups for Supabase
5. **Monitoring**: Configure Prometheus/Grafana after deployment
6. **SSL**: DO automatically provisions Let's Encrypt certificates
7. **Rate Limiting**: Configure rate limits in DO dashboard
8. **Scaling**: Monitor resource usage, scale up if needed

---

## 🆘 Troubleshooting

### Odoo won't start
- Check logs: `doctl apps logs <APP_ID> --type=RUN --follow`
- Verify database connection in env vars
- Check health endpoint: `/web/health`

### Mobile app build fails
- Verify expo dependencies: `npm install`
- Check Expo CLI version: `eas --version`
- Clear build cache: `eas build --clear-cache`

### OCR service errors
- Verify endpoint: `curl https://ade-ocr-backend-d9dru.ondigitalocean.app/health`
- Check image URL is publicly accessible
- Verify image format (JPEG/PNG)

### Superset connection fails
- Verify database URL in Superset settings
- Check Supabase pooler port (6543)
- Test connection string with `psql`

---

**Last Updated**: 2025-11-06
**Maintained By**: InsightPulse DevOps Team
