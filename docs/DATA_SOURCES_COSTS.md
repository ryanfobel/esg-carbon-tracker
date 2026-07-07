# Data Sources: Costs & Update Frequencies

This document outlines the costs and recommended update frequencies for real ESG data sources.

## Cloud Provider Carbon Footprint Data

### Google Cloud Platform (GCP)
- **Cost**: **FREE** (uses your existing GCP project)
- **API**: [Carbon Footprint BigQuery Export](https://cloud.google.com/carbon-footprint)
- **Requirements**:
  - GCP project with billing enabled
  - Service account credentials
  - Carbon Footprint BigQuery export enabled (free)
- **Update Frequency**: Monthly (data refreshes 15th of following month)
- **Latency**: 45-60 days post-month-end
- **Recommended Refresh**: **Once per month** (after 15th)

### Amazon Web Services (AWS)
- **Cost**: **FREE** (uses your existing AWS account)
- **API**: [Customer Carbon Footprint Tool](https://aws.amazon.com/aws-cost-management/aws-customer-carbon-footprint-tool/)
- **Requirements**: AWS account with Cost Explorer enabled
- **Update Frequency**: Monthly
- **Latency**: ~21 days post-month-end
- **Recommended Refresh**: **Once per month** (after 21st)

### Microsoft Azure
- **Cost**: **FREE** (uses your existing Azure subscription)
- **API**: [Emissions Impact Dashboard](https://learn.microsoft.com/en-us/azure/carbon-optimization/)
- **Requirements**: Azure subscription
- **Update Frequency**: Monthly
- **Latency**: 19-30 days post-month-end
- **Recommended Refresh**: **Once per month** (after month-end)

**💡 Cloud Provider Summary**: All cloud carbon data is **FREE** - you're just accessing your own usage data.

---

## Grid Carbon Intensity Data

### Option 1: Electricity Maps (Commercial)

#### Pricing Tiers:
- **Starter**: €99/month
  - 100,000 API calls/month
  - Historical data (24 months)
  - ~200 zones worldwide

- **Professional**: €299/month
  - 500,000 API calls/month
  - Historical data (unlimited)
  - Priority support

- **Enterprise**: Custom pricing
  - Unlimited API calls
  - SLA guarantees
  - Custom integrations

#### Coverage:
- 200+ grid zones globally
- 5-minute update intervals
- Real-time and historical data

#### Recommended Usage:
- **For real-time dashboard**: 1 call per zone per hour = ~4,800 calls/day
  - For 50 zones: 240,000 calls/month → **Starter tier ($99/mo)**
  - For 200 zones: 960,000 calls/month → **Professional tier ($299/mo)**

- **For daily batch updates**: 1 call per zone per day = ~200 calls/day
  - For 200 zones: 6,000 calls/month → **Starter tier ($99/mo)** ✅

**💡 Cost-Effective Strategy**:
- Update once per day during off-peak hours
- Store historical data locally to avoid repeated API calls
- Start with key zones (50-100), expand as needed

### Option 2: WattTime (Free & Paid)

#### Pricing:
- **Free Tier**: **$0/month**
  - Non-commercial use only
  - Real-time MOER (Marginal Operating Emissions Rate)
  - North America coverage
  - Rate limits: ~500 calls/day

- **Pro Tier**: Custom pricing
  - Commercial use
  - Higher rate limits
  - Historical data access

#### Coverage:
- Primarily North America (US, Canada)
- Real-time MOER data
- 5-minute updates

#### Recommended Usage:
- **Best for**: North American-focused projects with limited budget
- **Update frequency**: Hourly or daily
- **Limitation**: Not global - only covers North America

### Option 3: Public Grid Operator APIs (FREE)

Many grid operators provide free public APIs:

#### IESO (Ontario, Canada)
- **Cost**: **FREE**
- **API**: http://reports.ieso.ca/public/
- **Data**: Real-time generation mix, demand, emissions
- **Update Frequency**: 5-minute intervals
- **Coverage**: Ontario only
- **Recommended Refresh**: Hourly

#### CAISO (California)
- **Cost**: **FREE**
- **API**: http://www.caiso.com/Pages/default.aspx
- **Data**: Real-time generation, emissions intensity
- **Coverage**: California only

#### UK National Grid ESO
- **Cost**: **FREE**
- **API**: https://carbon-intensity.github.io/api-definitions/
- **Data**: Carbon intensity forecasts and historical data
- **Coverage**: UK only
- **Update Frequency**: 30-minute intervals

#### Other Free Sources:
- **ENTSOE** (Europe): https://transparency.entsoe.eu/
- **EIA** (US): https://www.eia.gov/opendata/
- **Electricity System Operator (ESO)** (UK)

**💡 Free Grid Data Strategy**:
- Use free regional APIs where available (IESO, CAISO, UK, etc.)
- Supplement with Electricity Maps/WattTime for regions without free APIs
- Mix free and paid sources to minimize costs

---

## Recommended Cost-Effective Setup

### Minimal Cost Option (~$99-299/month)
1. **Cloud Carbon Data**: FREE (use existing accounts)
   - Refresh: Monthly

2. **Grid Intensity**:
   - **Primary**: WattTime Free Tier (North America)
   - **Supplement**: Electricity Maps Starter ($99/mo) for global coverage
   - Refresh: Daily batch updates

3. **Total Monthly Cost**: **$0-99/month**

### Comprehensive Option (~$299/month)
1. **Cloud Carbon Data**: FREE
   - Refresh: Monthly

2. **Grid Intensity**:
   - Electricity Maps Professional ($299/mo)
   - 200 zones globally
   - Hourly updates

3. **Total Monthly Cost**: **$299/month**

### Enterprise Option (Custom pricing)
1. **Cloud Carbon Data**: FREE
2. **Grid Intensity**: Electricity Maps Enterprise
3. **Additional**: Custom data sources, real-time feeds

---

## Update Frequency Recommendations

### Cloud Provider Data
- **Frequency**: Monthly
- **Timing**: 15th-21st of month (after data refresh)
- **Why**: Data only updates monthly with 19-60 day latency
- **Cost Impact**: None (FREE)

### Grid Intensity Data

#### Real-Time Dashboard (Highest Cost)
- **Frequency**: Every 5-60 minutes
- **API Calls**: ~480,000-2M calls/month (200 zones)
- **Cost**: $299-999/month
- **Use Case**: Live operations, real-time optimization

#### Daily Updates (Cost-Effective) ✅
- **Frequency**: Once per day (e.g., 2 AM UTC)
- **API Calls**: ~6,000 calls/month (200 zones)
- **Cost**: $99/month
- **Use Case**: Trend analysis, reporting, dashboards

#### Weekly Updates (Minimal Cost)
- **Frequency**: Once per week
- **API Calls**: ~800 calls/month (200 zones)
- **Cost**: $99/month (well within limits)
- **Use Case**: High-level monitoring

---

## Implementation Recommendations

### Phase 1: Start Free (Month 1)
1. Enable cloud provider carbon reporting (FREE)
2. Use WattTime free tier for North America (FREE)
3. Use free regional APIs (IESO, CAISO, UK) (FREE)
4. **Total Cost**: $0/month
5. **Coverage**: North America + limited regions

### Phase 2: Expand Coverage (Month 2+)
1. Keep cloud provider data (FREE)
2. Add Electricity Maps Starter ($99/mo)
3. Daily batch updates
4. **Total Cost**: $99/month
5. **Coverage**: Global (200+ zones)

### Phase 3: Production Scale (Month 6+)
1. Keep cloud provider data (FREE)
2. Upgrade to Electricity Maps Professional ($299/mo)
3. Hourly updates
4. **Total Cost**: $299/month
5. **Coverage**: Comprehensive global real-time

---

## Cost Optimization Tips

1. **Cache aggressively**: Store historical data locally to avoid repeated API calls
2. **Batch requests**: Fetch multiple zones in single API call where supported
3. **Smart polling**: Only poll zones you actively monitor
4. **Use free sources first**: Leverage IESO, CAISO, UK APIs before paid sources
5. **Monitor usage**: Track API call volumes to avoid overages
6. **Start small**: Begin with 20-50 key zones, expand as needed

---

## Decision Matrix

| Budget | Update Frequency | Coverage | Recommended Setup |
|--------|-----------------|----------|-------------------|
| $0/mo | Monthly | North America | Cloud APIs (FREE) + WattTime (FREE) |
| $99/mo | Daily | Global | Cloud APIs + Electricity Maps Starter |
| $299/mo | Hourly | Global | Cloud APIs + Electricity Maps Professional |
| Custom | Real-time | Global | Cloud APIs + Electricity Maps Enterprise |

---

## Next Steps

1. **Decide on budget**: How much are you willing to spend monthly?
2. **Choose coverage**: Which regions are most important?
3. **Set update frequency**: How fresh does the data need to be?
4. **Configure pipelines**: Set up credentials and run initial load
5. **Monitor costs**: Track API usage and adjust as needed

**Questions to answer**:
- What's your monthly budget for data sources?
- Do you need global coverage or specific regions?
- Is daily/weekly data sufficient, or do you need real-time?
