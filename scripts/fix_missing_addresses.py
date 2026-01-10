#!/usr/bin/env python3
"""
Fix missing addresses for schools with null address fields.
Uses schoolwijzer.amsterdam.nl and school websites to find addresses.
"""

import json
import os
from pathlib import Path
import time
from bs4 import BeautifulSoup
import requests

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_address_from_schoolwijzer(school_name):
    """Try to find address from schoolwijzer.amsterdam.nl"""
    try:
        # Create search-friendly slug from school name
        slug = school_name.lower()
        slug = slug.replace('(vo)', '').replace('/', '-').strip()
        slug = slug.replace(' ', '-')

        # Try schoolwijzer URL
        url = f"https://schoolwijzer.amsterdam.nl/nl/vo/school/{slug}/"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for address in contact info
            address_elem = soup.find('p', class_='address')
            if address_elem:
                lines = address_elem.get_text(separator='\n').strip().split('\n')
                if len(lines) >= 2:
                    street = lines[0].strip()
                    postal_city = lines[1].strip()
                    # Extract postal code (format: 1234 AB)
                    parts = postal_city.split(' ')
                    if len(parts) >= 3:
                        postal = f"{parts[0]} {parts[1]}"
                        return {
                            'address': street,
                            'postal_code': postal
                        }
    except Exception as e:
        print(f"    Error fetching from schoolwijzer: {e}")

    return None

def find_address_from_website(website_url):
    """Try to extract address from school website"""
    if not website_url:
        return None

    try:
        response = requests.get(website_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Common patterns for address on Dutch school websites
            # Look for contact page
            contact_link = soup.find('a', string=lambda s: s and 'contact' in s.lower())
            if contact_link and contact_link.get('href'):
                contact_url = contact_link['href']
                if not contact_url.startswith('http'):
                    from urllib.parse import urljoin
                    contact_url = urljoin(website_url, contact_url)

                response = requests.get(contact_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

            # Look for address patterns
            text = soup.get_text()
            import re
            # Dutch postal code pattern: 1234 AB
            postal_pattern = r'\b\d{4}\s+[A-Z]{2}\b'
            matches = re.findall(postal_pattern, text)
            if matches:
                postal_code = matches[0]
                # Find the line with postal code and extract address
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if postal_code in line:
                        # Try to find street address in nearby lines
                        for j in range(max(0, i-3), i+1):
                            if re.search(r'\d', lines[j]) and 'Amsterdam' not in lines[j]:
                                street = lines[j].strip()
                                if len(street) > 5 and len(street) < 100:
                                    return {
                                        'address': street,
                                        'postal_code': postal_code
                                    }
    except Exception as e:
        print(f"    Error fetching from website: {e}")

    return None

def fix_school_addresses():
    """Find and fix all schools with null addresses."""
    print("=" * 70)
    print("Missing Address Fixer")
    print("=" * 70)

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

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
            website = data['basic_info'].get('contact', {}).get('website')

            print(f"\n{school_name}")
            print(f"  Current: address=null, website={website}")

            # Try schoolwijzer first
            print(f"  Searching schoolwijzer...")
            address_data = find_address_from_schoolwijzer(school_name)

            # If that fails, try the website
            if not address_data and website:
                print(f"  Trying school website...")
                address_data = find_address_from_website(website)

            if address_data:
                # Update the school data
                data['basic_info']['address'] = address_data['address']
                data['basic_info']['postal_code'] = address_data['postal_code']
                save_school_data(school_file, data)

                print(f"  ✓ Fixed: {address_data['address']}, {address_data['postal_code']}")
                fixed_count += 1
            else:
                print(f"  ✗ Could not find address")
                failed_schools.append(school_name)

            # Rate limiting
            time.sleep(1)

    print("\n" + "=" * 70)
    print(f"Summary: Fixed {fixed_count} schools")
    if failed_schools:
        print(f"\nCould not find addresses for {len(failed_schools)} schools:")
        for school in failed_schools:
            print(f"  - {school}")
    print("=" * 70)

if __name__ == '__main__':
    fix_school_addresses()
