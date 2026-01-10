#!/usr/bin/env python3
"""
Consolidate all individual school JSON files into a single comprehensive file.
"""

import json
from pathlib import Path
from datetime import datetime

def load_all_schools():
    """Load all school JSON files from data/schools directory."""
    schools = []
    data_dir = Path(__file__).parent.parent / 'data' / 'schools'

    # Process Amsterdam schools
    amsterdam_dir = data_dir / 'amsterdam'
    amstelveen_dir = data_dir / 'amstelveen'

    for city_dir in [amsterdam_dir, amstelveen_dir]:
        if not city_dir.exists():
            continue

        for school_file in sorted(city_dir.glob('*.json')):
            try:
                with open(school_file, 'r', encoding='utf-8') as f:
                    school_data = json.load(f)
                    schools.append(school_data)
                    print(f"✓ Loaded {school_data['basic_info']['name']}")
            except Exception as e:
                print(f"❌ Error loading {school_file.name}: {e}")

    return schools

def calculate_statistics(schools):
    """Calculate summary statistics about the schools."""
    stats = {
        "total_schools": len(schools),
        "by_city": {},
        "by_type": {},
        "with_vwo": 0,
        "vwo_only": 0,
        "with_gymnasium": 0,
        "avg_completeness": 0.0
    }

    completeness_scores = []

    for school in schools:
        # City breakdown
        city = school['basic_info']['city']
        stats['by_city'][city] = stats['by_city'].get(city, 0) + 1

        # Type breakdown
        types = school['basic_info']['type']
        for t in types:
            stats['by_type'][t] = stats['by_type'].get(t, 0) + 1

        # VWO statistics
        if 'VWO' in types or 'Gymnasium' in types or 'Atheneum' in types:
            stats['with_vwo'] += 1

        if types == ['VWO'] or types == ['VWO', 'Gymnasium'] or types == ['VWO', 'Atheneum']:
            stats['vwo_only'] += 1

        if 'Gymnasium' in types:
            stats['with_gymnasium'] += 1

        # Completeness
        if 'metadata' in school and 'completeness_score' in school['metadata']:
            completeness_scores.append(school['metadata']['completeness_score'])

    if completeness_scores:
        stats['avg_completeness'] = round(sum(completeness_scores) / len(completeness_scores), 2)

    return stats

def create_consolidated_file():
    """Create the consolidated schools file."""
    print("Loading all school data...\n")
    schools = load_all_schools()

    if not schools:
        print("❌ No schools found!")
        return

    print(f"\n✓ Loaded {len(schools)} schools")

    print("\nCalculating statistics...")
    stats = calculate_statistics(schools)

    # Sort schools by city and name
    schools.sort(key=lambda s: (s['basic_info']['city'], s['basic_info']['name']))

    # Create consolidated data structure
    consolidated = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_schools": stats['total_schools'],
            "statistics": stats,
            "home_address": "Judith Leijsterweg 30, 1187 KE Amstelveen",
            "purpose": "Secondary school selection tool for student transitioning from primary school"
        },
        "schools": schools
    }

    # Save to file
    output_file = Path(__file__).parent.parent / 'data' / 'schools-consolidated.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Consolidated file created: {output_file}")
    print(f"\nStatistics:")
    print(f"  Total schools: {stats['total_schools']}")
    print(f"  By city: {stats['by_city']}")
    print(f"  Schools with VWO: {stats['with_vwo']}")
    print(f"  VWO-only schools: {stats['vwo_only']}")
    print(f"  Schools with Gymnasium: {stats['with_gymnasium']}")
    print(f"  Average completeness: {stats['avg_completeness']*100:.1f}%")

if __name__ == '__main__':
    create_consolidated_file()
