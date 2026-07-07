# ESG Carbon Tracker - Methodology

## Overview

This document describes the data collection, processing, and visualization methodology for the ESG Carbon Tracker dashboard. Our goal is to provide accurate, transparent, and actionable carbon emissions data across cloud infrastructure and electrical grid regions.

## Data Sources

### Cloud Carbon Footprint Data

**Primary Sources:**
- [GCP Carbon Footprint](https://cloud.google.com/carbon-footprint) - Google Cloud Platform's official carbon emissions data
- [AWS Customer Carbon Footprint Tool](https://aws.amazon.com/aws-cost-management/aws-customer-carbon-footprint-tool/) - Amazon Web Services emissions tracking
- [Microsoft Cloud for Sustainability](https://www.microsoft.com/en-us/sustainability/cloud) - Azure carbon emissions data
- [Cloud Carbon Footprint (OSS)](https://www.cloudcarbonfootprint.org/) - Open-source multi-cloud carbon estimation tool

**Methodology:**
- Emissions are reported in three scopes following the GHG Protocol:
  - **Scope 1**: Direct emissions from owned/controlled sources
  - **Scope 2 (Market-Based)**: Indirect emissions from purchased electricity
  - **Scope 3**: All other indirect emissions in the value chain
- Data aggregated by cloud provider, account, service, region, and month
- Metrics include kgCO2e per dollar spent and per kWh consumed

### Grid Carbon Intensity Data

**Primary Sources:**
- [Electricity Maps](https://www.electricitymaps.com/) - Real-time grid carbon intensity for 200+ regions
- [WattTime](https://www.watttime.org/) - Grid emissions data with marginal emissions methodology

**Update Frequency:** Hourly

**Methodology:**
- Carbon intensity measured in gCO2eq/kWh (grams CO2 equivalent per kilowatt-hour)
- Fuel mix percentages calculated from generation sources (fossil vs. renewable)
- Intensity categories assigned based on thresholds:
  - Very Low: < 100 gCO2eq/kWh
  - Low: 100-300 gCO2eq/kWh
  - Medium: 300-500 gCO2eq/kWh
  - High: 500-700 gCO2eq/kWh
  - Very High: > 700 gCO2eq/kWh

## Grid Region to Cloud Datacenter Mapping

### Mapping Approach

We maintain a comprehensive dimension table (`dim_grid_regions`) that maps electrical grid operators to cloud provider datacenter regions. This enables accurate carbon intensity attribution for cloud workloads.

**Mapping Criteria:**
1. **Geographic Proximity**: Cloud regions mapped to the grid operator serving that geographic area
2. **Grid Operator Coverage**: Using official ISO/RTO boundaries (CAISO, PJM, ERCOT, etc.)
3. **Cloud Provider Documentation**: Cross-referenced with official datacenter location disclosures

### Regional Coverage

**Total Regions**: 51 global regions across 6 continents

**North America** (12 regions):
- United States: 9 regions covering major ISOs/RTOs (CAISO, PJM, ERCOT, MISO, etc.)
- Canada: 3 regions (Ontario, Quebec, Montreal)

**Europe** (17 regions):
- Coverage includes: UK, Germany, France, Netherlands, Belgium, Finland, Switzerland, Italy, Poland, Ireland, Spain, Sweden, Denmark, Norway, Austria
- Grid operators from ENTSO-E network members

**Asia-Pacific** (14 regions):
- Coverage includes: Singapore, Tokyo, Osaka, Sydney, Mumbai, Delhi, Seoul, Hong Kong, Taiwan, Jakarta, Bangkok, Manila

**Middle East** (4 regions):
- UAE (Dubai), Qatar (Doha), Bahrain, Saudi Arabia (Dammam)

**South America** (2 regions):
- Brazil (São Paulo), Chile (Santiago)

**Africa** (1 region):
- South Africa (Johannesburg)

### Data Quality Standards

1. **Coordinate Accuracy**: Latitude/longitude coordinates represent the approximate center of datacenter clusters within each region
2. **Grid Operator Verification**: All grid operator assignments verified against official ISO/RTO service territories
3. **Cloud Region Mapping**: Cloud provider region codes verified against official documentation (GCP, AWS, Azure)
4. **Update Cadence**: Mappings reviewed quarterly to reflect new datacenter announcements

## Data Processing Pipeline

### Sample Data Generation

For demonstration purposes, we generate realistic sample data that mirrors production data patterns:

**Cloud Carbon Data:**
- 3 cloud providers (GCP, AWS, Azure)
- 6 months of historical data
- Service-level granularity (Compute, Storage, Networking, AI/ML)
- Regional distribution across major cloud regions
- Realistic emission factors based on regional grid intensity

**Grid Intensity Data:**
- Hourly readings for all 51 regions
- 30 days of historical data
- Daily variation patterns (higher fossil fuel usage during peak hours)
- Seasonal trends (renewable percentage varies by time of year)
- Source attribution (Electricity Maps or WattTime)

### Database Schema

**Fact Tables:**
- `fact_cloud_carbon`: Cloud emissions by provider, account, service, region, month
- `fact_grid_intensity`: Hourly grid carbon intensity by region
- `carbon_trends_monthly`: Aggregated trends with MoM changes and rolling averages

**Dimension Tables:**
- `dim_grid_regions`: Comprehensive grid region metadata with coordinates and cloud mappings

### Calculations

**Carbon Trends:**
- Month-over-Month (MoM) % Change: `(current_month - previous_month) / previous_month * 100`
- Rolling 3-Month Average: `AVG(total_mtco2e) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`
- Year-to-Date Total: `SUM(total_mtco2e) OVER (PARTITION BY YEAR(month) ORDER BY month)`
- Trend Indicators:
  - ⬆ Increasing: MoM change > +10%
  - ⬇ Decreasing: MoM change < -10%
  - ⏸ Stable: MoM change between -10% and +10%

**Scope Percentages:**
- Scope 1%: `scope1_kgco2e / total_kgco2e * 100`
- Scope 2%: `scope2_market_based_kgco2e / total_kgco2e * 100`
- Scope 3%: `scope3_kgco2e / total_kgco2e * 100`

## Visualization Framework

### Technology Stack

- **Evidence.dev 40.0.0**: SQL-first dashboard framework
- **DuckDB 2.0.0**: Embedded analytical database
- **Vite 5.4**: Build tool and dev server
- **Svelte**: Component framework
- **GitHub Pages**: Static site hosting with automated CI/CD

### Dashboard Pages

1. **Overview** (`index.md`): Total emissions, provider comparison, monthly trends, scope breakdown
2. **Grid Intensity** (`grid.md`): Real-time intensity, regional comparison, fuel mix, geographic map
3. **Trends** (`trends.md`): Month-over-month changes, rolling averages, year-to-date cumulative

### Key Visualizations

- **BubbleMap**: Geographic distribution of grid carbon intensity with bubble size proportional to intensity
- **LineCharts**: Time-series trends with multi-series support for provider comparison
- **BarCharts**: Regional comparisons and fuel mix stacked bars
- **DataTables**: Detailed drill-down with formatting and sorting

## Limitations and Caveats

1. **Sample Data**: The current implementation uses generated sample data for demonstration. Production deployment requires integration with actual cloud billing APIs and grid intensity feeds.

2. **Grid Mapping Granularity**: Some cloud regions span multiple grid operators. We map to the primary grid serving the datacenter location, which may not capture the full complexity of multi-grid regions.

3. **Scope 3 Estimation**: Scope 3 emissions (embodied carbon) rely on cloud provider estimations and may vary in methodology across providers.

4. **Real-Time Lag**: Grid intensity data typically has a 15-60 minute lag depending on the data source.

5. **Geographic Coverage**: While we cover 51 major regions, some smaller cloud regions may not have corresponding grid intensity data available.

## Future Enhancements

1. **Live Data Integration**: Connect to actual cloud billing APIs and grid intensity feeds
2. **Marginal Emissions**: Incorporate marginal emissions methodology for time-shifting optimization
3. **Carbon-Aware Scheduling**: Recommendations for workload scheduling based on grid forecasts
4. **Cost-Carbon Optimization**: Multi-objective optimization balancing cost and carbon impact
5. **Expanded Coverage**: Additional cloud providers (Oracle, IBM, Alibaba) and grid regions

## References

- [GHG Protocol](https://ghgprotocol.org/) - Greenhouse Gas accounting standards
- [IPCC AR6](https://www.ipcc.ch/report/ar6/) - Climate change science and emissions factors
- [ENTSO-E](https://www.entsoe.eu/) - European grid operator data
- [EIA](https://www.eia.gov/) - U.S. Energy Information Administration grid data
- [Cloud Carbon Footprint Methodology](https://www.cloudcarbonfootprint.org/docs/methodology/) - Open-source carbon estimation methodology

## Version History

- **v1.0** (2026-07-06): Initial release with 51 global regions, comprehensive grid mappings, and publication-quality methodology documentation

## License and Attribution

This project is open source. When using this data or methodology, please attribute:

```
ESG Carbon Tracker - Open Data Coop
https://github.com/[username]/esg-carbon-tracker
```

Data sources should be credited as listed in the respective dashboard pages.
