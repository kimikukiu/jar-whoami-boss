# JARVIS ECOSYSTEM - INSTALLATION & SETUP

## Requirements
- Python 3.11+
- Ollama (for local AI models)
- Node.js 18+ (for frontend)
- 8GB+ RAM recommended
- Windows 10/11 or Linux

## Quick Start

### 1. Install Ollama
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | bash

# Windows - Download from https://ollama.com/download
```

### 2. Pull Models
```bash
ollama pull llama3.3:70b-instruct-q4_K_M
ollama pull qwen2.5-coder:7b-instruct-q4_K_M
ollama pull deepseek-r1:14b-q4_K_M
ollama pull mistral-nemo:12b-instruct-q4_K_M
ollama pull nousresearch/hermes-3-llama-3.1-8b
```

### 3. Install Python Dependencies
```bash
cd d:\jarvis\ecosystem
pip install -r requirements.txt
```

### 4. Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 6. Start JARVIS
```bash
# Start backend
python main.py

# Start frontend (new terminal)
cd frontend
npm run dev
```

## Agent Roster
- **Director Fury** - Chief of Staff (Tier 0)
- **Heimdall** - Gatekeeper/Security (Tier 1)
- **John Kramer** - Planner (Tier 2)
- **Morpheus** - Dispatcher/Social Media (Tier 2)
- **Sherlock Holmes** - Inspector/Researcher (Tier 2)
- **Data** - Archivist/Memory (Tier 2)
- **Saul Goodman** - Patch Agent (Tier 3)
- **JARVIS** - Build Validator (Tier 3)
- **Ripley** - Bug Hunter/Bug Bounty (Tier 3)
- **Da Vinci** - UI/Content Creator (Tier 3)
- **John Wick** - Final Implementation (Tier 3)

## Capabilities
- Social Media Management (YouTube, TikTok, Facebook, Instagram, Telegram)
- Bug Bounty Hunting (HackerOne, Bugcrowd, etc.)
- Company Management & Freelance Operations
- Wallet & Payment Management
- OS/Software Development
- Darkweb Research & Investigations
- Full PC Administrative Control
- Voice Commands
- And more...