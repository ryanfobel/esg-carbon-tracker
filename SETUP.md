# Setup Guide: Publishing ESG Carbon Tracker to GitHub

This guide will help you publish the ESG Carbon Tracker as a public repository on GitHub.

## Step 1: Create GitHub Repository

1. Go to [https://github.com/new](https://github.com/new)
2. Set the repository name: `esg-carbon-tracker`
3. Add description: "Open-source carbon emissions tracking for cloud infrastructure and grid electricity"
4. Choose **Public** visibility
5. Do **NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push to GitHub

```bash
cd /Users/ryan/dev/esg-carbon-tracker

# Add the remote (replace YOUR-USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR-USERNAME/esg-carbon-tracker.git

# Push to main branch
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select **GitHub Actions**
4. Click **Save**

## Step 4: Trigger First Deployment

The GitHub Actions workflow will automatically run on the next push. To trigger it immediately:

**Option A: Make a small change**
```bash
cd /Users/ryan/dev/esg-carbon-tracker
git commit --allow-empty -m "Trigger GitHub Pages deployment"
git push
```

**Option B: Use workflow dispatch**
1. Go to **Actions** tab on GitHub
2. Click **Deploy Evidence Dashboard** workflow
3. Click **Run workflow** → **Run workflow**

## Step 5: View Your Dashboard

After the workflow completes (usually 2-3 minutes):

1. Go to **Settings** → **Pages**
2. You'll see: "Your site is live at https://YOUR-USERNAME.github.io/esg-carbon-tracker/"
3. Click the link to view your dashboard

## Step 6: Update README Links

Update the README with your actual GitHub username:

```bash
cd /Users/ryan/dev/esg-carbon-tracker

# Replace YOUR-USERNAME with your actual GitHub username in README.md
# You can do this manually or with:
sed -i '' 's/YOUR-USERNAME/your-actual-username/g' README.md

git add README.md
git commit -m "Update README with actual GitHub username"
git push
```

## Troubleshooting

### Workflow Fails: "Permission denied"

If the GitHub Actions workflow fails with permission errors:

1. Go to **Settings** → **Actions** → **General**
2. Scroll to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**
6. Re-run the failed workflow

### Dashboard Shows 404

This means GitHub Pages hasn't been enabled or the build hasn't completed:

1. Check **Actions** tab - ensure the workflow completed successfully
2. Verify **Settings** → **Pages** shows "GitHub Actions" as source
3. Wait a few minutes for DNS propagation

### Sample Data Not Showing

The GitHub Actions workflow runs `init_sample_warehouse.py` during build. If data isn't showing:

1. Check the workflow logs in **Actions** tab
2. Verify the Evidence connection in `esg-evidence/esg-evidence-new/sources/connection.yaml`
3. Ensure the DuckDB file path matches between the sample script and Evidence config

## Local Testing

Before pushing, you can test locally:

```bash
# Generate sample data
cd esg-pipelines
pixi install
python init_sample_warehouse.py

# Preview dashboard
cd ../esg-evidence/esg-evidence-new
npm install
npm run dev
# Open http://localhost:3000
```

## Repository Settings

### Topics

Add these topics to make your repository discoverable:

1. Go to repository homepage
2. Click the gear icon next to "About"
3. Add topics:
   - `carbon-emissions`
   - `esg`
   - `sustainability`
   - `cloud-carbon-footprint`
   - `data-pipeline`
   - `duckdb`
   - `evidence`
   - `dbt`
   - `fastapi`
   - `environmental-impact`

### Social Preview

Upload a screenshot of your dashboard:

1. Take screenshot of dashboard
2. Go to **Settings** → **Options**
3. Scroll to **Social preview**
4. Click **Edit** → **Upload an image**

## Next Steps

### Add Real Data

Replace sample data with real cloud provider data:

1. Set up cloud provider credentials (see `esg-pipelines/README.md`)
2. Run pipelines: `pixi run all-pipelines`
3. Run dbt: `pixi run dbt-run`
4. Rebuild dashboard: `npm run build`

### Customize Dashboard

Edit Evidence dashboard pages in `esg-evidence/esg-evidence-new/pages/`:
- `index.md` - Overview page
- `trends.md` - Trends analysis
- `grid.md` - Grid intensity

### Add CI Tests

Consider adding tests to the GitHub Actions workflow:
```yaml
- name: Run Tests
  run: |
    cd esg-pipelines
    pixi run pytest
```

## Support

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions or share ideas
- **Documentation**: See README.md for full documentation

---

**Ready to publish?** Follow Steps 1-3 above to make your repository public!
