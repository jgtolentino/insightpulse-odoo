#!/usr/bin/env python3
"""
Receipt Test Harness - Automated OCR Quality Testing

Usage:
    python test-harness.py --images ./test_receipts --ground-truth ground_truth.csv --api-url https://ocr.insightpulseai.net/api/expense/ocr --api-key YOUR_KEY

Ground truth CSV format:
    file_name,vendor,date,total,currency
    jollibee_001.jpg,Jollibee,2025-11-15,345.50,PHP
    711_receipt.jpg,7-Eleven,2025-11-18,89.00,PHP
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from tabulate import tabulate


class GroundTruth:
    """Ground truth data for a single receipt"""
    def __init__(self, file_name: str, vendor: str, date: str, total: float, currency: str):
        self.file_name = file_name
        self.vendor = vendor
        self.date = date
        self.total = total
        self.currency = currency


class OcrResult:
    """OCR extraction result"""
    def __init__(self, vendor: str, date: str, total: float, currency: str, duration_ms: int):
        self.vendor = vendor
        self.date = date
        self.total = total
        self.currency = currency
        self.duration_ms = duration_ms


class TestHarness:
    """Receipt OCR test harness"""

    def __init__(self, api_url: str, api_key: Optional[str] = None, timeout: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.results = []

    def load_ground_truth(self, csv_path: str) -> Dict[str, GroundTruth]:
        """Load ground truth from CSV file"""
        ground_truth = {}
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                gt = GroundTruth(
                    file_name=row['file_name'],
                    vendor=row['vendor'],
                    date=row['date'],
                    total=float(row['total']),
                    currency=row['currency']
                )
                ground_truth[gt.file_name] = gt
        return ground_truth

    def call_ocr(self, image_path: Path) -> Optional[OcrResult]:
        """Call OCR API for single image"""
        start_time = time.time()

        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/jpeg')}
                headers = {}
                if self.api_key:
                    headers['X-API-Key'] = self.api_key

                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(self.api_url, files=files, headers=headers)
                    response.raise_for_status()
                    data = response.json()

            duration_ms = int((time.time() - start_time) * 1000)

            return OcrResult(
                vendor=data.get('merchant_name', ''),
                date=data.get('invoice_date', ''),
                total=float(data.get('total_amount', 0.0)),
                currency=data.get('currency', ''),
                duration_ms=duration_ms
            )

        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {e}")
            return None

    def compare(self, gt: GroundTruth, result: Optional[OcrResult]) -> Dict:
        """Compare ground truth vs OCR result"""
        if result is None:
            return {
                'file': gt.file_name,
                'vendor_match': False,
                'date_match': False,
                'total_match': False,
                'currency_match': False,
                'total_close': False,
                'duration_ms': 0,
                'error': 'OCR failed'
            }

        # Exact matches
        vendor_match = result.vendor.lower().strip() == gt.vendor.lower().strip()
        date_match = result.date == gt.date
        total_match = abs(result.total - gt.total) < 0.01
        currency_match = result.currency == gt.currency

        # "Close enough" for amounts (±1 peso)
        total_close = abs(result.total - gt.total) <= 1.0

        return {
            'file': gt.file_name,
            'vendor_match': vendor_match,
            'date_match': date_match,
            'total_match': total_match,
            'currency_match': currency_match,
            'total_close': total_close,
            'duration_ms': result.duration_ms,
            'gt_vendor': gt.vendor,
            'extracted_vendor': result.vendor,
            'gt_total': gt.total,
            'extracted_total': result.total,
            'gt_date': gt.date,
            'extracted_date': result.date,
        }

    def run_tests(self, images_dir: Path, ground_truth: Dict[str, GroundTruth]):
        """Run OCR tests on all images"""
        print(f"\n🧪 Running OCR Test Harness")
        print(f"   API: {self.api_url}")
        print(f"   Images: {images_dir}")
        print(f"   Ground Truth: {len(ground_truth)} receipts\n")

        for file_name, gt in ground_truth.items():
            image_path = images_dir / file_name

            if not image_path.exists():
                print(f"⚠️  Image not found: {file_name}")
                self.results.append({
                    'file': file_name,
                    'error': 'File not found',
                    'vendor_match': False,
                    'date_match': False,
                    'total_match': False,
                    'currency_match': False,
                    'total_close': False,
                    'duration_ms': 0
                })
                continue

            print(f"📷 Processing: {file_name}")
            result = self.call_ocr(image_path)
            comparison = self.compare(gt, result)
            self.results.append(comparison)

            # Print quick status
            status = "✅" if (comparison['vendor_match'] and comparison['total_match']) else "⚠️"
            print(f"   {status} Vendor: {comparison.get('extracted_vendor', 'N/A')} | Total: {comparison.get('extracted_total', 0.0)} | {comparison['duration_ms']}ms\n")

    def generate_report(self):
        """Generate summary report"""
        if not self.results:
            print("No results to report")
            return

        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r['vendor_match'] and r['total_match'])

        # Field-wise accuracy
        vendor_correct = sum(1 for r in self.results if r['vendor_match'])
        date_correct = sum(1 for r in self.results if r['date_match'])
        total_exact = sum(1 for r in self.results if r['total_match'])
        total_close = sum(1 for r in self.results if r['total_close'])
        currency_correct = sum(1 for r in self.results if r['currency_match'])

        # Average duration
        avg_duration = sum(r['duration_ms'] for r in self.results) / total_tests

        print("\n" + "="*80)
        print("📊 OCR Test Harness Report")
        print("="*80)

        # Overall summary
        print(f"\n**Overall Performance:**")
        print(f"  Total Tests: {total_tests}")
        print(f"  Fully Successful: {successful} ({successful/total_tests*100:.1f}%)")
        print(f"  Average Duration: {avg_duration:.0f}ms")

        # Field accuracy
        print(f"\n**Field-wise Accuracy:**")
        table_data = [
            ["Vendor", f"{vendor_correct}/{total_tests}", f"{vendor_correct/total_tests*100:.1f}%"],
            ["Date", f"{date_correct}/{total_tests}", f"{date_correct/total_tests*100:.1f}%"],
            ["Total (exact)", f"{total_exact}/{total_tests}", f"{total_exact/total_tests*100:.1f}%"],
            ["Total (±1 peso)", f"{total_close}/{total_tests}", f"{total_close/total_tests*100:.1f}%"],
            ["Currency", f"{currency_correct}/{total_tests}", f"{currency_correct/total_tests*100:.1f}%"],
        ]
        print(tabulate(table_data, headers=["Field", "Correct", "Accuracy"], tablefmt="simple"))

        # Per-vendor breakdown (if vendor info available)
        vendors = {}
        for r in self.results:
            if 'gt_vendor' in r:
                vendor = r['gt_vendor']
                if vendor not in vendors:
                    vendors[vendor] = {'total': 0, 'correct': 0}
                vendors[vendor]['total'] += 1
                if r['total_match']:
                    vendors[vendor]['correct'] += 1

        if vendors:
            print(f"\n**Per-Vendor Performance:**")
            vendor_data = []
            for vendor, stats in vendors.items():
                accuracy = stats['correct'] / stats['total'] * 100
                vendor_data.append([vendor, stats['total'], f"{stats['correct']}/{stats['total']}", f"{accuracy:.1f}%"])
            print(tabulate(vendor_data, headers=["Vendor", "Count", "Correct", "Accuracy"], tablefmt="simple"))

        # Failures
        failures = [r for r in self.results if not (r['vendor_match'] and r['total_match'])]
        if failures:
            print(f"\n**Failed/Partial Results ({len(failures)}):**")
            failure_data = []
            for f in failures:
                reason = []
                if not f['vendor_match']:
                    reason.append(f"vendor: '{f.get('extracted_vendor', 'N/A')}' ≠ '{f.get('gt_vendor', 'N/A')}'")
                if not f['total_match']:
                    reason.append(f"total: {f.get('extracted_total', 0.0)} ≠ {f.get('gt_total', 0.0)}")
                if 'error' in f:
                    reason.append(f"error: {f['error']}")
                failure_data.append([f['file'], "; ".join(reason)])
            print(tabulate(failure_data, headers=["File", "Issues"], tablefmt="simple"))

        print("\n" + "="*80)

        # Export detailed results to JSON
        report_path = Path("ocr_test_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'successful': successful,
                    'avg_duration_ms': avg_duration,
                    'vendor_accuracy': vendor_correct / total_tests,
                    'date_accuracy': date_correct / total_tests,
                    'total_exact_accuracy': total_exact / total_tests,
                    'total_close_accuracy': total_close / total_tests,
                    'currency_accuracy': currency_correct / total_tests,
                },
                'per_vendor': vendors,
                'detailed_results': self.results,
            }, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='Receipt OCR Test Harness')
    parser.add_argument('--images', required=True, help='Directory containing receipt images')
    parser.add_argument('--ground-truth', required=True, help='CSV file with ground truth data')
    parser.add_argument('--api-url', required=True, help='OCR API endpoint URL')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')

    args = parser.parse_args()

    # Validate inputs
    images_dir = Path(args.images)
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        sys.exit(1)

    gt_path = Path(args.ground_truth)
    if not gt_path.exists():
        print(f"❌ Ground truth file not found: {gt_path}")
        sys.exit(1)

    # Run harness
    harness = TestHarness(args.api_url, args.api_key, args.timeout)
    ground_truth = harness.load_ground_truth(str(gt_path))
    harness.run_tests(images_dir, ground_truth)
    harness.generate_report()


if __name__ == '__main__':
    main()
