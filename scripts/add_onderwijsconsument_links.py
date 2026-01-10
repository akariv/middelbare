#!/usr/bin/env python3
"""
Add onderwijsconsument.nl links to all schools based on BRIN codes
"""

import json
import requests
from pathlib import Path


def get_brin_mapping():
    """Get mapping of school names to BRIN codes from API"""
    url = 'https://www.onderwijsconsument.nl/api/scholen'
    response = requests.get(url, timeout=10)
    schools = response.json()

    # Create mapping of normalized names to BRIN codes
    mapping = {}
    for school in schools:
        name = school.get('naam', '').lower().strip()
        brin = school.get('brin', '').strip()
        if name and brin:
            mapping[name] = brin

    return mapping


def normalize_name(name):
    """Normalize school name for matching"""
    return name.lower().strip()


def find_brin_code(school_name, brin_mapping):
    """Find BRIN code for a school by name matching"""
    normalized = normalize_name(school_name)

    # Direct match
    if normalized in brin_mapping:
        return brin_mapping[normalized]

    # Fuzzy match - check if any key contains the school name or vice versa
    for api_name, brin in brin_mapping.items():
        # Remove common suffixes for better matching
        school_base = normalized.replace(' amsterdam', '').replace(' amstelveen', '')
        api_base = api_name.replace(' amsterdam', '').replace(' amstelveen', '')

        if school_base in api_base or api_base in school_base:
            if len(school_base) > 5:  # Avoid false matches on very short names
                return brin

    return None


def add_links_to_schools():
    """Add onderwijsconsument links to all school JSON files"""
    print("Fetching BRIN codes from API...")
    brin_mapping = get_brin_mapping()
    print(f"✓ Found {len(brin_mapping)} schools in API\n")

    cities = ['amsterdam', 'amstelveen']
    updated_count = 0
    not_found = []

    for city in cities:
        city_dir = Path(f'data/schools/{city}')
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            with open(school_file, 'r', encoding='utf-8') as f:
                school = json.load(f)

            school_name = school['basic_info']['name']

            # Find BRIN code
            brin = find_brin_code(school_name, brin_mapping)

            if brin:
                # Create onderwijsconsument URL
                oc_url = f"https://www.onderwijsconsument.nl/scholenoverzicht/vo/school/{brin}"

                # Check if link already exists
                links = school.get('practical_info', {}).get('links', [])
                if oc_url not in links:
                    links.append(oc_url)
                    school['practical_info']['links'] = links

                    # Update data sources
                    if 'onderwijsconsument.nl' not in school.get('metadata', {}).get('data_sources', []):
                        school['metadata']['data_sources'].append('onderwijsconsument.nl')

                    # Save updated school
                    with open(school_file, 'w', encoding='utf-8') as f:
                        json.dump(school, f, indent=2, ensure_ascii=False)

                    print(f"✓ {school_name}")
                    print(f"  Added: {oc_url}")
                    updated_count += 1
                else:
                    print(f"→ {school_name} (already has link)")
            else:
                not_found.append(school_name)
                print(f"✗ {school_name} - BRIN not found")

    print(f"\n{'='*70}")
    print(f"✅ Updated {updated_count} schools")

    if not_found:
        print(f"\n⚠️  Could not find BRIN codes for {len(not_found)} schools:")
        for name in not_found:
            print(f"   - {name}")

    print(f"{'='*70}")


if __name__ == '__main__':
    add_links_to_schools()
