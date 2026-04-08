from twilio.rest import Client
import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')

SCHEME_PORTALS = {
    'ration card': 'https://ecitizen.citizen.gov.in/',
    'ration': 'https://ecitizen.citizen.gov.in/',
    'pension': 'https://samaswasam.kerala.gov.in/',
    'social security': 'https://samaswasam.kerala.gov.in/',
    'scholarship': 'https://egrantz.kerala.gov.in/',
    'education': 'https://egrantz.kerala.gov.in/',
    'student': 'https://egrantz.kerala.gov.in/',
    'health': 'https://karunya.kerala.gov.in/',
    'karunya': 'https://karunya.kerala.gov.in/',
    'medical': 'https://karunya.kerala.gov.in/',
    'housing': 'https://pmaymis.gov.in/',
    'awas': 'https://pmaymis.gov.in/',
    'pmay': 'https://pmaymis.gov.in/',
    'mgnrega': 'https://www.nrega.nic.in/',
    'nrega': 'https://www.nrega.nic.in/',
    'job': 'https://www.nrega.nic.in/',
    'disability': 'https://sjd.kerala.gov.in/',
    'disabled': 'https://sjd.kerala.gov.in/',
    'widow': 'https://sjd.kerala.gov.in/',
    'senior': 'https://sjd.kerala.gov.in/',
    'elderly': 'https://sjd.kerala.gov.in/',
    'women': 'https://wcd.kerala.gov.in/',
    'child': 'https://wcd.kerala.gov.in/',
    'anganwadi': 'https://wcd.kerala.gov.in/',
    'birth certificate': 'https://cr.kerala.gov.in/',
    'death certificate': 'https://cr.kerala.gov.in/',
    'certificate': 'https://www.kerala.gov.in/',
    'license': 'https://www.kerala.gov.in/',
    'business': 'https://www.kerala.gov.in/',
    'food': 'https://foscos.fssai.gov.in/',
    'fssai': 'https://foscos.fssai.gov.in/',
    'vishwakarma': 'https://pmvishwakarma.gov.in/',
    'mudra': 'https://www.mudra-lenders.in/',
    'stand up india': 'https://www.standupmitra.in/',
    'startup': 'https://www.startupindia.gov.in/',
    'agriculture': 'https://krishi.kerala.gov.in/',
    'farmer': 'https://krishi.kerala.gov.in/',
    'kisan': 'https://pmkisan.gov.in/',
    'insurance': 'https://www.jansuraksha.gov.in/',
    'life insurance': 'https://www.jansuraksha.gov.in/',
    'accident': 'https://www.jansuraksha.gov.in/',
}

COMMON_DOCS_MAPPING = {
    'ration card': 'Ration Card',
    'aadhaar': 'Aadhaar Card',
    'income certificate': 'Income Certificate',
    'income proof': 'Income Certificate',
    'caste certificate': 'Caste Certificate',
    'category certificate': 'Category Certificate',
    'bank account': 'Bank Account/Passbook',
    'bank passbook': 'Bank Passbook',
    'photo': 'Passport Photo',
    'address proof': 'Address Proof',
    'bpl card': 'BPL Card',
    'bpl': 'BPL Certificate',
    'disability certificate': 'Disability Certificate',
    'death certificate': 'Death Certificate',
    'birth certificate': 'Birth Certificate',
    'domicile': 'Domicile Certificate',
    'residence': 'Residence Certificate',
    'marksheet': 'Marksheet',
    'mark sheet': 'Marksheet',
    'student id': 'Student ID',
    'college id': 'College ID',
    'school id': 'School ID',
    'land document': 'Land Documents',
    'property': 'Property Documents',
    'electricity bill': 'Electricity Bill',
    'water bill': 'Water Bill',
    'tax': 'Tax Receipt',
    'voter': 'Voter ID',
    'election': 'Voter ID',
    'driving': 'Driving License',
    'vehicle': 'Vehicle Documents',
    'pan': 'PAN Card',
}

def get_portal_for_scheme(scheme_name: str) -> str:
    """Get application portal URL for a scheme"""
    name_lower = scheme_name.lower()
    for keywords, url in SCHEME_PORTALS.items():
        if keywords in name_lower:
            return url
    return "Visit nearest government office"

def extract_documents_from_text(text: str) -> str:
    """Extract required documents from raw text"""
    if not text:
        return None
    text_lower = text.lower()
    found_docs = set()
    for keyword, doc_name in COMMON_DOCS_MAPPING.items():
        if keyword in text_lower:
            found_docs.add(doc_name)
    if found_docs:
        return ', '.join(sorted(found_docs)[:5])
    return None

def extract_criteria_from_text(text: str) -> str:
    """Extract eligibility criteria from raw text"""
    if not text:
        return None
    text_lower = text.lower()
    criteria_parts = []
    income_patterns = [
        r'(?:annual\s+)?income\s+(?:below|less\s+than|under)\s*(?:₹|Rs\.?)\s*([\d,]+)',
        r'income\s+(?:of\s+)?(?:₹|Rs\.?)\s*([\d,]+)\s*(?:lakh|L)',
    ]
    for pattern in income_patterns:
        match = re.search(pattern, text_lower)
        if match:
            income = match.group(1).replace(',', '')
            if int(income) >= 100000:
                criteria_parts.append(f"Income below ₹{int(income)//100000} lakh")
            else:
                criteria_parts.append(f"Income below ₹{income}")
            break
    age_match = re.search(r'age\s+(?:should\s+be\s+)?(?:above|minimum|at\s+least)\s*(\d+)', text_lower)
    if age_match:
        criteria_parts.append(f"Age {age_match.group(1)}+ years")
    if any(x in text_lower for x in ['bpl', 'below poverty']):
        criteria_parts.append("BPL category")
    if 'kerala' in text_lower and 'resident' in text_lower:
        criteria_parts.append("Kerala resident")
    if criteria_parts:
        return '; '.join(criteria_parts[:3])
    return None

def get_eligibility_reason(scheme: dict, user: dict) -> str:
    """Get why user is eligible for this scheme"""
    reasons = []
    name_lower = scheme.get('name', '').lower()
    conditions = scheme.get('conditions', {})
    income = user.get('income', 0)
    age = user.get('age', 0)
    category = user.get('category', '')
    marital = user.get('marital_status', '')
    house = user.get('house_ownership', '')
    vehicle = user.get('vehicle_type', 'none')
    education = user.get('education_level', '')
    employment = user.get('employment_status', '')
    if 'pension' in name_lower and age >= 60:
        reasons.append(f"Age {age} years (60+)")
    if 'pension' in name_lower and income <= 100000:
        reasons.append(f"Low income ₹{income:,}")
    if 'bpl' in name_lower and category == 'BPL':
        reasons.append("BPL category")
    if 'bpl' in name_lower and category == 'OBC' and income <= 100000:
        reasons.append(f"OBC with low income ₹{income:,}")
    if 'widow' in name_lower and marital == 'widowed':
        reasons.append("Widowed")
    if ('scholarship' in name_lower or 'student' in name_lower) and education:
        reasons.append(f"Student ({education})")
    if ('housing' in name_lower or 'awas' in name_lower) and house != 'owned':
        reasons.append("No pucca house")
    if ('health' in name_lower or 'karunya' in name_lower) and income <= 100000:
        reasons.append(f"Low income ₹{income:,}")
    if category in ['SC', 'ST'] and ('sc' in name_lower or 'st' in name_lower or 'scheduled' in name_lower):
        reasons.append(f"{category} category")
    if reasons:
        return "Because you're: " + ', '.join(reasons[:2])
    return None

def send_whatsapp(phone: str, message: str) -> dict:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    if not clean_phone.startswith('91'):
        clean_phone = '91' + clean_phone
    
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:+{clean_phone}'
        )
        logger.info(f"WhatsApp message sent to {phone}: {msg.sid}")
        return {'success': True, 'message_id': msg.sid, 'status': msg.status}
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {phone}: {str(e)}")
        return {'success': False, 'error': str(e)}

def get_top_eligible_schemes(profile: dict, limit: int = 3) -> list:
    """Get top eligible schemes based on full profile including extra fields"""
    from eligibility import RULES, check_eligibility
    
    house_ownership = profile.get('house_ownership', '')
    vehicle_type = profile.get('vehicle_type', 'none')
    marital_status = profile.get('marital_status', '')
    employment_status = profile.get('employment_status', '')
    education_level = profile.get('education_level', '')
    is_urban = profile.get('is_urban', False)
    has_health_insurance = profile.get('has_health_insurance', False)
    
    full_profile = {
        'income': profile.get('income'),
        'age': profile.get('age'),
        'category': profile.get('category'),
        'family_size': profile.get('family_size'),
        'district': profile.get('district'),
        'kerala_resident': True,
        'has_bpl_card': profile.get('category') == 'BPL',
        'has_aadhaar': True,
        'has_bank_account': True,
        'is_rural': not is_urban,
        'is_urban': is_urban,
        'has_family': True,
        'is_widowed': marital_status == 'widowed',
        'has_disability_cert': profile.get('has_disability_cert', False),
        'is_artisan': profile.get('is_artisan', False),
        'is_student': education_level in ['higher_secondary', 'graduate', 'post_graduate'] if education_level else False,
        'has_private_insurance': has_health_insurance,
        'receives_other_pension': profile.get('receives_other_pension', False),
        'remarried': profile.get('remarried', False),
        'owns_4_wheeler': vehicle_type in ['four_wheeler', 'both'],
        'government_employee': employment_status == 'govt_employee',
        'has_pucca_house': house_ownership == 'owned',
        'is_food_business': profile.get('is_food_business', False),
        'income_above_100000': profile.get('income', 0) > 100000,
        'income_above_300000': profile.get('income', 0) > 300000,
        'income_above_500000': profile.get('income', 0) > 500000,
        'age_below_60': profile.get('age', 0) < 60,
        'age_below_18': profile.get('age', 0) < 18,
    }
    
    eligible = []
    for scheme_key, rule in RULES.items():
        result = check_eligibility(rule['name'], full_profile)
        if result['eligible'] is True:
            eligible.append(rule['name'])
    
    return eligible[:limit]

def format_welcome_notification_ml(user_name: str, eligible_schemes: list) -> str:
    name_greeting = f"സ്വാഗതം {user_name}" if user_name else "സ്വാഗതം!"
    
    schemes_text = ""
    if eligible_schemes:
        for i, scheme in enumerate(eligible_schemes, 1):
            schemes_text += f"📌 {i}. {scheme}\n"
    else:
        schemes_text = "📌 നിങ്ങൾക്ക് അർഹമായ സ്കീമുകൾ അറിയാൻ ചോദിക്കൂ!\n"
    
    return f"""{name_greeting}
ഞാൻ നിങ്ങളുടെ AI പഞ്ചായത്ത് സേവ അസിസ്റ്റന്റാണ്.

✅ അക്കൗണ്ട് വിജയകരമായി സൃഷ്ടിച്ചു!

📢 നിങ്ങൾക്ക് അർഹമായ സ്കീമുകൾ:
{schemes_text}
📌 നിങ്ങൾക്ക് ഇവിടെ ചെയ്യാം:

1️⃣ എല്ലാ സ്കീമുകളും അറിയാൻ → "എനിക്ക് ഏത് സ്കീമുകൾക്ക് അർഹതയുണ്ട്?"
2️⃣ സർട്ടിഫിക്കറ്റുകൾ → "ബർത്ത് സർട്ടിഫിക്കറ്റ് എങ്ങനെ എടുക്കാം?"
3️⃣ ഓഫീസ് വിലാസം → "എനിക്ക് ഏറ്റവും അടുത്ത ഓഫീസ് എവിടെ?"

💬 I will update u with new schemes!!"""

def format_welcome_notification_en(user_name: str, eligible_schemes: list) -> str:
    name_greeting = f"Welcome {user_name}" if user_name else "Welcome!"
    
    schemes_text = ""
    if eligible_schemes:
        for i, scheme in enumerate(eligible_schemes, 1):
            schemes_text += f"📌 {i}. {scheme}\n"
    else:
        schemes_text = "📌 Ask about schemes you qualify for!\n"
    
    return f"""{name_greeting}
I am your AI Panchayat Seva assistant.

✅ Account created successfully!

📢 Your eligible schemes:
{schemes_text}
📌 What you can do here:

1️⃣ All schemes → Ask "What schemes am I eligible for?"
2️⃣ Certificates → Ask "How to get birth certificate?"
3️⃣ Find offices → Ask "Where is the nearest office?"

💬 I will update u with new schemes!!"""

def send_welcome_notification(user: dict) -> dict:
    """Send welcome notification to newly registered user"""
    print(f"[NOTIFIER] Starting welcome notification for user: {user.get('name')}, phone: {user.get('phone')}")
    lang = user.get('language', 'malayalam')
    user_name = user.get('name', '') if user.get('name') else ''
    print(f"[NOTIFIER] Language: {lang}")
    
    eligible_schemes = get_top_eligible_schemes(user)
    print(f"[NOTIFIER] Eligible schemes: {eligible_schemes}")
    
    if lang == 'malayalam':
        message = format_welcome_notification_ml(user_name, eligible_schemes)
        print(f"[NOTIFIER] Using Malayalam format")
    else:
        message = format_welcome_notification_en(user_name, eligible_schemes)
        print(f"[NOTIFIER] Using English format")
    
    print(f"[NOTIFIER] Sending WhatsApp to {user['phone']}...")
    result = send_whatsapp(user['phone'], message)
    print(f"[NOTIFIER] WhatsApp result: {result}")
    
    return result

def format_daily_digest_ml(schemes: list) -> str:
    if not schemes:
        return ""
    
    header = """🏛️ പഞ്ചായത്ത് സേവ ഏജന്റ് - ദൈനംദിന സംഗ്രഹം

ഇന്നത്തെ അർഹതയുള്ള സ്കീമുകൾ:"""
    
    items = []
    for s in schemes[:5]:
        items.append(f"\n📌 {s['name']}\n   💰 {s.get('benefit', 'N/A')}")
    
    footer = "\n\n💬 കൂടുതൽ വിവരങ്ങൾക്ക് ഈ ചാറ്റിൽ ചോദിക്കുക!"
    
    return header + "\n".join(items) + footer

def format_daily_digest_en(schemes: list) -> str:
    if not schemes:
        return ""
    
    header = """🏛️ Panchayat Seva Agent - Daily Digest

Your eligible schemes for today:"""
    
    items = []
    for s in schemes[:5]:
        items.append(f"\n📌 {s['name']}\n   💰 {s.get('benefit', 'N/A')}")
    
    footer = "\n\n💬 Reply for more details!"
    
    return header + "\n".join(items) + footer

def notify_user(user: dict, scheme: dict) -> dict:
    from database import add_notification
    
    lang = user.get('language', 'malayalam')
    
    if lang == 'malayalam':
        message = format_scheme_notification_ml(scheme)
    else:
        message = format_scheme_notification_en(scheme)
    
    result = send_whatsapp(user['phone'], message)
    
    if result['success']:
        add_notification(
            user['user_id'],
            scheme['name'],
            format_scheme_notification_en(scheme),
            format_scheme_notification_ml(scheme)
        )
    
    return result

def notify_user_daily_digest(user: dict, schemes: list) -> dict:
    from database import add_notification
    
    if not schemes:
        return {'success': True, 'sent': 0}
    
    lang = user.get('language', 'malayalam')
    
    if lang == 'malayalam':
        message = format_daily_digest_ml(schemes)
    else:
        message = format_daily_digest_en(schemes)
    
    result = send_whatsapp(user['phone'], message)
    
    if result['success']:
        scheme_names = ", ".join([s['name'] for s in schemes[:3]])
        add_notification(
            user['user_id'],
            f"Daily Digest: {scheme_names}",
            format_daily_digest_en(schemes),
            format_daily_digest_ml(schemes)
        )
    
    return result

def broadcast_to_eligible_users(scheme: dict) -> dict:
    from database import get_all_users_for_notifications
    
    users = get_all_users_for_notifications()
    
    results = {'sent': 0, 'failed': 0, 'total': len(users)}
    
    for user in users:
        result = notify_user(user, scheme)
        if result['success']:
            results['sent'] += 1
        else:
            results['failed'] += 1
    
    logger.info(f"Broadcast complete: {results}")
    return results

def send_test_notification(phone: str) -> dict:
    test_message = """Welcome [User]!
I am your AI Panchayat Seva assistant.

✅ WhatsApp Integration Test Successful!

You will receive scheme notifications here.

💬 I will update u with new schemes!!"""
    
    return send_whatsapp(phone, test_message)

def format_eligibility_batch_ml(schemes: list) -> str:
    """Format batch eligibility notification in Malayalam (detailed format)"""
    if not schemes:
        return ""
    
    header = """🏛️ പഞ്ചായത്ത് സേവ ഏജന്റ്

🎉 നിങ്ങൾക്ക് അർഹമായ സ്കീമുകൾ കണ്ടെത്തി!

"""
    
    generic_docs = "ആധാർ, വരുമാന സർട്ടിഫിക്കറ്റ്, ബാങ്ക് അക്കൗണ്ട്, പാസ്‌പോർട്ട് ഫോട്ടോ"
    generic_criteria = "കേരള സ്വദേശി; വരുമാനം പരിശോധിക്കുക"
    
    items = []
    for i, s in enumerate(schemes, 1):
        name = s['name'][:60] if len(s['name']) > 60 else s['name']
        benefit = s.get('benefit', 'സർക്കാർ വെബ്‌സൈറ്റിൽ പരിശോധിക്കുക')
        reason = s.get('eligibility_reason', '')
        criteria = s.get('criteria_summary_ml', '') or s.get('criteria_summary_en', generic_criteria)
        
        docs = s.get('documents', '')
        if not docs or 'Check' in docs:
            docs = generic_docs
        
        portal = s.get('portal', get_portal_for_scheme(s['name']))
        
        item = f"""📌 {i}. {name}
━━━━━━━━━━━━━━━━━━━━━
💰 ഗുണഭോഗം: {benefit}"""
        
        if reason:
            item += f"\n✅ അർഹത: {reason}"
        
        item += f"""
📋 മാനദണ്ഡങ്ങൾ: {criteria}
📄 രേഖകൾ: {docs}
🔗 അപേക്ഷിക്കാൻ: {portal}"""
        
        items.append(item)
    
    footer = """
💬 കൂടുതൽ സഹായത്തിന് ഈ ചാറ്റിൽ ചോദിക്കുക!
🔄 പുതിയ സ്കീമുകൾ ലഭിക്കുമ്പോൾ ഞാൻ അറിയിക്കാം!"""
    
    return header + "\n\n".join(items) + footer

def format_eligibility_batch_en(schemes: list) -> str:
    """Format batch eligibility notification in English (detailed format)"""
    if not schemes:
        return ""
    
    header = """🏛️ Panchayat Seva Agent

🎉 You've been matched with eligible schemes!

"""
    
    generic_docs = "Aadhaar, Income certificate, Bank account, Passport photo"
    generic_criteria = "Kerala resident; Income criteria apply"
    
    items = []
    for i, s in enumerate(schemes, 1):
        name = s['name'][:60] if len(s['name']) > 60 else s['name']
        benefit = s.get('benefit', 'Check government website')
        reason = s.get('eligibility_reason', '')
        criteria = s.get('criteria_summary_en', '') or generic_criteria
        
        docs = s.get('documents', '')
        if not docs or 'Check' in docs:
            docs = generic_docs
        
        portal = s.get('portal', get_portal_for_scheme(s['name']))
        
        item = f"""📌 {i}. {name}
━━━━━━━━━━━━━━━━━━━━━
💰 Benefit: {benefit}"""
        
        if reason:
            item += f"\n✅ Why eligible: {reason}"
        
        item += f"""
📋 Criteria: {criteria}
📄 Documents: {docs}
🔗 Apply at: {portal}"""
        
        items.append(item)
    
    footer = """
💬 Reply for more help!
🔄 I'll notify you when new schemes match your profile!"""
    
    return header + "\n\n".join(items) + footer

MAX_CHARS = 1600
MAX_SCHEMES_PER_MSG = 5
MIN_SCHEMES_PER_MSG = 3

def score_scheme_for_user(scheme: dict, user: dict) -> int:
    """Score a scheme based on user profile relevance with proper disqualifiers"""
    name_lower = scheme.get('name', '').lower()
    income = user.get('income', 0)
    category = user.get('category', '')
    age = user.get('age', 0)
    marital = user.get('marital_status', '')
    house = user.get('house_ownership', '')
    vehicle = user.get('vehicle_type', 'none')
    employment = user.get('employment_status', '')
    education = user.get('education_level', '')
    
    conditions = scheme.get('conditions', {})
    
    # DISQUALIFIERS - Return -1 to exclude
    # Widow schemes - only for widowed
    if 'widow' in name_lower and marital != 'widowed':
        return -1
    
    # BPL-specific schemes - only for BPL category
    if any(x in name_lower for x in ['bpl ration', 'below poverty']):
        if category != 'BPL':
            return -1
    
    # PM Awas (housing) - only if no pucca house
    if any(x in name_lower for x in ['awas', 'housing scheme', 'pmay']):
        if house == 'owned':
            return -1
    
    # Government employee exclusion schemes
    if employment == 'govt_employee':
        # Some schemes explicitly exclude govt employees
        if any(x in name_lower for x in ['mgnrega', 'nrega', 'pmay', 'ration card']):
            # These are typically for poor/unemployed
            if income > 100000:
                return -1
    
    # 4-wheeler owners - disqualify from some poverty schemes
    if vehicle in ['four_wheeler', 'both']:
        if any(x in name_lower for x in ['bpl ration', 'below poverty', 'antyodaya']):
            return -1
    
    # SC/ST specific schemes
    if any(x in name_lower for x in ['sc stipend', 'sc scholarship', 'scheduled caste']):
        if category != 'SC':
            return -1
    if any(x in name_lower for x in ['st scholarship', 'scheduled tribe']):
        if category != 'ST':
            return -1
    
    # Disability schemes - require disability certificate
    if any(x in name_lower for x in ['disability', 'disabled', 'divyang']):
        if not user.get('has_disability_cert', False):
            return -1
    
    # BPL Ration Card - require BPL category
    if 'ration card' in name_lower:
        if 'bpl' in name_lower and category != 'BPL':
            return -1
    
    # MGNREGA - exclude elderly (manual labor not suitable)
    if any(x in name_lower for x in ['mgnrega', 'nrega', 'job card']):
        if age >= 60:
            return -1
    
    # Income too high for low-income schemes
    income_max = conditions.get('annual_income_max', 999999999)
    if income_max < 999999999 and income > income_max:
        return -1
    
    # Age requirements
    age_min = conditions.get('age_min', 0)
    if age_min > 0 and age < age_min:
        return -1
    age_max = conditions.get('age_max', 999)
    if age_max < 999 and age > age_max:
        return -1
    
    # Calculate positive score
    score = 0
    
    # Income match bonus
    if income <= 100000:
        score += 3
    elif income <= 300000:
        score += 2
    elif income <= 500000:
        score += 1
    
    # Category match
    if category == 'BPL':
        score += 2
    elif category in ['SC', 'ST']:
        score += 2
    
    # Age bonuses
    if age >= 60:
        if 'pension' in name_lower or 'senior' in name_lower or 'elderly' in name_lower:
            score += 4
        score += 1
    elif age >= 18 and education:
        if 'scholarship' in name_lower or 'student' in name_lower:
            score += 4
    
    # Marital status
    if marital == 'widowed':
        if 'widow' in name_lower:
            score += 5
    
    # Housing
    if house != 'owned':
        if 'housing' in name_lower or 'awas' in name_lower:
            score += 3
    else:
        # Has house - good for some schemes
        if 'repair' in name_lower or 'renovation' in name_lower:
            score += 2
    
    # Employment
    if employment == 'unemployed':
        if 'self employment' in name_lower or 'mgnrega' in name_lower:
            score += 3
    elif employment in ['self_employed', 'employed']:
        if 'skill' in name_lower or 'training' in name_lower:
            score += 2
    
    # Has benefit
    if scheme.get('benefit'):
        score += 1
    
    return max(score, 1)  # At least 1 point if not disqualified

def get_top_schemes_for_user(user: dict, schemes: list, limit: int = 5) -> list:
    """Get top N most relevant schemes for a user"""
    scored = []
    for scheme in schemes:
        score = score_scheme_for_user(scheme, user)
        if score > 0:
            reason = get_eligibility_reason(scheme, user)
            scheme['relevance_score'] = score
            scheme['eligibility_reason'] = reason
            scored.append((score, scheme))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s[1] for s in scored[:limit]]

def send_eligibility_batch(user: dict, schemes: list, is_new_user: bool = False) -> dict:
    """Send ONE WhatsApp message with top eligible schemes (3-5 per message)"""
    if not schemes:
        return {'success': True, 'sent': 0, 'message': 'No schemes to notify'}
    
    lang = user.get('language', 'malayalam')
    phone = user.get('phone')
    user_id = user.get('user_id')
    
    # For new users: send 3-5 top schemes
    # For daily updates: send 3-5 new schemes
    top_schemes = get_top_schemes_for_user(user, schemes, limit=5)
    
    print(f"[NOTIFIER] Sending eligibility batch ({len(top_schemes)} schemes) to {phone}")
    
    all_results = {'success': True, 'sent': 0, 'failed': 0}
    
    # Send as single batch (3-5 schemes)
    if lang == 'malayalam':
        message = format_eligibility_batch_ml(top_schemes)
    else:
        message = format_eligibility_batch_en(top_schemes)
    
    # Truncate if too long
    if len(message) > MAX_CHARS:
        top_schemes = top_schemes[:3]  # Reduce to 3 if too long
        if lang == 'malayalam':
            message = format_eligibility_batch_ml(top_schemes)
        else:
            message = format_eligibility_batch_en(top_schemes)
    
    result = send_whatsapp(phone, message)
    
    if result['success']:
        all_results['sent'] = 1
    else:
        all_results['failed'] = 1
        all_results['success'] = False
    
    if all_results['sent'] > 0:
        from database import add_notification
        scheme_names = ", ".join([s['name'] for s in top_schemes[:3]])
        
        add_notification(
            user_id,
            f"Eligible: {scheme_names}",
            format_eligibility_batch_en(top_schemes),
            format_eligibility_batch_ml(top_schemes)
        )
        print(f"[NOTIFIER] Batch notification sent successfully ({len(top_schemes)} schemes)")
    
    return all_results

def was_notified_recently(user_id: str, scheme_name: str, days: int = 30) -> bool:
    """Check if user was notified about this scheme in last N days"""
    from database import was_notified_recently as db_check
    return db_check(user_id, scheme_name, days)

if __name__ == "__main__":
    print("=== Notifier Module Test ===")
    print(f"TWILIO_ACCOUNT_SID: {'Set' if TWILIO_ACCOUNT_SID else 'Not set'}")
    print(f"TWILIO_AUTH_TOKEN: {'Set' if TWILIO_AUTH_TOKEN else 'Not set'}")
    print(f"TWILIO_WHATSAPP_FROM: {TWILIO_WHATSAPP_FROM}")
    
    test_result = send_test_notification("9876543210")
    print(f"\nTest result: {test_result}")
