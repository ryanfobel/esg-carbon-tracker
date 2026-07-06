"""
GCP Carbon Footprint Pipeline

Extracts carbon emissions data from Google Cloud Platform using BigQuery.

Data Source: GCP Carbon Footprint (BigQuery Data Transfer)
Scopes: 1, 2 (location-based, market-based), 3
Refresh: Monthly (15th of following month)
Latency: 45-60 days post-month-end

References:
- https://cloud.google.com/carbon-footprint
- https://docs.cloud.google.com/carbon-footprint/docs/api
- Architecture: docs/architecture/esg-data-pipeline.md Section 2.1

Authentication:
- Service Account with roles/bigquery.dataViewer, roles/bigquery.jobUser
- Credentials via keystore: dt keystore set gcp.service_account_json /path/to/key.json
"""

import dlt
from typing import Iterator, Dict, Any
from datetime import datetime, date
from pathlib import Path
import os


@dlt.resource(
    name="gcp_carbon_footprint",
    primary_key="id",
    write_disposition="merge",
    merge_key=["project_id", "service_description", "location_region", "usage_month"]
)
def gcp_carbon_footprint(
    project_id: str,
    dataset_id: str = "carbon_footprint_dataset",
    table_id: str = "carbon_footprint",
    lookback_months: int = 3
) -> Iterator[Dict[str, Any]]:
    """
    Extract GCP Carbon Footprint data from BigQuery.

    Args:
        project_id: GCP project ID containing carbon footprint data
        dataset_id: BigQuery dataset ID (default: carbon_footprint_dataset)
        table_id: BigQuery table ID (default: carbon_footprint)
        lookback_months: Number of months to fetch initially (default: 3)

    Yields:
        Carbon footprint records with schema:
        {
            'id': str,  # Composite key
            'project_id': str,
            'service_description': str,  # e.g., "Compute Engine"
            'location_region': str,  # e.g., "us-central1"
            'usage_month': date,
            'scope1_kgco2e': float,
            'scope2_location_based_kgco2e': float,
            'scope2_market_based_kgco2e': float,
            'scope3_kgco2e': float,
            'total_kgco2e': float,
            'extracted_at': datetime
        }

    Incremental Loading:
        Uses dlt state to track last_usage_month.
        Only fetches months after last successful run.
    """
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
    except ImportError:
        raise ImportError(
            "google-cloud-bigquery required. Install with: "
            "pip install google-cloud-bigquery"
        )

    # Get credentials from keystore or environment
    credentials = _get_gcp_credentials()

    # Initialize BigQuery client
    client = bigquery.Client(
        credentials=credentials,
        project=project_id
    )

    # Get last processed month from dlt state (for incremental loading)
    last_month = dlt.current.resource_state().get("last_usage_month")

    if last_month:
        # Incremental: fetch only new months
        dlt.current.resource_state().setdefault("incremental_loads", 0)
        dlt.current.resource_state()["incremental_loads"] += 1
        min_month = last_month
    else:
        # Initial load: fetch last N months
        from datetime import timedelta
        min_month = (date.today() - timedelta(days=30 * lookback_months)).replace(day=1)

    # BigQuery SQL
    query = f"""
        SELECT
            CONCAT(
                project.id, '_',
                service.description, '_',
                location.region, '_',
                FORMAT_DATE('%Y-%m', usage_month)
            ) AS id,

            project.id AS project_id,
            service.description AS service_description,
            location.region AS location_region,
            usage_month,

            -- Scope emissions
            carbon_footprint_kgCO2e.scope1 AS scope1_kgco2e,
            carbon_footprint_kgCO2e.scope2.location_based AS scope2_location_based_kgco2e,
            carbon_footprint_kgCO2e.scope2.market_based AS scope2_market_based_kgco2e,
            carbon_footprint_kgCO2e.scope3 AS scope3_kgco2e,

            -- Total
            (
                IFNULL(carbon_footprint_kgCO2e.scope1, 0) +
                IFNULL(carbon_footprint_kgCO2e.scope2.location_based, 0) +
                IFNULL(carbon_footprint_kgCO2e.scope3, 0)
            ) AS total_kgco2e,

            CURRENT_TIMESTAMP() AS extracted_at

        FROM `{project_id}.{dataset_id}.{table_id}`
        WHERE usage_month >= @min_month
        ORDER BY usage_month DESC
    """

    # Query configuration
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "min_month",
                "DATE",
                min_month if isinstance(min_month, date) else date.fromisoformat(min_month)
            )
        ]
    )

    # Execute query
    print(f"Fetching GCP carbon data from {min_month}...")
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    # Yield records
    max_month = None
    row_count = 0

    for row in results:
        record = dict(row)

        # Track max month for state update
        if not max_month or record['usage_month'] > max_month:
            max_month = record['usage_month']

        row_count += 1
        yield record

    # Update state for next run
    if max_month:
        dlt.current.resource_state()["last_usage_month"] = max_month.isoformat()

    print(f"Extracted {row_count} records. Last month: {max_month}")


def _get_gcp_credentials():
    """
    Get GCP credentials from keystore or environment.

    Tries in order:
    1. Keystore: dt keystore get gcp.service_account_json
    2. Environment: GOOGLE_APPLICATION_CREDENTIALS
    3. Default credentials (gcloud auth application-default login)

    Returns:
        google.oauth2.service_account.Credentials
    """
    from google.oauth2 import service_account
    import json

    # Try keystore first (dt keystore set gcp.service_account_json /path/to/key.json)
    try:
        from data_toolbox.core.keystore import get_credential
        key_path = get_credential("gcp.service_account_json")
        if key_path and Path(key_path).exists():
            return service_account.Credentials.from_service_account_file(key_path)
    except (ImportError, Exception):
        pass

    # Try environment variable
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and Path(creds_path).exists():
        return service_account.Credentials.from_service_account_file(creds_path)

    # Fall back to default credentials
    print("Using default GCP credentials (gcloud auth application-default)")
    return None  # Will use default credentials


# dlt pipeline definition
def run_pipeline(
    project_id: str,
    warehouse_path: str = "~/.paimon/esg_data/warehouse.duckdb"
):
    """
    Run GCP Carbon Footprint pipeline.

    Args:
        project_id: GCP project ID
        warehouse_path: Path to DuckDB/Paimon warehouse

    Example:
        python pipelines/gcp_carbon.py YOUR_PROJECT_ID
    """
    # Expand user path
    warehouse_path = Path(warehouse_path).expanduser()
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)

    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="gcp_carbon_footprint",
        destination=dlt.destinations.duckdb(str(warehouse_path)),
        dataset_name="raw"
    )

    # Run pipeline
    load_info = pipeline.run(gcp_carbon_footprint(project_id))

    # Print summary
    print(f"\nPipeline completed:")
    print(f"  Status: {load_info.status}")
    print(f"  Destination: {warehouse_path}")
    print(f"  Dataset: raw")
    print(f"  Table: gcp_carbon_footprint")

    if load_info.has_failed_jobs:
        print(f"  ⚠ Failed jobs: {len(load_info.failed_jobs)}")
        for job in load_info.failed_jobs:
            print(f"    - {job.job_file_info.job_id}: {job.exception}")

    return load_info


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pipelines/gcp_carbon.py PROJECT_ID [WAREHOUSE_PATH]")
        print("\nExample:")
        print("  python pipelines/gcp_carbon.py my-gcp-project")
        print("  python pipelines/gcp_carbon.py my-gcp-project ~/.paimon/esg.duckdb")
        sys.exit(1)

    project_id = sys.argv[1]
    warehouse_path = sys.argv[2] if len(sys.argv) > 2 else "~/.paimon/esg_data/warehouse.duckdb"

    print(f"Running GCP Carbon Footprint pipeline...")
    print(f"  Project: {project_id}")
    print(f"  Warehouse: {warehouse_path}")
    print()

    run_pipeline(project_id, warehouse_path)
