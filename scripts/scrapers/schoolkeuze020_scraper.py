#!/usr/bin/env python3
"""
Scraper for schoolkeuze020.nl - Amsterdam school choice portal
Extracts practical information like open days, information sessions, etc.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "https://schoolkeuze020.nl"

def scrape_schools_overview():
    """Get list of schools from Schoolkeuze 020."""
    url = f"{BASE_URL}/scholen/"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        schools = []
        school_cards = soup.find_all('div', class_='school-card') or soup.find_all('article', class_='school')

        for card in school_cards:
            school = {}

            # Name
            name_elem = card.find('h2') or card.find('h3')
            if name_elem:
                school['name'] = name_elem.get_text(strip=True)

            # Link
            link_elem = card.find('a', href=True)
            if link_elem:
                school['url'] = link_elem['href']
                if not school['url'].startswith('http'):
                    school['url'] = BASE_URL + school['url']

            if school.get('name'):
                schools.append(school)

        print(f"Found {len(schools)} schools on Schoolkeuze 020")
        return schools

    except Exception as e:
        print(f"Error scraping Schoolkeuze 020: {e}")
        return []

def scrape_school_open_days(school_url):
    """Scrape open days and information sessions for a school."""
    try:
        response = requests.get(school_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        details = {
            'open_days': [],
            'info_sessions': [],
            'practical_info': {}
        }

        # Find open days section
        open_days_section = soup.find('section', id='open-dagen') or soup.find('div', class_='open-days')
        if open_days_section:
            event_items = open_days_section.find_all('div', class_='event') or open_days_section.find_all('li')

            for event in event_items:
                event_data = {}

                # Date
                date_elem = event.find('time') or event.find('span', class_='date')
                if date_elem:
                    event_data['date'] = date_elem.get_text(strip=True)
                    # Try to parse date
                    try:
                        event_data['date_parsed'] = date_elem.get('datetime')
                    except:
                        pass

                # Time
                time_elem = event.find('span', class_='time')
                if time_elem:
                    event_data['time'] = time_elem.get_text(strip=True)

                # Type
                type_elem = event.find('span', class_='type')
                if type_elem:
                    event_data['type'] = type_elem.get_text(strip=True)
                else:
                    event_data['type'] = 'Open Day'

                # Description
                desc_elem = event.find('p', class_='description')
                if desc_elem:
                    event_data['description'] = desc_elem.get_text(strip=True)

                if event_data.get('date'):
                    details['open_days'].append(event_data)

        # Find information sessions
        info_section = soup.find('section', id='informatie') or soup.find('div', class_='info-sessions')
        if info_section:
            sessions = info_section.find_all('div', class_='session')

            for session in sessions:
                session_data = {}

                title_elem = session.find('h4') or session.find('strong')
                if title_elem:
                    session_data['title'] = title_elem.get_text(strip=True)

                date_elem = session.find('time') or session.find('span', class_='date')
                if date_elem:
                    session_data['date'] = date_elem.get_text(strip=True)

                if session_data.get('title'):
                    details['info_sessions'].append(session_data)

        # Application deadlines
        deadline_section = soup.find('section', id='aanmelden') or soup.find('div', class_='deadlines')
        if deadline_section:
            deadline_text = deadline_section.get_text(strip=True)
            details['practical_info']['application_info'] = deadline_text

        # Contact for questions
        contact_section = soup.find('section', id='contact')
        if contact_section:
            email_elem = contact_section.find('a', href=lambda x: x and x.startswith('mailto:'))
            if email_elem:
                details['practical_info']['contact_email'] = email_elem.get_text(strip=True)

            phone_elem = contact_section.find('a', href=lambda x: x and x.startswith('tel:'))
            if phone_elem:
                details['practical_info']['contact_phone'] = phone_elem.get_text(strip=True)

        return details

    except Exception as e:
        print(f"Error scraping {school_url}: {e}")
        return {}

def enrich_schools_with_schoolkeuze020():
    """Enrich existing school files with Schoolkeuze 020 data."""
    data_dir = Path(__file__).parent.parent.parent / 'data' / 'schools'
    updated_count = 0

    # First get schools overview
    schools_overview = scrape_schools_overview()

    for city_dir in [data_dir / 'amsterdam']:  # Schoolkeuze 020 is Amsterdam-only
        if not city_dir.exists():
            continue

        for json_file in sorted(city_dir.glob('*.json')):
            with open(json_file, 'r', encoding='utf-8') as f:
                school_data = json.load(f)

            school_name = school_data['basic_info']['name']
            print(f"Processing: {school_name}")

            # Find matching school in overview
            matching_school = None
            for school in schools_overview:
                if school_name.lower() in school['name'].lower() or school['name'].lower() in school_name.lower():
                    matching_school = school
                    break

            if matching_school and matching_school.get('url'):
                print(f"  Found on Schoolkeuze 020")

                # Scrape details
                details = scrape_school_open_days(matching_school['url'])

                # Update open days
                if details.get('open_days'):
                    # Convert to our format
                    formatted_open_days = []
                    for event in details['open_days']:
                        formatted_event = {
                            'date': event.get('date_parsed') or event.get('date'),
                            'time': event.get('time', ''),
                            'type': event.get('type', 'Open Day')
                        }
                        if event.get('description'):
                            formatted_event['description'] = event['description']
                        formatted_open_days.append(formatted_event)

                    school_data['practical_info']['open_days'] = formatted_open_days
                    print(f"  ✓ Added {len(formatted_open_days)} open day(s)")

                # Update information sessions
                if details.get('info_sessions'):
                    school_data['practical_info']['information_sessions'] = [
                        s.get('title', '') + (' - ' + s.get('date', '') if s.get('date') else '')
                        for s in details['info_sessions']
                    ]
                    print(f"  ✓ Added {len(details['info_sessions'])} info session(s)")

                # Update application info
                if details.get('practical_info', {}).get('application_info'):
                    school_data['practical_info']['application_info'] = details['practical_info']['application_info']

                # Update contact if missing
                if not school_data['basic_info']['contact'].get('email') and details.get('practical_info', {}).get('contact_email'):
                    school_data['basic_info']['contact']['email'] = details['practical_info']['contact_email']

                if not school_data['basic_info']['contact'].get('phone') and details.get('practical_info', {}).get('contact_phone'):
                    school_data['basic_info']['contact']['phone'] = details['practical_info']['contact_phone']

                # Update metadata
                school_data['metadata']['data_sources'].append(BASE_URL)
                school_data['metadata']['data_sources'] = list(set(school_data['metadata']['data_sources']))

                # Save updated file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(school_data, f, indent=2, ensure_ascii=False)

                updated_count += 1
                print(f"  ✓ Updated")

                time.sleep(1)  # Be respectful
            else:
                print(f"  ⚠️  Not found on Schoolkeuze 020")

    print(f"\n✅ Updated {updated_count} schools with Schoolkeuze 020 data")

if __name__ == '__main__':
    print("Schoolkeuze 020 Scraper")
    print("=" * 70)

    enrich_schools_with_schoolkeuze020()
