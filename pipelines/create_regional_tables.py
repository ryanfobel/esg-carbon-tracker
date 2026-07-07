"""
Create missing regional tables in Evidence warehouse.
Executes the dbt model SQL logic directly in DuckDB.
"""

import duckdb
from pathlib import Path

# Connect to warehouse
warehouse_path = Path(__file__).parent.parent / "warehouse/esg_data.duckdb"
conn = duckdb.connect(str(warehouse_path))

print("Creating regional tables for Evidence dashboard...")

# Check if fact_grid_intensity exists
try:
    result = conn.execute("SELECT COUNT(*) FROM fact_grid_intensity").fetchone()
    print(f"  Found {result[0]} rows in fact_grid_intensity")
except:
    print("  WARNING: fact_grid_intensity table not found. Make sure base data is loaded first.")
    exit(1)

# Create grid_intensity_daily
print("  - Creating grid_intensity_daily...")
conn.execute("DROP TABLE IF EXISTS grid_intensity_daily")
conn.execute("""
CREATE TABLE grid_intensity_daily AS
WITH daily_agg AS (
    SELECT
        grid_region,
        timestamp_day,
        date_trunc('week', timestamp_day) AS timestamp_week,
        date_trunc('month', timestamp_day) AS timestamp_month,
        EXTRACT(year FROM timestamp_day) AS year,
        EXTRACT(month FROM timestamp_day) AS month,
        EXTRACT(dow FROM timestamp_day) AS day_of_week,

        -- Carbon intensity aggregates
        AVG(carbon_intensity_gco2eq_per_kwh) AS avg_carbon_intensity,
        MIN(carbon_intensity_gco2eq_per_kwh) AS min_carbon_intensity,
        MAX(carbon_intensity_gco2eq_per_kwh) AS max_carbon_intensity,
        STDDEV(carbon_intensity_gco2eq_per_kwh) AS stddev_carbon_intensity,

        -- Fuel mix (from Electricity Maps data)
        AVG(fossil_fuel_percentage) AS avg_fossil_fuel_percentage,
        AVG(renewable_percentage) AS avg_renewable_percentage,

        -- Time-based aggregates
        COUNT(*) AS hours_reported,
        COUNT(DISTINCT timestamp_hour) AS distinct_hours,

        -- Clean hours metrics
        SUM(CASE WHEN carbon_intensity_gco2eq_per_kwh < 250 THEN 1 ELSE 0 END) AS low_carbon_hours,
        SUM(CASE WHEN carbon_intensity_gco2eq_per_kwh >= 600 THEN 1 ELSE 0 END) AS high_carbon_hours,

        -- Peak/off-peak analysis (assuming peak = 7am-11pm)
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
),

final AS (
    SELECT
        grid_region,
        timestamp_day,
        timestamp_week,
        timestamp_month,
        year,
        month,
        day_of_week,

        -- Carbon intensity metrics
        avg_carbon_intensity,
        min_carbon_intensity,
        max_carbon_intensity,
        stddev_carbon_intensity,
        max_carbon_intensity - min_carbon_intensity AS daily_range,

        -- Categorize average daily intensity
        CASE
            WHEN avg_carbon_intensity < 100 THEN 'Very Low'
            WHEN avg_carbon_intensity < 250 THEN 'Low'
            WHEN avg_carbon_intensity < 400 THEN 'Medium'
            WHEN avg_carbon_intensity < 600 THEN 'High'
            ELSE 'Very High'
        END AS avg_intensity_category,

        -- Fuel mix
        avg_fossil_fuel_percentage,
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
)

SELECT * FROM final
""")

rows = conn.execute("SELECT COUNT(*) FROM grid_intensity_daily").fetchone()[0]
print(f"    Created grid_intensity_daily with {rows} rows")

# Create or update dim_grid_regions (if it doesn't exist from init script)
print("  - Creating/updating dim_grid_regions...")

# Check if table exists and what schema it has
try:
    existing_cols = conn.execute("DESCRIBE dim_grid_regions").fetchall()
    has_stats = any('avg_carbon_intensity' in str(col) for col in existing_cols)

    if not has_stats:
        print("    Existing dim_grid_regions found but missing stats columns. Creating backup...")
        conn.execute("CREATE TABLE dim_grid_regions_backup AS SELECT * FROM dim_grid_regions")
except:
    has_stats = False

if not has_stats:
    # Create the statistics-enriched version
    conn.execute("DROP TABLE IF EXISTS dim_grid_regions_stats")
    conn.execute("""
    CREATE TABLE dim_grid_regions_stats AS
    WITH base_regions AS (
        SELECT DISTINCT grid_region
        FROM fact_grid_intensity
    ),

    region_stats AS (
        SELECT
            grid_region,
            MIN(timestamp_day) AS first_data_date,
            MAX(timestamp_day) AS last_data_date,
            COUNT(DISTINCT timestamp_day) AS days_of_data,
            AVG(carbon_intensity_gco2eq_per_kwh) AS avg_carbon_intensity,
            MIN(carbon_intensity_gco2eq_per_kwh) AS min_carbon_intensity,
            MAX(carbon_intensity_gco2eq_per_kwh) AS max_carbon_intensity,
            AVG(renewable_percentage) AS avg_renewable_percentage
        FROM fact_grid_intensity
        GROUP BY 1
    ),

    final AS (
        SELECT
            r.grid_region,

            -- Statistics
            s.first_data_date,
            s.last_data_date,
            s.days_of_data,
            s.avg_carbon_intensity,
            s.min_carbon_intensity,
            s.max_carbon_intensity,
            s.avg_renewable_percentage,

            -- Categorize region by average carbon intensity
            CASE
                WHEN s.avg_carbon_intensity < 150 THEN 'Very Clean'
                WHEN s.avg_carbon_intensity < 300 THEN 'Clean'
                WHEN s.avg_carbon_intensity < 450 THEN 'Medium'
                WHEN s.avg_carbon_intensity < 600 THEN 'Dirty'
                ELSE 'Very Dirty'
            END AS cleanliness_category

        FROM base_regions r
        LEFT JOIN region_stats s ON r.grid_region = s.grid_region
    )

    SELECT * FROM final
    """)

    rows = conn.execute("SELECT COUNT(*) FROM dim_grid_regions_stats").fetchone()[0]
    print(f"    Created dim_grid_regions_stats with {rows} rows")
    print("    Note: Original dim_grid_regions preserved with geographic data")

conn.close()
print("\n✓ Regional tables created successfully!")
print("  - grid_intensity_daily: Daily aggregation with peak/off-peak analysis")
print("  - dim_grid_regions_stats: Region statistics and cleanliness categories")
print("\nRefresh your Evidence dashboard to see the charts working!")
