"""
Validate that required tables exist in the warehouse.
Run this before deploying or starting the dashboard to catch schema errors early.
"""

import duckdb
import sys
from pathlib import Path

# Required tables and their expected columns
REQUIRED_TABLES = {
    'fact_grid_intensity': [
        'grid_region', 'timestamp_hour', 'carbon_intensity_gco2eq_per_kwh',
        'renewable_percentage', 'fossil_fuel_percentage'
    ],
    'fact_cloud_carbon': [
        'cloud_provider', 'usage_month_start', 'total_mtco2e', 'region'
    ],
    'grid_intensity_daily': [
        'grid_region', 'date', 'avg_intensity',
        'min_intensity', 'max_intensity', 'avg_fossil_percentage', 'avg_renewable_percentage'
    ],
    'dim_grid_regions': [
        'grid_region', 'region_name', 'country', 'latitude', 'longitude'
    ],
    'carbon_trends_monthly': [
        'month', 'cloud_provider', 'total_mtco2e'
    ]
}

def validate_warehouse():
    """Validate warehouse schema matches dashboard requirements."""
    warehouse_path = Path(__file__).parent.parent / "warehouse/esg_data.duckdb"

    if not warehouse_path.exists():
        print(f"❌ ERROR: Warehouse not found at {warehouse_path}")
        print("   Run: python init_evidence_warehouse.py")
        return False

    conn = duckdb.connect(str(warehouse_path), read_only=True)
    errors = []
    warnings = []

    print("Validating warehouse schema...\n")

    # Check each required table
    for table_name, required_columns in REQUIRED_TABLES.items():
        print(f"Checking {table_name}...", end=" ")

        try:
            # Check table exists
            result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            row_count = result[0]

            # Check required columns exist
            columns = conn.execute(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
            """).fetchall()

            existing_cols = [col[0] for col in columns]
            missing_cols = [col for col in required_columns if col not in existing_cols]

            if missing_cols:
                errors.append(f"  ❌ {table_name}: Missing columns: {', '.join(missing_cols)}")
                print("❌")
            elif row_count == 0:
                warnings.append(f"  ⚠️  {table_name}: Table exists but has 0 rows")
                print("⚠️  (empty)")
            else:
                print(f"✓ ({row_count:,} rows)")

        except Exception as e:
            errors.append(f"  ❌ {table_name}: {str(e)}")
            print("❌")

    # Print results
    print()
    if errors:
        print("ERRORS:")
        for error in errors:
            print(error)
        print()

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(warning)
        print()

    if errors:
        print("❌ Validation FAILED - dashboard will have errors")
        print("\nTo fix:")
        print("  1. Run: python create_regional_tables.py")
        print("  2. Or run: python init_evidence_warehouse.py")
        return False
    elif warnings:
        print("⚠️  Validation passed with warnings")
        return True
    else:
        print("✅ All tables validated successfully!")
        return True

if __name__ == "__main__":
    success = validate_warehouse()
    sys.exit(0 if success else 1)
