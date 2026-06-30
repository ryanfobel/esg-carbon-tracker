{{
    config(
        materialized='view'
    )
}}

-- Staging model for Cloud Carbon Footprint data
-- Aggregates daily CCF data to monthly for consistency with cloud provider APIs

with source as (
    select * from {{ source('raw', 'ccf_carbon_footprint') }}
),

daily as (
    select
        -- Identifiers
        id,
        cloud_provider,
        account_id,
        service_name,
        region,

        -- Time
        usage_date,
        date_trunc('month', usage_date) as usage_month,

        -- Emissions (already in kg CO2e)
        scope1_kgco2e,
        scope2_kgco2e,
        scope3_kgco2e,
        total_kgco2e,

        -- Additional metrics
        kilowatt_hours,
        cost_usd,

        -- Metadata
        extracted_at

    from source
    where total_kgco2e > 0
),

-- Aggregate to monthly for consistency
monthly as (
    select
        cloud_provider || '_' || account_id || '_' || service_name || '_' || region || '_' || to_char(usage_month, 'YYYY-MM') as id,
        cloud_provider,
        account_id,
        service_name,
        region,
        usage_month as usage_month_start,

        sum(scope1_kgco2e) as scope1_kgco2e,
        sum(scope2_kgco2e) as scope2_kgco2e,
        sum(scope3_kgco2e) as scope3_kgco2e,
        sum(total_kgco2e) as total_kgco2e,
        sum(scope1_kgco2e + scope2_kgco2e + scope3_kgco2e) as total_market_based_kgco2e,

        sum(kilowatt_hours) as total_kilowatt_hours,
        sum(cost_usd) as total_cost_usd,

        max(extracted_at) as extracted_at,
        current_timestamp as processed_at

    from daily
    group by 1, 2, 3, 4, 5, 6
)

select * from monthly
