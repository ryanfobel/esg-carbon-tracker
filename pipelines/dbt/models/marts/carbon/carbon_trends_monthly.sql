{{
    config(
        materialized='table',
        tags=['carbon', 'analytics', 'trends']
    )
}}

-- Monthly carbon emissions trends and aggregations
-- Provides time-series analytics for carbon footprint reporting

with monthly_cloud as (
    select
        usage_month_start as month,
        cloud_provider,
        account_id,

        -- Total emissions
        sum(total_kgco2e) as total_kgco2e,
        sum(total_mtco2e) as total_mtco2e,

        -- By scope
        sum(scope1_kgco2e) as scope1_kgco2e,
        sum(scope2_market_based_kgco2e) as scope2_kgco2e,
        sum(scope3_kgco2e) as scope3_kgco2e,

        -- Cost and energy
        sum(cost_usd) as total_cost_usd,
        sum(kilowatt_hours) as total_kwh,

        -- Service breakdown
        count(distinct service_name) as num_services,
        count(distinct region) as num_regions

    from {{ ref('fact_cloud_carbon') }}
    group by 1, 2, 3
),

with_trends as (
    select
        month,
        cloud_provider,
        account_id,

        -- Current month
        total_kgco2e,
        total_mtco2e,
        scope1_kgco2e,
        scope2_kgco2e,
        scope3_kgco2e,
        total_cost_usd,
        total_kwh,
        num_services,
        num_regions,

        -- Previous month
        lag(total_kgco2e, 1) over (partition by cloud_provider, account_id order by month) as prev_month_kgco2e,

        -- Month-over-month change
        total_kgco2e - lag(total_kgco2e, 1) over (partition by cloud_provider, account_id order by month) as mom_change_kgco2e,

        -- Month-over-month percent change
        case
            when lag(total_kgco2e, 1) over (partition by cloud_provider, account_id order by month) > 0
            then ((total_kgco2e - lag(total_kgco2e, 1) over (partition by cloud_provider, account_id order by month)) /
                  lag(total_kgco2e, 1) over (partition by cloud_provider, account_id order by month)) * 100
            else null
        end as mom_change_percent,

        -- 3-month rolling average
        avg(total_kgco2e) over (
            partition by cloud_provider, account_id
            order by month
            rows between 2 preceding and current row
        ) as rolling_3mo_avg_kgco2e,

        -- Year-to-date
        sum(total_kgco2e) over (
            partition by cloud_provider, account_id, date_trunc('year', month)
            order by month
        ) as ytd_total_kgco2e

    from monthly_cloud
),

final as (
    select
        month,
        cloud_provider,
        account_id,

        -- Current metrics
        total_kgco2e,
        total_mtco2e,
        scope1_kgco2e,
        scope2_kgco2e,
        scope3_kgco2e,

        -- Scope percentages
        case when total_kgco2e > 0 then (scope1_kgco2e / total_kgco2e) * 100 else 0 end as scope1_percent,
        case when total_kgco2e > 0 then (scope2_kgco2e / total_kgco2e) * 100 else 0 end as scope2_percent,
        case when total_kgco2e > 0 then (scope3_kgco2e / total_kgco2e) * 100 else 0 end as scope3_percent,

        -- Cost and energy
        total_cost_usd,
        total_kwh,

        -- Intensity metrics
        case when total_cost_usd > 0 then total_kgco2e / total_cost_usd else null end as kgco2e_per_dollar,
        case when total_kwh > 0 then total_kgco2e / total_kwh else null end as kgco2e_per_kwh,

        -- Coverage
        num_services,
        num_regions,

        -- Trends
        prev_month_kgco2e,
        mom_change_kgco2e,
        mom_change_percent,
        rolling_3mo_avg_kgco2e,
        ytd_total_kgco2e,

        -- Trend indicator
        case
            when mom_change_percent > 10 then 'Increasing ⬆'
            when mom_change_percent < -10 then 'Decreasing ⬇'
            when mom_change_percent is null then 'New Account'
            else 'Stable ⏸'
        end as trend_indicator,

        current_timestamp as processed_at

    from with_trends
)

select * from final
order by month desc, cloud_provider, account_id
