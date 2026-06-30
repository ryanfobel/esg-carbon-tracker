# ESG Carbon Footprint Dashboard

Multi-cloud carbon emissions and grid intensity tracking.

```sql cloud_totals
SELECT
    cloud_provider,
    SUM(total_mtco2e) as total_mtco2e,
    SUM(scope1_kgco2e) / 1000 as scope1_mtco2e,
    SUM(scope2_market_based_kgco2e) / 1000 as scope2_mtco2e,
    SUM(scope3_kgco2e) / 1000 as scope3_mtco2e,
    COUNT(DISTINCT account_id) as num_accounts,
    COUNT(DISTINCT service_name) as num_services
FROM fact_cloud_carbon
GROUP BY cloud_provider
ORDER BY total_mtco2e DESC
```

```sql monthly_trend
SELECT
    usage_month_start,
    cloud_provider,
    SUM(total_mtco2e) as total_mtco2e
FROM fact_cloud_carbon
GROUP BY usage_month_start, cloud_provider
ORDER BY usage_month_start
```

```sql scope_breakdown
SELECT
    'Scope 1' as scope,
    SUM(scope1_kgco2e) / 1000 as mtco2e
FROM fact_cloud_carbon
UNION ALL
SELECT
    'Scope 2 (Market-Based)',
    SUM(scope2_market_based_kgco2e) / 1000
FROM fact_cloud_carbon
UNION ALL
SELECT
    'Scope 3',
    SUM(scope3_kgco2e) / 1000
FROM fact_cloud_carbon
```

## Overview

<BigValue
    data={cloud_totals}
    value=total_mtco2e
    title="Total Emissions"
    fmt="# metric tons CO2e"
/>

## Emissions by Cloud Provider

<BarChart
    data={cloud_totals}
    x=cloud_provider
    y=total_mtco2e
    yAxisTitle="Metric Tons CO2e"
    title="Total Emissions by Provider"
/>

## Emissions Trend

<LineChart
    data={monthly_trend}
    x=usage_month_start
    y=total_mtco2e
    series=cloud_provider
    yAxisTitle="Metric Tons CO2e"
    title="Monthly Emissions Trend"
/>

## Scope Breakdown

<BarChart
    data={scope_breakdown}
    x=scope
    y=mtco2e
    yAxisTitle="Metric Tons CO2e"
    title="Emissions by Scope"
/>

## Provider Details

<DataTable data={cloud_totals}>
    <Column id=cloud_provider title="Provider"/>
    <Column id=total_mtco2e title="Total (mtCO2e)" fmt="#,##0.00"/>
    <Column id=scope1_mtco2e title="Scope 1" fmt="#,##0.00"/>
    <Column id=scope2_mtco2e title="Scope 2" fmt="#,##0.00"/>
    <Column id=scope3_mtco2e title="Scope 3" fmt="#,##0.00"/>
    <Column id=num_accounts title="Accounts" fmt="#,##0"/>
    <Column id=num_services title="Services" fmt="#,##0"/>
</DataTable>

---

**Data Sources**: GCP, AWS, Azure, Cloud Carbon Footprint
**Last Updated**: {new Date().toISOString().split('T')[0]}
