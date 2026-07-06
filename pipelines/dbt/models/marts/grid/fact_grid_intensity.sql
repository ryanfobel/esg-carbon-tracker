{{
    config(
        materialized='table',
        tags=['grid', 'electricity']
    )
}}

-- Unified grid carbon intensity metrics
-- Combines Electricity Maps and WattTime for comprehensive grid analysis

with electricity_maps as (
    select
        zone as grid_region,
        timestamp_hour,
        timestamp_day,

        -- Carbon intensity
        carbon_intensity_kgco2eq_per_kwh,
        carbon_intensity_gco2eq_per_kwh,

        -- Fuel mix
        fossil_fuel_percentage,
        renewable_percentage,
        low_carbon_percentage,
        high_carbon_percentage,

        -- Power breakdown
        power_production_breakdown,

        -- Source
        'Electricity Maps' as data_source,
        extracted_at

    from {{ ref('stg_electricity_maps') }}
),

watttime as (
    select
        ba as grid_region,
        point_time_hour as timestamp_hour,
        point_time_day as timestamp_day,

        -- Carbon intensity (already converted to kg/kWh)
        moer_kgco2_per_kwh as carbon_intensity_kgco2eq_per_kwh,
        moer_kgco2_per_kwh * 1000 as carbon_intensity_gco2eq_per_kwh,

        -- Percentile rank
        percent,

        -- Source
        'WattTime' as data_source,
        extracted_at

    from {{ ref('stg_watttime') }}
),

-- Hourly aggregates from Electricity Maps
em_hourly as (
    select
        grid_region,
        timestamp_hour,
        timestamp_day,
        avg(carbon_intensity_kgco2eq_per_kwh) as avg_carbon_intensity_kgco2eq_per_kwh,
        avg(carbon_intensity_gco2eq_per_kwh) as avg_carbon_intensity_gco2eq_per_kwh,
        avg(fossil_fuel_percentage) as avg_fossil_fuel_percentage,
        avg(renewable_percentage) as avg_renewable_percentage,
        data_source,
        max(extracted_at) as extracted_at
    from electricity_maps
    group by 1, 2, 3, 7
),

-- Hourly aggregates from WattTime (5-min intervals -> hourly)
wt_hourly as (
    select
        grid_region,
        timestamp_hour,
        timestamp_day,
        avg(carbon_intensity_kgco2eq_per_kwh) as avg_carbon_intensity_kgco2eq_per_kwh,
        avg(carbon_intensity_gco2eq_per_kwh) as avg_carbon_intensity_gco2eq_per_kwh,
        avg(percent) as avg_percentile,
        data_source,
        max(extracted_at) as extracted_at
    from watttime
    group by 1, 2, 3, 7
),

-- Combine both sources
combined as (
    select
        grid_region,
        timestamp_hour,
        timestamp_day,
        avg_carbon_intensity_kgco2eq_per_kwh as carbon_intensity_kgco2eq_per_kwh,
        avg_carbon_intensity_gco2eq_per_kwh as carbon_intensity_gco2eq_per_kwh,
        avg_fossil_fuel_percentage as fossil_fuel_percentage,
        avg_renewable_percentage as renewable_percentage,
        null as percentile_rank,
        data_source,
        extracted_at
    from em_hourly

    union all

    select
        grid_region,
        timestamp_hour,
        timestamp_day,
        avg_carbon_intensity_kgco2eq_per_kwh,
        avg_carbon_intensity_gco2eq_per_kwh,
        null as fossil_fuel_percentage,
        null as renewable_percentage,
        avg_percentile as percentile_rank,
        data_source,
        extracted_at
    from wt_hourly
),

final as (
    select
        grid_region,
        timestamp_hour,
        timestamp_day,
        date_trunc('week', timestamp_day) as timestamp_week,
        date_trunc('month', timestamp_day) as timestamp_month,

        -- Carbon intensity
        carbon_intensity_kgco2eq_per_kwh,
        carbon_intensity_gco2eq_per_kwh,

        -- Fuel mix (from Electricity Maps)
        fossil_fuel_percentage,
        renewable_percentage,

        -- Percentile (from WattTime)
        percentile_rank,

        -- Categorize intensity
        case
            when carbon_intensity_gco2eq_per_kwh < 100 then 'Very Low'
            when carbon_intensity_gco2eq_per_kwh < 250 then 'Low'
            when carbon_intensity_gco2eq_per_kwh < 400 then 'Medium'
            when carbon_intensity_gco2eq_per_kwh < 600 then 'High'
            else 'Very High'
        end as intensity_category,

        -- Source
        data_source,
        extracted_at,
        current_timestamp as processed_at

    from combined
)

select * from final
