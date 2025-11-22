# Receipt OCR Module for InsightPulse AI

Embeddable Flutter module for OCR-powered receipt scanning with Supabase caching and offline support.

## Features

- **Camera/Gallery Picker**: Capture receipts via camera or select from gallery
- **Document Type Selector**: Auto-detection or manual hint (Receipt, Invoice, Expense Report, Statement)
- **OpenAI Enhancement**: GPT-4o-mini post-processing for intelligent field extraction
- **Supabase Integration**: Automatic caching for offline access
- **Line Item Extraction**: Full line-by-line breakdown with quantities, prices, and VAT
- **Rate Limiting**: 100 requests/hour per API key
- **RLS Security**: Row-Level Security policies ensure data isolation

## Architecture

```
Flutter App → Supabase Storage (image upload)
           → OCR Backend (https://ocr.insightpulseai.net/ocr)
           → OpenAI GPT-4o-mini (structured extraction)
           → Supabase PostgreSQL (caching)
```

## Installation

### As Embeddable Module

Copy the `lib/receipt_ocr/` directory into your Flutter project:

```bash
# In your Flutter project
mkdir -p lib/receipt_ocr
cp -r /path/to/receipt_ocr/lib/receipt_ocr/* lib/receipt_ocr/
```

Add dependencies to `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.2.0
  image_picker: ^1.0.7
  supabase_flutter: ^2.3.0
  path: ^1.8.3
  path_provider: ^2.1.2
```

### As Standalone App

Clone and run directly:

```bash
flutter pub get
flutter run
```

## Usage

### 1. Initialize Supabase

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:receipt_ocr/receipt_ocr.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: OcrConfig.supabaseUrl,
    anonKey: OcrConfig.supabaseAnonKey,
  );

  runApp(MyApp());
}
```

### 2. Create API Client

```dart
final apiClient = OcrApiClient(
  baseUrl: OcrConfig.ocrEndpoint,
  apiKey: OcrConfig.apiKey,
  supabase: Supabase.instance.client,
);
```

### 3. Use the OCR Sheet Widget

```dart
Scaffold(
  body: ReceiptOcrSheet(
    apiClient: apiClient,
    onCompleted: (receipt) {
      print('Vendor: ${receipt.vendorName}');
      print('Total: ${receipt.currency} ${receipt.totalAmount}');
      print('Line items: ${receipt.lineItems.length}');

      // Use parsed data in your app
      _createExpense(receipt);
    },
  ),
)
```

### 4. Work with Cached Receipts

```dart
// Get recent receipts
final cached = await apiClient.getCachedReceipts(limit: 50);

// Get image URL
final imageUrl = apiClient.getReceiptImageUrl(receipt.imagePath);

// Delete receipt
await apiClient.deleteReceipt(receiptId, imagePath);
```

## Configuration

Edit `lib/receipt_ocr/config.dart`:

```dart
class OcrConfig {
  static const String ocrEndpoint = 'https://ocr.insightpulseai.net/ocr';
  static const String apiKey = 'your_api_key_here';  // Get from backend admin

  static const String supabaseUrl = 'https://your-project.supabase.co';
  static const String supabaseAnonKey = 'your_anon_key';

  static const String storageBucket = 'receipt-images';
  static const String receiptsTable = 'parsed_receipts';
}
```

**Security Note**: In production, store API keys securely using `flutter_secure_storage` or environment variables.

## Data Models

### ParsedReceipt

```dart
class ParsedReceipt {
  final String docType;              // receipt, invoice, statement, expense_report
  final String? vendorName;
  final String? vendorAddress;
  final String? invoiceNumber;
  final String? documentDate;
  final String? currency;            // PHP, USD, etc.
  final double? totalAmount;
  final double? subtotalAmount;
  final double? vatAmount;
  final bool? isCredit;
  final List<ReceiptLineItem> lineItems;
  final ReceiptSource? source;
  final ReceiptProcessingMeta? processingMeta;
}
```

### ReceiptLineItem

```dart
class ReceiptLineItem {
  final String description;
  final double? unitPrice;
  final double? quantity;
  final double? lineTotal;
  final double? taxRate;
  final String? category;
}
```

## Backend Integration

### OCR Endpoint

**URL**: `https://ocr.insightpulseai.net/ocr`

**Headers**:
- `X-API-KEY`: Your mobile API key (required)

**Form Data**:
- `file`: Image file (JPEG, PNG)
- `doc_type_hint`: Optional hint (receipt, invoice, statement, expense_report)

**Response**: Unified JSON schema (see [OCR_ENHANCEMENT_COMPLETE.md](../../OCR_ENHANCEMENT_COMPLETE.md))

### Supabase Database

**Table**: `parsed_receipts`

```sql
CREATE TABLE parsed_receipts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  image_path TEXT NOT NULL,
  doc_type TEXT,
  vendor_name TEXT,
  total_amount NUMERIC(10,2),
  subtotal_amount NUMERIC(10,2),
  vat_amount NUMERIC(10,2),
  currency TEXT DEFAULT 'PHP',
  document_date DATE,
  line_items JSONB,
  processing_meta JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id)
);
```

**Storage Bucket**: `receipt-images` (private with RLS)

## Performance

- **OCR Processing**: P95 < 30 seconds
- **Image Upload**: < 2 seconds
- **Cache Retrieval**: < 500ms
- **Offline Support**: Cached receipts available without network

## Testing

### Test Harness

Run the standalone test app:

```bash
flutter run
```

Features:
- Camera/Gallery picker
- Document type selector
- Real-time progress indicator
- Result display with line items
- Cached receipts tab

### Document Types to Test

1. **Simple Receipt**: POS receipt from cafe/restaurant
2. **Complex Invoice**: Utility bill, telco statement
3. **Expense Report**: Cash advance liquidation form
4. **Statement**: Monthly credit card statement

## Troubleshooting

### Authentication Error (401)

```
Invalid or missing API key. Include X-API-KEY header.
```

**Solution**: Verify `OcrConfig.apiKey` is correct and request new key from backend admin.

### Rate Limit (429)

```
Rate limit exceeded. Limit: 100 requests per 1 hour(s)
```

**Solution**: Wait for rate limit window to reset or request higher limit.

### Storage Permission Error

**iOS**: Add to `Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to scan receipts</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>We need photo library access to select receipt images</string>
```

**Android**: Add to `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
```

### Supabase RLS Error

```
Row Level Security policy violation
```

**Solution**: Ensure user is authenticated via `Supabase.instance.client.auth.signIn()`.

## License

Proprietary - InsightPulse AI

## Support

For issues or questions, contact: jgtolentino_rn@yahoo.com
