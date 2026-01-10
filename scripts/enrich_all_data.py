#!/usr/bin/env python3
"""
Master enrichment script - Runs all scrapers and Google Maps API
to comprehensively enrich school data.
"""

import sys
import os
from pathlib import Path

# Add scrapers directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scrapers'))

def main():
    print("=" * 70)
    print("SCHOOL DATA ENRICHMENT - MASTER SCRIPT")
    print("=" * 70)
    print()

    # Check for Google Maps API key
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    print("This script will enrich school data from multiple sources:")
    print("1. Google Maps API (geocoding + accurate commute times)")
    print("2. Schoolwijzer Amsterdam (official data)")
    print("3. Onderwijsconsument (reviews & ratings)")
    print("4. Schoolkeuze 020 (open days & practical info)")
    print()

    response = input("Proceed with enrichment? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    print("\n" + "=" * 70)

    # Step 1: Google Maps enrichment (if API key available)
    if api_key:
        print("\n### STEP 1: Google Maps Enrichment ###\n")
        try:
            # Import and run Google Maps enrichment
            sys.path.insert(0, str(Path(__file__).parent))
            from calculate_commutes_gmaps import enrich_all_schools
            enrich_all_schools()
        except Exception as e:
            print(f"❌ Error in Google Maps enrichment: {e}")
    else:
        print("\n### STEP 1: Google Maps Enrichment - SKIPPED ###")
        print("⚠️  GOOGLE_MAPS_API_KEY not set")
        print("   Set the environment variable to enable accurate geocoding and commute calculations")

    # Step 2: Schoolwijzer scraping
    print("\n" + "=" * 70)
    print("\n### STEP 2: Schoolwijzer Amsterdam Scraper ###\n")
    try:
        from schoolwijzer_scraper import scrape_school_list, enrich_school_data, match_and_update_json_files

        schools = scrape_school_list()
        if schools:
            enriched = enrich_school_data(schools[:10])  # Limit to avoid rate limiting
            match_and_update_json_files(enriched)
    except Exception as e:
        print(f"❌ Error in Schoolwijzer scraping: {e}")

    # Step 3: Onderwijsconsument scraping
    print("\n" + "=" * 70)
    print("\n### STEP 3: Onderwijsconsument Scraper ###\n")
    try:
        from onderwijsconsument_scraper import enrich_schools_with_onderwijsconsument
        enrich_schools_with_onderwijsconsument()
    except Exception as e:
        print(f"❌ Error in Onderwijsconsument scraping: {e}")

    # Step 4: Schoolkeuze 020 scraping
    print("\n" + "=" * 70)
    print("\n### STEP 4: Schoolkeuze 020 Scraper ###\n")
    try:
        from schoolkeuze020_scraper import enrich_schools_with_schoolkeuze020
        enrich_schools_with_schoolkeuze020()
    except Exception as e:
        print(f"❌ Error in Schoolkeuze 020 scraping: {e}")

    # Step 5: Reconsolidate data
    print("\n" + "=" * 70)
    print("\n### STEP 5: Reconsolidating Data ###\n")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from consolidate_schools import create_consolidated_file
        create_consolidated_file()
    except Exception as e:
        print(f"❌ Error in reconsolidation: {e}")

    print("\n" + "=" * 70)
    print("\n✅ ENRICHMENT COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Review enriched data in data/schools-consolidated.json")
    print("2. Proceed to Part 2: Implement scoring system")
    print("3. Proceed to Part 3: Build interactive tool")

if __name__ == '__main__':
    main()
