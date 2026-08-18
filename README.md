# MTEJA AI

**Agentic AI-powered Omnichannel CRM**

MTEJA AI is a SaaS platform that lets businesses manage all customer conversations, leads, sales, support, and marketing from **one unified dashboard**.

Instead of switching between WhatsApp, Facebook, Instagram, Telegram, X/Twitter, TikTok, Email, SMS and other channels, everything lives in a single workspace powered by specialized AI agents.

---

## Key Features

- **Unified Inbox** – all channels in one place
- **AI Agents** – Sales, Support, Marketing, Follow-up (agentic architecture)
- **CRM Core** – Customers, Leads, Deals, Campaigns
- **Multi-tenant** – full organization isolation
- **Real-time** – WebSocket updates
- **Human Handoff** – AI or human can take over anytime
- **TikTok ready** – first-class channel in the architecture

---

## Supported Channels

WhatsApp · Facebook · Instagram · Telegram · X/Twitter · **TikTok** · Email · Website Chat · SMS · Voice (planned)

> Channel adapters are built as independent modules. Status (Implemented / Planned) is tracked in `docs/integrations.md`.

---

## Tech Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Frontend    | React + Vite + Tailwind |
| Backend     | FastAPI (Python)        |
| Database    | PostgreSQL              |
| Cache/Queue | Redis                   |
| Real-time   | WebSockets              |
| Workers     | Background tasks        |
| Deploy      | Docker                  |

---

## Project Structure

```text
mteja-ai/
├── frontend/          # React dashboard
├── backend/           # FastAPI + AI agents + integrations
├── database/          # Schema & migrations
├── docs/              # Architecture & API docs
├── docker/            # Dockerfiles
├── scripts/           # Setup helpers
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/willy7890/mteja-ai.git
cd mteja-ai
```

### 2. Environment files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 3. Run with Docker

```bash
docker compose up --build
```
### Optional run without docker
'''cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev

- Frontend → http://localhost:5173  
- Backend API → http://localhost:8000  
- API Docs → http://localhost:8000/docs  

'''

### How to push to github
# Initialize git
git init

# Add all files
git add .

# Make the first commit
git commit -m "Initial commit - MTEJA AI"

# Rename branch to main (if needed)
git branch -M main

# Connect to your GitHub repository
git remote add origin https://github.com/willy7890/Mteja-AI.git

# Push the code
git push -u origin main
'''
# 1. Always start from the latest develop
git checkout develop
git pull origin develop

# 2. Create your own feature branch from develop
git checkout -b feature/your-name-feature

# 3. Work on your code...
# then commit
git add .
git commit -m "Your message"

# 4. Push your feature branch
git push -u origin feature/your-name-feature

---

## Architecture (simplified)

```text
Customer → Channel (WhatsApp / TikTok / etc.)
         ↓
   Integration Hub
         ↓
  Unified Message
         ↓
     CRM Core
         ↓
 AI Agent Orchestrator
   (Sales / Support / Marketing…)
         ↓
   Response back to original channel
```

---

## License

MIT License – see [LICENSE](LICENSE)

---

**MTEJA AI** — One platform. Every channel. Intelligent action.
