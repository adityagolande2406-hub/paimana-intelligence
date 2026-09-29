import pymupdf
from pathlib import Path

PDF_PATH = Path("data/raw/official_reports/FlashReport_August_2026.pdf")

doc = pymupdf.open(PDF_PATH)

# PDF page 57 corresponds to index 56
page = doc[56]

print("=" * 60)
print("PAIMANA TABLE 6 INSPECTION")
print("=" * 60)

print(f"PDF Page: {page.number + 1}")

text = page.get_text()

print(f"Extracted characters: {len(text)}")
print("\nEXTRACTED CONTENT")
print("-" * 60)

print(text[:5000])

print("\nInspection completed.")