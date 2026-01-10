# Setup Guide - Middelbare School Research Tool

## Installation

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd /Users/adam/Code/misc/middelbare

# Install required packages
pip3 install -r requirements.txt
```

### 2. Set Up Google Maps API (Required for accurate commute calculations)

#### Get API Key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Geocoding API
   - Distance Matrix API
   - Directions API
4. Create credentials → API Key
5. (Optional) Restrict API key to these APIs for security

#### Configure API Key:

**Option 1: .env File (Recommended)**
```bash
# Create .env file in project root (already exists if you added it)
# Add your API key:
echo "GOOGLE_MAPS_API_KEY=your-api-key-here" > .env

# Or edit .env file directly and add:
GOOGLE_MAPS_API_KEY=your-api-key-here
```

**Option 2: Environment Variable**
```bash
# Add to your ~/.zshrc or ~/.bash_profile
export GOOGLE_MAPS_API_KEY='your-api-key-here'

# Or set for current session only:
export GOOGLE_MAPS_API_KEY='your-api-key-here'
```

**Note**: The `.env` file is already in `.gitignore` so your API key won't be committed to git.

### 3. Verify Installation

```bash
# Test that dependencies are installed
python3 -c "import googlemaps, bs4, requests; print('✓ All dependencies installed')"

# Check API key (loads from .env)
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ API key set' if os.getenv('GOOGLE_MAPS_API_KEY') else '✗ API key not set')"
```

## Usage

### Quick Start: Enrich All Data

Run the master enrichment script to update all school data:

```bash
python3 scripts/enrich_all_data.py
```

This will:
1. ✅ Geocode all school addresses
2. ✅ Calculate accurate bike routes and times
3. ✅ Calculate public transport routes and times
4. ✅ Scrape additional data from Schoolwijzer
5. ✅ Add reviews from Onderwijsconsument
6. ✅ Get open days from Schoolkeuze 020
7. ✅ Reconsolidate all data

### Individual Scripts

#### Calculate Commutes with Google Maps:
```bash
python3 scripts/calculate_commutes_gmaps.py
```

#### Scrape Specific Sources:
```bash
# Schoolwijzer Amsterdam (official data)
python3 scripts/scrapers/schoolwijzer_scraper.py

# Onderwijsconsument (reviews & ratings)
python3 scripts/scrapers/onderwijsconsument_scraper.py

# Schoolkeuze 020 (open days)
python3 scripts/scrapers/schoolkeuze020_scraper.py
```

#### Consolidate Data:
```bash
python3 scripts/consolidate_schools.py
```

## Data Structure

### Input Data:
```
data/
├── schools/
│   ├── amsterdam/     # 43 individual JSON files
│   └── amstelveen/    # 2 individual JSON files
└── schools-list.json  # Master tracking list
```

### Output Data:
```
data/
├── schools-consolidated.json     # All schools merged
└── scraped_*.json                # Raw scraped data (backup)
```

## Google Maps API Costs

### Free Tier (as of 2026):
- **Geocoding API**: Free up to 40,000 requests/month ($5.00 per 1000 after)
- **Distance Matrix API**: Free up to 40,000 elements/month ($5.00 per 1000 after)
- **Directions API**: Free up to 40,000 requests/month ($5.00 per 1000 after)

### Estimated Usage:
- 45 schools × 1 geocode request = 45 requests
- 45 schools × 2 route requests (bike + transit) = 90 requests
- **Total: ~135 requests** (well within free tier)

### Monthly Credit:
Google provides $200/month free credit, which covers:
- ~40,000 geocoding requests
- ~40,000 directions requests

**Conclusion**: This project will **not incur charges** under normal usage.

## Troubleshooting

### "Module not found" errors:
```bash
pip3 install -r requirements.txt
```

### "API key not set" error:
```bash
export GOOGLE_MAPS_API_KEY='your-key-here'
# Or add to ~/.zshrc and restart terminal
```

### "Rate limit exceeded" error:
- The scripts include rate limiting (0.5-2 seconds between requests)
- If error persists, increase sleep times in scripts
- Free tier limits should not be hit for this dataset

### SSL/Certificate errors:
```bash
# On macOS, install certificates:
/Applications/Python\ 3.*/Install\ Certificates.command
```

### Permission denied:
```bash
chmod +x scripts/*.py scripts/scrapers/*.py
```

## Next Steps

### After Data Enrichment:

1. **Review consolidated data**:
   ```bash
   cat data/schools-consolidated.json | python3 -m json.tool | less
   ```

2. **Check data completeness**:
   ```bash
   python3 -c "import json; data=json.load(open('data/schools-consolidated.json')); print(f\"Average completeness: {data['metadata']['statistics']['avg_completeness']*100:.1f}%\")"
   ```

3. **Proceed to Part 2**: Implement scoring system
   - See `part2-scoring-plan.md` for details

4. **Proceed to Part 3**: Build interactive tool
   - See `part3-interactive-tool-plan.md` for details

## Maintenance

### Updating School Data:

School information changes over time. To keep data current:

1. **Re-run enrichment script** (recommended: monthly):
   ```bash
   python3 scripts/enrich_all_data.py
   ```

2. **Update open days** (before enrollment period):
   ```bash
   python3 scripts/scrapers/schoolkeuze020_scraper.py
   ```

3. **Refresh reviews** (quarterly):
   ```bash
   python3 scripts/scrapers/onderwijsconsument_scraper.py
   ```

### Adding New Schools:

1. Create new JSON file in `data/schools/amsterdam/` or `data/schools/amstelveen/`
2. Use existing file as template
3. Run enrichment script to populate details
4. Run consolidation script

## Support

### Common Issues:
- **Geocoding fails**: Verify address format is correct
- **No route found**: Check if address is valid and accessible
- **Scraper errors**: Websites may have changed structure; inspect HTML manually

### Getting Help:
- Check error messages carefully
- Review individual script comments
- Test with single school first before batch processing
- Verify API key permissions and quota

## Security

### Protecting Your API Key:
```bash
# NEVER commit API keys to git
echo "GOOGLE_MAPS_API_KEY=*" >> .gitignore

# Use environment variables only
# Consider using API key restrictions in Google Cloud Console
```

### Recommended API Key Restrictions:
- **API restrictions**: Limit to Geocoding, Distance Matrix, Directions APIs only
- **Application restrictions**: Restrict to your IP address for development
- **Usage quotas**: Set daily quotas to prevent unexpected charges

## Advanced Usage

### Filtering Schools:
```python
# Example: Get only VWO-only schools within 5km
import json

with open('data/schools-consolidated.json') as f:
    data = json.load(f)

vwo_only_nearby = [
    s for s in data['schools']
    if s['basic_info']['type'] == ['VWO'] and
    s['location']['bike_accessibility'].get('distance_km', 99) < 5
]

print(f"Found {len(vwo_only_nearby)} VWO-only schools within 5km")
```

### Custom Scraping:
- Modify scraper scripts in `scripts/scrapers/`
- Add new data sources following existing patterns
- Update schema in individual school JSON files as needed

## Credits

Data sources:
- Google Maps (routing & geocoding)
- Schoolwijzer Amsterdam (official municipal data)
- Onderwijsconsument (consumer reviews)
- Schoolkeuze 020 (Amsterdam school choice portal)
- Individual school websites
