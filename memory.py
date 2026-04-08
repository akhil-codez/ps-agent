import database
from typing import Optional, Dict, Any

class SessionMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._memory: Dict[str, str] = {}
        self._profile: Optional[Dict] = None
        self._loaded = False
        self._last_scheme: str = ""
    
    def load_from_db(self) -> None:
        if self._loaded:
            return
        
        profile = database.get_user_profile(self.user_id)
        if profile:
            self._profile = profile
            for key in ['name', 'district', 'category', 'income', 'age', 
                       'family_size', 'language', 'phone']:
                if key in profile and profile[key] is not None:
                    self._memory[key] = str(profile[key])
        
        self._loaded = True
    
    def save_to_db(self, key: str, value: str) -> bool:
        self._memory[key] = value
        
        if key in ['name', 'district', 'category', 'language', 'notify']:
            profile_updates = {key: value}
            database.update_user_profile(self.user_id, profile_updates)
            return True
        
        return False
    
    def get(self, key: str) -> str:
        self.load_from_db()
        return self._memory.get(key, 'not_found')
    
    def set(self, key: str, value: str) -> str:
        self._memory[key] = value
        self.save_to_db(key, value)
        return f'Saved: {key} = {value}'
    
    def get_profile(self) -> Dict[str, Any]:
        self.load_from_db()
        return self._profile or {}
    
    def get_profile_for_eligibility(self) -> Dict[str, Any]:
        profile = self.get_profile()
        
        if not profile:
            return {}
        
        extra_profile = database.get_all_extra_profile_fields(self.user_id)
        
        house_ownership = extra_profile.get('house_ownership', '')
        vehicle_type = extra_profile.get('vehicle_type', 'none')
        marital_status = extra_profile.get('marital_status', '')
        employment_status = extra_profile.get('employment_status', '')
        education_level = extra_profile.get('education_level', '')
        is_urban = extra_profile.get('is_urban', False)
        has_health_insurance = extra_profile.get('has_health_insurance', False)
        has_life_insurance = extra_profile.get('has_life_insurance', False)
        
        profile_dict = {
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
            'willing_for_manual_work': True,
            'has_family': True,
            'refuses_work': False,
            'not_kerala_resident': False,
            'category_general': profile.get('category') not in ['SC', 'ST', 'OBC'],
            'not_sc_st': profile.get('category') not in ['SC', 'ST'],
            'has_apl_card': profile.get('category') == 'General',
            'income_above_100000': profile.get('income', 0) > 100000,
            'income_above_300000': profile.get('income', 0) > 300000,
            'income_above_500000': profile.get('income', 0) > 500000,
            'income_above_250000': profile.get('income', 0) > 250000,
            'age_below_60': profile.get('age', 0) < 60,
            'age_below_18': profile.get('age', 0) < 18,
            'not_artisan': True,
            'is_artisan': False,
            'is_student': education_level in ['higher_secondary', 'graduate', 'post_graduate'],
            'is_widowed': marital_status == 'widowed',
            'is_urban': is_urban,
            'has_pucca_house': house_ownership == 'owned',
            'owns_4_wheeler': vehicle_type in ['four_wheeler', 'both'],
            'government_employee': employment_status == 'govt_employee',
            'has_private_insurance': has_health_insurance,
            'receives_other_pension': False,
            'remarried': False,
        }
        
        profile_dict.update(extra_profile)
        
        return profile_dict
    
    def get_conversation_context(self) -> str:
        self.load_from_db()
        
        if not self._profile:
            return "No user profile found. Please ask for basic information."
        
        context_parts = []
        
        if self._profile.get('name'):
            context_parts.append(f"User name: {self._profile['name']}")
        
        if self._profile.get('district'):
            context_parts.append(f"District: {self._profile['district']}")
        
        if self._profile.get('category'):
            context_parts.append(f"Category: {self._profile['category']}")
        
        if self._profile.get('income'):
            context_parts.append(f"Annual income: Rs.{self._profile['income']:,}")
        
        if self._profile.get('age'):
            context_parts.append(f"Age: {self._profile['age']}")
        
        if self._profile.get('family_size'):
            context_parts.append(f"Family size: {self._profile['family_size']}")
        
        if self._profile.get('language'):
            context_parts.append(f"Preferred language: {self._profile['language']}")
        
        return ", ".join(context_parts)

_session_instances: Dict[str, SessionMemory] = {}

def get_memory(user_id: str) -> SessionMemory:
    if user_id not in _session_instances:
        _session_instances[user_id] = SessionMemory(user_id)
    return _session_instances[user_id]

def save_to_memory(user_id: str, key: str, value: str) -> str:
    memory = get_memory(user_id)
    return memory.set(key, value)

def get_from_memory(user_id: str, key: str) -> str:
    memory = get_memory(user_id)
    return memory.get(key)

def get_user_context(user_id: str) -> str:
    memory = get_memory(user_id)
    return memory.get_conversation_context()

def get_user_profile_for_eligibility(user_id: str) -> Dict[str, Any]:
    memory = get_memory(user_id)
    return memory.get_profile_for_eligibility()

def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    return database.get_user_profile(user_id)

def save_extra_profile_field(user_id: str, field: str, value) -> dict:
    return database.update_user_extra_profile(user_id, field, value)

def get_user_language(user_id: str) -> str:
    profile = get_user_profile(user_id)
    if profile:
        return profile.get('language', 'malayalam')
    return 'malayalam'

def get_all_missing_fields(user_id: str) -> dict:
    profile = get_profile_for_eligibility(user_id)
    if not profile:
        return {}
    
    from eligibility import get_all_missing_fields_for_schemes
    return get_all_missing_fields_for_schemes(profile)

def set_last_scheme(user_id: str, scheme_name: str):
    memory = get_memory(user_id)
    memory._last_scheme = scheme_name

def get_last_scheme(user_id: str) -> str:
    memory = get_memory(user_id)
    return memory._last_scheme

if __name__ == "__main__":
    print("=== Memory Module Test ===")
    
    test_profile = {
        'income': 80000,
        'age': 65,
        'category': 'BPL',
        'family_size': 5,
        'district': 'Thrissur'
    }
    
    print(f"Test profile: {test_profile}")
    print("\nMemory module ready!")
