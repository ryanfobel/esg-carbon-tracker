{{
    config(
        materialized='view'
    )
}}

-- Staging model for Electricity Maps grid carbon intensity data
-- Cleans and standardizes hourly grid data

with source as (
    select * from {{ source('raw', 'electricity_maps_carbon_intensity') }}
),

cleaned as (
    select
        -- Identifiers
        id,
        zone,

        -- Time
        timestamp,
        date_trunc('hour', timestamp) as timestamp_hour,
        date_trunc('day', timestamp) as timestamp_day,

        -- Carbon intensity (gCO2eq/kWh)
        carbon_intensity_gco2eq_per_kwh,
        carbon_intensity_gco2eq_per_kwh / 1000 as carbon_intensity_kgco2eq_per_kwh,

        -- Fuel mix percentages
        fossil_fuel_percentage,
        renewable_percentage,
        low_carbon_percentage,
        100 - low_carbon_percentage as high_carbon_percentage,

        -- Power breakdown (stored as JSON)
        power_production_breakdown,
        power_consumption_breakdown,

        -- Metadata
        'Electricity Maps' as data_source,
        extracted_at,
        current_timestamp as processed_at

    from source
    where carbon_intensity_gco2eq_per_kwh > 0
)

select * from cleaned
