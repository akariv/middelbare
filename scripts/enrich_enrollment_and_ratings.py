#!/usr/bin/env python3
"""
Enrich schools with:
1. Student enrollment numbers (leerlingaantal)
2. Parent satisfaction scores (ouderoordeel)
From onderwijsconsument.nl jaren/vo API
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import re

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_jaren_data():
    """Fetch jaren/vo data from API."""
    print("Fetching jaren/vo data from API...")
    url = 'https://www.onderwijsconsument.nl/api/jaren/vo'

    response = requests.get(url, timeout=30)

    if response.status_code != 200:
        print(f"❌ Failed to fetch API: {response.status_code}")
        return []

    data = response.json()
    print(f"✓ Loaded {len(data)} jaren records")

    return data

def parse_rating(rating_str):
    """Parse rating string like '7,1 (aanrader 7,0)' into components."""
    if not rating_str or rating_str == '':
        return None

    # Pattern: "7,1 (aanrader 7,0)" or "6,9 (mening telt 6,5)"
    match = re.search(r'(\d+[,.]?\d*)', rating_str)
    if not match:
        return None

    overall = float(match.group(1).replace(',', '.'))

    result = {'overall': overall}

    # Extract sub-score
    sub_match = re.search(r'\((.*?)\s+(\d+[,.]?\d*)\)', rating_str)
    if sub_match:
        sub_type = sub_match.group(1).strip()
        sub_score = float(sub_match.group(2).replace(',', '.'))

        if 'aanrad' in sub_type.lower():
            result['would_recommend'] = sub_score
        elif 'mening' in sub_type.lower():
            result['voice_matters'] = sub_score

    return result

def get_latest_data_for_school(jaren_data, school_id):
    """Get the most recent enrollment and satisfaction data for a school."""
    # Filter for this school
    school_records = [r for r in jaren_data if r['school_id'] == school_id]

    if not school_records:
        return None

    # Sort by year (most recent first)
    school_records.sort(key=lambda x: x['schooljaar'], reverse=True)

    result = {
        'enrollment': None,
        'parent_satisfaction': None,
        'student_satisfaction': None
    }

    # Get most recent enrollment (leerlingaantal > 0)
    for record in school_records:
        if record.get('leerlingaantal') and record['leerlingaantal'] > 0:
            result['enrollment'] = {
                'total': record['leerlingaantal'],
                'year': record['schooljaar']
            }
            break

    # Get most recent parent satisfaction
    for record in school_records:
        if record.get('ouderoordeel') and record['ouderoordeel'] != '':
            parsed = parse_rating(record['ouderoordeel'])
            if parsed:
                result['parent_satisfaction'] = {
                    **parsed,
                    'year': record['schooljaar']
                }
                break

    # Get most recent student satisfaction
    for record in school_records:
        if record.get('leerlingoordeel') and record['leerlingoordeel'] != '':
            parsed = parse_rating(record['leerlingoordeel'])
            if parsed:
                result['student_satisfaction'] = {
                    **parsed,
                    'year': record['schooljaar']
                }
                break

    return result

def match_school_to_api(school_data, jaren_data):
    """Try to find matching school_id in jaren data."""
    school_name = school_data['basic_info']['name'].lower()

    # Get unique school IDs from jaren data
    school_ids = set(r['school_id'] for r in jaren_data)

    # Try to match by BRIN code if available
    for record in jaren_data:
        if record.get('brin') and record['brin'] != '':
            # Check if our school has this BRIN in metadata or somewhere
            # For now, skip BRIN matching as we don't have it readily accessible
            pass

    # Try name matching
    for school_id in school_ids:
        # Get a sample record for this school
        sample = next((r for r in jaren_data if r['school_id'] == school_id), None)
        if not sample:
            continue

        # Get school name from API records (we need to look at onderwijsconsument.nl/api/scholen)
        # For now, use school_id directly and match later
        pass

    return None

def enrich_all_schools():
    """Enrich all schools with enrollment and satisfaction data."""
    print("=" * 70)
    print("Enrollment & Satisfaction Scores Enrichment")
    print("=" * 70)

    # Fetch jaren data
    jaren_data = fetch_jaren_data()

    if not jaren_data:
        print("❌ No jaren data available")
        return

    # Also need to fetch school data to map school_id to names
    print("\nFetching school data to map IDs...")
    schools_resp = requests.get('https://www.onderwijsconsument.nl/api/scholen', timeout=30)
    schools_api = schools_resp.json() if schools_resp.status_code == 200 else []

    # Create mapping of school_id to school info
    school_id_map = {}
    for school in schools_api:
        if school.get('type') in ['vo', 'VO']:
            school_id_map[school['id']] = {
                'name': school.get('naam', ''),
                'long_name': school.get('lange_naam', ''),
                'brin': school.get('brin', '')
            }

    print(f"✓ Mapped {len(school_id_map)} schools")

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    enriched_count = 0
    enrollment_added = 0
    parent_satisfaction_added = 0
    student_satisfaction_added = 0

    for city_dir in [data_dir / 'amstelveen', data_dir / 'amsterdam']:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            school_data = load_school_data(school_file)
            school_name = school_data['basic_info']['name']

            # Try to find matching school_id
            school_id = None
            school_name_lower = school_name.lower()

            for sid, info in school_id_map.items():
                api_name = info['name'].lower()
                api_long_name = info['long_name'].lower()

                # Flexible matching
                if (school_name_lower in api_long_name or
                    api_name in school_name_lower or
                    api_long_name in school_name_lower):
                    school_id = sid
                    break

            if not school_id:
                continue

            # Get latest data
            latest_data = get_latest_data_for_school(jaren_data, school_id)

            if not latest_data:
                continue

            updated = False

            # Add enrollment
            if latest_data['enrollment']:
                school_data['basic_info']['enrollment']['total'] = latest_data['enrollment']['total']
                print(f"\n{school_name}")
                print(f"  ✓ Enrollment: {latest_data['enrollment']['total']} students ({latest_data['enrollment']['year']})")
                enrollment_added += 1
                updated = True

            # Add parent satisfaction
            if latest_data['parent_satisfaction']:
                if 'parent_reviews' not in school_data['reviews_reputation']:
                    school_data['reviews_reputation']['parent_reviews'] = []

                parent_review = {
                    'overall_rating': latest_data['parent_satisfaction']['overall'],
                    'year': latest_data['parent_satisfaction']['year'],
                    'source': 'onderwijsconsument.nl'
                }

                if 'would_recommend' in latest_data['parent_satisfaction']:
                    parent_review['would_recommend'] = latest_data['parent_satisfaction']['would_recommend']

                # Replace or add
                school_data['reviews_reputation']['parent_reviews'] = [parent_review]

                print(f"  ✓ Parent rating: {latest_data['parent_satisfaction']['overall']}/10", end='')
                if 'would_recommend' in latest_data['parent_satisfaction']:
                    print(f" (recommend: {latest_data['parent_satisfaction']['would_recommend']}/10)", end='')
                print(f" ({latest_data['parent_satisfaction']['year']})")

                parent_satisfaction_added += 1
                updated = True

            # Add student satisfaction
            if latest_data['student_satisfaction']:
                if 'student_reviews' not in school_data['reviews_reputation']:
                    school_data['reviews_reputation']['student_reviews'] = []

                student_review = {
                    'overall_rating': latest_data['student_satisfaction']['overall'],
                    'year': latest_data['student_satisfaction']['year'],
                    'source': 'onderwijsconsument.nl'
                }

                if 'voice_matters' in latest_data['student_satisfaction']:
                    student_review['voice_matters'] = latest_data['student_satisfaction']['voice_matters']

                # Replace or add
                school_data['reviews_reputation']['student_reviews'] = [student_review]

                print(f"  ✓ Student rating: {latest_data['student_satisfaction']['overall']}/10", end='')
                if 'voice_matters' in latest_data['student_satisfaction']:
                    print(f" (voice matters: {latest_data['student_satisfaction']['voice_matters']}/10)", end='')
                print(f" ({latest_data['student_satisfaction']['year']})")

                student_satisfaction_added += 1
                updated = True

            if updated:
                # Update metadata
                school_data['metadata']['last_updated'] = datetime.now().isoformat()
                if 'onderwijsconsument.nl jaren/vo' not in school_data['metadata'].get('data_sources', []):
                    if 'data_sources' not in school_data['metadata']:
                        school_data['metadata']['data_sources'] = []
                    school_data['metadata']['data_sources'].append('onderwijsconsument.nl jaren/vo')

                save_school_data(school_file, school_data)
                enriched_count += 1

    print("\n" + "=" * 70)
    print(f"✅ Enriched {enriched_count} schools")
    print(f"✅ Added enrollment data: {enrollment_added} schools")
    print(f"✅ Added parent satisfaction: {parent_satisfaction_added} schools")
    print(f"✅ Added student satisfaction: {student_satisfaction_added} schools")
    print("=" * 70)

if __name__ == '__main__':
    enrich_all_schools()
