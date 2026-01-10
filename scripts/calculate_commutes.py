#!/usr/bin/env python3
"""
Calculate commute times from home address to all schools.
Uses public transport and biking routes.
"""

import json
import os
from pathlib import Path
import time

# Home address
HOME_ADDRESS = "Judith Leijsterweg 30, 1187 KE Amstelveen"
HOME_COORDS = {"lat": 52.2889, "lon": 4.8492}

def calculate_distance_km(coord1, coord2):
    """Calculate approximate distance in km between two coordinates using Haversine formula."""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth's radius in km

    lat1, lon1 = radians(coord1['lat']), radians(coord1['lon'])
    lat2, lon2 = radians(coord2['lat']), radians(coord2['lon'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c

def estimate_bike_time(distance_km):
    """Estimate bike commute time. Average speed: 15 km/h in city."""
    BIKE_SPEED_KMH = 15
    return int(distance_km / BIKE_SPEED_KMH * 60)  # minutes

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def enrich_commute_data():
    """Enrich all school files with commute calculations."""
    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    # Process Amsterdam schools
    amsterdam_dir = data_dir / 'amsterdam'
    amstelveen_dir = data_dir / 'amstelveen'

    total_processed = 0

    for city_dir in [amsterdam_dir, amstelveen_dir]:
        if not city_dir.exists():
            continue

        for school_file in city_dir.glob('*.json'):
            try:
                data = load_school_data(school_file)

                # Get school coordinates
                school_coords = data.get('location', {}).get('coordinates', {})
                if not school_coords.get('lat') or not school_coords.get('lon'):
                    print(f"⚠️  {data['basic_info']['name']}: Missing coordinates, skipping")
                    continue

                # Calculate distance
                distance = calculate_distance_km(HOME_COORDS, school_coords)
                bike_time = estimate_bike_time(distance)

                # Update bike accessibility
                if 'location' not in data:
                    data['location'] = {}
                if 'bike_accessibility' not in data['location']:
                    data['location']['bike_accessibility'] = {}

                data['location']['bike_accessibility']['distance_km'] = round(distance, 2)
                data['location']['bike_accessibility']['duration_minutes'] = bike_time

                # Add route quality estimate
                if distance < 3:
                    data['location']['bike_accessibility']['route_quality'] = "Very short distance, local biking"
                elif distance < 6:
                    data['location']['bike_accessibility']['route_quality'] = "Short distance, easy bike commute"
                elif distance < 10:
                    data['location']['bike_accessibility']['route_quality'] = "Moderate distance, typical bike commute"
                else:
                    data['location']['bike_accessibility']['route_quality'] = "Long distance, may prefer public transport"

                # Save updated data
                save_school_data(school_file, data)

                print(f"✓ {data['basic_info']['name']}: {distance:.1f}km, ~{bike_time}min by bike")
                total_processed += 1

            except Exception as e:
                print(f"❌ Error processing {school_file.name}: {e}")

    print(f"\n✅ Processed {total_processed} schools")

if __name__ == '__main__':
    print("Calculating commute times from home to all schools...")
    print(f"Home: {HOME_ADDRESS}\n")
    enrich_commute_data()
