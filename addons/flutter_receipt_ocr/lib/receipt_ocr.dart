/// Receipt OCR Module for InsightPulse AI
///
/// This module provides OCR capabilities for receipts, invoices, and expense reports
/// with Supabase caching for offline access.
///
/// ## Usage
///
/// ```dart
/// import 'package:receipt_ocr/receipt_ocr.dart';
/// import 'package:supabase_flutter/supabase_flutter.dart';
///
/// // Initialize Supabase
/// await Supabase.initialize(
///   url: OcrConfig.supabaseUrl,
///   anonKey: OcrConfig.supabaseAnonKey,
/// );
///
/// // Create API client
/// final apiClient = OcrApiClient(
///   baseUrl: OcrConfig.ocrEndpoint,
///   apiKey: OcrConfig.apiKey,
///   supabase: Supabase.instance.client,
/// );
///
/// // Use the OCR sheet widget
/// ReceiptOcrSheet(
///   apiClient: apiClient,
///   onCompleted: (receipt) {
///     print('Parsed: ${receipt.vendorName} - ${receipt.totalAmount}');
///   },
/// );
/// ```
library receipt_ocr;

export 'receipt_ocr/config.dart';
export 'receipt_ocr/parsed_receipt.dart';
export 'receipt_ocr/ocr_api_client.dart';
export 'receipt_ocr/receipt_ocr_sheet.dart';
