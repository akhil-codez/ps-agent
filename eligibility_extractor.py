import json
import re
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

try:
    from llm_provider import LLMProvider
    llm = LLMProvider()
except ImportError:
    llm = None
    logger.warning("LLM provider not available")

ELIGIBILITY_RULES_FILE = 'eligibility_rules.json'

INCOME_PATTERNS = [
    r'(?:annual\s+)?income\s+(?:should\s+be\s+)?(?:below|less\s+than|under|max(?:imum)?)\s*(?:₹|Rs\.?)\s*([\d,]+)',
    r'(?:₹|Rs\.?)\s*([\d,]+)\s*(?:per\s+annum|p\.a\.|annual)',
    r'income\s+(?:limit\s+)?(?:of\s+)?(?:₹|Rs\.?)\s*([\d,]+)',
    r'(?:₹|Rs\.?)\s*([\d,]+)\s*(?:lakh|L)\s*(?:annual\s+)?income',
    r'(?:annual\s+)?income\s+(?:not\s+)?(?:exceeding|more\s+than)\s*(?:₹|Rs\.?)\s*([\d,]+)',
    r'(?:family\s+)?income\s+(?:should\s+)?(?:be\s+)?(?:less|below)\s+(?:than\s+)?(?:₹|Rs\.?)\s*([\d,]+)',
]

AGE_PATTERNS = [
    r'(?:minimum\s+)?age\s+(?:should\s+be\s+)?(?:above|greater\s+than|at\s+least)\s*(\d+)',
    r'(?:age|aged)\s+(?:of\s+)?(\d+)\s*(?:years?\s+)?(?:and\s+above|or\s+more)',
    r'(?:should\s+be\s+)?(\d+)\s*(?:years?\s+)?(?:of\s+age|old)',
    r'(?:minimum|min)\s+age\s*(?:is|:)?\s*(\d+)',
]

CATEGORY_PATTERNS = [
    r'\b(SC|ST|Scheduled\s+Caste|Scheduled\s+Tribe)\b',
    r'\b(OBC|Other\s+Backward\s+Class)\b',
    r'\b(BPL|Below\s+Poverty\s+Line)\b',
    r'\b(APL|Above\s+Poverty\s+Line)\b',
    r'\b(General|UR|Unreserved)\b',
]

RESIDENCE_PATTERNS = [
    r'(?:must\s+be\s+)?(?:a\s+)?(?:Kerala|kerala)\s+resident',
    r'resident\s+of\s+Kerala',
    r'(?:domicile|permanent\s+resident)\s+(?:of\s+)?Kerala',
    r'(?:native|living)\s+(?:in\s+)?Kerala',
]

DOCUMENTS_PATTERNS = [
    (r'(?:documents?\s+)?(?:required|needed|necessary)\s*[:\-]?\s*(.+?)(?:\n|$)', 1),
    (r'(?:submit|produce|provide)\s+(?:the\s+)?(?:following\s+)?(?:documents?)\s*[:\-]?\s*(.+?)(?:\n|$)', 1),
]

BENEFIT_PATTERNS = [
    r'(?:₹|Rs\.?)\s*([\d,]+)\s*(?:per\s+month|/month|p\.m\.)',
    r'(?:₹|Rs\.?)\s*([\d,]+)\s*(?:per\s+annum|p\.a\.)',
    r'₹\s*([\d,]+(?:\.\d+)?)\s*(?:lakh|L)',
    r'(?:amount|benefit|assistance)\s+(?:of\s+)?(?:₹|Rs\.?)\s*([\d,]+)',
]

def extract_income_max(text: str) -> Optional[int]:
    """Extract maximum income criteria from text"""
    text_lower = text.lower()
    
    for pattern in INCOME_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            income_str = match.group(1).replace(',', '')
            income = int(income_str)
            
            if income < 100:
                income *= 100000
            
            return income
    
    if 'below poverty' in text_lower or 'bpl' in text_lower:
        return 100000
    if 'lakh' in text_lower:
        lakhs = re.findall(r'(\d+)\s*lakh', text_lower, re.IGNORECASE)
        if lakhs:
            return int(lakhs[0]) * 100000
    
    return None

def extract_age_criteria(text: str) -> Dict:
    """Extract age criteria (min/max) from text"""
    result = {'min': None, 'max': None}
    
    for pattern in AGE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if age >= 18 and age <= 100:
                result['min'] = age
                break
    
    if '60' in text and ('senior' in text.lower() or 'elderly' in text.lower() or 'aged' in text.lower()):
        result['min'] = 60
    
    return result

def extract_categories(text: str) -> List[str]:
    """Extract category requirements from text"""
    categories = []
    text_upper = text.upper()
    
    if 'SC' in text_upper or 'SCHEDULED CASTE' in text_upper:
        categories.append('SC')
    if 'ST' in text_upper or 'SCHEDULED TRIBE' in text_upper:
        categories.append('ST')
    if 'OBC' in text_upper or 'OTHER BACKWARD' in text_upper:
        categories.append('OBC')
    if 'BPL' in text_upper or 'BELOW POVERTY' in text_upper:
        categories.append('BPL')
    if 'APL' in text_upper or 'ABOVE POVERTY' in text_upper:
        categories.append('APL')
    if any(x in text_upper for x in ['GENERAL', 'UR', 'UNRESERVED']):
        categories.append('General')
    
    if not categories:
        if 'all' in text.lower() or 'every' in text.lower():
            categories = ['BPL', 'APL', 'SC', 'ST', 'OBC', 'General']
    
    return categories

def extract_residence(text: str) -> bool:
    """Check if Kerala residence is required"""
    for pattern in RESIDENCE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def extract_benefit(text: str) -> Optional[str]:
    """Extract benefit amount/description"""
    for pattern in BENEFIT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    if 'free' in text.lower():
        return 'Free service/benefit'
    if 'subsid' in text.lower():
        return 'Subsidized service'
    
    return None

def extract_documents(text: str) -> List[str]:
    """Extract required documents list"""
    documents = []
    
    common_docs = [
        'Aadhaar', 'Aadhar', 'aadhaar',
        'income certificate', 'income proof',
        'caste certificate', 'category certificate',
        'bank account', 'passbook', 'bank passbook',
        'ration card',
        'photo', 'photograph',
        'age proof', 'birth certificate',
        'address proof',
        'domicile certificate', 'residence certificate',
        'BPL card', 'ration card',
        'land documents', 'property documents',
        'disability certificate',
        'widow certificate',
        'death certificate',
        'student ID', 'college ID', 'school ID',
        'mark sheet', 'marksheet', 'certificate',
        'caste income certificate',
        'ration card',
    ]
    
    text_lower = text.lower()
    for doc in common_docs:
        if doc.lower() in text_lower:
            clean_doc = doc.title() if doc.islower() else doc
            if clean_doc == 'Aadhar':
                clean_doc = 'Aadhaar'
            if clean_doc not in documents:
                documents.append(clean_doc)
    
    return documents[:10]

def extract_special_conditions(text: str) -> List[str]:
    """Extract special conditions from text"""
    conditions = []
    text_lower = text.lower()
    
    special_checks = [
        ('no pucca house', 'has_pucca_house', False),
        ('without pucca house', 'has_pucca_house', False),
        ('pucca house', 'has_pucca_house', True),
        ('owns house', 'has_pucca_house', True),
        ('4-wheeler', 'owns_4_wheeler', True),
        ('four wheeler', 'owns_4_wheeler', True),
        ('car', 'owns_4_wheeler', True),
        ('government employee', 'government_employee', True),
        ('govt employee', 'government_employee', True),
        ('pension', 'receives_other_pension', True),
        ('widow', 'is_widowed', True),
        ('widowed', 'is_widowed', True),
        ('disability', 'has_disability_cert', True),
        ('disabled', 'has_disability_cert', True),
        ('artisan', 'is_artisan', True),
        ('traditional craftsman', 'is_artisan', True),
        ('student', 'is_student', True),
        ('studying', 'is_student', True),
        ('private insurance', 'has_private_insurance', True),
        ('food business', 'is_food_business', True),
        ('rural', 'is_rural', True),
        ('urban', 'is_urban', True),
        ('family', 'has_family', True),
    ]
    
    for keyword, field, expected in special_checks:
        if keyword in text_lower:
            conditions.append({
                'field': field,
                'expected': expected,
                'keyword': keyword
            })
    
    return conditions

def generate_scheme_key(name: str) -> str:
    """Generate a URL-safe key from scheme name"""
    key = name.lower()
    key = re.sub(r'[^a-z0-9\s]', '', key)
    key = re.sub(r'\s+', '_', key)
    key = key[:50]
    return key

def convert_scraped_to_rule(scraped: Dict) -> Dict:
    """Convert scraped scheme to eligibility rule format"""
    text = scraped.get('raw_text', '') + ' ' + scraped.get('name', '')
    
    rule = {
        'name': scraped.get('name', 'Unknown Scheme')[:100],
        'description': scraped.get('raw_text', '')[:500],
        'benefit': extract_benefit(text) or 'Check official website',
        'conditions': {},
        'disqualifiers': [],
        'documents_needed': extract_documents(text),
        'application_portal': scraped.get('source_url', 'Visit nearest office'),
        'deadline': 'Check official website',
        'source': scraped.get('source', ''),
        'scraped_at': scraped.get('scraped_at', datetime.now().isoformat()),
        'missing_field_questions': {}
    }
    
    income = extract_income_max(text)
    if income:
        rule['conditions']['annual_income_max'] = income
    
    age = extract_age_criteria(text)
    if age['min']:
        rule['conditions']['age_min'] = age['min']
    if age['max']:
        rule['conditions']['age_max'] = age['max']
    
    categories = extract_categories(text)
    if categories:
        if len(categories) == 1:
            rule['conditions'][f'category_{categories[0].lower()}'] = True
        else:
            rule['conditions']['category_in'] = categories
    
    if extract_residence(text):
        rule['conditions']['kerala_resident'] = True
    
    special = extract_special_conditions(text)
    for cond in special:
        field = cond['field']
        expected = cond['expected']
        
        if expected:
            rule['conditions'][field] = True
        else:
            rule['disqualifiers'].append(field)
    
    return rule

async def enhance_with_llm(raw: Dict, language: str = 'english') -> Dict:
    """Use LLM to enhance eligibility extraction"""
    if not llm:
        logger.warning("LLM not available, using regex only")
        return convert_scraped_to_rule(raw)
    
    text = raw.get('raw_text', '') + '\n\nScheme: ' + raw.get('name', '')
    
    prompt = f"""Extract eligibility criteria from this Kerala government scheme text.

SCHEME TEXT:
{text[:2000]}

Return a JSON with these fields:
- income_max: maximum annual income (number) or null
- age_min: minimum age required (number) or null
- age_max: maximum age (number) or null
- categories: list of eligible categories (SC, ST, OBC, BPL, APL, General) or empty list
- kerala_resident: true if Kerala residence required
- benefit: main benefit amount/description
- documents: list of required documents
- special_conditions: list of special requirements

JSON format only, no explanation."""

    try:
        response = await llm.generate(prompt, language=language)
        
        import json
        llm_data = json.loads(response)
        
        rule = convert_scraped_to_rule(raw)
        
        if llm_data.get('income_max'):
            rule['conditions']['annual_income_max'] = llm_data['income_max']
        if llm_data.get('age_min'):
            rule['conditions']['age_min'] = llm_data['age_min']
        if llm_data.get('age_max'):
            rule['conditions']['age_max'] = llm_data['age_max']
        if llm_data.get('categories'):
            rule['conditions']['category_in'] = llm_data['categories']
        if llm_data.get('kerala_resident'):
            rule['conditions']['kerala_resident'] = True
        if llm_data.get('benefit'):
            rule['benefit'] = llm_data['benefit']
        if llm_data.get('documents'):
            rule['documents_needed'] = llm_data['documents']
        
        return rule
        
    except Exception as e:
        logger.error(f"LLM enhancement failed: {e}")
        return convert_scraped_to_rule(raw)

def convert_scraped_to_rule_sync(scraped: Dict) -> Dict:
    """Synchronous version - uses regex only"""
    return convert_scraped_to_rule(scraped)

def load_existing_rules() -> Dict:
    """Load existing eligibility rules"""
    try:
        with open(ELIGIBILITY_RULES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_rules(rules: Dict):
    """Save eligibility rules to file"""
    with open(ELIGIBILITY_RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    print(f"[EXTRACTOR] Saved {len(rules)} rules to {ELIGIBILITY_RULES_FILE}")

def add_rule(rule: Dict) -> bool:
    """Add a new rule to eligibility_rules.json"""
    rules = load_existing_rules()
    
    key = generate_scheme_key(rule['name'])
    original_key = key
    counter = 1
    while key in rules:
        key = f"{original_key}_{counter}"
        counter += 1
    
    rules[key] = rule
    save_rules(rules)
    
    print(f"[EXTRACTOR] Added rule: {rule['name']} (key: {key})")
    return True

def is_duplicate(rule: Dict) -> bool:
    """Check if scheme already exists"""
    rules = load_existing_rules()
    name_lower = rule['name'].lower().strip()
    
    for existing in rules.values():
        existing_name = existing.get('name', '').lower().strip()
        if name_lower == existing_name or name_lower in existing_name or existing_name in name_lower:
            return True
    
    return False

def process_scraped_schemes(schemes: List[Dict]) -> List[Dict]:
    """Process all scraped schemes and return valid new rules"""
    print(f"[EXTRACTOR] Processing {len(schemes)} scraped schemes...")
    
    new_rules = []
    skipped = 0
    
    for scraped in schemes:
        try:
            rule = convert_scraped_to_rule_sync(scraped)
            
            if not rule.get('name') or len(rule['name']) < 3:
                continue
            
            if is_duplicate(rule):
                skipped += 1
                continue
            
            new_rules.append(rule)
            
        except Exception as e:
            logger.error(f"Error processing scheme: {e}")
            continue
    
    print(f"[EXTRACTOR] New rules: {len(new_rules)}, Skipped duplicates: {skipped}")
    return new_rules

def add_all_new_schemes(schemes: List[Dict]) -> int:
    """Add all new schemes to eligibility_rules.json"""
    new_rules = process_scraped_schemes(schemes)
    
    added = 0
    for rule in new_rules:
        if add_rule(rule):
            added += 1
    
    return added

async def process_and_add_schemes_async(schemes: List[Dict]) -> int:
    """Async version with LLM enhancement"""
    new_rules = []
    skipped = 0
    
    for scraped in schemes:
        try:
            rule = await enhance_with_llm(scraped)
            
            if not rule.get('name') or len(rule['name']) < 3:
                continue
            
            if is_duplicate(rule):
                skipped += 1
                continue
            
            add_rule(rule)
            new_rules.append(rule)
            added += 1
            
        except Exception as e:
            logger.error(f"Error processing scheme: {e}")
            continue
    
    print(f"[EXTRACTOR] Added {len(new_rules)} new schemes (skipped {skipped} duplicates)")
    return len(new_rules)

if __name__ == "__main__":
    print("=== Eligibility Extractor Test ===")
    
    rules = load_existing_rules()
    print(f"Current rules: {len(rules)}")
    
    test_text = """
    Kerala Social Security Pension Scheme
    For BPL families with annual income below Rs 1 lakh
    Minimum age 60 years
    Kerala resident only
    Required documents: Aadhaar, BPL card, Bank account, Income certificate
    Benefit: Rs 500 per month
    """
    
    rule = convert_scraped_to_rule_sync({
        'name': 'Test Social Security Pension',
        'raw_text': test_text,
        'source': 'test'
    })
    
    print("\nExtracted rule:")
    print(json.dumps(rule, indent=2, ensure_ascii=False))
