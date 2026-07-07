# Cloud Datacenter Emissions

Carbon footprint of cloud infrastructure by region and datacenter location.

```sql datacenter_emissions
SELECT
    c.cloud_provider,
    c.region as datacenter_region,
    c.service_name,
    SUM(c.total_mtco2e) as total_emissions_mtco2e,
    COUNT(DISTINCT c.usage_month_start) as months_of_data,
    AVG(c.total_mtco2e) as avg_monthly_emissions
FROM esg_data.fact_cloud_carbon c
WHERE c.region IS NOT NULL
GROUP BY c.cloud_provider, c.region, c.service_name
ORDER BY total_emissions_mtco2e DESC
```

```sql datacenter_totals
SELECT
    c.cloud_provider,
    c.region as datacenter_region,
    SUM(c.total_mtco2e) as total_emissions_mtco2e,
    COUNT(DISTINCT c.service_name) as num_services
FROM esg_data.fact_cloud_carbon c
WHERE c.region IS NOT NULL
GROUP BY c.cloud_provider, c.region
ORDER BY total_emissions_mtco2e DESC
```

```sql datacenter_grid_mapping
SELECT
    r.grid_region,
    r.region_name as grid_region_name,
    r.country,
    r.cloud_providers,
    r.gcp_regions,
    r.aws_regions,
    r.azure_regions,
    r.latitude,
    r.longitude
FROM esg_data.dim_grid_regions r
WHERE r.cloud_providers IS NOT NULL
ORDER BY r.grid_region
```

```sql datacenter_with_grid
-- Join cloud emissions with grid region data and calculate average grid intensity
WITH cloud_regions AS (
    SELECT
        cloud_provider,
        region as datacenter_region,
        SUM(total_mtco2e) as total_emissions_mtco2e
    FROM esg_data.fact_cloud_carbon
    WHERE region IS NOT NULL
    GROUP BY cloud_provider, region
),
grid_intensity_avg AS (
    SELECT
        grid_region,
        AVG(avg_intensity) as avg_carbon_intensity,
        CASE
            WHEN AVG(avg_intensity) < 100 THEN 'Very Low'
            WHEN AVG(avg_intensity) < 250 THEN 'Low'
            WHEN AVG(avg_intensity) < 400 THEN 'Medium'
            WHEN AVG(avg_intensity) < 600 THEN 'High'
            ELSE 'Very High'
        END as cleanliness_category
    FROM esg_data.grid_intensity_daily
    GROUP BY grid_region
),
grid_mappings AS (
    SELECT
        r.grid_region,
        r.region_name,
        r.country,
        gi.avg_carbon_intensity,
        gi.cleanliness_category,
        CASE
            WHEN cloud_provider = 'GCP' THEN TRIM(UNNEST(string_split(r.gcp_regions, ',')))
            WHEN cloud_provider = 'AWS' THEN TRIM(UNNEST(string_split(r.aws_regions, ',')))
            WHEN cloud_provider = 'Azure' THEN TRIM(UNNEST(string_split(r.azure_regions, ',')))
        END as datacenter_region,
        cloud_provider,
        r.latitude,
        r.longitude
    FROM esg_data.dim_grid_regions r
    LEFT JOIN grid_intensity_avg gi ON r.grid_region = gi.grid_region
    CROSS JOIN (VALUES ('GCP'), ('AWS'), ('Azure')) AS providers(cloud_provider)
    WHERE r.cloud_providers LIKE '%' || cloud_provider || '%'
)
SELECT
    gm.cloud_provider,
    gm.datacenter_region,
    gm.grid_region,
    gm.region_name as grid_region_name,
    gm.country,
    gm.avg_carbon_intensity as grid_avg_intensity,
    gm.cleanliness_category,
    COALESCE(cr.total_emissions_mtco2e, 0) as total_emissions_mtco2e,
    gm.latitude,
    gm.longitude
FROM grid_mappings gm
LEFT JOIN cloud_regions cr
    ON gm.cloud_provider = cr.cloud_provider
    AND gm.datacenter_region = cr.datacenter_region
WHERE gm.datacenter_region IS NOT NULL AND gm.datacenter_region != ''
ORDER BY total_emissions_mtco2e DESC
```

## Top Emitting Datacenters

<BigValue
    data={datacenter_totals}
    value=total_emissions_mtco2e
    title="Highest Emitting Datacenter"
    fmt="#,##0.00 mtCO2e"
/>

<BarChart
    data={datacenter_totals}
    x=datacenter_region
    y=total_emissions_mtco2e
    series=cloud_provider
    yAxisTitle="Total Emissions (mtCO2e)"
    title="Cloud Emissions by Datacenter Region"
    swapXY=true
/>

## Datacenter Emissions by Service

<DataTable data={datacenter_emissions}>
    <Column id=cloud_provider title="Provider"/>
    <Column id=datacenter_region title="Region"/>
    <Column id=service_name title="Service"/>
    <Column id=total_emissions_mtco2e title="Total (mtCO2e)" fmt="#,##0.00"/>
    <Column id=avg_monthly_emissions title="Avg Monthly" fmt="#,##0.00"/>
    <Column id=months_of_data title="Months"/>
</DataTable>

## Datacenter-Grid Region Mapping

Shows which cloud datacenters are located in which electricity grid regions and their carbon intensity.

<DataTable data={datacenter_with_grid}>
    <Column id=cloud_provider title="Cloud"/>
    <Column id=datacenter_region title="Datacenter Region"/>
    <Column id=grid_region_name title="Grid Region"/>
    <Column id=country title="Country"/>
    <Column id=grid_avg_intensity title="Grid Intensity" fmt="#,##0"/>
    <Column id=cleanliness_category title="Grid Cleanliness"/>
    <Column id=total_emissions_mtco2e title="Emissions (mtCO2e)" fmt="#,##0.00"/>
</DataTable>

## Geographic Distribution

```sql datacenter_map
SELECT
    cloud_provider,
    datacenter_region,
    grid_region_name,
    grid_avg_intensity,
    total_emissions_mtco2e,
    latitude as lat,
    longitude as long
FROM (
    SELECT * FROM datacenter_with_grid
)
WHERE total_emissions_mtco2e > 0
```

<BubbleMap
    data={datacenter_map}
    lat=lat
    long=long
    size=total_emissions_mtco2e
    value=total_emissions_mtco2e
    valueFmt="#,##0 mtCO2e"
    pointName=datacenter_region
    title="Cloud Datacenter Emissions by Location"
    height=500
/>

## Cleanest Datacenters

Datacenters in the cleanest grid regions (lowest carbon intensity):

```sql cleanest_datacenters
SELECT
    cloud_provider,
    datacenter_region,
    grid_region_name,
    country,
    grid_avg_intensity,
    cleanliness_category,
    total_emissions_mtco2e
FROM datacenter_with_grid
WHERE total_emissions_mtco2e > 0
ORDER BY grid_avg_intensity ASC
LIMIT 10
```

<BarChart
    data={cleanest_datacenters}
    x=datacenter_region
    y=grid_avg_intensity
    series=cloud_provider
    yAxisTitle="Grid Carbon Intensity (gCO2eq/kWh)"
    title="Cleanest Cloud Regions by Grid Intensity"
    swapXY=true
/>

## Analysis

- **Grid Region Mapping**: Shows which electricity grid region each cloud datacenter draws power from
- **Grid Intensity**: Lower values indicate cleaner electricity (more renewable energy)
- **Emissions**: Total carbon footprint from compute, storage, and networking in each region
- **Cleanest Regions**: Typically in areas with high hydro/nuclear/wind generation

---

**Data Sources**: Cloud provider carbon reports (GCP, AWS, Azure) + Grid region metadata
