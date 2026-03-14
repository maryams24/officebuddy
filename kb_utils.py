# kb_utils.py
def upload_policies(files):
    docs = []
    for f in files:
        content = f.read().decode("utf-8", errors="ignore")
        docs.append(content)
    return docs

def search_kb(docs, query):
    query_lower = query.lower()
    hits = []
    for doc in docs:
        if query_lower in doc.lower():
            hits.append(doc)
    return hits
