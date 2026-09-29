import pymupdf
from pathlib import Path

PDF_PATH = Path("data/raw/official_reports/FlashReport_August_2026.pdf")

if not PDF_PATH.exists():
    print("ERROR: PDF not found!")
    raise SystemExit(1)

doc = pymupdf.open(PDF_PATH)

print("=" * 50)
print("PAIMANA PDF INSPECTION")
print("=" * 50)

print(f"Total pages: {len(doc)}")
print(f"File size: {PDF_PATH.stat().st_size / (1024 * 1024):.2f} MB")

print("\nChecking first 3 pages:")

for page_number in range(min(3, len(doc))):
    page = doc[page_number]
    text = page.get_text()

    print(f"\nPage {page_number + 1}")
    print(f"Extracted characters: {len(text)}")
    print("-" * 40)
    print(text[:500])

print("\nInspection completed.")