{{
    config(
        materialized='table',
        tags=['grid', 'dimension']
    )
}}

-- Dimension table for grid regions
-- Provides metadata about grid regions/balancing authorities

with base_regions as (
    -- Extract unique regions from grid intensity data
    select distinct
        grid_region
    from {{ ref('fact_grid_intensity') }}
),

region_stats as (
    -- Calculate statistics for each region
    select
        grid_region,
        min(timestamp_day) as first_data_date,
        max(timestamp_day) as last_data_date,
        count(distinct timestamp_day) as days_of_data,
        avg(carbon_intensity_gco2eq_per_kwh) as avg_carbon_intensity,
        min(carbon_intensity_gco2eq_per_kwh) as min_carbon_intensity,
        max(carbon_intensity_gco2eq_per_kwh) as max_carbon_intensity,
        avg(renewable_percentage) as avg_renewable_percentage
    from {{ ref('fact_grid_intensity') }}
    group by 1
),

region_metadata as (
    -- Map grid regions to metadata
    -- This is a static mapping that can be expanded with GSF RTC data
    select
        grid_region,
        case
            -- US regions (ISO/RTO codes)
            when grid_region in ('CAISO', 'CISO', 'US-CAL-CISO') then 'California ISO'
            when grid_region in ('ERCOT', 'US-TEX-ERCO') then 'Texas (ERCOT)'
            when grid_region in ('PJM', 'US-MIDA-PJM') then 'PJM Interconnection'
            when grid_region in ('MISO', 'US-MIDW-MISO') then 'Midcontinent ISO'
            when grid_region in ('NYISO', 'US-NY-NYIS') then 'New York ISO'
            when grid_region in ('ISONE', 'US-NE-ISNE') then 'ISO New England'
            when grid_region in ('SPP', 'US-CENT-SPP') then 'Southwest Power Pool'

            -- Canadian regions
            when grid_region = 'IESO' then 'Ontario (IESO)'
            when grid_region = 'AESO' then 'Alberta'
            when grid_region = 'BC' then 'British Columbia'
            when grid_region = 'SaskPower' then 'Saskatchewan'

            -- European regions (Electricity Maps codes)
            when grid_region like 'DE%' then 'Germany'
            when grid_region like 'FR%' then 'France'
            when grid_region like 'GB%' then 'United Kingdom'
            when grid_region like 'ES%' then 'Spain'
            when grid_region like 'IT%' then 'Italy'
            when grid_region like 'NL%' then 'Netherlands'
            when grid_region like 'SE%' then 'Sweden'
            when grid_region like 'NO%' then 'Norway'
            when grid_region like 'DK%' then 'Denmark'

            else grid_region
        end as region_name,

        case
            when grid_region like 'US-%' or grid_region in ('CAISO', 'CISO', 'ERCOT', 'PJM', 'MISO', 'NYISO', 'ISONE', 'SPP') then 'United States'
            when grid_region in ('IESO', 'AESO', 'BC', 'SaskPower') then 'Canada'
            when grid_region like 'DE%' then 'Germany'
            when grid_region like 'FR%' then 'France'
            when grid_region like 'GB%' then 'United Kingdom'
            when grid_region like 'ES%' then 'Spain'
            when grid_region like 'IT%' then 'Italy'
            when grid_region like 'NL%' then 'Netherlands'
            when grid_region like 'SE%' then 'Sweden'
            when grid_region like 'NO%' then 'Norway'
            when grid_region like 'DK%' then 'Denmark'
            else 'Unknown'
        end as country,

        case
            when grid_region like 'US-%' or grid_region in ('CAISO', 'CISO', 'ERCOT', 'PJM', 'MISO', 'NYISO', 'ISONE', 'SPP') then 'North America'
            when grid_region in ('IESO', 'AESO', 'BC', 'SaskPower') then 'North America'
            when grid_region like any (array['DE%', 'FR%', 'GB%', 'ES%', 'IT%', 'NL%', 'SE%', 'NO%', 'DK%']) then 'Europe'
            else 'Other'
        end as continent,

        -- Timezone mapping (simplified)
        case
            when grid_region in ('CAISO', 'CISO', 'US-CAL-CISO') then 'America/Los_Angeles'
            when grid_region in ('ERCOT', 'US-TEX-ERCO') then 'America/Chicago'
            when grid_region in ('PJM', 'US-MIDA-PJM') then 'America/New_York'
            when grid_region in ('NYISO', 'US-NY-NYIS') then 'America/New_York'
            when grid_region in ('ISONE', 'US-NE-ISNE') then 'America/New_York'
            when grid_region = 'IESO' then 'America/Toronto'
            when grid_region like 'GB%' then 'Europe/London'
            when grid_region like 'DE%' then 'Europe/Berlin'
            when grid_region like 'FR%' then 'Europe/Paris'
            else null
        end as timezone,

        -- Region type
        case
            when grid_region like 'US-%' or grid_region in ('CAISO', 'CISO', 'ERCOT', 'PJM', 'MISO', 'NYISO', 'ISONE', 'SPP') then 'ISO/RTO'
            when grid_region in ('IESO', 'AESO') then 'ISO/RTO'
            when grid_region in ('BC', 'SaskPower') then 'Utility'
            else 'Grid Zone'
        end as region_type

    from base_regions
),

final as (
    select
        r.grid_region,
        m.region_name,
        m.country,
        m.continent,
        m.timezone,
        m.region_type,

        -- Statistics
        s.first_data_date,
        s.last_data_date,
        s.days_of_data,
        s.avg_carbon_intensity,
        s.min_carbon_intensity,
        s.max_carbon_intensity,
        s.avg_renewable_percentage,

        -- Categorize region by average carbon intensity
        case
            when s.avg_carbon_intensity < 150 then 'Very Clean'
            when s.avg_carbon_intensity < 300 then 'Clean'
            when s.avg_carbon_intensity < 450 then 'Medium'
            when s.avg_carbon_intensity < 600 then 'Dirty'
            else 'Very Dirty'
        end as cleanliness_category,

        -- Placeholders for future GSF RTC integration
        null::double as pue,  -- Power Usage Effectiveness
        null::double as wue,  -- Water Usage Effectiveness
        null::double as cfe_percent,  -- Carbon-free energy percentage
        null::varchar as grid_zone_id,  -- GSF RTC zone mapping

        current_timestamp as processed_at

    from base_regions r
    left join region_metadata m on r.grid_region = m.grid_region
    left join region_stats s on r.grid_region = s.grid_region
)

select * from final
