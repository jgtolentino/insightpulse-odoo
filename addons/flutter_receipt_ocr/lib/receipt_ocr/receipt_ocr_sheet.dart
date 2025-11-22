import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import 'ocr_api_client.dart';
import 'parsed_receipt.dart';

/// Embeddable receipt OCR sheet widget
///
/// This widget provides a complete UI for scanning receipts:
/// - Camera/gallery picker
/// - Document type selector
/// - OCR result display with line items
/// - Cached receipts tab
/// - "Use Result" callback for integration
class ReceiptOcrSheet extends StatefulWidget {
  final OcrApiClient apiClient;
  final void Function(ParsedReceipt result)? onCompleted;

  const ReceiptOcrSheet({
    super.key,
    required this.apiClient,
    this.onCompleted,
  });

  @override
  State<ReceiptOcrSheet> createState() => _ReceiptOcrSheetState();
}

class _ReceiptOcrSheetState extends State<ReceiptOcrSheet>
    with SingleTickerProviderStateMixin {
  DocTypeHint _selectedHint = DocTypeHint.auto;
  ParsedReceipt? _result;
  bool _loading = false;
  double _progress = 0.0;
  String? _error;
  List<ParsedReceipt> _cachedReceipts = [];
  late TabController _tabController;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadCachedReceipts();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadCachedReceipts() async {
    final cached = await widget.apiClient.getCachedReceipts();
    setState(() => _cachedReceipts = cached);
  }

  Future<void> _pickAndScan(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image == null) return;

      setState(() {
        _loading = true;
        _error = null;
        _progress = 0.0;
      });

      final result = await widget.apiClient.parseDocument(
        File(image.path),
        docTypeHint: _selectedHint.apiValue,
        onProgress: (progress) {
          setState(() => _progress = progress);
        },
      );

      setState(() {
        _result = result;
        _loading = false;
        _progress = 1.0;
      });

      // Refresh cached receipts
      await _loadCachedReceipts();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'New Scan', icon: Icon(Icons.camera_alt)),
            Tab(text: 'Cached', icon: Icon(Icons.history)),
          ],
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildNewScanTab(),
              _buildCachedTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildNewScanTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Document type selector
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Document Type',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  DropdownButton<DocTypeHint>(
                    value: _selectedHint,
                    isExpanded: true,
                    items: DocTypeHint.values
                        .map((hint) => DropdownMenuItem(
                              value: hint,
                              child: Text(hint.label),
                            ))
                        .toList(),
                    onChanged: _loading
                        ? null
                        : (value) {
                            if (value != null) {
                              setState(() => _selectedHint = value);
                            }
                          },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Camera/Gallery buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _loading
                      ? null
                      : () => _pickAndScan(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _loading
                      ? null
                      : () => _pickAndScan(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Loading indicator
          if (_loading) ...[
            LinearProgressIndicator(value: _progress),
            const SizedBox(height: 8),
            Text(
              'Processing: ${(_progress * 100).toInt()}%',
              textAlign: TextAlign.center,
            ),
          ],

          // Error display
          if (_error != null) ...[
            Card(
              color: Colors.red.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.error, color: Colors.red),
                        SizedBox(width: 8),
                        Text(
                          'Error',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.red,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(_error!),
                  ],
                ),
              ),
            ),
          ],

          // Result display
          if (_result != null) ...[
            const Divider(height: 32),
            _buildResultCard(_result!),
          ],
        ],
      ),
    );
  }

  Widget _buildCachedTab() {
    if (_cachedReceipts.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text(
              'No cached receipts',
              style: TextStyle(fontSize: 18, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _cachedReceipts.length,
      itemBuilder: (context, index) {
        final receipt = _cachedReceipts[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: const Icon(Icons.receipt),
            title: Text(receipt.vendorName ?? 'Unknown Vendor'),
            subtitle: Text(
              '${receipt.currency ?? 'PHP'} ${receipt.totalAmount?.toStringAsFixed(2) ?? '0.00'}\n${receipt.documentDate ?? 'No date'}',
            ),
            trailing: Text(
              receipt.docType.toUpperCase(),
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            onTap: () {
              setState(() => _result = receipt);
              _tabController.animateTo(0);
            },
          ),
        );
      },
    );
  }

  Widget _buildResultCard(ParsedReceipt result) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green),
                const SizedBox(width: 8),
                const Text(
                  'OCR Result',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
                const Spacer(),
                Chip(
                  label: Text(result.docType.toUpperCase()),
                  backgroundColor: Colors.blue.shade100,
                ),
              ],
            ),
            const Divider(),
            _buildInfoRow('Vendor', result.vendorName ?? 'N/A'),
            if (result.vendorAddress != null)
              _buildInfoRow('Address', result.vendorAddress!),
            _buildInfoRow('Invoice #', result.invoiceNumber ?? 'N/A'),
            _buildInfoRow('Date', result.documentDate ?? 'N/A'),
            const Divider(),
            _buildInfoRow(
              'Subtotal',
              '${result.currency ?? 'PHP'} ${result.subtotalAmount?.toStringAsFixed(2) ?? '0.00'}',
            ),
            if (result.vatAmount != null)
              _buildInfoRow(
                'VAT',
                '${result.currency ?? 'PHP'} ${result.vatAmount!.toStringAsFixed(2)}',
              ),
            _buildInfoRow(
              'Total',
              '${result.currency ?? 'PHP'} ${result.totalAmount?.toStringAsFixed(2) ?? '0.00'}',
              isBold: true,
            ),
            if (result.lineItems.isNotEmpty) ...[
              const Divider(),
              const Text(
                'Line Items',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...result.lineItems.map((item) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 3,
                          child: Text(item.description),
                        ),
                        if (item.quantity != null)
                          Expanded(
                            child: Text(
                              '×${item.quantity!.toStringAsFixed(0)}',
                              textAlign: TextAlign.center,
                            ),
                          ),
                        Expanded(
                          flex: 2,
                          child: Text(
                            '${result.currency ?? 'PHP'} ${item.lineTotal?.toStringAsFixed(2) ?? '0.00'}',
                            textAlign: TextAlign.right,
                          ),
                        ),
                      ],
                    ),
                  )),
            ],
            if (result.processingMeta != null) ...[
              const Divider(),
              Text(
                'Confidence: ${(result.processingMeta!.ocrConfidence! * 100).toStringAsFixed(1)}%',
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              if (result.processingMeta!.openaiProcessed)
                Text(
                  'Enhanced with ${result.processingMeta!.openaiModel}',
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
            ],
            if (widget.onCompleted != null) ...[
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => widget.onCompleted!(result),
                  icon: const Icon(Icons.check),
                  label: const Text('Use Result'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: const TextStyle(color: Colors.grey),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: TextStyle(
                fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }
}
