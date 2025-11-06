"""Mobile receipt upload controller with OCR and Supabase sink."""
import base64
import hashlib
import json
import logging
import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MobileReceiptController(http.Controller):
    """Mobile endpoint for receipt upload → OCR → save."""

    @http.route('/ip/mobile/receipt', type='http', auth='user', methods=['POST'], csrf=False)
    def upload_receipt(self, **kw):
        """
        Upload receipt image, call AI OCR, save to Odoo + Supabase.

        POST multipart/form-data with 'file' field.
        Returns JSON: {success: bool, receipt_id: int, message: str}
        """
        try:
            # 1. Get uploaded file
            uploaded_file = request.httprequest.files.get('file')
            if not uploaded_file:
                return self._json_response({
                    'success': False,
                    'message': 'No file uploaded. Use multipart/form-data with "file" field.'
                }, status=400)

            filename = uploaded_file.filename
            file_data = uploaded_file.read()

            if not file_data:
                return self._json_response({
                    'success': False,
                    'message': 'Empty file uploaded.'
                }, status=400)

            _logger.info("Received receipt upload: %s (%d bytes) from user %s",
                        filename, len(file_data), request.env.user.login)

            # 2. Call AI OCR
            ocr_result = self._call_ocr_api(file_data, filename)
            if not ocr_result:
                return self._json_response({
                    'success': False,
                    'message': 'OCR processing failed. Check AI Inference Hub connectivity.'
                }, status=500)

            # 3. Save to Odoo
            receipt = self._create_odoo_receipt(filename, ocr_result)

            # 4. Sink to Supabase (async, best-effort)
            self._sink_to_supabase(receipt, ocr_result)

            return self._json_response({
                'success': True,
                'receipt_id': receipt.id,
                'line_count': receipt.line_count,
                'avg_confidence': receipt.avg_confidence,
                'message': f'Receipt "{filename}" processed successfully.'
            }, status=201)

        except Exception as e:
            _logger.exception("Failed to process receipt upload")
            return self._json_response({
                'success': False,
                'message': f'Internal error: {str(e)}'
            }, status=500)

    def _call_ocr_api(self, file_data, filename):
        """Call AI Inference Hub OCR endpoint."""
        ocr_url = request.env['ir.config_parameter'].sudo().get_param(
            'ip_expense_mvp.ai_ocr_url',
            'http://127.0.0.1:8100/v1/ocr/receipt'
        )

        try:
            files = {'file': (filename, file_data, 'image/jpeg')}
            response = requests.post(ocr_url, files=files, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error("OCR API call failed: %s", e)
            return None

    def _create_odoo_receipt(self, filename, ocr_result):
        """Create ip.ocr.receipt record."""
        lines = ocr_result.get('lines', [])
        line_count = len(lines)

        # Calculate average confidence
        confidences = [line.get('confidence', 0) for line in lines]
        avg_confidence = (sum(confidences) / len(confidences) * 100) if confidences else 0.0

        # Try to extract total amount (basic heuristic)
        total_amount = self._extract_total_amount(lines)

        vals = {
            'name': filename,
            'filename': filename,
            'uploaded_by': request.env.user.id,
            'ocr_json': json.dumps(ocr_result),
            'line_count': line_count,
            'avg_confidence': avg_confidence,
            'total_amount': total_amount,
            'state': 'processed',
        }

        receipt = request.env['ip.ocr.receipt'].sudo().create(vals)
        _logger.info("Created OCR receipt #%d for %s", receipt.id, filename)
        return receipt

    def _extract_total_amount(self, lines):
        """Simple heuristic to extract total amount from OCR lines."""
        import re
        for line in reversed(lines):  # Start from bottom
            text = line.get('text', '').upper()
            if 'TOTAL' in text or 'AMOUNT' in text:
                # Extract numbers
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    try:
                        return float(numbers[-1])
                    except ValueError:
                        pass
        return 0.0

    def _sink_to_supabase(self, receipt, ocr_result):
        """Send to Supabase analytics (idempotent upsert via RPC)."""
        supabase_url = request.env['ir.config_parameter'].sudo().get_param(
            'ip_expense_mvp.supabase_url'
        )
        supabase_key = request.env['ir.config_parameter'].sudo().get_param(
            'ip_expense_mvp.supabase_service_key'
        )

        if not supabase_url or not supabase_key:
            _logger.warning("Supabase not configured; skipping analytics sink")
            return

        # Generate dedupe key (hash of filename + user + timestamp)
        dedupe_str = f"{receipt.filename}_{receipt.uploaded_by.id}_{receipt.create_date}"
        dedupe_key = hashlib.sha256(dedupe_str.encode()).hexdigest()

        rpc_url = f"{supabase_url.rstrip('/')}/rest/v1/rpc/upsert_ip_ocr_receipt"
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'p_filename': receipt.filename,
            'p_line_count': receipt.line_count,
            'p_total_amount': receipt.total_amount or 0.0,
            'p_currency': receipt.currency_id.name or 'PHP',
            'p_uploaded_by': None,  # UUID not mapped in this MVP
            'p_ocr_json': ocr_result,
            'p_dedupe_key': dedupe_key,
        }

        try:
            resp = requests.post(rpc_url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            _logger.info("Synced receipt #%d to Supabase analytics", receipt.id)
        except requests.RequestException as e:
            _logger.error("Failed to sink to Supabase: %s", e)

    def _json_response(self, data, status=200):
        """Return JSON response with proper headers."""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
            ],
            status=status
        )
