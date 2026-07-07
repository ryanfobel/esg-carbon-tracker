# Grid Carbon Intensity

Real-time and historical grid carbon intensity across regions.

```sql current_intensity
SELECT
    grid_region,
    timestamp_hour,
    carbon_intensity_gco2eq_per_kwh,
    intensity_category,
    fossil_fuel_percentage,
    renewable_percentage,
    data_source
FROM esg_data.fact_grid_intensity
WHERE timestamp_hour >= (SELECT MAX(timestamp_hour) - INTERVAL 1 DAY FROM esg_data.fact_grid_intensity)
ORDER BY carbon_intensity_gco2eq_per_kwh DESC
```

```sql intensity_trend
SELECT
    timestamp_hour,
    grid_region,
    carbon_intensity_gco2eq_per_kwh
FROM esg_data.fact_grid_intensity
WHERE timestamp_hour >= (SELECT MAX(timestamp_hour) - INTERVAL 7 DAY FROM esg_data.fact_grid_intensity)
ORDER BY timestamp_hour
```

```sql by_category
SELECT
    intensity_category,
    COUNT(*) as count,
    AVG(carbon_intensity_gco2eq_per_kwh) as avg_intensity
FROM esg_data.fact_grid_intensity
WHERE timestamp_hour >= (SELECT MAX(timestamp_hour) - INTERVAL 7 DAY FROM esg_data.fact_grid_intensity)
GROUP BY intensity_category
ORDER BY avg_intensity DESC
```

## Current Grid Intensity

<BigValue
    data={current_intensity}
    value=carbon_intensity_gco2eq_per_kwh
    title="Current Intensity"
    fmt="# gCO2eq/kWh"
/>

## Intensity by Region

<BarChart
    data={current_intensity}
    x=grid_region
    y=carbon_intensity_gco2eq_per_kwh
    yAxisTitle="gCO2eq/kWh"
    title="Current Carbon Intensity by Region"
    swapXY=true
/>

## 7-Day Trend

<LineChart
    data={intensity_trend}
    x=timestamp_hour
    y=carbon_intensity_gco2eq_per_kwh
    series=grid_region
    yAxisTitle="gCO2eq/kWh"
    title="Carbon Intensity Over Time"
/>

## Fuel Mix

<BarChart
    data={current_intensity}
    x=grid_region
    y={["fossil_fuel_percentage", "renewable_percentage"]}
    yAxisTitle="%"
    title="Current Fuel Mix by Region"
    type=stacked
    swapXY=true
/>

## Geographic Distribution

```sql map_data
SELECT
    f.grid_region,
    r.region_name,
    r.city,
    r.country,
    r.cloud_providers,
    AVG(f.carbon_intensity_gco2eq_per_kwh) as avg_intensity,
    AVG(f.fossil_fuel_percentage) as avg_fossil,
    AVG(f.renewable_percentage) as avg_renewable,
    r.latitude as lat,
    r.longitude as long
FROM esg_data.fact_grid_intensity f
JOIN main.dim_grid_regions r ON f.grid_region = r.grid_region
WHERE f.timestamp_hour >= (SELECT MAX(timestamp_hour) - INTERVAL 1 DAY FROM esg_data.fact_grid_intensity)
GROUP BY f.grid_region, r.region_name, r.city, r.country, r.cloud_providers, r.latitude, r.longitude
```

<BubbleMap
    data={map_data}
    lat=lat
    long=long
    size=avg_intensity
    value=avg_intensity
    valueFmt="#,##0"
    pointName=grid_region
    title="Carbon Intensity by Region"
    height=400
/>

## Regional Comparisons

### Daily Average by Region (Last 7 Days)

```sql daily_averages
SELECT
    d.date,
    d.grid_region,
    r.region_name,
    r.country,
    d.avg_intensity,
    d.avg_fossil_percentage,
    d.avg_renewable_percentage
FROM main.grid_intensity_daily d
JOIN main.dim_grid_regions r ON d.grid_region = r.grid_region
WHERE d.date >= CURRENT_DATE - INTERVAL 7 DAYS
ORDER BY d.date DESC, d.avg_intensity DESC
```

<LineChart
    data={daily_averages}
    x=date
    y=avg_intensity
    series=region_name
    yAxisTitle="gCO2eq/kWh"
    title="Daily Average Carbon Intensity by Region"
/>

### Weekly Comparison

```sql weekly_comparison
SELECT
    d.grid_region,
    r.region_name,
    r.country,
    AVG(d.avg_intensity) as avg_intensity,
    AVG(d.avg_fossil_percentage) as avg_fossil,
    AVG(d.avg_renewable_percentage) as avg_renewable,
    MIN(d.avg_intensity) as min_intensity,
    MAX(d.avg_intensity) as max_intensity
FROM main.grid_intensity_daily d
JOIN main.dim_grid_regions r ON d.grid_region = r.grid_region
WHERE d.date >= CURRENT_DATE - INTERVAL 7 DAYS
GROUP BY d.grid_region, r.region_name, r.country
ORDER BY avg_intensity ASC
LIMIT 20
```

<BarChart
    data={weekly_comparison}
    x=region_name
    y=avg_intensity
    yAxisTitle="Average gCO2eq/kWh (7-day)"
    title="Lowest Carbon Intensity Regions (7-Day Average)"
    swapXY=true
/>

### Monthly Trends by Region

```sql monthly_regional_trends
SELECT
    m.month_start,
    m.grid_region,
    r.region_name,
    r.country,
    m.avg_intensity,
    m.avg_fossil_percentage,
    m.avg_renewable_percentage
FROM main.grid_intensity_monthly m
JOIN main.dim_grid_regions r ON m.grid_region = r.grid_region
ORDER BY m.month_start DESC, m.avg_intensity
```

<DataTable data={monthly_regional_trends}>
    <Column id=month_start title="Month" fmt="yyyy-MM"/>
    <Column id=region_name title="Region"/>
    <Column id=country title="Country"/>
    <Column id=avg_intensity title="Avg Intensity" fmt="#,##0"/>
    <Column id=min_intensity title="Min" fmt="#,##0"/>
    <Column id=max_intensity title="Max" fmt="#,##0"/>
    <Column id=avg_fossil_percentage title="Fossil %" fmt="#0.0"/>
    <Column id=avg_renewable_percentage title="Renewable %" fmt="#0.0"/>
</DataTable>

## Current Readings

<DataTable data={current_intensity}>
    <Column id=grid_region title="Region"/>
    <Column id=carbon_intensity_gco2eq_per_kwh title="Intensity (gCO2eq/kWh)" fmt="#,##0"/>
    <Column id=intensity_category title="Category"/>
    <Column id=fossil_fuel_percentage title="Fossil Fuel %" fmt="#0.0"/>
    <Column id=renewable_percentage title="Renewable %" fmt="#0.0"/>
    <Column id=data_source title="Source"/>
    <Column id=timestamp_hour title="Timestamp" fmt="yyyy-MM-dd HH:mm"/>
</DataTable>

---

**Data Sources**: [Electricity Maps](https://www.electricitymaps.com/), [WattTime](https://www.watttime.org/)
**Update Frequency**: Hourly
