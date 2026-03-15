import streamlit as st

import pandas as pd

import uuid

from datetime import datetime

import re

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


st.set_page_config(page_title="Office Helpdesk Assistant", page_icon="🛠️")



st.title("🛠️ Office Helpdesk Assistant")



# ---------------- NLP KEYWORDS ----------------



nlp_data = {

    "Access": ["login","password","account","locked"],

    "VPN": ["vpn","remote access"],

    "WiFi": ["wifi","internet","network","slow"],

    "Printer": ["printer","printing"],

    "Phishing": ["phishing","spam","suspicious"],

    "Software": ["install","software","application"]

}



solutions = {

"VPN":"Restart VPN and check internet connection.",

"WiFi":"Restart router or reconnect WiFi.",

"Access":"Reset password or check caps lock.",

"Printer":"Restart printer and clear print queue.",

"Phishing":"Do not click links and report email to IT.",

"Software":"Request installation access from IT.",

"General":"Please provide more details."

}



def _build_training_data(nlp_data_dict):
    X, y = [], []

    templates = [
        "I have an issue with {kw}",
        "Help me with {kw}",
        "{kw} not working",
        "Problem: {kw}",
        "My {kw} is not working",
        "Need help: {kw}",
        "Cannot use {kw}",
        "How to fix {kw}?"
    ]

    for cat, kws in nlp_data_dict.items():
        for kw in kws:
            X.append(kw); y.append(cat)
            for t in templates:
                X.append(t.format(kw=kw)); y.append(cat)

    general_examples = [
        "hello", "hi", "thanks", "thank you", "good morning",
        "need help", "can you help me", "it is not working", "something is broken",
        "please assist", "issue", "problem", "help"
    ]
    for ex in general_examples:
        X.append(ex); y.append("General")

    return X, y


def _train_model(extra_samples):
    X_train, y_train = _build_training_data(nlp_data)
    if extra_samples:
        for text, label in extra_samples:
            if text and label:
                X_train.append(str(text))
                y_train.append(str(label))
    model = Pipeline(steps=[
        ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
        ("clf", LogisticRegression(max_iter=2000))
    ])
    model.fit(X_train, y_train)
    return model


def _ensure_ml_state():
    if "labeled_samples" not in st.session_state:
        st.session_state.labeled_samples = []
    if "issue_model" not in st.session_state:
        st.session_state.issue_model = _train_model(st.session_state.labeled_samples)
    if "last_confidence" not in st.session_state:
        st.session_state.last_confidence = None
    if "last_top2" not in st.session_state:
        st.session_state.last_top2 = None


_ensure_ml_state()


def extract_entities(text):
    t = text or ""

    email = None
    m = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", t)
    if m:
        email = m.group(0)

    error_code = None
    m2 = re.search(r"\b(?:ERR|ERROR|E|CODE)[-:\s]?\d{2,6}\b", t, flags=re.IGNORECASE)
    if m2:
        error_code = m2.group(0)

    priority = "Normal"
    if re.search(r"\b(urgent|asap|immediately|right now|high priority)\b", t, flags=re.IGNORECASE):
        priority = "High"

    return {"Email": email, "Error": error_code, "Priority": priority}


def detect_issue_detail(text):
    model = st.session_state.issue_model
    probs = model.predict_proba([text])[0]
    classes = model.classes_
    order = probs.argsort()[::-1]
    top1_idx = int(order[0])
    top2_idx = int(order[1]) if len(order) > 1 else top1_idx
    top1 = str(classes[top1_idx])
    top2 = str(classes[top2_idx])
    conf1 = float(probs[top1_idx])
    conf2 = float(probs[top2_idx])
    return top1, conf1, top2, conf2


def detect_issue(text):
    top1, conf1, top2, conf2 = detect_issue_detail(text)
    st.session_state.last_confidence = conf1
    st.session_state.last_top2 = (top1, conf1, top2, conf2)
    if conf1 < 0.45:
        return "General"
    return top1



# ---------------- SESSION STORAGE ----------------



if "tickets" not in st.session_state:
    st.session_state.tickets=[]



if "current_issue" not in st.session_state:
    st.session_state.current_issue=None



if "current_category" not in st.session_state:
    st.session_state.current_category=None



if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]



# ---------------- TABS ----------------



tab1, tab2 = st.tabs(["💬 Chatbot Help", "🎫 Ticket System"])



# =====================================================
# CHATBOT TAB
# =====================================================



with tab1:



    st.subheader("💬 IT Helpdesk Chatbot")



    st.write("Ask questions related to office IT issues.")



    st.write("Quick Questions")



    col1,col2,col3 = st.columns(3)



    if col1.button("VPN not working"):
        user_input="vpn not working"
    elif col2.button("Cannot login"):
        user_input="cannot login"
    elif col3.button("Printer not printing"):
        user_input="printer not printing"
    else:
        user_input=None



    text_input = st.text_input("Ask your question")



    if text_input:
        user_input=text_input



    if user_input:



        category = detect_issue(user_input)



        solution = solutions.get(category)



        conf = st.session_state.last_confidence
        conf_pct = int(round((conf or 0.0) * 100))
        top2_info = st.session_state.last_top2

        entities = extract_entities(user_input)
        details = []
        if entities.get("Priority") == "High":
            details.append("Priority: High")
        if entities.get("Email"):
            details.append(f"Email: {entities['Email']}")
        if entities.get("Error"):
            details.append(f"Error: {entities['Error']}")

        response = f"Issue detected: {category} (confidence: {conf_pct}%)\n\nSuggested Fix: {solution}"

        if details:
            response = response + "\n\nDetected details: " + ", ".join(details)

        if category == "General" and top2_info:
            t1, c1, t2, c2 = top2_info
            response = response + f"\n\nPossible categories: {t1} ({int(round(c1*100))}%), {t2} ({int(round(c2*100))}%)"



        st.session_state.current_issue=user_input
        st.session_state.current_category=category



        st.session_state.chat_history.append(("User",user_input))
        st.session_state.chat_history.append(("Bot",response))



    for role,msg in st.session_state.chat_history:



        if role=="User":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**Bot:** {msg}")



    if st.session_state.current_issue:
        st.write("Improve the model (optional):")
        all_cats = sorted(list(nlp_data.keys()) + ["General"])
        default_idx = all_cats.index(st.session_state.current_category) if st.session_state.current_category in all_cats else all_cats.index("General")
        corrected = st.selectbox("Correct Category", all_cats, index=default_idx, key="corrected_category")
        if st.button("Save Feedback"):
            st.session_state.labeled_samples.append((st.session_state.current_issue, corrected))
            st.session_state.issue_model = _train_model(st.session_state.labeled_samples)
            st.success("Saved feedback. Model updated.")



    st.info("If issue is not solved go to Ticket System tab to create a ticket.")



# =====================================================
# TICKET TAB
# =====================================================



with tab2:



    st.subheader("🎫 Helpdesk Ticket System")



    if st.button("Create Ticket from Last Issue"):



        if st.session_state.current_issue:



            ticket_id = "HD-"+uuid.uuid4().hex[:6].upper()



            ticket = {

                "Ticket ID":ticket_id,

                "Time":datetime.now().strftime("%Y-%m-%d %H:%M"),

                "Category":st.session_state.current_category,

                "Issue":st.session_state.current_issue,

                "Status":"Open"

            }



            st.session_state.tickets.append(ticket)



            st.success(f"Ticket Created: {ticket_id}")



            st.session_state.current_issue=None



        else:
            st.warning("Ask the chatbot first before creating a ticket.")



    st.subheader("📊 Ticket Dashboard")



    df = pd.DataFrame(st.session_state.tickets)



    if not df.empty:



        col1,col2,col3 = st.columns(3)



        col1.metric("Open", len(df[df["Status"]=="Open"]))
        col2.metric("In Progress", len(df[df["Status"]=="In Progress"]))
        col3.metric("Resolved", len(df[df["Status"]=="Resolved"]))



    search = st.text_input("Search Ticket")



    if search and not df.empty:
        df = df[df["Issue"].str.contains(search, case=False)]



    status_filter = st.selectbox(
        "Filter Tickets",
        ["All","Open","In Progress","Resolved"]
    )



    if not df.empty and status_filter!="All":
        df = df[df["Status"]==status_filter]



    st.dataframe(df)



    st.subheader("Update Ticket Status")



    if not df.empty:



        ticket_ids = df["Ticket ID"].tolist()



        selected_ticket = st.selectbox("Ticket ID", ticket_ids)



        new_status = st.selectbox(
            "New Status",
            ["Open","In Progress","Resolved"]
        )



        if st.button("Update Status"):



            for t in st.session_state.tickets:
                if t["Ticket ID"]==selected_ticket:
                    t["Status"]=new_status



            st.success("Status Updated")



    st.subheader("Download Tickets")



    if not df.empty:



        csv = df.to_csv(index=False)



        st.download_button(
            "Download CSV",
            csv,
            "tickets.csv",
            "text/csv"
        )



        json_data = df.to_json(orient="records")



        st.download_button(
            "Download JSON",
            json_data,
            "tickets.json",
            "application/json"
        )
