import sys
sys.stdout.reconfigure(encoding='utf-8')

from eligibility import get_all_eligible_schemes, reload_rules

print("=== Testing Profile-Based Eligibility (Simulated) ===")

reload_rules()

test_profiles = [
    {
        'name': 'Student Profile',
        'income': 50000,
        'age': 20,
        'category': 'OBC',
        'family_size': 4,
        'district': 'Thiruvananthapuram',
        'gender': 'male',
        'marital_status': 'unmarried',
        'education_level': 'graduate',
        'employment_status': 'unemployed',
        'house_ownership': 'owned',
        'vehicle_type': 'none',
        'is_urban': True,
        'has_health_insurance': False,
    },
    {
        'name': 'Senior Widowed',
        'income': 60000,
        'age': 70,
        'category': 'BPL',
        'family_size': 2,
        'district': 'Kottayam',
        'gender': 'female',
        'marital_status': 'widowed',
        'education_level': 'primary',
        'employment_status': 'unemployed',
        'house_ownership': 'owned',
        'vehicle_type': 'none',
        'is_urban': False,
        'has_health_insurance': False,
    },
    {
        'name': 'Government Employee',
        'income': 400000,
        'age': 45,
        'category': 'General',
        'family_size': 5,
        'district': 'Ernakulam',
        'gender': 'male',
        'marital_status': 'married',
        'education_level': 'post_graduate',
        'employment_status': 'govt_employee',
        'house_ownership': 'owned',
        'vehicle_type': 'four_wheeler',
        'is_urban': True,
        'has_health_insurance': True,
    },
]

for profile in test_profiles:
    print(f"\n{'='*50}")
    print(f"Profile: {profile['name']}")
    print(f"  Age: {profile['age']}, Income: {profile['income']}")
    print(f"  Category: {profile['category']}, Employment: {profile['employment_status']}")
    print(f"  Marital: {profile['marital_status']}, Education: {profile['education_level']}")
    print(f"  House: {profile['house_ownership']}, Vehicle: {profile['vehicle_type']}")
    print(f"  Urban: {profile['is_urban']}, Health Insurance: {profile['has_health_insurance']}")
    
    eligible = get_all_eligible_schemes(profile)
    print(f"\n  Eligible schemes: {len(eligible)}")
    for s in eligible[:8]:
        print(f"    - {s['name'][:55]}")
    if len(eligible) > 8:
        print(f"    ... and {len(eligible) - 8} more")
