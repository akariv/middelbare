#!/usr/bin/env python3
"""
Manually enrich the 3 remaining schools with exam data using corrected BRIN codes.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Manual BRIN code mappings discovered from DUO data
MANUAL_MAPPINGS = {
    'hervormd-lyceum-zuid-amsterdam': '02AR',  # Het Hervormd Lyc Zuid
    'csb-amsterdam': '14VY',  # Chr Sgm Buitenveldert
    'denise-amsterdam': '17YS',  # Esprit Scholen (DENISE is part of Esprit)
}

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_duo_csv():
    """Load DUO exam data from CSV."""
    print("Loading DUO exam data from CSV...")
    csv_file = '/tmp/examenkandidaten-en-geslaagden-2020-2025.csv'

    df = pd.read_csv(csv_file, sep=';', encoding='utf-8')

    # Filter for Amsterdam
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

def enrich_manual_schools():
    """Enrich the 3 schools with manually mapped BRIN codes."""
    print("=" * 70)
    print("Manual Exam Results Enrichment")
    print("=" * 70)

    duo_data = load_duo_csv()

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    enriched_count = 0

    for school_id, brin_code in MANUAL_MAPPINGS.items():
        # Find the school file
        city = school_id.split('-')[-1]  # amsterdam or amstelveen
        school_filename = school_id.replace(f'-{city}', '') + '.json'
        school_file = data_dir / city / school_filename

        if not school_file.exists():
            print(f"\n❌ File not found: {school_file}")
            continue

        school_data = load_school_data(school_file)
        school_name = school_data['basic_info']['name']

        print(f"\n{school_name}")
        print(f"  ✓ Using BRIN: {brin_code}")

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
    print("=" * 70)

if __name__ == '__main__':
    enrich_manual_schools()
