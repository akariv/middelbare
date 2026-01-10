#!/usr/bin/env python3
"""
Fetch school addresses from onderwijsconsument.nl API
"""

import json
import requests
from pathlib import Path

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def search_api_for_school(school_name):
    """Search the API for a school by name"""
    try:
        # Try different API endpoints
        endpoints = [
            'https://www.onderwijsconsument.nl/api/scholen',
            'https://www.onderwijsconsument.nl/api/vo-scholen',
        ]

        for endpoint in endpoints:
            try:
                print(f"    Trying {endpoint}...")
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    schools = response.json()

                    # Search for matching school
                    for school in schools:
                        if 'naam' in school:
                            api_name = school['naam'].lower()
                            search_name = school_name.lower()

                            # Flexible matching
                            if (search_name in api_name or
                                api_name in search_name or
                                search_name.replace(' ', '') == api_name.replace(' ', '')):

                                address_data = {}
                                if 'straat' in school and school['straat']:
                                    address_data['address'] = school['straat']
                                    if 'huisnr' in school and school['huisnr']:
                                        address_data['address'] += f" {school['huisnr']}"

                                if 'pc' in school and school['pc']:
                                    address_data['postal_code'] = school['pc']

                                if address_data:
                                    return address_data

            except Exception as e:
                print(f"    Error with {endpoint}: {e}")
                continue

    except Exception as e:
        print(f"    API error: {e}")

    return None

def fix_missing_addresses():
    """Fix all missing addresses using the API"""
    print("=" * 70)
    print("Address Fixer using onderwijsconsument.nl API")
    print("=" * 70)

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    # First, let's test the API
    print("\nTesting API access...")
    try:
        response = requests.get('https://www.onderwijsconsument.nl/api/scholen', timeout=10)
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Records found: {len(data)}")
            if len(data) > 0:
                print(f"Sample fields: {list(data[0].keys())[:10]}")
    except Exception as e:
        print(f"API test failed: {e}")

    fixed_count = 0
    failed_schools = []

    for city_dir in [data_dir / 'amsterdam', data_dir / 'amstelveen']:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            data = load_school_data(school_file)

            # Check if address is null
            if data['basic_info']['address'] is not None:
                continue

            school_name = data['basic_info']['name']
            print(f"\n{school_name}")

            # Try API search
            address_data = search_api_for_school(school_name)

            if address_data and 'address' in address_data:
                data['basic_info']['address'] = address_data['address']
                if 'postal_code' in address_data:
                    data['basic_info']['postal_code'] = address_data['postal_code']

                save_school_data(school_file, data)
                print(f"  ✓ Fixed: {address_data['address']}, {address_data.get('postal_code', 'N/A')}")
                fixed_count += 1
            else:
                print(f"  ✗ Not found in API")
                failed_schools.append(school_name)

    print("\n" + "=" * 70)
    print(f"Summary: Fixed {fixed_count} schools")
    if failed_schools:
        print(f"\nCould not find {len(failed_schools)} schools:")
        for school in failed_schools:
            print(f"  - {school}")
    print("=" * 70)

if __name__ == '__main__':
    fix_missing_addresses()
