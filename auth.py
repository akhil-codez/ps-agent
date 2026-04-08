import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import database

ph = PasswordHasher()

KERALA_DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta",
    "Alappuzha", "Kottayam", "Idukki", "Ernakulam",
    "Thrissur", "Palakkad", "Malappuram", "Kozhikode",
    "Wayanad", "Kannur", "Kasaragod"
]

CATEGORIES = ["BPL", "APL", "SC", "ST", "OBC", "General"]

LANGUAGES = ["malayalam", "english"]

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        ph.verify(password_hash, password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False

def validate_phone(phone: str) -> dict:
    cleaned = re.sub(r'\D', '', phone)
    
    if len(cleaned) == 10:
        return {'valid': True, 'phone': cleaned}
    elif len(cleaned) == 12 and cleaned.startswith('91'):
        return {'valid': True, 'phone': cleaned[2:]}
    elif len(cleaned) == 13 and cleaned.startswith('+91'):
        return {'valid': True, 'phone': cleaned[3:]}
    else:
        return {'valid': False, 'error': 'Invalid phone number. Enter 10 digits.'}

def validate_password(password: str) -> dict:
    if len(password) < 6:
        return {'valid': False, 'error': 'Password must be at least 6 characters'}
    return {'valid': True, 'password': password}

def validate_income(income: int) -> dict:
    if income < 0:
        return {'valid': False, 'error': 'Income cannot be negative'}
    if income > 10000000:
        return {'valid': False, 'error': 'Income seems too high. Please verify.'}
    return {'valid': True, 'income': income}

def validate_age(age: int) -> dict:
    if age < 18:
        return {'valid': False, 'error': 'You must be at least 18 years old'}
    if age > 120:
        return {'valid': False, 'error': 'Invalid age'}
    return {'valid': True, 'age': age}

def validate_family_size(size: int) -> dict:
    if size < 1:
        return {'valid': False, 'error': 'Family size must be at least 1'}
    if size > 20:
        return {'valid': False, 'error': 'Family size seems too high'}
    return {'valid': True, 'family_size': size}

def validate_district(district: str) -> dict:
    if district in KERALA_DISTRICTS:
        return {'valid': True, 'district': district}
    return {'valid': False, 'error': 'Invalid district'}

def validate_category(category: str) -> dict:
    if category in CATEGORIES:
        return {'valid': True, 'category': category}
    return {'valid': False, 'error': 'Invalid category'}

def validate_language(language: str) -> dict:
    if language in LANGUAGES:
        return {'valid': True, 'language': language}
    return {'valid': False, 'error': 'Invalid language'}

def validate_name(name: str) -> dict:
    if len(name) < 2:
        return {'valid': False, 'error': 'Name must be at least 2 characters'}
    if len(name) > 50:
        return {'valid': False, 'error': 'Name must be less than 50 characters'}
    if not re.match(r'^[a-zA-Z\s\.\-]+$', name):
        return {'valid': False, 'error': 'Name contains invalid characters'}
    return {'valid': True, 'name': name.strip()}

def validate_registration_data(data: dict) -> dict:
    errors = []
    
    name_result = validate_name(data.get('name', ''))
    if not name_result['valid']:
        errors.append(name_result['error'])
    
    phone_result = validate_phone(data.get('phone', ''))
    if not phone_result['valid']:
        errors.append(phone_result['error'])
    else:
        data['phone'] = phone_result['phone']
    
    password_result = validate_password(data.get('password', ''))
    if not password_result['valid']:
        errors.append(password_result['error'])
    
    district_result = validate_district(data.get('district', ''))
    if not district_result['valid']:
        errors.append(district_result['error'])
    
    category_result = validate_category(data.get('category', ''))
    if not category_result['valid']:
        errors.append(category_result['error'])
    
    income_result = validate_income(data.get('income', 0))
    if not income_result['valid']:
        errors.append(income_result['error'])
    
    age_result = validate_age(data.get('age', 0))
    if not age_result['valid']:
        errors.append(age_result['error'])
    
    family_result = validate_family_size(data.get('family_size', 0))
    if not family_result['valid']:
        errors.append(family_result['error'])
    
    language_result = validate_language(data.get('language', 'malayalam'))
    if not language_result['valid']:
        errors.append(language_result['error'])
    
    if errors:
        return {'valid': False, 'errors': errors}
    
    return {
        'valid': True,
        'data': {
            'name': name_result['name'],
            'phone': phone_result['phone'],
            'password_hash': hash_password(password_result['password']),
            'district': district_result['district'],
            'category': category_result['category'],
            'income': income_result['income'],
            'age': age_result['age'],
            'family_size': family_result['family_size'],
            'language': language_result['language'],
            'notify': data.get('notify', 1)
        }
    }

def register_user(data: dict) -> dict:
    import logging
    logger = logging.getLogger(__name__)
    
    validation = validate_registration_data(data)
    
    if not validation['valid']:
        return {
            'success': False,
            'errors': validation['errors']
        }
    
    if database.user_exists(validation['data']['phone']):
        return {
            'success': False,
            'errors': ['Phone number already registered']
        }
    
    result = database.create_user(validation['data'])
    
    if result['success']:
        print(f"[AUTH] User created: {result['user_id']}, sending notifications...")
        try:
            import notifier
            import eligibility
            
            user_data = {
                'user_id': result['user_id'],
                'phone': validation['data']['phone'],
                'name': validation['data']['name'],
                'language': validation['data']['language'],
                'income': validation['data']['income'],
                'age': validation['data']['age'],
                'category': validation['data']['category'],
                'family_size': validation['data']['family_size'],
                'district': validation['data']['district'],
            }
            print(f"[AUTH] User data prepared, language={user_data['language']}")
            
            print(f"[AUTH] Sending welcome notification...")
            notif_result = notifier.send_welcome_notification(user_data)
            print(f"[AUTH] Welcome notification result: {notif_result}")
            
            print(f"[AUTH] Checking eligible schemes for new user...")
            full_profile = database.get_user_full_profile(result['user_id'])
            eligible_schemes = eligibility.get_all_eligible_schemes(full_profile)
            print(f"[AUTH] Found {len(eligible_schemes)} eligible schemes")
            
            if eligible_schemes:
                print(f"[AUTH] Getting top 5 most relevant schemes...")
                top_schemes = notifier.get_top_schemes_for_user(full_profile, eligible_schemes, limit=5)
                print(f"[AUTH] Sending top {len(top_schemes)} schemes to new user...")
                batch_result = notifier.send_eligibility_batch(full_profile, top_schemes, is_new_user=True)
                print(f"[AUTH] Eligibility batch result: {batch_result}")
            
            logger.info(f"Welcome notification sent to {validation['data']['phone']}")
        except Exception as e:
            print(f"[AUTH] ERROR sending notifications: {e}")
            import traceback
            traceback.print_exc()
            logger.error(f"Failed to send notifications: {e}")
        
        return {
            'success': True,
            'user_id': result['user_id'],
            'message': 'Registration successful!'
        }
    
    return {
        'success': False,
        'errors': [result.get('error', 'Registration failed')]
    }

def login_user(phone: str, password: str) -> dict:
    phone_result = validate_phone(phone)
    
    if not phone_result['valid']:
        return {
            'success': False,
            'error': phone_result['error']
        }
    
    phone = phone_result['phone']
    
    if not database.user_exists(phone):
        return {
            'success': False,
            'error': 'Phone number not registered'
        }
    
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute('SELECT password_hash FROM users WHERE phone = ?', (phone,))
    row = c.fetchone()
    conn.close()
    
    if not verify_password(password, row['password_hash']):
        return {
            'success': False,
            'error': 'Invalid password'
        }
    
    basic_profile = database.verify_user(phone, row['password_hash'])
    
    if basic_profile.get('user_id'):
        profile = database.get_user_full_profile(basic_profile['user_id'])
        if not profile:
            profile = basic_profile
    else:
        profile = basic_profile
    
    return {
        'success': True,
        'user_id': profile['user_id'],
        'profile': profile,
        'message': 'Login successful!'
    }

if __name__ == "__main__":
    database.init_db()
    print("Auth module ready!")
    print(f"Districts: {KERALA_DISTRICTS}")
    print(f"Categories: {CATEGORIES}")
