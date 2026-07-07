-- Join cloud emissions with grid region data and calculate average grid intensity
WITH cloud_regions AS (
    SELECT
        cloud_provider,
        region as datacenter_region,
        SUM(total_mtco2e) as total_emissions_mtco2e
    FROM fact_cloud_carbon
    WHERE region IS NOT NULL
    GROUP BY cloud_provider, region
),
grid_intensity_avg AS (
    SELECT
        grid_region,
        AVG(avg_intensity) as avg_carbon_intensity,
        CASE
            WHEN AVG(avg_intensity) < 100 THEN 'Very Low'
            WHEN AVG(avg_intensity) < 250 THEN 'Low'
            WHEN AVG(avg_intensity) < 400 THEN 'Medium'
            WHEN AVG(avg_intensity) < 600 THEN 'High'
            ELSE 'Very High'
        END as cleanliness_category
    FROM grid_intensity_daily
    GROUP BY grid_region
),
grid_mappings AS (
    SELECT
        r.grid_region,
        r.region_name,
        r.country,
        gi.avg_carbon_intensity,
        gi.cleanliness_category,
        CASE
            WHEN cloud_provider = 'GCP' THEN TRIM(UNNEST(string_split(r.gcp_regions, ',')))
            WHEN cloud_provider = 'AWS' THEN TRIM(UNNEST(string_split(r.aws_regions, ',')))
            WHEN cloud_provider = 'Azure' THEN TRIM(UNNEST(string_split(r.azure_regions, ',')))
        END as datacenter_region,
        cloud_provider,
        r.latitude,
        r.longitude
    FROM dim_grid_regions r
    LEFT JOIN grid_intensity_avg gi ON r.grid_region = gi.grid_region
    CROSS JOIN (VALUES ('GCP'), ('AWS'), ('Azure')) AS providers(cloud_provider)
    WHERE r.cloud_providers LIKE '%' || cloud_provider || '%'
)
SELECT
    gm.cloud_provider,
    gm.datacenter_region,
    gm.grid_region,
    gm.region_name as grid_region_name,
    gm.country,
    gm.avg_carbon_intensity as grid_avg_intensity,
    gm.cleanliness_category,
    COALESCE(cr.total_emissions_mtco2e, 0) as total_emissions_mtco2e,
    gm.latitude,
    gm.longitude
FROM grid_mappings gm
LEFT JOIN cloud_regions cr
    ON gm.cloud_provider = cr.cloud_provider
    AND gm.datacenter_region = cr.datacenter_region
WHERE gm.datacenter_region IS NOT NULL AND gm.datacenter_region != ''
ORDER BY total_emissions_mtco2e DESC
