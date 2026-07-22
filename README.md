# Chit Fund Adviser Chatbot

AI-powered chatbot that helps customers understand chit funds, get personalized recommendations, and calculate auction outcomes.

## Features

- Learn how chit funds work (Knowledge RAG)
- Browse available chit schemes from schemes.json
- Get personalized scheme recommendations based on budget and goals
- Calculate auction discounts, dividends, and installments
- Full month-by-month breakdown table
- Investment summary with profit calculations
- Compare different chit plans
- Capture customer enquiries via form

## Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini (google-genai SDK)
- **Vector DB:** Qdrant (Hybrid Search: Dense + Sparse vectors)
- **Database:** MongoDB
- **PDF Processing:** PyMuPDF

## Prerequisites

- Python 3.10+
- Docker (for Qdrant and MongoDB)

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd chitfund_chatbot
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and configure:

```
GEMINI_API_KEY=your_api_key_here
FOREMAN_COMMISSION_RATE=1.5
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Start services

```bash
docker run -d -p 6333:6333 qdrant/qdrant
docker run -d -p 27017:27017 mongo
```

### 4. Index the PDF

```bash
python ai/pdf_processor.py
```

### 5. Run the app

```bash
streamlit run app.py
```

## Project Structure

```
chitfund_chatbot/
├── app.py                  # Streamlit UI
├── tools.py                # Simple tool interface
├── schemes.json            # Chit scheme data
├── .env                    # Environment variables
├── requirements.txt
├── agents/
│   ├── conversation_agent.py    # Intent detection & routing
│   ├── rag_agent.py             # Knowledge Q&A (no numbers)
│   ├── recommendation_agent.py  # Scheme recommendations
│   ├── calculation_agent.py     # Financial calculations
│   └── lead_agent.py            # Customer lead capture
├── ai/
│   ├── gemini_client.py         # Gemini chat wrapper
│   ├── embeddings.py            # Gemini embeddings + sparse
│   ├── vector_store.py          # Qdrant hybrid search
│   └── pdf_processor.py         # PDF text extraction
├── database/
│   ├── mongodb.py               # Connection
│   ├── users.py                 # User CRUD
│   ├── conversations.py         # Chat history
│   └── leads.py                 # Lead storage
├── logic/
│   └── chit_calculator.py       # Financial calculations
├── config/
│   └── settings.py              # Configuration
└── documents/
    └── chitfunds.pdf            # Knowledge source
```

## Architecture

```
                 Chat UI (Streamlit)
                     │
                     ▼
              Intent Detection (Gemini)
                     │
     ┌───────────────┼────────────────┐
     ▼               ▼                ▼
 Knowledge RAG   Scheme Engine   Calculation Engine
     │               │                │
     ▼               ▼                ▼
 Vector DB      schemes.json     chit_calculator.py
     │                                │
     └───────────────┬────────────────┘
                     ▼
          Recommendation Engine
                     │
                     ▼
             Response Formatter
                     │
                     ▼
                 MongoDB
```



## How It Works

1. User asks a question in Streamlit chat
2. Conversation Agent detects intent using Gemini
3. Routes to appropriate agent:
   - **Knowledge questions** → RAG Agent (Vector DB search)
   - **Scheme recommendations** → Recommendation Engine
   - **Calculations** → Calculation Engine (Python math, never AI)
4. All numbers come from `chit_calculator.py` and `schemes.json`
5. RAG Agent explains concepts only, never returns numbers
6. Response is formatted and shown to user
7. Conversation is saved to MongoDB

## Chunking Workflow
Each chunk is stored in Qdrant as a PointStruct, consisting of:

- **Dense Vector** (3072-dim semantic embedding via Gemini)
- **Sparse Vector** (keyword-based embedding)
- **Metadata** (title, category, intent, tags, source)

```
Knowledge Chunk
      │
      ▼
PointStruct
      │
      ├── Dense Vector (3072-dim)
      ├── Sparse Vector
      └── Metadata
            ├── title
            ├── category (definition/process/faq/benefits/example/policies)
            ├── intent
            ├── tags
            └── source
```

## Chunking Method
We use **intent-based chunking** (not character-based):

```
PDF Document
      │
      ▼
Manual Curation (25 chunks)
      │
      ├── Definitions (9 chunks)
      ├── Process (4 chunks)
      ├── Examples (2 chunks)
      ├── Benefits (4 chunks)
      ├── FAQ (10 chunks)
      └── Policies (2 chunks)
      │
      ▼
Knowledge Chunks (with metadata)
      │
      ├── Dense Embedding (Gemini 3072-dim)
      └── Sparse Embedding
      │
      ▼
Qdrant Vector Database
      │
      ▼
Hybrid Search (Dense + Sparse)
      │
      ▼
Large Language Model (Gemini)
      │
      ▼
Generated Response
```

### Why Intent-Based Chunking?
- Each chunk is a complete concept (not split mid-sentence)
- FAQ chunks match how users naturally ask questions
- Metadata enables category-based filtering
- Better retrieval accuracy than character-based chunking


## Scheme Data

| Group | Members | Duration | Schemes |
|-------|---------|----------|---------|
| 1 | 20 | 20 months | 1L, 2L, 3L, 5L |
| 2 | 30 | 30 months | 3L, 5L, 10L |
| 3 | 40 | 40 months | 5L, 10L, 20L |
| 4 | 50 | 50 months | 5L, 10L, 25L |

## Tools Interface

```python
from tools import find_scheme_by_budget, find_scheme_by_value, calculate_profit

# Find schemes by budget
schemes = find_scheme_by_budget(10000)

# Find scheme by value
scheme = find_scheme_by_value(500000)

# Calculate profit
profit = calculate_profit(500000, 10000, 50, 50)
```

## License

Private
