# Architecture Notes

## Retrieval
The first stage uses embedding cosine distance to retrieve a broader candidate set. A transparent lexical-overlap reranker then promotes candidates sharing meaningful query terms. This is intentionally simple enough to explain; a cross-encoder reranker can replace it later.

## Numerical grounding
Financial values come from SEC Company Facts rather than being extracted by the LLM from arbitrary passages whenever the router identifies a quantitative question.

## Routing
- `rag`: narrative questions
- `structured`: quantitative questions
- `hybrid`: questions requiring both a number/trend and management explanation

## Production tradeoffs
Exact pgvector search is appropriate for the initial corpus. At substantially larger corpus sizes, add an HNSW cosine index recall/latency before choosing ANN parameters.
