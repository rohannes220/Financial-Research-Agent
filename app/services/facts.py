from sqlalchemy import select
from app.models import Company,FinancialFact
ALIASES={
 "revenue":["RevenueFromContractWithCustomerExcludingAssessedTax","Revenues","SalesRevenueNet"],
 "operating income":["OperatingIncomeLoss"],"net income":["NetIncomeLoss","ProfitLoss"],
 "assets":["Assets"],"liabilities":["Liabilities"],"cash":["CashAndCashEquivalentsAtCarryingValue"]}
def get_facts(db,ticker,question):
    company=db.scalar(select(Company).where(Company.ticker==ticker.upper()))
    if not company:return []
    q=question.lower(); concepts=[]
    for phrase,names in ALIASES.items():
        if phrase in q: concepts+=names
    concepts=list(dict.fromkeys(concepts)) or ALIASES["revenue"]
    out=[]
    for concept in concepts:
        stmt=(select(FinancialFact).where(FinancialFact.company_id==company.id,
              FinancialFact.concept==concept,FinancialFact.form.in_(["10-K","10-Q"]))
              .order_by(FinancialFact.end.desc()).limit(8))
        for f in db.scalars(stmt):
            out.append({"concept":f.concept,"label":f.label,"value":f.value,"unit":f.unit,
                        "start":f.start.isoformat() if f.start else None,"end":f.end.isoformat(),
                        "fy":f.fy,"fp":f.fp,"form":f.form})
    seen=set(); clean=[]
    for x in out:
        k=(x["concept"],x["end"],x["value"],x["form"])
        if k not in seen: seen.add(k);clean.append(x)
    return clean[:24]
