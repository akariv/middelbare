# Amsterdam/Amstelveen School Selection Tool

An interactive tool to help select the best secondary school (middelbare school) in Amsterdam and Amstelveen based on comprehensive data and personalized criteria.

## Features

- **📊 Interactive Rankings**: View schools ranked by customizable scoring criteria
- **⚖️ School Comparison**: Side-by-side comparison of multiple schools
- **⭐ Favorites Management**: Save and manage your shortlist
- **⚙️ Custom Weighting**: Adjust importance of different criteria
- **🔍 Smart Filtering**: Filter by city, school type, commute time, etc.

## Data Coverage

- **45 schools** across Amsterdam and Amstelveen
- **Official exam pass rates** from DUO (22 schools)
- **Parent satisfaction ratings** (37 schools)
- **Student satisfaction ratings** (38 schools)
- **Accurate commute times** (bike and public transit)
- **2026 open day events** (36 schools)
- **Comprehensive facility information**

## Scoring Criteria

The tool evaluates schools based on 8 key criteria:

1. **Academic Performance** (30% default) - Exam pass rates and trends
2. **Proximity** (20% default) - Bike and transit commute times
3. **Parent Satisfaction** (15% default) - Parent ratings and recommendations
4. **Student Satisfaction** (10% default) - Student feedback
5. **Facilities** (10% default) - Technology, sports, specialized rooms
6. **School Size** (5% default) - Enrollment size preference match
7. **Extracurriculars** (5% default) - Activities and programs
8. **Special Programs** (5% default) - Unique educational offerings

All weights can be customized to match your priorities.

## Installation

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Set up Google Maps API key (for commute calculations):
   - Create a `.env` file with: `GOOGLE_MAPS_API_KEY=your_key_here`
   - Enable: Geocoding API, Directions API, Distance Matrix API

## Usage

### Run the Interactive Web Application

```bash
streamlit run app.py
```

This will launch a web interface at `http://localhost:8501` with:
- Home dashboard with statistics
- School rankings with filtering
- Side-by-side school comparison
- Favorites management
- Custom weight adjustment

### Run Command-Line Scoring

```bash
python3 scoring.py
```

This displays the top 10 schools with detailed scores in the terminal.

## Project Structure

```
middelbare/
├── app.py                          # Streamlit web application
├── scoring.py                      # Scoring system and algorithms
├── data/
│   └── schools/
│       ├── amsterdam/              # 38 Amsterdam schools (JSON)
│       └── amstelveen/             # 7 Amstelveen schools (JSON)
├── scripts/
│   ├── calculate_commutes_gmaps.py # Google Maps integration
│   ├── enrich_*.py                 # Data enrichment scripts
│   └── scrape_*.py                 # Web scraping scripts
└── requirements.txt                # Python dependencies
```

## Data Sources

- **DUO (Dienst Uitvoering Onderwijs)**: Official exam results
- **onderwijsconsument.nl**: Enrollment, ratings, facility data
- **schoolkeuze020.nl**: 2026 open day events
- **Google Maps API**: Accurate commute times and routing
- **School websites**: Contact info, programs, facilities

## Customization Examples

### Prioritize Academic Performance

In the web app, go to "Customize Weights" and set:
- Academic Performance: 50%
- Parent Satisfaction: 20%
- Proximity: 15%
- Other criteria: 15% combined

### Prioritize Proximity

- Proximity: 40%
- Academic Performance: 30%
- Facilities: 15%
- Other criteria: 15% combined

### Find Small Schools

- Set "Preferred School Size" to "small"
- Filter by "Max Bike Commute" for nearby options

## Key Insights

**Top Schools by Academic Performance:**
- Ignatiusgymnasium: 96.1% pass rate (5-year avg: 95.7%)
- Amstelveen College: 89.6% pass rate (5-year avg: 87.2%)
- Barlaeus Gymnasium: 93.1% pass rate (5-year avg: 93.4%)

**Closest Schools (from home address):**
- Amstelveen College: 10 mins bike
- Cheider: 11 mins bike
- Joodse Scholengemeenschap Maimonides: 12 mins bike

**Highest Parent Satisfaction:**
- Barlaeus Gymnasium: 8.8/10
- Spinoza Lyceum: 8.6/10
- Metis Montessori Lyceum: 8.6/10

## Development

### Add More Schools

1. Create JSON file in `data/schools/[city]/[school-slug].json`
2. Follow the schema used by existing schools
3. Run enrichment scripts to add additional data

### Update Commute Times

```bash
python3 scripts/calculate_commutes_gmaps.py
```

### Refresh Exam Data

```bash
python3 scripts/enrich_exam_results.py
```

### Update Enrollment & Ratings

```bash
python3 scripts/enrich_enrollment_and_ratings.py
```

### Update Open Days

```bash
python3 scripts/scrape_open_dagen_2026.py
```

## License

This is a personal project for school selection. Data is aggregated from public sources for educational purposes.

## Credits

Data collection and enrichment completed: 2026-01-09
