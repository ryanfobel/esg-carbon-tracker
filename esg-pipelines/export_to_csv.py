"""
Export DuckDB warehouse to CSV files for Evidence.
"""

import duckdb
from pathlib import Path

# Connect to existing warehouse
warehouse_path = Path(__file__).parent.parent / "esg-evidence/esg-evidence-new/esg_data.duckdb"

if not warehouse_path.exists():
    print(f"Warehouse not found at {warehouse_path}")
    print("Run init_evidence_warehouse.py first!")
    exit(1)

conn = duckdb.connect(str(warehouse_path), read_only=True)

# Create CSV directory
csv_dir = Path(__file__).parent.parent / "esg-evidence/esg-evidence-new/sources/esg_data"
csv_dir.mkdir(parents=True, exist_ok=True)

print("Exporting DuckDB tables to CSV...")

tables = ['fact_cloud_carbon', 'fact_grid_intensity', 'carbon_trends_monthly']

for table in tables:
    csv_file = csv_dir / f"{table}.csv"
    conn.execute(f"COPY {table} TO '{csv_file}' (HEADER, DELIMITER ',')")

    # Get count
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  ✓ {table}.csv ({count} rows)")

conn.close()
print(f"\n✓ CSV files created in {csv_dir}")
print("Update connection.yaml to use CSV source")
