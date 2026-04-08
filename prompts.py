SYSTEM_PROMPT = '''You are Panchayat Seva Agent - an expert AI assistant for Kerala government services.

Your role:
- Help citizens understand and apply for government services and schemes
- Answer questions about documents, offices, fees, timelines
- Check eligibility for welfare schemes using the check_eligibility tool
- Always be helpful, patient, and clear

Important rules:
1. ALWAYS use check_eligibility tool for any scheme eligibility question - NEVER guess
2. ALWAYS call get_from_memory first to know the user's profile before asking questions
3. ALWAYS use translate_to_malayalam as your final step if user's language is Malayalam
4. NEVER make up information - use web_search or knowledge.json for accurate data
5. If a service is not in knowledge.json, use web_search to find information
6. Always suggest visiting nearest Akshaya Centre for help with applications

User profile context will be provided. Use this to provide personalized responses.

Response format:
- Be clear and structured
- Use bullet points for documents
- Include office addresses, fees, timelines
- End with encouraging message'''

REACT_FORMAT = '''Follow the ReAct format:
- Think about what you need to do
- Take action by calling appropriate tool
- Observe the result
- Continue until you have complete answer
- End with Final Answer

Available tools:
- web_search: Search internet for government service information
- chromadb_search: Search local knowledge base
- get_document_checklist: Get documents for known services
- find_office: Find correct government office
- check_eligibility: Check scheme eligibility (ALWAYS use this for eligibility questions)
- translate_to_malayalam: Translate response to Malayalam
- save_to_memory: Save user information
- get_from_memory: Get stored user information'''

MALAYALAM_GREETINGS = [
    "Namaskaram! Njan Panchayat Seva Agent. Ningalku enthu sahaayam vendum?",
    "Namaste! Welcome to Panchayat Seva Agent. How can I help you today?",
    "Hello! Njan ninnakku government services-il sahayam cheyyan undakkuka. Enthu vendum?"
]

ONBOARDING_SCRIPT = [
    {
        "question": "Namaskaram! Ente peru Panchayat Seva Agent. Ningalku enthu sahaayam vendum?",
        "context": "Introduction and welcome message"
    },
    {
        "question": "Njan ninnakayi sheri aaya office kaaNicchu tharaan. Ningal ethu jillayilaanu?",
        "context": "Ask for district if not known"
    },
    {
        "question": "Ningalude pera enthu? Ellaa communications-um personalized aakkaan.",
        "context": "Confirm or ask for name if not known"
    },
    {
        "question": "Sarkaar schemes eligibility check cheyyaan - kudum-batthile aaLukaL ethra?",
        "context": "Confirm family size for scheme eligibility"
    }
]

ENGLISH_GREETINGS = [
    "Namaste! Welcome to Panchayat Seva Agent. How can I help you today?",
    "Hello! I'm here to help with Kerala government services. What do you need?",
    "Welcome! Ask me about government services, schemes, documents, and more."
]

def get_greeting(language: str = 'malayalam') -> str:
    if language == 'malayalam':
        return MALAYALAM_GREETINGS[0]
    return ENGLISH_GREETINGS[0]

def build_context_prompt(user_context: str) -> str:
    if not user_context or user_context == "No user profile found.":
        return ""
    return f"\n\nUser Profile Context:\n{user_context}\n\nUse this context to provide personalized responses."

def build_service_prompt(service_type: str = 'general') -> str:
    base = SYSTEM_PROMPT
    
    if service_type == 'eligibility':
        base += "\n\nIMPORTANT: For eligibility checks, you MUST use the check_eligibility tool."
        base += " Pass the scheme name and user profile to get accurate eligibility status."
    
    elif service_type == 'documents':
        base += "\n\nIMPORTANT: For document requests, use get_document_checklist tool."
        base += " Provide service name and subtype if available."
    
    elif service_type == 'office':
        base += "\n\nIMPORTANT: For office queries, use find_office tool."
        base += " Include district from user profile if available."
    
    return base

def get_fallback_response(service_name: str) -> str:
    return f"""I don't have detailed information about {service_name} in my knowledge base.

Here is what I can help with:
- Search online for latest information
- Check eligibility for known schemes
- Guide you to the correct government office

Would you like me to search online for {service_name} information?"""

def get_office_not_found_response() -> str:
    return """I couldn't find the specific office information.

Suggestions:
- Visit your nearest Akshaya Centre for help
- Check kerala.gov.in for office directories
- Call the district collectorate for assistance

Would you like me to help with something else?"""

def get_eligibility_error_response() -> str:
    return """I couldn't complete the eligibility check.

Possible reasons:
- Scheme not found in database
- Missing user profile information
- Technical error

Please provide more details or ask about a specific scheme."""

HELPFUL_TIPS = [
    "Tip: Keep your Aadhaar, Ration Card, and Bank Account details ready for most applications.",
    "Tip: Visit your nearest Akshaya Centre - they help with government applications for free!",
    "Tip: Many services can be applied online at ecitizen.gov.in or keralaplus.kerala.gov.in",
    "Tip: Start applications early - government processes can take 15-60 days.",
    "Tip: Keep copies of all documents - you'll need them for multiple services."
]

def get_random_tip() -> str:
    import random
    return random.choice(HELPFUL_TIPS)

CLOSING_MESSAGES = {
    'malayalam': "Ningalude doubt-il ente saadhanamundi. Enthu venam boothamaanikkum!",
    'english': "Is there anything else I can help you with today?"
}

def get_closing_message(language: str = 'malayalam') -> str:
    msg = CLOSING_MESSAGES.get(language, CLOSING_MESSAGES['english'])
    tip = get_random_tip()
    return f"{msg}\n\n{tip}"

if __name__ == "__main__":
    print("=== Prompts Module Test ===")
    print(f"Greeting (ML): {get_greeting('malayalam')}")
    print(f"Greeting (EN): {get_greeting('english')}")
    print(f"\nRandom tip: {get_random_tip()}")
    print(f"\nClosing (ML): {get_closing_message('malayalam')}")
    print(f"\nClosing (EN): {get_closing_message('english')}")
    print("\nPrompts module ready!")
