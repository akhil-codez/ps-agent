import json
import os
import re

def load_rules():
    rules_path = os.path.join(os.path.dirname(__file__), 'eligibility_rules.json')
    with open(rules_path, 'r', encoding='utf-8') as f:
        return json.load(f)

RULES = load_rules()

FIELD_MAPPING = {
    'annual_income': 'income',
    'annual_turnover': 'turnover',
    'disability_percent': 'disability_percentage',
    'disability_percentage_val': 'disability_percentage',
}

EXTRA_PROFILE_FIELDS = {
    'has_pucca_house', 'owns_4_wheeler', 'government_employee',
    'receives_other_pension', 'remarried', 'has_disability_cert',
    'disability_percentage', 'is_artisan', 'is_student',
    'has_private_insurance', 'is_food_business', 'has_other_govt_scheme',
    'has_vehicle_above_4_lakh', 'is_urban', 'refuses_work'
}

def normalize_scheme_name(scheme_name: str) -> str:
    name = scheme_name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = name.replace(' ', '_')
    return name

def find_matching_scheme(scheme_name: str) -> tuple:
    normalized = normalize_scheme_name(scheme_name)
    
    if normalized in RULES:
        return normalized, RULES[normalized]
    
    name_parts = set(normalized.split('_'))
    name_parts.discard('scheme')
    name_parts.discard('certificate')
    name_parts.discard('card')
    name_parts.discard('registration')
    name_parts.discard('license')
    name_parts.discard('service')
    
    if not name_parts:
        return None, None
    
    best_match = None
    best_score = 0
    
    for key, rule in RULES.items():
        rule_name = rule['name'].lower()
        rule_parts = set(re.sub(r'[^\w\s]', '', rule_name).split())
        
        score = len(name_parts & rule_parts)
        
        if score > best_score:
            best_score = score
            best_match = (key, rule)
    
    if best_score >= 2:
        return best_match
    
    return None, None

def check_eligibility(scheme_name: str, user_profile: dict) -> dict:
    scheme_key, rule = find_matching_scheme(scheme_name)
    
    if not rule:
        return {
            'eligible': None,
            'scheme_name': scheme_name,
            'reason': 'Scheme not found in local database. Please check official website for eligibility criteria.',
            'benefit': 'N/A',
            'criteria_url': 'Visit the respective government portal for details.'
        }
    
    conditions = rule.get('conditions', {})
    disqualifiers = rule.get('disqualifiers', [])
    
    # Create derived fields from base profile
    marital = user_profile.get('marital_status', '')
    user_data = {k: v for k, v in user_profile.items() if v is not None}
    user_data['is_widowed'] = marital == 'widowed'
    user_data['remarried'] = user_profile.get('remarried', False)
    user_data['receives_other_pension'] = user_profile.get('receives_other_pension', False)
    user_data['owns_4_wheeler'] = user_profile.get('vehicle_type') in ['four_wheeler', 'both']
    user_data['has_pucca_house'] = user_profile.get('house_ownership') == 'owned'
    user_data['government_employee'] = user_profile.get('employment_status') == 'govt_employee'
    user_data['income_above_100000'] = user_profile.get('income', 0) > 100000
    user_data['income_above_300000'] = user_profile.get('income', 0) > 300000
    user_data['income_above_500000'] = user_profile.get('income', 0) > 500000
    
    for d in disqualifiers:
        if user_data.get(d, False):
            reason_text = d.replace('_', ' ')
            return {
                'eligible': False,
                'scheme_name': rule['name'],
                'reason': f'Not eligible: {reason_text}',
                'benefit': rule.get('benefit', ''),
                'criteria_url': rule.get('application_portal', '')
            }
    
    for cond, required_val in conditions.items():
        if cond.endswith('_max'):
            field = cond.replace('_max', '')
            user_val = user_data.get(field, 0)
            if user_val and user_val > required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} Rs.{user_val:,} exceeds limit Rs.{required_val:,}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', '')
                }
        
        elif cond.endswith('_min'):
            field = cond.replace('_min', '')
            user_val = user_data.get(field, 0)
            if user_val and user_val < required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} {user_val} is below minimum {required_val}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', '')
                }
        
        elif cond.endswith('_in'):
            field = cond.replace('_in', '')
            user_val = user_data.get(field, '')
            if user_val and user_val not in required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} {user_val} is not in eligible categories: {", ".join(required_val)}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', '')
                }
        
        elif isinstance(required_val, bool):
            user_val = user_data.get(cond)
            if user_val is not None and user_val != required_val:
                reason = 'required but not met' if not required_val else 'should not be true'
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'Condition not met: {cond.replace("_", " ")}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', '')
                }
    
    return {
        'eligible': True,
        'scheme_name': rule['name'],
        'reason': 'All eligibility conditions met!',
        'benefit': rule.get('benefit', ''),
        'documents_needed': rule.get('documents_needed', []),
        'application_portal': rule.get('application_portal', ''),
        'criteria_url': rule.get('application_portal', '')
    }

def check_multiple_schemes(user_profile: dict) -> list:
    results = []
    
    for scheme_key, rule in RULES.items():
        result = check_eligibility(rule['name'], user_profile)
        results.append(result)
    
    return sorted(results, key=lambda x: (x['eligible'] is not True, x['eligible']))

def get_eligible_schemes(user_profile: dict) -> list:
    all_results = check_multiple_schemes(user_profile)
    return [r for r in all_results if r['eligible'] is True]

def format_eligibility_response(result: dict) -> str:
    if result['eligible'] is None:
        return f"ℹ️ {result['scheme_name']}: {result['reason']}\n📎 {result['criteria_url']}"
    
    if result['eligible']:
        response = f"✅ **{result['scheme_name']}** - ELIGIBLE\n"
        response += f"📌 {result['reason']}\n"
        response += f"💰 Benefit: {result['benefit']}\n"
        if result.get('documents_needed'):
            response += f"📄 Documents: {', '.join(result['documents_needed'][:3])}...\n"
        if result.get('application_portal'):
            response += f"🔗 Apply: {result['application_portal']}"
        return response
    else:
        response = f"❌ **{result['scheme_name']}** - NOT ELIGIBLE\n"
        response += f"📌 Reason: {result['reason']}\n"
        if result.get('criteria_url'):
            response += f"🔗 More info: {result['criteria_url']}"
        return response

def check_eligibility_with_questions(scheme_name: str, user_profile: dict) -> dict:
    scheme_key, rule = find_matching_scheme(scheme_name)
    
    if not rule:
        return {
            'eligible': None,
            'scheme_name': scheme_name,
            'reason': 'Scheme not found in local database.',
            'benefit': 'N/A',
            'criteria_url': 'Visit the respective government portal for details.',
            'missing_fields': [],
            'needs_more_info': False
        }
    
    conditions = rule.get('conditions', {})
    disqualifiers = rule.get('disqualifiers', [])
    
    # Create derived fields
    marital = user_profile.get('marital_status', '')
    user_data = {k: v for k, v in user_profile.items() if v is not None}
    user_data['is_widowed'] = marital == 'widowed'
    user_data['remarried'] = user_profile.get('remarried', False)
    user_data['receives_other_pension'] = user_profile.get('receives_other_pension', False)
    user_data['owns_4_wheeler'] = user_profile.get('vehicle_type') in ['four_wheeler', 'both']
    user_data['has_pucca_house'] = user_profile.get('house_ownership') == 'owned'
    user_data['government_employee'] = user_profile.get('employment_status') == 'govt_employee'
    user_data['income_above_100000'] = user_profile.get('income', 0) > 100000
    user_data['income_above_300000'] = user_profile.get('income', 0) > 300000
    user_data['income_above_500000'] = user_profile.get('income', 0) > 500000
    
    questions = rule.get('missing_field_questions', {})
    
    missing_fields = []
    
    for d in disqualifiers:
        if user_data.get(d, False):
            reason_text = d.replace('_', ' ')
            return {
                'eligible': False,
                'scheme_name': rule['name'],
                'reason': f'Not eligible: {reason_text}',
                'benefit': rule.get('benefit', ''),
                'criteria_url': rule.get('application_portal', ''),
                'missing_fields': [],
                'needs_more_info': False
            }
    
    for cond, required_val in conditions.items():
        if cond.endswith('_max'):
            field = cond.replace('_max', '')
            field = FIELD_MAPPING.get(field, field)
            user_val = user_data.get(field, 0)
            if user_val and user_val > required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} Rs.{user_val:,} exceeds limit Rs.{required_val:,}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', ''),
                    'missing_fields': [],
                    'needs_more_info': False
                }
        
        elif cond.endswith('_min'):
            field = cond.replace('_min', '')
            field = FIELD_MAPPING.get(field, field)
            user_val = user_data.get(field, 0)
            if user_val and user_val < required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} {user_val} is below minimum {required_val}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', ''),
                    'missing_fields': [],
                    'needs_more_info': False
                }
        
        elif cond.endswith('_in'):
            field = cond.replace('_in', '')
            user_val = user_data.get(field, '')
            if user_val and user_val not in required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'{field.replace("_", " ").title()} {user_val} is not in eligible categories: {", ".join(required_val)}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', ''),
                    'missing_fields': [],
                    'needs_more_info': False
                }
        
        elif isinstance(required_val, bool):
            user_val = user_data.get(cond)
            if user_val is not None and user_val != required_val:
                return {
                    'eligible': False,
                    'scheme_name': rule['name'],
                    'reason': f'Condition not met: {cond.replace("_", " ")}',
                    'benefit': rule.get('benefit', ''),
                    'criteria_url': rule.get('application_portal', ''),
                    'missing_fields': [],
                    'needs_more_info': False
                }
            
            if user_val is None and cond in questions and cond in EXTRA_PROFILE_FIELDS:
                missing_fields.append({
                    'field': cond,
                    'question_en': questions[cond].get('question_en', ''),
                    'question_ml': questions[cond].get('question_ml', ''),
                    'context_en': questions[cond].get('context_en', ''),
                    'context_ml': questions[cond].get('context_ml', ''),
                    'input_type': questions[cond].get('input_type', 'yesno')
                })
    
    if missing_fields:
        return {
            'eligible': None,
            'scheme_name': rule['name'],
            'reason': 'More information needed to determine eligibility.',
            'benefit': rule.get('benefit', ''),
            'criteria_url': rule.get('application_portal', ''),
            'documents_needed': rule.get('documents_needed', []),
            'missing_fields': missing_fields,
            'needs_more_info': True
        }
    
    return {
        'eligible': True,
        'scheme_name': rule['name'],
        'reason': 'All eligibility conditions met!',
        'benefit': rule.get('benefit', ''),
        'documents_needed': rule.get('documents_needed', []),
        'application_portal': rule.get('application_portal', ''),
        'criteria_url': rule.get('application_portal', ''),
        'missing_fields': [],
        'needs_more_info': False
    }

def get_all_missing_fields_for_schemes(user_profile: dict) -> dict:
    all_missing = {}
    
    for scheme_key, rule in RULES.items():
        result = check_eligibility_with_questions(rule['name'], user_profile)
        if result.get('needs_more_info'):
            all_missing[rule['name']] = result['missing_fields']
    
    return all_missing

def reload_rules():
    """Reload eligibility rules from file"""
    global RULES
    RULES = load_rules()
    print(f"[ELIGIBILITY] Reloaded {len(RULES)} rules")

def get_all_eligible_schemes(user_profile: dict) -> list:
    """
    Get ALL schemes user is eligible for with full details.
    Returns list of scheme details for notifications.
    """
    # Create derived fields from base profile
    derived = {}
    marital = user_profile.get('marital_status', '')
    derived['is_widowed'] = marital == 'widowed'
    derived['remarried'] = user_profile.get('remarried', False)
    derived['receives_other_pension'] = user_profile.get('receives_other_pension', False)
    derived['owns_4_wheeler'] = user_profile.get('vehicle_type') in ['four_wheeler', 'both']
    derived['has_pucca_house'] = user_profile.get('house_ownership') == 'owned'
    derived['government_employee'] = user_profile.get('employment_status') == 'govt_employee'
    derived['has_disability_cert'] = user_profile.get('has_disability_cert', False)
    derived['is_student'] = user_profile.get('education_level') in ['higher_secondary', 'graduate', 'post_graduate']
    derived['has_private_insurance'] = user_profile.get('has_health_insurance', False)
    derived['is_artisan'] = user_profile.get('is_artisan', False)
    derived['is_food_business'] = user_profile.get('is_food_business', False)
    derived['income_above_100000'] = user_profile.get('income', 0) > 100000
    derived['income_above_300000'] = user_profile.get('income', 0) > 300000
    derived['income_above_500000'] = user_profile.get('income', 0) > 500000
    derived['age_below_60'] = user_profile.get('age', 0) < 60
    derived['age_below_18'] = user_profile.get('age', 0) < 18
    derived['is_urban'] = user_profile.get('is_urban', False)
    
    # Merge derived fields with user data
    user_data = {k: v for k, v in user_profile.items() if v is not None}
    user_data.update(derived)
    
    eligible = []
    
    for scheme_key, rule in RULES.items():
        conditions = rule.get('conditions', {})
        disqualifiers = rule.get('disqualifiers', [])
        
        is_eligible = True
        
        for d in disqualifiers:
            if user_data.get(d, False):
                is_eligible = False
                break
        
        if not is_eligible:
            continue
        
        for cond, required_val in conditions.items():
            if cond.endswith('_max'):
                field = cond.replace('_max', '')
                field = FIELD_MAPPING.get(field, field)
                user_val = user_data.get(field, 0)
                if user_val and user_val > required_val:
                    is_eligible = False
                    break
            
            elif cond.endswith('_min'):
                field = cond.replace('_min', '')
                field = FIELD_MAPPING.get(field, field)
                user_val = user_data.get(field, 0)
                if user_val and user_val < required_val:
                    is_eligible = False
                    break
            
            elif cond.endswith('_in'):
                field = cond.replace('_in', '')
                user_val = user_data.get(field, '')
                if user_val and user_val not in required_val:
                    is_eligible = False
                    break
            
            elif isinstance(required_val, bool):
                user_val = user_data.get(cond)
                if user_val is not None and user_val != required_val:
                    is_eligible = False
                    break
        
        if is_eligible:
            scheme_info = {
                'name': rule.get('name', scheme_key),
                'benefit': rule.get('benefit', ''),
                'criteria_summary_en': summarize_criteria_en(rule),
                'criteria_summary_ml': summarize_criteria_ml(rule),
                'documents': ', '.join(rule.get('documents_needed', [])[:5]),
                'documents_list': rule.get('documents_needed', [])[:5],
                'portal': rule.get('application_portal', 'Visit nearest office'),
            }
            eligible.append(scheme_info)
    
    return eligible

def summarize_criteria_en(rule: dict) -> str:
    """Create English criteria summary for notification"""
    parts = []
    conditions = rule.get('conditions', {})
    
    if 'annual_income_max' in conditions:
        income = conditions['annual_income_max']
        if income >= 100000:
            parts.append(f"Income below ₹{income//100000} lakh")
        else:
            parts.append(f"Income below ₹{income:,}")
    
    if 'age_min' in conditions:
        parts.append(f"Age {conditions['age_min']}+ years")
    
    if 'category_in' in conditions:
        cats = conditions['category_in']
        if len(cats) > 3:
            parts.append("All categories")
        else:
            parts.append(f"Category: {', '.join(cats)}")
    
    if conditions.get('kerala_resident'):
        parts.append("Kerala resident")
    
    if conditions.get('has_pucca_house') is False:
        parts.append("No pucca house")
    
    if conditions.get('has_bpl_card'):
        parts.append("BPL card required")
    
    return '; '.join(parts) if parts else "Check eligibility"

def summarize_criteria_ml(rule: dict) -> str:
    """Create Malayalam criteria summary for notification"""
    parts = []
    conditions = rule.get('conditions', {})
    
    if 'annual_income_max' in conditions:
        income = conditions['annual_income_max']
        if income >= 100000:
            parts.append(f"വരുമാനം ₹{income//100000} ലക്ഷത്തിൽ കുറവ്")
        else:
            parts.append(f"വരുമാനം ₹{income:,}-ൽ കുറവ്")
    
    if 'age_min' in conditions:
        parts.append(f"വയസ്സ് {conditions['age_min']}+")
    
    if 'category_in' in conditions:
        cats = conditions['category_in']
        if len(cats) > 3:
            parts.append("എല്ലാ വിഭാഗങ്ങൾക്കും")
        else:
            parts.append(f"വിഭാഗം: {', '.join(cats)}")
    
    if conditions.get('kerala_resident'):
        parts.append("കേരള സ്വദേശി")
    
    if conditions.get('has_pucca_house') is False:
        parts.append("പൂർണ്ണ വീടില്ലാത്തവർ")
    
    if conditions.get('has_bpl_card'):
        parts.append("BPL കാർഡ് ആവശ്യമാണ്")
    
    return '; '.join(parts) if parts else "അർഹത പരിശോധിക്കുക"

if __name__ == "__main__":
    test_profile = {
        'income': 80000,
        'age': 65,
        'category': 'BPL',
        'family_size': 5,
        'district': 'Thrissur',
        'has_pucca_house': False,
        'kerala_resident': True
    }
    
    print("=== Eligibility Test ===")
    schemes = ['BPL Ration Card', 'PM Awas Yojana', 'Old Age Pension', 'Karunya Health']
    for scheme in schemes:
        result = check_eligibility(scheme, test_profile)
        print(f"\n{scheme}:")
        print(format_eligibility_response(result))
