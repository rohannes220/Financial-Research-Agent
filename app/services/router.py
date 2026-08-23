METRICS = {
    "revenue", "sales", "operating income", "net income",
    "profit", "assets", "liabilities", "cash", "margin",
    "eps", "earnings", "growth", "increase", "decrease"
}

NARRATIVE = {
    "why", "reason", "management", "risk", "strategy",
    "discuss", "explain", "driver", "competition",
    "outlook", "factor"
}

FINANCIAL_CONTEXT = {
    "company", "business", "financial", "finance",
    "10-k", "filing", "sec", "performance",
    "market", "segment", "product"
}

def route_question(question: str) -> str:
    q = question.lower()

    m = any(x in q for x in METRICS)
    n = any(x in q for x in NARRATIVE)
    f = any(x in q for x in FINANCIAL_CONTEXT)

    if m and n:
        return "hybrid"

    if m:
        return "structured"

    if n or f:
        return "rag"

    return "out_of_scope"
