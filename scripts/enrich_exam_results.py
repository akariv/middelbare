#!/usr/bin/env python3
"""
Enrich schools with DUO exam results (pass rates, graduation statistics).
This adds critical quality metrics for school comparison.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def download_duo_data():
    """Download DUO exam results file if not already present."""
    duo_file = Path('/tmp/duo_exams_2020-2025.xlsx')

    if duo_file.exists():
        print("✓ DUO data file already downloaded")
        return duo_file

    print("Downloading DUO exam results...")
    url = 'https://duo.nl/open_onderwijsdata/images/examenkandidaten-en-geslaagden-2020-2025.xlsx'
    response = requests.get(url, timeout=60)

    if response.status_code == 200:
        with open(duo_file, 'wb') as f:
            f.write(response.content)
        print("✓ Downloaded DUO exam data")
        return duo_file
    else:
        print(f"❌ Failed to download DUO data: {response.status_code}")
        return None

def load_duo_data(duo_file):
    """Load and process DUO exam data."""
    print("Loading DUO exam data...")
    df = pd.read_excel(duo_file)

    # Filter for Amsterdam and Amstelveen
    cities = df[df['GEMEENTENAAM'].isin(['AMSTERDAM', 'AMSTELVEEN'])].copy()
    print(f"✓ Loaded {len(cities)} exam records for Amsterdam/Amstelveen")

    # Convert "<5" values to numeric (treat as 2.5 for calculations)
    for col in cities.columns:
        if 'EXAMENKANDIDATEN' in col or 'GESLAAGDEN' in col:
            cities[col] = cities[col].apply(lambda x: 2.5 if x == '<5' else x)
            cities[col] = pd.to_numeric(cities[col], errors='coerce').fillna(0)

    return cities

def get_exam_data_for_brin(duo_data, brin_code):
    """Extract exam data for a specific school BRIN code."""
    school_data = duo_data[duo_data['INSTELLINGSCODE'] == brin_code]

    if len(school_data) == 0:
        return None

    # Group by education type and get statistics
    exam_results = {}

    for edu_type in ['VMBO', 'HAVO', 'VWO']:
        type_data = school_data[school_data['ONDERWIJSTYPE VO'] == edu_type]

        if len(type_data) == 0:
            continue

        # Get latest year (2024-2025) statistics
        candidates_2024 = type_data['EXAMENKANDIDATEN SCHOOLJAAR 2024-2025 - TOTAAL'].sum()
        passed_2024 = type_data['GESLAAGDEN SCHOOLJAAR 2024-2025 - TOTAAL'].sum()

        # Calculate overall pass rate for this type
        if candidates_2024 > 0:
            pass_rate_2024 = round((passed_2024 / candidates_2024) * 100, 1)
        else:
            pass_rate_2024 = None

        # Get 5-year averages
        years = ['2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
        pass_rates = []

        for year in years:
            col_candidates = f'EXAMENKANDIDATEN SCHOOLJAAR {year} - TOTAAL'
            col_passed = f'GESLAAGDEN SCHOOLJAAR {year} - TOTAAL'

            cand = type_data[col_candidates].sum()
            passed = type_data[col_passed].sum()

            if cand > 0:
                pass_rates.append((passed / cand) * 100)

        avg_pass_rate = round(sum(pass_rates) / len(pass_rates), 1) if pass_rates else None

        exam_results[edu_type.lower()] = {
            'pass_rate_2024_2025': pass_rate_2024,
            'candidates_2024_2025': int(candidates_2024) if candidates_2024 > 0 else None,
            'passed_2024_2025': int(passed_2024) if passed_2024 > 0 else None,
            'average_pass_rate_5yr': avg_pass_rate
        }

    return exam_results if exam_results else None

def find_brin_code(school_data, duo_data):
    """Try to find BRIN code for a school."""
    school_name = school_data['basic_info']['name']

    # Search in DUO data by name matching
    for brin in duo_data['INSTELLINGSCODE'].unique():
        duo_names = duo_data[duo_data['INSTELLINGSCODE'] == brin]['INSTELLINGSNAAM VESTIGING'].unique()

        for duo_name in duo_names:
            duo_name_lower = duo_name.lower()
            school_name_lower = school_name.lower()

            # Flexible matching
            if (school_name_lower in duo_name_lower or
                duo_name_lower in school_name_lower or
                school_name_lower.replace(' ', '') == duo_name_lower.replace(' ', '')):
                return brin

    return None

def enrich_all_schools_with_exam_data():
    """Enrich all schools with DUO exam results."""
    print("=" * 70)
    print("DUO Exam Results Enrichment")
    print("=" * 70)

    # Download and load DUO data
    duo_file = download_duo_data()
    if not duo_file:
        print("❌ Cannot proceed without DUO data")
        return

    duo_data = load_duo_data(duo_file)

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    enriched_count = 0
    not_found_schools = []

    for city_dir in [data_dir / 'amstelveen', data_dir / 'amsterdam']:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            school_data = load_school_data(school_file)
            school_name = school_data['basic_info']['name']

            print(f"\n{school_name}")

            # Try to find BRIN code
            brin_code = find_brin_code(school_data, duo_data)

            if not brin_code:
                print(f"  ⚠️  BRIN code not found in DUO data")
                not_found_schools.append(school_name)
                continue

            print(f"  ✓ Found BRIN: {brin_code}")

            # Get exam data
            exam_results = get_exam_data_for_brin(duo_data, brin_code)

            if not exam_results:
                print(f"  ℹ️  No exam results available")
                continue

            # Update school data
            if 'exam_scores' not in school_data['academic_performance']:
                school_data['academic_performance']['exam_scores'] = {}

            school_data['academic_performance']['exam_scores'] = exam_results

            # Update metadata
            school_data['metadata']['last_updated'] = datetime.now().isoformat()
            if 'DUO exam results' not in school_data['metadata'].get('data_sources', []):
                if 'data_sources' not in school_data['metadata']:
                    school_data['metadata']['data_sources'] = []
                school_data['metadata']['data_sources'].append('DUO exam results')

            # Save
            save_school_data(school_file, school_data)

            # Display results
            print(f"  ✅ Added exam results:")
            for edu_type, results in exam_results.items():
                if results['pass_rate_2024_2025']:
                    print(f"    - {edu_type.upper()}: {results['pass_rate_2024_2025']}% pass rate " +
                          f"({results['candidates_2024_2025']} candidates)")

            enriched_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Enriched {enriched_count} schools with exam results")

    if not_found_schools:
        print(f"\n⚠️  {len(not_found_schools)} schools not found in DUO data:")
        for school in not_found_schools:
            print(f"   - {school}")

    print("=" * 70)

if __name__ == '__main__':
    enrich_all_schools_with_exam_data()
