from sqlalchemy import select
from app.models import Company,Filing,FilingChunk
from app.services.llm import embed
from app.services.reranker import rerank
from app.config import settings
def retrieve(db,ticker,question,top_k=None):
    wanted=top_k or settings.top_k
    qvec=embed([question])[0]
    stmt=(select(FilingChunk,Filing).join(Filing,Filing.id==FilingChunk.filing_id)
          .join(Company,Company.id==Filing.company_id).where(Company.ticker==ticker.upper())
          .order_by(FilingChunk.embedding.cosine_distance(qvec)).limit(max(wanted*4,20)))
    candidates=[{"source_id":f"F{f.id}-C{c.chunk_index}","text":c.text,"section":c.section,"form":f.form,
                 "filed_at":f.filed_at.isoformat(),"source_url":f.source_url} for c,f in db.execute(stmt).all()]
    return rerank(question,candidates,wanted)
