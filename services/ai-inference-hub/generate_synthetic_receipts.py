#!/usr/bin/env python3
"""
Synthetic Philippine Receipt Generator
Generates 1,000 realistic Philippine receipt images for PaddleOCR training

Features:
- Mixed English/Tagalog text
- Philippine merchants (SM, Puregold, 7-Eleven, Jollibee, etc.)
- 12% VAT calculation
- TIN format: XXX-XXX-XXX-XXX
- Thermal receipt simulation (fade, noise)
- Date range: 2023-2024
"""

import os
import random
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import json

# Philippine merchant names
MERCHANTS = [
    ("SM SUPERMARKET", "North EDSA Branch"),
    ("PUREGOLD", "Cubao Branch"),
    ("7-ELEVEN", "Quezon City"),
    ("JOLLIBEE", "Ortigas Center"),
    ("MERCURY DRUG", "Makati"),
    ("ROBINSON'S", "Galleria"),
    ("MINISTOP", "BGC"),
    ("ALFAMART", "Mandaluyong"),
    ("FAMILY MART", "Pasig City"),
    ("SAVEMORE", "Manila"),
]

# Common items with Filipino naming
ITEMS = [
    ("Gatas/Milk 1L", 85, 120),
    ("Tinapay/Bread", 45, 65),
    ("Itlog/Eggs (1 dozen)", 120, 150),
    ("Bigas/Rice 5kg", 250, 300),
    ("Manok/Chicken 1kg", 180, 220),
    ("Gulay/Vegetables", 50, 100),
    ("Prutas/Fruits", 80, 150),
    ("Tubig/Water 1L", 20, 35),
    ("Kape/Coffee", 150, 200),
    ("Asukal/Sugar 1kg", 60, 80),
    ("Asin/Salt", 15, 25),
    ("Toyo/Soy Sauce", 35, 50),
    ("Cooking Oil 1L", 120, 160),
    ("Sardinas/Sardines", 25, 40),
    ("Corned Beef", 45, 70),
    ("Instant Noodles", 12, 18),
    ("Shampoo", 80, 150),
    ("Sabon/Soap", 30, 60),
    ("Toothpaste", 45, 80),
    ("Toilet Paper", 60, 100),
]

def generate_tin():
    """Generate Philippine TIN format: XXX-XXX-XXX-XXX"""
    return f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}"

def generate_date():
    """Generate random date in 2023-2024"""
    start = datetime(2023, 1, 1)
    end = datetime(2024, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_date = start + timedelta(days=random_days)
    return random_date

def create_receipt(receipt_id):
    """Generate a single synthetic receipt image"""

    # Create image
    width, height = 400, 650
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Select merchant
    merchant_name, branch = random.choice(MERCHANTS)
    tin = generate_tin()
    receipt_date = generate_date()

    # Generate transaction
    num_items = random.randint(3, 8)
    selected_items = random.sample(ITEMS, num_items)

    # Build receipt lines
    lines = []
    lines.append(merchant_name)
    lines.append(branch)
    lines.append(f"TIN: {tin}")
    lines.append("")
    lines.append(f"DATE: {receipt_date.strftime('%Y-%m-%d')}")
    lines.append(f"TIME: {receipt_date.strftime('%H:%M:%S')}")
    lines.append("")
    lines.append("ITEMS:")

    subtotal = 0
    items_data = []
    for item_name, min_price, max_price in selected_items:
        price = random.randint(min_price, max_price)
        subtotal += price
        lines.append(f"{item_name[:20].ljust(20)} ₱{price:>6.2f}")
        items_data.append({"name": item_name, "price": price})

    # Calculate VAT (12%)
    vat = subtotal * 0.12
    total = subtotal + vat

    lines.append("")
    lines.append(f"SUBTOTAL:       ₱{subtotal:>6.2f}")
    lines.append(f"VAT (12%):       ₱{vat:>6.2f}")
    lines.append(f"TOTAL:          ₱{total:>6.2f}")

    # Payment
    cash = total + random.randint(10, 100)
    change = cash - total
    lines.append("")
    lines.append(f"CASH:           ₱{cash:>6.2f}")
    lines.append(f"CHANGE:          ₱{change:>6.2f}")

    # Footer
    lines.append("")
    lines.append("Salamat po! / Thank you!")

    # Draw text
    y = 15
    for line in lines:
        draw.text((15, y), line, fill='black')
        y += 25

    # Add slight noise/variation (simulate thermal receipt)
    if random.random() > 0.5:
        # Slight fade effect
        img = img.convert('L')  # Grayscale
        img = img.point(lambda x: x + random.randint(-10, 10))
        img = img.convert('RGB')

    # Save image
    output_dir = "/tmp/synthetic_receipts"
    os.makedirs(output_dir, exist_ok=True)
    img_path = f"{output_dir}/receipt_{receipt_id:04d}.png"
    img.save(img_path)

    # Save annotation
    annotation = {
        "image": f"receipt_{receipt_id:04d}.png",
        "merchant_name": merchant_name,
        "branch": branch,
        "tin": tin,
        "date": receipt_date.strftime('%Y-%m-%d'),
        "time": receipt_date.strftime('%H:%M:%S'),
        "items": items_data,
        "subtotal": round(subtotal, 2),
        "vat": round(vat, 2),
        "total": round(total, 2),
        "cash": round(cash, 2),
        "change": round(change, 2)
    }

    return img_path, annotation

def main():
    """Generate 1,000 synthetic receipts"""
    print("🧾 Generating 1,000 synthetic Philippine receipts...")

    annotations = []

    for i in range(1, 1001):
        img_path, annotation = create_receipt(i)
        annotations.append(annotation)

        if i % 100 == 0:
            print(f"✓ Generated {i}/1000 receipts")

    # Save annotations
    with open('/tmp/synthetic_receipts/annotations.json', 'w') as f:
        json.dump(annotations, f, indent=2)

    print("\n✅ Complete!")
    print(f"📁 Images: /tmp/synthetic_receipts/receipt_0001.png to receipt_1000.png")
    print(f"📝 Annotations: /tmp/synthetic_receipts/annotations.json")
    print(f"\nDataset ready for PaddleOCR training")

if __name__ == "__main__":
    main()
