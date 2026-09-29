import pdfplumber
from pathlib import Path

PDF_PATH = Path(
    "data/raw/official_reports/FlashReport_August_2026.pdf"
)

with pdfplumber.open(PDF_PATH) as pdf:

    page = pdf.pages[57]

    print("=" * 60)
    print("TABLE EXTRACTION TEST")
    print("=" * 60)

    tables = page.extract_tables()

    print(f"Tables detected: {len(tables)}")

    for table_number, table in enumerate(tables, start=1):

        print(f"\nTABLE {table_number}")
        print("-" * 60)

        for row_number, row in enumerate(table[:8], start=1):
            print(f"Row {row_number}: {row}")