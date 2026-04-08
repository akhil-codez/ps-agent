import sys
sys.stdout.reconfigure(encoding='utf-8')

from eligibility_extractor import process_scraped_schemes, add_all_new_schemes, load_existing_rules
from scheme_scraper import load_scraped_schemes
from eligibility import reload_rules

print("=== Testing Eligibility Extractor ===")

existing = load_existing_rules()
print(f"Existing rules: {len(existing)}")

scraped = load_scraped_schemes()
print(f"Loaded {len(scraped)} scraped schemes")

print("\nProcessing schemes...")
new_rules = process_scraped_schemes(scraped)
print(f"New valid rules: {len(new_rules)}")

if new_rules:
    print("\nSample new rules:")
    for rule in new_rules[:5]:
        print(f"  - {rule['name'][:50]}")
        print(f"    Income max: {rule['conditions'].get('annual_income_max', 'N/A')}")
        print(f"    Age min: {rule['conditions'].get('age_min', 'N/A')}")
        print(f"    Documents: {len(rule.get('documents_needed', []))}")

print("\nAdding schemes to eligibility_rules.json...")
added = add_all_new_schemes(scraped)
print(f"Added {added} new schemes")

reload_rules()
final = load_existing_rules()
print(f"\nFinal total rules: {len(final)}")
