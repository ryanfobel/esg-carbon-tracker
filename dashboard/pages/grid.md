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
