#!/usr/bin/env python3
"""
Calculate accurate commute times using Google Maps APIs.
Requires: GOOGLE_MAPS_API_KEY in .env file or environment variable
"""

import json
import os
from pathlib import Path
import time
import googlemaps
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
HOME_ADDRESS = "Judith Leijsterweg 30, 1181 TC Amstelveen, Netherlands"
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

if not API_KEY:
    print("❌ Error: GOOGLE_MAPS_API_KEY environment variable not set")
    print("   Get API key from: https://console.cloud.google.com/")
    print("   Enable APIs: Geocoding API, Distance Matrix API, Directions API")
    exit(1)

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

def geocode_address(address):
    """Geocode an address to get precise coordinates."""
    try:
        result = gmaps.geocode(address)
        if result:
            location = result[0]['geometry']['location']
            return {
                'lat': location['lat'],
                'lon': location['lng'],
                'formatted_address': result[0]['formatted_address']
            }
    except Exception as e:
        print(f"  ⚠️  Geocoding error: {e}")
    return None

def get_commute_info(origin, destination):
    """Get detailed commute information for bike and public transit."""
    commute_data = {
        'bike': None,
        'transit': None
    }

    # Get biking directions
    try:
        bike_directions = gmaps.directions(
            origin,
            destination,
            mode="bicycling",
            departure_time=datetime(2026, 2, 10, 8, 0)  # Monday morning
        )

        if bike_directions:
            leg = bike_directions[0]['legs'][0]
            commute_data['bike'] = {
                'distance_km': leg['distance']['value'] / 1000,
                'duration_minutes': leg['duration']['value'] / 60,
                'duration_text': leg['duration']['text'],
                'distance_text': leg['distance']['text']
            }
    except Exception as e:
        print(f"  ⚠️  Bike routing error: {e}")

    # Get public transit directions
    try:
        transit_directions = gmaps.directions(
            origin,
            destination,
            mode="transit",
            departure_time=datetime(2026, 2, 10, 8, 0),  # Monday morning
            transit_mode=["bus", "rail", "tram", "subway"]
        )

        if transit_directions:
            leg = transit_directions[0]['legs'][0]

            # Count transfers
            transfers = 0
            transit_modes = set()
            for step in leg['steps']:
                if step['travel_mode'] == 'TRANSIT':
                    transit_modes.add(step['transit_details']['line']['vehicle']['type'])
                    if len(transit_modes) > 1:
                        transfers += 1

            # Extract route info
            routes = []
            for step in leg['steps']:
                if step['travel_mode'] == 'TRANSIT':
                    transit = step['transit_details']
                    routes.append({
                        'line': transit['line']['short_name'] if 'short_name' in transit['line'] else transit['line']['name'],
                        'vehicle': transit['line']['vehicle']['type'],
                        'from': transit['departure_stop']['name'],
                        'to': transit['arrival_stop']['name']
                    })

            commute_data['transit'] = {
                'duration_minutes': leg['duration']['value'] / 60,
                'duration_text': leg['duration']['text'],
                'transfers': transfers,
                'routes': routes,
                'departure_time': leg['departure_time']['text'] if 'departure_time' in leg else None,
                'arrival_time': leg['arrival_time']['text'] if 'arrival_time' in leg else None
            }
    except Exception as e:
        print(f"  ⚠️  Transit routing error: {e}")

    return commute_data

def load_school_data(school_file):
    """Load school JSON data."""
    with open(school_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_school_data(school_file, data):
    """Save updated school JSON data."""
    with open(school_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def enrich_school_with_gmaps(school_file, home_coords):
    """Enrich a school file with Google Maps data."""
    data = load_school_data(school_file)
    school_name = data['basic_info']['name']

    # Build school address
    address_parts = [
        data['basic_info'].get('address', ''),
        data['basic_info'].get('postal_code', ''),
        data['basic_info'].get('city', ''),
        'Netherlands'
    ]
    school_address = ', '.join(filter(None, address_parts))

    print(f"Processing: {school_name}")
    print(f"  Address: {school_address}")

    # Geocode school address if coordinates missing or inaccurate
    if not data['location']['coordinates'].get('lat') or not data['location']['coordinates'].get('lon'):
        print(f"  📍 Geocoding address...")
        geocode_result = geocode_address(school_address)

        if geocode_result:
            data['location']['coordinates'] = {
                'lat': geocode_result['lat'],
                'lon': geocode_result['lon']
            }
            data['basic_info']['formatted_address'] = geocode_result['formatted_address']
            print(f"  ✓ Coordinates: {geocode_result['lat']:.4f}, {geocode_result['lon']:.4f}")
        else:
            print(f"  ❌ Geocoding failed")
            return False

    # Get commute information
    print(f"  🚴 Calculating routes...")
    commute_data = get_commute_info(HOME_ADDRESS, school_address)

    # Update bike accessibility
    if commute_data['bike']:
        bike = commute_data['bike']
        data['location']['bike_accessibility'] = {
            'distance_km': round(bike['distance_km'], 2),
            'duration_minutes': int(bike['duration_minutes']),
            'distance_text': bike['distance_text'],
            'duration_text': bike['duration_text']
        }

        # Add route quality estimate
        if bike['distance_km'] < 3:
            data['location']['bike_accessibility']['route_quality'] = "Very short distance, local biking"
        elif bike['distance_km'] < 6:
            data['location']['bike_accessibility']['route_quality'] = "Short distance, easy bike commute"
        elif bike['distance_km'] < 10:
            data['location']['bike_accessibility']['route_quality'] = "Moderate distance, typical bike commute"
        else:
            data['location']['bike_accessibility']['route_quality'] = "Long distance, may prefer public transport"

        print(f"  ✓ Bike: {bike['distance_text']} (~{int(bike['duration_minutes'])} min)")
    else:
        print(f"  ⚠️  Bike route not available")

    # Update public transport
    if commute_data['transit']:
        transit = commute_data['transit']
        data['location']['public_transport']['commute_from_home'] = {
            'duration_minutes': int(transit['duration_minutes']),
            'duration_text': transit['duration_text'],
            'transfers': transit['transfers'],
            'routes': transit['routes'],
            'departure_time': transit['departure_time'],
            'arrival_time': transit['arrival_time']
        }

        # Extract nearest stops from routes
        if transit['routes']:
            nearest_stops = []
            for route in transit['routes']:
                stop_info = f"{route['from']} ({route['vehicle']}: {route['line']})"
                if stop_info not in nearest_stops:
                    nearest_stops.append(stop_info)
            data['location']['public_transport']['nearest_stops'] = nearest_stops[:3]  # Top 3

        print(f"  ✓ Transit: {transit['duration_text']} ({transit['transfers']} transfer(s))")
        for route in transit['routes']:
            print(f"    - {route['vehicle']} {route['line']}: {route['from']} → {route['to']}")
    else:
        print(f"  ⚠️  Public transport route not available")

    # Update metadata
    data['metadata']['last_updated'] = datetime.now().isoformat()
    if 'google_maps_enriched' not in data['metadata']:
        data['metadata']['google_maps_enriched'] = True

    # Save updated data
    save_school_data(school_file, data)
    print(f"  ✅ Saved\n")

    return True

def enrich_all_schools():
    """Enrich all school files with Google Maps data."""
    print("=" * 70)
    print("Google Maps Commute Calculator")
    print("=" * 70)
    print(f"Home: {HOME_ADDRESS}\n")

    # Geocode home address
    print("Geocoding home address...")
    home_geocode = geocode_address(HOME_ADDRESS)
    if not home_geocode:
        print("❌ Failed to geocode home address")
        return

    home_coords = {
        'lat': home_geocode['lat'],
        'lon': home_geocode['lon']
    }
    print(f"✓ Home coordinates: {home_coords['lat']:.4f}, {home_coords['lon']:.4f}\n")

    data_dir = Path(__file__).parent.parent / 'data' / 'schools'
    amsterdam_dir = data_dir / 'amsterdam'
    amstelveen_dir = data_dir / 'amstelveen'

    total_processed = 0
    total_success = 0

    for city_dir in [amstelveen_dir, amsterdam_dir]:  # Process Amstelveen first (closer)
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            try:
                success = enrich_school_with_gmaps(school_file, home_coords)
                total_processed += 1
                if success:
                    total_success += 1

                # Rate limiting: Google Maps has usage limits
                # Free tier: ~50 requests per second, 40k/day for Geocoding
                # Be conservative to avoid hitting limits
                time.sleep(0.5)  # 2 requests/second max

            except Exception as e:
                print(f"❌ Error processing {school_file.name}: {e}\n")

    print("=" * 70)
    print(f"✅ Complete: {total_success}/{total_processed} schools enriched successfully")
    print("=" * 70)

    if total_success < total_processed:
        print(f"\n⚠️  {total_processed - total_success} schools had errors")
        print("   Check error messages above for details")

if __name__ == '__main__':
    if not API_KEY:
        print("\n📋 Setup Instructions:")
        print("1. Get a Google Maps API key:")
        print("   https://console.cloud.google.com/")
        print("2. Enable these APIs:")
        print("   - Geocoding API")
        print("   - Distance Matrix API")
        print("   - Directions API")
        print("3. Set environment variable:")
        print("   export GOOGLE_MAPS_API_KEY='your-api-key-here'")
        print("4. Run this script again")
        exit(1)

    print("🗺️  Using Google Maps API for accurate commute calculations\n")
    enrich_all_schools()
