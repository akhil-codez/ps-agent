import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import get_user_full_profile, get_all_users_full_profile
from eligibility import get_all_eligible_schemes, reload_rules

print("=== Testing Profile-Based Eligibility ===")

reload_rules()

users = get_all_users_full_profile()
print(f"Users: {len(users)}")

for user in users:
    print(f"\nUser: {user.get('name')} ({user.get('phone')})")
    print(f"  Income: {user.get('income')}")
    print(f"  Age: {user.get('age')}")
    print(f"  Category: {user.get('category')}")
    print(f"  Gender: {user.get('gender', 'N/A')}")
    print(f"  Marital Status: {user.get('marital_status', 'N/A')}")
    print(f"  Education: {user.get('education_level', 'N/A')}")
    print(f"  Employment: {user.get('employment_status', 'N/A')}")
    print(f"  House: {user.get('house_ownership', 'N/A')}")
    print(f"  Vehicle: {user.get('vehicle_type', 'N/A')}")
    print(f"  Urban: {user.get('is_urban', False)}")
    print(f"  Health Insurance: {user.get('has_health_insurance', False)}")
    
    eligible = get_all_eligible_schemes(user)
    print(f"\n  Eligible schemes: {len(eligible)}")
    for s in eligible[:5]:
        print(f"    - {s['name'][:50]}")
