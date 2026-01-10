#!/usr/bin/env python3
"""
Scrape 2026 open day events from schoolkeuze020.nl and add to school data.
"""

import json
import requests
from bs4 import BeautifulSoup
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

def scrape_open_dagen():
    """Scrape open day events from schoolkeuze020.nl."""
    print("Fetching open day data from schoolkeuze020.nl...")

    url = "https://schoolkeuze020.nl/open-dagen/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    events = []

    # Find all event entries - they're typically in a table or list
    # Try multiple selectors
    event_containers = (
        soup.find_all('tr') or  # table rows
        soup.find_all('div', class_=re.compile(r'event|open-dag', re.I)) or  # divs with event classes
        soup.find_all('article')  # articles
    )

    for container in event_containers:
        text = container.get_text(separator=' ', strip=True)

        # Look for date pattern (e.g., "10 januari", "13 jan", "14-01-2026")
        date_patterns = [
            r'(\d{1,2})\s+(januari|februari|maart|april)',
            r'(\d{1,2})-(\d{1,2})-2026',
            r'(\d{1,2})/(\d{1,2})/2026'
        ]

        date_match = None
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                break

        if not date_match:
            continue

        # Look for time pattern (e.g., "18:00-19:30", "12:00 - 15:00")
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})', text)

        # Try to extract school name - usually at the start or in a heading
        school_name = None

        # Try to find heading or strong text
        heading = container.find(['h2', 'h3', 'h4', 'strong', 'b'])
        if heading:
            school_name = heading.get_text(strip=True)
        else:
            # Try to get first substantial text before the date
            parts = text.split(date_match.group(0))
            if parts and len(parts[0]) > 3:
                school_name = parts[0].strip()[:100]  # Limit length

        if school_name and len(school_name) > 2:
            # Clean up school name
            school_name = re.sub(r'\s+', ' ', school_name).strip()

            # Parse date
            month_map = {
                'januari': '01', 'februari': '02', 'maart': '03',
                'april': '04', 'mei': '05', 'juni': '06'
            }

            day = date_match.group(1)
            month = date_match.group(2).lower() if len(date_match.groups()) > 1 else None

            if month and month in month_map:
                date_str = f"2026-{month_map[month]}-{day.zfill(2)}"
            else:
                # Try numeric date
                try:
                    date_str = f"2026-{date_match.group(2).zfill(2)}-{day.zfill(2)}"
                except:
                    continue

            event = {
                'school_name': school_name,
                'date': date_str,
                'type': 'Open Day'
            }

            if time_match:
                start_time = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
                end_time = f"{time_match.group(3).zfill(2)}:{time_match.group(4)}"
                event['time'] = f"{start_time}-{end_time}"

            # Look for registration requirement
            if re.search(r'aanmeld|registr|inschrijv', text, re.IGNORECASE):
                event['registration_required'] = True

            events.append(event)

    # Remove duplicates
    unique_events = []
    seen = set()
    for event in events:
        key = (event['school_name'], event['date'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    print(f"✓ Found {len(unique_events)} open day events")
    return unique_events

def match_school_name(school_name, event_school_name):
    """Flexible school name matching."""
    school_lower = school_name.lower()
    event_lower = event_school_name.lower()

    # Remove common words
    remove_words = ['lyceum', 'college', 'gymnasium', 'school', 'het', 'de', 'amsterdam']

    school_clean = school_lower
    event_clean = event_lower

    for word in remove_words:
        school_clean = school_clean.replace(word, ' ')
        event_clean = event_clean.replace(word, ' ')

    school_clean = ' '.join(school_clean.split())
    event_clean = ' '.join(event_clean.split())

    # Check if core names match
    if school_clean in event_clean or event_clean in school_clean:
        return True

    # Check if main word matches
    school_words = set(school_clean.split())
    event_words = set(event_clean.split())

    # If at least 2 significant words match
    common_words = school_words & event_words
    if len(common_words) >= 2 or (len(common_words) >= 1 and len(school_words) <= 2):
        return True

    return False

def enrich_schools_with_open_dagen():
    """Add 2026 open day events to school data."""
    print("=" * 70)
    print("2026 Open Day Events Enrichment")
    print("=" * 70)

    # Scrape events
    events = scrape_open_dagen()

    if not events:
        print("❌ No events found")
        return

    # Print sample events
    print("\nSample events found:")
    for event in events[:10]:
        print(f"  - {event['school_name']}: {event['date']}")
        if 'time' in event:
            print(f"    Time: {event['time']}")

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    enriched_count = 0
    events_added = 0

    for city_dir in [data_dir / 'amstelveen', data_dir / 'amsterdam']:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            school_data = load_school_data(school_file)
            school_name = school_data['basic_info']['name']

            # Find matching events
            matching_events = []
            for event in events:
                if match_school_name(school_name, event['school_name']):
                    matching_events.append(event)

            if matching_events:
                print(f"\n{school_name}")
                print(f"  Found {len(matching_events)} event(s)")

                # Convert to our format
                open_days = []
                for event in matching_events:
                    open_day = {
                        'date': event['date'],
                        'type': event['type']
                    }

                    if 'time' in event:
                        open_day['time'] = event['time']

                    if event.get('registration_required'):
                        open_day['registration_required'] = True

                    open_days.append(open_day)
                    print(f"    ✓ {event['date']}", end='')
                    if 'time' in event:
                        print(f" {event['time']}", end='')
                    print()

                # Update school data
                school_data['practical_info']['open_days'] = open_days

                # Update metadata
                school_data['metadata']['last_updated'] = datetime.now().isoformat()
                if 'schoolkeuze020.nl open dagen' not in school_data['metadata'].get('data_sources', []):
                    if 'data_sources' not in school_data['metadata']:
                        school_data['metadata']['data_sources'] = []
                    school_data['metadata']['data_sources'].append('schoolkeuze020.nl open dagen')

                save_school_data(school_file, school_data)

                enriched_count += 1
                events_added += len(open_days)

    print("\n" + "=" * 70)
    print(f"✅ Enriched {enriched_count} schools")
    print(f"✅ Added {events_added} total open day events")
    print("=" * 70)

if __name__ == '__main__':
    enrich_schools_with_open_dagen()
