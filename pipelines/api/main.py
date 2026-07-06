"""
ESG Data API

FastAPI service providing REST endpoints and data export capabilities for ESG warehouse.

Features:
- REST API for querying carbon footprint data
- Parquet file exports (static and on-demand)
- Direct DuckDB query interface
- Incremental updates and snapshot versioning

Run:
    uvicorn api.main:app --reload --port 8000

Docs:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
import duckdb
import json
import io

app = FastAPI(
    title="ESG Data API",
    description="REST API for multi-cloud carbon footprint and grid intensity data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configuration
WAREHOUSE_PATH = Path("~/.paimon/esg_data/warehouse.duckdb").expanduser()


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    GCP = "GCP"
    AWS = "AWS"
    AZURE = "Azure"
    ALL = "all"


class DataSource(str, Enum):
    """Supported grid data sources"""
    ELECTRICITY_MAPS = "Electricity Maps"
    WATTTIME = "WattTime"
    ALL = "all"


def get_db_connection():
    """Get DuckDB connection to warehouse"""
    if not WAREHOUSE_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Warehouse not found at {WAREHOUSE_PATH}. Run pipelines first."
        )
    return duckdb.connect(str(WAREHOUSE_PATH), read_only=True)


# Health check
@app.get("/")
def root():
    """API health check and info"""
    return {
        "service": "ESG Data API",
        "version": "1.0.0",
        "status": "healthy",
        "warehouse": str(WAREHOUSE_PATH),
        "warehouse_exists": WAREHOUSE_PATH.exists(),
        "endpoints": {
            "docs": "/docs",
            "cloud_carbon": "/api/v1/carbon/cloud",
            "grid_intensity": "/api/v1/carbon/grid",
            "trends": "/api/v1/carbon/trends",
            "exports": "/api/v1/exports"
        }
    }


# Cloud Carbon Endpoints
@app.get("/api/v1/carbon/cloud", tags=["Cloud Carbon"])
def get_cloud_carbon(
    provider: CloudProvider = Query(CloudProvider.ALL, description="Cloud provider filter"),
    start_month: Optional[date] = Query(None, description="Start month (YYYY-MM-DD)"),
    end_month: Optional[date] = Query(None, description="End month (YYYY-MM-DD)"),
    account_id: Optional[str] = Query(None, description="Account/Project ID filter"),
    service_name: Optional[str] = Query(None, description="Service name filter"),
    region: Optional[str] = Query(None, description="Region filter"),
    limit: int = Query(1000, ge=1, le=10000, description="Max records to return")
):
    """
    Query cloud carbon footprint data.

    Returns unified emissions across GCP, AWS, Azure with Scopes 1, 2, 3.
    Data from dbt mart: marts.fact_cloud_carbon
    """
    conn = get_db_connection()

    # Build query
    where_clauses = []
    params = {}

    if provider != CloudProvider.ALL:
        where_clauses.append("cloud_provider = $provider")
        params["provider"] = provider.value

    if start_month:
        where_clauses.append("usage_month_start >= $start_month")
        params["start_month"] = start_month

    if end_month:
        where_clauses.append("usage_month_start <= $end_month")
        params["end_month"] = end_month

    if account_id:
        where_clauses.append("account_id = $account_id")
        params["account_id"] = account_id

    if service_name:
        where_clauses.append("service_name ILIKE $service_name")
        params["service_name"] = f"%{service_name}%"

    if region:
        where_clauses.append("region = $region")
        params["region"] = region

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT
            id,
            cloud_provider,
            account_id,
            service_name,
            region,
            usage_month_start,
            scope1_kgco2e,
            scope2_market_based_kgco2e,
            scope3_kgco2e,
            total_kgco2e,
            total_mtco2e,
            kgco2e_per_dollar,
            kgco2e_per_kwh,
            extracted_at
        FROM marts.fact_cloud_carbon
        {where_sql}
        ORDER BY usage_month_start DESC, total_kgco2e DESC
        LIMIT {limit}
    """

    result = conn.execute(query, params).fetchdf()

    return {
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


@app.get("/api/v1/carbon/cloud/summary", tags=["Cloud Carbon"])
def get_cloud_carbon_summary(
    provider: CloudProvider = Query(CloudProvider.ALL, description="Cloud provider filter"),
    start_month: Optional[date] = Query(None, description="Start month"),
    end_month: Optional[date] = Query(None, description="End month")
):
    """
    Get summarized cloud carbon metrics.

    Returns totals and averages across all providers and services.
    """
    conn = get_db_connection()

    where_clauses = []
    params = {}

    if provider != CloudProvider.ALL:
        where_clauses.append("cloud_provider = $provider")
        params["provider"] = provider.value

    if start_month:
        where_clauses.append("usage_month_start >= $start_month")
        params["start_month"] = start_month

    if end_month:
        where_clauses.append("usage_month_start <= $end_month")
        params["end_month"] = end_month

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT
            cloud_provider,
            COUNT(*) as record_count,
            SUM(total_mtco2e) as total_mtco2e,
            AVG(total_mtco2e) as avg_mtco2e,
            SUM(scope1_kgco2e) / 1000 as scope1_mtco2e,
            SUM(scope2_market_based_kgco2e) / 1000 as scope2_mtco2e,
            SUM(scope3_kgco2e) / 1000 as scope3_mtco2e,
            COUNT(DISTINCT account_id) as num_accounts,
            COUNT(DISTINCT service_name) as num_services,
            COUNT(DISTINCT region) as num_regions
        FROM marts.fact_cloud_carbon
        {where_sql}
        GROUP BY cloud_provider
        ORDER BY total_mtco2e DESC
    """

    result = conn.execute(query, params).fetchdf()

    return {
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


# Grid Intensity Endpoints
@app.get("/api/v1/carbon/grid", tags=["Grid Carbon"])
def get_grid_intensity(
    region: Optional[str] = Query(None, description="Grid region/zone filter"),
    source: DataSource = Query(DataSource.ALL, description="Data source filter"),
    start_time: Optional[datetime] = Query(None, description="Start timestamp"),
    end_time: Optional[datetime] = Query(None, description="End timestamp"),
    limit: int = Query(1000, ge=1, le=10000, description="Max records to return")
):
    """
    Query grid carbon intensity data.

    Returns hourly carbon intensity from Electricity Maps and WattTime.
    Data from dbt mart: marts.fact_grid_intensity
    """
    conn = get_db_connection()

    where_clauses = []
    params = {}

    if region:
        where_clauses.append("grid_region ILIKE $region")
        params["region"] = f"%{region}%"

    if source != DataSource.ALL:
        where_clauses.append("data_source = $source")
        params["source"] = source.value

    if start_time:
        where_clauses.append("timestamp_hour >= $start_time")
        params["start_time"] = start_time

    if end_time:
        where_clauses.append("timestamp_hour <= $end_time")
        params["end_time"] = end_time

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT
            grid_region,
            timestamp_hour,
            carbon_intensity_gco2eq_per_kwh,
            carbon_intensity_kgco2eq_per_kwh,
            fossil_fuel_percentage,
            renewable_percentage,
            intensity_category,
            data_source
        FROM marts.fact_grid_intensity
        {where_sql}
        ORDER BY timestamp_hour DESC
        LIMIT {limit}
    """

    result = conn.execute(query, params).fetchdf()

    return {
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


@app.get("/api/v1/carbon/grid/current", tags=["Grid Carbon"])
def get_current_grid_intensity(
    region: Optional[str] = Query(None, description="Grid region/zone filter")
):
    """
    Get most recent grid carbon intensity.

    Returns the latest hourly reading for each grid region.
    """
    conn = get_db_connection()

    where_clause = "WHERE grid_region ILIKE $region" if region else ""
    params = {"region": f"%{region}%"} if region else {}

    query = f"""
        WITH latest AS (
            SELECT
                grid_region,
                MAX(timestamp_hour) as max_hour
            FROM marts.fact_grid_intensity
            {where_clause}
            GROUP BY grid_region
        )
        SELECT
            g.grid_region,
            g.timestamp_hour,
            g.carbon_intensity_gco2eq_per_kwh,
            g.intensity_category,
            g.fossil_fuel_percentage,
            g.renewable_percentage,
            g.data_source
        FROM marts.fact_grid_intensity g
        JOIN latest l ON g.grid_region = l.grid_region AND g.timestamp_hour = l.max_hour
        ORDER BY g.carbon_intensity_gco2eq_per_kwh DESC
    """

    result = conn.execute(query, params).fetchdf()

    return {
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


# Trends Endpoint
@app.get("/api/v1/carbon/trends", tags=["Trends"])
def get_carbon_trends(
    provider: CloudProvider = Query(CloudProvider.ALL, description="Cloud provider filter"),
    account_id: Optional[str] = Query(None, description="Account/Project ID filter"),
    limit: int = Query(12, ge=1, le=48, description="Number of months")
):
    """
    Get monthly carbon trends with MoM changes and rolling averages.

    Data from dbt mart: marts.carbon_trends_monthly
    """
    conn = get_db_connection()

    where_clauses = []
    params = {}

    if provider != CloudProvider.ALL:
        where_clauses.append("cloud_provider = $provider")
        params["provider"] = provider.value

    if account_id:
        where_clauses.append("account_id = $account_id")
        params["account_id"] = account_id

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
        SELECT
            month,
            cloud_provider,
            account_id,
            total_mtco2e,
            scope1_percent,
            scope2_percent,
            scope3_percent,
            mom_change_percent,
            rolling_3mo_avg_kgco2e / 1000 as rolling_3mo_avg_mtco2e,
            ytd_total_kgco2e / 1000 as ytd_total_mtco2e,
            trend_indicator,
            kgco2e_per_dollar
        FROM marts.carbon_trends_monthly
        {where_sql}
        ORDER BY month DESC
        LIMIT {limit}
    """

    result = conn.execute(query, params).fetchdf()

    return {
        "count": len(result),
        "data": result.to_dict(orient="records")
    }


# Export Endpoints
@app.get("/api/v1/exports/parquet/{table}", tags=["Exports"])
def export_table_parquet(
    table: str = PathParam(..., description="Table name (cloud_carbon, grid_intensity, trends)")
):
    """
    Export table as Parquet file.

    Downloads the full table as a Parquet file for bulk access.
    """
    conn = get_db_connection()

    # Map friendly names to actual table names
    table_map = {
        "cloud_carbon": "marts.fact_cloud_carbon",
        "grid_intensity": "marts.fact_grid_intensity",
        "trends": "marts.carbon_trends_monthly"
    }

    if table not in table_map:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table}' not found. Available: {list(table_map.keys())}"
        )

    full_table = table_map[table]

    # Export to temp parquet file
    temp_path = Path(f"/tmp/esg_{table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet")

    query = f"COPY (SELECT * FROM {full_table}) TO '{temp_path}' (FORMAT PARQUET)"
    conn.execute(query)

    return FileResponse(
        path=temp_path,
        media_type="application/octet-stream",
        filename=f"{table}.parquet"
    )


@app.get("/api/v1/exports/csv/{table}", tags=["Exports"])
def export_table_csv(
    table: str = PathParam(..., description="Table name"),
    limit: int = Query(10000, ge=1, le=100000, description="Max rows")
):
    """
    Export table as CSV file.

    Downloads table data as CSV (limited to prevent timeouts).
    """
    conn = get_db_connection()

    table_map = {
        "cloud_carbon": "marts.fact_cloud_carbon",
        "grid_intensity": "marts.fact_grid_intensity",
        "trends": "marts.carbon_trends_monthly"
    }

    if table not in table_map:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table}' not found"
        )

    full_table = table_map[table]

    query = f"SELECT * FROM {full_table} LIMIT {limit}"
    result = conn.execute(query).fetchdf()

    # Convert to CSV
    csv_buffer = io.StringIO()
    result.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={table}.csv"}
    )


@app.get("/api/v1/query", tags=["Advanced"])
def execute_query(
    sql: str = Query(..., description="SQL query to execute (SELECT only)"),
    format: str = Query("json", description="Output format (json, csv)")
):
    """
    Execute arbitrary SQL query against warehouse.

    Security: Only SELECT statements allowed. Read-only access.
    """
    conn = get_db_connection()

    # Validate query is SELECT only
    sql_lower = sql.strip().lower()
    if not sql_lower.startswith("select"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries allowed"
        )

    if any(keyword in sql_lower for keyword in ["drop", "delete", "insert", "update", "alter", "create"]):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries allowed"
        )

    try:
        result = conn.execute(sql).fetchdf()

        if format == "csv":
            csv_buffer = io.StringIO()
            result.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return StreamingResponse(
                iter([csv_buffer.getvalue()]),
                media_type="text/csv"
            )
        else:
            return {
                "count": len(result),
                "data": result.to_dict(orient="records")
            }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
