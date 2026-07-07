{{
    config(
        materialized='table',
        tags=['grid', 'electricity', 'daily']
    )
}}

-- Daily aggregation of grid carbon intensity metrics
-- Rolls up hourly fact_grid_intensity to daily summaries

with daily_agg as (
    select
        grid_region,
        timestamp_day,
        date_trunc('week', timestamp_day) as timestamp_week,
        date_trunc('month', timestamp_day) as timestamp_month,
        extract(year from timestamp_day) as year,
        extract(month from timestamp_day) as month,
        extract(dow from timestamp_day) as day_of_week,

        -- Carbon intensity aggregates
        avg(carbon_intensity_gco2eq_per_kwh) as avg_carbon_intensity,
        min(carbon_intensity_gco2eq_per_kwh) as min_carbon_intensity,
        max(carbon_intensity_gco2eq_per_kwh) as max_carbon_intensity,
        stddev(carbon_intensity_gco2eq_per_kwh) as stddev_carbon_intensity,

        -- Fuel mix (from Electricity Maps data)
        avg(fossil_fuel_percentage) as avg_fossil_fuel_percentage,
        avg(renewable_percentage) as avg_renewable_percentage,

        -- Time-based aggregates
        count(*) as hours_reported,
        count(distinct timestamp_hour) as distinct_hours,

        -- Clean hours metrics
        sum(case when carbon_intensity_gco2eq_per_kwh < 250 then 1 else 0 end) as low_carbon_hours,
        sum(case when carbon_intensity_gco2eq_per_kwh >= 600 then 1 else 0 end) as high_carbon_hours,

        -- Peak/off-peak analysis (assuming peak = 7am-11pm)
        avg(case
            when extract(hour from timestamp_hour) between 7 and 22
            then carbon_intensity_gco2eq_per_kwh
        end) as avg_peak_intensity,
        avg(case
            when extract(hour from timestamp_hour) not between 7 and 22
            then carbon_intensity_gco2eq_per_kwh
        end) as avg_offpeak_intensity,

        -- Data quality
        count(distinct data_source) as num_data_sources,
        max(extracted_at) as last_extracted_at,
        current_timestamp as processed_at

    from {{ ref('fact_grid_intensity') }}
    group by 1, 2, 3, 4, 5, 6, 7
),

final as (
    select
        grid_region,
        timestamp_day,
        timestamp_week,
        timestamp_month,
        year,
        month,
        day_of_week,

        -- Carbon intensity metrics
        avg_carbon_intensity,
        min_carbon_intensity,
        max_carbon_intensity,
        stddev_carbon_intensity,
        max_carbon_intensity - min_carbon_intensity as daily_range,

        -- Categorize average daily intensity
        case
            when avg_carbon_intensity < 100 then 'Very Low'
            when avg_carbon_intensity < 250 then 'Low'
            when avg_carbon_intensity < 400 then 'Medium'
            when avg_carbon_intensity < 600 then 'High'
            else 'Very High'
        end as avg_intensity_category,

        -- Fuel mix
        avg_fossil_fuel_percentage,
        avg_renewable_percentage,

        -- Time metrics
        hours_reported,
        distinct_hours,
        low_carbon_hours,
        high_carbon_hours,
        case when distinct_hours >= 20 then true else false end as is_complete_day,

        -- Peak vs off-peak
        avg_peak_intensity,
        avg_offpeak_intensity,
        avg_peak_intensity - avg_offpeak_intensity as peak_offpeak_delta,

        -- Data quality
        num_data_sources,
        last_extracted_at,
        processed_at

    from daily_agg
)

select * from final
