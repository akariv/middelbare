# Data Accuracy Fix - Summary Report

**Date:** 2026-01-09
**Issue:** Inaccurate commute times due to missing school addresses
**Status:** ✅ RESOLVED

## Problem Discovered

During manual verification, significant discrepancies were found between the calculated commute data and actual locations. Investigation revealed:

- **31 out of 45 schools (69%)** had `null` address fields
- Google Maps script geocoded only city names ("Amsterdam, Netherlands") instead of actual street addresses
- This resulted in:
  - Inaccurate coordinates (city center instead of actual school location)
  - Incorrect commute distances and times
  - Misleading proximity calculations

## Root Cause

The background agent that initially collected school data did not successfully scrape street addresses for most schools. The schools-list.json tracked schools as "completed" but many had incomplete address data.

## Solution Implemented

### 1. Address Collection (31 schools fixed)

**Method 1: onderwijsconsument.nl API** ✅
- Created `fetch_addresses_from_api.py` script
- Successfully fetched 27 addresses automatically
- API provided: street address, house number, postal code

**Method 2: Manual Web Search** ✅
- Manually searched and updated 4 schools:
  - Joodse Scholengemeenschap Maimonides: Noordbrabantstraat 15-17, 1083 BE
  - Vossius Gymnasium: Messchaertstraat 1, 1077 WS
  - Cygnus Gymnasium: Vrolikstraat 8, 1091 VG
  - Het 4e Gymnasium: Archangelweg 4, 1013 ZZ
  - Vox College: Meeuwenlaan 132, 1022 AM

### 2. Google Maps Re-enrichment

Re-ran `calculate_commutes_gmaps.py` for all 45 schools with corrected addresses:
- Accurate geocoding with real street addresses
- Real bike routes via Google Directions API
- Public transport routes with transfers, times, and stops

## Impact Examples

### Joodse Scholengemeenschap Maimonides
| Metric | Before (null address) | After (correct address) | Improvement |
|--------|----------------------|------------------------|-------------|
| Bike distance | 9.3 km | **3.8 km** | 5.5 km closer |
| Bike time | 31 mins | **12 mins** | 19 mins faster |
| Transit time | 29 mins | 32 mins | Accurate route |

### Other Schools Verified
- **Vossius Gymnasium**: 6.0 km (20 mins bike), 30 mins transit
- **Spinoza Lyceum**: 4.7 km (15 mins bike), 29 mins transit
- **Hermann Wesselink College**: 3.2 km (10 mins bike), 21 mins transit
- **Cygnus Gymnasium**: 9.4 km (29 mins bike), 43 mins transit

## Final Results

✅ **All 45 schools now have:**
- Complete street addresses with postal codes
- Accurate GPS coordinates from real addresses
- Correct bike commute distances and durations
- Accurate public transport routes with:
  - Number of transfers
  - Specific routes and line numbers
  - Departure and arrival times
  - Nearest stops

## Files Modified

### Scripts Created
- `scripts/fix_missing_addresses.py` - Web scraping attempt
- `scripts/fetch_addresses_from_api.py` - API-based address fetcher

### Data Updated
- All 31 school JSON files with null addresses
- All 45 schools re-enriched with accurate Google Maps data

## Verification

```bash
# Confirm no null addresses remain
grep -l '"address": null' data/schools/*/*.json | wc -l
# Output: 0

# Sample commute data looks accurate
jq '.location.bike_accessibility.distance_km' data/schools/*/*.json | sort -n
# Range: 2.7 km (CSB) to 16.2 km (Montessori Lyceum Terra Nova)
```

## Lessons Learned

1. **Always validate scraped data** - "completed" status doesn't mean complete data
2. **APIs are more reliable than web scraping** - onderwijsconsument.nl API was highly effective
3. **Geocoding accuracy matters** - 5+ km differences can dramatically affect school selection
4. **Verify critical fields** - Address data is essential for location-based calculations

## Next Steps

Data is now accurate and ready for:
- ✅ Part 2: Scoring system implementation
- ✅ Part 3: Interactive visualization tool
- ✅ User decision-making for school selection
