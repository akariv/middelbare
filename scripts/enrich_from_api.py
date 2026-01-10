#!/usr/bin/env python3
"""
Comprehensive school data enrichment using onderwijsconsument.nl API.
Fills in all missing fields across all categories.
"""

import json
import requests
from pathlib import Path
from datetime import datetime

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_api_data():
    """Fetch all schools from API."""
    try:
        response = requests.get('https://www.onderwijsconsument.nl/api/scholen', timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching API data: {e}")
    return []

def find_school_in_api(school_name, api_data):
    """Find a school in the API data by name matching."""
    search_name = school_name.lower().strip()

    # Try exact matches and partial matches
    for api_school in api_data:
        if api_school.get('type') not in ['vo', 'VO']:
            continue

        api_name = api_school.get('naam', '').lower().strip()
        api_lange_naam = api_school.get('lange_naam', '').lower().strip()

        # Exact match
        if search_name == api_name or search_name == api_lange_naam:
            return api_school

        # Partial match (school name in API name or vice versa)
        if (search_name in api_name or api_name in search_name or
            search_name in api_lange_naam or api_lange_naam in search_name):
            # Avoid false positives with very short names
            if len(search_name) > 5:
                return api_school

    return None

def map_denominatie_to_religious_affiliation(denominatie):
    """Map Dutch denominatie to English religious affiliation."""
    mapping = {
        'openbaar': 'Public (openbaar onderwijs)',
        'algemeen bijzonder': 'Private non-denominational',
        'rooms-katholiek': 'Roman Catholic',
        'protestants-christelijk': 'Protestant Christian',
        'reformatorisch': 'Reformed Protestant',
        'evangelisch': 'Evangelical',
        'joods': 'Jewish',
        'islamitisch': 'Islamic',
        'hindoeïstisch': 'Hindu',
        'antroposofisch': 'Anthroposophic (Waldorf/Steiner)',
        'buddhist': 'Buddhist'
    }

    denominatie_lower = denominatie.lower() if denominatie else ''
    for key, value in mapping.items():
        if key in denominatie_lower:
            return value

    return denominatie if denominatie else None

def enrich_school_from_api(school_data, api_school):
    """Enrich school data with information from API."""
    updated_fields = []

    # BASIC INFO
    basic = school_data['basic_info']

    # Phone
    if not basic['contact'].get('phone') and api_school.get('telefoon'):
        basic['contact']['phone'] = api_school['telefoon']
        updated_fields.append('phone')

    # Email
    if not basic['contact'].get('email') and api_school.get('email'):
        basic['contact']['email'] = api_school['email']
        updated_fields.append('email')

    # Website
    if not basic['contact'].get('website') and api_school.get('website'):
        basic['contact']['website'] = api_school['website']
        updated_fields.append('website')

    # Religious affiliation
    if api_school.get('denominatie'):
        mapped_affiliation = map_denominatie_to_religious_affiliation(api_school['denominatie'])
        if mapped_affiliation and (not basic.get('religious_affiliation') or
                                   basic.get('religious_affiliation') in ['None', 'Unknown', None]):
            basic['religious_affiliation'] = mapped_affiliation
            updated_fields.append('religious_affiliation')

    # ACADEMIC PERFORMANCE
    academic = school_data['academic_performance']

    # Education concept
    if api_school.get('onderwijsconcept'):
        concept = api_school['onderwijsconcept']
        if 'montessori' in concept.lower() and 'Montessori' not in str(academic.get('special_programs', [])):
            if 'special_programs' not in academic or not academic['special_programs']:
                academic['special_programs'] = []
            if 'Montessori education' not in academic['special_programs']:
                academic['special_programs'].append('Montessori education')
                updated_fields.append('montessori_program')

    # Extracurricular activities
    if api_school.get('buitenschools'):
        activities = api_school['buitenschools']
        if activities and len(activities) > 10:  # Has meaningful content
            if not academic.get('extracurricular_activities'):
                academic['extracurricular_activities'] = []
            # Parse and add activities
            activity_list = [a.strip() for a in activities.split(',') if a.strip()]
            for activity in activity_list[:5]:  # Add up to 5 activities
                if activity not in academic['extracurricular_activities']:
                    academic['extracurricular_activities'].append(activity)
                    updated_fields.append('extracurricular')

    # FACILITIES
    facilities = school_data['facilities']

    # Classrooms/building quality
    if not facilities.get('classrooms_labs_quality') and api_school.get('schoolgebouw'):
        building = api_school['schoolgebouw']
        if building and len(building) > 5:
            facilities['classrooms_labs_quality'] = building
            updated_fields.append('building_info')

    # Technology
    if not facilities.get('technology') or not facilities['technology']:
        facilities['technology'] = {}

    if api_school.get('ict_hardware') and not facilities['technology'].get('description'):
        facilities['technology']['description'] = api_school['ict_hardware']
        updated_fields.append('technology')

    # STUDENT SUPPORT
    support = school_data['student_support']

    # Counseling/study guidance
    if not support.get('counseling') and api_school.get('studiebegeleiding'):
        guidance = api_school['studiebegeleiding']
        if guidance and len(guidance) > 5:
            support['counseling'] = guidance
            updated_fields.append('counseling')

    # Special education support
    if api_school.get('zorgaanbod'):
        zorg = api_school['zorgaanbod']
        if zorg and len(zorg) > 5:
            if not support.get('special_education'):
                support['special_education'] = []
            # Parse support services
            services = [s.strip() for s in zorg.split(',') if s.strip()]
            for service in services[:5]:
                if service not in support['special_education']:
                    support['special_education'].append(service)
                    updated_fields.append('special_education')

    # Support from API ondersteuningsaanbod
    if api_school.get('ondersteuningsaanbod'):
        if not support.get('special_education'):
            support['special_education'] = []
        for item in api_school['ondersteuningsaanbod'][:5]:
            support_type = item.get('ondersteuningsaanbod')
            if support_type and support_type not in support['special_education']:
                support['special_education'].append(support_type)
                updated_fields.append('support_services')

    # ENVIRONMENT
    environment = school_data['environment']

    # Safety measures
    if api_school.get('veiligheid'):
        safety = api_school['veiligheid']
        if safety and len(safety) > 5:
            if not environment.get('safety_measures'):
                environment['safety_measures'] = []
            measures = [s.strip() for s in safety.split(',') if s.strip()]
            for measure in measures:
                if measure not in environment['safety_measures']:
                    environment['safety_measures'].append(measure)
                    updated_fields.append('safety')

    # Culture and values - add general description
    if not environment.get('culture_values') and api_school.get('algemene_beschrijving'):
        description = api_school['algemene_beschrijving']
        if description and len(description) > 20:
            environment['culture_values'] = description
            updated_fields.append('culture_description')

    # LOCATION
    location = school_data['location']

    # Public transport info
    if api_school.get('bereikbaarheid') and not location.get('public_transport', {}).get('description'):
        if 'public_transport' not in location:
            location['public_transport'] = {}
        location['public_transport']['accessibility_info'] = api_school['bereikbaarheid']
        updated_fields.append('transport_access')

    # PRACTICAL INFO
    practical = school_data['practical_info']

    # Admission rules
    if api_school.get('voorrangsregels') or api_school.get('toelating'):
        admission_info = []
        if api_school.get('voorrangsregels'):
            admission_info.append(f"Voorrangsregels: {api_school['voorrangsregels']}")
        if api_school.get('toelating'):
            admission_info.append(f"Toelating: {api_school['toelating']}")

        if not practical.get('admission_info'):
            practical['admission_info'] = admission_info
            updated_fields.append('admission')

    # School hours
    if api_school.get('begintijd') and not school_data['basic_info']['hours'].get('school_hours'):
        start_time = api_school.get('begintijd', '')
        end_time = api_school.get('eindtijd_lange_dag', '')
        if start_time:
            hours_str = f"{start_time}"
            if end_time:
                hours_str += f"-{end_time}"
            school_data['basic_info']['hours']['school_hours'] = hours_str
            updated_fields.append('school_hours')

    # Links
    if not practical.get('links'):
        practical['links'] = []

    if api_school.get('schoolwijzerlink') and api_school['schoolwijzerlink'] not in practical['links']:
        practical['links'].append(api_school['schoolwijzerlink'].strip())
        updated_fields.append('links')

    if api_school.get('inspectielink') and api_school['inspectielink'] not in practical['links']:
        practical['links'].append(api_school['inspectielink'])
        updated_fields.append('links')

    if api_school.get('scholenopdekaart') and api_school['scholenopdekaart'] not in practical['links']:
        practical['links'].append(api_school['scholenopdekaart'])
        updated_fields.append('links')

    # Update metadata
    if updated_fields:
        school_data['metadata']['last_updated'] = datetime.now().isoformat()
        if 'onderwijsconsument.nl API' not in school_data['metadata'].get('data_sources', []):
            if 'data_sources' not in school_data['metadata']:
                school_data['metadata']['data_sources'] = []
            school_data['metadata']['data_sources'].append('onderwijsconsument.nl API')

    return updated_fields

def enrich_all_schools():
    """Enrich all school files with API data."""
    print("=" * 70)
    print("Comprehensive School Data Enrichment from API")
    print("=" * 70)

    print("\nFetching API data...")
    api_data = fetch_api_data()
    print(f"✓ Loaded {len(api_data)} schools from API")

    vo_schools = [s for s in api_data if s.get('type') in ['vo', 'VO']]
    print(f"✓ Found {len(vo_schools)} VO (secondary) schools in API\n")

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    enriched_count = 0
    total_fields_added = 0
    not_found_schools = []

    for city_dir in [data_dir / 'amstelveen', data_dir / 'amsterdam']:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            school_data = load_school_data(school_file)
            school_name = school_data['basic_info']['name']

            print(f"{school_name}")

            # Find school in API
            api_school = find_school_in_api(school_name, vo_schools)

            if api_school:
                print(f"  ✓ Found in API: {api_school['naam']}")

                # Enrich the school data
                updated_fields = enrich_school_from_api(school_data, api_school)

                if updated_fields:
                    save_school_data(school_file, school_data)
                    field_count = len(set(updated_fields))
                    print(f"  ✅ Added {field_count} fields: {', '.join(list(set(updated_fields))[:5])}")
                    enriched_count += 1
                    total_fields_added += field_count
                else:
                    print(f"  ℹ️  No new data to add")
            else:
                print(f"  ⚠️  Not found in API")
                not_found_schools.append(school_name)

    print("\n" + "=" * 70)
    print(f"✅ Enriched {enriched_count} schools")
    print(f"✅ Added {total_fields_added} total fields")

    if not_found_schools:
        print(f"\n⚠️  {len(not_found_schools)} schools not found in API:")
        for school in not_found_schools:
            print(f"   - {school}")

    print("=" * 70)

if __name__ == '__main__':
    enrich_all_schools()
