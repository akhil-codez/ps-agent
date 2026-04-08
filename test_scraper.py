import sys
sys.stdout.reconfigure(encoding='utf-8')

from scheme_scraper import scrape_all_sources, save_scraped_schemes

print("=== Testing Scheme Scraper ===")
schemes = scrape_all_sources()
print(f"\nTotal schemes found: {len(schemes)}")

if schemes:
    print("\nSample schemes:")
    for s in schemes[:10]:
        print(f"  - {s.get('name', 'Unknown')[:60]}")
        print(f"    Source: {s.get('source', 'Unknown')}")

save_scraped_schemes(schemes)
print(f"\nSaved {len(schemes)} schemes to scraped_schemes_raw.json")
