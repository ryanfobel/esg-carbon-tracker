# ESG Data Pipelines

Multi-cloud carbon footprint and sustainability metrics pipelines using dlt + dbt + Paimon.

## Architecture

Based on: `docs/architecture/esg-data-pipeline.md`

**Stack:**
- **Ingestion**: dlt (data load tool)
- **Warehouse**: Apache Paimon (via DuckDB)
- **Transform**: dbt (data build tool)
- **Query**: DuckDB
- **Dashboards**: Evidence.dev

## Data Sources

### Cloud Providers
1. **GCP Carbon Footprint** - BigQuery export, Scopes 1-3
2. **AWS Sustainability API** - boto3 API, Scopes 1-3
3. **Azure Carbon Insights** - REST API, Scopes 1-3

### Open-Source Data
4. **Cloud Carbon Footprint (CCF)** - Emission factor tables
5. **GSF Real Time Cloud (RTC)** - Regional metadata (PUE, WUE, CFE)
6. **Electricity Maps** - Real-time grid carbon intensity
7. **WattTime** - Marginal emissions rates

## Project Structure

```
esg-pipelines/
├── pipelines/              # dlt pipeline definitions
│   ├── gcp_carbon.py
│   ├── aws_carbon.py
│   ├── azure_carbon.py
│   ├── ccf_factors.py
│   ├── rtc_metadata.py
│   ├── electricity_maps.py
│   └── watttime.py
├── dbt/                    # dbt transformation models
│   ├── models/
│   │   ├── staging/       # Normalize raw data
│   │   └── marts/         # Business logic
│   ├── dbt_project.yml
│   └── profiles.yml
├── config/                 # Pipeline configurations
│   ├── gcp.yaml
│   ├── aws.yaml
│   └── azure.yaml
├── tests/                  # Integration tests
└── README.md
```

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install dlt[duckdb] dbt-duckdb pydantic pyyaml

# Or use pixi
cd projects/esg-pipelines
pixi install
```

### Run Pipelines

```bash
# Run GCP Carbon Footprint pipeline
python pipelines/gcp_carbon.py

# Run all pipelines
./run_all.sh

# Schedule with cron (daily at 2 AM)
# 0 2 * * * cd /path/to/esg-pipelines && ./run_all.sh
```

### Transform with dbt

```bash
cd dbt
dbt run  # Run all models
dbt test # Run data quality tests
```

### Query Data

```bash
# Using DuckDB CLI
duckdb ~/.paimon/esg_data/warehouse.duckdb

# Or use dt CLI
dt query "SELECT * FROM marts.carbon_intensity_by_region LIMIT 10"
```

## Configuration

### Credentials

Store API credentials securely using system keystore:

```bash
# GCP
dt keystore set gcp.service_account_json /path/to/key.json

# AWS
dt keystore set aws.access_key_id YOUR_KEY
dt keystore set aws.secret_access_key YOUR_SECRET

# Azure
dt keystore set azure.client_id YOUR_CLIENT_ID
dt keystore set azure.client_secret YOUR_SECRET
dt keystore set azure.tenant_id YOUR_TENANT
```

### Pipeline Config

Edit `config/*.yaml` to customize:
- Refresh schedules
- Incremental loading settings
- Data retention policies

Example `config/gcp.yaml`:
```yaml
source: gcp_carbon_footprint
schedule: monthly
incremental: true
lookback_months: 3
destination:
  warehouse: ~/.paimon/esg_data
  table: raw.gcp_carbon_footprint
```

## Data Schema

### Raw Tables (dlt output)
- `raw.gcp_carbon_footprint`
- `raw.aws_carbon_footprint`
- `raw.azure_carbon_insights`
- `raw.ccf_coefficients`
- `raw.rtc_region_metadata`
- `raw.electricity_maps`
- `raw.watttime`

### Staging Tables (dbt normalized)
- `staging.cloud_emissions_normalized`
- `staging.grid_intensity_normalized`

### Marts (dbt business logic)
- `marts.carbon_intensity_by_region`
- `marts.cloud_emissions_by_service`
- `marts.wue_by_datacenter`
- `marts.cfe_progress`

## Dashboards

View data in Evidence.dev dashboards:

```bash
cd ../esg-evidence
npm run dev
# Open http://localhost:3000
```

See bead: `open-data-coop-6k7`

## Development

### Add New Pipeline

1. Create pipeline file: `pipelines/new_source.py`
2. Define dlt resource with incremental loading
3. Add config: `config/new_source.yaml`
4. Add dbt staging model: `dbt/models/staging/stg_new_source.sql`
5. Update mart models to include new data
6. Add tests
7. Update this README

### Testing

```bash
# Run pipeline tests
pytest tests/

# Test dbt models
cd dbt && dbt test

# Validate data quality
python tests/validate_data_quality.py
```

## References

- Architecture: `docs/architecture/esg-data-pipeline.md`
- dlt docs: https://dlthub.com/docs
- dbt docs: https://docs.getdbt.com
- Paimon docs: https://paimon.apache.org
- Evidence docs: https://docs.evidence.dev

## Related Beads

- `open-data-coop-6w3`: ESG pipeline architecture design
- `open-data-coop-i6n`: Cloud provider pipelines
- `open-data-coop-eb1`: Open-source data pipelines
- `open-data-coop-sl6`: dbt transformation models
- `open-data-coop-6k7`: Evidence.dev ESG dashboard
