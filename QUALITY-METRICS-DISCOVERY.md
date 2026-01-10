# Quality Metrics Discovery - Comprehensive Report

**Date:** 2026-01-09
**Status:** ✅ MAJOR DISCOVERY

## Executive Summary

Following your suggestion to check individual school API endpoints, we discovered **multiple high-value data sources** containing quality metrics that were not available in the initial onderwijsconsument.nl bulk API. These metrics are essential for data-driven school selection.

## Data Sources Discovered

### 1. DUO (Dienst Uitvoering Onderwijs) - Official Government Exam Results ⭐⭐⭐

**Source:** https://duo.nl/open_onderwijsdata/voortgezet-onderwijs/examens/examens-vmbo-havo-vwo.jsp

**Data Available:**
- ✅ **Pass rates (Slagingspercentages)** by education level (VMBO, HAVO, VWO)
- ✅ **Number of exam candidates** per year
- ✅ **Number of students who passed**
- ✅ **5 years of historical data** (2020-2025)
- ✅ **Gender breakdowns** (male/female/total)
- ✅ **Specific study profiles** (N&T, N&G, E&M, C&M)

**Integration Status:** ✅ **INTEGRATED**
- 22 out of 45 schools enriched with exam data
- Data stored in `academic_performance.exam_scores` field

**Sample Data:**

#### Amstelveen College
- VMBO: **96.4%** pass rate (82 candidates), 5-year avg: 91.4%
- HAVO: **80.1%** pass rate (130 candidates), 5-year avg: 81.1%
- VWO: **95.6%** pass rate (90 candidates), 5-year avg: 89.0%

#### Cygnus Gymnasium
- VMBO: **89.8%** pass rate (146 candidates), 5-year avg: 94.8%
- HAVO: **85.8%** pass rate (127 candidates), 5-year avg: 88.4%
- VWO: **87.9%** pass rate (173 candidates), 5-year avg: 92.5%

#### Barlaeus Gymnasium
- VWO: **92.1%** pass rate (114 candidates), 5-year avg: 93.4%

#### Hervormd Lyceum West
- VMBO: **91.0%** pass rate (61 candidates)
- HAVO: **92.3%** pass rate (39 candidates)
- VWO: **100.0%** pass rate (14 candidates) 🌟

### 2. onderwijsconsument.nl API - jaren/vo Endpoint ⭐⭐

**Endpoint:** `https://www.onderwijsconsument.nl/api/jaren/vo`

**Data Available:**
- ✅ **Student ratings (leerlingoordeel)** - Overall satisfaction + "voice matters" sub-score
- ✅ **Parent ratings (ouderoordeel)** - Overall satisfaction + "would recommend" sub-score
- ✅ **School climate (schoolklimaat)** scores
- ✅ **Inspection ratings (inspectieoordeel)**
- ✅ **Historical enrollment numbers (leerlingaantal)**
- ✅ **Annual costs (kosten)**
- ✅ **Historical pass rates (slagingspercentage)** - text format

**Records Found:** 1,265 total records
**Recent Ratings:** 77 schools with 2021-2024 student/parent ratings

**Integration Status:** 🔄 **DISCOVERED - NOT YET INTEGRATED**

**Sample Data:**

#### Joodse Scholengemeenschap Maimonides (2021-2022)
- Student rating: **6.6** (voice matters: 5.1)
- Parent rating: **8.3** (would recommend: 9.3)

#### Sample School (2021-2022)
- Student rating: **7.0** (voice matters: 7.3)
- Parent rating: **8.3** (would recommend: 8.8)

### 3. onderwijsconsument.nl API - open_dagen Endpoint ⭐

**Endpoint:** `https://www.onderwijsconsument.nl/api/open_dagen`

**Data Available:**
- ✅ **Open house dates and times**
- ✅ **Event descriptions** (open avond, lesjesmiddag, etc.)
- ✅ **Special notes (bijzonderheden)**
- ✅ **Event URLs**

**Records Found:** 1,516 total records
**Date Range:** 2008-2021 (mostly historical)

**Integration Status:** 🔄 **DISCOVERED - NOT YET INTEGRATED**

**Sample Data (Maimonides):**
- 2021-02-09: Digital open evening 19:00-21:00
- 2021-02-12: Trial lesson afternoon 13:00-15:00
- 2020-02-04: Open evening for new students and parents
- 2020-02-14: Trial lesson afternoon for new bridge class

## Quality Metrics Summary

### Now Available for School Comparison

| Metric | Source | Coverage | Data Quality |
|--------|--------|----------|--------------|
| **Exam Pass Rates** | DUO | 22/45 schools | ⭐⭐⭐⭐⭐ Official |
| **Pass Rate Trends** | DUO | 22/45 schools | ⭐⭐⭐⭐⭐ 5-year history |
| **Student Ratings** | OCO jaren/vo | 77 schools | ⭐⭐⭐⭐ Survey-based |
| **Parent Ratings** | OCO jaren/vo | 77 schools | ⭐⭐⭐⭐ Survey-based |
| **School Climate** | OCO jaren/vo | Limited | ⭐⭐⭐ Text-based |
| **Inspection Ratings** | OCO jaren/vo | Historical | ⭐⭐⭐ Text-based |
| **Enrollment Numbers** | OCO jaren/vo | Extensive | ⭐⭐⭐⭐ Annual data |
| **Annual Costs** | OCO jaren/vo | Partial | ⭐⭐⭐ Self-reported |
| **Open Days** | OCO open_dagen | Historical | ⭐⭐ 2008-2021 only |

## Data Insights

### Pass Rate Analysis (from DUO data)

**Highest Pass Rates (VWO 2024-2025):**
1. Hervormd Lyceum West: **100.0%** (14 candidates)
2. Amstelveen College: **95.6%** (90 candidates)
3. Het Amsterdams Lyceum: **95.3%** (85 candidates)
4. Vossius Gymnasium: **92.8%** (125 candidates)
5. Barlaeus Gymnasium: **92.1%** (114 candidates)

**Significant Sample Sizes (VWO 2024-2025):**
- Cygnus Gymnasium: 173 candidates, 87.9% pass rate
- Vossius Gymnasium: 125 candidates, 92.8% pass rate
- Het 4e Gymnasium: 116 candidates, 88.8% pass rate

**Performance Variations:**
- Some schools show consistent high performance across VMBO, HAVO, and VWO
- Others show variation between education levels
- Smaller schools sometimes show 100% pass rates but with fewer candidates

### Student/Parent Satisfaction Patterns

**Typical Rating Ranges:**
- Student Overall: **6.2 - 7.1** (out of 10)
- Student "Voice Matters": **5.0 - 7.3**
- Parent Overall: **7.0 - 8.3**
- Parent "Would Recommend": **7.0 - 9.3**

**Observations:**
- Parents consistently rate schools higher than students
- "Would recommend" scores often exceed overall satisfaction
- Student ratings on "voice matters" tend to be lower than overall satisfaction

## Technical Implementation

### DUO Data Integration

**Script:** `scripts/enrich_exam_results.py`

**Process:**
1. Downloads Excel file from DUO (2.2 MB, 50+ columns)
2. Filters for Amsterdam/Amstelveen schools
3. Handles privacy-protected values ("<5" candidates)
4. Matches schools by BRIN code
5. Calculates 5-year averages
6. Adds to `academic_performance.exam_scores`

**Data Format Added to JSON:**
```json
{
  "academic_performance": {
    "exam_scores": {
      "vmbo": {
        "pass_rate_2024_2025": 96.4,
        "candidates_2024_2025": 82,
        "passed_2024_2025": 79,
        "average_pass_rate_5yr": 91.4
      },
      "havo": {
        "pass_rate_2024_2025": 80.1,
        "candidates_2024_2025": 130,
        "passed_2024_2025": 104,
        "average_pass_rate_5yr": 81.1
      },
      "vwo": {
        "pass_rate_2024_2025": 95.6,
        "candidates_2024_2025": 90,
        "passed_2024_2025": 86,
        "average_pass_rate_5yr": 89.0
      }
    }
  }
}
```

### Potential Future Integration

**jaren/vo Student/Parent Ratings:**
```json
{
  "reviews_reputation": {
    "student_satisfaction": {
      "overall_rating": 6.6,
      "voice_matters_rating": 5.1,
      "year": "2021-2022"
    },
    "parent_satisfaction": {
      "overall_rating": 8.3,
      "would_recommend_rating": 9.3,
      "year": "2021-2022"
    }
  }
}
```

**open_dagen Event Information:**
```json
{
  "practical_info": {
    "open_days": [
      {
        "date": "2021-02-09",
        "time": "19:00-21:00",
        "type": "digitale open avond",
        "url": "https://www.jsgmaimonides.nl/"
      }
    ]
  }
}
```

## Impact on School Selection

### Decision-Making Value

**High-Value Metrics (Must-Have):**
1. ✅ **Exam Pass Rates** - Objective academic performance indicator
2. ✅ **Pass Rate Trends** - Shows consistency and improvement over time
3. ✅ **Number of Candidates** - Indicates statistical reliability
4. 🔄 **Student Satisfaction** - Direct user experience feedback
5. 🔄 **Parent Satisfaction** - Parent perspective and recommendation

**Medium-Value Metrics (Nice-to-Have):**
- Historical enrollment trends
- Annual costs (when available)
- School climate assessments
- Open house schedules (for current year)

**Low-Value (Historical Interest):**
- Historical open days from 2008-2021
- Old inspection ratings (pre-2020)

### Scoring System Integration

These quality metrics can now be weighted in Part 2 (Scoring System):

**Suggested Weighting:**
1. **Academic Performance (30%)**: Pass rates, trends, exam results
2. **Proximity (20%)**: Bike/transit commute times
3. **Student/Parent Satisfaction (15%)**: Rating scores
4. **Facilities & Support (15%)**: Technology, special education
5. **Programs & Activities (10%)**: Special programs, extracurriculars
6. **Environment (5%)**: Safety, culture, values
7. **Practical Factors (5%)**: Open days, costs, accessibility

## Statistics

### Current Data Completeness

**Before Quality Metrics:**
- Average completeness: 46%
- No objective performance data
- Subjective assessments only

**After Quality Metrics:**
- Average completeness: **52%** (+6%)
- 22 schools: Objective exam performance data (official government source)
- 77 schools: Potential student/parent satisfaction data (if integrated)
- Comprehensive basis for data-driven comparison

### Schools with Exam Data (22)

✅ With DUO Exam Results:
1. Amstelveen College
2. Barlaeus Gymnasium
3. Calandlyceum
4. Cheider
5. Cornelius Haga Lyceum
6. Cygnus Gymnasium
7. Fons Vitae Lyceum
8. Hervormd Lyceum West
9. Het 4e Gymnasium
10. Het Amsterdams Lyceum
11. Hyperion Lyceum
12. Ignatiusgymnasium
13. Ir. Lely Lyceum
14. Lumion
15. Metis Montessori Lyceum
16. Montessori Lyceum Oostpoort
17. Montessori Lyceum Terra Nova
18. St. Nicolaaslyceum
19. Vinse School
20. Vossius Gymnasium
21. Vox College
22. Spinoza20first

⚠️ Not Found in DUO (23 schools):
- Likely due to name variations or recent establishment
- Could be matched manually with BRIN codes

## Recommendations

### Immediate Next Steps

1. **✅ DONE**: Integrate DUO exam pass rates (22 schools)
2. **RECOMMENDED**: Integrate jaren/vo student/parent ratings (potential 77+ schools)
3. **OPTIONAL**: Add historical open dagen data where useful
4. **FUTURE**: Manual BRIN code matching for 23 unmatched schools

### For Part 2 (Scoring System)

- Use pass rates as primary academic quality metric
- Weight 5-year average for stability assessment
- Consider sample size when evaluating reliability
- Integrate student/parent satisfaction as supplementary metric
- Use trends to identify improving/declining schools

### For Part 3 (Interactive Tool)

**Display Features:**
- Pass rate badges/indicators on school cards
- Trend graphs (5-year history)
- Student vs. parent rating comparison
- "Reliability" indicator based on sample size
- Color-coded performance tiers

## Files Created/Modified

### Scripts
- ✅ `scripts/enrich_exam_results.py` - DUO exam data integration

### Documentation
- ✅ `QUALITY-METRICS-DISCOVERY.md` - This comprehensive report
- ✅ `API-ENRICHMENT-SUMMARY.md` - Previous API enrichment summary
- ✅ `DATA-ACCURACY-FIX-SUMMARY.md` - Address correction summary

### Data Files
- ✅ 22 school JSON files updated with exam_scores
- ✅ `/tmp/duo_exams_2020-2025.xlsx` - Downloaded DUO data (2.2 MB)

## Conclusion

Your suggestion to check individual school API endpoints led to the discovery of **invaluable official government exam data** and **user satisfaction ratings**. The DUO exam results provide objective, reliable quality metrics that are essential for school comparison and ranking.

**Key Achievement:**
- Transformed the dataset from subjective descriptions to **objective, quantifiable performance metrics**
- Added **5 years of historical pass rate data** for trend analysis
- Discovered **student and parent satisfaction scores** for 77+ schools
- Created foundation for **data-driven school selection**

The school database now contains:
1. ✅ Complete accurate addresses and coordinates
2. ✅ Precise commute times (bike and transit)
3. ✅ Comprehensive facility and program information
4. ✅ **Official government exam performance data**
5. 🔄 Student/parent satisfaction metrics (discoverable)

**Ready for Part 2 & 3!** 🚀
