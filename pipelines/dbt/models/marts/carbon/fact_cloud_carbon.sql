{{
    config(
        materialized='table',
        tags=['carbon', 'cloud']
    )
}}

-- Unified cloud carbon emissions across all providers
-- Combines GCP, AWS, Azure, and CCF data into a single fact table

with gcp as (
    select
        id,
        cloud_provider,
        project_id as account_id,
        service_name,
        region,
        usage_month_start,
        scope1_kgco2e,
        scope2_location_based_kgco2e,
        scope2_market_based_kgco2e,
        scope3_kgco2e,
        total_market_based_kgco2e,
        null::double as kilowatt_hours,
        null::double as cost_usd,
        extracted_at,
        processed_at
    from {{ ref('stg_gcp_carbon') }}
),

aws as (
    select
        id,
        cloud_provider,
        account_id,
        service_name,
        region,
        usage_month_start,
        scope1_kgco2e,
        scope2_location_based_kgco2e,
        scope2_market_based_kgco2e,
        scope3_kgco2e,
        total_market_based_kgco2e,
        null::double as kilowatt_hours,
        null::double as cost_usd,
        extracted_at,
        processed_at
    from {{ ref('stg_aws_carbon') }}
),

azure as (
    select
        id,
        cloud_provider,
        account_id,
        service_name,
        region,
        usage_month_start,
        scope1_kgco2e,
        scope2_location_based_kgco2e,
        scope2_market_based_kgco2e,
        scope3_kgco2e,
        total_market_based_kgco2e,
        null::double as kilowatt_hours,
        null::double as cost_usd,
        extracted_at,
        processed_at
    from {{ ref('stg_azure_carbon') }}
),

ccf as (
    select
        id,
        cloud_provider,
        account_id,
        service_name,
        region,
        usage_month_start,
        scope1_kgco2e,
        scope2_kgco2e as scope2_location_based_kgco2e,
        scope2_kgco2e as scope2_market_based_kgco2e,
        scope3_kgco2e,
        total_market_based_kgco2e,
        total_kilowatt_hours as kilowatt_hours,
        total_cost_usd as cost_usd,
        extracted_at,
        processed_at
    from {{ ref('stg_ccf_carbon') }}
),

unioned as (
    select * from gcp
    union all
    select * from aws
    union all
    select * from azure
    union all
    select * from ccf
),

final as (
    select
        id,
        cloud_provider,
        account_id,
        service_name,
        region,
        usage_month_start,

        -- Scope emissions
        scope1_kgco2e,
        scope2_location_based_kgco2e,
        scope2_market_based_kgco2e,
        scope3_kgco2e,

        -- Totals
        total_market_based_kgco2e as total_kgco2e,
        scope1_kgco2e + scope2_location_based_kgco2e + scope3_kgco2e as total_location_based_kgco2e,

        -- Convert to metric tons for reporting
        total_market_based_kgco2e / 1000 as total_mtco2e,

        -- Additional metrics
        kilowatt_hours,
        cost_usd,

        -- Intensity metrics (if cost available)
        case
            when cost_usd > 0 then total_market_based_kgco2e / cost_usd
            else null
        end as kgco2e_per_dollar,

        case
            when kilowatt_hours > 0 then total_market_based_kgco2e / kilowatt_hours
            else null
        end as kgco2e_per_kwh,

        -- Metadata
        extracted_at,
        processed_at

    from unioned
)

select * from final
