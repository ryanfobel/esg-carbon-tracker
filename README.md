# ESG Carbon Tracker

Open-source carbon emissions tracking and analytics for cloud infrastructure and grid electricity.

## Features

- **Multi-Cloud Carbon Footprints**: Automated data pipelines for AWS, GCP, and Azure carbon emissions
- **Grid Carbon Intensity**: Real-time and historical grid emissions data from WattTime and Electricity Maps
- **Cloud Carbon Footprint (CCF)**: Integration with the open-source CCF tool
- **Data Warehouse**: DuckDB-based analytical warehouse with dbt transformations
- **REST API**: FastAPI service for querying carbon metrics
- **Interactive Dashboard**: Evidence.dev dashboard for visualization and reporting

## Live Dashboard

View the live dashboard at: [https://YOUR-USERNAME.github.io/esg-carbon-tracker/](https://YOUR-USERNAME.github.io/esg-carbon-tracker/)

## Quick Start

### 1. Generate Sample Data

```bash
# Install dependencies
cd esg-pipelines
pixi install

# Generate sample warehouse
python init_sample_warehouse.py
```

This creates a sample DuckDB warehouse at `~/.paimon/esg_data/warehouse.duckdb` with:
- 6 months of multi-cloud carbon data
- 7 days of grid intensity data
- Pre-aggregated monthly trends

### 2. View the Dashboard

```bash
cd esg-evidence/esg-evidence-new
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the dashboard.

## Project Structure

```
esg-carbon-tracker/
├── esg-pipelines/           # Data ingestion and transformation
│   ├── pipelines/           # dlt pipelines for data extraction
│   │   ├── aws_carbon.py    # AWS Customer Carbon Footprint Tool
│   │   ├── gcp_carbon.py    # GCP Carbon Footprint API
│   │   ├── azure_carbon.py  # Azure Emissions API
│   │   ├── ccf_carbon.py    # Cloud Carbon Footprint tool
│   │   ├── watttime.py      # WattTime grid intensity
│   │   └── electricity_maps.py  # Electricity Maps API
│   ├── dbt/                 # Data transformations
│   │   ├── models/staging/  # Raw data cleaning
│   │   └── models/marts/    # Analytical models
│   ├── api/                 # FastAPI REST service
│   └── init_sample_warehouse.py  # Sample data generator
├── esg-evidence/            # Evidence.dev dashboard
│   └── esg-evidence-new/    # Dashboard source
└── .github/workflows/       # CI/CD for GitHub Pages
```

## Data Pipelines

### Prerequisites

- Python 3.11+
- [Pixi](https://pixi.sh/) package manager
- Cloud provider credentials (for real data)

### Running Pipelines

```bash
cd esg-pipelines

# Run all pipelines
pixi run all-pipelines

# Run individual pipelines
pixi run pipeline-aws
pixi run pipeline-gcp
pixi run pipeline-azure
pixi run pipeline-ccf
pixi run pipeline-watttime
pixi run pipeline-electricity-maps

# Run dbt transformations
pixi run dbt-run

# Start API server
pixi run api
```

### Authentication

Pipelines support multiple authentication methods:

1. **Environment Variables**: Set credentials in your shell
2. **Cloud SDK**: Use `gcloud`, `aws configure`, `az login`
3. **Keystore**: Store credentials securely (see individual pipeline docs)

See [esg-pipelines/README.md](esg-pipelines/README.md) for detailed authentication instructions.

## REST API

The FastAPI service provides endpoints for querying carbon metrics:

```bash
cd esg-pipelines
pixi run api
```

### Endpoints

- `GET /cloud-carbon` - Cloud provider emissions
- `GET /cloud-carbon/trends` - Monthly trends
- `GET /grid-intensity` - Grid carbon intensity
- `GET /grid-intensity/latest` - Current grid intensity
- `GET /export/json` - Export all data as JSON
- `GET /export/csv` - Export as CSV
- `GET /export/parquet` - Export as Parquet

API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## Dashboard

The Evidence.dev dashboard provides:

- **Overview**: Total emissions, monthly trends, scope breakdowns
- **Cloud Providers**: Emissions by provider, service, and region
- **Grid Intensity**: Real-time and historical grid carbon intensity
- **Trends**: Month-over-month changes, rolling averages, YTD totals

### Local Development

```bash
cd esg-evidence/esg-evidence-new
npm install
npm run dev
```

### Production Build

```bash
npm run build
```

The static site is generated in `build/` and can be deployed anywhere.

## GitHub Pages Deployment

The repository includes a GitHub Actions workflow that automatically:

1. Generates sample warehouse data
2. Builds the Evidence dashboard
3. Deploys to GitHub Pages

To enable:

1. Go to **Settings → Pages**
2. Set **Source** to "GitHub Actions"
3. Push to main branch

The dashboard will be live at `https://YOUR-USERNAME.github.io/esg-carbon-tracker/`

## Data Models

### Raw Layer

Direct extraction from source APIs:
- `raw.aws_carbon_footprint`
- `raw.gcp_carbon_footprint`
- `raw.azure_emissions`
- `raw.ccf_emissions`
- `raw.watttime_moer`
- `raw.electricity_maps_carbon_intensity`

### Staging Layer

Cleaned and normalized data:
- `staging.stg_aws_carbon`
- `staging.stg_gcp_carbon`
- `staging.stg_azure_carbon`
- `staging.stg_ccf_carbon`
- `staging.stg_watttime`
- `staging.stg_electricity_maps`

### Marts Layer

Analytical models:
- `marts.fact_cloud_carbon` - Unified cloud emissions across all providers
- `marts.fact_grid_intensity` - Grid carbon intensity metrics
- `marts.carbon_trends_monthly` - Aggregated monthly trends

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/) - Open-source CCF methodology
- [WattTime](https://www.watttime.org/) - Real-time grid emissions data
- [Electricity Maps](https://www.electricitymaps.com/) - Global grid carbon intensity
- [Evidence.dev](https://evidence.dev/) - Dashboard framework
- [dlt](https://dlthub.com/) - Data pipeline framework
- [dbt](https://www.getdbt.com/) - Data transformation framework

## Related Projects

- [Cloud Carbon Footprint](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint)
- [carbon-aware-sdk](https://github.com/Green-Software-Foundation/carbon-aware-sdk)
- [grid-intensity-go](https://github.com/thegreenwebfoundation/grid-intensity-go)

## Support

- [Issues](https://github.com/YOUR-USERNAME/esg-carbon-tracker/issues)
- [Discussions](https://github.com/YOUR-USERNAME/esg-carbon-tracker/discussions)
