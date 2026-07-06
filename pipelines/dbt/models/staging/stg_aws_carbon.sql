{{
    config(
        materialized='view'
    )
}}

-- Staging model for AWS Carbon Footprint data
-- Cleans and standardizes AWS Sustainability API data

with source as (
    select * from {{ source('raw', 'aws_carbon_footprint') }}
),

cleaned as (
    select
        -- Identifiers
        id,
        account_id,
        service_name,
        region,

        -- Time
        usage_month,
        date_trunc('month', usage_month) as usage_month_start,

        -- Emissions (already in kg CO2e)
        scope1_kgco2e,
        scope2_location_based_kgco2e,
        scope2_market_based_kgco2e,
        scope3_kgco2e,
        total_kgco2e,

        -- Use market-based Scope 2 as primary
        scope1_kgco2e + scope2_market_based_kgco2e + scope3_kgco2e as total_market_based_kgco2e,

        -- Metadata
        'AWS' as cloud_provider,
        extracted_at,
        current_timestamp as processed_at

    from source
    where total_kgco2e > 0
)

select * from cleaned
