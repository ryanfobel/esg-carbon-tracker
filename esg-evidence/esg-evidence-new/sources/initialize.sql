-- Create views in main schema pointing to marts tables
CREATE OR REPLACE VIEW fact_cloud_carbon AS SELECT * FROM marts.fact_cloud_carbon;
CREATE OR REPLACE VIEW fact_grid_intensity AS SELECT * FROM marts.fact_grid_intensity;
CREATE OR REPLACE VIEW carbon_trends_monthly AS SELECT * FROM marts.carbon_trends_monthly;
