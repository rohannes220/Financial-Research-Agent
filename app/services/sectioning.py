import re
SECTIONS=[
 ("business",r"item\s+1[\.\s]+business"),
 ("risk_factors",r"item\s+1a[\.\s]+risk\s+factors"),
 ("mda",r"item\s+7[\.\s]+management.?s discussion and analysis"),
 ("financial_statements",r"item\s+8[\.\s]+financial statements")
]
def infer_section(text:str)->str:
    head=text[:1200].lower()
    for name,pattern in SECTIONS:
        if re.search(pattern,head,re.I): return name
    return "other"
