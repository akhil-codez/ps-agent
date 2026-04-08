import os
import json
import requests
from typing import Optional
from duckduckgo_search import DDGS
import memory
import eligibility

SARVAM_API_KEY = os.getenv('SARVAM_API_KEY', '')

VALID_ELIGIBILITY_FIELDS = {
    'has_pucca_house', 'owns_4_wheeler', 'government_employee',
    'receives_other_pension', 'remarried', 'has_disability_cert',
    'disability_percentage', 'is_artisan', 'is_student',
    'has_private_insurance', 'is_food_business', 'has_other_govt_scheme',
    'has_vehicle_above_4_lakh', 'is_urban', 'refuses_work'
}

def web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query + " Kerala government", max_results=5))
            if not results:
                return "No search results found."
            
            output = "Search Results:\n\n"
            for i, r in enumerate(results, 1):
                output += f"{i}. {r.get('title', 'N/A')}\n"
                output += f"   {r.get('body', 'N/A')}\n"
                if r.get('href'):
                    output += f"   Link: {r.get('href')}\n"
                output += "\n"
            return output
    except Exception as e:
        return f"Search failed: {str(e)}"

def chromadb_search(query: str, user_id: str = None) -> str:
    try:
        from chromadb_ingest import search_knowledge
        results = search_knowledge(query, n_results=3)
        
        if not results:
            return "No relevant documents found in knowledge base."
        
        output = "Relevant Government Documents:\n\n"
        for r in results:
            output += f"--- {r['id']} ---\n"
            content = r['content']
            if len(content) > 500:
                content = content[:500] + "..."
            output += content + "\n\n"
        return output
    except Exception as e:
        return f"Knowledge search failed: {str(e)}"

def get_document_checklist(service: str, subtype: str = 'default', user_id: str = None) -> str:
    service_key = service.lower().replace(' ', '_').replace('-', '_')
    
    with open('knowledge.json', 'r', encoding='utf-8') as f:
        knowledge = json.load(f)
    
    if service_key not in knowledge:
        for key, data in knowledge.items():
            if (service.lower() in data.get('name', '').lower() or
                any(service.lower() in kw.lower() for kw in data.get('keywords', []))):
                service_key = key
                break
    
    if service_key not in knowledge:
        return f"Service '{service}' not found in database. Let me search online...\n\n" + web_search(f"{service} Kerala documents required 2025")
    
    service_data = knowledge[service_key]
    subtypes = service_data.get('subtypes', {})
    
    if subtype not in subtypes:
        subtype = list(subtypes.keys())[0] if subtypes else 'default'
    
    subtype_data = subtypes.get(subtype, service_data)
    
    output = f"📋 {service_data['name']} - {subtype}\n\n"
    output += f"📄 Documents Required:\n"
    for doc in subtype_data.get('documents', []):
        output += f"   • {doc}\n"
    
    output += f"\n🏢 Office:\n   {subtype_data.get('office', 'Contact local authority')}\n"
    output += f"\n💰 Fee:\n   {subtype_data.get('fee', 'Varies')}\n"
    output += f"\n⏱️ Timeline:\n   {subtype_data.get('timeline', 'Contact office')}\n"
    
    if subtype_data.get('online_available'):
        output += f"\n🌐 Online Portal:\n   {subtype_data.get('portal_link', 'N/A')}\n"
    
    return output

def find_office(service: str, district: str = None, user_id: str = None) -> str:
    if not district and user_id:
        district = memory.get_from_memory(user_id, 'district')
    
    service_key = service.lower().replace(' ', '_').replace('-', '_')
    
    with open('knowledge.json', 'r', encoding='utf-8') as f:
        knowledge = json.load(f)
    
    if service_key not in knowledge:
        for key, data in knowledge.items():
            if (service.lower() in data.get('name', '').lower() or
                any(service.lower() in kw.lower() for kw in data.get('keywords', []))):
                service_key = key
                break
    
    if service_key in knowledge:
        service_data = knowledge[service_key]
        subtypes = service_data.get('subtypes', {})
        
        for subtype_key, subtype_data in subtypes.items():
            office = subtype_data.get('office', '')
            if district and district.lower() in office.lower():
                output = f"🏢 Government Office for {service_data['name']} in {district}:\n\n"
                output += f"Office: {office}\n"
                output += f"\n📝 Note: Contact this office for application submission.\n"
                output += f"\n💡 Tip: Visit your nearest Akshaya Centre for free application help.\n"
                return output
    
    search_query = f"{service} office {district if district else 'Kerala'} address phone hours"
    search_result = web_search(search_query)
    
    output = f"🏢 Office Information for {service}:\n\n"
    output += search_result
    output += f"\n💡 Tip: Visit akshaya.kerala.gov.in to find your nearest Akshaya Centre.\n"
    
    return output

def check_eligibility_tool(scheme_name: str, user_id: str = None) -> str:
    if not user_id:
        return "Error: User ID required for eligibility check"
    
    user_profile = memory.get_user_profile_for_eligibility(user_id)
    result = eligibility.check_eligibility_with_questions(scheme_name, user_profile)
    
    if result.get('needs_more_info'):
        first_question = result['missing_fields'][0]
        lang = memory.get_user_language(user_id)
        
        question = first_question.get(f'question_{lang}') or first_question.get('question_en', '')
        context = first_question.get(f'context_{lang}') or first_question.get('context_en', '')
        
        return f"NEED_INFO|{first_question['field']}|{first_question['input_type']}|{question}\n\n{context}"
    
    if result['eligible'] is None:
        return f"ℹ️ {result['scheme_name']}\n\n{result['reason']}\n\n🔗 {result['criteria_url']}"
    
    if result['eligible']:
        output = f"✅ ELIGIBLE for {result['scheme_name']}\n\n"
        output += f"📌 {result['reason']}\n\n"
        output += f"💰 Benefit: {result.get('benefit', 'N/A')}\n\n"
        
        if result.get('documents_needed'):
            output += f"📄 Documents Needed:\n"
            for doc in result['documents_needed'][:5]:
                output += f"   • {doc}\n"
            output += "\n"
        
        if result.get('application_portal'):
            output += f"🔗 Apply at: {result['application_portal']}\n"
        
        return output
    else:
        return f"❌ NOT ELIGIBLE for {result['scheme_name']}\n\n📌 Reason: {result['reason']}\n\n💡 Tip: Visit your nearest Akshaya Centre or check if there are other schemes you qualify for."

def save_eligibility_answer(field: str, value: str, user_id: str = None, scheme_name: str = None) -> str:
    if not user_id:
        return "Error: User ID required"
    
    if field not in VALID_ELIGIBILITY_FIELDS:
        if scheme_name:
            memory.set_last_scheme(user_id, scheme_name)
        return "INVALID_FIELD|recheck"
    
    bool_value = None
    if value.lower() in ['yes', 'y', 'അതെ', 'അതെയാണ്', 'true', '1']:
        bool_value = True
    elif value.lower() in ['no', 'n', 'അല്ല', 'അല്ലായിരുന്നു', 'false', '0']:
        bool_value = False
    
    if bool_value is None:
        try:
            bool_value = float(value) >= 40 if field == 'disability_percentage' else bool(float(value))
        except ValueError:
            return f"Error: Invalid value '{value}' for {field}"
    
    if field == 'disability_percentage':
        try:
            num_value = int(float(value))
            database.update_user_extra_profile(user_id, field, num_value)
            if scheme_name:
                memory.set_last_scheme(user_id, scheme_name)
            return f"SAVED|{field}|{num_value}"
        except ValueError:
            return f"Error: Please enter a number for disability percentage"
    
    result = memory.save_extra_profile_field(user_id, field, bool_value)
    if result.get('success'):
        if scheme_name:
            memory.set_last_scheme(user_id, scheme_name)
        return f"SAVED|{field}|{bool_value}"
    return f"Error saving {field}"

def recheck_eligibility_tool(scheme_name: str, user_id: str = None) -> str:
    return check_eligibility_tool(scheme_name, user_id)

def translate_to_malayalam(text: str) -> str:
    if not SARVAM_API_KEY:
        return text
    
    url = 'https://api.sarvam.ai/translate'
    headers = {
        'API-Subscription-Key': SARVAM_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'input': text,
        'source_language_code': 'en-IN',
        'target_language_code': 'ml-IN',
        'model': 'mayura:v1',
        'enable_preprocessing': True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get('translated_text', text)
    except Exception as e:
        pass
    
    return text

def save_to_memory_tool(key: str, value: str, user_id: str = None) -> str:
    if not user_id:
        return "Error: User ID required"
    
    result = memory.save_to_memory(user_id, key, value)
    return result

def get_from_memory_tool(key: str, user_id: str = None) -> str:
    if not user_id:
        return "Error: User ID required"
    
    result = memory.get_from_memory(user_id, key)
    if result == 'not_found':
        return f"Information about '{key}' not found in memory."
    return result

def get_user_context_tool(user_id: str = None) -> str:
    if not user_id:
        return "Error: User ID required"
    
    context = memory.get_user_context(user_id)
    if context == "No user profile found.":
        return "No profile information available."
    return f"User Profile:\n{context}"

TOOLS = {
    'web_search': {
        'func': web_search,
        'description': 'Search the internet for Kerala government service information. Use for any query not in knowledge base.',
        'parameters': {'query': 'str - search query'}
    },
    'chromadb_search': {
        'func': chromadb_search,
        'description': 'Search the local knowledge base for government services, documents, and procedures.',
        'parameters': {'query': 'str - search query'}
    },
    'get_document_checklist': {
        'func': get_document_checklist,
        'description': 'Get required documents, office, fee, and timeline for a government service.',
        'parameters': {'service': 'str - service name', 'subtype': 'str - optional service type'}
    },
    'find_office': {
        'func': find_office,
        'description': 'Find the correct government office for a service in the user district.',
        'parameters': {'service': 'str - service name', 'district': 'str - optional district'}
    },
    'check_eligibility': {
        'func': check_eligibility_tool,
        'description': 'Check if user is eligible for a government scheme. Uses user profile and may ask follow-up questions.',
        'parameters': {'scheme_name': 'str - name of the scheme'}
    },
    'save_eligibility_answer': {
        'func': save_eligibility_answer,
        'description': 'Save user answer to eligibility question. Use after check_eligibility returns NEED_INFO.',
        'parameters': {'field': 'str - field name', 'value': 'str - user answer (Yes/No or number)'}
    },
    'recheck_eligibility': {
        'func': recheck_eligibility_tool,
        'description': 'Re-check eligibility after saving answers. Use after save_eligibility_answer.',
        'parameters': {'scheme_name': 'str - name of the scheme'}
    },
    'translate_to_malayalam': {
        'func': translate_to_malayalam,
        'description': 'Translate English text to Malayalam for response.',
        'parameters': {'text': 'str - English text to translate'}
    },
    'save_to_memory': {
        'func': save_to_memory_tool,
        'description': 'Save user information to memory for future reference.',
        'parameters': {'key': 'str - information type', 'value': 'str - information value'}
    },
    'get_from_memory': {
        'func': get_from_memory_tool,
        'description': 'Retrieve saved information about the user.',
        'parameters': {'key': 'str - information type to retrieve'}
    }
}

def execute_tool(tool_name: str, parameters: dict, user_id: str = None) -> str:
    if tool_name not in TOOLS:
        return f"Error: Unknown tool '{tool_name}'"
    
    tool = TOOLS[tool_name]
    func = tool['func']
    
    params = {}
    for key, value in parameters.items():
        if value is not None and value != '':
            params[key] = value
    
    if user_id and 'user_id' in tool['parameters']:
        params['user_id'] = user_id
    
    try:
        result = func(**params)
        return str(result) if result else "Tool executed successfully"
    except TypeError as e:
        required_params = list(tool['parameters'].keys())
        return f"Error: Missing required parameters. Required: {required_params}"
    except Exception as e:
        return f"Error executing tool: {str(e)}"

if __name__ == "__main__":
    print("=== Tools Module Test ===")
    print()
    print("1. Web Search:")
    result = web_search("birth certificate Kerala")
    print(result[:200] + "...")
    print()
    print("2. Get Documents:")
    result = get_document_checklist("birth certificate", "newborn")
    print(result[:200] + "...")
    print()
    print("3. Check Eligibility:")
    result = check_eligibility_tool("BPL Ration Card")
    print(result)
    print()
    print("=== Tools module ready! ===")
