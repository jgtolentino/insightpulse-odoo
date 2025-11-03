# InsightPulse Mobile App - Technical Specification

**Version**: 1.0.0
**Platform**: React Native + Expo
**Target**: iOS 14+ / Android 10+
**Repository**: https://github.com/jgtolentino/insightpulse-mobile

---

## 🎯 Overview

Mobile application for InsightPulse platform enabling:
- Expense submission with OCR receipt scanning
- Real-time expense tracking and approval
- Embedded Superset dashboard analytics
- Offline mode with background sync
- Push notifications for approvals

---

## 🏗️ Architecture

### Technology Stack

```json
{
  "framework": "React Native 0.72+",
  "platform": "Expo SDK 50+",
  "language": "TypeScript 5.0+",
  "navigation": "React Navigation 6.x",
  "state": "Zustand 4.x",
  "api": "Axios + React Query 5.x",
  "camera": "expo-camera",
  "storage": "AsyncStorage",
  "auth": "expo-auth-session",
  "notifications": "expo-notifications",
  "analytics": "expo-analytics"
}
```

### App Structure

```
insightpulse-mobile/
├── app/
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/
│   │   ├── index.tsx          # Dashboard
│   │   ├── expenses.tsx       # Expense list
│   │   ├── camera.tsx         # OCR capture
│   │   ├── analytics.tsx      # Superset embed
│   │   └── profile.tsx        # User settings
│   └── _layout.tsx
├── components/
│   ├── ExpenseCard.tsx
│   ├── CameraView.tsx
│   ├── OCRResult.tsx
│   └── SupersetEmbed.tsx
├── services/
│   ├── authService.ts         # OAuth + JWT
│   ├── ocrService.ts          # PaddleOCR integration
│   ├── expenseService.ts      # Odoo API
│   └── analyticsService.ts    # Superset API
├── store/
│   ├── authStore.ts
│   ├── expenseStore.ts
│   └── syncStore.ts
├── utils/
│   ├── api.ts
│   ├── storage.ts
│   └── validation.ts
└── app.json
```

---

## 🔑 Core Features

### 1. Authentication

**OAuth 2.0 Flow with Odoo**

```typescript
// services/authService.ts
import * as AuthSession from 'expo-auth-session';
import { makeRedirectUri } from 'expo-auth-session';

const discovery = {
  authorizationEndpoint: 'https://insightpulseai.net/odoo/oauth2/authorize',
  tokenEndpoint: 'https://insightpulseai.net/odoo/oauth2/token',
};

export const login = async () => {
  const redirectUri = makeRedirectUri({ scheme: 'insightpulse' });

  const authRequest = new AuthSession.AuthRequest({
    clientId: process.env.EXPO_PUBLIC_ODOO_CLIENT_ID,
    scopes: ['userinfo', 'expense.read', 'expense.write'],
    redirectUri,
  });

  const result = await authRequest.promptAsync(discovery);

  if (result.type === 'success') {
    const { code } = result.params;
    const tokens = await exchangeCodeForToken(code);
    await storeTokens(tokens);
    return tokens;
  }
};

export const refreshToken = async (refresh: string) => {
  const response = await axios.post(
    'https://insightpulseai.net/odoo/oauth2/token',
    {
      grant_type: 'refresh_token',
      refresh_token: refresh,
      client_id: process.env.EXPO_PUBLIC_ODOO_CLIENT_ID,
      client_secret: process.env.EXPO_PUBLIC_ODOO_CLIENT_SECRET,
    }
  );
  return response.data;
};
```

**Features**:
- Biometric authentication (Face ID / Fingerprint)
- Auto-refresh JWT tokens
- Secure token storage (Keychain/Keystore)
- Session timeout (30 minutes)

---

### 2. Camera & OCR Integration

**Receipt Scanning Flow**

```typescript
// components/CameraView.tsx
import { Camera } from 'expo-camera';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';

export const CameraView = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const cameraRef = useRef<Camera>(null);

  const takePicture = async () => {
    if (!cameraRef.current) return;

    const photo = await cameraRef.current.takePictureAsync({
      quality: 0.8,
      base64: true,
    });

    // Preprocess image
    const processed = await manipulateAsync(
      photo.uri,
      [
        { resize: { width: 1024 } },
        { rotate: 0 },
      ],
      { compress: 0.8, format: SaveFormat.JPEG }
    );

    // Send to OCR service
    const ocrResult = await ocrService.scanReceipt(processed.uri);

    // Navigate to expense form with pre-filled data
    navigation.navigate('ExpenseForm', { ocrData: ocrResult });
  };

  return (
    <Camera
      ref={cameraRef}
      style={styles.camera}
      type={Camera.Constants.Type.back}
    >
      <View style={styles.buttonContainer}>
        <TouchableOpacity onPress={takePicture}>
          <Text style={styles.text}>Capture Receipt</Text>
        </TouchableOpacity>
      </View>
    </Camera>
  );
};
```

**OCR Service Integration**

```typescript
// services/ocrService.ts
import * as FileSystem from 'expo-file-system';

export const scanReceipt = async (imageUri: string): Promise<OCRResult> => {
  const formData = new FormData();
  formData.append('file', {
    uri: imageUri,
    type: 'image/jpeg',
    name: 'receipt.jpg',
  } as any);

  const response = await axios.post(
    'https://ade-ocr-backend-d9dru.ondigitalocean.app/api/v1/ocr/scan',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-API-Key': process.env.EXPO_PUBLIC_OCR_API_KEY,
      },
    }
  );

  return {
    vendor: response.data.merchant_name,
    date: response.data.date,
    amount: response.data.total_amount,
    currency: response.data.currency || 'USD',
    taxAmount: response.data.tax_amount,
    items: response.data.line_items || [],
    confidence: response.data.confidence,
    rawData: response.data,
  };
};
```

**Features**:
- Auto-focus and flash control
- Image preprocessing (rotation, crop, enhance)
- Confidence scoring
- Multi-language support
- Receipt history with re-scan option

---

### 3. Expense Management

**Expense Submission**

```typescript
// services/expenseService.ts
export const submitExpense = async (expenseData: ExpenseData) => {
  const response = await apiClient.post('/api/v1/expenses', {
    name: expenseData.description,
    employee_id: getCurrentUserId(),
    product_id: expenseData.category,
    unit_amount: expenseData.amount,
    quantity: 1,
    date: expenseData.date,
    payment_mode: expenseData.paymentMode,
    reference: expenseData.receiptNumber,
    attachment_ids: [
      {
        name: 'receipt.jpg',
        datas: expenseData.receiptBase64,
        mimetype: 'image/jpeg',
      },
    ],
    // OCR metadata
    ocr_vendor: expenseData.vendor,
    ocr_confidence: expenseData.confidence,
    ocr_raw_data: expenseData.ocrRawData,
  });

  return response.data;
};

export const getExpenses = async (filters?: ExpenseFilters) => {
  const params = {
    limit: filters?.limit || 20,
    offset: filters?.offset || 0,
    state: filters?.status,
    date_from: filters?.dateFrom,
    date_to: filters?.dateTo,
  };

  const response = await apiClient.get('/api/v1/expenses', { params });
  return response.data;
};
```

**Expense Form Component**

```typescript
// components/ExpenseForm.tsx
export const ExpenseForm = ({ ocrData }: { ocrData?: OCRResult }) => {
  const [formData, setFormData] = useState({
    description: ocrData?.vendor || '',
    amount: ocrData?.amount || 0,
    date: ocrData?.date || new Date(),
    category: '',
    paymentMode: 'own_account',
    receiptUri: '',
  });

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await expenseService.submitExpense(formData);
      Toast.show('Expense submitted successfully');
      navigation.goBack();
    } catch (error) {
      Toast.show('Failed to submit expense');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView>
      <TextInput
        label="Description"
        value={formData.description}
        onChangeText={(text) => setFormData({ ...formData, description: text })}
      />
      <TextInput
        label="Amount"
        value={formData.amount.toString()}
        keyboardType="numeric"
        onChangeText={(text) => setFormData({ ...formData, amount: parseFloat(text) })}
      />
      <DatePicker
        label="Date"
        value={formData.date}
        onChange={(date) => setFormData({ ...formData, date })}
      />
      {/* Category, Payment Mode, etc. */}
      <Button mode="contained" onPress={handleSubmit} loading={loading}>
        Submit Expense
      </Button>
    </ScrollView>
  );
};
```

**Features**:
- Pre-filled from OCR data
- Attachment management
- Category auto-suggestion
- Policy validation
- Draft save (offline mode)

---

### 4. Offline Mode & Sync

**Offline Storage Strategy**

```typescript
// store/syncStore.ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SyncState {
  pendingExpenses: Expense[];
  syncQueue: SyncItem[];
  lastSyncTime: number;
  isOnline: boolean;
  addPendingExpense: (expense: Expense) => void;
  syncPendingExpenses: () => Promise<void>;
}

export const useSyncStore = create<SyncState>()(
  persist(
    (set, get) => ({
      pendingExpenses: [],
      syncQueue: [],
      lastSyncTime: 0,
      isOnline: true,

      addPendingExpense: (expense) => {
        set((state) => ({
          pendingExpenses: [...state.pendingExpenses, expense],
        }));
      },

      syncPendingExpenses: async () => {
        const { pendingExpenses } = get();
        const synced: string[] = [];

        for (const expense of pendingExpenses) {
          try {
            await expenseService.submitExpense(expense);
            synced.push(expense.id);
          } catch (error) {
            console.error('Failed to sync expense:', expense.id);
          }
        }

        set((state) => ({
          pendingExpenses: state.pendingExpenses.filter(
            (e) => !synced.includes(e.id)
          ),
          lastSyncTime: Date.now(),
        }));
      },
    }),
    {
      name: 'sync-storage',
      storage: AsyncStorage,
    }
  )
);
```

**Network Detection & Auto-Sync**

```typescript
// hooks/useNetworkStatus.ts
import NetInfo from '@react-native-community/netinfo';

export const useNetworkStatus = () => {
  const { setSyncState } = useSyncStore();

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      const isOnline = state.isConnected && state.isInternetReachable;
      setSyncState({ isOnline });

      if (isOnline) {
        // Auto-sync when connection is restored
        useSyncStore.getState().syncPendingExpenses();
      }
    });

    return () => unsubscribe();
  }, []);
};
```

**Features**:
- Offline expense creation
- Background sync when online
- Conflict resolution
- Sync status indicators
- Manual sync trigger

---

### 5. Superset Dashboard Embed

**WebView Integration**

```typescript
// components/SupersetEmbed.tsx
import { WebView } from 'react-native-webview';

export const SupersetEmbed = ({ dashboardId }: { dashboardId: string }) => {
  const { accessToken } = useAuthStore();
  const [guestToken, setGuestToken] = useState('');

  useEffect(() => {
    fetchGuestToken();
  }, [dashboardId]);

  const fetchGuestToken = async () => {
    const response = await axios.post(
      'https://insightpulseai.net/superset/api/v1/security/guest_token',
      {
        user: {
          username: 'mobile_user',
          first_name: 'Mobile',
          last_name: 'User',
        },
        resources: [
          {
            type: 'dashboard',
            id: dashboardId,
          },
        ],
        rls: [
          {
            clause: `employee_id = ${getCurrentUserId()}`,
          },
        ],
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );

    setGuestToken(response.data.token);
  };

  const embedUrl = `https://insightpulseai.net/superset/embedded/${dashboardId}?guest_token=${guestToken}`;

  return (
    <WebView
      source={{ uri: embedUrl }}
      style={{ flex: 1 }}
      javaScriptEnabled
      domStorageEnabled
      startInLoadingState
      renderLoading={() => <ActivityIndicator />}
    />
  );
};
```

**Features**:
- Authenticated embed with guest tokens
- Row-level security (RLS)
- Interactive charts and filters
- Full-screen mode
- Share dashboard snapshots

---

### 6. Push Notifications

**Expo Notifications Setup**

```typescript
// services/notificationService.ts
import * as Notifications from 'expo-notifications';
import Constants from 'expo-constants';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export const registerForPushNotifications = async () => {
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    return null;
  }

  const token = (await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas.projectId,
  })).data;

  // Register token with Odoo backend
  await apiClient.post('/api/v1/users/register-device', {
    push_token: token,
    platform: Platform.OS,
  });

  return token;
};

export const listenForNotifications = () => {
  // Notification received while app is in foreground
  Notifications.addNotificationReceivedListener((notification) => {
    console.log('Notification received:', notification);
  });

  // User tapped on notification
  Notifications.addNotificationResponseReceivedListener((response) => {
    const data = response.notification.request.content.data;

    if (data.type === 'expense_approved') {
      navigation.navigate('ExpenseDetail', { id: data.expense_id });
    } else if (data.type === 'approval_required') {
      navigation.navigate('Approvals', { id: data.approval_id });
    }
  });
};
```

**Notification Types**:
- Expense approved/rejected
- Approval required
- Payment processed
- Budget alerts
- Policy violations

---

## 🎨 UI/UX Design

### Design System

```typescript
// theme/colors.ts
export const colors = {
  primary: '#0066CC',
  secondary: '#00CC66',
  accent: '#FF6B35',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  text: '#212121',
  textSecondary: '#757575',
  border: '#E0E0E0',
  error: '#D32F2F',
  success: '#388E3C',
  warning: '#F57C00',
};

// theme/spacing.ts
export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

// theme/typography.ts
export const typography = {
  h1: { fontSize: 32, fontWeight: 'bold' },
  h2: { fontSize: 24, fontWeight: 'bold' },
  h3: { fontSize: 20, fontWeight: '600' },
  body1: { fontSize: 16, fontWeight: 'normal' },
  body2: { fontSize: 14, fontWeight: 'normal' },
  caption: { fontSize: 12, fontWeight: 'normal' },
};
```

### Screen Mockups

**Dashboard Screen**:
```
┌─────────────────────────────────┐
│  ☰  InsightPulse         🔔 👤 │
├─────────────────────────────────┤
│                                 │
│  Quick Stats                    │
│  ┌──────┐ ┌──────┐ ┌──────┐   │
│  │ $450 │ │  12  │ │  3   │   │
│  │ Spent│ │ Exp. │ │Pend. │   │
│  └──────┘ └──────┘ └──────┘   │
│                                 │
│  Recent Expenses                │
│  ┌───────────────────────────┐ │
│  │ 🍽️  Lunch Meeting         │ │
│  │ $45.00  •  Approved       │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ ✈️  Flight to NYC         │ │
│  │ $280.00  •  Pending       │ │
│  └───────────────────────────┘ │
│                                 │
│  [+] New Expense                │
└─────────────────────────────────┘
```

**Camera Screen**:
```
┌─────────────────────────────────┐
│  ← Scan Receipt                 │
├─────────────────────────────────┤
│                                 │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │       [Camera View]       │ │
│  │                           │ │
│  │       [Viewfinder]        │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                 │
│  Tips:                          │
│  • Align receipt in frame       │
│  • Ensure good lighting         │
│  • Keep steady                  │
│                                 │
│          [📸 Capture]           │
│        [🖼️ Gallery]            │
└─────────────────────────────────┘
```

---

## 📱 Platform-Specific Configurations

### iOS (app.json)

```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.insightpulse.app",
      "buildNumber": "1.0.0",
      "supportsTablet": true,
      "infoPlist": {
        "NSCameraUsageDescription": "This app needs access to your camera to scan receipts.",
        "NSPhotoLibraryUsageDescription": "This app needs access to your photo library to upload receipts.",
        "NSFaceIDUsageDescription": "This app uses Face ID for secure authentication."
      },
      "config": {
        "usesNonExemptEncryption": false
      }
    }
  }
}
```

### Android (app.json)

```json
{
  "expo": {
    "android": {
      "package": "com.insightpulse.app",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#0066CC"
      },
      "permissions": [
        "CAMERA",
        "READ_EXTERNAL_STORAGE",
        "WRITE_EXTERNAL_STORAGE",
        "VIBRATE",
        "USE_BIOMETRIC",
        "USE_FINGERPRINT"
      ]
    }
  }
}
```

---

## 🧪 Testing Strategy

### Unit Tests (Jest)

```typescript
// __tests__/services/ocrService.test.ts
import { scanReceipt } from '../../services/ocrService';

describe('OCR Service', () => {
  it('should parse receipt data correctly', async () => {
    const mockImage = 'mock-image-uri';
    const result = await scanReceipt(mockImage);

    expect(result).toHaveProperty('vendor');
    expect(result).toHaveProperty('amount');
    expect(result).toHaveProperty('date');
    expect(result.confidence).toBeGreaterThan(0.8);
  });
});
```

### Integration Tests (Detox)

```typescript
// e2e/expense-submission.e2e.ts
describe('Expense Submission Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  it('should submit expense via camera', async () => {
    await element(by.id('camera-tab')).tap();
    await element(by.id('capture-button')).tap();
    await waitFor(element(by.id('expense-form')))
      .toBeVisible()
      .withTimeout(2000);

    await element(by.id('submit-button')).tap();
    await expect(element(by.text('Expense submitted successfully')))
      .toBeVisible();
  });
});
```

---

## 🚀 Build & Deployment

### Development Build

```bash
# Install dependencies
npm install

# Start Expo dev server
npx expo start

# Run on iOS simulator
npx expo run:ios

# Run on Android emulator
npx expo run:android
```

### Production Build (EAS)

```bash
# Configure EAS
eas build:configure

# Build for iOS
eas build --platform ios --profile production

# Build for Android
eas build --platform android --profile production

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

### CI/CD (GitHub Actions)

```yaml
# .github/workflows/mobile-build.yml
name: Mobile App Build

on:
  push:
    branches: [main]
    paths:
      - 'mobile/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build with EAS
        run: |
          npx eas-cli build --platform all --non-interactive
        env:
          EXPO_TOKEN: ${{ secrets.EXPO_TOKEN }}
```

---

## 📊 Analytics & Monitoring

### Expo Analytics

```typescript
// utils/analytics.ts
import * as Analytics from 'expo-firebase-analytics';

export const logEvent = (name: string, params?: Record<string, any>) => {
  Analytics.logEvent(name, params);
};

export const logScreenView = (screenName: string) => {
  Analytics.setCurrentScreen(screenName);
};

// Usage
logEvent('expense_submitted', {
  amount: 45.0,
  category: 'Meals',
  has_ocr: true,
});
```

### Error Tracking (Sentry)

```typescript
// utils/errorTracking.ts
import * as Sentry from 'sentry-expo';

Sentry.init({
  dsn: process.env.EXPO_PUBLIC_SENTRY_DSN,
  enableInExpoDevelopment: false,
  debug: __DEV__,
});

export const captureException = (error: Error) => {
  Sentry.Native.captureException(error);
};
```

---

## 🔒 Security Checklist

- [x] SSL pinning for API calls
- [x] Secure token storage (Keychain/Keystore)
- [x] Code obfuscation
- [x] Root/jailbreak detection
- [x] Input validation
- [x] XSS prevention
- [x] API rate limiting
- [x] Biometric authentication
- [x] Session timeout
- [x] Encrypted offline storage

---

## 📞 Support & Resources

- **Documentation**: `/docs/mobile-app-guide.md`
- **API Reference**: `/docs/api-reference.md`
- **Expo Docs**: https://docs.expo.dev/
- **React Native Docs**: https://reactnative.dev/

---

**Last Updated**: 2025-11-02
**Status**: ✅ Specification Complete
**Next Steps**: Repository creation and initial setup
