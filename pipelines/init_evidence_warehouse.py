"""
Initialize Evidence-compatible warehouse with sample data.
Creates tables in main schema (no marts prefix) for Evidence dashboard.
"""

import duckdb
from datetime import date, datetime, timedelta
import random
from pathlib import Path

# Create warehouse in dedicated warehouse directory
warehouse_path = Path(__file__).parent.parent / "warehouse/esg_data.duckdb"
warehouse_path.parent.mkdir(parents=True, exist_ok=True)

conn = duckdb.connect(str(warehouse_path))

print("Creating sample ESG data for Evidence dashboard...")

# dim_grid_regions - dimension table for grid region metadata
print("  - dim_grid_regions")
conn.execute("DROP TABLE IF EXISTS dim_grid_regions")
conn.execute("""
    CREATE TABLE dim_grid_regions (
        grid_region VARCHAR PRIMARY KEY,
        region_name VARCHAR,
        city VARCHAR,
        country VARCHAR,
        country_code VARCHAR,
        latitude DOUBLE,
        longitude DOUBLE,
        grid_operator VARCHAR,
        cloud_providers VARCHAR,
        gcp_regions VARCHAR,
        aws_regions VARCHAR,
        azure_regions VARCHAR
    )
""")

# Insert comprehensive region mappings
regions_data = [
    # North America - United States
    ('US-CA-CISO', 'California ISO', 'San Francisco', 'United States', 'US', 37.7749, -122.4194, 'CAISO', 'GCP, AWS, Azure', 'us-west1', 'us-west-1', 'West US'),
    ('US-OR', 'Oregon', 'Portland', 'United States', 'US', 45.5152, -122.6784, 'BPA', 'GCP, AWS, Azure', 'us-west2', 'us-west-2', 'West US 2'),
    ('US-VA-PJM', 'Virginia PJM', 'Ashburn', 'United States', 'US', 37.4316, -77.4024, 'PJM', 'AWS, Azure', '', 'us-east-1', 'East US'),
    ('US-NC', 'North Carolina', 'Charlotte', 'United States', 'US', 35.7596, -79.0193, 'Duke Energy', 'GCP, Azure', 'us-east1', '', 'East US 2'),
    ('US-OH', 'Ohio', 'Columbus', 'United States', 'US', 39.9612, -82.9988, 'PJM', 'AWS, Azure', '', 'us-east-2', 'Central US'),
    ('US-TX-ERCOT', 'Texas ERCOT', 'Dallas', 'United States', 'US', 30.2672, -97.7431, 'ERCOT', 'GCP, Azure', 'us-south1', '', 'South Central US'),
    ('US-IA-MISO', 'Iowa MISO', 'Council Bluffs', 'United States', 'US', 41.5868, -93.6250, 'MISO', 'GCP, Azure', 'us-central1', '', 'North Central US'),
    ('US-NV', 'Nevada', 'Las Vegas', 'United States', 'US', 36.1699, -115.1398, 'NV Energy', 'GCP, Azure', 'us-west4', '', 'West US 3'),
    ('US-FL', 'Florida', 'Miami', 'United States', 'US', 27.9506, -81.7605, 'FPL', 'Azure', '', '', 'Florida'),

    # North America - Canada
    ('CA-ON', 'Ontario', 'Toronto', 'Canada', 'CA', 43.6532, -79.3832, 'IESO', 'GCP, Azure', 'northamerica-northeast1', '', 'Canada Central'),
    ('CA-QC', 'Quebec', 'Montreal', 'Canada', 'CA', 45.5017, -73.5673, 'Hydro-Québec', 'GCP, Azure', 'northamerica-northeast2', '', 'Canada East'),
    ('CA-AB', 'Alberta', 'Calgary', 'Canada', 'CA', 51.0447, -114.0719, 'AESO', 'GCP', 'northamerica-northeast3', '', ''),

    # South America
    ('BR-SP', 'São Paulo', 'São Paulo', 'Brazil', 'BR', -23.5505, -46.6333, 'ONS', 'GCP, AWS, Azure', 'southamerica-east1', 'sa-east-1', 'Brazil South'),
    ('CL', 'Chile', 'Santiago', 'Chile', 'CL', -33.4489, -70.6693, 'Coordinador', 'AWS', '', 'sa-east-2', ''),

    # Europe - Western
    ('GB', 'United Kingdom', 'London', 'United Kingdom', 'GB', 51.5074, -0.1278, 'National Grid ESO', 'GCP, AWS, Azure', 'europe-west2', 'eu-west-2', 'UK South'),
    ('IE', 'Ireland', 'Dublin', 'Ireland', 'IE', 53.3498, -6.2603, 'EirGrid', 'GCP, AWS, Azure', 'europe-west1', 'eu-west-1', 'North Europe'),
    ('NL', 'Netherlands', 'Amsterdam', 'Netherlands', 'NL', 52.3676, 4.9041, 'TenneT', 'GCP, Azure', 'europe-west4', '', 'West Europe'),
    ('BE', 'Belgium', 'Brussels', 'Belgium', 'BE', 50.8503, 4.3517, 'Elia', 'GCP, Azure', 'europe-west1', '', 'West Europe'),
    ('FR', 'France', 'Paris', 'France', 'FR', 48.8566, 2.3522, 'RTE', 'GCP, AWS, Azure', 'europe-west9', 'eu-west-3', 'France Central'),
    ('ES', 'Spain', 'Madrid', 'Spain', 'ES', 40.4168, -3.7038, 'REE', 'GCP, Azure', 'europe-southwest1', '', 'Spain Central'),

    # Europe - Central
    ('DE', 'Germany', 'Frankfurt', 'Germany', 'DE', 52.5200, 13.4050, '50Hertz/Amprion/TenneT/TransnetBW', 'GCP, AWS, Azure', 'europe-west3', 'eu-central-1', 'Germany West Central'),
    ('CH', 'Switzerland', 'Zurich', 'Switzerland', 'CH', 47.3769, 8.5417, 'Swissgrid', 'GCP, AWS, Azure', 'europe-west6', 'eu-central-2', 'Switzerland North'),
    ('AT', 'Austria', 'Vienna', 'Austria', 'AT', 48.2082, 16.3738, 'APG', 'Azure', '', '', 'Austria East'),
    ('PL', 'Poland', 'Warsaw', 'Poland', 'PL', 52.2297, 21.0122, 'PSE', 'GCP, Azure', 'europe-central2', '', 'Poland Central'),

    # Europe - Northern
    ('SE', 'Sweden', 'Stockholm', 'Sweden', 'SE', 59.3293, 18.0686, 'Svenska Kraftnät', 'GCP, Azure', 'europe-north1', '', 'Sweden Central'),
    ('NO', 'Norway', 'Oslo', 'Norway', 'NO', 59.9139, 10.7522, 'Statnett', 'Azure', '', '', 'Norway East'),
    ('FI', 'Finland', 'Helsinki', 'Finland', 'FI', 60.1699, 24.9384, 'Fingrid', 'GCP, AWS, Azure', 'europe-north1', 'eu-north-1', 'Finland'),
    ('DK', 'Denmark', 'Copenhagen', 'Denmark', 'DK', 55.6761, 12.5683, 'Energinet', 'Azure', '', '', 'Denmark East'),

    # Europe - Southern
    ('IT', 'Italy', 'Milan', 'Italy', 'IT', 41.9028, 12.4964, 'Terna', 'GCP, AWS, Azure', 'europe-west8', 'eu-south-1', 'Italy North'),

    # Middle East
    ('AE', 'United Arab Emirates', 'Dubai', 'United Arab Emirates', 'AE', 25.2048, 55.2708, 'DEWA/TRANSCO', 'GCP, AWS, Azure', 'me-west1', 'me-south-1', 'UAE North'),
    ('IL', 'Israel', 'Tel Aviv', 'Israel', 'IL', 32.0853, 34.7818, 'Israel Electric Corporation', 'GCP, AWS, Azure', 'me-west1', 'il-central-1', 'Israel Central'),
    ('BH', 'Bahrain', 'Manama', 'Bahrain', 'BH', 26.0667, 50.5577, 'EWA', 'AWS', '', 'me-south-1', ''),
    ('SA', 'Saudi Arabia', 'Riyadh', 'Saudi Arabia', 'SA', 24.7136, 46.6753, 'SEC', 'Azure', '', '', 'Saudi Arabia'),

    # Asia - East Asia
    ('JP-TK', 'Japan Tokyo', 'Tokyo', 'Japan', 'JP', 35.6762, 139.6503, 'TEPCO', 'GCP, AWS, Azure', 'asia-northeast1', 'ap-northeast-1', 'Japan East'),
    ('JP-OS', 'Japan Osaka', 'Osaka', 'Japan', 'JP', 34.6937, 135.5023, 'KEPCO', 'GCP, AWS, Azure', 'asia-northeast2', 'ap-northeast-3', 'Japan West'),
    ('KR', 'South Korea', 'Seoul', 'South Korea', 'KR', 37.5665, 126.9780, 'KPX', 'GCP, AWS, Azure', 'asia-northeast3', 'ap-northeast-2', 'Korea Central'),
    ('TW', 'Taiwan', 'Taipei', 'Taiwan', 'TW', 25.0330, 121.5654, 'Taipower', 'GCP, Azure', 'asia-east1', '', 'Taiwan'),
    ('HK', 'Hong Kong', 'Hong Kong', 'Hong Kong', 'HK', 22.3193, 114.1694, 'CLP/HEC', 'GCP, AWS, Azure', 'asia-east2', 'ap-east-1', 'Hong Kong'),

    # Asia - Southeast Asia
    ('SG', 'Singapore', 'Singapore', 'Singapore', 'SG', 1.3521, 103.8198, 'EMA', 'GCP, AWS, Azure', 'asia-southeast1', 'ap-southeast-1', 'Southeast Asia'),
    ('ID', 'Indonesia', 'Jakarta', 'Indonesia', 'ID', -6.2088, 106.8456, 'PLN', 'GCP, AWS, Azure', 'asia-southeast2', 'ap-southeast-3', 'Indonesia'),
    ('MY', 'Malaysia', 'Kuala Lumpur', 'Malaysia', 'MY', 3.1390, 101.6869, 'TNB', 'Azure', '', '', 'Malaysia South'),
    ('TH', 'Thailand', 'Bangkok', 'Thailand', 'TH', 13.7563, 100.5018, 'EGAT', 'AWS', '', 'ap-southeast-4', ''),

    # Asia - South Asia
    ('IN-MH', 'India Mumbai', 'Mumbai', 'India', 'IN', 19.0760, 72.8777, 'MSETCL', 'GCP, AWS, Azure', 'asia-south1', 'ap-south-1', 'Central India'),
    ('IN-TG', 'India Hyderabad', 'Hyderabad', 'India', 'IN', 17.3850, 78.4867, 'TSTRANSCO', 'GCP, AWS, Azure', 'asia-south2', 'ap-south-2', 'South India'),
    ('IN-DL', 'India Delhi', 'Delhi', 'India', 'IN', 28.7041, 77.1025, 'POSOCO', 'GCP, Azure', 'asia-south2', '', 'North India'),

    # Oceania
    ('AU-NSW', 'Australia NSW', 'Sydney', 'Australia', 'AU', -33.8688, 151.2093, 'AEMO', 'GCP, AWS, Azure', 'australia-southeast1', 'ap-southeast-2', 'Australia East'),
    ('AU-VIC', 'Australia Victoria', 'Melbourne', 'Australia', 'AU', -37.8136, 144.9631, 'AEMO', 'GCP, Azure', 'australia-southeast2', '', 'Australia Southeast'),
    ('NZ', 'New Zealand', 'Auckland', 'New Zealand', 'NZ', -36.8485, 174.7633, 'Transpower', 'Azure', '', '', 'New Zealand North'),

    # Africa
    ('ZA', 'South Africa', 'Johannesburg', 'South Africa', 'ZA', -33.9249, 18.4241, 'Eskom', 'GCP, AWS, Azure', 'africa-south1', 'af-south-1', 'South Africa North'),
]

conn.executemany("""
    INSERT INTO dim_grid_regions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", regions_data)

print(f"  ✓ Created {len(regions_data)} region mappings")

# fact_cloud_carbon (no schema prefix)
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
    'GCP': ['us-central1', 'europe-west1'],
    'AWS': ['us-east-1', 'eu-west-1'],
    'Azure': ['eastus', 'westeurope']
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
# Comprehensive datacenter regions covering all major cloud providers
zones = [
    # North America - United States
    'US-CA-CISO',    # California (GCP us-west1, AWS us-west-1, Azure West US)
    'US-OR',         # Oregon (GCP us-west2, AWS us-west-2, Azure West US 2)
    'US-VA-PJM',     # Virginia (AWS us-east-1, Azure East US)
    'US-NC',         # North Carolina (GCP us-east1, Azure East US 2)
    'US-OH',         # Ohio (AWS us-east-2, Azure Central US)
    'US-TX-ERCOT',   # Texas (GCP us-south1, Azure South Central US)
    'US-IA-MISO',    # Iowa (GCP us-central1, Azure North Central US)
    'US-NV',         # Nevada (GCP us-west4, Azure West US 3)
    'US-FL',         # Florida (Azure Florida)

    # North America - Canada
    'CA-ON',         # Ontario (GCP northamerica-northeast1, Azure Canada Central)
    'CA-QC',         # Quebec (GCP northamerica-northeast2, Azure Canada East)
    'CA-AB',         # Alberta (Calgary)

    # South America
    'BR-SP',         # Brazil São Paulo (GCP southamerica-east1, AWS sa-east-1, Azure Brazil South)
    'CL',            # Chile Santiago (AWS sa-east-2)

    # Europe - Western
    'GB',            # United Kingdom (GCP europe-west2, AWS eu-west-2, Azure UK South)
    'IE',            # Ireland (GCP europe-west1, AWS eu-west-1, Azure North Europe)
    'NL',            # Netherlands (GCP europe-west4, Azure West Europe)
    'BE',            # Belgium (GCP europe-west1, Azure West Europe)
    'FR',            # France (GCP europe-west9, AWS eu-west-3, Azure France Central)
    'ES',            # Spain (GCP europe-southwest1, Azure Spain Central)

    # Europe - Central
    'DE',            # Germany (GCP europe-west3, AWS eu-central-1, Azure Germany West Central)
    'CH',            # Switzerland (GCP europe-west6, AWS eu-central-2, Azure Switzerland North)
    'AT',            # Austria (Azure Austria East)
    'PL',            # Poland (GCP europe-central2, Azure Poland Central)

    # Europe - Northern
    'SE',            # Sweden (GCP europe-north1, Azure Sweden Central)
    'NO',            # Norway (Azure Norway East)
    'FI',            # Finland (GCP europe-north1, AWS eu-north-1, Azure Finland)
    'DK',            # Denmark (Azure Denmark East)

    # Europe - Southern
    'IT',            # Italy (GCP europe-west8, AWS eu-south-1, Azure Italy North)

    # Middle East
    'AE',            # UAE Dubai (GCP me-west1, AWS me-south-1, Azure UAE North)
    'IL',            # Israel (GCP me-west1, AWS il-central-1, Azure Israel Central)
    'BH',            # Bahrain (AWS me-south-1)
    'SA',            # Saudi Arabia (Azure Saudi Arabia)

    # Asia - East Asia
    'JP-TK',         # Japan Tokyo (GCP asia-northeast1, AWS ap-northeast-1, Azure Japan East)
    'JP-OS',         # Japan Osaka (GCP asia-northeast2, AWS ap-northeast-3, Azure Japan West)
    'KR',            # South Korea Seoul (GCP asia-northeast3, AWS ap-northeast-2, Azure Korea Central)
    'TW',            # Taiwan (GCP asia-east1, Azure Taiwan)
    'HK',            # Hong Kong (GCP asia-east2, AWS ap-east-1, Azure Hong Kong)

    # Asia - Southeast Asia
    'SG',            # Singapore (GCP asia-southeast1, AWS ap-southeast-1, Azure Southeast Asia)
    'ID',            # Indonesia Jakarta (GCP asia-southeast2, AWS ap-southeast-3, Azure Indonesia)
    'MY',            # Malaysia (Azure Malaysia South)
    'TH',            # Thailand (AWS ap-southeast-4)

    # Asia - South Asia
    'IN-MH',         # India Mumbai (GCP asia-south1, AWS ap-south-1, Azure Central India)
    'IN-TG',         # India Hyderabad (GCP asia-south2, AWS ap-south-2, Azure South India)
    'IN-DL',         # India Delhi (GCP asia-south2, Azure North India)

    # Oceania
    'AU-NSW',        # Australia Sydney (GCP australia-southeast1, AWS ap-southeast-2, Azure Australia East)
    'AU-VIC',        # Australia Melbourne (GCP australia-southeast2, Azure Australia Southeast)
    'NZ',            # New Zealand (Azure New Zealand North)

    # Africa
    'ZA',            # South Africa (GCP africa-south1, AWS af-south-1, Azure South Africa North)
]
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

# Verify
count = conn.execute('SELECT COUNT(*) FROM fact_cloud_carbon').fetchone()[0]
print(f"\n✓ Created {count} cloud carbon records")

count = conn.execute('SELECT COUNT(*) FROM fact_grid_intensity').fetchone()[0]
print(f"✓ Created {count} grid intensity records")

count = conn.execute('SELECT COUNT(*) FROM carbon_trends_monthly').fetchone()[0]
print(f"✓ Created {count} trend records")

conn.close()

print(f"\n✓ Evidence warehouse created at {warehouse_path}")
print("  Ready for Evidence dashboard build!")
