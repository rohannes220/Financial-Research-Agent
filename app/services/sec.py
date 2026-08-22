import re,time,warnings
from datetime import date
import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from tenacity import retry,stop_after_attempt,wait_exponential
from sqlalchemy import select
from app.config import settings
from app.models import Company,Filing,FilingChunk,FinancialFact
from app.services.llm import embed
from app.services.sectioning import infer_section
DATA="https://data.sec.gov"; ARCH="https://www.sec.gov/Archives/edgar/data"
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
def headers():return {"User-Agent":settings.sec_user_agent,"Accept-Encoding":"gzip, deflate"}
@retry(stop=stop_after_attempt(3),wait=wait_exponential(min=1,max=8))
def get_json(url):
    with httpx.Client(timeout=30,headers=headers()) as c:
        r=c.get(url);r.raise_for_status();return r.json()
@retry(stop=stop_after_attempt(3),wait=wait_exponential(min=1,max=8))
def get_text(url):
    with httpx.Client(timeout=30,headers=headers()) as c:
        r=c.get(url);r.raise_for_status();return r.text
def company(db,ticker,cik,name=""):
    x=db.scalar(select(Company).where(Company.ticker==ticker.upper()))
    if not x:
        x=Company(ticker=ticker.upper(),cik=str(cik).zfill(10),name=name);db.add(x);db.commit();db.refresh(x)
    return x
def recent(cik,forms,limit):
    d=get_json(f"{DATA}/submissions/CIK{str(cik).zfill(10)}.json");r=d["filings"]["recent"];out=[]
    for i,form in enumerate(r["form"]):
        if form not in forms:continue
        acc=r["accessionNumber"][i];plain=acc.replace("-","");cikplain=str(cik).lstrip("0")
        out.append({"name":d.get("name",""),"accession":acc,"form":form,"filed":r["filingDate"][i],
                    "url":f"{ARCH}/{cikplain}/{plain}/{r['primaryDocument'][i]}"})
        if len(out)>=limit:break
    return out
def clean_html(html):
    s=BeautifulSoup(html,"lxml")
    for t in s(["script","style"]):t.decompose()
    return re.sub(r"\s+"," ",s.get_text(" ",strip=True))
def chunks(text,size=4500,overlap=600):
    out=[];start=0
    while start<len(text):
        end=min(len(text),start+size)
        if end<len(text):
            b=text.rfind(". ",start+int(size*.65),end)
            if b>start:end=b+1
        x=text[start:end].strip()
        if len(x)>300:out.append(x)
        if end>=len(text):break
        start=max(start+1,end-overlap)
    return out
def ingest_filings(db,ticker,cik,forms,limit):
    rows=recent(cik,forms,limit);co=company(db,ticker,cik,rows[0]["name"] if rows else "")
    for row in rows:
        if db.scalar(select(Filing).where(Filing.accession==row["accession"])):continue
        parts=chunks(clean_html(get_text(row["url"])))
        f=Filing(company_id=co.id,accession=row["accession"],form=row["form"],
                 filed_at=date.fromisoformat(row["filed"]),source_url=row["url"])
        db.add(f);db.commit();db.refresh(f)
        for start in range(0,len(parts),20):
            batch=parts[start:start+20];vectors=embed(batch)
            for j,(txt,vec) in enumerate(zip(batch,vectors),start=start):
                db.add(FilingChunk(filing_id=f.id,chunk_index=j,text=txt,section=infer_section(txt),embedding=vec))
            db.commit()
        time.sleep(.12)
def ingest_companyfacts(db,ticker,cik):
    co=company(db,ticker,cik)
    d=get_json(f"{DATA}/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json")
    db.query(FinancialFact).filter(FinancialFact.company_id==co.id).delete();db.commit()
    for taxonomy,concepts in d.get("facts",{}).items():
        for concept,meta in concepts.items():
            for unit,obslist in meta.get("units",{}).items():
                if unit not in {"USD","shares","USD/shares"}:continue
                for o in obslist:
                    if o.get("form") not in {"10-K","10-Q"} or "val" not in o or "end" not in o:continue
                    try:
                        db.add(FinancialFact(company_id=co.id,taxonomy=taxonomy,concept=concept,
                         label=meta.get("label",""),unit=unit,value=float(o["val"]),
                         start=date.fromisoformat(o["start"]) if o.get("start") else None,
                         end=date.fromisoformat(o["end"]),fy=o.get("fy"),fp=o.get("fp"),
                         form=o.get("form"),accession=o.get("accn")))
                    except (ValueError,TypeError):pass
    db.commit()
