METRICS={"revenue","sales","operating income","net income","profit","assets","liabilities","cash","margin","eps","earnings","growth","increase","decrease"}
NARRATIVE={"why","reason","management","risk","strategy","discuss","explain","driver","competition","outlook","factor"}
def route_question(question:str)->str:
    q=question.lower()
    m=any(x in q for x in METRICS); n=any(x in q for x in NARRATIVE)
    if m and n:return "hybrid"
    if m:return "structured"
    return "rag"
