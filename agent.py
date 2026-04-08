import os
from dotenv import load_dotenv
load_dotenv()

import json
import re
import logging

import tools
import memory
import prompts
from llm_provider import get_llm_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_agent_response(text: str) -> str:
    text = re.sub(r'\(save_eligibility_answer:.*?\)', '', text)
    text = re.sub(r'\(recheck_eligibility:.*?\)', '', text)
    text = re.sub(r'\(check_eligibility:.*?\)', '', text)
    text = re.sub(r'\[Function Result\]:.*?(?=\n|$)', '', text)
    text = re.sub(r'\(System:.*?\)', '', text)
    text = re.sub(r'Let me check.*?\.', '', text)
    text = re.sub(r'I\'ll save your answer.*?\.', '', text)
    text = re.sub(r'After re-checking.*?\.', '', text)
    text = re.sub(r'To check your eligibility accurately, I need one more piece of information:', 'To check eligibility, I need to ask:', text)
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text

def get_user_language(user_id: str) -> str:
    profile = memory.get_user_profile(user_id)
    if profile:
        return profile.get('language', 'malayalam')
    return 'malayalam'

def get_user_context(user_id: str) -> str:
    profile = memory.get_user_profile(user_id)
    if not profile:
        return "No user profile available."
    
    context = []
    if profile.get('name'):
        context.append(f"Name: {profile['name']}")
    if profile.get('district'):
        context.append(f"District: {profile['district']}")
    if profile.get('category'):
        context.append(f"Category: {profile['category']}")
    if profile.get('income'):
        context.append(f"Annual Income: Rs.{profile['income']:,}")
    if profile.get('age'):
        context.append(f"Age: {profile['age']}")
    if profile.get('family_size'):
        context.append(f"Family Size: {profile['family_size']}")
    if profile.get('language'):
        context.append(f"Preferred Language: {profile['language']}")
    
    return ", ".join(context)

SYSTEM_PROMPT = '''You are Panchayat Seva Agent - Kerala's friendly government services helper.

Your role:
- Help Kerala citizens understand and apply for government services and welfare schemes
- Answer questions about documents, offices, fees, and timelines in a friendly way
- Check eligibility for welfare schemes
- Be warm, patient, and genuinely helpful

IMPORTANT RULES:
1. For eligibility questions, use the check_eligibility function
2. For document questions, use the get_document_checklist function
3. For unknown services, use web_search function
4. NEVER make up information
5. Include office addresses and portal links when available

ELIGIBILITY CHECK FLOW (CRITICAL):
When check_eligibility returns "NEED_INFO|field|type|question":
1. Display the question to user in a friendly way
2. Wait for their response (Yes/No or number)
3. After user responds, use save_eligibility_answer(field, value) to save their answer
4. Then use recheck_eligibility to get the final result
5. Present the eligibility result to user

Example conversation:
User: "Am I eligible for PM Awas?"
Agent: (calls check_eligibility)
System: "NEED_INFO|has_pucca_house|yesno|Do you own a pucca house?"
Agent: "To check your eligibility accurately, I need one more piece of information: Do you own a pucca house (permanent concrete house)? This is required because PM Awas Yojana is only for those without a permanent house."
User: "No"
Agent: (calls save_eligibility_answer with has_pucca_house=No)
Agent: (calls recheck_eligibility)
Agent: "Great news! You are eligible for PM Awas Yojana Gramin!..."

You have access to these functions:
- check_eligibility(scheme_name): Check if user is eligible for a scheme
- save_eligibility_answer(field, value): Save user's answer to eligibility question (use Yes/No or number)
- recheck_eligibility(scheme_name): Re-check eligibility after saving answers
- get_document_checklist(service_name, subtype): Get required documents
- find_office(service_name, district): Find the correct government office
- web_search(query): Search internet for information
- chromadb_search(query): Search local knowledge base
- translate_to_malayalam(text): Translate to Malayalam
- save_to_memory(key, value): Save user information
- get_from_memory(key): Get saved information

RESPONSE STYLE GUIDE:
- Write in simple English that translates well to Malayalam
- Mix English and Malayalam naturally (20-30% English words is good)
- Keep these terms in English (they translate better this way):
  * Government terms: Government, Certificate, Application, Office, Service, Scheme, Benefit
  * Personal docs: Aadhaar, Voter ID, Ration Card, PAN Card, Bank Account, Passport
  * Categories: BPL, APL, SC, ST, OBC, General, Below Poverty Line
  * Places: Akshaya Centre, Panchayat, Taluk Office, District Office, Collectorate
  * Actions: Apply, Submit, Register, Download, Upload, Pay, Book Appointment

RESPONSE FORMAT:
[Brief response to the user's question]

[Service Name]:
- Required document 1
- Required document 2

Office: [Location name]
Fee: [Amount] INR
Time needed: [Duration]

Important tip: [Helpful advice about Akshaya Centre or online options]

Need more help? Ask me anything!

Remember:
- Use short paragraphs (2-3 sentences max)
- Keep a friendly, helpful tone
- Be specific with fees and timelines
- Always suggest Akshaya Centre for free help'''

def call_function(name: str, args: dict, user_id: str) -> str:
    try:
        if name == 'check_eligibility':
            scheme_name = args.get('scheme_name', '')
            memory.set_last_scheme(user_id, scheme_name)
            result = tools.check_eligibility_tool(scheme_name, user_id)
            if result.startswith('NEED_INFO|'):
                return result
            return result
        elif name == 'save_eligibility_answer':
            field = args.get('field', '')
            value = args.get('value', '')
            scheme_name = memory.get_last_scheme(user_id)
            result = tools.save_eligibility_answer(field, value, user_id, scheme_name)
            if result.startswith('INVALID_FIELD|'):
                rechk_result = tools.recheck_eligibility_tool(scheme_name, user_id)
                return rechk_result
            return result
        elif name == 'recheck_eligibility':
            scheme_name = args.get('scheme_name', '') or memory.get_last_scheme(user_id)
            return tools.recheck_eligibility_tool(scheme_name, user_id)
        elif name == 'get_document_checklist':
            return tools.get_document_checklist(
                args.get('service_name', ''),
                args.get('subtype', 'default'),
                user_id
            )
        elif name == 'find_office':
            return tools.find_office(
                args.get('service_name', ''),
                args.get('district', ''),
                user_id
            )
        elif name == 'web_search':
            return tools.web_search(args.get('query', ''))
        elif name == 'chromadb_search':
            return tools.chromadb_search(args.get('query', ''), user_id)
        elif name == 'translate_to_malayalam':
            return tools.translate_to_malayalam(args.get('text', ''))
        elif name == 'save_to_memory':
            key_val = args.get('key_value', '')
            if '|' in key_val:
                key, val = key_val.split('|', 1)
                return tools.save_to_memory_tool(key.strip(), val.strip(), user_id)
            return "Error: Use format 'key|value'"
        elif name == 'get_from_memory':
            return tools.get_from_memory_tool(args.get('key', ''), user_id)
        else:
            return f"Unknown function: {name}"
    except Exception as e:
        return f"Error calling {name}: {str(e)}"

def process_message(user_id: str, message: str, is_first: bool = False) -> str:
    try:
        user_context = get_user_context(user_id)
        user_lang = get_user_language(user_id)
        
        context = f"User Profile: {user_context}\n\n" if user_context != "No user profile available." else ""
        
        greeting_note = ""
        if is_first:
            greeting_note = "[GREETING REQUIRED] Start with a warm greeting addressing the user by name if available. "
        else:
            greeting_note = "[NO GREETING] Directly answer the user's question without greeting. "
        
        full_prompt = f'''{SYSTEM_PROMPT}

{greeting_note}{context}
User Question: {message}

Provide a helpful, structured response with relevant government service information.
'''
        
        response_text = get_llm_provider().generate(full_prompt, language=user_lang)
        
        if '```json' in response_text:
            try:
                import re
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    func_data = json.loads(json_match.group(1))
                    func_name = func_data.get('function')
                    func_args = func_data.get('arguments', {})
                    
                    if func_name and func_args:
                        result = call_function(func_name, func_args, user_id)
                        
                        if result.startswith('NEED_INFO|'):
                            parts = result.split('|', 4)
                            if len(parts) >= 5:
                                question = parts[4].split('\n')[0]
                                response_text = question
                            else:
                                response_text = result
                        else:
                            full_prompt += f"\n\n[Function Result]: {result}\n\nBased on this information, provide your final response:"
                            response_text = get_llm_provider().generate(full_prompt, language=user_lang)
            except:
                pass
        
        response_text = clean_agent_response(response_text)
        
        if user_lang == 'malayalam' and not any('\u0d15' <= c <= '\u0d46' for c in response_text[:100]):
            try:
                ml_response = tools.translate_to_malayalam(response_text)
                if ml_response and ml_response != response_text:
                    return ml_response
            except Exception as trans_err:
                logger.warning(f"Sarvam fallback failed: {trans_err}")
        
        return response_text
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"I encountered an error: {str(e)}\n\nPlease try again."

def simple_process_message(user_id: str, message: str, is_first: bool = False) -> str:
    try:
        user_context = get_user_context(user_id)
        user_lang = get_user_language(user_id)
        
        context = f"User Profile: {user_context}\n\n" if user_context != "No user profile available." else ""
        
        greeting_note = ""
        if is_first:
            greeting_note = "[GREETING REQUIRED] Start with a warm greeting addressing the user by name if available. "
        else:
            greeting_note = "[NO GREETING] Directly answer the user's question without greeting. "
        
        full_prompt = f'''{SYSTEM_PROMPT}

{greeting_note}{context}
User Question: {message}

Provide a helpful, structured response with relevant government service information.
'''
        
        response_text = get_llm_provider().generate(full_prompt, language=user_lang)
        
        if user_lang == 'malayalam' and not any('\u0d15' <= c <= '\u0d46' for c in response_text[:100]):
            try:
                ml_response = tools.translate_to_malayalam(response_text)
                if ml_response and ml_response != response_text:
                    return clean_agent_response(ml_response)
            except Exception as trans_err:
                logger.warning(f"Sarvam fallback failed: {trans_err}")
        
        return clean_agent_response(response_text)
        
    except Exception as e:
        logger.error(f"Agent error: {e}")
        return f"I encountered an error: {str(e)}\n\nPlease try again."

if __name__ == "__main__":
    print("=== Agent Module Ready ===")
    print()
    
    # Show LLM provider status
    status = get_llm_provider().get_status()
    print("LLM Provider Status:")
    gemini_status = "[OK]" if status['gemini']['configured'] else "[X]"
    groq_status = "[OK]" if status['groq']['configured'] else "[X]"
    print(f"  Gemini: {gemini_status} Available" if status['gemini']['configured'] else f"  Gemini: {gemini_status} Not configured")
    print(f"  Groq:   {groq_status} ({status['groq']['model']})")
    print()
    print("Fallback: Gemini -> Groq (automatic on quota error)")
    print()
    print("Usage:")
    print("  from agent import process_message, simple_process_message")
    print()
    print("  response = simple_process_message(user_id, 'your question')")
