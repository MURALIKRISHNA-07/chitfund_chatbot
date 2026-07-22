# Chit Fund Adviser Chatbot

## Project Overview

AI-powered Chit Fund Adviser chatbot that helps customers:

- Understand chit funds
- Learn available chit schemes
- Get personalized chit recommendations
- Calculate auction outcomes
- Understand dividends and installment adjustments
- Capture customer enquiries

Runs on Streamlit. Architecture supports future website migration.

---

## Technology Stack

**Frontend:** Streamlit
**AI:** Google Gemini API
**Vector DB:** Qdrant (Hybrid Search: Dense + Sparse)
**Database:** MongoDB
**PDF Processing:** PyMuPDF

---

## Architecture

```
Chat UI (Streamlit)
       │
       ▼
Intent Detection (Gemini)
       │
  ┌────┼────────────┐
  ▼    ▼            ▼
RAG  Scheme    Calculation
  │   Engine    Engine
  ▼    │            │
Vector  ▼            ▼
DB   schemes.json  chit_calculator.py
  │                  │
  └───────┬──────────┘
          ▼
  Recommendation Engine
          │
          ▼
  Response Formatter
          │
          ▼
      MongoDB
```

---

## Agents

### 1. Conversation Agent
- Intent detection using regex-first approach + LLM fallback
- Routes to correct agent
- Supported intents: learn_chit_fund, recommend_scheme, calculate_chit, compare_plans, ask_rules, capture_lead, find_scheme

### 2. RAG Knowledge Agent
- Answers knowledge questions from PDF
- Never returns numbers or calculations
- Uses Qdrant hybrid search (dense + sparse vectors)

### 3. Recommendation Engine
- Extracts user goals (budget, duration, purpose)
- Finds matching schemes from schemes.json
- Calculates profit/dividend for each scheme
- Explains why each scheme fits the user

### 4. Calculation Agent
- All numbers come from chit_calculator.py
- Never uses AI for calculations
- Handles: breakdown, dividend, profit, summary

### 5. Lead Agent
- Captures customer details via form or chat
- Stores in MongoDB

---

## Tools Interface

```python
from tools import find_scheme_by_budget, find_scheme_by_value, calculate_profit

schemes = find_scheme_by_budget(10000)
scheme = find_scheme_by_value(500000)
profit = calculate_profit(500000, 10000, 50, 50)
```

---

## Financial Calculation Rules

**Never calculate money using Gemini.**

All calculations use Python functions in `logic/chit_calculator.py`:
- calculate_prize_amount()
- calculate_dividend()
- calculate_next_installment()
- generate_chit_breakdown()
- compare_schemes()

---

## Vector Database

**Collection:** chitfund_knowledge

**25 Intent-Based Chunks:**

| Category | Chunks |
|----------|--------|
| Definitions | 9 (What is Chit Fund, Dividend, Prize Money, etc.) |
| Process | 4 (How it works, Auction, Registration) |
| Examples | 2 (5 Lakh Example, Investment Return) |
| Benefits | 4 (General, Savings, Business, Emergency) |
| FAQ | 10 (Questions users naturally ask) |
| Policies | 2 (Eligibility, Commission) |

**Each chunk has metadata:**
- `title` - Clear question/statement
- `category` - For filtering
- `intent` - Always "knowledge"
- `tags` - For better retrieval

---

## MongoDB Collections

**users** - Customer profiles
**conversations** - Chat history
**leads** - Customer enquiries

---

## Project Structure

```
chitfund_chatbot/
├── app.py                  # Streamlit UI
├── tools.py                # Simple tool interface
├── schemes.json            # Chit scheme data
├── agents/
│   ├── conversation_agent.py
│   ├── rag_agent.py
│   ├── recommendation_agent.py
│   ├── calculation_agent.py
│   └── lead_agent.py
├── ai/
│   ├── gemini_client.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── pdf_processor.py
├── database/
│   ├── mongodb.py
│   ├── conversations.py
│   └── leads.py
├── logic/
│   └── chit_calculator.py
├── config/
│   └── settings.py
└── documents/
    └── chitfunds.pdf
```
## Design Principles

- AI is responsible for language understanding, intent detection, and response generation.
- Financial calculations are deterministic and implemented entirely in Python.
- RAG is used exclusively for knowledge retrieval and explanations.
- Business rules are separated from AI prompts to improve reliability and maintainability.
- Each agent has a single responsibility, making the system easier to test and extend.
