import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'receipt_ocr.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase
  await Supabase.initialize(
    url: OcrConfig.supabaseUrl,
    anonKey: OcrConfig.supabaseAnonKey,
  );

  runApp(const ReceiptOcrApp());
}

class ReceiptOcrApp extends MaterialApp {
  const ReceiptOcrApp({super.key})
      : super(
          title: 'Receipt OCR Test',
          home: const ReceiptOcrTestScreen(),
          theme: const ThemeData(
            primarySwatch: Colors.blue,
            useMaterial3: true,
          ),
        );
}

class ReceiptOcrTestScreen extends StatefulWidget {
  const ReceiptOcrTestScreen({super.key});

  @override
  State<ReceiptOcrTestScreen> createState() => _ReceiptOcrTestScreenState();
}

class _ReceiptOcrTestScreenState extends State<ReceiptOcrTestScreen> {
  late OcrApiClient _apiClient;
  ParsedReceipt? _lastResult;

  @override
  void initState() {
    super.initState();
    _apiClient = OcrApiClient(
      baseUrl: OcrConfig.ocrEndpoint,
      apiKey: OcrConfig.apiKey,
      supabase: Supabase.instance.client,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Receipt OCR Test Harness'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            onPressed: _showInfo,
          ),
        ],
      ),
      body: Column(
        children: [
          if (_lastResult != null)
            Container(
              color: Colors.green.shade50,
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: Colors.green),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Last scan: ${_lastResult!.vendorName} - ${_lastResult!.currency} ${_lastResult!.totalAmount?.toStringAsFixed(2)}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => setState(() => _lastResult = null),
                  ),
                ],
              ),
            ),
          Expanded(
            child: ReceiptOcrSheet(
              apiClient: _apiClient,
              onCompleted: (result) {
                setState(() => _lastResult = result);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Parsed: ${result.vendorName} - ${result.currency} ${result.totalAmount?.toStringAsFixed(2)}',
                    ),
                    backgroundColor: Colors.green,
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _showInfo() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Receipt OCR Info'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildInfoRow('OCR Endpoint', OcrConfig.ocrEndpoint),
              _buildInfoRow('Supabase Project', OcrConfig.supabaseUrl),
              _buildInfoRow('Storage Bucket', OcrConfig.storageBucket),
              _buildInfoRow('Rate Limit', '${OcrConfig.rateLimitRequests} requests / ${OcrConfig.rateLimitWindowHours}h'),
              const Divider(),
              const Text(
                'Features:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('• Camera/Gallery picker'),
              const Text('• Document type selector'),
              const Text('• OpenAI GPT-4o-mini enhancement'),
              const Text('• Supabase caching'),
              const Text('• Offline access'),
              const Text('• Line item extraction'),
              const Text('• VAT calculation'),
              const Divider(),
              const Text(
                'Supported Document Types:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text('• Receipts (POS, small vendors)'),
              const Text('• Invoices (utilities, telco)'),
              const Text('• Statements (monthly bills)'),
              const Text('• Expense Reports (cash advance)'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}
