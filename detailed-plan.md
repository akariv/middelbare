# Detailed Implementation Plan: Middelbare School Research Tool

## Overview
Build a comprehensive tool to support secondary school selection for students transitioning from primary school in Amsterdam and Amstelveen area, with a focus on VWO (pre-university) schools.

**Student Home Address**: Judith Leijsterweg 30, Amstelveen

---

## Part 1: Data Collection, Analysis, and Enrichment

### Phase 1.1: School Discovery and Initial Data Collection

**Approach:**
1. **Identify all VWO schools** in Amsterdam and Amstelveen using:
   - https://schoolkeuze020.nl/ (Amsterdam schools)
   - https://schoolwijzer.amsterdam.nl/nl/vo (Amsterdam municipal guide)
   - https://onderwijsconsument.nl/ (Consumer organization data)
   - https://www.oudersteunpunt.nl/ (Parent support organization)
   - Additional sources for Amstelveen schools

2. **Data Sources Strategy:**
   - **Primary sources**: Official school websites, DUO (government education database)
   - **Secondary sources**: Review sites, parent forums, news articles
   - **API/Structured data**: Check for available APIs or structured data exports
   - **Web scraping**: When necessary, respect robots.txt and rate limits

### Phase 1.2: Data Structure Design

**File Organization:**
```
data/
├── schools/
│   ├── amsterdam/
│   │   ├── school-name-1.json
│   │   ├── school-name-2.json
│   │   └── ...
│   └── amstelveen/
│       ├── school-name-1.json
│       └── ...
├── schools-consolidated.json
└── metadata.json
```

**Individual School Data Schema:**
```json
{
  "id": "unique-school-identifier",
  "basic_info": {
    "name": "",
    "official_name": "",
    "address": "",
    "city": "",
    "postal_code": "",
    "contact": {
      "phone": "",
      "email": "",
      "website": ""
    },
    "type": ["VWO", "HAVO", "VMBO"],
    "religious_affiliation": "",
    "enrollment": {
      "total": 0,
      "by_program": {}
    },
    "hours": {
      "school_days": "",
      "school_hours": ""
    }
  },
  "academic_performance": {
    "exam_scores": {},
    "graduation_rates": {},
    "student_teacher_ratio": 0,
    "special_programs": [],
    "extracurricular_activities": []
  },
  "facilities": {
    "classrooms_labs_quality": "",
    "sports_facilities": [],
    "library": {},
    "technology": {}
  },
  "student_support": {
    "counseling": "",
    "newcomers_class": false,
    "language_support": [],
    "special_education": [],
    "after_school_programs": []
  },
  "environment": {
    "safety_measures": [],
    "diversity": {},
    "parent_involvement": "",
    "culture_values": ""
  },
  "location": {
    "coordinates": {"lat": 0, "lon": 0},
    "public_transport": {
      "nearest_stops": [],
      "commute_from_home": {
        "duration_minutes": 0,
        "transfers": 0,
        "routes": []
      }
    },
    "bike_accessibility": {
      "distance_km": 0,
      "duration_minutes": 0,
      "route_quality": ""
    },
    "accessibility_disabilities": ""
  },
  "reviews_reputation": {
    "parent_reviews": [],
    "student_reviews": [],
    "awards": [],
    "alumni_stories": []
  },
  "practical_info": {
    "open_days": [],
    "information_sessions": [],
    "application_deadlines": [],
    "links": []
  },
  "ai_analysis": {
    "strengths": [],
    "considerations": [],
    "best_fit_for": [],
    "summary": ""
  },
  "metadata": {
    "last_updated": "",
    "data_sources": [],
    "completeness_score": 0
  }
}
```

### Phase 1.3: Data Collection Process

**For Each School:**
1. **Scrape/fetch basic information** from primary sources
2. **Calculate commute times** using:
   - Google Maps API / OpenStreetMap for routes
   - 9292.nl API for public transport
   - Cycling route APIs
3. **Gather reviews** from multiple sources
4. **Cross-reference data** between sources for accuracy
5. **AI-powered enrichment**:
   - Analyze collected text data
   - Generate summaries and insights
   - Identify strengths and considerations
   - Match school characteristics to student needs

### Phase 1.4: Data Consolidation

Create `schools-consolidated.json` with:
- Array of all schools
- Summary statistics
- Data quality metrics
- Collection timestamp

---

## Part 2: Scoring System Design (To be detailed after Part 1)

**Initial Concept:**
- Define weighted criteria across 8 categories
- Normalize scores to 0-100 scale
- Allow customizable weights
- Include both objective (exam scores) and subjective (reviews) measures

**Preliminary Criteria Categories:**
1. Academic Performance (default weight: 25%)
2. Location & Accessibility (default weight: 15%)
3. Facilities (default weight: 10%)
4. Student Support (default weight: 15%)
5. School Environment (default weight: 15%)
6. Reviews & Reputation (default weight: 10%)
7. Extracurricular Opportunities (default weight: 5%)
8. Practical Considerations (default weight: 5%)

---

## Part 3: Interactive Visualization Tool (To be detailed after Part 1)

**Initial Concept:**
- Web-based interface (React/Vue/Svelte)
- Interactive table with sorting/filtering
- Weight adjustment sliders
- Real-time score recalculation
- School comparison view
- Map visualization with commute routes

**Features:**
- Export comparison results
- Save weight preferences
- Print-friendly reports
- Mobile-responsive design

---

## Technical Stack (Proposed)

**Data Collection:**
- Python for web scraping (BeautifulSoup, Scrapy)
- API clients for structured data sources
- Claude API for AI analysis and enrichment

**Data Processing:**
- Python (pandas) for data cleaning and consolidation
- JSON for data storage (easy to read, version control friendly)

**Frontend (Part 3):**
- Modern web framework (React/Vue/Svelte)
- Visualization library (D3.js, Chart.js, or Plotly)
- Map integration (Leaflet or Google Maps)

---

## Success Criteria

**Part 1 Complete When:**
- ✅ All VWO schools in Amsterdam and Amstelveen identified
- ✅ Individual JSON files created for each school
- ✅ At least 70% of data fields populated per school
- ✅ Consolidated JSON file created
- ✅ Commute calculations completed for all schools
- ✅ AI analysis generated for each school

**Part 2 Complete When:**
- Scoring algorithm designed and documented
- Default weights established
- Score calculation tested and validated

**Part 3 Complete When:**
- Interactive tool functional
- All features implemented
- User testing completed
- Documentation provided

---

## Next Steps

1. **Start Part 1**: Begin with school discovery from the listed websites
2. **Create data/ directory structure**
3. **Collect data for first 3-5 schools** to validate schema
4. **Iterate on schema** based on actual data availability
5. **Scale to all schools**
6. **Review Part 1 results** before proceeding to Parts 2 & 3
