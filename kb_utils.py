# kb_utils.py
import re

STOPWORDS = {"the","a","an","and","or","to","for","of","in","on","at","is","are","am","with","by","from","this","that","it","as","be","we","you","i","our","your","please","pls","plz","can","could","would","need","want","help","me","my","hi","hello","hey","thanks","thank"}

def normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> set:
    words = set(normalize(text).split())
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}

def upload_policies(files):
    docs = []
    for f in files:
        content = f.read().decode("utf-8", errors="ignore")
        docs.append(content)
    return docs

def search_kb(docs, query, top_k=3):
    q = tokenize(query)
    if not q:
        return []
    results = []
    for d in docs:
        tokens = tokenize(d)
        if q & tokens:
            results.append(d)
    return results[:top_k]
