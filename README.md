# Personal Finance Coach Agent

## Overview
This project is a multi-agent personal finance coach that helps track expenses, analyze budgets, provide savings advice, monitor financial goals, and generate spending reports. It uses a main coordinator agent to orchestrate sub-agents and integrates tools for storage, search, memory, and logging.

## Problem Statement
Managing personal finances is hard for beginners. People struggle to consistently track expenses, understand budgets, and find practical ways to save. This agent offers an approachable, conversational interface to organize spending, set goals, and receive actionable advice.

## Solution Architecture
Multi-agent system:

- Main Coordinator Agent (routes requests and manages context)
  - Expense Tracker Agent (categorizes and saves expenses)
  - Budget Analyzer Agent (compares spending vs. budget)
  - Savings Advisor Agent (fetches tips and gives advice)
  - Goal Monitor Agent (tracks goals and progress)

Agents share tools:

- Storage Tool (JSON file storage for simplicity)
- Search Tool (Serper API integration for Google Search)
- Memory System (conversation history and user preferences)
- Logger (observability of agent actions and errors)

## Features
- Track expenses: "I spent $50 on groceries"
- Analyze budget and show category totals
- Get personalized savings advice with web tips
- Set and monitor financial goals
- Generate spending reports
- Persistent memory and preferences
- Detailed logging for observability

## Technologies Used
- Google Gemini (AI model)
- Python 3.10+
- Rich (CLI output formatting)
- Requests (HTTP client)
- Python Dotenv (env management)

## Installation

### Prerequisites
- Python 3.10+
- Google Gemini API key (optional but recommended)
- Serper API key (optional for web search)

### Setup Steps
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with API keys (see `.env.example`)
4. Run: `python main.py`

### UI (Web App)
- Install extra dependencies: `pip install -r requirements.txt`
- Run the UI: `streamlit run ui/app.py`
- Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Usage Examples

Example session:

- `/expense` → Enter: `I spent $25 on transport to office`
- `/budget` → Agent compares monthly spend vs budget
- `/advice` → Agent suggests tips based on spending and web search
- `/goal` → Set: `Save $5000 for a car by 2026-12-31`
- `/report` → Shows monthly totals and categories
- `/help` → Lists available commands
- `/quit` → Exit

UI pages:
- Home → Overview and quick start
- Add Expense → Structured form to save expenses
- Budget → Monthly analysis, category chart, set monthly budget
- Advice → Personalized savings tips and web results
- Goals → Set, list, and check progress against goals
- Report → Monthly report with CSV export
- Settings → Preferences (budget, session)
- Logs → View latest agent logs

## Agent Architecture
- The coordinator agent interprets intent (using Gemini when available), maintains memory, and routes requests to sub-agents.
- Sub-agents operate independently with shared tools:
  - Expense Tracker parses user statements and writes to storage
  - Budget Analyzer totals expenses and compares to budget
  - Savings Advisor pulls current tips and personalizes suggestions
  - Goal Monitor stores goals and computes progress requirements

## Competition Requirements Met
✅ Multi-agent system: main coordinator with four sub-agents
✅ Tools: storage tool (JSON), search tool (Serper/Google), calculation utilities
✅ Memory & Sessions: conversation history and user preferences persisted
✅ Observability: timestamped logs for actions, tool usage, and errors

## Notes
- If Gemini or Serper keys are missing, the system gracefully degrades to heuristic intent and local tips.
- Default monthly budget is `$1000`; you can change via `/budget` settings.