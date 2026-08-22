from collections import defaultdict

def annual_series(facts:list[dict], concept_contains:str|None=None):
    rows=[x for x in facts if x.get("form")=="10-K" and (not concept_contains or concept_contains.lower() in x["concept"].lower())]
    by_end={}
    for x in rows:
        by_end.setdefault(x["end"],x)
    return [by_end[k] for k in sorted(by_end)]

def growth_rates(series:list[dict]):
    out=[]
    for prev,cur in zip(series,series[1:]):
        if prev["value"] not in (0,None):
            out.append({"from":prev["end"],"to":cur["end"],
                        "growth_pct":round((cur["value"]/prev["value"]-1)*100,2)})
    return out
