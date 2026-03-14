# kb_utils.py
from typing import List
import streamlit as st

def upload_policies() -> List[str]:
    st.sidebar.subheader("Upload HR/IT Policies (TXT/MD)")
    files = st.sidebar.file_uploader(
        "Upload .txt or .md files", 
        type=["txt","md"], 
        accept_multiple_files=True
    )
    texts = []
    if files:
        for f in files:
            try:
                texts.append(f.read().decode("utf-8", errors="ignore"))
            except:
                continue
        st.sidebar.success(f"Loaded {len(texts)} file(s)")
    return texts

def search_kb(query: str, kb_texts: List[str], top_k: int=3) -> str:
    query = query.lower()
    results = []
    for txt in kb_texts:
        if query in txt.lower():
            results.append(txt[:1000])  # return first 1000 chars as snippet
            if len(results) >= top_k:
                break
    if results:
        return "\n\n---\n\n".join(results)
    return ""
