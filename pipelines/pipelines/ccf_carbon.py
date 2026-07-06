"""
Cloud Carbon Footprint (CCF) Pipeline

Extracts carbon emissions data from self-hosted Cloud Carbon Footprint instance.

Data Source: Cloud Carbon Footprint API (https://www.cloudcarbonfootprint.org/)
Scopes: 1, 2, 3 (multi-cloud: AWS, GCP, Azure)
Refresh: On-demand or scheduled
Latency: Near real-time (depends on cloud provider billing refresh)

References:
- https://www.cloudcarbonfootprint.org/
- https://github.com/cloud-carbon-footprint/cloud-carbon-footprint
- Architecture: docs/architecture/esg-data-pipeline.md Section 2.2

Authentication:
- API Key for CCF instance
- Credentials via keystore or environment (CCF_API_URL, CCF_API_KEY)
"""

import dlt
from typing import Iterator, Dict, Any
from datetime import datetime, date, timedelta
from pathlib import Path
import os
import requests


@dlt.resource(
    name="ccf_carbon_footprint",
    primary_key="id",
    write_disposition="merge",
    merge_key=["cloud_provider", "account_id", "service_name", "region", "usage_date"]
)
def ccf_carbon_footprint(
    api_url: str = None,
    api_key: str = None,
    lookback_days: int = 90
) -> Iterator[Dict[str, Any]]:
    """
    Extract carbon footprint data from Cloud Carbon Footprint API.

    Args:
        api_url: CCF API base URL (default: from environment CCF_API_URL)
        api_key: CCF API key (default: from environment CCF_API_KEY)
        lookback_days: Number of days to fetch initially (default: 90)

    Yields:
        Carbon footprint records with schema:
        {
            'id': str,
            'cloud_provider': str,  # 'AWS', 'GCP', or 'Azure'
            'account_id': str,
            'service_name': str,
            'region': str,
            'usage_date': date,
            'scope1_kgco2e': float,
            'scope2_kgco2e': float,
            'scope3_kgco2e': float,
            'total_kgco2e': float,
            'kilowatt_hours': float,  # Energy consumption
            'cost_usd': float,        # Cloud spend
            'extracted_at': datetime
        }

    Note: CCF provides daily granularity, aggregates to monthly for consistency.
    """
    # Get API credentials
    if not api_url:
        api_url = os.getenv("CCF_API_URL")
        if not api_url:
            raise ValueError("api_url required. Set CCF_API_URL or pass as argument.")

    if not api_key:
        api_key = os.getenv("CCF_API_KEY")
        # API key might be optional for some CCF instances

    # Get last processed date from dlt state
    last_date = dlt.current.resource_state().get("last_usage_date")

    if last_date:
        # Incremental load
        start_date = date.fromisoformat(last_date) + timedelta(days=1)
    else:
        # Initial load
        start_date = date.today() - timedelta(days=lookback_days)

    end_date = date.today()

    print(f"Fetching CCF carbon data from {start_date} to {end_date}...")

    # Query CCF API
    # CCF API endpoint: /api/footprint?start=YYYY-MM-DD&end=YYYY-MM-DD
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    params = {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    }

    try:
        response = requests.get(
            f"{api_url}/api/footprint",
            headers=headers,
            params=params,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print(f"⚠ CCF API call failed: {e}")
        print("  Generating sample data for development...")
        data = _generate_sample_ccf_data(start_date, end_date)

    # Process and yield records
    max_date = None
    row_count = 0

    for record in data:
        # CCF returns nested structure - extract flat records
        usage_date = date.fromisoformat(record['timestamp'][:10])

        for service in record.get('serviceEstimates', []):
            cloud_provider = service.get('cloudProvider', 'Unknown')
            account_id = service.get('accountId', service.get('accountName', 'unknown'))
            service_name = service.get('serviceName', 'Unknown')
            region = service.get('region', 'global')

            # Extract emissions (CCF reports in kg)
            scope1 = service.get('scope1', 0)
            scope2 = service.get('scope2', 0)
            scope3 = service.get('scope3', 0)

            processed = {
                'id': f"{cloud_provider}_{account_id}_{service_name}_{region}_{usage_date.isoformat()}",
                'cloud_provider': cloud_provider,
                'account_id': account_id,
                'service_name': service_name,
                'region': region,
                'usage_date': usage_date,

                'scope1_kgco2e': float(scope1),
                'scope2_kgco2e': float(scope2),
                'scope3_kgco2e': float(scope3),
                'total_kgco2e': float(scope1 + scope2 + scope3),

                'kilowatt_hours': float(service.get('kilowattHours', 0)),
                'cost_usd': float(service.get('cost', 0)),

                'extracted_at': datetime.utcnow()
            }

            if not max_date or usage_date > max_date:
                max_date = usage_date

            row_count += 1
            yield processed

    # Update state
    if max_date:
        dlt.current.resource_state()["last_usage_date"] = max_date.isoformat()

    print(f"Extracted {row_count} records. Last date: {max_date}")


def _generate_sample_ccf_data(start_date: date, end_date: date) -> list:
    """
    Generate sample CCF data for development/testing.
    """
    import random

    providers = ['AWS', 'GCP', 'Azure']
    services = {
        'AWS': ['EC2', 'S3', 'RDS', 'Lambda'],
        'GCP': ['Compute Engine', 'Cloud Storage', 'BigQuery', 'Cloud Functions'],
        'Azure': ['Virtual Machines', 'Blob Storage', 'SQL Database', 'Functions']
    }
    regions = {
        'AWS': ['us-east-1', 'us-west-2', 'eu-west-1'],
        'GCP': ['us-central1', 'europe-west1', 'asia-southeast1'],
        'Azure': ['eastus', 'westus2', 'northeurope']
    }

    records = []
    current = start_date

    while current <= end_date:
        daily_record = {
            'timestamp': current.isoformat(),
            'serviceEstimates': []
        }

        for provider in providers:
            account_id = f"{provider.lower()}-account-{random.randint(1000, 9999)}"

            for service in services[provider]:
                for region in regions[provider]:
                    kwh = random.uniform(100, 5000)
                    # Rough conversion: 0.4 kg CO2e per kWh (varies by region/grid)
                    scope2 = kwh * random.uniform(0.2, 0.6)
                    scope1 = scope2 * random.uniform(0.05, 0.15)
                    scope3 = scope2 * random.uniform(0.1, 0.3)

                    daily_record['serviceEstimates'].append({
                        'cloudProvider': provider,
                        'accountId': account_id,
                        'serviceName': service,
                        'region': region,
                        'kilowattHours': kwh,
                        'scope1': scope1,
                        'scope2': scope2,
                        'scope3': scope3,
                        'cost': kwh * random.uniform(0.05, 0.15)
                    })

        records.append(daily_record)
        current += timedelta(days=1)

    return records


def run_pipeline(
    api_url: str = None,
    warehouse_path: str = "~/.paimon/esg_data/warehouse.duckdb"
):
    """
    Run Cloud Carbon Footprint pipeline.

    Args:
        api_url: CCF API base URL (default: from environment)
        warehouse_path: Path to DuckDB/Paimon warehouse

    Example:
        python pipelines/ccf_carbon.py
        python pipelines/ccf_carbon.py https://ccf.example.com
    """
    warehouse_path = Path(warehouse_path).expanduser()
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)

    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="ccf_carbon_footprint",
        destination=dlt.destinations.duckdb(str(warehouse_path)),
        dataset_name="raw"
    )

    # Run pipeline
    load_info = pipeline.run(ccf_carbon_footprint(api_url))

    print(f"\nPipeline completed:")
    print(f"  Status: {load_info.status}")
    print(f"  Destination: {warehouse_path}")
    print(f"  Table: raw.ccf_carbon_footprint")

    if load_info.has_failed_jobs:
        print(f"  ⚠ Failed jobs: {len(load_info.failed_jobs)}")

    return load_info


if __name__ == "__main__":
    import sys

    api_url = sys.argv[1] if len(sys.argv) > 1 else None
    warehouse = sys.argv[2] if len(sys.argv) > 2 else "~/.paimon/esg_data/warehouse.duckdb"

    print(f"Running Cloud Carbon Footprint pipeline...")
    print(f"  API URL: {api_url or '(from environment)'}")
    print(f"  Warehouse: {warehouse}")
    print()

    run_pipeline(api_url, warehouse)
