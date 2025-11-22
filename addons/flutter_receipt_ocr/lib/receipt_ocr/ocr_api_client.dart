import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:path/path.dart' as path;

import 'config.dart';
import 'parsed_receipt.dart';

/// OCR API client with Supabase caching
class OcrApiClient {
  final String baseUrl;
  final String apiKey;
  final SupabaseClient supabase;

  OcrApiClient({
    required this.baseUrl,
    required this.apiKey,
    required this.supabase,
  });

  /// Parse document with optional document type hint
  ///
  /// This uploads the image to Supabase Storage, sends it to OCR endpoint,
  /// and caches the result in Supabase database for offline access.
  Future<ParsedReceipt> parseDocument(
    File imageFile, {
    String? docTypeHint,
    Function(double progress)? onProgress,
  }) async {
    try {
      onProgress?.call(0.1);

      // 1. Upload image to Supabase Storage
      final userId = supabase.auth.currentUser?.id;
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final fileName = '${userId}/${DateTime.now().millisecondsSinceEpoch}_${path.basename(imageFile.path)}';

      onProgress?.call(0.2);

      await supabase.storage
          .from(OcrConfig.storageBucket)
          .upload(fileName, imageFile, fileOptions: const FileOptions(
            cacheControl: '3600',
            upsert: false,
          ));

      onProgress?.call(0.4);

      // 2. Call OCR endpoint
      final request = http.MultipartRequest('POST', Uri.parse(baseUrl))
        ..headers['X-API-KEY'] = apiKey
        ..files.add(await http.MultipartFile.fromPath('file', imageFile.path));

      final normalizedHint = (docTypeHint ?? '').trim().toLowerCase();
      if (normalizedHint.isNotEmpty && normalizedHint != 'auto') {
        request.fields['doc_type_hint'] = normalizedHint;
      }

      onProgress?.call(0.5);

      final response = await request.send();
      final body = await response.stream.bytesToString();

      onProgress?.call(0.8);

      if (response.statusCode != 200) {
        throw Exception('OCR failed: ${response.statusCode} $body');
      }

      final json = jsonDecode(body) as Map<String, dynamic>;
      final receipt = ParsedReceipt.fromJson(json);

      // 3. Cache in Supabase database
      await _cacheReceipt(receipt, fileName);

      onProgress?.call(1.0);

      return receipt;
    } catch (e) {
      rethrow;
    }
  }

  /// Cache parsed receipt in Supabase database
  Future<void> _cacheReceipt(ParsedReceipt receipt, String imagePath) async {
    try {
      await supabase.from(OcrConfig.receiptsTable).insert({
        'image_path': imagePath,
        'doc_type': receipt.docType,
        'vendor_name': receipt.vendorName,
        'total_amount': receipt.totalAmount,
        'subtotal_amount': receipt.subtotalAmount,
        'vat_amount': receipt.vatAmount,
        'currency': receipt.currency,
        'document_date': receipt.documentDate,
        'line_items': receipt.lineItems
            .map((item) => {
                  'description': item.description,
                  'unit_price': item.unitPrice,
                  'quantity': item.quantity,
                  'line_total': item.lineTotal,
                  'tax_rate': item.taxRate,
                  'category': item.category,
                })
            .toList(),
        'processing_meta': receipt.processingMeta != null
            ? {
                'ocr_confidence': receipt.processingMeta!.ocrConfidence,
                'openai_processed': receipt.processingMeta!.openaiProcessed,
                'openai_model': receipt.processingMeta!.openaiModel,
                'doc_type_hint': receipt.processingMeta!.docTypeHint,
              }
            : null,
      });
    } catch (e) {
      print('Error caching receipt: $e');
      // Don't throw - caching is not critical
    }
  }

  /// Get cached receipts from Supabase database
  ///
  /// Returns most recent receipts first, limited to [limit] items.
  Future<List<ParsedReceipt>> getCachedReceipts({int limit = 50}) async {
    try {
      final response = await supabase
          .from(OcrConfig.receiptsTable)
          .select()
          .order('created_at', ascending: false)
          .limit(limit);

      return (response as List)
          .map((json) => ParsedReceipt.fromJson(json as Map<String, dynamic>))
          .toList();
    } catch (e) {
      print('Error fetching cached receipts: $e');
      return [];
    }
  }

  /// Get receipt image URL from Supabase Storage
  String? getReceiptImageUrl(String imagePath) {
    try {
      return supabase.storage.from(OcrConfig.storageBucket).getPublicUrl(imagePath);
    } catch (e) {
      print('Error getting image URL: $e');
      return null;
    }
  }

  /// Delete cached receipt and its image
  Future<void> deleteReceipt(String receiptId, String imagePath) async {
    try {
      // Delete from database
      await supabase.from(OcrConfig.receiptsTable).delete().eq('id', receiptId);

      // Delete from storage
      await supabase.storage.from(OcrConfig.storageBucket).remove([imagePath]);
    } catch (e) {
      print('Error deleting receipt: $e');
      rethrow;
    }
  }
}
