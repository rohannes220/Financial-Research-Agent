import argparse
from app.db import SessionLocal
from app.services.sec import ingest_filings,ingest_companyfacts
p=argparse.ArgumentParser()
p.add_argument("--ticker",required=True);p.add_argument("--cik",required=True)
p.add_argument("--forms",default="10-K,10-Q");p.add_argument("--limit",type=int,default=3)
a=p.parse_args();db=SessionLocal()
try:
    ingest_filings(db,a.ticker,a.cik,{x.strip() for x in a.forms.split(",")},a.limit)
    ingest_companyfacts(db,a.ticker,a.cik)
    print("Done:",a.ticker.upper())
finally:db.close()
