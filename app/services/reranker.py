import re
STOP={"the","a","an","and","or","of","to","in","for","with","what","why","how","did","does","is","was"}
def lexical_score(query:str,text:str)->float:
    q={x for x in re.findall(r"[a-z0-9]+",query.lower()) if x not in STOP and len(x)>2}
    t=set(re.findall(r"[a-z0-9]+",text.lower()))
    return len(q&t)/max(1,len(q))
def rerank(query:str,items:list[dict],limit:int=6)->list[dict]:
    # Vector search supplies candidates; lexical overlap is a transparent second-stage signal.
    return sorted(items,key=lambda x:lexical_score(query,x["text"]),reverse=True)[:limit]
