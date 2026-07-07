"""
Initialize sample warehouse for Evidence dashboard.
Creates marts tables directly with sample data.
"""

import duckdb
from pathlib import Path
from datetime import date, datetime, timedelta
import random

# Create warehouse
warehouse_path = Path(__file__).parent.parent / "warehouse/esg_data.duckdb"
warehouse_path.parent.mkdir(parents=True, exist_ok=True)

conn = duckdb.connect(str(warehouse_path))

print("Creating sample ESG data...")

# fact_cloud_carbon
print("  - fact_cloud_carbon")
conn.execute("DROP TABLE IF EXISTS fact_cloud_carbon")
conn.execute("""
    CREATE TABLE fact_cloud_carbon (
        id VARCHAR,
        cloud_provider VARCHAR,
        account_id VARCHAR,
        service_name VARCHAR,
        region VARCHAR,
        usage_month_start DATE,
        scope1_kgco2e DOUBLE,
        scope2_market_based_kgco2e DOUBLE,
        scope3_kgco2e DOUBLE,
        total_kgco2e DOUBLE,
        total_mtco2e DOUBLE,
        kgco2e_per_dollar DOUBLE,
        kgco2e_per_kwh DOUBLE,
        extracted_at TIMESTAMP
    )
""")

# Generate 6 months of cloud data
providers = ['GCP', 'AWS', 'Azure']
services = {
    'GCP': ['Compute Engine', 'Cloud Storage', 'BigQuery'],
    'AWS': ['EC2', 'S3', 'RDS'],
    'Azure': ['Virtual Machines', 'Blob Storage', 'SQL Database']
}
regions = {
    'GCP': ['us-central1', 'europe-west1', 'northamerica-northeast1', 'asia-southeast1'],
    'AWS': ['us-east-1', 'eu-west-1', 'ca-central-1', 'ap-southeast-1', 'us-west-2'],
    'Azure': ['eastus', 'westeurope', 'canadacentral', 'southeastasia', 'uksouth']
}

for i in range(6):
    month = (date.today().replace(day=1) - timedelta(days=30*i))

    for provider in providers:
        for service in services[provider]:
            for region in regions[provider]:
                scope1 = random.uniform(100, 1000)
                scope2 = random.uniform(500, 5000)
                scope3 = random.uniform(200, 2000)
                total = scope1 + scope2 + scope3

                conn.execute("""
                    INSERT INTO fact_cloud_carbon VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, [
                    f"{provider}_{service}_{region}_{month.isoformat()}",
                    provider,
                    f"{provider.lower()}-account-001",
                    service,
                    region,
                    month,
                    scope1,
                    scope2,
                    scope3,
                    total,
                    total / 1000,
                    total / random.uniform(100, 1000),
                    random.uniform(0.3, 0.6),
                    datetime.now()
                ])

# fact_grid_intensity
print("  - fact_grid_intensity")
conn.execute("DROP TABLE IF EXISTS fact_grid_intensity")
conn.execute("""
    CREATE TABLE fact_grid_intensity (
        grid_region VARCHAR,
        timestamp_hour TIMESTAMP,
        timestamp_day DATE,
        carbon_intensity_gco2eq_per_kwh DOUBLE,
        carbon_intensity_kgco2eq_per_kwh DOUBLE,
        fossil_fuel_percentage DOUBLE,
        renewable_percentage DOUBLE,
        intensity_category VARCHAR,
        data_source VARCHAR
    )
""")

# Generate 7 days of grid data
zones = ['US-CA-CISO', 'US-VA-PJM', 'US-IA-MISO', 'CA-QC', 'CA-ON', 'GB', 'DE', 'NL', 'IE', 'SG']
for i in range(7 * 24):
    timestamp = datetime.now() - timedelta(hours=i)

    for zone in zones:
        intensity = random.uniform(200, 600)
        fossil = random.uniform(30, 70)
        renewable = random.uniform(20, 50)

        conn.execute("""
            INSERT INTO fact_grid_intensity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            zone,
            timestamp,
            timestamp.date(),
            intensity,
            intensity / 1000,
            fossil,
            renewable,
            'Medium' if intensity < 400 else 'High',
            'Electricity Maps'
        ])

# carbon_trends_monthly
print("  - carbon_trends_monthly")
conn.execute("DROP TABLE IF EXISTS carbon_trends_monthly")
conn.execute("""
    CREATE TABLE carbon_trends_monthly (
        month DATE,
        cloud_provider VARCHAR,
        account_id VARCHAR,
        total_mtco2e DOUBLE,
        scope1_percent DOUBLE,
        scope2_percent DOUBLE,
        scope3_percent DOUBLE,
        mom_change_percent DOUBLE,
        rolling_3mo_avg_mtco2e DOUBLE,
        ytd_total_mtco2e DOUBLE,
        trend_indicator VARCHAR,
        kgco2e_per_dollar DOUBLE
    )
""")

# Generate 6 months of trends
for i in range(6):
    month = date.today().replace(day=1) - timedelta(days=30*i)

    for provider in providers:
        total = random.uniform(10, 100)
        prev = random.uniform(10, 100) if i > 0 else total
        mom = ((total - prev) / prev * 100) if i > 0 else None

        conn.execute("""
            INSERT INTO carbon_trends_monthly VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            month,
            provider,
            f"{provider.lower()}-account-001",
            total,
            random.uniform(5, 15),
            random.uniform(60, 75),
            random.uniform(15, 30),
            mom,
            random.uniform(20, 80),
            random.uniform(50, 300),
            'Stable ⏸' if mom and abs(mom) < 10 else 'Increasing ⬆',
            random.uniform(0.5, 2.0)
        ])

conn.close()

print(f"\n✓ Sample warehouse created at {warehouse_path}")
print(f"  Ready for Evidence dashboard build!")
