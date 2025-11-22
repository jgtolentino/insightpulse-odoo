import 'dart:convert';

/// Document type hint enum
enum DocTypeHint {
  auto('Auto'),
  receipt('Receipt'),
  invoice('Invoice'),
  expenseReport('Expense Report'),
  statement('Statement');

  final String label;
  const DocTypeHint(this.label);

  String get apiValue => name == 'auto'
      ? ''
      : name == 'expenseReport'
          ? 'expense_report'
          : name;
}

/// Line item in a receipt
class ReceiptLineItem {
  final String description;
  final double? unitPrice;
  final double? quantity;
  final double? lineTotal;
  final double? taxRate;
  final String? category;

  ReceiptLineItem({
    required this.description,
    this.unitPrice,
    this.quantity,
    this.lineTotal,
    this.taxRate,
    this.category,
  });

  factory ReceiptLineItem.fromJson(Map<String, dynamic> json) {
    return ReceiptLineItem(
      description: json['description']?.toString() ?? '',
      unitPrice: _toDouble(json['unit_price']),
      quantity: _toDouble(json['quantity']),
      lineTotal: _toDouble(json['line_total']),
      taxRate: _toDouble(json['tax_rate']),
      category: json['category']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'description': description,
        'unit_price': unitPrice,
        'quantity': quantity,
        'line_total': lineTotal,
        'tax_rate': taxRate,
        'category': category,
      };

  static double? _toDouble(dynamic value) {
    if (value == null) return null;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }
}

/// Processing metadata from OCR
class ReceiptProcessingMeta {
  final double? ocrConfidence;
  final bool openaiProcessed;
  final String? openaiModel;
  final String? docTypeHint;

  ReceiptProcessingMeta({
    this.ocrConfidence,
    required this.openaiProcessed,
    this.openaiModel,
    this.docTypeHint,
  });

  factory ReceiptProcessingMeta.fromJson(Map<String, dynamic> json) {
    return ReceiptProcessingMeta(
      ocrConfidence: ReceiptLineItem._toDouble(json['ocr_confidence']),
      openaiProcessed: json['openai_processed'] ?? false,
      openaiModel: json['openai_model']?.toString(),
      docTypeHint: json['doc_type_hint']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'ocr_confidence': ocrConfidence,
        'openai_processed': openaiProcessed,
        'openai_model': openaiModel,
        'doc_type_hint': docTypeHint,
      };
}

/// Source metadata
class ReceiptSource {
  final String? fileName;
  final String? ocrEngine;
  final String? language;
  final String? country;

  ReceiptSource({
    this.fileName,
    this.ocrEngine,
    this.language,
    this.country,
  });

  factory ReceiptSource.fromJson(Map<String, dynamic>? json) {
    if (json == null) return ReceiptSource();
    return ReceiptSource(
      fileName: json['file_name']?.toString(),
      ocrEngine: json['ocr_engine']?.toString(),
      language: json['language']?.toString(),
      country: json['country']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'file_name': fileName,
        'ocr_engine': ocrEngine,
        'language': language,
        'country': country,
      };
}

/// Parsed receipt data model (unified JSON schema)
class ParsedReceipt {
  final String docType;
  final String? vendorName;
  final String? vendorAddress;
  final String? vendorTaxId;
  final String? invoiceNumber;
  final String? documentDate;
  final String? currency;
  final double? totalAmount;
  final double? subtotalAmount;
  final double? vatAmount;
  final bool? isCredit;
  final List<ReceiptLineItem> lineItems;
  final ReceiptSource? source;
  final ReceiptProcessingMeta? processingMeta;
  final Map<String, dynamic>? apiInfo;

  ParsedReceipt({
    required this.docType,
    this.vendorName,
    this.vendorAddress,
    this.vendorTaxId,
    this.invoiceNumber,
    this.documentDate,
    this.currency,
    this.totalAmount,
    this.subtotalAmount,
    this.vatAmount,
    this.isCredit,
    this.lineItems = const [],
    this.source,
    this.processingMeta,
    this.apiInfo,
  });

  factory ParsedReceipt.fromJson(Map<String, dynamic> json) {
    final lineItemsJson = json['line_items'] as List<dynamic>? ?? [];
    final lineItems = lineItemsJson
        .map((item) => ReceiptLineItem.fromJson(item as Map<String, dynamic>))
        .toList();

    return ParsedReceipt(
      docType: json['doc_type']?.toString() ?? 'other',
      vendorName: json['vendor_name']?.toString(),
      vendorAddress: json['vendor_address']?.toString(),
      vendorTaxId: json['vendor_tax_id']?.toString(),
      invoiceNumber: json['invoice_number']?.toString(),
      documentDate: json['document_date']?.toString(),
      currency: json['currency']?.toString() ?? 'PHP',
      totalAmount: ReceiptLineItem._toDouble(json['total_amount']),
      subtotalAmount: ReceiptLineItem._toDouble(json['subtotal_amount']),
      vatAmount: ReceiptLineItem._toDouble(json['vat_amount']),
      isCredit: json['is_credit'] as bool?,
      lineItems: lineItems,
      source: ReceiptSource.fromJson(
          json['source'] as Map<String, dynamic>?),
      processingMeta: json['_processing'] != null
          ? ReceiptProcessingMeta.fromJson(
              json['_processing'] as Map<String, dynamic>)
          : null,
      apiInfo: json['_api'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'doc_type': docType,
        'vendor_name': vendorName,
        'vendor_address': vendorAddress,
        'vendor_tax_id': vendorTaxId,
        'invoice_number': invoiceNumber,
        'document_date': documentDate,
        'currency': currency,
        'total_amount': totalAmount,
        'subtotal_amount': subtotalAmount,
        'vat_amount': vatAmount,
        'is_credit': isCredit,
        'line_items': lineItems.map((item) => item.toJson()).toList(),
        'source': source?.toJson(),
        '_processing': processingMeta?.toJson(),
        '_api': apiInfo,
      };

  String toJsonString() => jsonEncode(toJson());
}
