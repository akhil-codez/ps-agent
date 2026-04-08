import sys
sys.stdout.reconfigure(encoding='utf-8')

from database import get_user_full_profile
from eligibility import get_all_eligible_schemes

user_id = '870bb851-fb26-4c84-b1bd-436417e59eaa'

user = get_user_full_profile(user_id)
print('User profile:')
print(f"  Name: {user.get('name')}")
print(f"  Income: {user.get('income')}")
print(f"  Age: {user.get('age')}")
print(f"  Category: {user.get('category')}")
print(f"  Gender: {user.get('gender')}")
print(f"  Marital Status: {user.get('marital_status')}")
print(f"  Education: {user.get('education_level')}")
print(f"  Employment: {user.get('employment_status')}")
print(f"  House: {user.get('house_ownership')}")
print(f"  Vehicle: {user.get('vehicle_type')}")
print(f"  Urban: {user.get('is_urban')}")
print(f"  Health Insurance: {user.get('has_health_insurance')}")
print()
eligible = get_all_eligible_schemes(user)
print(f"Eligible schemes: {len(eligible)}")
for s in eligible[:10]:
    print(f"  - {s['name'][:50]}")
