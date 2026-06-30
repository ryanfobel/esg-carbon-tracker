# ESG Evidence Dashboard

Evidence.dev dashboard for visualizing multi-cloud carbon footprint and grid intensity data.

## Features

- **Overview**: Total emissions, scope breakdown, provider comparison
- **Grid Intensity**: Real-time carbon intensity, fuel mix, regional trends
- **Trends**: Month-over-month changes, rolling averages, YTD cumulative

## Installation

```bash
cd projects/esg-evidence

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at http://localhost:3000

## Data Source

Evidence connects directly to the DuckDB warehouse at `~/.paimon/esg_data/warehouse.duckdb`.

The dashboard queries dbt marts:
- `marts.fact_cloud_carbon` - Unified cloud emissions
- `marts.fact_grid_intensity` - Grid carbon intensity
- `marts.carbon_trends_monthly` - Monthly trends

## Building for Production

```bash
# Build static site
npm run build

# Output in build/ directory
```

## Publishing to GitHub Pages

The Evidence dashboard can be published as a static site to GitHub Pages:

### Option 1: Manual Build

```bash
# Build static site
npm run build

# Copy to docs/ for GitHub Pages
cp -r build/* ../../docs/esg-dashboard/

# Commit and push
git add docs/esg-dashboard
git commit -m "docs: update ESG dashboard"
git push
```

Enable GitHub Pages in repo settings → Pages → Source: `/docs` directory.

### Option 2: GitHub Actions

Create `.github/workflows/evidence-deploy.yml`:

```yaml
name: Deploy Evidence Dashboard

on:
  push:
    branches: [main]
    paths:
      - 'projects/esg-evidence/**'
      - 'projects/esg-pipelines/dbt/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install Evidence
        working-directory: projects/esg-evidence
        run: npm install

      - name: Build Dashboard
        working-directory: projects/esg-evidence
        run: npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./projects/esg-evidence/build
```

### Option 3: Evidence Cloud

Evidence offers managed hosting:

```bash
npm run build
evidence deploy
```

## Data Updates

The dashboard reflects the latest data in the DuckDB warehouse. To update:

```bash
# Run ESG pipelines to fetch new data
cd ../esg-pipelines
python pipelines/gcp_carbon.py YOUR_PROJECT_ID
python pipelines/aws_carbon.py
# ... other pipelines

# Run dbt to update marts
cd dbt
dbt run

# Dashboard will automatically show updated data
```

## Pages

- **`/`** (index.md) - Overview dashboard
- **`/grid`** - Grid carbon intensity
- **`/trends`** - Monthly trends and analysis

## Adding Pages

Create new Markdown files in `pages/`:

```markdown
# New Page

\`\`\`sql my_query
SELECT * FROM marts.fact_cloud_carbon
LIMIT 10
\`\`\`

<DataTable data={my_query} />
```

Evidence will automatically add it to the navigation.

## References

- Evidence Docs: https://docs.evidence.dev
- DuckDB Connector: https://docs.evidence.dev/core-concepts/data-sources/duckdb
- Component Library: https://docs.evidence.dev/components
