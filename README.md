<div align="center">

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=30&pause=1000&color=14B8A6&center=true&vCenter=true&width=700&lines=MtejaAI+%F0%9F%A4%96;Talk+to+Customers+%C2%B7+Never+Miss+a+Lead;Built+with+FastAPI+%2B+React" alt="Typing SVG" />

<br/>

<img src="https://img.shields.io/badge/Status-In%20Development-orange?style=for-the-badge&logo=git" />
<img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
<img src="https://img.shields.io/badge/PostgreSQL-16+-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
<img src="https://img.shields.io/badge/Version-1.0%20MVP-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />

<br/><br/>

> **MtejaAI**  An agentic customer-response platform built as a university field practice project. Captures customer messages from SMS and email, classifies genuine customer inquiries automatically, and lets an AI agent hold a bounded conversation with customers so none go unanswered — with a CRM pipeline and dashboard for the business owner.

<br/>

*"Mteja" — Swahili for "customer." The whole product is built around not losing one.*

[📖 Documentation](#-documentation) · [🚀 Quick Start](#-quick-start) · [📡 API Reference](#-api-reference) · [🗺️ Roadmap](#-roadmap) · [👥 Team](#-team)

</div>

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [V1 Scope](#-v1-scope)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Database Schema](#-database-schema)
- [Roadmap](#-roadmap)
- [Team](#-team)
- [License](#-license)

---

## 🎯 About the Project

**MtejaAI** is an agentic customer-response platform developed by a team of three students at **Mbeya University of Science and Technology (MUST)**, built for industrial/field practice. The system follows a clean layered architecture separating API routing, business logic, data access, and the database, paired with a React dashboard for the business owner.

The core problem: small businesses lose customers not from bad service, but from slow replies. A customer messages in, no one answers fast enough, and they go to a competitor. MtejaAI solves this by having an AI agent respond immediately — holding a real conversation, not just an auto-reply — while keeping every message visible to staff and handing off anything the agent shouldn't decide alone.

**What the platform does:**

- 💬 **Multi-channel intake** — receives customer messages via SMS and email
- 🔍 **Classification** — automatically separates genuine customer inquiries from non-customer/informal messages
- 🤖 **Agentic conversation** — an AI agent replies to customers directly, using each contact's full message history
- 🧭 **Handoff logic** — anything outside the agent's scope (pricing disputes, complaints) is flagged for a human instead of guessed at
- 📋 **Pipeline & CRM** — every contact tracked through stages (new inquiry → in conversation → booked / handed to human)
- 🛠️ **Owner dashboard** — live view of messages, leads, active agents, and conversation activity

---

## 📦 V1 Scope

Version 1 is intentionally scoped to the core loop: receive a message, classify it, let the agent respond or escalate. Scope is **locked** — any additions beyond what is listed below require a formal change request.

### ✅ What's Included in V1

| Area | Features |
|---|---|
| **Contacts & Pipeline** | Contact record per customer, tags, custom fields, pipeline with stages |
| **Channels** | SMS (inbound + outbound via Africa's Talking), Email (inbound + outbound via Gmail API/IMAP) |
| **Classification** | Formal/customer vs informal/non-customer message filtering before anything reaches the agent |
| **Conversational Agent** | Bounded AI replies using per-contact conversation history; FAQ-style and confirmation-level questions only |
| **Handoff** | Automatic escalation to a human task when a message is outside the agent's defined scope |
| **Timeline** | Merged activity log per contact — every SMS, email, and agent reply in one place |
| **Dashboard** | Message/lead counters, channel activity, live agent status (Sales / Support / Follow-up) |

### ❌ What's NOT in V1

| Excluded Feature | Reason |
|---|---|
| WhatsApp, Instagram, Telegram, X/Twitter channels | Each carries separate business-verification or per-message-cost overhead — out of V1 scope |
| Drag-and-drop funnel/website builder | Not needed for the core problem being solved |
| Voice AI / phone calls | Post-MVP |
| Calendar & booking system | Post-MVP |
| Multi-tenant / white-label / agency mode | Out of V1 scope — single business only |
| Membership sites, reporting dashboards beyond the basics shown | Post-MVP |
| Fully autonomous pricing or complaint handling by the agent | Deliberately excluded — always hands off to a human |

> ⚠️ **Note:** Scope is locked after Phase 1. Any change requests must be reviewed by the project lead and will affect the project timeline.

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│              React 18 · Tailwind CSS · Axios                 │
│      (Dashboard · Pipeline Board · Conversation Viewer)      │
└────────────────────────┬─────────────────────────────────────┘
                         │  HTTP / REST
┌────────────────────────▼─────────────────────────────────────┐
│                    API LAYER (FastAPI)                       │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐│
│ │/contacts │ │/channels │ │ /agent   │ │     /pipeline      ││
│ │  router  │ │  router  │ │  router  │ │       router       ││
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┬─────────┘│
└──────┼────────────┼────────────┼──────────────────┼──────────┘
       │             │            │                  │
┌──────▼─────────────▼────────────▼──────────────────▼─────────┐
│                      SERVICE LAYER                           │
│   Classification · Agent Orchestration · Handoff Logic       │
└───────────────────────────────┬────────────────────────────--┘
                                │
┌───────────────────────────────▼──────────────────────────────┐
│                    REPOSITORY LAYER                          │
│              SQLAlchemy 2.0 Async ORM Queries                │
└───────────────────────────────┬──────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────┐
│                     DATABASE LAYER                           │
│               PostgreSQL 16 · Alembic Migrations             │
└──────────────────────────────────────────────────────────────┘

        ▲                                          ▲
        │                                          │
┌───────┴──────── ┐                        ┌────────┴─────────┐
│  Africa's       │                        │   Gmail API /    │
│  Talking (SMS)  │                        │   IMAP (Email)   │
└─────────────────┘                        └──────────────────┘
```

**Design Pattern:** Routes → Services → Repositories → Models  
**Agent Flow:** Message In → Classify → Route (Agent / Human) → Log to Timeline  
**Validation:** Pydantic v2 schemas on all inputs and outputs  
**Frontend ↔ Backend:** REST API via Axios with CORS configured

---

## 🛠️ Tech Stack

### Backend

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Core runtime |
| **Framework** | FastAPI 0.110+ | REST API & OpenAPI docs |
| **ORM** | SQLAlchemy 2.0 (async) | Database abstraction |
| **Database** | PostgreSQL 16+ | Primary data store |
| **Migrations** | Alembic | Schema version control |
| **Validation** | Pydantic v2 | Request / response schemas |
| **Background Jobs** | APScheduler / Celery | Delayed follow-ups, scheduled checks |
| **SMS Channel** | Africa's Talking API | Send / receive customer SMS |
| **Email Channel** | Gmail API / IMAP | Read and send customer email |
| **AI Layer** | LLM API (chat + classification prompts) | Message classification & agent replies |
| **Testing** | pytest + httpx | Unit & integration tests |
| **Dev Server** | Uvicorn | ASGI server |

### Frontend

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | React 18+ | UI component library |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **HTTP Client** | Axios | API requests |
| **Routing** | React Router v6 | Client-side navigation |
| **State** | Context API | Dashboard & auth state management |
| **Build Tool** | Vite | Fast dev server & bundler |

---

## 📁 Project Structure

```
mtejaai/
│
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 📁 v1/
│   │   │   │   ├── contacts.py       # Contact & pipeline endpoints
│   │   │   │   ├── channels.py       # SMS & email webhook + send endpoints
│   │   │   │   ├── agent.py          # Agent reply & handoff endpoints
│   │   │   │   └── pipeline.py       # Stage-move endpoints
│   │   │   └── deps.py               # Shared dependencies (auth, db)
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── config.py             # App settings (env vars)
│   │   │   ├── security.py           # Auth for the owner dashboard
│   │   │   └── database.py           # Async DB engine & session
│   │   │
│   │   ├── 📁 models/
│   │   │   ├── contact.py            # Contact ORM model
│   │   │   ├── message.py            # Message ORM model (sms/email, in/out)
│   │   │   ├── pipeline.py           # Pipeline & Stage ORM models
│   │   │   └── task.py               # Human handoff task ORM model
│   │   │
│   │   ├── 📁 schemas/
│   │   │   ├── contact.py            # Pydantic schemas for contacts
│   │   │   ├── message.py            # Pydantic schemas for messages
│   │   │   └── agent.py              # Pydantic schemas for agent I/O
│   │   │
│   │   ├── 📁 services/
│   │   │   ├── classification_service.py  # Formal/informal message classifier
│   │   │   ├── agent_service.py           # Conversation orchestration
│   │   │   ├── channel_service.py         # SMS/email send & receive logic
│   │   │   └── pipeline_service.py        # Stage transitions
│   │   │
│   │   ├── 📁 repositories/
│   │   │   ├── contact_repo.py       # Contact DB queries
│   │   │   ├── message_repo.py       # Message DB queries
│   │   │   └── task_repo.py          # Handoff task DB queries
│   │   │
│   │   └── main.py                   # App entry point & router mount
│   │
│   ├── 📁 alembic/                   # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── 📁 tests/
│   │   ├── test_contacts.py
│   │   ├── test_classification.py
│   │   └── test_agent.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   ├── alembic.ini
│   └── README.md
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/            # Reusable UI components
│   │   ├── 📁 pages/                 # Route-level pages
│   │   │   ├── Overview.jsx
│   │   │   ├── Inbox.jsx
│   │   │   ├── Pipeline.jsx
│   │   │   ├── ContactDetail.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── AgentSettings.jsx
│   │   ├── 📁 context/               # Auth & dashboard state
│   │   ├── 📁 services/              # Axios API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
└── README.md                         # ← You are here
```

---

## 🚀 Quick Start

### Prerequisites

Make sure you have the following installed:

- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [PostgreSQL 16+](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)
- An [Africa's Talking](https://developers.africastalking.com/) sandbox account
- A Gmail API / IMAP-enabled email account for testing

---

### 1. Clone the Repository

```bash
git clone https://github.com/khamismgofi-web/Mteja-AI.git
  **OR**
git clone https://github.com/willy7890/Mteja-Ai.git
cd mtejaai
```

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate — Linux / macOS
source venv/bin/activate

# Activate — Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Configure environment variables:**

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mtejaai_db

# SMS Channel
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-sandbox-api-key

# Email Channel
GMAIL_CLIENT_ID=your-gmail-oauth-client-id
GMAIL_CLIENT_SECRET=your-gmail-oauth-client-secret

# AI Layer
LLM_API_KEY=your-llm-api-key

# App
APP_NAME=MtejaAI
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173
```

**Run database migrations:**

```bash
alembic upgrade head
```

**Start the backend server:**

```bash
uvicorn app.main:app --reload
```

Backend is live at **[http://localhost:8000](http://localhost:8000)**

```
🌐 Swagger UI  →  http://localhost:8000/docs
📘 ReDoc       →  http://localhost:8000/redoc
💓 Health      →  http://localhost:8000/health
```

---

### 3. Frontend Setup

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend is live at **[http://localhost:5173](http://localhost:5173)**

---

## 📡 API Reference

### Contacts & Pipeline

```http
GET    /api/v1/contacts                    # List all contacts
GET    /api/v1/contacts/{id}               # Get single contact + timeline
POST   /api/v1/contacts                    # Create a contact
PATCH  /api/v1/contacts/{id}               # Update tags / custom fields
POST   /api/v1/pipeline/stages/{id}/move   # Move a contact between stages
```

### Channels

```http
POST   /api/v1/channels/sms/webhook        # Inbound SMS receiver (Africa's Talking)
POST   /api/v1/channels/sms/send           # Send outbound SMS
POST   /api/v1/channels/email/webhook      # Inbound email receiver
POST   /api/v1/channels/email/send         # Send outbound email
```

### Agent & Classification

```http
POST   /api/v1/agent/classify              # Classify an inbound message (customer / non-customer)
POST   /api/v1/agent/respond               # Generate an agent reply for a contact
GET    /api/v1/agent/tasks                 # [Staff] View messages handed off to a human
PUT    /api/v1/agent/tasks/{id}/resolve    # [Staff] Resolve a handed-off task
```

### Dashboard

```http
GET    /api/v1/dashboard/summary           # Total messages, leads, active agents
GET    /api/v1/dashboard/activity          # Message/lead activity over time
```

> 📘 Full interactive documentation available at `/docs` once the backend server is running.

---

## 🗄️ Database Schema

```
┌──────────────┐       ┌─────────────────┐       ┌───────────────────┐
│   contacts   │       │    messages     │       │      stages       │
├──────────────┤       ├─────────────────┤       ├───────────────────┤
│ id (PK)      │◄──────│ id (PK)         │       │ id (PK)           │
│ name         │       │ contact_id (FK) │       │ pipeline_id (FK)  │
│ phone        │       │ channel         │       │ name              │
│ email        │       │ direction       │       │ order             │
│ tags         │       │ body            │       └───────────────────┘
│ created_at   │       │ classification  │
└──────┬───────┘       │ created_at      │
       │               └─────────────────┘
       │
┌──────▼─────── ┐       ┌─────────────────┐
│ contact_stage │       │      tasks      │
│    _link      │       ├─────────────────┤
├───────────────┤       │ id (PK)         │
│ contact_id(FK)│       │ contact_id (FK) │
│ stage_id (FK) │       │ reason          │
│ entered_at    │       │ status          │
└───────────────┘       │ created_at      │
                        └─────────────────┘
```

---

## 🗺️ Roadmap

### Phase 1 — Initiation ✅
- [x] Project assigned (agentic CRM/automation platform)
- [x] Team roles assigned
- [x] Scope defined and locked

### Phase 2 — Planning 🔄
- [ ] Requirements documented
- [ ] Timeline and milestones set
- [ ] Risk register created

### Phase 3 — Design
- [ ] Wireframes created
- [ ] Dashboard UI approved
- [ ] Architecture diagram finalized

### Phase 4 — Development
- [ ] Repository setup & branch protection
- [ ] Backend: Contacts & pipeline endpoints
- [ ] Backend: SMS channel integration
- [ ] Backend: Email channel integration
- [ ] Backend: Classification service
- [ ] Backend: Conversational agent + handoff logic
- [ ] Frontend: Dashboard, inbox, pipeline board
- [ ] Frontend: Conversation viewer

### Phase 5 — Testing
- [ ] Classification accuracy testing against real message set
- [ ] Agent eval set (15–20 scenarios, including handoff cases)
- [ ] API integration testing
- [ ] User acceptance testing (UAT)

### Phase 6 — Deployment
- [ ] Configure production environment
- [ ] Deploy backend (Railway / Render)
- [ ] Deploy frontend (Vercel / Netlify)
- [ ] Release validation

### Phase 7 — Closure
- [ ] Documentation handover
- [ ] Lessons learned review
- [ ] Project closure report

---

## 👥 Team

<div align="center">

| Role | Name | Responsibility |
|---|---|---|
| **Project Lead / CRM & Data Layer** | Khamis Mgofi | Architecture, contacts/pipeline API, code review, delivery |
| **Automation Engine** | Wilbard Magaso | Background workers, message routing logic |
| **Integration & Frontend** | Cisco Liberati | SMS/email integration, React dashboard, agent feature |

*Developed at **Mbeya University of Science and Technology (MUST)**, Tanzania*

</div>

---

## 🤝 Contributing

This is a university field practice project. Contributions are limited to team members. Branch protection rules are enforced — all changes go through pull requests.

```bash
# 1. Pull the latest main
git pull origin main

# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Commit your changes (follow Conventional Commits)
git commit -m "feat: add sms classification service"

# 4. Push to your branch
git push origin feature/your-feature-name

# 5. Open a Pull Request for review
```

**Branch naming convention:**
- `feature/` — new features
- `fix/` — bug fixes
- `docs/` — documentation updates
- `test/` — adding or updating tests

> ⚠️ No direct pushes to `main`. All PRs require review from the project lead before merging.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ by **Khamis Mgofi & Willbard Magaso** · MUST, Tanzania · 2026

⭐ Star this repo if you found it helpful!

</div>
