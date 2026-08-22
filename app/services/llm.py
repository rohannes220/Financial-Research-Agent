from openai import OpenAI
from app.config import settings
def client():
    if not settings.openai_api_key: raise RuntimeError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=settings.openai_api_key)
def embed(texts:list[str])->list[list[float]]:
    r=client().embeddings.create(model=settings.openai_embed_model,input=texts)
    return [x.embedding for x in r.data]
def answer(question:str,evidence:str)->str:
    system=("You are a financial research assistant. Use ONLY supplied evidence. "
            "Never invent financial values. Cite filing source IDs in square brackets. "
            "Refer to structured values as SEC XBRL facts. If evidence is insufficient, say so. "
            "Separate observed facts from interpretation. Do not provide personalized investment advice.")
    r=client().chat.completions.create(model=settings.openai_chat_model,temperature=0,
        messages=[{"role":"system","content":system},
                  {"role":"user","content":f"QUESTION:\n{question}\n\nEVIDENCE:\n{evidence}"}])
    return r.choices[0].message.content or ""
