{{
    config(
        materialized='view'
    )
}}

-- Staging model for WattTime MOER data
-- Cleans and standardizes marginal operating emissions rate data

with source as (
    select * from {{ source('raw', 'watttime_moer') }}
),

cleaned as (
    select
        -- Identifiers
        id,
        ba,
        ba_name,

        -- Time
        point_time,
        date_trunc('hour', point_time) as point_time_hour,
        date_trunc('day', point_time) as point_time_day,

        -- MOER (lbs CO2/MWh)
        moer,
        moer_kgco2_per_kwh,

        -- Percentile rank (0-100)
        percent,

        -- Update frequency (seconds)
        frequency,

        -- Market type
        market,

        -- Metadata
        'WattTime' as data_source,
        extracted_at,
        current_timestamp as processed_at

    from source
    where moer > 0
)

select * from cleaned
