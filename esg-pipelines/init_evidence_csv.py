"""
Export sample data to CSV files for Evidence dashboard.
More reliable than DuckDB for Evidence.
"""

import duckdb
from pathlib import Path

# Create warehouse temporarily
warehouse_path = Path("/tmp/esg_temp.duckdb")
conn = duckdb.connect(str(warehouse_path))

# Create tables (same as before)
print("Generating sample data...")
exec(open("init_evidence_warehouse.py").read())

# Export to CSV
csv_dir = Path(__file__).parent.parent / "esg-evidence/esg-evidence-new/sources/esg_data"
csv_dir.mkdir(parents=True, exist_ok=True)

print("\nExporting to CSV...")
conn.execute(f"COPY fact_cloud_carbon TO '{csv_dir}/fact_cloud_carbon.csv' (HEADER, DELIMITER ',')")
print(f"  ✓ fact_cloud_carbon.csv")

conn.execute(f"COPY fact_grid_intensity TO '{csv_dir}/fact_grid_intensity.csv' (HEADER, DELIMITER ',')")
print(f"  ✓ fact_grid_intensity.csv")

conn.execute(f"COPY carbon_trends_monthly TO '{csv_dir}/carbon_trends_monthly.csv' (HEADER, DELIMITER ',')")
print(f"  ✓ carbon_trends_monthly.csv")

conn.close()
print(f"\n✓ CSV files created in {csv_dir}")
