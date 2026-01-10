#!/usr/bin/env python3
"""
Scraper for schoolwijzer.amsterdam.nl - Official Amsterdam school finder
Extracts comprehensive school information including exam scores, enrollment, etc.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

BASE_URL = "https://schoolwijzer.amsterdam.nl"

def scrape_school_list():
    """Get list of all VO schools from Schoolwijzer."""
    url = f"{BASE_URL}/nl/vo/list/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        schools = []
        # Find school list items
        school_items = soup.find_all('div', class_='school-item') or soup.find_all('article')

        for item in school_items:
            school_data = {}

            # Extract school name
            name_elem = item.find('h2') or item.find('h3') or item.find('a', class_='school-name')
            if name_elem:
                school_data['name'] = name_elem.get_text(strip=True)

            # Extract school link
            link_elem = item.find('a', href=True)
            if link_elem:
                school_data['url'] = link_elem['href']
                if not school_data['url'].startswith('http'):
                    school_data['url'] = BASE_URL + school_data['url']

            # Extract types
            types_elem = item.find('span', class_='types') or item.find('div', class_='education-types')
            if types_elem:
                school_data['types'] = types_elem.get_text(strip=True)

            # Extract address
            address_elem = item.find('address') or item.find('span', class_='address')
            if address_elem:
                school_data['address'] = address_elem.get_text(strip=True)

            if school_data.get('name'):
                schools.append(school_data)

        print(f"Found {len(schools)} schools on Schoolwijzer")
        return schools

    except Exception as e:
        print(f"Error scraping school list: {e}")
        return []

def scrape_school_detail(school_url):
    """Scrape detailed information for a single school."""
    try:
        response = requests.get(school_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        details = {}

        # Extract various data points
        # This is a template - actual selectors depend on site structure

        # Contact information
        phone_elem = soup.find('a', href=lambda x: x and x.startswith('tel:'))
        if phone_elem:
            details['phone'] = phone_elem.get_text(strip=True)

        email_elem = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        if email_elem:
            details['email'] = email_elem.get_text(strip=True)

        # Website
        website_elem = soup.find('a', class_='website') or soup.find('a', text=lambda x: x and 'website' in x.lower())
        if website_elem:
            details['website'] = website_elem['href']

        # Enrollment
        enrollment_elem = soup.find(text=lambda x: x and 'leerlingen' in x.lower())
        if enrollment_elem:
            details['enrollment_text'] = enrollment_elem.strip()

        # BRIN number (official school ID)
        brin_elem = soup.find(text=lambda x: x and 'BRIN' in x)
        if brin_elem:
            details['brin'] = brin_elem.strip()

        # Extract exam scores if available
        scores_section = soup.find('section', id=lambda x: x and 'scores' in x) or soup.find('div', class_='exam-results')
        if scores_section:
            details['exam_scores'] = {}
            for score_item in scores_section.find_all('div', class_='score-item'):
                label = score_item.find('span', class_='label')
                value = score_item.find('span', class_='value')
                if label and value:
                    details['exam_scores'][label.get_text(strip=True)] = value.get_text(strip=True)

        return details

    except Exception as e:
        print(f"Error scraping school detail {school_url}: {e}")
        return {}

def enrich_school_data(schools_list):
    """Enrich school data with detailed information."""
    enriched = []

    for school in schools_list:
        print(f"Scraping: {school['name']}")

        if school.get('url'):
            details = scrape_school_detail(school['url'])
            school.update(details)
            time.sleep(1)  # Be respectful, don't hammer the server

        enriched.append(school)

    return enriched

def match_and_update_json_files(scraped_data):
    """Match scraped data with existing JSON files and update them."""
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'schools' / 'amsterdam'
    updated_count = 0

    for school in scraped_data:
        school_name = school['name']

        # Try to find matching JSON file
        # Normalize name for matching
        normalized_name = school_name.lower().replace(' ', '-').replace('(', '').replace(')', '')

        for json_file in data_dir.glob('*.json'):
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

            if existing_data['basic_info']['name'].lower() in school_name.lower() or \
               school_name.lower() in existing_data['basic_info']['name'].lower():

                print(f"  Updating {existing_data['basic_info']['name']}")

                # Update contact info if missing
                if not existing_data['basic_info']['contact'].get('phone') and school.get('phone'):
                    existing_data['basic_info']['contact']['phone'] = school['phone']

                if not existing_data['basic_info']['contact'].get('email') and school.get('email'):
                    existing_data['basic_info']['contact']['email'] = school['email']

                if not existing_data['basic_info']['contact'].get('website') and school.get('website'):
                    existing_data['basic_info']['contact']['website'] = school['website']

                # Update enrollment if available
                if school.get('enrollment_text'):
                    existing_data['basic_info']['enrollment']['note'] = school['enrollment_text']

                # Update exam scores
                if school.get('exam_scores'):
                    existing_data['academic_performance']['exam_scores'] = school['exam_scores']

                # Add BRIN number
                if school.get('brin'):
                    existing_data['basic_info']['brin'] = school['brin']

                # Update metadata
                existing_data['metadata']['data_sources'].append(BASE_URL)
                existing_data['metadata']['data_sources'] = list(set(existing_data['metadata']['data_sources']))

                # Save updated file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)

                updated_count += 1
                break

    print(f"\n✅ Updated {updated_count} school files with Schoolwijzer data")

if __name__ == '__main__':
    print("Schoolwijzer Scraper")
    print("=" * 70)

    # Scrape school list
    schools = scrape_school_list()

    if schools:
        # Enrich with details
        enriched_schools = enrich_school_data(schools[:5])  # Start with first 5 for testing

        # Match and update JSON files
        match_and_update_json_files(enriched_schools)

        # Save raw scraped data
        output_file = Path(__file__).parent.parent.parent / 'data' / 'scraped_schoolwijzer.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_schools, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Raw data saved to {output_file}")
