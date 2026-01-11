"""
School Scoring System

Calculates quality scores and rankings for schools based on multiple criteria.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import statistics


class SchoolScorer:
    """Calculate scores for schools based on various metrics."""

    # Default weights for scoring (can be customized)
    DEFAULT_WEIGHTS = {
        'academic_performance': 30,
        'proximity': 20,
        'parent_satisfaction': 15,
        'student_satisfaction': 10,
        'facilities': 10,
        'school_size': 5,
        'extracurriculars': 5,
        'special_programs': 5
    }

    def __init__(self, data_dir: str = "data/schools"):
        self.data_dir = Path(data_dir)
        self.schools = []
        self.load_schools()

    def load_schools(self):
        """Load all school data from JSON files."""
        self.schools = []
        for city_dir in [self.data_dir / 'amsterdam', self.data_dir / 'amstelveen']:
            if city_dir.exists():
                for school_file in sorted(city_dir.glob('*.json')):
                    with open(school_file, 'r', encoding='utf-8') as f:
                        school = json.load(f)
                        self.schools.append(school)
        print(f"Loaded {len(self.schools)} schools")

    def calculate_academic_score(self, school: Dict) -> Dict[str, float]:
        """Calculate academic performance score (0-100)."""
        exam_scores = school.get('academic_performance', {}).get('exam_scores', {})

        if not exam_scores:
            return {'score': None, 'details': 'No exam data available'}

        # Extract pass rates with level tracking
        level_data = {}
        five_year_avgs = []
        candidate_counts = []

        # Weights for different education levels (VWO weighted highest)
        level_weights = {
            'vmbo': 0.7,   # Prevocational - lower weight
            'havo': 1.0,   # Senior general - standard weight
            'vwo': 1.5     # Pre-university - higher weight
        }

        for level in ['vmbo', 'havo', 'vwo']:
            if level in exam_scores:
                rate = exam_scores[level].get('pass_rate_2024_2025')
                avg_5yr = exam_scores[level].get('average_pass_rate_5yr')
                candidates = exam_scores[level].get('candidates_2024_2025')

                if rate:
                    level_data[level] = rate
                if avg_5yr:
                    five_year_avgs.append(avg_5yr)
                if candidates:
                    candidate_counts.append(candidates)

        if not level_data:
            return {'score': None, 'details': 'No pass rate data'}

        # Calculate weighted average based on education level
        if len(level_data) == 1:
            current_rate = list(level_data.values())[0]
        else:
            # Apply weights: VWO gets higher weight than HAVO/VMBO
            weighted_sum = sum(rate * level_weights[level] for level, rate in level_data.items())
            total_weight = sum(level_weights[level] for level in level_data.keys())
            current_rate = weighted_sum / total_weight

        # Factor in 5-year average for consistency
        if five_year_avgs:
            avg_rate = statistics.mean(five_year_avgs)
            # 70% current, 30% historical average
            final_rate = (current_rate * 0.7) + (avg_rate * 0.3)
        else:
            final_rate = current_rate

        # Bonus for large sample size (more reliable)
        total_candidates = sum(candidate_counts) if candidate_counts else 0
        reliability_bonus = min(total_candidates / 500 * 5, 5)  # Up to +5 points

        score = min(final_rate + reliability_bonus, 100)

        return {
            'score': round(score, 1),
            'details': f"{final_rate:.1f}% pass rate, {total_candidates} candidates"
        }

    def calculate_proximity_score(self, school: Dict) -> Dict[str, float]:
        """Calculate proximity score based on commute times (0-100)."""
        bike = school.get('location', {}).get('bike_accessibility', {})
        transit = school.get('location', {}).get('public_transport', {}).get('commute_from_home', {})

        bike_mins = bike.get('duration_minutes')
        transit_mins = transit.get('duration_minutes')

        if not bike_mins and not transit_mins:
            return {'score': None, 'details': 'No commute data'}

        # Use bike time primarily, transit as backup
        primary_mins = bike_mins if bike_mins else transit_mins

        # Score: 100 for 0 mins, decreasing linearly
        # 10 mins = 90, 20 mins = 80, 30 mins = 70, etc.
        if primary_mins <= 10:
            score = 100 - (primary_mins * 1)
        elif primary_mins <= 30:
            score = 90 - ((primary_mins - 10) * 2)
        else:
            score = max(50 - ((primary_mins - 30) * 1), 0)

        method = 'bike' if bike_mins else 'transit'
        return {
            'score': round(score, 1),
            'details': f"{primary_mins} mins by {method}"
        }

    def calculate_parent_satisfaction_score(self, school: Dict) -> Dict[str, float]:
        """Calculate parent satisfaction score (0-100)."""
        reviews = school.get('reviews_reputation', {}).get('parent_reviews', [])

        if not reviews:
            return {'score': None, 'details': 'No parent reviews'}

        # Get most recent review
        latest = reviews[0]
        rating = latest.get('overall_rating')

        if not rating:
            return {'score': None, 'details': 'No rating available'}

        # Convert 0-10 scale to 0-100
        score = rating * 10

        recommend = latest.get('would_recommend')
        recommend_text = f", {recommend:.1f}/10 recommend" if recommend else ""

        return {
            'score': round(score, 1),
            'details': f"{rating:.1f}/10 rating{recommend_text}"
        }

    def calculate_student_satisfaction_score(self, school: Dict) -> Dict[str, float]:
        """Calculate student satisfaction score (0-100)."""
        reviews = school.get('reviews_reputation', {}).get('student_reviews', [])

        if not reviews:
            return {'score': None, 'details': 'No student reviews'}

        # Get most recent review
        latest = reviews[0]
        rating = latest.get('overall_rating')

        if not rating:
            return {'score': None, 'details': 'No rating available'}

        # Convert 0-10 scale to 0-100
        score = rating * 10

        voice_matters = latest.get('voice_matters')
        voice_text = f", {voice_matters:.1f}/10 voice matters" if voice_matters else ""

        return {
            'score': round(score, 1),
            'details': f"{rating:.1f}/10 rating{voice_text}"
        }

    def calculate_facilities_score(self, school: Dict) -> Dict[str, float]:
        """Calculate facilities score based on available amenities (0-100)."""
        facilities = school.get('facilities', {})

        score = 50  # Base score

        # Technology
        if facilities.get('technology', {}).get('description'):
            score += 15

        # Sports facilities
        sports = facilities.get('sports_facilities', [])
        if sports and len(sports) > 0:
            score += 15

        # Classrooms/labs quality
        classrooms = facilities.get('classrooms_labs_quality', '')
        if classrooms and len(classrooms) > 50:
            score += 10

        # Library
        library = facilities.get('library', {})
        if library:
            score += 10

        details_parts = []
        if facilities.get('technology'):
            details_parts.append('technology')
        if sports:
            details_parts.append('sports')
        if classrooms:
            details_parts.append('specialized classrooms')

        details = ', '.join(details_parts) if details_parts else 'Basic facilities'

        return {
            'score': round(min(score, 100), 1),
            'details': details
        }

    def calculate_school_size_score(self, school: Dict, preferred_size: str = 'medium') -> Dict[str, float]:
        """Calculate school size score based on preference (0-100)."""
        enrollment = school.get('basic_info', {}).get('enrollment', {}).get('total')

        if not enrollment:
            return {'score': None, 'details': 'No enrollment data'}

        # Size categories
        # Small: < 500, Medium: 500-1000, Large: 1000-1500, Very Large: > 1500

        size_category = 'very_large' if enrollment > 1500 else \
                       'large' if enrollment > 1000 else \
                       'medium' if enrollment >= 500 else 'small'

        # Scoring based on preference
        preference_scores = {
            'small': {'small': 100, 'medium': 70, 'large': 50, 'very_large': 30},
            'medium': {'small': 70, 'medium': 100, 'large': 80, 'very_large': 60},
            'large': {'small': 50, 'medium': 80, 'large': 100, 'very_large': 90},
            'any': {'small': 80, 'medium': 80, 'large': 80, 'very_large': 80}
        }

        score = preference_scores.get(preferred_size, preference_scores['any']).get(size_category, 80)

        return {
            'score': score,
            'details': f"{enrollment} students ({size_category.replace('_', ' ')})"
        }

    def calculate_extracurriculars_score(self, school: Dict) -> Dict[str, float]:
        """Calculate extracurricular activities score (0-100)."""
        activities = school.get('academic_performance', {}).get('extracurricular_activities', [])
        after_school = school.get('student_support', {}).get('after_school_programs', [])

        total_activities = len(activities) + len(after_school)

        if total_activities == 0:
            return {'score': 50, 'details': 'No data on activities'}

        # Score based on number of activities
        # 0 = 50, 5 = 75, 10+ = 100
        score = min(50 + (total_activities * 5), 100)

        return {
            'score': score,
            'details': f"{total_activities} activities listed"
        }

    def calculate_special_programs_score(self, school: Dict) -> Dict[str, float]:
        """Calculate special programs score (0-100)."""
        programs = school.get('academic_performance', {}).get('special_programs', [])

        if not programs:
            return {'score': 50, 'details': 'No special programs listed'}

        # Score based on number of programs
        score = min(50 + (len(programs) * 10), 100)

        program_list = ', '.join(programs[:3])
        if len(programs) > 3:
            program_list += f', +{len(programs) - 3} more'

        return {
            'score': score,
            'details': program_list
        }

    def calculate_composite_score(self, school: Dict, weights: Optional[Dict] = None,
                                  preferences: Optional[Dict] = None) -> Dict:
        """Calculate weighted composite score for a school."""
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        if preferences is None:
            preferences = {}

        preferred_size = preferences.get('school_size', 'medium')

        # Calculate individual scores
        scores = {
            'academic_performance': self.calculate_academic_score(school),
            'proximity': self.calculate_proximity_score(school),
            'parent_satisfaction': self.calculate_parent_satisfaction_score(school),
            'student_satisfaction': self.calculate_student_satisfaction_score(school),
            'facilities': self.calculate_facilities_score(school),
            'school_size': self.calculate_school_size_score(school, preferred_size),
            'extracurriculars': self.calculate_extracurriculars_score(school),
            'special_programs': self.calculate_special_programs_score(school)
        }

        # Calculate weighted average
        weighted_sum = 0
        total_weight = 0

        for category, weight in weights.items():
            score_data = scores.get(category)
            if score_data and score_data['score'] is not None:
                weighted_sum += score_data['score'] * weight
                total_weight += weight

        composite_score = weighted_sum / total_weight if total_weight > 0 else None

        return {
            'composite_score': round(composite_score, 1) if composite_score else None,
            'category_scores': scores,
            'weights_used': weights,
            'total_weight': total_weight
        }

    def rank_schools(self, weights: Optional[Dict] = None,
                    preferences: Optional[Dict] = None,
                    filters: Optional[Dict] = None) -> List[Dict]:
        """Rank all schools by composite score."""
        results = []

        for school in self.schools:
            # Apply filters
            if filters:
                if not self._passes_filters(school, filters):
                    continue

            score_data = self.calculate_composite_score(school, weights, preferences)

            if score_data['composite_score'] is not None:
                results.append({
                    'school': school,
                    'score_data': score_data
                })

        # Sort by composite score descending
        results.sort(key=lambda x: x['score_data']['composite_score'], reverse=True)

        return results

    def _passes_filters(self, school: Dict, filters: Dict) -> bool:
        """Check if school passes filter criteria."""
        # School type filter
        if 'school_type' in filters and filters['school_type']:
            school_types = school.get('basic_info', {}).get('type', [])
            if not any(t in school_types for t in filters['school_type']):
                return False

        # Religious affiliation filter
        if 'religious_affiliation' in filters and filters['religious_affiliation']:
            affiliation = school.get('basic_info', {}).get('religious_affiliation', '')
            if filters['religious_affiliation'].lower() not in affiliation.lower():
                return False

        # Max commute time filter
        if 'max_commute_minutes' in filters:
            bike_mins = school.get('location', {}).get('bike_accessibility', {}).get('duration_minutes')
            if bike_mins and bike_mins > filters['max_commute_minutes']:
                return False

        # City filter
        if 'city' in filters and filters['city']:
            city = school.get('basic_info', {}).get('city', '')
            if city.lower() != filters['city'].lower():
                return False

        return True


if __name__ == '__main__':
    # Test the scoring system
    scorer = SchoolScorer()

    print("\n" + "="*70)
    print("Top 10 Schools by Default Weighting")
    print("="*70)

    rankings = scorer.rank_schools()

    for i, result in enumerate(rankings[:10], 1):
        school = result['school']
        score = result['score_data']['composite_score']
        name = school['basic_info']['name']

        print(f"\n{i}. {name}")
        print(f"   Overall Score: {score}/100")

        # Show category scores
        for category, data in result['score_data']['category_scores'].items():
            if data['score'] is not None:
                print(f"   - {category.replace('_', ' ').title()}: {data['score']:.1f} ({data['details']})")
