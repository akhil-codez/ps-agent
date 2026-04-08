import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import database
import auth
import agent
import memory

app = FastAPI(
    title="Panchayat Seva Agent API",
    description="Backend API for Kerala Government Services AI Assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ps-agent.vercel.app",
        "https://ps-agent-api.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    phone: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    district: str
    category: str
    income: int
    age: int
    family_size: int
    language: str = "malayalam"

class ChatRequest(BaseModel):
    user_id: str
    message: str
    is_first: bool = False

class ProfileUpdateRequest(BaseModel):
    user_id: str
    updates: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Panchayat Seva Agent API", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "panchayat-seva-agent"}

class LoginResponse(BaseModel):
    success: bool
    user_id: Optional[str] = None
    profile: Optional[Dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    result = auth.login_user(request.phone, request.password)
    return LoginResponse(**result)

class RegisterResponse(BaseModel):
    success: bool
    user_id: Optional[str] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None

@app.post("/auth/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    result = auth.register_user(request.dict())
    if result['success']:
        return RegisterResponse(
            success=True,
            user_id=result['user_id'],
            message=result['message']
        )
    return RegisterResponse(
        success=False,
        errors=result.get('errors', ['Registration failed'])
    )

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    profile = database.get_user_full_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "profile": profile}

@app.put("/profile/{user_id}")
async def update_profile(user_id: str, request: ProfileUpdateRequest):
    basic_fields = ['name', 'district', 'category', 'income', 'age', 'family_size', 'language', 'notify']
    
    basic_updates = {k: v for k, v in request.updates.items() if k in basic_fields}
    extra_updates = {k: v for k, v in request.updates.items() if k not in basic_fields}
    
    if basic_updates:
        database.update_user_profile(user_id, basic_updates)
    
    for field, value in extra_updates.items():
        database.update_user_extra_profile(user_id, field, value)
    
    return {"success": True, "message": "Profile updated"}

@app.post("/profile/{user_id}/extra")
async def update_extra_profile(user_id: str, request: ProfileUpdateRequest):
    """Update only extra profile fields"""
    profile = database.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in request.updates.items():
        database.update_user_extra_profile(user_id, field, value)
    
    return {"success": True, "message": "Extra profile updated"}

class ChatResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        profile = database.get_user_profile(request.user_id)
        if not profile:
            return ChatResponse(
                success=False,
                error="User not found. Please login again."
            )
        
        response = agent.process_message(request.user_id, request.message, request.is_first)
        
        return ChatResponse(success=True, response=response)
    
    except Exception as e:
        return ChatResponse(success=False, error=str(e))

@app.get("/notifications/{user_id}")
async def get_notifications(user_id: str):
    notifications = database.get_unread_notifications(user_id)
    return {"success": True, "notifications": notifications}

@app.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    database.mark_notification_read(notification_id)
    return {"success": True}

@app.get("/schemes/eligible/{user_id}")
async def get_eligible_schemes(user_id: str):
    from eligibility import check_eligibility_with_questions, RULES
    
    profile = database.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    eligibility_profile = memory.get_user_profile_for_eligibility(user_id)
    
    eligible = []
    not_eligible = []
    needs_info = []
    
    for scheme_key, rule in RULES.items():
        result = check_eligibility_with_questions(rule['name'], eligibility_profile)
        
        if result['eligible'] is True:
            eligible.append({
                'scheme_name': result['scheme_name'],
                'eligible': True,
                'reason': result.get('reason', ''),
                'benefit': result.get('benefit', '')
            })
        elif result['eligible'] is False:
            not_eligible.append({
                'scheme_name': result['scheme_name'],
                'eligible': False,
                'reason': result.get('reason', '')
            })
        else:
            needs_info.append({
                'scheme_name': result['scheme_name'],
                'eligible': None,
                'reason': result.get('reason', ''),
                'missing_fields': result.get('missing_fields', [])
            })
    
    return {
        "success": True,
        "eligible_schemes": eligible,
        "not_eligible_schemes": not_eligible,
        "unknown_schemes": needs_info,
        "total_schemes": len(RULES)
    }

@app.get("/schemes/missing-fields/{user_id}")
async def get_missing_eligibility_fields(user_id: str):
    profile = database.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    missing = memory.get_all_missing_fields(user_id)
    
    all_missing = []
    for scheme_name, fields in missing.items():
        for field in fields:
            all_missing.append({
                'scheme': scheme_name,
                'field': field['field'],
                'question_en': field.get('question_en', ''),
                'question_ml': field.get('question_ml', ''),
                'input_type': field.get('input_type', 'yesno')
            })
    
    return {
        "success": True,
        "missing_fields": all_missing,
        "total_missing": len(all_missing)
    }

@app.get("/services")
async def get_services():
    import json
    
    with open('knowledge.json', 'r', encoding='utf-8') as f:
        knowledge = json.load(f)
    
    services = []
    for key, data in knowledge.items():
        services.append({
            "key": key,
            "name": data.get("name"),
            "description": data.get("description"),
            "subtypes": list(data.get("subtypes", {}).keys())
        })
    
    return {"success": True, "services": services}

class SaveEligibilityAnswerRequest(BaseModel):
    user_id: str
    field: str
    value: str

@app.post("/eligibility/save-answer")
async def save_eligibility_answer(request: SaveEligibilityAnswerRequest):
    result = memory.save_extra_profile_field(request.user_id, request.field, request.value)
    return result

@app.post("/notifications/broadcast/{scheme_name}")
async def broadcast_scheme_notification(scheme_name: str):
    """Send notification to all eligible users about a scheme"""
    from eligibility import RULES
    
    scheme_key = scheme_name.lower().replace(' ', '_').replace('-', '_')
    
    if scheme_key not in RULES:
        return {"success": False, "error": "Scheme not found"}
    
    rule = RULES[scheme_key]
    scheme = {
        'name': rule['name'],
        'benefit': rule.get('benefit', ''),
        'portal': rule.get('application_portal', ''),
        'description': rule.get('description', ''),
    }
    
    import notifier
    result = notifier.broadcast_to_eligible_users(scheme)
    return {"success": True, "scheme": scheme['name'], **result}

@app.post("/notifications/broadcast-all")
async def broadcast_all_schemes():
    """Send notification to all eligible users about ALL schemes"""
    try:
        from notification_scheduler import trigger_broadcast_all
        result = trigger_broadcast_all()
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/notifications/test/{user_id}")
async def test_notification(user_id: str):
    """Send test notification to specific user"""
    user = database.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    import notifier
    result = notifier.send_test_notification(user['phone'])
    return {"success": result['success'], "details": result}

@app.get("/notifications/status")
async def notification_status():
    """Get notification system status"""
    from notification_scheduler import get_scheduler_status
    users = database.get_all_users_for_notifications()
    from eligibility import RULES
    return {
        "success": True,
        "scheduler": get_scheduler_status(),
        "users_with_notifications_enabled": len(users),
        "total_schemes": len(RULES)
    }

@app.post("/notifications/trigger-daily")
async def trigger_daily_notification():
    """Manually trigger daily digest notification (for testing)"""
    try:
        from notification_scheduler import trigger_daily_digest_now
        result = trigger_daily_digest_now()
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/scrape-and-notify")
async def scrape_and_notify():
    """Scrape new schemes and notify eligible users"""
    try:
        from notification_scheduler import trigger_scrape_and_notify_now
        result = trigger_scrape_and_notify_now()
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/scrape/status")
async def scrape_status():
    """Get scraping and scheme status"""
    from eligibility import RULES
    import os
    
    raw_file = 'scraped_schemes_raw.json'
    raw_count = 0
    if os.path.exists(raw_file):
        import json
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_count = len(json.load(f))
    
    return {
        "success": True,
        "total_schemes_in_rules": len(RULES),
        "last_scraped_raw_count": raw_count
    }

if __name__ == "__main__":
    import uvicorn
    database.init_db()
    
    try:
        from notification_scheduler import setup_scheduler
        setup_scheduler()
        print("Notification scheduler started")
    except Exception as e:
        print(f"Warning: Could not start scheduler: {e}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
