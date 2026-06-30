# Carbon Trends

Monthly trends with month-over-month changes and rolling averages.

```sql trends
SELECT
    month,
    cloud_provider,
    account_id,
    total_mtco2e,
    mom_change_percent,
    rolling_3mo_avg_mtco2e,
    ytd_total_mtco2e,
    trend_indicator,
    scope1_percent,
    scope2_percent,
    scope3_percent
FROM marts.carbon_trends_monthly
ORDER BY month DESC, cloud_provider
LIMIT 100
```

```sql mom_change
SELECT
    month,
    cloud_provider,
    mom_change_percent
FROM marts.carbon_trends_monthly
WHERE mom_change_percent IS NOT NULL
ORDER BY month
```

```sql ytd
SELECT
    month,
    cloud_provider,
    ytd_total_mtco2e
FROM marts.carbon_trends_monthly
ORDER BY month
```

## Month-over-Month Change

<LineChart
    data={mom_change}
    x=month
    y=mom_change_percent
    series=cloud_provider
    yAxisTitle="% Change"
    title="Month-over-Month Emissions Change"
/>

## Year-to-Date Cumulative

<AreaChart
    data={ytd}
    x=month
    y=ytd_total_mtco2e
    series=cloud_provider
    yAxisTitle="Metric Tons CO2e"
    title="Year-to-Date Cumulative Emissions"
/>

## Recent Trends

<DataTable data={trends}>
    <Column id=month title="Month" fmt="yyyy-MM"/>
    <Column id=cloud_provider title="Provider"/>
    <Column id=account_id title="Account"/>
    <Column id=total_mtco2e title="Total (mtCO2e)" fmt="#,##0.00"/>
    <Column id=mom_change_percent title="MoM Change" fmt="+#0.0%;-#0.0%"/>
    <Column id=trend_indicator title="Trend"/>
    <Column id=rolling_3mo_avg_mtco2e title="3Mo Avg" fmt="#,##0.00"/>
    <Column id=ytd_total_mtco2e title="YTD Total" fmt="#,##0.00"/>
</DataTable>

---

**Analysis**: 3-month rolling averages smooth out monthly variability.

**Trend Indicators**: ⬆ Increasing (greater than 10%), ⬇ Decreasing (less than -10%), ⏸ Stable
