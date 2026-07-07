# ESG Carbon Tracker

Publication-quality carbon emissions tracking and analytics for cloud infrastructure and electrical grid intensity.

## Features

- **Multi-Cloud Carbon Footprints**: Track emissions across AWS, GCP, and Azure with Scope 1/2/3 breakdown
- **Global Grid Carbon Intensity**: Real-time and historical data for 51 regions across 6 continents
- **Comprehensive Grid Mappings**: Dimension table linking electrical grid operators to cloud datacenter regions
- **Interactive Visualizations**: Geographic maps, time-series trends, and detailed drill-down tables
- **Documented Methodology**: Publication-quality documentation of data sources, calculations, and mappings
- **Static Dashboard**: Fast, lightweight Evidence.dev dashboard deployable to GitHub Pages

## Live Dashboard

View the live dashboard at: [https://ryanfobel.github.io/esg-carbon-tracker/](https://ryanfobel.github.io/esg-carbon-tracker/)

## Methodology

See [METHODOLOGY.md](METHODOLOGY.md) for comprehensive documentation of:
- Data sources and update frequencies
- Grid region to cloud datacenter mapping approach
- Carbon intensity calculations and categorization
- Quality standards and limitations
- References and attribution

## Quick Start

### Prerequisites

- [Pixi](https://pixi.sh/) package manager (includes Python and Node.js)
- Git

### 1. Clone and Setup

```bash
git clone https://github.com/ryanfobel/esg-carbon-tracker.git
cd esg-carbon-tracker
pixi install
```

### 2. Generate Sample Data

```bash
pixi run generate
```

This creates a sample DuckDB warehouse at `warehouse/esg_data.duckdb` with:
- 6 months of multi-cloud carbon data across AWS, GCP, and Azure
- 30 days of hourly grid intensity data for 51 global regions
- Pre-calculated monthly trends with MoM changes and rolling averages
- Comprehensive dimension table with grid operator to cloud region mappings

### 3. View the Dashboard

```bash
pixi run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the interactive dashboard.

### 4. Build for Production

```bash
pixi run build
```

The static site is generated in `dashboard/build/` and can be deployed to any static hosting service.

## Project Structure

```
esg-carbon-tracker/
├── pipelines/                    # Data generation and ETL
│   └── init_evidence_warehouse.py  # Sample data generator with comprehensive regional coverage
├── dashboard/                    # Evidence.dev dashboard
│   ├── pages/                    # Dashboard pages (index, grid, trends)
│   ├── sources/                  # Data source configurations
│   │   └── esg_data/
│   │       └── connection.yaml   # DuckDB connection to warehouse
│   ├── static/                   # Static assets
│   └── package.json              # Node.js dependencies
├── warehouse/                    # DuckDB analytical database (gitignored)
│   ├── esg_data.duckdb          # Fact and dimension tables
│   └── README.md                 # Data acquisition instructions
├── pixi.toml                     # Pixi environment and task definitions
├── METHODOLOGY.md                # Publication-quality methodology documentation
└── .github/workflows/            # CI/CD for automated GitHub Pages deployment
    └── evidence.yml              # Build and deploy workflow
```

## Available Commands

All commands run via `pixi run <command>`:

- `generate` - Generate sample warehouse data with 51 global regions
- `install` - Install dashboard dependencies (npm)
- `dev` - Start development server with hot reload
- `build` - Build static dashboard for production
- `preview` - Preview production build locally

## Dashboard Pages

### Overview
- Total emissions across all cloud providers
- Monthly trend visualization
- Emissions breakdown by scope (1, 2, 3)
- Provider comparison bar charts

### Grid Intensity
- Real-time carbon intensity for 51 global regions
- 7-day historical trends
- Fuel mix analysis (fossil vs. renewable)
- Interactive geographic bubble map
- Detailed readings table with all metrics

### Trends
- Month-over-month percentage changes
- 3-month rolling averages
- Year-to-date cumulative totals
- Trend indicators (increasing/decreasing/stable)

## Data Schema

### Fact Tables

**fact_cloud_carbon**
- Multi-cloud emissions data (AWS, GCP, Azure)
- Scope 1, 2 (market-based), and 3 breakdowns
- Service-level granularity (Compute, Storage, Networking, AI/ML)
- Monthly aggregation with cost metrics (kgCO2e per dollar)

**fact_grid_intensity**
- Hourly carbon intensity for 51 global regions
- Measured in gCO2eq/kWh
- Fuel mix percentages (fossil vs. renewable)
- Intensity categorization (Very Low to Very High)
- Data source attribution (Electricity Maps, WattTime)

**carbon_trends_monthly**
- Pre-calculated monthly trends
- Month-over-month percentage changes
- 3-month rolling averages
- Year-to-date cumulative totals
- Trend indicators

### Dimension Tables

**dim_grid_regions**
- 51 global regions across 6 continents
- Geographic coordinates (latitude/longitude)
- Grid operator information (ISO/RTO)
- Cloud provider region mappings (GCP, AWS, Azure)
- Country and city metadata

See [METHODOLOGY.md](METHODOLOGY.md) for detailed mapping approach and data quality standards.

## GitHub Pages Deployment

The repository includes a GitHub Actions workflow (`.github/workflows/evidence.yml`) that automatically:

1. Sets up Pixi environment with Python and Node.js
2. Generates sample warehouse data
3. Installs dashboard dependencies
4. Builds static Evidence dashboard
5. Deploys to GitHub Pages

**To enable:**

1. Go to **Settings → Pages**
2. Set **Source** to "GitHub Actions"
3. Push changes to main branch
4. Workflow runs automatically on pushes to `dashboard/` or `pipelines/`

The dashboard will be live at: `https://<username>.github.io/esg-carbon-tracker/`

**Note**: The workflow uses a relative database path (`../../../warehouse/esg_data.duckdb`) and references dimension tables with the `main.` schema prefix for compatibility with Evidence's DuckDB connector.

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

- [Issues](https://github.com/ryanfobel/esg-carbon-tracker/issues)
- [Discussions](https://github.com/ryanfobel/esg-carbon-tracker/discussions)
