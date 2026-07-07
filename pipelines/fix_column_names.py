"""
Fix column names in grid_intensity_daily to match dashboard expectations.
The dashboard queries expect: date, avg_intensity, avg_fossil_percentage
But we created: timestamp_day, avg_carbon_intensity, avg_fossil_fuel_percentage
"""

import duckdb
from pathlib import Path

warehouse_path = Path(__file__).parent.parent / "warehouse/esg_data.duckdb"
conn = duckdb.connect(str(warehouse_path))

print("Fixing column names to match dashboard queries...")

# Recreate grid_intensity_daily with correct column names
print("  - Recreating grid_intensity_daily with aligned column names...")
conn.execute("DROP TABLE IF EXISTS grid_intensity_daily")
conn.execute("""
CREATE TABLE grid_intensity_daily AS
WITH daily_agg AS (
    SELECT
        grid_region,
        timestamp_day AS date,  -- Renamed from timestamp_day
        date_trunc('week', timestamp_day) AS timestamp_week,
        date_trunc('month', timestamp_day) AS timestamp_month,
        EXTRACT(year FROM timestamp_day) AS year,
        EXTRACT(month FROM timestamp_day) AS month,
        EXTRACT(dow FROM timestamp_day) AS day_of_week,

        -- Carbon intensity aggregates
        AVG(carbon_intensity_gco2eq_per_kwh) AS avg_intensity,  -- Renamed from avg_carbon_intensity
        MIN(carbon_intensity_gco2eq_per_kwh) AS min_intensity,
        MAX(carbon_intensity_gco2eq_per_kwh) AS max_intensity,
        STDDEV(carbon_intensity_gco2eq_per_kwh) AS stddev_intensity,

        -- Fuel mix
        AVG(fossil_fuel_percentage) AS avg_fossil_percentage,  -- Renamed from avg_fossil_fuel_percentage
        AVG(renewable_percentage) AS avg_renewable_percentage,

        -- Time-based aggregates
        COUNT(*) AS hours_reported,
        COUNT(DISTINCT timestamp_hour) AS distinct_hours,

        -- Clean hours metrics
        SUM(CASE WHEN carbon_intensity_gco2eq_per_kwh < 250 THEN 1 ELSE 0 END) AS low_carbon_hours,
        SUM(CASE WHEN carbon_intensity_gco2eq_per_kwh >= 600 THEN 1 ELSE 0 END) AS high_carbon_hours,

        -- Peak/off-peak analysis
        AVG(CASE
            WHEN EXTRACT(hour FROM timestamp_hour) BETWEEN 7 AND 22
            THEN carbon_intensity_gco2eq_per_kwh
        END) AS avg_peak_intensity,
        AVG(CASE
            WHEN EXTRACT(hour FROM timestamp_hour) NOT BETWEEN 7 AND 22
            THEN carbon_intensity_gco2eq_per_kwh
        END) AS avg_offpeak_intensity,

        -- Data quality
        COUNT(DISTINCT data_source) AS num_data_sources

    FROM fact_grid_intensity
    GROUP BY 1, 2, 3, 4, 5, 6, 7
)

SELECT
    grid_region,
    date,
    timestamp_week,
    timestamp_month,
    year,
    month,
    day_of_week,

    -- Carbon intensity metrics
    avg_intensity,
    min_intensity,
    max_intensity,
    stddev_intensity,
    max_intensity - min_intensity AS daily_range,

    -- Categorize average daily intensity
    CASE
        WHEN avg_intensity < 100 THEN 'Very Low'
        WHEN avg_intensity < 250 THEN 'Low'
        WHEN avg_intensity < 400 THEN 'Medium'
        WHEN avg_intensity < 600 THEN 'High'
        ELSE 'Very High'
    END AS avg_intensity_category,

    -- Fuel mix
    avg_fossil_percentage,
    avg_renewable_percentage,

    -- Time metrics
    hours_reported,
    distinct_hours,
    low_carbon_hours,
    high_carbon_hours,
    CASE WHEN distinct_hours >= 20 THEN true ELSE false END AS is_complete_day,

    -- Peak vs off-peak
    avg_peak_intensity,
    avg_offpeak_intensity,
    avg_peak_intensity - avg_offpeak_intensity AS peak_offpeak_delta,

    -- Data quality
    num_data_sources

FROM daily_agg
""")

rows = conn.execute("SELECT COUNT(*) FROM grid_intensity_daily").fetchone()[0]
print(f"    ✓ Recreated with {rows} rows")

# Verify column names
print("\n  - Verifying column names...")
columns = conn.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'grid_intensity_daily'
    ORDER BY ordinal_position
""").fetchall()

expected_cols = {'date', 'avg_intensity', 'avg_fossil_percentage', 'avg_renewable_percentage'}
actual_cols = {col[0] for col in columns}

if expected_cols.issubset(actual_cols):
    print("    ✓ All expected columns present:")
    for col in expected_cols:
        print(f"      - {col}")
else:
    missing = expected_cols - actual_cols
    print(f"    ✗ Missing columns: {missing}")

print("\n✅ Column names fixed! Dashboard queries should now work.")

conn.close()
