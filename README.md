# Financial Research Agent — V3

A portfolio-grade AI system combining SEC filings, XBRL financial facts, vector retrieval, SQL, and an LLM to answer company-research questions with grounded evidence.

## Architecture

```text
User Question
     |
FastAPI + deterministic query router
     |--------------------|
     v                    v
SEC filing RAG        Structured XBRL facts
Postgres + pgvector   PostgreSQL + SQL
     |--------------------|
              v
       Grounded LLM answer
       + filing citations
```

## Quick start

```bash
cp .env.example .env
docker compose up -d db
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/ingest_company.py --ticker MSFT --cik 789019 --forms 10-K --limit 3
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs`.

Set a real contact in `SEC_USER_AGENT`, as SEC automated requests should identify the requester.

## Example

POST `/ask`

```json
{"ticker":"MSFT","question":"Why did revenue change and what did management say drove it?"}
```

The router selects `hybrid`, retrieves filing passages, queries structured financial facts, and gives both to the answer model.


## Interview talking points
1. Why hybrid RAG + SQL is safer for financial numbers than pure RAG.
2. Chunk-size/overlap tradeoffs.
3. Exact vector search vs HNSW as the corpus grows.
4. How structured XBRL facts reduce numerical hallucination.
5. Why deterministic routing is testable and inexpensive.
6. How you would add reranking, section-aware chunking, tracing, and human-labeled evaluation.

## Strong V2 upgrades
- Hybrid lexical + vector search and reranking
- Section-aware 10-K parsing (MD&A, Risk Factors, Financial Statements)
- Multi-company comparison and query decomposition
- XBRL concept canonicalization
- HNSW indexing at larger scale
- React research workspace
- LLM-as-judge plus human benchmark set
- OpenTelemetry traces and production monitoring


## V2 additions

- Browser research workspace at `/`
- Broader vector candidate retrieval + transparent lexical reranking
- Company corpus summary endpoint
- Cleaner evidence/fact presentation
- Separate architecture notes
- Additional reranking test

The UI intentionally has no Node build step: run FastAPI and open the root URL.


## V3: impressive, but explainable

V3 deliberately adds only features that have a clear technical reason:
- **Section-aware filing chunks** so evidence can be identified as MD&A, Risk Factors, etc.
- **Financial calculations** computed in Python instead of delegated to an LLM.
- **Interview guide** explaining every important design decision and limitation.

If upgrading an existing V2 database, run `MIGRATION_V2_TO_V3.sql`. A fresh database gets the new schema automatically.

### Design principle
Complexity must earn its place. The system uses deterministic routing and a transparent reranker today; autonomous planning, cross-encoders, HNSW, and distributed queues are documented as scale-up options rather than added merely as buzzwords.
