from app.services.router import route_question
def test_structured():assert route_question("What was revenue last year?")=="structured"
def test_rag():assert route_question("What risks does management discuss?")=="rag"
def test_hybrid():assert route_question("Why did revenue increase?")=="hybrid"
