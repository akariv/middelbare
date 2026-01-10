#!/usr/bin/env python3
"""
Unit tests for school data validation

Validates that all school JSON files conform to the expected schema
and contain valid data types and values.
"""

import json
import unittest
from pathlib import Path
from datetime import datetime


class SchoolDataValidationTests(unittest.TestCase):
    """Test suite for validating school data integrity"""

    @classmethod
    def setUpClass(cls):
        """Load all school data files"""
        cls.schools = []
        for city_dir in [Path('data/schools/amsterdam'), Path('data/schools/amstelveen')]:
            if city_dir.exists():
                for school_file in sorted(city_dir.glob('*.json')):
                    with open(school_file, 'r', encoding='utf-8') as f:
                        school_data = json.load(f)
                        school_data['_file_path'] = str(school_file)
                        cls.schools.append(school_data)

        print(f"\n✓ Loaded {len(cls.schools)} schools for testing")

    def test_all_schools_loaded(self):
        """Verify that schools were loaded successfully"""
        self.assertGreater(len(self.schools), 0, "No schools found")
        self.assertGreaterEqual(len(self.schools), 46, "Expected at least 46 schools")

    def test_required_top_level_keys(self):
        """Test that all schools have required top-level keys"""
        required_keys = [
            'id', 'basic_info', 'academic_performance', 'facilities',
            'student_support', 'environment', 'location',
            'reviews_reputation', 'practical_info', 'ai_analysis', 'metadata'
        ]

        for school in self.schools:
            with self.subTest(school=school['basic_info']['name']):
                for key in required_keys:
                    self.assertIn(key, school,
                        f"Missing required key '{key}' in {school['_file_path']}")

    def test_basic_info_structure(self):
        """Test basic_info section structure"""
        required_fields = ['name', 'address', 'city', 'postal_code', 'contact', 'type']

        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                basic_info = school['basic_info']

                # Required fields
                for field in required_fields:
                    self.assertIn(field, basic_info,
                        f"Missing '{field}' in basic_info for {name}")

                # Name should be a non-empty string
                self.assertIsInstance(basic_info['name'], str)
                self.assertGreater(len(basic_info['name']), 0)

                # Type should be a list
                self.assertIsInstance(basic_info['type'], list)
                self.assertGreater(len(basic_info['type']), 0,
                    f"{name} has no school types")

                # Contact should have required fields
                contact = basic_info['contact']
                self.assertIsInstance(contact, dict)
                self.assertIn('phone', contact)
                self.assertIn('email', contact)
                self.assertIn('website', contact)

    def test_coordinates_format(self):
        """Test that coordinates are valid numbers"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                location = school.get('location', {})
                coords = location.get('coordinates', {})

                if coords:
                    self.assertIn('lat', coords)
                    self.assertIn('lon', coords)

                    if coords['lat'] is not None:
                        self.assertIsInstance(coords['lat'], (int, float))
                        self.assertGreater(coords['lat'], 50)  # Amsterdam area
                        self.assertLess(coords['lat'], 54)

                    if coords['lon'] is not None:
                        self.assertIsInstance(coords['lon'], (int, float))
                        self.assertGreater(coords['lon'], 4)
                        self.assertLess(coords['lon'], 6)

    def test_open_days_structure(self):
        """Test that open_days are properly structured as dict objects"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                open_days = school.get('practical_info', {}).get('open_days', [])

                # Should be a list
                self.assertIsInstance(open_days, list,
                    f"open_days should be a list in {name}")

                # Each event should be a dict with required fields
                for i, event in enumerate(open_days):
                    self.assertIsInstance(event, dict,
                        f"Event {i} in {name} should be a dict, got {type(event)}")

                    # Should have these keys
                    self.assertIn('date', event,
                        f"Event {i} in {name} missing 'date'")
                    self.assertIn('type', event,
                        f"Event {i} in {name} missing 'type'")

                    # Date should be a string in YYYY-MM-DD format
                    if event['date']:
                        self.assertIsInstance(event['date'], str)
                        try:
                            datetime.strptime(event['date'], '%Y-%m-%d')
                        except ValueError:
                            self.fail(f"Invalid date format '{event['date']}' in {name}")

    def test_enrollment_data(self):
        """Test enrollment data structure"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                enrollment = school.get('basic_info', {}).get('enrollment')

                if enrollment:
                    self.assertIsInstance(enrollment, dict)

                    if 'total' in enrollment and enrollment['total'] is not None:
                        self.assertIsInstance(enrollment['total'], int)
                        self.assertGreater(enrollment['total'], 0)
                        self.assertLess(enrollment['total'], 5000,
                            f"Suspicious enrollment count {enrollment['total']} for {name}")

    def test_exam_scores_structure(self):
        """Test exam scores data structure"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                exam_scores = school.get('academic_performance', {}).get('exam_scores', {})

                # Should be a dict
                self.assertIsInstance(exam_scores, dict)

                # Check each level
                for level in ['vmbo', 'havo', 'vwo']:
                    if level in exam_scores:
                        level_data = exam_scores[level]
                        self.assertIsInstance(level_data, dict)

                        # Check pass rates
                        if 'pass_rate_2024_2025' in level_data:
                            rate = level_data['pass_rate_2024_2025']
                            if rate is not None:
                                self.assertIsInstance(rate, (int, float))
                                self.assertGreaterEqual(rate, 0)
                                self.assertLessEqual(rate, 100)

    def test_satisfaction_scores_structure(self):
        """Test parent and student satisfaction data structure"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                reviews = school.get('reviews_reputation', {})

                # Parent reviews
                parent_reviews = reviews.get('parent_reviews', [])
                self.assertIsInstance(parent_reviews, list)

                for review in parent_reviews:
                    self.assertIsInstance(review, dict)
                    if 'overall_rating' in review and review['overall_rating'] is not None:
                        rating = review['overall_rating']
                        self.assertIsInstance(rating, (int, float))
                        self.assertGreaterEqual(rating, 0)
                        self.assertLessEqual(rating, 10)

                # Student reviews
                student_reviews = reviews.get('student_reviews', [])
                self.assertIsInstance(student_reviews, list)

                for review in student_reviews:
                    self.assertIsInstance(review, dict)
                    if 'overall_rating' in review and review['overall_rating'] is not None:
                        rating = review['overall_rating']
                        self.assertIsInstance(rating, (int, float))
                        self.assertGreaterEqual(rating, 0)
                        self.assertLessEqual(rating, 10)

    def test_commute_data_structure(self):
        """Test commute data structure"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                location = school.get('location', {})

                # Bike accessibility
                bike = location.get('bike_accessibility', {})
                if bike and 'duration_minutes' in bike and bike['duration_minutes'] is not None:
                    self.assertIsInstance(bike['duration_minutes'], (int, float))
                    self.assertGreater(bike['duration_minutes'], 0)
                    self.assertLess(bike['duration_minutes'], 120,
                        f"Suspicious bike time {bike['duration_minutes']} for {name}")

                # Transit
                transit = location.get('public_transport', {}).get('commute_from_home', {})
                if transit and 'duration_minutes' in transit and transit['duration_minutes'] is not None:
                    self.assertIsInstance(transit['duration_minutes'], (int, float))
                    self.assertGreater(transit['duration_minutes'], 0)
                    self.assertLess(transit['duration_minutes'], 180,
                        f"Suspicious transit time {transit['duration_minutes']} for {name}")

    def test_metadata_present(self):
        """Test that metadata is present and valid"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                metadata = school.get('metadata', {})

                self.assertIsInstance(metadata, dict)
                self.assertIn('data_sources', metadata)
                self.assertIsInstance(metadata['data_sources'], list)

    def test_ai_analysis_completeness(self):
        """Test that AI analysis section has required fields"""
        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                ai_analysis = school.get('ai_analysis', {})

                self.assertIsInstance(ai_analysis, dict)

                # Check for key sections
                for key in ['strengths', 'considerations', 'best_fit_for', 'summary']:
                    self.assertIn(key, ai_analysis,
                        f"Missing '{key}' in ai_analysis for {name}")

    def test_lists_not_strings(self):
        """Test that list fields are actually lists, not strings"""
        list_fields = [
            ('basic_info', 'type'),
            ('academic_performance', 'special_programs'),
            ('academic_performance', 'extracurricular_activities'),
            ('student_support', 'special_education'),
            ('facilities', 'sports_facilities'),
            ('practical_info', 'open_days'),
            ('reviews_reputation', 'parent_reviews'),
            ('reviews_reputation', 'student_reviews'),
        ]

        for school in self.schools:
            name = school['basic_info']['name']
            with self.subTest(school=name):
                for section, field in list_fields:
                    if section in school and field in school[section]:
                        value = school[section][field]
                        self.assertIsInstance(value, list,
                            f"{section}.{field} should be a list in {name}, got {type(value)}")

    def test_unique_school_ids(self):
        """Test that all school IDs are unique"""
        ids = [school['id'] for school in self.schools]
        duplicates = [id for id in ids if ids.count(id) > 1]

        self.assertEqual(len(set(ids)), len(ids),
            f"Duplicate school IDs found: {set(duplicates)}")

    def test_no_null_names(self):
        """Test that no school has null or empty name"""
        for school in self.schools:
            name = school['basic_info'].get('name')
            self.assertIsNotNone(name, f"School has null name in {school['_file_path']}")
            self.assertIsInstance(name, str)
            self.assertGreater(len(name.strip()), 0)


class SchoolDataConsistencyTests(unittest.TestCase):
    """Test suite for cross-school data consistency"""

    @classmethod
    def setUpClass(cls):
        """Load all school data files"""
        cls.schools = []
        for city_dir in [Path('data/schools/amsterdam'), Path('data/schools/amstelveen')]:
            if city_dir.exists():
                for school_file in sorted(city_dir.glob('*.json')):
                    with open(school_file, 'r', encoding='utf-8') as f:
                        cls.schools.append(json.load(f))

    def test_amsterdam_schools_in_amsterdam(self):
        """Test that schools in amsterdam folder are in Amsterdam city"""
        amsterdam_dir = Path('data/schools/amsterdam')
        if amsterdam_dir.exists():
            for school_file in amsterdam_dir.glob('*.json'):
                with open(school_file, 'r') as f:
                    school = json.load(f)
                    city = school['basic_info'].get('city', '').lower()
                    self.assertEqual(city, 'amsterdam',
                        f"{school['basic_info']['name']} in amsterdam folder but city is '{city}'")

    def test_amstelveen_schools_in_amstelveen(self):
        """Test that schools in amstelveen folder are in Amstelveen city"""
        amstelveen_dir = Path('data/schools/amstelveen')
        if amstelveen_dir.exists():
            for school_file in amstelveen_dir.glob('*.json'):
                with open(school_file, 'r') as f:
                    school = json.load(f)
                    city = school['basic_info'].get('city', '').lower()
                    self.assertEqual(city, 'amstelveen',
                        f"{school['basic_info']['name']} in amstelveen folder but city is '{city}'")


def run_tests():
    """Run all tests and provide summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(SchoolDataValidationTests))
    suite.addTests(loader.loadTestsFromTestCase(SchoolDataConsistencyTests))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ All data validation tests passed!")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
