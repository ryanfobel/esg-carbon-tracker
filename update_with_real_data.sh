#!/bin/bash
# Update Evidence dashboard with real historical data

set -e

echo "🔄 Updating ESG Carbon Tracker with real data..."

cd "$(dirname "$0")"

# Step 1: Run pipelines
echo ""
echo "📊 Step 1: Fetching data from cloud providers..."
cd esg-pipelines

# Check if credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ] && ! aws sts get-caller-identity &>/dev/null; then
    echo "⚠️  AWS credentials not found. Skipping AWS pipeline."
    echo "   Run 'aws configure' or set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY"
else
    echo "  Running AWS pipeline..."
    pixi run python pipelines/aws_carbon.py || echo "  ⚠️  AWS pipeline failed"
fi

if ! gcloud auth list --filter=status:ACTIVE 2>/dev/null | grep -q ACTIVE; then
    echo "⚠️  GCP credentials not found. Skipping GCP pipeline."
    echo "   Run 'gcloud auth application-default login'"
else
    echo "  Running GCP pipeline..."
    pixi run python pipelines/gcp_carbon.py || echo "  ⚠️  GCP pipeline failed"
fi

# WattTime is optional
if [ -n "$WATTTIME_USERNAME" ]; then
    echo "  Running WattTime pipeline..."
    pixi run python pipelines/watttime.py || echo "  ⚠️  WattTime pipeline failed"
else
    echo "ℹ️  WattTime credentials not set. Skipping grid intensity."
    echo "   Sign up at https://www.watttime.org/ and set WATTTIME_USERNAME/PASSWORD"
fi

# Step 2: Run dbt
echo ""
echo "🔨 Step 2: Running dbt transformations..."
pixi run dbt-run

# Step 3: Export to CSV
echo ""
echo "📤 Step 3: Exporting to Evidence CSV format..."
pixi run python -c "
import duckdb
from pathlib import Path

warehouse_path = Path.home() / '.paimon/esg_data/warehouse.duckdb'
csv_dir = Path('esg-evidence/esg-evidence-new/sources/esg_data')

if not warehouse_path.exists():
    print('❌ Warehouse not found. No data to export.')
    exit(1)

conn = duckdb.connect(str(warehouse_path), read_only=True)

# Check if marts tables exist
tables = conn.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = 'marts'\").fetchall()
if not tables:
    print('❌ No marts tables found. Run dbt first.')
    exit(1)

# Export
conn.execute(f\"COPY marts.fact_cloud_carbon TO '{csv_dir}/fact_cloud_carbon.csv' (HEADER)\")
count = conn.execute('SELECT COUNT(*) FROM marts.fact_cloud_carbon').fetchone()[0]
print(f'  ✓ fact_cloud_carbon.csv ({count} rows)')

conn.execute(f\"COPY marts.fact_grid_intensity TO '{csv_dir}/fact_grid_intensity.csv' (HEADER)\")
count = conn.execute('SELECT COUNT(*) FROM marts.fact_grid_intensity').fetchone()[0]
print(f'  ✓ fact_grid_intensity.csv ({count} rows)')

conn.execute(f\"COPY marts.carbon_trends_monthly TO '{csv_dir}/carbon_trends_monthly.csv' (HEADER)\")
count = conn.execute('SELECT COUNT(*) FROM marts.carbon_trends_monthly').fetchone()[0]
print(f'  ✓ carbon_trends_monthly.csv ({count} rows)')

conn.close()
"

# Step 4: Rebuild Evidence
echo ""
echo "🎨 Step 4: Rebuilding Evidence dashboard..."
cd ../esg-evidence/esg-evidence-new
npm run sources
npm run build

echo ""
echo "✅ Dashboard updated with real data!"
echo ""
echo "Next steps:"
echo "  • Preview locally: npm run preview"
echo "  • Deploy: git add sources/esg_data/*.csv && git commit -m 'Update with real data' && git push"
