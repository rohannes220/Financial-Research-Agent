import time
from pathlib import Path
from fastapi import FastAPI,Depends,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select,func
from app.db import get_db
from app.models import Company,Filing,FilingChunk
from app.services.router import route_question
from app.services.retrieval import retrieve
from app.services.facts import get_facts
from app.services.llm import answer
from app.services.finance import annual_series,growth_rates
from pydantic import BaseModel,Field

class Ask(BaseModel):
    ticker:str=Field(min_length=1,max_length=16)
    question:str=Field(min_length=3,max_length=2000)

app=FastAPI(title="Financial Research Agent",version="2.0.0")
STATIC=Path(__file__).parent/"static"

@app.get("/")
def home(): return FileResponse(STATIC/"index.html")
@app.get("/health")
def health(): return {"status":"ok","version":"2.0.0"}


@app.get("/companies")
def companies(db=Depends(get_db)):
    rows=db.scalars(select(Company).order_by(Company.name)).all()
    return [{"ticker":x.ticker,"name":x.name} for x in rows]

@app.get("/companies/{ticker}/summary")
def summary(ticker:str,db=Depends(get_db)):
    co=db.scalar(select(Company).where(Company.ticker==ticker.upper()))
    if not co: raise HTTPException(404,"Company not ingested.")
    filings=db.scalar(select(func.count(Filing.id)).where(Filing.company_id==co.id))
    chunks=db.scalar(select(func.count(FilingChunk.id)).join(Filing).where(Filing.company_id==co.id))
    return {"ticker":co.ticker,"name":co.name,"cik":co.cik,"filings":filings,"chunks":chunks}

@app.post("/ask")
def ask(req:Ask,db=Depends(get_db)):
    t=time.perf_counter();ticker=req.ticker.upper()
    if not db.scalar(select(Company).where(Company.ticker==ticker)):
        raise HTTPException(404,f"{ticker} has not been ingested.")
    route=route_question(req.question)
    passages=retrieve(db,ticker,req.question) if route in {"rag","hybrid"} else []
    facts=get_facts(db,ticker,req.question) if route in {"structured","hybrid"} else []
    evidence=[f"[{x['source_id']}] {x['form']} filed {x['filed_at']}\n{x['text']}" for x in passages]
    if facts:evidence.append("SEC XBRL FACTS:\n"+"\n".join(
        f"{x['concept']} | {x['end']} | {x['value']} {x['unit']} | {x['form']}" for x in facts))
    if not evidence:raise HTTPException(404,"No evidence available.")
    return {"answer":answer(req.question,"\n\n".join(evidence)),"route":route,
      "citations":[{"source_id":x["source_id"],"form":x["form"],"filed_at":x["filed_at"],
                    "source_url":x["source_url"],"section":x.get("section","other"),"excerpt":x["text"][:280]+"..."} for x in passages],
      "facts_used":facts,"calculations":{"annual_series":annual_series(facts),"growth_rates":growth_rates(annual_series(facts))},"latency_ms":int((time.perf_counter()-t)*1000)}

app.mount("/static",StaticFiles(directory=STATIC),name="static")
