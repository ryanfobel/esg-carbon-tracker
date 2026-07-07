# Setting Up Real Data Sources

Step-by-step guide to configure real ESG data pipelines.

## Prerequisites

- Python 3.11+ with pixi environment
- Git repository cloned
- Cloud provider accounts (GCP, AWS)

---

## Part 1: GCP Carbon Footprint Data

### Step 1: Enable Carbon Footprint in GCP

1. **Go to GCP Console**: https://console.cloud.google.com
2. **Select your project** (or create one)
3. **Enable Carbon Footprint**:
   - Navigate to: **Billing → Reports → Carbon Footprint**
   - Click **"Enable Carbon Footprint"**
   - This creates a BigQuery dataset in your project

4. **Note your project ID**: You'll need this later

### Step 2: Create Service Account

1. **Go to IAM & Admin → Service Accounts**:
   https://console.cloud.google.com/iam-admin/serviceaccounts

2. **Create Service Account**:
   - Name: `esg-carbon-reader`
   - Description: "Read carbon footprint data for ESG dashboard"

3. **Grant Permissions**:
   - `BigQuery Data Viewer`
   - `BigQuery Job User`

4. **Create Key**:
   - Click on the service account
   - Go to **Keys** tab
   - Click **Add Key → Create new key → JSON**
   - Download the JSON key file
   - Save it securely (e.g., `~/.gcp/esg-carbon-sa-key.json`)

### Step 3: Configure Pipeline

```bash
cd /Users/ryan/dev/esg-carbon-tracker/pipelines

# Set GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.gcp/esg-carbon-sa-key.json"

# Or store in dlt secrets (recommended)
mkdir -p .dlt
cat > .dlt/secrets.toml <<EOF
[sources.gcp_carbon]
credentials = "$HOME/.gcp/esg-carbon-sa-key.json"
project_id = "YOUR_GCP_PROJECT_ID"
EOF
```

### Step 4: Test GCP Pipeline

```bash
# Run the pipeline
pixi run python -c "
from pipelines.gcp_carbon import gcp_carbon_footprint
import dlt

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name='gcp_carbon',
    destination='duckdb',
    dataset_name='esg_data',
    dev_mode=True
)

# Load data
data = gcp_carbon_footprint(
    project_id='YOUR_GCP_PROJECT_ID',
    lookback_months=6
)

# Run
info = pipeline.run(data)
print(info)
"
```

**Expected Output**:
- Should fetch 6 months of carbon footprint data
- Data written to warehouse/esg_data.duckdb
- Look for: "Pipeline gcp_carbon completed in X seconds"

---

## Part 2: AWS Customer Carbon Footprint

### Step 1: Enable Carbon Footprint Tool in AWS

1. **Go to AWS Cost Management Console**:
   https://console.aws.amazon.com/cost-management/home

2. **Navigate to**: Cost Management → Customer Carbon Footprint Tool

3. **Enable the tool** (if not already enabled)

4. **Note**: It may take 24-48 hours for initial data to appear

### Step 2: Create IAM User/Role

1. **Go to IAM Console**:
   https://console.aws.amazon.com/iam/

2. **Create User** (or use existing):
   - Name: `esg-carbon-reader`
   - Access type: **Programmatic access**

3. **Attach Policies**:
   - `AWSSustainabilityReadOnlyAccess` (if available)
   - Or create custom policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "sustainability:GetCarbonFootprintSummary"
      ],
      "Resource": "*"
    }
  ]
}
```

4. **Create Access Key**:
   - Download and save the Access Key ID and Secret Access Key

### Step 3: Configure Pipeline

```bash
cd /Users/ryan/dev/esg-carbon-tracker/pipelines

# Option 1: Environment variables
export AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export AWS_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export AWS_DEFAULT_REGION="us-east-1"

# Option 2: dlt secrets (recommended)
cat >> .dlt/secrets.toml <<EOF

[sources.aws_carbon]
aws_access_key_id = "YOUR_ACCESS_KEY"
aws_secret_access_key = "YOUR_SECRET_KEY"
region = "us-east-1"
EOF
```

### Step 4: Test AWS Pipeline

```bash
pixi run python -c "
from pipelines.aws_carbon import aws_carbon_footprint
import dlt

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name='aws_carbon',
    destination='duckdb',
    dataset_name='esg_data',
    dev_mode=True
)

# Load data
data = aws_carbon_footprint(lookback_months=6)

# Run
info = pipeline.run(data)
print(info)
"
```

**Expected Output**:
- Should fetch 6 months of carbon footprint data
- Data written to warehouse/esg_data.duckdb

---

## Part 3: WattTime Grid Intensity Data (FREE - North America)

### Step 1: Register for WattTime

1. **Sign up**: https://www.watttime.org/api-documentation/#register-new-user

```bash
# Register new user
curl -X POST https://api.watttime.org/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-email@example.com",
    "password": "your-secure-password",
    "email": "your-email@example.com",
    "org": "Your Organization Name"
  }'
```

2. **Note your credentials** (username and password)

### Step 2: Configure Pipeline

```bash
cat >> .dlt/secrets.toml <<EOF

[sources.watttime]
username = "your-email@example.com"
password = "your-secure-password"
EOF
```

### Step 3: Test WattTime Pipeline

```bash
pixi run python -c "
from pipelines.watttime import watttime_grid_intensity
import dlt

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name='watttime',
    destination='duckdb',
    dataset_name='esg_data',
    dev_mode=True
)

# Load data for key North American regions
regions = ['CAISO_NORTH', 'MISO_WEST', 'PJM', 'IESO']

data = watttime_grid_intensity(
    regions=regions,
    lookback_hours=168  # 7 days
)

# Run
info = pipeline.run(data)
print(info)
"
```

---

## Part 4: Run Complete Data Pipeline

Once all sources are configured, run the full pipeline:

```bash
cd /Users/ryan/dev/esg-carbon-tracker/pipelines

# Create master pipeline script
cat > run_all_pipelines.py <<'EOF'
"""
Master pipeline script - runs all data sources
"""
import dlt
from pipelines.gcp_carbon import gcp_carbon_footprint
from pipelines.aws_carbon import aws_carbon_footprint
from pipelines.watttime import watttime_grid_intensity
from datetime import datetime

def run_all():
    print(f"Starting data pipeline run at {datetime.now()}")

    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name='esg_data',
        destination='duckdb',
        dataset_name='esg_data'
    )

    # 1. GCP Carbon
    print("\n1. Fetching GCP carbon data...")
    gcp_data = gcp_carbon_footprint(
        project_id='YOUR_GCP_PROJECT_ID',
        lookback_months=6
    )
    info = pipeline.run(gcp_data, table_name='fact_cloud_carbon')
    print(f"   Loaded {info.metrics.get('rows_loaded', 0)} GCP rows")

    # 2. AWS Carbon
    print("\n2. Fetching AWS carbon data...")
    aws_data = aws_carbon_footprint(lookback_months=6)
    info = pipeline.run(aws_data, table_name='fact_cloud_carbon')
    print(f"   Loaded {info.metrics.get('rows_loaded', 0)} AWS rows")

    # 3. WattTime Grid Intensity
    print("\n3. Fetching grid intensity data...")
    regions = ['CAISO_NORTH', 'MISO_WEST', 'PJM', 'IESO', 'NYISO']
    grid_data = watttime_grid_intensity(
        regions=regions,
        lookback_hours=168  # 7 days
    )
    info = pipeline.run(grid_data, table_name='fact_grid_intensity')
    print(f"   Loaded {info.metrics.get('rows_loaded', 0)} grid intensity rows")

    print(f"\n✓ Pipeline completed at {datetime.now()}")

if __name__ == '__main__':
    run_all()
EOF

# Run it
pixi run python run_all_pipelines.py
```

---

## Part 5: Update Dashboard

After loading real data, rebuild the dashboard views:

```bash
# Rebuild derived tables
pixi run python create_regional_tables.py

# Rebuild dim_grid_regions with real regions
# (You'll need to update this based on actual regions in the data)

# Restart Evidence dashboard (if running)
# It should auto-reload with new data
```

---

## Scheduling Automatic Updates

### Option 1: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /Users/ryan/dev/esg-carbon-tracker/pipelines && pixi run python run_all_pipelines.py >> /tmp/esg-pipeline.log 2>&1
```

### Option 2: GitHub Actions

Create `.github/workflows/update-data.yml`:

```yaml
name: Update ESG Data

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: prefix-dev/setup-pixi@v0.4.1
      - name: Run pipelines
        env:
          GCP_CREDENTIALS: ${{ secrets.GCP_CREDENTIALS }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          WATTTIME_USERNAME: ${{ secrets.WATTTIME_USERNAME }}
          WATTTIME_PASSWORD: ${{ secrets.WATTTIME_PASSWORD }}
        run: |
          cd pipelines
          pixi run python run_all_pipelines.py
      - name: Commit updated data
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add warehouse/
          git commit -m "chore: update ESG data $(date +%Y-%m-%d)" || exit 0
          git push
```

---

## Troubleshooting

### GCP: "Permission denied" error
- Check service account has `BigQuery Data Viewer` role
- Verify credentials file path is correct
- Ensure Carbon Footprint is enabled in your project

### AWS: "Access denied" error
- Check IAM user has `ce:GetCostAndUsage` permission
- Verify Carbon Footprint Tool is enabled (may take 24-48 hours)
- Try `aws sts get-caller-identity` to verify credentials

### WattTime: "Invalid credentials"
- Verify username/password are correct
- Check if account is activated (check email)
- Try logging in via website first

### No data returned
- Cloud carbon data has 19-60 day latency - recent months may be empty
- AWS Carbon Footprint needs 24-48 hours after enabling
- WattTime free tier has rate limits - space out requests

---

## Next Steps

1. **Set up GCP credentials** (Step 1-3 above)
2. **Set up AWS credentials** (Step 1-3 above)
3. **Register for WattTime** (Step 1-2 above)
4. **Run test pipelines** to verify each source works
5. **Run master pipeline** to load all data
6. **Set up scheduling** for automatic updates

**Need help?** Check the troubleshooting section or open an issue on GitHub.
