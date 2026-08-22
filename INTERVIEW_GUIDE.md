# Interview Guide — Explain This Project Without Buzzword Soup

## 30-second version
I built a financial research assistant that answers questions using SEC filings and structured SEC financial facts. Narrative questions retrieve relevant 10-K passages with embeddings and reranking, numerical questions use XBRL facts stored in PostgreSQL, and mixed questions use both. The LLM only receives retrieved evidence and is required to cite it.

## 2-minute architecture explanation
1. I ingest 10-K/10-Q filings and SEC Company Facts.
2. Filing text is cleaned, chunked, labeled by filing section, embedded, and stored in PostgreSQL with pgvector.
3. A simple deterministic router classifies questions as narrative, quantitative, or hybrid.
4. Narrative queries use vector retrieval followed by a transparent lexical reranker.
5. Quantitative queries use normalized XBRL facts, avoiding asking the LLM to invent or extract numbers.
6. The answer model receives only the evidence selected by those components.

## Questions you should be able to answer

### Why RAG?
The source material is too large and changes over time. Retrieval selects relevant evidence instead of putting entire filings into every prompt.

### Why PostgreSQL + pgvector?
The project needs both relational financial facts and vector embeddings. Keeping both in PostgreSQL reduces infrastructure complexity and makes the architecture easier to operate.

### Why not use an autonomous agent for everything?
The three routes are predictable. Deterministic routing is cheaper, testable, and easier to debug. More autonomy is only useful when query decomposition becomes genuinely complex.

### Why rerank?
Embedding similarity is good for semantic recall but the nearest chunks are not always the most directly relevant. A second stage improves ordering. This implementation deliberately uses a simple lexical signal so its behavior is transparent.

### Why XBRL?
Financial metrics are structured facts reported to the SEC. Using them directly is safer than asking an LLM to read a paragraph and reproduce exact values.

### Biggest limitation?
SEC concepts differ across issuers and periods. A production system needs stronger concept canonicalization, filing-section parsing, and a larger human-labeled evaluation set.

### What would you scale first?
At a larger corpus I would benchmark an HNSW pgvector index, add hybrid lexical/vector retrieval, and move ingestion into background jobs.

## Resume bullet
Built a hybrid financial-research agent combining SEC 10-K/10-Q retrieval, pgvector semantic search, reranking, and structured XBRL financial data to generate evidence-grounded answers with source citations.
