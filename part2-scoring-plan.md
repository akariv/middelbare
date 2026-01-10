# Part 2: Scoring System Design

## Overview
Design and implement a weighted scoring system to evaluate and rank schools based on multiple criteria, with customizable weights to match family priorities.

## Scoring Criteria and Default Weights

### 1. Academic Performance (25%)
**Metrics:**
- Exam scores (standardized to 0-100 scale)
- Graduation rates (if available)
- Student-teacher ratio (lower is better, normalized)
- Special programs availability (count and quality)

**Scoring approach:**
- If exam scores available: 40% of category score
- If graduation rates available: 30% of category score
- Student-teacher ratio: 20% of category score
- Special programs: 10% of category score (0.5 points per program, capped at 10)

### 2. Location & Accessibility (15%)
**Metrics:**
- Bike distance from home (Judith Leijsterweg 30)
- Bike commute time
- Public transport connections
- Route quality

**Scoring approach:**
- Distance scoring (inverse):
  - 0-2km: 100 points
  - 2-5km: 90 points
  - 5-8km: 75 points
  - 8-10km: 60 points
  - 10-15km: 40 points
  - 15km+: 20 points
- Public transport bonus: +10 points if well-connected (multiple lines)
- Route quality bonus: +5 points for safe/easy routes

### 3. Facilities (10%)
**Metrics:**
- Building quality/age
- Sports facilities
- Library resources
- Technology availability
- Lab quality

**Scoring approach:**
- Text analysis of facilities descriptions
- Count of specific amenities (sports, labs, tech)
- Modern building bonus (new or renovated post-2015): +20 points
- Each major facility type: +15 points (max 100)

### 4. Student Support (15%)
**Metrics:**
- Counseling services
- Language support programs
- Special education availability
- After-school programs
- Newcomers class

**Scoring approach:**
- Counseling available: 30 points
- Language support: 20 points
- Special education: 20 points
- After-school programs: 15 points per program type (max 30)
- Each additional support feature: +10 points

### 5. School Environment (15%)
**Metrics:**
- Safety measures
- Diversity
- Parent involvement
- School culture/values quality
- School size (enrollment)

**Scoring approach:**
- Safety measures: 10 points per measure (max 30)
- Positive culture indicators from text analysis: up to 40 points
- Parent involvement: 20 points if active
- School size preference (medium size optimal):
  - 500-1000 students: 100 points
  - 300-500 or 1000-1500: 80 points
  - <300 or 1500-2000: 60 points
  - >2000: 40 points

### 6. Reviews & Reputation (10%)
**Metrics:**
- Parent reviews count and sentiment
- Student reviews sentiment
- Awards and recognitions
- Alumni success stories

**Scoring approach:**
- Awards: 20 points each (max 60)
- Positive review sentiment: up to 40 points
- Reputation indicators from AI analysis: up to 40 points

### 7. Extracurricular Opportunities (5%)
**Metrics:**
- Number and variety of activities
- Sports programs
- Arts programs
- Clubs and organizations

**Scoring approach:**
- Each activity type: 15 points (max 100)
- Variety bonus: +20 points if 4+ different categories

### 8. Practical Considerations (5%)
**Metrics:**
- Open days scheduled
- Application process clarity
- Website quality/information availability
- Data completeness

**Scoring approach:**
- Open days scheduled: 30 points
- Good website/info: 30 points
- Application info clear: 20 points
- High data completeness (>70%): 20 points

## Score Calculation Algorithm

### Step 1: Calculate Raw Scores (0-100 for each criterion)
```python
def calculate_criterion_score(school, criterion):
    # Apply criterion-specific scoring logic
    # Return score 0-100
    pass
```

### Step 2: Apply Weights
```python
def calculate_weighted_score(school, weights):
    total_score = 0
    for criterion, weight in weights.items():
        raw_score = calculate_criterion_score(school, criterion)
        weighted_score = raw_score * weight
        total_score += weighted_score
    return total_score  # 0-100 scale
```

### Step 3: Handle Missing Data
- If criterion data is completely missing: Use 50 points (neutral)
- If partially missing: Calculate based on available sub-metrics
- Track data completeness for transparency

### Step 4: Generate Rankings
```python
def rank_schools(schools, weights):
    scored_schools = []
    for school in schools:
        score = calculate_weighted_score(school, weights)
        scored_schools.append({
            'school': school,
            'total_score': score,
            'criterion_scores': {...}  # breakdown
        })
    return sorted(scored_schools, key=lambda x: x['total_score'], reverse=True)
```

## Implementation Plan

### Phase 1: Core Scoring Engine
**File:** `scripts/scoring_engine.py`

```python
class SchoolScorer:
    def __init__(self, weights=None):
        self.weights = weights or self.get_default_weights()

    def get_default_weights(self):
        return {
            'academic_performance': 0.25,
            'location_accessibility': 0.15,
            'facilities': 0.10,
            'student_support': 0.15,
            'school_environment': 0.15,
            'reviews_reputation': 0.10,
            'extracurricular': 0.05,
            'practical': 0.05
        }

    def score_school(self, school):
        # Calculate scores for each criterion
        # Return dict with total and breakdown
        pass

    def score_all_schools(self, schools):
        # Score all schools and rank them
        pass

    def get_top_schools(self, schools, n=10):
        # Return top N schools
        pass
```

### Phase 2: Criterion Scorers
**Files:** `scripts/scorers/` directory with individual criterion scorers

Each scorer implements:
```python
class CriterionScorer:
    def calculate(self, school_data):
        # Return score 0-100
        pass

    def explain(self, school_data):
        # Return explanation of score
        pass
```

### Phase 3: Data Enrichment
**File:** `scripts/enrich_scores.py`

```python
def enrich_school_with_scores(school, weights):
    scorer = SchoolScorer(weights)
    scores = scorer.score_school(school)
    school['scores'] = scores
    return school

def enrich_all_schools():
    # Read consolidated file
    # Add scores to each school
    # Save enriched version
    pass
```

### Phase 4: Export Scored Data
**File:** `data/schools-scored.json`

Structure:
```json
{
  "metadata": {
    "generated_at": "...",
    "weights_used": {...},
    "total_schools": 45
  },
  "schools": [
    {
      ...school data...,
      "scores": {
        "total": 78.5,
        "rank": 3,
        "breakdown": {
          "academic_performance": 85.0,
          "location_accessibility": 92.0,
          ...
        },
        "explanations": {
          "academic_performance": "Strong special programs...",
          ...
        }
      }
    }
  ]
}
```

## Testing and Validation

### Test Cases:
1. **School with complete data** - Should score based on actual metrics
2. **School with missing data** - Should use defaults appropriately
3. **Schools with same scores** - Should handle tie-breaking (alphabetical)
4. **Weight changes** - Should recalculate correctly
5. **Extreme values** - Should normalize properly

### Validation:
- Manual review of top 10 schools to ensure sensibility
- Check that weights sum to 1.0
- Verify all scores are 0-100
- Ensure rankings are deterministic

## Usage Example

```python
# Load data
with open('data/schools-consolidated.json') as f:
    data = json.load(f)

# Score with default weights
scorer = SchoolScorer()
ranked_schools = scorer.score_all_schools(data['schools'])

# Get top 10
top_10 = ranked_schools[:10]
for i, school in enumerate(top_10, 1):
    print(f"{i}. {school['basic_info']['name']} - {school['scores']['total']:.1f}")

# Score with custom weights (prioritize location)
custom_weights = {
    'academic_performance': 0.20,
    'location_accessibility': 0.30,  # Increased
    'facilities': 0.10,
    'student_support': 0.15,
    'school_environment': 0.10,
    'reviews_reputation': 0.05,
    'extracurricular': 0.05,
    'practical': 0.05
}
scorer_custom = SchoolScorer(custom_weights)
custom_ranked = scorer_custom.score_all_schools(data['schools'])
```

## Deliverables

1. **Scoring engine** (`scripts/scoring_engine.py`)
2. **Individual criterion scorers** (`scripts/scorers/*.py`)
3. **Enrichment script** (`scripts/enrich_scores.py`)
4. **Scored data file** (`data/schools-scored.json`)
5. **Documentation** (`docs/scoring-methodology.md`)
6. **Test suite** (`tests/test_scoring.py`)

## Next Steps After Part 2

Once scoring is complete:
- Validate top 10 results manually
- Document any adjustments to weights or algorithms
- Prepare data for Part 3 (interactive tool)
