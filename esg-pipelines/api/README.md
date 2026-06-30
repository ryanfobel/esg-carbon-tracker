# ESG Data API

REST API for querying and exporting ESG carbon footprint data from the DuckDB/Paimon warehouse.

## Features

- **REST API**: Query cloud carbon and grid intensity data
- **Parquet Export**: Download full tables as Parquet files
- **CSV Export**: Download data as CSV (with limits)
- **Direct SQL**: Execute read-only SQL queries
- **OpenAPI Docs**: Interactive documentation at `/docs`

## Installation

```bash
cd projects/esg-pipelines/api
pip install -r requirements.txt
```

## Running the API

```bash
# Development server
uvicorn api.main:app --reload --port 8000

# Production server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Cloud Carbon

- `GET /api/v1/carbon/cloud` - Query cloud carbon footprint data
  - Filters: provider, start_month, end_month, account_id, service_name, region
  - Returns: Unified emissions across GCP, AWS, Azure

- `GET /api/v1/carbon/cloud/summary` - Get summarized metrics
  - Returns: Totals and averages by provider

### Grid Intensity

- `GET /api/v1/carbon/grid` - Query grid carbon intensity
  - Filters: region, source, start_time, end_time
  - Returns: Hourly grid data from Electricity Maps and WattTime

- `GET /api/v1/carbon/grid/current` - Get current grid intensity
  - Returns: Most recent reading for each region

### Trends

- `GET /api/v1/carbon/trends` - Get monthly carbon trends
  - Returns: MoM changes, rolling averages, YTD totals

### Exports

- `GET /api/v1/exports/parquet/{table}` - Export table as Parquet
  - Tables: `cloud_carbon`, `grid_intensity`, `trends`

- `GET /api/v1/exports/csv/{table}` - Export table as CSV
  - Limited to 100k rows

### Advanced

- `GET /api/v1/query?sql=SELECT...` - Execute custom SQL query
  - Read-only SELECT statements only
  - Supports JSON or CSV output

## Example Queries

### Get AWS emissions for last 3 months

```bash
curl "http://localhost:8000/api/v1/carbon/cloud?provider=AWS&start_month=2026-04-01&end_month=2026-06-30"
```

### Get current grid intensity in California

```bash
curl "http://localhost:8000/api/v1/carbon/grid/current?region=CAISO"
```

### Download cloud carbon as Parquet

```bash
curl -O "http://localhost:8000/api/v1/exports/parquet/cloud_carbon"
```

### Execute custom SQL query

```bash
curl "http://localhost:8000/api/v1/query?sql=SELECT%20cloud_provider,%20SUM(total_mtco2e)%20FROM%20marts.fact_cloud_carbon%20GROUP%20BY%201"
```

## Documentation

Interactive OpenAPI documentation: http://localhost:8000/docs
ReDoc documentation: http://localhost:8000/redoc

## Security

- All database connections are read-only
- Only SELECT queries allowed in `/query` endpoint
- CORS enabled (configure for production)

## Integration with Evidence.dev

Evidence can query this API directly or connect to the DuckDB warehouse:

```yaml
# evidence.config.yaml
sources:
  esg_api:
    type: rest
    endpoint: http://localhost:8000/api/v1

  esg_warehouse:
    type: duckdb
    filename: ~/.paimon/esg_data/warehouse.duckdb
```

## Integration with Data Toolbox

The API supports Paimon distribution workflow:

```bash
# Clone ESG data via API
dt clone esg-data http://localhost:8000/api/v1/exports/parquet

# Or query directly
dt query "SELECT * FROM marts.fact_cloud_carbon" --source esg-api
```
