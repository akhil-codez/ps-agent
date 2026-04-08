# Panchayat Seva Agent

> Your AI Assistant for Kerala Government Services - കേരള സർക്കാർ സേവനങ്ങൾക്കായുള്ള നിങ്ങളുടെ AI സഹായി

An intelligent conversational agent that helps Kerala citizens understand and apply for government services and welfare schemes. Supports Malayalam and English with proactive scheme notifications.

## Features

- **Conversational AI Agent** - Natural language queries about government services
- **Bilingual Support** - Malayalam and English with automatic translation
- **Scheme Eligibility Checker** - Rule-based eligibility matching for 12+ welfare schemes
- **Document Checklists** - Required documents, fees, timelines for each service
- **Proactive Notifications** - WhatsApp alerts for new matching schemes (Phase 2)
- **Multi-Platform UI** - Modern React web app + Streamlit fallback

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- API Keys (see Configuration)

### Backend Setup

```bash
# Navigate to project directory
cd panchayat_seva_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python database.py

# Start FastAPI backend
python main.py
```

Backend runs at: http://localhost:8000

### Frontend Setup (React Web App)

```bash
# Navigate to web-app directory
cd web-app

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: http://localhost:3000

### Alternative: Streamlit UI

```bash
# Run Streamlit app (simpler UI)
streamlit run app.py
```

## Project Structure

```
panchayat_seva_agent/
├── main.py                   # FastAPI app & endpoints
├── agent.py                  # AI agent with unified prompts
├── tools.py                  # Tool functions (8 tools)
├── llm_provider.py           # LLM provider (Gemini + Groq)
├── eligibility.py            # Rule-based eligibility engine
├── eligibility_rules.json    # Scheme rules database (12 schemes)
├── memory.py                # Session memory management
├── database.py               # SQLite operations
├── auth.py                  # Authentication & validation
├── knowledge.json           # Service information database
├── app.py                   # Streamlit fallback UI
│
├── web-app/                 # Modern React frontend
│   ├── src/
│   │   ├── App.tsx              # Root component (navigation)
│   │   ├── components/
│   │   │   ├── LandingScreen.tsx    # Landing page
│   │   │   ├── AuthScreen.tsx      # Login/Register
│   │   │   └── MainApp.tsx         # Chat UI + sidebar
│   │   ├── context/
│   │   │   └── AuthContext.tsx      # Auth state management
│   │   └── services/
│   │       └── api.ts                # API calls + conversations
│   └── package.json
│
├── blueprints/               # Design specifications
│   ├── blueprint_v2_full.txt
│   └── blueprint_v3_full.txt
│
├── panchayat_seva.db         # SQLite database
├── requirements.txt          # Python dependencies
└── README.md
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interface (React Web App)                │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Landing    │──▶│    Auth      │──▶│    MainApp       │   │
│  │  (LandingScreen.tsx)│(AuthScreen.tsx)│(MainApp.tsx)  │   │
│  │              │    │              │    │  - Chat         │   │
│  │  - Sign In   │    │  - Login    │    │  - Notifications│   │
│  │  - Get Start │    │  - Register │    │  - Profile      │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   localStorage                           │   │
│  │  - ps_conversations_{userId} (multi-conversation)      │   │
│  │  - ps_user (current user profile)                       │   │
│  │  - theme (dark/light)                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (main.py)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      API Routes                           │  │
│  │  POST /auth/login    POST /auth/register                  │  │
│  │  POST /chat         GET  /notifications/{user_id}         │  │
│  │  GET  /profile/{id} PUT  /profile/{id}                    │  │
│  │  GET  /schemes/eligible/{id}                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌───────────────────────────┼──────────────────────────────┐  │
│  │                      Agent System                        │  │
│  │  ┌───────────────┐   ┌─────────────┐   ┌──────────┐   │  │
│  │  │ LLM Provider  │──▶│ Tool Exec   │──▶│  Tools   │   │  │
│  │  │ Gemini→Groq   │   │             │   │  (8)     │   │  │
│  │  └───────────────┘   └─────────────┘   └──────────┘   │  │
│  │         │                      │                       │  │
│  │         ▼                      ▼                       │  │
│  │  ┌───────────────┐     ┌──────────────┐               │  │
│  │  │ Memory Module │     │ Knowledge    │               │  │
│  │  │ - Profile    │     │ - eligibility│               │  │
│  │  │ - Session    │     │ - knowledge  │               │  │
│  │  └───────────────┘     └──────────────┘               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────────┐         ┌──────────────────────────────┐ │
│  │   SQLite DB      │         │  External APIs               │ │
│  │  - users         │         │  - Gemini AI (primary)        │ │
│  │  - notifications │         │  - Groq (fallback)           │ │
│  │  - scheme_log    │         │  - Sarvam (ML fallback)       │ │
│  └──────────────────┘         └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│  ┌──────────────────┐         ┌──────────────────────────────┐ │
│  │   React Web App  │         │     Streamlit App (Alt)      │ │
│  │   (Modern UI)    │         │     (Simple UI)             │ │
│  └────────┬─────────┘         └──────────────┬─────────────┘ │
└───────────┼────────────────────────────────────┼───────────────┘
            │                                    │
            ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      API Routes                          │   │
│  │  /auth/login  /auth/register  /chat  /notifications      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌────────────────────────────┼────────────────────────────┐  │
│  │                       Agent System                        │  │
│  │  ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │  │
│  │  │ ReAct Loop   │───▶│ Tool Executor│───▶│   Tools    │  │  │
│  │  │ (Gemini AI)  │    │              │    │  (8 tools) │  │  │
│  │  └──────────────┘    └──────────────┘    └────────────┘  │  │
│  │         │                                       │        │  │
│  │         ▼                                       ▼        │  │
│  │  ┌──────────────┐                    ┌────────────────┐  │  │
│  │  │Memory Module │                    │Knowledge Base  │  │  │
│  │  │  - Profile   │                    │- ChromaDB      │  │  │
│  │  │  - Session   │                    │- knowledge.json│  │  │
│  │  └──────────────┘                    └────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                 │
│  ┌──────────────────┐         ┌──────────────────────────────┐ │
│  │   SQLite DB      │         │  External APIs               │ │
│  │  - users         │         │  - Gemini AI                 │ │
│  │  - notifications │         │  - Sarvam Translation        │ │
│  │  - scheme_log    │         │  - DuckDuckGo Search         │ │
│  └──────────────────┘         └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Agent System

### How It Works

The agent uses a custom ReAct (Reasoning + Acting) loop to process user queries:

1. **Understand** - Parse user query and identify intent
2. **Plan** - Determine which tools to use
3. **Execute** - Call appropriate tools (search, eligibility check, etc.)
4. **Respond** - Format response in user's preferred language

### LLM Provider (Multi-Provider Fallback)

The agent uses a unified LLM provider with automatic fallback:

```
┌─────────────────────────────────────────────┐
│              LLM Provider                    │
├─────────────────────────────────────────────┤
│                                             │
│  User Message                               │
│       │                                    │
│       ▼                                    │
│  ┌─────────────────┐                        │
│  │   Try Gemini    │ (Primary)              │
│  │   2.5 Flash     │                        │
│  └────────┬────────┘                        │
│           │ Success                         │
│           ▼                                 │
│      Return Response                        │
│                                             │
│  If Quota Error (429):                     │
│       │                                    │
│       ▼                                    │
│  ┌─────────────────┐                        │
│  │   Try Groq      │ (Fallback)            │
│  │   Llama 3.3 70B │                        │
│  └────────┬────────┘                        │
│           │ Success                         │
│           ▼                                 │
│      Return Response                        │
│                                             │
└─────────────────────────────────────────────┘
```

| Provider | Model | Purpose | Quota |
|----------|-------|--------|-------|
| Gemini | gemini-2.5-flash | Primary | 20 req/day (free) |
| Groq | llama-3.3-70b-versatile | Fallback | Unlimited (fast) |

**Implementation:** `llm_provider.py` provides automatic fallback on quota errors.

### Available Tools

| Tool | Purpose | Data Source |
|------|---------|-------------|
| `web_search` | Search internet for information | DuckDuckGo |
| `chromadb_search` | Search local knowledge base | ChromaDB |
| `get_document_checklist` | Get required documents | knowledge.json |
| `find_office` | Locate government office | knowledge.json + Web |
| `check_eligibility` | Check scheme eligibility | eligibility_rules.json |
| `translate_to_malayalam` | Translate response | Sarvam AI |
| `save_to_memory` | Save user information | SQLite |
| `get_from_memory` | Retrieve user information | SQLite |

### Eligibility Engine

Rule-based system matching user profiles against 12 welfare schemes:

| Scheme | Key Criteria |
|--------|--------------|
| BPL Ration Card | Income ≤₹1L, Kerala resident |
| PM Awas Yojana Gramin | Income ≤₹3L, No pucca house |
| Karunya Health | BPL card, Income ≤₹3L |
| Old Age Pension | Age ≥60, Income ≤₹1L |
| Widow Pension | Widowed, Income ≤₹1L |
| Disability Pension | Disability cert ≥40%, Income ≤₹1L |
| Karunya Suraksha | Income ≤₹5L, APL families |
| PM Vishwakarma | Artisans, Income ≤₹3L |
| MGNREGA | Age ≥18, Rural, Manual work willing |
| Kerala Scholarship | SC/ST/OBC, Student, Income ≤₹2.5L |
| FSSAI Registration | Food business, Turnover ≤₹12L |

## Proactive Notifier System (Phase 2)

The Proactive Notifier is an automated system that watches government portals for new schemes and notifies eligible users via WhatsApp.

### Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PROACTIVE NOTIFIER ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                    │
│  │   SCHEME         │         │   PLAYWRIGHT     │                    │
│  │   WATCHER        │────────▶│   SCRAPER        │                    │
│  │   (Scheduler)    │         │                  │                    │
│  │   Runs daily     │         │ - kerala.gov.in  │                    │
│  │   at 8:00 AM     │         │ - lsgkerala.gov  │                    │
│  └────────┬─────────┘         │ - socialsecurity  │                    │
│           │                   └────────┬─────────┘                    │
│           ▼                            ▼                              │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   SCHEME          │         │   CONTENT        │                 │
│  │   PARSER          │◀────────│   EXTRACTOR      │                 │
│  │                  │         │                  │                   │
│  │ - Extract name   │         │ - Title          │                   │
│  │ - Extract criteria│        │ - Deadline       │                   │
│  │ - Extract benefits│        │ - Benefits       │                   │
│  └────────┬─────────┘         │ - Link           │                   │
│           │                   └──────────────────┘                   │
│           ▼                                                       │
│  ┌──────────────────┐                                             │
│  │   ELIGIBILITY     │                                             │
│  │   MATCHER         │                                             │
│  │                  │                                              │
│  │ For each user:   │──────────┌──────────────┐                    │
│  │ - Match criteria │          │   DATABASE   │                    │
│  │ - Calculate score│          │   - users    │                    │
│  │ - Filter matches │          │   - notifs   │                    │
│  └────────┬─────────┘          └──────────────┘                    │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │   WHATSAPP        │────────▶│   TWILIO API     │                 │
│  │   NOTIFIER        │         │                  │                   │
│  │                  │         │ - Send message  │                   │
│  │ - Malayalam msg   │         │ - Delivery track│                   │
│  │ - English fallback│         │ - Opt-out      │                   │
│  └──────────────────┘         └──────────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Scheme Watcher

The Scheme Watcher runs on a scheduled basis to discover new government schemes:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from playwright.sync_api import sync_playwright

def scheme_watcher():
    """Runs daily at 8:00 AM IST"""
    portals = [
        'https://kerala.gov.in/en/web/guest/news',
        'https://www.lsgkerala.gov.in/en/announcements',
        'https://www.socialsecuritymission.gov.in/schemes',
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for portal in portals:
            page = browser.new_page()
            page.goto(portal)
            content = page.inner_text('body')
            # Extract scheme information
            schemes = extract_schemes(content)
            for scheme in schemes:
                store_scheme(scheme)
        browser.close()

scheduler = AsyncIOScheduler()
scheduler.add_job(scheme_watcher, 'cron', hour=8, minute=0)
scheduler.start()
```

### Playwright Scraper

The scraper uses Playwright to extract content from government portals:

| Portal | URL | Content Type |
|--------|-----|-------------|
| Kerala Government | kerala.gov.in | News, Announcements |
| LSGD Kerala | lsgkerala.gov.in | Scheme Updates |
| Social Security Mission | socialsecuritymission.gov.in | Welfare Schemes |
| ecitizen | ecitizen.gov.in | Service Updates |
| Kerala Plus | keralaplus.kerala.gov.in | New Services |

```python
from playwright.sync_api import sync_playwright

def scrape_portal(url: str) -> list[dict]:
    """Scrape scheme information from a portal"""
    schemes = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set viewport and user agent
        page.set_viewport_size({"width": 1280, "height": 720})
        
        # Navigate with retry
        for attempt in range(3):
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
                break
            except TimeoutError:
                if attempt == 2:
                    raise
        
        # Extract content
        content = page.inner_text('body')
        
        # Parse and extract schemes
        schemes = parse_scheme_announcements(content, url)
        
        browser.close()
    
    return schemes
```

### WhatsApp Notifications

Notifications are sent via Twilio WhatsApp API:

```python
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')

def send_whatsapp_notification(phone: str, message_ml: str, message_en: str):
    """Send WhatsApp notification to user"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Prefer Malayalam message
    message = message_ml or message_en
    
    # Format phone number (ensure +91 prefix)
    if not phone.startswith('+'):
        phone = f'+91{phone}'
    
    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:{phone}'
        )
        return {'success': True, 'message_id': msg.sid}
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Example notification message
NOTIFICATION_TEMPLATE_ML = """🏛️ പഞ്ചായത്ത് സേവ ഏജന്റ്

പുതിയ സ്കീമ: {scheme_name}

{summary}

📅 അപേക്ഷിക്കേണ്ട തീയതി: {deadline}

📎 അർഹത: {eligibility}

🔗 {link}

കൂടുതൽ വിവരങ്ങൾക്ക് ഈ ചാറ്റിൽ ചോദിക്കുക!
"""

NOTIFICATION_TEMPLATE_EN = """🏛️ Panchayat Seva Agent

New Scheme: {scheme_name}

{summary}

📅 Deadline: {deadline}

📎 Eligibility: {eligibility}

🔗 {link}

Reply to this message for more details!
"""
```

### Notification Flow

```
1. SCHEME DISCOVERED
   └─▶ New scheme found by scraper
   
2. SCHEME STORED
   └─▶ Save to scheme_log_auto table
   
3. USER MATCHING
   └─▶ Query all users with notify=1
   └─▶ For each user, check eligibility
   
4. ELIGIBILITY CHECK
   └─▶ Compare scheme criteria with user profile
   └─▶ If match, add to notification queue
   
5. NOTIFICATION QUEUE
   └─▶ Batch notifications (max 100/min for Twilio)
   └─▶ Respect user preferences (language, frequency)
   
6. MESSAGE SENT
   └─▶ Twilio WhatsApp API
   └─▶ Log delivery status
   
7. USER RESPONSE
   └─▶ User can reply to message
   └─▶ Triggers reactive agent conversation
```

### User Preferences

Users can control notification settings:

| Setting | Options | Default |
|---------|---------|---------|
| Notifications | On/Off | On |
| Language | Malayalam/English/Both | Malayalam |
| Frequency | Daily summary/Instant | Instant |
| Categories | All/Selected schemes | All |

```json
// User notification preferences
{
  "user_id": "uuid",
  "notify": true,
  "notify_language": "malayalam",
  "notify_frequency": "instant",
  "notify_categories": ["all"],
  "whatsapp_opt_in": true,
  "quiet_hours_start": 22,
  "quiet_hours_end": 8
}
```

### Notification Database

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    scheme_id TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    message_en TEXT,
    message_ml TEXT,
    is_read INTEGER DEFAULT 0,
    notification_type TEXT DEFAULT 'whatsapp',
    delivery_status TEXT DEFAULT 'pending',
    sent_at TEXT,
    read_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE scheme_log_auto (
    scheme_id TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    summary TEXT,
    benefits TEXT,
    eligibility_criteria TEXT,
    deadline TEXT,
    application_url TEXT,
    source_portal TEXT,
    discovered_at TEXT NOT NULL,
    last_checked TEXT
);
```

### Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Scheduler | ✅ Ready | APScheduler configured |
| Playwright Scraper | 🔲 Pending | Code structure defined |
| Scheme Parser | 🔲 Pending | Extractor logic needed |
| Eligibility Matcher | ✅ Ready | Reuse existing engine |
| WhatsApp Sender | 🔲 Pending | Twilio integration needed |
| Message Templates | 🔲 Pending | ML/EN templates needed |
| Delivery Tracking | 🔲 Pending | Status logging needed |
| User Preferences | 🔲 Pending | Settings page needed |

### Testing the Notifier

```bash
# Test scraper manually
python -c "
from notifier import scrape_portal
results = scrape_portal('https://kerala.gov.in/en/web/guest/news')
print(f'Found {len(results)} announcements')
"

# Test WhatsApp send
python -c "
from notifier import send_whatsapp_notification
result = send_whatsapp_notification('9876543210', 'Test message', '')
print(result)
"

# Simulate daily run
python -c "
from notifier import run_daily_check
results = run_daily_check()
print(f'Processed {len(results)} users')
"
```

## API Reference

### Authentication

#### POST /auth/register
Register a new user.

```json
// Request
{
  "name": "Rajan Kumar",
  "phone": "9876543210",
  "password": "securepass123",
  "district": "Thrissur",
  "category": "BPL",
  "income": 80000,
  "age": 65,
  "family_size": 5,
  "language": "malayalam"
}

// Response
{
  "success": true,
  "user_id": "uuid-string",
  "message": "Registration successful!"
}
```

#### POST /auth/login
Authenticate user.

```json
// Request
{
  "phone": "9876543210",
  "password": "securepass123"
}

// Response
{
  "success": true,
  "user_id": "uuid-string",
  "profile": {
    "name": "Rajan Kumar",
    "district": "Thrissur",
    "category": "BPL",
    "income": 80000,
    "age": 65,
    "language": "malayalam"
  }
}
```

### Chat

#### POST /chat
Send message to agent.

```json
// Request
{
  "user_id": "uuid-string",
  "message": "Am I eligible for PM Awas?"
}

// Response
{
  "success": true,
  "response": "✅ ELIGIBLE for PM Awas Yojana Gramin\n\n📌 You meet all conditions!\n💰 Benefit: ₹1.20 lakh in plain areas\n📄 Documents Needed: Aadhaar, Income certificate, Bank account..."
}
```

### Schemes

#### GET /schemes/eligible/{user_id}
Get all schemes the user is eligible for.

```json
// Response
{
  "success": true,
  "eligible_schemes": [
    {
      "scheme_name": "BPL Ration Card",
      "reason": "All eligibility conditions met!",
      "benefit": "Free/subsidized rice, wheat, sugar..."
    }
  ],
  "not_eligible_schemes": [...],
  "unknown_schemes": [...],
  "total_schemes": 12
}
```

### Notifications

#### GET /notifications/{user_id}
Get unread notifications.

```json
// Response
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "scheme_name": "New Scholarship Available",
      "message_ml": "പുതിയ സ്കോളർഷിപ്പ് ലഭ്യമാണ്",
      "is_read": false
    }
  ]
}
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    phone TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    district TEXT NOT NULL,
    category TEXT NOT NULL,
    income INTEGER NOT NULL,
    age INTEGER NOT NULL,
    family_size INTEGER NOT NULL,
    language TEXT DEFAULT 'malayalam',
    notify INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login TEXT
);
```

### Notifications Table
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    message_en TEXT,
    message_ml TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
```

### Scheme Log Tables
```sql
-- Manual scheme discoveries
CREATE TABLE scheme_log (...);

-- Auto-discovered schemes (for notifications)
CREATE TABLE scheme_log_auto (...);
```

## Configuration

### Environment Variables (.env)

```env
# Gemini AI - https://aistudio.google.com/apikey
GEMINI_API_KEY=your_gemini_api_key

# Sarvam AI Translation - https://sarvam.ai
SARVAM_API_KEY=your_sarvam_api_key

# Groq API (Fallback LLM) - https://console.groq.com
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

# Twilio WhatsApp - https://console.twilio.com
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Serper Search (optional)
SERPER_API_KEY=your_serper_key
```

### API Keys Required

| Service | Purpose | Required |
|---------|---------|----------|
| Gemini AI | Primary LLM | Yes (free tier) |
| Groq AI | Fallback LLM | Recommended |
| Sarvam AI | Malayalam translation | Yes |
| Twilio | WhatsApp notifications | Phase 2 |
| Serper | Enhanced web search | No | |

## Testing

### Test Plan Summary

#### Test Categories (Target: 150 queries)

| Category | Count | Examples |
|----------|-------|----------|
| Document Services | 40 | Birth cert, Ration card, Caste cert |
| Scheme Eligibility | 35 | PM Awas, Old Age Pension, Karunya |
| Business Permits | 30 | FSSAI, Trade License, GST |
| Multi-service | 25 | "Open a medical shop" workflow |
| RTI Procedures | 10 | How to file RTI |
| Edge Cases | 10 | Gibberish, out-of-scope |

#### Test User Profiles

| Profile | District | Category | Income | Age | Purpose |
|---------|----------|----------|--------|-----|---------|
| UP-01 | Thrissur | BPL | ₹80,000 | 65 | Elderly BPL tests |
| UP-02 | Ernakulam | General | ₹400,000 | 28 | General user tests |
| UP-03 | Wayanad | SC | ₹60,000 | 35 | Caste cert tests |
| UP-04 | Palakkad | OBC | ₹120,000 | 45 | Widow + family tests |
| UP-05 | - | - | - | - | Unregistered user |

#### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Answer Accuracy | ≥85% | Expert validation |
| Tool Call Appropriateness | ≥80% | Correct tools called |
| Malayalam Quality | ≥4.0/5.0 | Native speaker rating |
| Response Time | ≤8 seconds | Time to first token |

## Development

### Tech Stack

**Backend**
- Python 3.10+
- FastAPI 0.110
- SQLite (PostgreSQL planned)
- Google Gemini AI (primary)
- Groq Mixtral (fallback)
- LangChain (planned)

**Frontend**
- React 19
- TypeScript
- Tailwind CSS 4
- Framer Motion
- Vite

**Infrastructure**
- ChromaDB (vector store)
- Playwright (scraping - Phase 2)
- Twilio (WhatsApp - Phase 2)

### Adding New Services

1. Add service to `knowledge.json`:
```json
{
  "service_key": {
    "name": "Service Name",
    "description": "...",
    "subtypes": {
      "default": {
        "documents": [...],
        "office": "...",
        "fee": "...",
        "timeline": "..."
      }
    },
    "keywords": ["search", "terms"]
  }
}
```

2. Add eligibility rule to `eligibility_rules.json`:
```json
{
  "service_key": {
    "name": "Service Name",
    "conditions": {
      "income_max": 100000,
      "age_min": 18
    },
    "disqualifiers": [],
    "documents_needed": [...]
  }
}
```

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# API endpoint tests
python -m pytest tests/test_api.py

# Agent tests
python -m pytest tests/test_agent.py

# Manual UI testing
streamlit run app.py
```

## Roadmap

### Phase 1: Reactive Agent (Current)
- [x] FastAPI backend with authentication
- [x] Modern React web UI
- [x] AI agent with tool calling
- [x] Eligibility engine (12 schemes)
- [x] Knowledge base (10+ services)
- [x] Malayalam translation (Sarvam)
- [x] Session memory
- [ ] **LangChain ReAct (planned)**
- [ ] **Form Drafter tool (planned)**

### Phase 2: Proactive Notifier (In Progress)
- [x] Architecture design documented
- [x] Notification database tables ready
- [x] APScheduler configured
- [ ] Playwright scraper implementation
- [ ] Scheme parser/extractor
- [ ] WhatsApp notification sender (Twilio)
- [ ] Message templates (Malayalam/English)
- [ ] User preference settings UI
- [ ] Delivery status tracking

### Phase 3: Enhancement
- [ ] LangChain ReAct agent
- [ ] PostgreSQL database
- [ ] Voice I/O (Sarvam Saaras + Bulbul)
- [ ] Akshaya Centre integration
- [ ] Mobile app (React Native)
- [ ] AWS deployment

## Troubleshooting

### Common Issues

**Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.10+

# Verify dependencies
pip list | grep fastapi

# Check port availability
netstat -an | grep 8000
```

**Agent not responding**
```bash
# Verify API key
echo $GEMINI_API_KEY

# Test API key
python -c "import google.generativeai as genai; genai.configure()"
```

**Translation not working**
```bash
# Check Sarvam API key
echo $SARVAM_API_KEY

# Test connection
curl -X POST https://api.sarvam.ai/translate \
  -H "API-Subscription-Key: $SARVAM_API_KEY" \
  -d '{"input":"Hello","source_language_code":"en-IN","target_language_code":"ml-IN"}'
```

**Database errors**
```bash
# Reinitialize database
rm panchayat_seva.db
python database.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary software developed for Kerala Government services.

## Acknowledgments

- Kerala Government for service information
- Google for Gemini AI
- Sarvam AI for Malayalam translation
- Groq AI for fast inference
- Kerala IT Mission for support

---

## Implementation Summary (Updated: 2026-04-08)

This section documents all completed implementations for project continuity.

---

### Project Structure

```
C:\Users\akhia\OneDrive\Documents\ps_agent\
├── agent.py                    # AI agent with unified prompts
├── llm_provider.py            # Gemini + Groq fallback with language support
├── tools.py                   # 8 tools + Sarvam translation fallback
├── eligibility.py             # Scheme eligibility rules
├── eligibility_rules.json     # 12 welfare schemes
├── knowledge.json             # Service information database
├── memory.py                  # User session memory
├── database.py               # SQLite operations
├── main.py                   # FastAPI backend (all endpoints)
├── app.py                    # Streamlit fallback UI
│
├── web-app\                  # React frontend
│   └── src\
│       ├── App.tsx           # Root with Landing → Auth → MainApp flow
│       ├── components\
│       │   ├── LandingScreen.tsx    # Landing page with CTA buttons
│       │   ├── AuthScreen.tsx      # Login/Register
│       │   └── MainApp.tsx         # Chat UI with sidebar
│       ├── context\
│       │   └── AuthContext.tsx      # Auth state management
│       └── services\
│           └── api.ts               # API calls + conversation management
│
└── README.md
```

---

## Completed Implementations

### Phase 1: Reactive Agent ✅ COMPLETE

| Component | Status | Description |
|-----------|--------|-------------|
| FastAPI Backend | ✅ | All endpoints: /auth, /chat, /profile, /notifications, /schemes |
| React Web UI | ✅ | Modern UI with landing, auth, chat, notifications, profile |
| Streamlit UI | ✅ | Alternative simple interface |
| LLM Provider | ✅ | Gemini (primary) + Groq Llama 3.3-70B (fallback) |
| Direct Malayalam | ✅ | LLM generates Malayalam directly via messages parameter |
| Sarvam Fallback | ✅ | Only used if LLM doesn't produce Malayalam |
| Eligibility Engine | ✅ | 12 welfare schemes with rule-based matching |
| 8 Tools | ✅ | web_search, chromadb_search, documents, eligibility, etc. |
| Multi-Conversation | ✅ | localStorage-based, max 50 conversations per user |
| First Message Greeting | ✅ | is_first parameter controls greeting behavior |
| Profile Edit | ✅ | Inline edit form in ProfileView |
| Quick Actions | ✅ | Clickable buttons send messages directly |
| Chat Persistence | ✅ | localStorage saves conversations across sessions |
| Landing → Auth Flow | ✅ | Landing → Sign In → MainApp navigation |

---

## Key Features Explained

### 1. API Service Layer (`web-app/src/services/api.ts`)

Centralized API calls with retry logic:

```typescript
// Key functions
export async function sendMessage(userId, message, isFirst)
export async function login(phone, password)
export async function register(data)

// Conversation management
export function createConversation(userId, firstMessage)
export function updateConversation(userId, convId, messages)
export function deleteConversation(userId, convId)
export function getAllConversations(userId)
```

### 2. Multi-Conversation System

Data stored in localStorage per user:

```typescript
interface Conversation {
  id: string;           // Generated UUID
  title: string;        // First message (truncated to 40 chars)
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

interface ConversationsStore {
  conversations: Conversation[];
  activeConversationId: string | null;
}
// Key: ps_conversations_{userId}
```

### 3. Language Generation

LLM generates directly in user's language via messages parameter:

```python
# llm_provider.py - Gemini
messages = [
    {"role": "user", "parts": [{"text": "You respond in Malayalam..."}]},
    {"role": "user", "parts": [{"text": prompt}]}
]

# llm_provider.py - Groq
messages = [
    {"role": "system", "content": "You respond in Malayalam..."},
    {"role": "user", "content": prompt}
]
```

### 4. Landing → Auth → MainApp Flow

```
Unauthenticated User
       ↓
   Landing Screen (LandingScreen.tsx)
       ↓
User clicks "Sign In" or "Get Started" → setShowAuth(true)
       ↓
   Auth Screen (AuthScreen.tsx)
       ↓
User logs in → user state set in AuthContext
       ↓
   MainApp (MainApp.tsx)
       ↓
Logo click → logout() + setShowAuth(false) → Landing Screen
```

### 5. First Message Greeting

```typescript
// MainApp.tsx - state tracking
const [isFirstMessage, setIsFirstMessage] = useState(true);

// When loading conversations
const history = getChatHistory(user.user_id);
setIsFirstMessage(history.length === 0);

// When sending
const wasFirst = isFirstMessage;
const result = await sendMessage(userId, message, wasFirst);
if (wasFirst) setIsFirstMessage(false);
```

Backend receives `is_first` parameter and adjusts prompt accordingly.

---

## API Endpoints

### POST /chat

```json
{
  "user_id": "uuid",
  "message": "How to apply for birth certificate?",
  "is_first": false
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | User's unique ID |
| message | string | User's question |
| is_first | boolean | Controls greeting (default: false) |

### Response

```json
{
  "success": true,
  "response": "നമസ്കാരം [name]...\n\n[Structured Malayalam response]"
}
```

---

## Known Limitations

| Issue | Workaround |
|-------|------------|
| Groq rate limit | Wait 1 minute or use Gemini (separate quota) |
| localStorage size | Max 50 conversations stored |
| Gemini daily quota | 20 req/day on free tier |
| Image attachments | Not supported, shows error message |

---

## Recent Changes (Changelog)

| Date | Change | Files Modified |
|------|--------|----------------|
| 2026-04-08 | ✅ FULLY DEPLOYED SYSTEM | All components |
| 2026-04-08 | Added google-generativeai and groq to requirements | requirements.txt |
| 2026-04-08 | Added diagnostic logging to LLM provider | llm_provider.py |
| 2026-04-08 | Added LLM provider lazy-loading (fixes startup issue) | agent.py |
| 2026-04-08 | Fixed PostgreSQL RealDictCursor connection | database.py |
| 2026-04-08 | Fixed CORS for Vercel frontend | main.py |
| 2026-04-08 | Implemented WhatsApp webhook handler | whatsapp.py |
| 2026-04-08 | Implemented notifier with scheme matching | notifier.py |
| 2026-04-08 | Added notification_scheduler for scheme scraping | notification_scheduler.py |
| 2026-04-08 | Added GitHub Actions for daily notifications | .github/workflows/notifications.yml |
| 2026-04-08 | Added render.yaml for Render deployment | render.yaml |
| 2026-04-08 | Added vercel.json for Vercel rewrites | web-app/vercel.json |
| 2026-04-08 | Added Landing → Auth navigation flow | App.tsx, LandingScreen.tsx, MainApp.tsx |
| 2026-04-08 | Added multi-conversation chat storage | api.ts, MainApp.tsx |
| 2026-04-08 | Added first message greeting control | agent.py, main.py, api.ts, MainApp.tsx |
| 2026-04-08 | Implemented direct Malayalam LLM generation | llm_provider.py, agent.py |
| 2026-04-08 | Unify process_message and simple_process_message | agent.py |
| 2026-04-08 | Added profile edit functionality | MainApp.tsx, api.ts, main.py |
| 2026-04-08 | Connected web-app chat to backend API | api.ts, MainApp.tsx, AuthContext.tsx |
| 2026-04-08 | Quick action buttons send messages directly | MainApp.tsx |
| 2026-04-07 | Changed Groq model to llama-3.3-70b-versatile | .env, llm_provider.py |
| 2026-04-07 | Added Groq fallback for Gemini quota errors | llm_provider.py |

---

## Testing Commands

```bash
# Navigate to project
cd C:\Users\akhia\OneDrive\Documents\ps_agent

# Start backend (FastAPI)
python main.py
# Runs at http://localhost:8000

# Start frontend (React)
cd web-app
npm run dev
# Runs at http://localhost:5173 (or next available port)

# Alternative: Streamlit UI
streamlit run app.py
# Runs at http://localhost:8501
```

---

## Next Session Resume

To resume work in a new conversation:

1. Read README.md - Project Status Summary section
2. Check Recent Changes (Changelog) section
3. Review current architecture in Architecture section
4. Check Environment Variables section for deployment config
5. Run backend: `python main.py`
6. Run frontend: `cd web-app && npm run dev`
7. Test at http://localhost:5173 (or port shown)

---

## Phase 2: Proactive Notifier ✅ COMPLETED

| Component | Status | Notes |
|-----------|--------|-------|
| Architecture | ✅ | Designed |
| Scheme Scraper | ✅ | scheme_scraper.py - SJD, WCD, egrantz, Serper search |
| WhatsApp Integration | ✅ | Twilio webhook implemented |
| Notification Scheduler | ✅ | notification_scheduler.py |
| GitHub Actions | ✅ | Daily 8 AM & 3:15 PM IST |
| Database | ✅ | PostgreSQL on Neon.tech |
| Render Deployment | ✅ | Auto-deploys on GitHub push |
| Vercel Frontend | ✅ | https://ps-agent.vercel.app |

### Deployment URLs

| Service | URL |
|---------|-----|
| Frontend | https://ps-agent.vercel.app |
| Backend API | https://ps-agent-api.onrender.com |
| Database | Neon.tech (PostgreSQL - neondb) |
| WhatsApp Webhook | https://ps-agent-api.onrender.com/webhook/whatsapp |
| GitHub Actions | Scheduled notifications |

---

## Project Status Summary (As of 2026-04-08)

### ✅ FULLY OPERATIONAL SYSTEM

| Component | Deployment | Status |
|-----------|------------|--------|
| Frontend | Vercel | ✅ Running |
| Backend API | Render | ✅ Running |
| Database | Neon.tech (PostgreSQL) | ✅ Connected |
| WhatsApp | Twilio | ✅ Configured |
| Scheduled Notifications | GitHub Actions | ✅ Active |

### System Architecture

```
User (WhatsApp/Web)
       │
       ├── WhatsApp → Twilio → Render Backend → Neon DB
       │
       └── Web (Vercel) → Render Backend → Neon DB
       
Scheduled Notifications (Daily):
GitHub Actions → Render Backend → Twilio → User WhatsApp
```

### Key Files

| File | Purpose |
|------|---------|
| main.py | FastAPI endpoints |
| agent.py | Chat agent with LLM (lazy-loaded) |
| llm_provider.py | Gemini + Groq LLM provider |
| notifier.py | WhatsApp notification sender |
| notification_scheduler.py | Scheme scraping & eligibility |
| database.py | PostgreSQL + SQLite (dual support) |
| auth.py | User registration/login |
| whatsapp.py | Twilio webhook handler |
| cron_notify.py | GitHub Actions entry point |

### Environment Variables (Deployed)

| Variable | Where Set | Purpose |
|----------|-----------|---------|
| DATABASE_URL | Render, GitHub Actions | Neon PostgreSQL connection |
| GEMINI_API_KEY | Render, GitHub Actions | Primary LLM |
| GROQ_API_KEY | Render, GitHub Actions | Fallback LLM |
| SERPER_API_KEY | Render, GitHub Actions | Search for schemes |
| TWILIO_ACCOUNT_SID | Render | WhatsApp sender |
| TWILIO_AUTH_TOKEN | Render | WhatsApp auth |
| TWILIO_WHATSAPP_FROM | Render | WhatsApp number |

### Critical Code Patterns (IMPORTANT)

1. **LLM Lazy Loading** (agent.py line 17):
   - DO NOT initialize LLM at module import
   - Use `get_llm_provider()` inside functions

2. **Database Cursor** (database.py):
   - Use `get_cursor()` context manager
   - Use `RealDictCursor` for PostgreSQL (NOT row_factory lambda)

3. **API Keys** (llm_provider.py):
   - Read via `os.getenv()`
   - Keys in Render env vars, not .env
   - Local .env only for development

4. **LLM Packages Required** (requirements.txt):
   - `google-generativeai>=0.3.0`
   - `groq>=0.4.0`

### Deployment Notes

- Render deploys automatically on GitHub push
- GitHub Actions deploys notifications daily at 8 AM & 3:15 PM IST
- Vercel deploys automatically on GitHub push
- Twilio webhook: https://ps-agent-api.onrender.com/webhook/whatsapp
- Groq is used as fallback (Gemini blocked in India)

### Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "No LLM provider" error | Add google-generativeai, groq to requirements.txt |
| "connection already closed" | Use RealDictCursor in database.py |
| Gemini blocked in India | Use Groq as fallback (working) |
| Render cold start | Normal for free tier - first request takes 30-60s |

---

**Built with ❤️ for Kerala Citizens**

For questions or support, contact the development team.
