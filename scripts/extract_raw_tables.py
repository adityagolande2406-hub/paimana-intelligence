import pdfplumber
import pandas as pd
import re

from pathlib import Path

PDF_PATH = Path(
    "data/raw/official_reports/FlashReport_August_2026.pdf"
)

OUTPUT_PATH = Path(
    "data/processed/raw_project_rows.csv"
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

all_rows = []
pages_with_tables = 0
pages_without_tables = []

with pdfplumber.open(PDF_PATH) as pdf:

    print(f"Total PDF pages: {len(pdf.pages)}")

    for page_number, page in enumerate(pdf.pages, start=1):

        tables = page.extract_tables()

        if not tables:
            pages_without_tables.append(page_number)
            continue

        for table in tables:

            for row in table:

                if not row or len(row) < 8:
                    continue

                serial = str(row[0] or "").strip()

                if re.fullmatch(r"\d+", serial):

                    all_rows.append({
                        "serial_number": serial,
                        "project_details": row[1],
                        "state": row[2],
                        "approval_dates": row[3],
                        "completion_dates": row[4],
                        "cost_values": row[5],
                        "expenditure": row[6],
                        "physical_progress": row[7],
                        "source_page": page_number
                    })

            pages_with_tables += 1

df = pd.DataFrame(all_rows)

df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print("\n" + "=" * 50)
print("RAW EXTRACTION SUMMARY")
print("=" * 50)

print(f"Extracted rows: {len(df)}")
print(f"Pages with detected tables: {pages_with_tables}")
print(f"Pages without tables: {len(pages_without_tables)}")

print(f"\nCSV saved to: {OUTPUT_PATH}")

print("\nFirst 5 extracted records:")
print(df.head().to_string(index=False))

print("\nExtraction completed.")