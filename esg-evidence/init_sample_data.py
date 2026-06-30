"""
Initialize sample data for Evidence dashboard demo.
Creates a minimal DuckDB warehouse with sample ESG data.
"""

import duckdb
from pathlib import Path
from datetime import date, datetime, timedelta
import random

# Create warehouse directory
warehouse_path = Path("~/.paimon/esg_data/warehouse.duckdb").expanduser()
warehouse_path.parent.mkdir(parents=True, exist_ok=True)

# Connect to DuckDB
conn = duckdb.connect(str(warehouse_path))

# Create schemas
conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
conn.execute("CREATE SCHEMA IF NOT EXISTS staging")
conn.execute("CREATE SCHEMA IF NOT EXISTS marts")

print("Creating sample cloud carbon data...")

# Sample cloud providers
providers = ['GCP', 'AWS', 'Azure']
services = {
    'GCP': ['Compute Engine', 'Cloud Storage', 'BigQuery'],
    'AWS': ['EC2', 'S3', 'RDS'],
    'Azure': ['Virtual Machines', 'Blob Storage', 'SQL Database']
}
regions = {
    'GCP': ['us-central1', 'europe-west1'],
    'AWS': ['us-east-1', 'eu-west-1'],
    'Azure': ['eastus', 'westeurope']
}

# Generate 6 months of data
cloud_data = []
for i in range(6):
    month = date.today().replace(day=1) - timedelta(days=30*i)

    for provider in providers:
        account_id = f"{provider.lower()}-acct-001"

        for service in services[provider]:
            for region in regions[provider]:
                # Random emissions
                scope1 = random.uniform(100, 1000)
                scope2 = random.uniform(500, 5000)
                scope3 = random.uniform(200, 2000)
                total = scope1 + scope2 + scope3

                cloud_data.append({
                    'id': f"{provider}_{account_id}_{service}_{region}_{month.isoformat()}",
                    'cloud_provider': provider,
                    'account_id': account_id,
                    'service_name': service,
                    'region': region,
                    'usage_month_start': month,
                    'scope1_kgco2e': scope1,
                    'scope2_market_based_kgco2e': scope2,
                    'scope3_kgco2e': scope3,
                    'total_kgco2e': total,
                    'total_mtco2e': total / 1000,
                    'kgco2e_per_dollar': total / random.uniform(100, 1000),
                    'kgco2e_per_kwh': random.uniform(0.3, 0.6),
                    'extracted_at': datetime.now()
                })

# Create fact_cloud_carbon table
conn.execute("""
    CREATE TABLE marts.fact_cloud_carbon AS
    SELECT * FROM (VALUES
        (
            CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR),
            CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR), CAST(NULL AS DATE),
            CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE),
            CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE),
            CAST(NULL AS DOUBLE), CAST(NULL AS TIMESTAMP)
        )
    ) AS t(
        id, cloud_provider, account_id, service_name, region, usage_month_start,
        scope1_kgco2e, scope2_market_based_kgco2e, scope3_kgco2e,
        total_kgco2e, total_mtco2e, kgco2e_per_dollar, kgco2e_per_kwh, extracted_at
    )
    WHERE false
""")

# Insert sample data
for row in cloud_data:
    conn.execute("""
        INSERT INTO marts.fact_cloud_carbon VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, [
        row['id'], row['cloud_provider'], row['account_id'], row['service_name'],
        row['region'], row['usage_month_start'], row['scope1_kgco2e'],
        row['scope2_market_based_kgco2e'], row['scope3_kgco2e'],
        row['total_kgco2e'], row['total_mtco2e'], row['kgco2e_per_dollar'],
        row['kgco2e_per_kwh'], row['extracted_at']
    ])

print(f"Created {len(cloud_data)} cloud carbon records")

# Grid intensity data
print("Creating sample grid intensity data...")

zones = ['US-CA-CISO', 'US-PJM', 'GB', 'DE']
grid_data = []

# Last 7 days, hourly
for i in range(7 * 24):
    timestamp = datetime.now() - timedelta(hours=i)

    for zone in zones:
        intensity = random.uniform(200, 600)
        fossil = random.uniform(30, 70)
        renewable = random.uniform(20, 50)

        grid_data.append({
            'grid_region': zone,
            'timestamp_hour': timestamp,
            'timestamp_day': timestamp.date(),
            'carbon_intensity_gco2eq_per_kwh': intensity,
            'carbon_intensity_kgco2eq_per_kwh': intensity / 1000,
            'fossil_fuel_percentage': fossil,
            'renewable_percentage': renewable,
            'intensity_category': 'Medium' if intensity < 400 else 'High',
            'data_source': 'Electricity Maps'
        })

conn.execute("""
    CREATE TABLE marts.fact_grid_intensity AS
    SELECT * FROM (VALUES
        (
            CAST(NULL AS VARCHAR), CAST(NULL AS TIMESTAMP), CAST(NULL AS DATE),
            CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE),
            CAST(NULL AS DOUBLE), CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR)
        )
    ) AS t(
        grid_region, timestamp_hour, timestamp_day,
        carbon_intensity_gco2eq_per_kwh, carbon_intensity_kgco2eq_per_kwh,
        fossil_fuel_percentage, renewable_percentage,
        intensity_category, data_source
    )
    WHERE false
""")

for row in grid_data:
    conn.execute("""
        INSERT INTO marts.fact_grid_intensity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        row['grid_region'], row['timestamp_hour'], row['timestamp_day'],
        row['carbon_intensity_gco2eq_per_kwh'], row['carbon_intensity_kgco2eq_per_kwh'],
        row['fossil_fuel_percentage'], row['renewable_percentage'],
        row['intensity_category'], row['data_source']
    ])

print(f"Created {len(grid_data)} grid intensity records")

# Trends data
print("Creating sample trends data...")

trends_data = []
for i in range(6):
    month = date.today().replace(day=1) - timedelta(days=30*i)

    for provider in providers:
        account_id = f"{provider.lower()}-acct-001"

        total_mtco2e = random.uniform(10, 100)
        prev_total = random.uniform(10, 100)
        mom_change = ((total_mtco2e - prev_total) / prev_total) * 100 if i > 0 else None

        trends_data.append({
            'month': month,
            'cloud_provider': provider,
            'account_id': account_id,
            'total_mtco2e': total_mtco2e,
            'scope1_percent': random.uniform(5, 15),
            'scope2_percent': random.uniform(60, 75),
            'scope3_percent': random.uniform(15, 30),
            'mom_change_percent': mom_change,
            'rolling_3mo_avg_mtco2e': random.uniform(20, 80),
            'ytd_total_mtco2e': random.uniform(50, 300),
            'trend_indicator': 'Stable ⏸' if mom_change and abs(mom_change) < 10 else 'Increasing ⬆',
            'kgco2e_per_dollar': random.uniform(0.5, 2.0)
        })

conn.execute("""
    CREATE TABLE marts.carbon_trends_monthly AS
    SELECT * FROM (VALUES
        (
            CAST(NULL AS DATE), CAST(NULL AS VARCHAR), CAST(NULL AS VARCHAR),
            CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE),
            CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE), CAST(NULL AS DOUBLE),
            CAST(NULL AS DOUBLE), CAST(NULL AS VARCHAR), CAST(NULL AS DOUBLE)
        )
    ) AS t(
        month, cloud_provider, account_id, total_mtco2e,
        scope1_percent, scope2_percent, scope3_percent,
        mom_change_percent, rolling_3mo_avg_mtco2e, ytd_total_mtco2e,
        trend_indicator, kgco2e_per_dollar
    )
    WHERE false
""")

for row in trends_data:
    conn.execute("""
        INSERT INTO marts.carbon_trends_monthly VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        row['month'], row['cloud_provider'], row['account_id'], row['total_mtco2e'],
        row['scope1_percent'], row['scope2_percent'], row['scope3_percent'],
        row['mom_change_percent'], row['rolling_3mo_avg_mtco2e'],
        row['ytd_total_mtco2e'], row['trend_indicator'], row['kgco2e_per_dollar']
    ])

print(f"Created {len(trends_data)} trend records")

conn.close()

print(f"\n✓ Sample warehouse created at {warehouse_path}")
print("  - marts.fact_cloud_carbon (cloud emissions)")
print("  - marts.fact_grid_intensity (grid carbon intensity)")
print("  - marts.carbon_trends_monthly (monthly trends)")
