# Panchayat Seva Agent - Complete Project Review

> കേരള സർക്കാർ സേവനങ്ങൾക്കായുള്ള നിങ്ങളുടെ AI സഹായി
> Your AI Assistant for Kerala Government Services

**Document Version:** 2.0  
**Last Updated:** 2026-04-09  
**Project Status:** ✅ Fully Operational

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features & Capabilities](#2-features--capabilities)
3. [Technical Architecture](#3-technical-architecture)
4. [External APIs & Integrations](#4-external-apis--integrations)
5. [Agent System Details](#5-agent-system-details)
6. [Database Schema](#6-database-schema)
7. [API Endpoints](#7-api-endpoints)
8. [Deployment Details](#8-deployment-details)
9. [Project File Structure](#9-project-file-structure)
10. [Frontend Components](#10-frontend-components)
11. [Backend Components](#11-backend-components)
12. [Libraries & Dependencies](#12-libraries--dependencies)
13. [Configuration](#13-configuration)
14. [Known Issues & Solutions](#14-known-issues--solutions)
15. [Roadmap](#15-roadmap)

---

## 1. Project Overview

### 1.1 Mission & Vision

**Panchayat Seva Agent** is an intelligent conversational AI system designed to help Kerala citizens easily understand and apply for government services and welfare schemes. The system supports both Malayalam and English languages, making it accessible to a wide range of users across Kerala.

### 1.2 Target Users

| User Type | Description | Use Case |
|-----------|-------------|----------|
| **General Citizens** | Kerala residents seeking government services | Birth certificates, ration cards, caste certificates |
| **Welfare Applicants** | Citizens eligible for government schemes | PM Awas, Old Age Pension, Karunya Health |
| **Business Owners** | Entrepreneurs needing permits/licenses | FSSAI, Trade License, GST registration |
| **Senior Citizens** | Elderly users eligible for pensions | Old Age Pension, Widow Pension |

### 1.3 Supported Languages

| Language | Code | Translation Support |
|----------|------|-------------------|
| Malayalam | `malayalam` | Full native support (മലയാളം) |
| English | `english` | Default fallback |

### 1.4 Kerala Districts Covered

All 14 Kerala districts are supported:
- Thiruvananthapuram, Kollam, Pathanamthitta, Alappuzha
- Kottayam, Idukki, Ernakulam, Thrissur
- Palakkad, Malappuram, Kozhikode, Wayanad, Kannur, Kasaragod

---

## 2. Features & Capabilities

### 2.1 Core Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Conversational AI Agent** | ✅ Complete | Natural language queries about government services |
| **Bilingual Support** | ✅ Complete | Malayalam and English with automatic translation |
| **Scheme Eligibility Checker** | ✅ Complete | Rule-based eligibility matching for 12+ welfare schemes |
| **Document Checklists** | ✅ Complete | Required documents, fees, timelines for each service |
| **Multi-Conversation Chat** | ✅ Complete | Multiple chat threads stored in localStorage |
| **User Profile Management** | ✅ Complete | View and edit user profile with extra fields |
| **Proactive Notifications** | ✅ Complete | WhatsApp alerts for new matching schemes |
| **Modern Web UI** | ✅ Complete | React-based modern interface |
| **Streamlit Fallback UI** | ✅ Complete | Simple Python-based interface |

### 2.2 Agent Capabilities

| Capability | Description |
|------------|-------------|
| **Natural Language Understanding** | Parses user queries to identify intent |
| **Tool Calling** | Automatically calls appropriate tools based on context |
| **Context Awareness** | Remembers user profile and conversation history |
| **Multi-turn Conversations** | Supports follow-up questions and clarifications |
| **Dynamic Response Generation** | Generates helpful responses in user's language |

### 2.3 Supported Government Services

| Category | Services |
|----------|----------|
| **Documents** | Birth Certificate, Death Certificate, Caste Certificate, Income Certificate |
| **Welfare Schemes** | PM Awas Yojana, Old Age Pension, Widow Pension, Karunya Health, Karunya Suraksha |
| **Business** | FSSAI Registration, Trade License, GST Registration |
| **Employment** | MGNREGA, PM Vishwakarma |
| **Education** | Kerala Scholarship (SC/ST/OBC) |
| **Healthcare** | Karunya Health, Disability Pension |

---

## 3. Technical Architecture

### 3.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PANCHAYAT SEVA AGENT                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         USER INTERFACE LAYER                          │   │
│  │                                                                       │   │
│  │   ┌──────────────────┐              ┌──────────────────────────┐      │   │
│  │   │   React Web App  │              │    Streamlit App         │      │   │
│  │   │   (Modern UI)    │              │    (Fallback UI)         │      │   │
│  │   │   Vercel         │              │    Local                 │      │   │
│  │   └────────┬─────────┘              └────────────┬───────────┘      │   │
│  │            │                                       │                 │   │
│  └────────────┼───────────────────────────────────────┼─────────────────┘   │
│               │                                       │                    │
│               ▼                                       ▼                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          API GATEWAY LAYER                            │   │
│  │                                                                       │   │
│  │   ┌─────────────────────────────────────────────────────────────┐    │   │
│  │   │                    FastAPI Backend                            │    │   │
│  │   │                                                               │    │   │
│  │   │   Endpoints:                                                  │    │   │
│  │   │   - /auth/login      - /auth/register                        │    │   │
│  │   │   - /chat           - /notifications/{user_id}               │    │   │
│  │   │   - /profile/{id}  - /schemes/eligible/{id}                  │    │   │
│  │   │   - /services       - /scrape-and-notify                     │    │   │
│  │   │                                                               │    │   │
│  │   └─────────────────────────────────────────────────────────────┘    │   │
│  │                              │                                       │   │
│  │                              ▼                                       │   │
│  │   ┌─────────────────────────────────────────────────────────────┐    │   │
│  │   │                       AGENT SYSTEM                            │    │   │
│  │   │                                                               │    │   │
│  │   │   ┌───────────────┐    ┌─────────────┐    ┌──────────┐        │    │   │
│  │   │   │ LLM Provider  │───▶│ Tool Exec   │───▶│  Tools   │        │    │   │
│  │   │   │ Gemini→Groq   │    │             │    │  (8)     │        │    │   │
│  │   │   └───────────────┘    └─────────────┘    └──────────┘        │    │   │
│  │   │                                                               │    │   │
│  │   │   ┌───────────────┐         ┌──────────────┐               │    │   │
│  │   │   │ Memory Module │         │ Knowledge    │               │    │   │
│  │   │   │ - Profile    │         │ - eligibility│               │    │   │
│  │   │   │ - Session    │         │ - knowledge  │               │    │   │
│  │   │   └───────────────┘         └──────────────┘               │    │   │
│  │   └─────────────────────────────────────────────────────────────┘    │   │
│  │                              │                                       │   │
│  └──────────────────────────────┼───────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                          DATA LAYER                                    │   │
│  │                                                                       │   │
│  │   ┌──────────────────┐              ┌────────────────────────────┐     │   │
│  │   │   PostgreSQL     │              │    External APIs            │     │   │
│  │   │   Neon.tech      │              │                            │     │   │
│  │   │                   │              │  ┌──────────────────────┐  │     │   │
│  │   │  - users         │              │  │ AI & Translation     │  │     │   │
│  │   │  - notifications │              │  │ - Gemini AI          │  │     │   │
│  │   │  - scheme_log    │              │  │ - Groq Llama        │  │     │   │
│  │   │  - extra_profile │              │  │ - Sarvam AI         │  │     │   │
│  │   │                   │              │  └──────────────────────┘  │     │   │
│  │   └──────────────────┘              │  ┌──────────────────────┐  │     │   │
│  │                                    │  │ Search & Scraping    │  │     │   │
│  │                                    │  │ - DuckDuckGo        │  │     │   │
│  │                                    │  │ - Serper API        │  │     │   │
│  │                                    │  └──────────────────────┘  │     │   │
│  │                                    │  ┌──────────────────────┐  │     │   │
│  │                                    │  │ Notifications        │  │     │   │
│  │                                    │  │ - Twilio WhatsApp   │  │     │   │
│  │                                    │  └──────────────────────┘  │     │   │
│  │                                    └────────────────────────────┘     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
User Message (Malayalam/English)
         │
         ▼
┌─────────────────┐
│  React Frontend │
│  - Validates    │
│  - Adds user_id │
└────────┬────────┘
         │
         │ HTTPS POST /chat
         ▼
┌─────────────────┐
│   FastAPI       │
│   - Auth        │
│   - Routes to   │
│     agent       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent.py      │
│   - Builds       │
│     context      │
│   - Calls LLM    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Provider    │
│ 1. Try Gemini   │
│    ↓ (fallback) │
│ 2. Try Groq     │
└────────┬────────┘
         │
         │ Response
         ▼
┌─────────────────┐
│ Tool Executor   │
│ (if needed)     │
│ - check_elig    │
│ - web_search    │
│ - documents     │
└────────┬────────┘
         │
         │ Final Response
         ▼
┌─────────────────┐
│ Response Format │
│ - Malayalam     │
│ - Structured    │
│ - User's lang   │
└─────────────────┘
```

### 3.3 Technology Stack

#### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Core language |
| FastAPI | 0.110+ | Web framework |
| Uvicorn | 0.23+ | ASGI server |
| Pydantic | 2.0+ | Data validation |

#### AI/ML
| Technology | Purpose |
|------------|---------|
| Google Gemini AI | Primary LLM (gemini-2.5-flash) |
| Groq Llama 3.3 70B | Fallback LLM |
| Sarvam AI | Malayalam translation fallback |
| ChromaDB | Vector knowledge base |

#### Database
| Technology | Purpose |
|------------|---------|
| PostgreSQL (Neon.tech) | Production database |
| SQLite | Local development |
| psycopg2 | PostgreSQL adapter |

#### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3+ | UI framework |
| TypeScript | 5.5+ | Type safety |
| Tailwind CSS | 3.4+ | Styling |
| Framer Motion | 11+ | Animations |
| Vite | 5.4+ | Build tool |

---

## 4. External APIs & Integrations

### 4.1 AI & Language APIs

#### Google Gemini AI
```python
# Package: google-generativeai
# Model: gemini-2.5-flash
# Quota: 20 requests/day (free tier)
# Purpose: Primary LLM for chat responses
```

| Aspect | Details |
|--------|---------|
| API Key | `GEMINI_API_KEY` |
| Endpoint | `generativelanguage.googleapis.com` |
| Model | `gemini-2.5-flash` |
| Use Case | Primary chat responses, eligibility checks |

#### Groq AI
```python
# Package: groq
# Model: llama-3.3-70b-versatile
# Quota: Unlimited (fast)
# Purpose: Fallback when Gemini fails/limits
```

| Aspect | Details |
|--------|---------|
| API Key | `GROQ_API_KEY` |
| Endpoint | `api.groq.com` |
| Model | `llama-3.3-70b-versatile` |
| Use Case | Fallback LLM, high-volume requests |

#### Sarvam AI
```python
# Package: requests
# Purpose: Malayalam translation fallback
# Note: Only used if LLM doesn't produce Malayalam
```

| Aspect | Details |
|--------|---------|
| API Key | `SARVAM_API_KEY` |
| Endpoint | `api.sarvam.ai` |
| Use Case | Translate English responses to Malayalam |

### 4.2 Search & Scraping APIs

#### DuckDuckGo Search
```python
# Package: duckduckgo-search
# Purpose: Free web search for government info
```

| Aspect | Details |
|--------|---------|
| Package | `duckduckgo-search>=3.0.0` |
| Use Case | Search for unknown services, office locations |

#### Serper Search
```python
# Package: requests (direct API call)
# Purpose: Enhanced search for scheme discovery
```

| Aspect | Details |
|--------|---------|
| API Key | `SERPER_API_KEY` |
| Use Case | Proactive scheme scraping |

### 4.3 Notification APIs

#### Twilio WhatsApp
```python
# Package: twilio>=8.0.0
# Purpose: Send WhatsApp notifications to users
```

| Aspect | Details |
|--------|---------|
| Account SID | `TWILIO_ACCOUNT_SID` |
| Auth Token | `TWILIO_AUTH_TOKEN` |
| WhatsApp From | `TWILIO_WHATSAPP_FROM` |
| Webhook | `/webhook/whatsapp` |

---

## 5. Agent System Details

### 5.1 Agent Architecture

The agent uses a custom **ReAct (Reasoning + Acting)** loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                        ReAct LOOP                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. REASON                                                      │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ User Message → Parse Intent → Identify Tools Needed   │     │
│     └─────────────────────────────────────────────────────┘     │
│                            │                                     │
│                            ▼                                     │
│  2. PLAN                                                         │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ Select appropriate tools:                              │     │
│     │ - check_eligibility (for scheme questions)           │     │
│     │ - get_document_checklist (for document questions)    │     │
│     │ - web_search (for unknown topics)                    │     │
│     │ - find_office (for office location questions)        │     │
│     └─────────────────────────────────────────────────────┘     │
│                            │                                     │
│                            ▼                                     │
│  3. ACT                                                          │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ Execute selected tools and collect results           │     │
│     └─────────────────────────────────────────────────────┘     │
│                            │                                     │
│                            ▼                                     │
│  4. RESPOND                                                      │
│     ┌─────────────────────────────────────────────────────┐     │
│     │ Format response in user's preferred language         │     │
│     │ (Malayalam or English)                              │     │
│     └─────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 LLM Provider (Multi-Provider Fallback)

```python
┌─────────────────────────────────────────────────────┐
│                  LLM Provider                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  User Message                                        │
│      │                                              │
│      ▼                                              │
│  ┌───────────────────┐                              │
│  │   Try Gemini      │ (Primary - gemini-2.5-flash) │
│  │   2.5 Flash      │                              │
│  └─────────┬─────────┘                              │
│            │ Success (200)                          │
│            ▼                                        │
│      Return Response                                │
│                                                      │
│      Quota Error (429)                              │
│            │                                        │
│            ▼                                        │
│  ┌───────────────────┐                              │
│  │   Try Groq        │ (Fallback - llama-3.3-70B)  │
│  │   Llama 3.3 70B  │                              │
│  └─────────┬─────────┘                              │
│            │ Success                                │
│            ▼                                        │
│      Return Response                                │
│                                                      │
│      Both Fail                                      │
│            │                                        │
│            ▼                                        │
│      Raise Exception                                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 5.3 Available Tools (8 Total)

| Tool | Function | Data Source | Description |
|------|----------|-------------|-------------|
| `web_search` | `tools.web_search()` | DuckDuckGo | Search internet for government info |
| `chromadb_search` | `tools.chromadb_search()` | ChromaDB | Search local knowledge base |
| `get_document_checklist` | `tools.get_document_checklist()` | knowledge.json | Get required documents |
| `find_office` | `tools.find_office()` | knowledge.json + Web | Locate government office |
| `check_eligibility` | `tools.check_eligibility_tool()` | eligibility_rules.json | Check scheme eligibility |
| `translate_to_malayalam` | `tools.translate_to_malayalam()` | Sarvam AI | Translate response |
| `save_to_memory` | `tools.save_to_memory_tool()` | SQLite/PostgreSQL | Save user information |
| `get_from_memory` | `tools.get_from_memory_tool()` | SQLite/PostgreSQL | Retrieve user information |

### 5.4 Eligibility Engine (12 Schemes)

| Scheme | Key Criteria | Benefit |
|--------|--------------|---------|
| BPL Ration Card | Income ≤₹1L, Kerala resident | Free/subsidized ration |
| PM Awas Yojana Gramin | Income ≤₹3L, No pucca house | ₹1.20 lakh grant |
| Karunya Health | BPL card, Income ≤₹3L | Healthcare coverage |
| Old Age Pension | Age ≥60, Income ≤₹1L | ₹500-1000/month |
| Widow Pension | Widowed, Income ≤₹1L | ₹500-1000/month |
| Disability Pension | Disability cert ≥40%, Income ≤₹1L | ₹500-1000/month |
| Karunya Suraksha | Income ≤₹5L, APL families | Health coverage |
| PM Vishwakarma | Artisans, Income ≤₹3L | Skill training, tools |
| MGNREGA | Age ≥18, Rural, Manual work | 100 days employment |
| Kerala Scholarship | SC/ST/OBC, Student, Income ≤₹2.5L | Education financial aid |
| FSSAI Registration | Food business, Turnover ≤₹12L | Food safety license |
| Indira Gandhi National Old Age Pension | Age ≥60, BPL | Central pension |

### 5.5 Language Generation

The agent generates responses directly in the user's preferred language:

```python
# For Malayalam users
messages = [
    {"role": "user", "parts": [{"text": "You respond in Malayalam..."}]},
    {"role": "user", "parts": [{"text": prompt}]}
]

# For English users
messages = [
    {"role": "user", "parts": [{"text": prompt}]}
]
```

---

## 6. Database Schema

### 6.1 Users Table

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

### 6.2 User Extra Profile Table

```sql
CREATE TABLE user_extra_profile (
    user_id TEXT PRIMARY KEY,
    has_pucca_house INTEGER,
    owns_4_wheeler INTEGER,
    government_employee INTEGER,
    receives_other_pension INTEGER,
    remarried INTEGER,
    has_disability_cert INTEGER,
    disability_percentage INTEGER,
    is_artisan INTEGER,
    is_student INTEGER,
    has_private_insurance INTEGER,
    is_food_business INTEGER,
    has_other_govt_scheme INTEGER,
    has_vehicle_above_4_lakh INTEGER,
    is_urban INTEGER,
    refuses_work INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 6.3 Notifications Table

```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
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
```

### 6.4 Scheme Log Tables

```sql
-- Manual scheme discoveries
CREATE TABLE scheme_log (
    scheme_id TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    summary TEXT,
    link TEXT,
    deadline TEXT,
    criteria TEXT,
    found_at TEXT NOT NULL
);

-- Auto-discovered schemes (for notifications)
CREATE TABLE scheme_log_auto (
    scheme_id TEXT PRIMARY KEY,
    scheme_name TEXT NOT NULL,
    summary TEXT,
    link TEXT,
    deadline TEXT,
    criteria TEXT,
    found_at TEXT NOT NULL
);
```

---

## 7. API Endpoints

### 7.1 Authentication Endpoints

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

// Response (Success)
{
  "success": true,
  "user_id": "uuid-string",
  "message": "Registration successful!"
}

// Response (Failure)
{
  "success": false,
  "errors": ["Phone number already registered"]
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

// Response (Success)
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

### 7.2 Chat Endpoint

#### POST /chat
Send message to agent.

```json
// Request
{
  "user_id": "uuid-string",
  "message": "Am I eligible for PM Awas?",
  "is_first": false
}

// Response
{
  "success": true,
  "response": "നമസ്കാരം Rajan...\n\nനിങ്ങൾക്ക് PM Awas Yojana Gramin-ലേക്ക് അർഹതയുണ്ട്!\n\n📌 എല്ലാ വ്യവസ്ഥകളും നിങ്ങൾ പാലിക്കുന്നു...\n\n💰 ആനുകൂല്യം: ₹1.20 ലക്ഷം..."
}
```

### 7.3 Profile Endpoints

#### GET /profile/{user_id}
Get user profile.

#### PUT /profile/{user_id}
Update user profile.

### 7.4 Schemes Endpoints

#### GET /schemes/eligible/{user_id}
Get all schemes the user is eligible for.

```json
// Response
{
  "success": true,
  "eligible_schemes": [
    {
      "scheme_name": "BPL Ration Card",
      "eligible": true,
      "reason": "All eligibility conditions met!",
      "benefit": "Free/subsidized rice, wheat, sugar..."
    }
  ],
  "not_eligible_schemes": [...],
  "unknown_schemes": [...],
  "total_schemes": 12
}
```

### 7.5 Notifications Endpoints

#### GET /notifications/{user_id}
Get unread notifications.

#### POST /notifications/{notification_id}/read
Mark notification as read.

---

## 8. Deployment Details

### 8.1 Current Deployment

| Service | Platform | URL | Status |
|---------|----------|-----|--------|
| **Frontend** | Vercel | https://ps-agent.vercel.app | ✅ Running |
| **Backend API** | Render | https://ps-agent-api.onrender.com | ✅ Running |
| **Database** | Neon.tech | neondb (PostgreSQL) | ✅ Connected |
| **WhatsApp Webhook** | Render | https://ps-agent-api.onrender.com/webhook/whatsapp | ✅ Active |

### 8.2 GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy.yml` | Push to main | Trigger Vercel deployment |
| `notifications.yml` | Daily (8:00 AM & 3:15 PM IST) | Send scheme notifications |

### 8.3 Environment Variables

#### Backend (Render)
| Variable | Purpose | Required |
|----------|---------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection | Yes |
| `GEMINI_API_KEY` | Google Gemini AI | Yes |
| `GROQ_API_KEY` | Groq AI fallback | Yes |
| `SARVAM_API_KEY` | Malayalam translation | Yes |
| `SERPER_API_KEY` | Enhanced search | No |
| `TWILIO_ACCOUNT_SID` | WhatsApp sender | Phase 2 |
| `TWILIO_AUTH_TOKEN` | WhatsApp auth | Phase 2 |
| `TWILIO_WHATSAPP_FROM` | WhatsApp number | Phase 2 |

---

## 9. Project File Structure

```
ps_agent/
│
├── 📁 Backend (Python/FastAPI)
│   ├── main.py                    # FastAPI application & endpoints
│   ├── agent.py                   # AI agent with ReAct loop
│   ├── tools.py                   # 8 tool functions
│   ├── llm_provider.py            # LLM provider (Gemini + Groq fallback)
│   ├── eligibility.py             # Rule-based eligibility engine
│   ├── eligibility_rules.json     # 12 welfare scheme rules
│   ├── knowledge.json              # Service information database
│   ├── memory.py                  # Session memory management
│   ├── database.py                # SQLite/PostgreSQL operations
│   ├── auth.py                    # Authentication & validation
│   ├── notifier.py                # WhatsApp notification sender
│   ├── notification_scheduler.py   # Daily notification scheduler
│   ├── scheme_scraper.py          # Government portal scraper
│   ├── whatsapp.py                # Twilio webhook handler
│   ├── cron_notify.py             # GitHub Actions entry point
│   ├── prompts.py                 # System prompts
│   ├── app.py                     # Streamlit fallback UI
│   ├── requirements.txt           # Python dependencies
│   └── .env.example               # Environment template
│
├── 📁 Frontend (React/TypeScript)
│   ├── 📁 web-app/
│   │   ├── package.json           # NPM dependencies
│   │   ├── vite.config.ts         # Vite configuration
│   │   ├── tsconfig.json          # TypeScript config
│   │   ├── tailwind.config.js     # Tailwind CSS config
│   │   ├── vercel.json            # Vercel deployment config
│   │   ├── index.html             # Entry HTML
│   │   ├── 📁 public/             # Static assets
│   │   └── 📁 src/
│   │       ├── App.tsx            # Root component
│   │       ├── main.tsx           # React entry point
│   │       ├── index.css           # Global styles
│   │       ├── 📁 components/
│   │       │   ├── LandingScreen.tsx    # Landing page
│   │       │   ├── AuthScreen.tsx       # Login/Register
│   │       │   ├── MainApp.tsx          # Main chat interface
│   │       │   └── components.css       # Component styles
│   │       ├── 📁 context/
│   │       │   └── AuthContext.tsx      # Auth state management
│   │       ├── 📁 services/
│   │       │   └── api.ts               # API calls
│   │       └── 📁 types/
│   │           └── index.ts             # TypeScript types
│
├── 📁 GitHub Configuration
│   └── 📁 .github/
│       └── 📁 workflows/
│           ├── deploy.yml              # Vercel deployment trigger
│           └── notifications.yml       # Daily notifications
│
├── 📁 Documentation
│   ├── README.md                    # Project documentation
│   ├── PROJECT_REVIEW.md            # This document
│   └── 📁 blueprints/              # Design specifications
│
├── 📁 Database
│   ├── panchayat_seva.db           # SQLite (local)
│   └── chroma_db/                   # ChromaDB vector store
│
└── 📁 Tests
    ├── test_extractor.py
    ├── test_scraper.py
    └── ...
```

---

## 10. Frontend Components

### 10.1 LandingScreen.tsx
**Purpose**: Landing page for unauthenticated users with hero section, feature highlights, and theme toggle.

### 10.2 AuthScreen.tsx
**Purpose**: Login and registration interface with loading states and error handling.

### 10.3 MainApp.tsx
**Purpose**: Main application interface with multi-conversation chat, notifications panel, and profile management.

### 10.4 AuthContext.tsx
**Purpose**: Global authentication state management with React Context API.

### 10.5 api.ts
**Purpose**: Centralized API service layer with retry logic.

---

## 11. Backend Components

### 11.1 main.py
FastAPI application with 20+ endpoints for auth, chat, profile, schemes, and notifications.

### 11.2 agent.py
AI agent with ReAct loop, lazy-loaded LLM provider, and response cleaning.

### 11.3 llm_provider.py
Multi-provider LLM with automatic Gemini→Groq fallback.

### 11.4 eligibility.py
Rule-based eligibility engine with fuzzy scheme name matching.

### 11.5 memory.py
Session memory management for user profiles and eligibility fields.

### 11.6 database.py
Dual database support (SQLite for dev, PostgreSQL for production).

### 11.7 notifier.py
WhatsApp notification system with message templates.

---

## 12. Libraries & Dependencies

### Python Dependencies (requirements.txt)
```txt
# Core
fastapi>=0.100.0, uvicorn>=0.23.0, pydantic>=2.0.0

# Database
psycopg2-binary>=2.9.0, sqlalchemy>=2.0.0

# AI & Search
requests>=2.31.0, duckduckgo-search>=3.0.0, chromadb>=0.4.0
google-generativeai>=0.3.0, groq>=0.4.0

# Notifications
twilio>=8.0.0, apscheduler>=3.10.0

# Security
argon2-cffi>=21.3.0
```

### NPM Dependencies (web-app/package.json)
```json
"dependencies": {
  "react": "^18.3.1", "framer-motion": "^11.0.0",
  "lucide-react": "^0.400.0", "clsx": "^2.1.1"
}
```

---

## 13. Configuration

### Environment Variables
```env
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key
SARVAM_API_KEY=your_key
DATABASE_URL=postgresql://...
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
```

---

## 14. Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| LLM not initializing | Use lazy loading with `get_llm_provider()` |
| PostgreSQL connection closed | Implement connection health check |
| Gemini quota exceeded | Use Groq as automatic fallback |
| TypeScript unused variable | Remove or prefix with `_` |

---

## 15. Roadmap

### Phase 1: Reactive Agent ✅ COMPLETE
All core features implemented and deployed.

### Phase 2: Proactive Notifier ✅ COMPLETE
WhatsApp notifications and scheme scraping active.

### Phase 3: Enhancements (Planned)
- LangChain ReAct agent
- Voice I/O (Sarvam Saaras)
- Mobile app (React Native)
- Form Drafter tool

---

**Document Generated**: 2026-04-09  
**Version**: 2.0  
**Status**: Complete
