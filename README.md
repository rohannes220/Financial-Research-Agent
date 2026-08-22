# Financial Research Agent

An AI-powered financial research application that analyzes SEC filings and structured financial data to answer questions about public companies with grounded, source-backed responses.

The system combines semantic retrieval over 10-K filings with structured SEC XBRL financial data, allowing it to answer both qualitative and quantitative financial questions without relying solely on an LLM.

## Overview

Financial research questions often require two different types of information.

Questions such as:

> What risks does management identify?

require understanding narrative sections of SEC filings.

Questions such as:

> How has revenue changed over the last three years?

are better answered using structured financial data.

The Financial Research Agent handles both by routing questions through the appropriate data source.

```text
                     User Question
                           |
                           v
                     Query Router
                    /      |      \
                   /       |       \
                RAG     Structured   Hybrid
                 |          |          |
          SEC Filings   XBRL Facts    Both
                 \          |          /
                  \         |         /
                   Grounded LLM Answer
                           |
                           v
                  Evidence + Citations
```

## Features

- Multi-company financial research
- SEC 10-K filing ingestion
- SEC XBRL financial fact ingestion
- Semantic search using embeddings
- PostgreSQL + pgvector vector storage
- Two-stage retrieval with lexical reranking
- Section-aware filing chunks
- Deterministic query routing
- Structured financial calculations
- Evidence-grounded LLM responses
- Direct links to SEC filing sources
- Browser-based research interface
- Company selector populated from the database

## How It Works

### 1. SEC Data Ingestion

The ingestion pipeline retrieves public company filings and financial facts from SEC EDGAR.

10-K filings are cleaned and divided into smaller chunks so relevant sections can be retrieved efficiently.

Each chunk is also associated with filing metadata such as its filing type, date, and inferred section.

### 2. Embeddings and Vector Search

Filing chunks are converted into vector embeddings and stored in PostgreSQL using pgvector.

When a user asks a narrative question, the application embeds the question and retrieves semantically similar filing passages.

A lightweight lexical reranker then reorders the candidate passages using meaningful keyword overlap.

### 3. Structured Financial Data

Numerical questions use SEC XBRL Company Facts rather than asking the language model to extract financial values from arbitrary text.

This allows calculations such as revenue trends and growth rates to be performed deterministically in Python before information is passed to the model.

### 4. Query Routing

Questions are classified into three routes:

| Route | Example | Data Source |
|---|---|---|
| RAG | "What risks does NVIDIA identify?" | SEC filing passages |
| Structured | "How has Microsoft's revenue changed?" | SEC XBRL facts |
| Hybrid | "Why did revenue increase?" | XBRL facts + filing passages |

The router is intentionally deterministic. For this use case, predictable routing is easier to test, debug, and explain than introducing unnecessary autonomous-agent behavior.

### 5. Grounded Answer Generation

The selected filing passages and/or structured financial facts are provided to the language model as evidence.

The resulting answer is grounded in that context and includes the SEC filing evidence used to generate the response.

## Architecture

```text
SEC EDGAR
   |
   +---- 10-K Filings
   |         |
   |      Parsing
   |         |
   |   Section-Aware Chunking
   |         |
   |     Embeddings
   |         |
   |   PostgreSQL + pgvector
   |         |
   |   Vector Retrieval
   |         |
   |      Reranking
   |
   +---- XBRL Company Facts
             |
       Structured Storage
             |
      Financial Calculations

                |
                v

          Query Router
       /       |       \
      RAG   Structured  Hybrid
       \       |       /
        \      |      /
        Grounded LLM
             |
             v
       Research Answer
       + SEC Evidence
```

## Technology Stack

**Backend:** Python, FastAPI, SQLAlchemy  
**Database:** PostgreSQL, pgvector  
**AI:** OpenAI embeddings and language models  
**Retrieval:** Semantic vector search + lexical reranking  
**Data:** SEC EDGAR filings and XBRL Company Facts  
**Frontend:** HTML, CSS, JavaScript  
**Infrastructure:** Docker

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-research-agent.git
cd financial-research-agent
```

### 2. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Add your OpenAI API key and SEC contact information to `.env`.

```text
OPENAI_API_KEY=your_api_key
SEC_USER_AGENT=Your Name your.email@example.com
```

Never commit the `.env` file.

### 4. Start PostgreSQL

```bash
docker compose up -d db
```

### 5. Initialize the database

```bash
PYTHONPATH=. python scripts/init_db.py
```

### 6. Ingest a company

For example, Microsoft:

```bash
PYTHONPATH=. python scripts/ingest_company.py \
  --ticker MSFT \
  --cik 789019 \
  --forms 10-K \
  --limit 3
```

The pipeline downloads the filings, processes the text, generates embeddings, stores the vectors, and retrieves structured SEC financial facts.

### 7. Start the application

```bash
PYTHONPATH=. uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Example Questions

The application can handle different types of financial research questions:

```text
What major risks does JPMorgan discuss?

How has Microsoft's revenue changed?

What drove NVIDIA's revenue growth?

How did Pfizer's revenue change and what factors did management discuss?

What does management say about competitive pressures?
```

For a question such as:

```text
Why did revenue change and what did management say drove it?
```

the application selects the **hybrid route**, combining structured XBRL financial information with relevant passages from the company's SEC filings.

## Design Decisions

### Why combine RAG and structured data?

RAG is useful for understanding narrative information such as strategy, risks, and management commentary.

Exact financial values are already available as structured XBRL facts. Using those values directly reduces the risk of numerical hallucination and makes calculations deterministic.

### Why PostgreSQL + pgvector?

The application needs both relational financial data and vector embeddings.

pgvector allows both to live in PostgreSQL, avoiding the operational complexity of maintaining a separate vector database for a relatively small research corpus.

### Why rerank retrieved passages?

Embedding similarity provides strong semantic recall, but the closest vector is not always the most directly relevant passage.

The application retrieves a broader candidate set and applies a lightweight lexical reranker to improve the final ordering.

### Why deterministic routing instead of multiple AI agents?

The application's decision space is small and well-defined.

A deterministic router provides predictable behavior, lower cost, easier debugging, and an architecture that can be clearly explained. More autonomous planning would only be justified if future versions required complex multi-step research.

## Current Scope

The project is designed as a focused financial research system rather than a general-purpose autonomous financial agent.

Current capabilities include:

- Multi-company SEC research
- Narrative filing analysis
- Structured financial analysis
- Hybrid qualitative + quantitative questions
- Source-grounded responses
- Financial trend calculations

Potential production-scale extensions include approximate vector indexing, stronger XBRL concept normalization, background ingestion jobs, and more advanced reranking.

## Project Structure

```text
financial-research-agent/
├── app/
│   ├── services/
│   │   ├── facts.py
│   │   ├── finance.py
│   │   ├── llm.py
│   │   ├── reranker.py
│   │   ├── retrieval.py
│   │   ├── router.py
│   │   ├── sec.py
│   │   └── sectioning.py
│   ├── static/
│   │   └── index.html
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   └── models.py
├── scripts/
│   ├── ingest_company.py
│   └── init_db.py
├── sql/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Disclaimer

This project is intended for educational and research purposes. It does not provide investment advice.
