# Data Warehouse

This directory contains the DuckDB warehouse file used by the Evidence dashboard.

## Why Gitignored?

The warehouse is excluded from version control to:
- **Avoid git bloat** - Binary database files don't belong in git
- **Update data independently** - Refresh data without new commits
- **Support large datasets** - No repo size limits

## Getting Data

### Option 1: Generate Sample Data (Development)
```bash
pixi run generate
```
Creates `esg_data.duckdb` with synthetic data for testing.

### Option 2: Download from Cloud (Production)
```bash
# TODO: Add cloud sync commands
# aws s3 cp s3://bucket/esg_data.duckdb warehouse/
# gcloud storage cp gs://bucket/esg_data.duckdb warehouse/
```

### Option 3: Run Real Pipelines
```bash
# Run data pipelines to fetch actual cloud billing data
pixi run -m pipelines dlt-aws
pixi run -m pipelines dlt-gcp
pixi run -m pipelines dbt-transform
```

## File Structure

```
warehouse/
├── esg_data.duckdb       # Main warehouse (gitignored)
├── esg_data.duckdb.wal   # Write-ahead log (gitignored)
├── .gitignore            # Keep directory structure
└── README.md             # This file
```

## Connection

The Evidence dashboard connects via:
```yaml
# dashboard/sources/esg_data/connection.yaml
filename: ../../../warehouse/esg_data.duckdb
```
