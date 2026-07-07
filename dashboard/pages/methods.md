# Methodology

Data sources, calculations, and implementation details for the ESG Carbon Tracker dashboard.

## Data Sources

### Cloud Provider Carbon Footprint Data

| Provider | API/Service | Update Frequency | Scope Coverage | Latency |
|----------|------------|------------------|----------------|---------|
| **Google Cloud** | [Carbon Footprint](https://cloud.google.com/carbon-footprint) via BigQuery | Monthly | Scopes 1, 2, 3 | 45-60 days |
| **AWS** | [Customer Carbon Footprint](https://aws.amazon.com/aws-cost-management/aws-customer-carbon-footprint-tool/) | Monthly | Scopes 1, 2, 3 | ~21 days |
| **Azure** | [Carbon Optimization](https://learn.microsoft.com/en-us/azure/carbon-optimization/) | Monthly | Location-based | 19-30 days |

**Sample Data**: This dashboard uses synthetic sample data generated to match the structure and patterns of real cloud carbon reports.

### Grid Carbon Intensity Data

| Source | Coverage | Update Frequency | Metrics |
|--------|----------|------------------|---------|
| **Electricity Maps** | 200+ grid zones globally | 5-minute intervals | Carbon intensity, fuel mix |
| **WattTime** | North America | 5-minute MOER | Marginal emissions rate |
| **IESO** (Ontario) | Ontario grid | 5-minute intervals | Generation mix, demand |

**Sample Data**: Grid intensity data is generated from historical patterns and typical grid compositions.

### Emission Factors & Regional Metadata

- **[Cloud Carbon Footprint (CCF)](https://github.com/cloud-carbon-footprint/cloud-carbon-footprint)** - Instance types, storage coefficients, embodied emissions
- **[Green Software Foundation Real-Time Cloud](https://github.com/Green-Software-Foundation/real-time-cloud)** - PUE, WUE, CFE% by datacenter region

## Calculations

### Cloud Emissions

Cloud provider APIs report emissions in three scopes following the [GHG Protocol](https://ghgprotocol.org/):

```
Total Emissions = Scope 1 + Scope 2 (Market-Based) + Scope 3
```

- **Scope 1**: Direct emissions from owned/controlled sources (backup generators, company vehicles)
- **Scope 2**: Indirect emissions from purchased electricity
  - **Location-based**: Uses average grid emission factor
  - **Market-based**: Accounts for renewable energy purchases (RECs, PPAs)
- **Scope 3**: Indirect emissions from value chain (embodied emissions from servers/networking equipment)

### Grid Carbon Intensity

Daily average calculated from hourly readings:

```sql
avg_carbon_intensity = AVG(carbon_intensity_gco2eq_per_kwh)
  WHERE timestamp_hour IN (date's 24 hours)
```

**Peak vs Off-Peak**:
- Peak hours: 7am-11pm
- Off-peak hours: 11pm-7am

**Cleanliness Categories**:
- Very Low: < 100 gCO2eq/kWh
- Low: 100-250 gCO2eq/kWh
- Medium: 250-400 gCO2eq/kWh
- High: 400-600 gCO2eq/kWh
- Very High: > 600 gCO2eq/kWh

### Datacenter-Grid Region Mapping

Cloud datacenters are mapped to their corresponding electricity grid regions based on:
1. **Geographic location** of the datacenter
2. **Utility service territory** or ISO/RTO that operates the local grid
3. **Publicly available** datacenter location data from cloud providers

Example mappings:
- GCP `us-central1` (Iowa) → MISO grid region
- AWS `us-east-1` (Virginia) → PJM grid region
- Azure `westeurope` (Netherlands) → TenneT grid region

## Data Pipeline Architecture

```
┌─────────────────────────┐
│  Cloud Provider APIs    │
│  (GCP, AWS, Azure)      │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  dlt (Data Pipelines)   │
│  - Extract & Load       │
│  - Incremental updates  │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  DuckDB Warehouse       │
│  - Fact tables          │
│  - Dimension tables     │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  dbt Transformations    │
│  - Staging models       │
│  - Marts (aggregates)   │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│  Evidence Dashboard     │
│  (This interface)       │
└─────────────────────────┘
```

### Technologies Used

- **[dlt (data load tool)](https://dlthub.com/)** - Extract data from cloud APIs
- **[DuckDB](https://duckdb.org/)** - Embedded analytical database
- **[dbt](https://www.getdbt.com/)** - Transform raw data into analytics-ready models
- **[Evidence](https://evidence.dev/)** - Build this dashboard with SQL + Markdown

## Code Repository

Full source code, data models, and pipeline configurations:

**[github.com/ryanfobel/esg-carbon-tracker](https://github.com/ryanfobel/esg-carbon-tracker)**

### Key Components

- `pipelines/` - dlt pipeline code for each data source
- `pipelines/dbt/models/` - dbt transformation models
  - `staging/` - Clean and normalize raw data
  - `marts/carbon/` - Cloud emissions analytics
  - `marts/grid/` - Grid intensity analytics
- `dashboard/` - Evidence dashboard (this interface)
- `warehouse/` - DuckDB database files

### Data Models

**Fact Tables**:
- `fact_cloud_carbon` - Cloud emissions by provider, region, service, month
- `fact_grid_intensity` - Grid carbon intensity by region, hour

**Dimension Tables**:
- `dim_grid_regions` - Grid region metadata, datacenter mappings

**Aggregates**:
- `grid_intensity_daily` - Daily averages with peak/off-peak analysis
- `grid_intensity_monthly` - Monthly aggregates
- `carbon_trends_monthly` - Month-over-month emission trends

## Data Quality & Limitations

### Sample Data Disclaimer

⚠️ **This dashboard uses synthetic sample data** generated to demonstrate the system architecture and analytical capabilities. The data is modeled after real cloud carbon reports but is not actual production data.

To use with real data:
1. Configure cloud provider API credentials
2. Run pipelines: `cd pipelines && python pipelines/gcp_carbon.py YOUR_PROJECT_ID`
3. Run dbt: `dbt run --project-dir dbt`
4. Refresh dashboard

### Data Quality Checks

Automated validation runs on every build:
- Table existence checks
- Column name validation
- Non-null constraints on key fields
- Emissions values >= 0
- Date ranges within expected bounds

Run validation: `cd pipelines && python validate_schema.py`

### Known Limitations

1. **Latency**: Cloud provider data has 19-60 day delay from month-end
2. **Scope Coverage**: Some providers report limited scope breakdowns
3. **Grid Mapping**: Datacenter→Grid region mappings are approximate and based on public information
4. **Sample Data**: Current dashboard uses synthetic data for demonstration

## References

### Standards & Frameworks

- [GHG Protocol](https://ghgprotocol.org/) - Greenhouse gas accounting standards
- [Green Software Foundation](https://greensoftware.foundation/) - Software carbon intensity (SCI) specification
- [ISO 14064](https://www.iso.org/standard/66453.html) - Greenhouse gas accounting and verification

### Cloud Provider Documentation

- [Google Cloud Carbon Footprint](https://cloud.google.com/carbon-footprint/docs)
- [AWS Customer Carbon Footprint Tool](https://aws.amazon.com/aws-cost-management/aws-customer-carbon-footprint-tool/)
- [Azure Carbon Optimization](https://learn.microsoft.com/en-us/azure/carbon-optimization/overview)

### Open Data & Tools

- [Cloud Carbon Footprint](https://www.cloudcarbonfootprint.org/) - Open-source cloud carbon estimation
- [Electricity Maps](https://www.electricitymaps.com/) - Real-time carbon intensity
- [WattTime](https://www.watttime.org/) - Grid optimization for emissions reduction

---

**Questions or Issues?** [Open an issue on GitHub](https://github.com/ryanfobel/esg-carbon-tracker/issues)
