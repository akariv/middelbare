#!/usr/bin/env python3
"""
Scraper for onderwijsconsument.nl - Education consumer organization
Extracts reviews, ratings, and objective school data
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path

BASE_URL = "https://www.onderwijsconsument.nl"

def search_school(school_name):
    """Search for a school on Onderwijsconsument."""
    search_url = f"{BASE_URL}/search"

    try:
        params = {
            'q': school_name,
            'type': 'vo'  # Voortgezet onderwijs
        }

        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find search results
        results = []
        result_items = soup.find_all('div', class_='search-result') or soup.find_all('article', class_='school-result')

        for item in result_items:
            result = {}

            # School name
            name_elem = item.find('h3') or item.find('a', class_='school-name')
            if name_elem:
                result['name'] = name_elem.get_text(strip=True)

            # Link to detail page
            link_elem = item.find('a', href=True)
            if link_elem:
                result['url'] = link_elem['href']
                if not result['url'].startswith('http'):
                    result['url'] = BASE_URL + result['url']

            # Rating
            rating_elem = item.find('span', class_='rating') or item.find('div', class_='score')
            if rating_elem:
                result['rating'] = rating_elem.get_text(strip=True)

            if result.get('name'):
                results.append(result)

        return results

    except Exception as e:
        print(f"Error searching for {school_name}: {e}")
        return []

def scrape_school_detail(school_url):
    """Scrape detailed school information including reviews."""
    try:
        response = requests.get(school_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        details = {
            'reviews': [],
            'ratings': {},
            'facts': {}
        }

        # Extract overall rating
        overall_rating = soup.find('div', class_='overall-rating') or soup.find('span', class_='rating-value')
        if overall_rating:
            details['overall_rating'] = overall_rating.get_text(strip=True)

        # Extract specific ratings (e.g., teaching quality, facilities, etc.)
        rating_items = soup.find_all('div', class_='rating-item')
        for item in rating_items:
            label = item.find('span', class_='label')
            value = item.find('span', class_='value')
            if label and value:
                details['ratings'][label.get_text(strip=True)] = value.get_text(strip=True)

        # Extract reviews
        review_sections = soup.find_all('div', class_='review') or soup.find_all('article', class_='review')
        for review in review_sections[:10]:  # Get top 10 reviews
            review_data = {}

            # Review text
            text_elem = review.find('p', class_='review-text') or review.find('div', class_='content')
            if text_elem:
                review_data['text'] = text_elem.get_text(strip=True)

            # Rating
            rating_elem = review.find('span', class_='rating')
            if rating_elem:
                review_data['rating'] = rating_elem.get_text(strip=True)

            # Date
            date_elem = review.find('time') or review.find('span', class_='date')
            if date_elem:
                review_data['date'] = date_elem.get_text(strip=True)

            # Reviewer type (parent, student, etc.)
            type_elem = review.find('span', class_='reviewer-type')
            if type_elem:
                review_data['reviewer_type'] = type_elem.get_text(strip=True)

            if review_data.get('text'):
                details['reviews'].append(review_data)

        # Extract objective facts
        facts_section = soup.find('section', id='facts') or soup.find('div', class_='school-facts')
        if facts_section:
            fact_items = facts_section.find_all('div', class_='fact')
            for fact in fact_items:
                label = fact.find('dt') or fact.find('span', class_='label')
                value = fact.find('dd') or fact.find('span', class_='value')
                if label and value:
                    details['facts'][label.get_text(strip=True)] = value.get_text(strip=True)

        return details

    except Exception as e:
        print(f"Error scraping school detail {school_url}: {e}")
        return {}

def enrich_schools_with_onderwijsconsument():
    """Enrich existing school files with Onderwijsconsument data."""
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'schools'
    updated_count = 0

    for city_dir in [data_dir / 'amsterdam', data_dir / 'amstelveen']:
        if not city_dir.exists():
            continue

        for json_file in sorted(city_dir.glob('*.json')):
            with open(json_file, 'r', encoding='utf-8') as f:
                school_data = json.load(f)

            school_name = school_data['basic_info']['name']
            print(f"Processing: {school_name}")

            # Search for school
            search_results = search_school(school_name)

            if search_results:
                # Take first result (best match)
                match = search_results[0]
                print(f"  Found: {match['name']}")

                if match.get('url'):
                    # Scrape details
                    details = scrape_school_detail(match['url'])

                    # Update school data
                    if details.get('overall_rating'):
                        school_data['reviews_reputation']['onderwijsconsument_rating'] = details['overall_rating']

                    if details.get('ratings'):
                        school_data['reviews_reputation']['category_ratings'] = details['ratings']

                    if details.get('reviews'):
                        # Add parent reviews
                        parent_reviews = [r for r in details['reviews'] if r.get('reviewer_type') == 'ouder']
                        school_data['reviews_reputation']['parent_reviews'] = parent_reviews

                        # Add student reviews
                        student_reviews = [r for r in details['reviews'] if r.get('reviewer_type') == 'leerling']
                        school_data['reviews_reputation']['student_reviews'] = student_reviews

                    if details.get('facts'):
                        # Update enrollment if available
                        if 'Aantal leerlingen' in details['facts']:
                            school_data['basic_info']['enrollment']['total'] = details['facts']['Aantal leerlingen']

                        # Update exam scores
                        if 'Examencijfer' in details['facts']:
                            school_data['academic_performance']['exam_scores']['gemiddeld'] = details['facts']['Examencijfer']

                    # Update metadata
                    school_data['metadata']['data_sources'].append(BASE_URL)
                    school_data['metadata']['data_sources'] = list(set(school_data['metadata']['data_sources']))

                    # Save updated file
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(school_data, f, indent=2, ensure_ascii=False)

                    updated_count += 1
                    print(f"  ✓ Updated")

                time.sleep(2)  # Be respectful with requests
            else:
                print(f"  ⚠️  Not found on Onderwijsconsument")

    print(f"\n✅ Updated {updated_count} schools with Onderwijsconsument data")

if __name__ == '__main__':
    print("Onderwijsconsument Scraper")
    print("=" * 70)

    enrich_schools_with_onderwijsconsument()
