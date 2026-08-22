from app.services.reranker import rerank
def test_relevant_passage_moves_up():
    docs=[{"text":"generic corporate information"},{"text":"revenue increased due to cloud demand"}]
    assert rerank("why did revenue increase",docs,1)[0]["text"].startswith("revenue")
