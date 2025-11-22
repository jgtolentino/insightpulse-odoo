/// Configuration for Receipt OCR module
class OcrConfig {
  /// OCR Backend endpoint
  static const String ocrEndpoint = 'https://ocr.insightpulseai.net/ocr';

  /// Mobile API key for OCR endpoint (X-API-KEY header)
  /// NOTE: This should be stored securely, preferably using flutter_secure_storage
  static const String apiKey = 'flutter_client_key_001';

  /// Supabase configuration
  static const String supabaseUrl =
      'https://spdtwktxdalcfigzeqrz.supabase.co';
  static const String supabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwZHR3a3R4ZGFsY2ZpZ3plcXJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk2OTc4ODgsImV4cCI6MjA3NTI3Mzg4OH0.MHwik3WhADRxvSHTwd_4z7-Q6QemBfBmMVU77PRpJBc';

  /// Storage bucket for receipt images
  static const String storageBucket = 'receipt-images';

  /// Database table for parsed receipts
  static const String receiptsTable = 'parsed_receipts';

  /// Rate limit information (for display purposes)
  static const int rateLimitRequests = 100;
  static const int rateLimitWindowHours = 1;
}
