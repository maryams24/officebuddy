import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# NLP MODEL IMPORTS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

st.set_page_config(page_title="Office Helpdesk Assistant", page_icon="🛠️")

st.title("🛠️ Office Helpdesk Assistant")

# ---------------- NLP TRAINING DATA ----------------

train_texts = [
"cannot login to account",
"password not working",
"account locked",
"login issue",
"vpn not connecting",
"vpn disconnected",
"remote access vpn issue",
"internet slow",
"wifi not working",
"network problem",
"printer not printing",
"printer offline",
"printing issue",
"suspicious email received",
"phishing email",
"spam email",
"cannot install software",
"software installation problem",
"application install error"
]

train_labels = [
"Access","Access","Access","Access",
"VPN","VPN","VPN",
"WiFi","WiFi","WiFi",
"Printer","Printer","Printer",
"Phishing","Phishing","Phishing",
"Software","Software","Software"
]

# ---------------- NLP MODEL ----------------

vectorizer = CountVectorizer()

X = vectorizer.fit_transform(train_texts)

model = MultinomialNB()

model.fit(X, train_labels)

# ---------------- SOLUTIONS ----------------

solutions = {
"VPN":"Restart VPN and check internet connection.",
"WiFi":"Restart router or reconnect WiFi.",
"Access":"Reset password or check caps lock.",
"Printer":"Restart printer and clear print queue.",
"Phishing":"Do not click links and report email to IT.",
"Software":"Request installation access from IT.",
"General":"Please provide more details."
}

# ---------------- NLP DETECTION ----------------

def detect_issue(text):

    text_vec = vectorizer.transform([text])

    prediction = model.predict(text_vec)

    return prediction[0]

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

    # ---- FAQ Buttons ----

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

    # ---- CHAT PROCESS ----

    if user_input:

        category = detect_issue(user_input)

        solution = solutions.get(category,"Please provide more details.")

        response = f"Issue detected: {category}\n\nSuggested Fix: {solution}"

        st.session_state.current_issue=user_input
        st.session_state.current_category=category

        st.session_state.chat_history.append(("User",user_input))
        st.session_state.chat_history.append(("Bot",response))

    # ---- CHAT DISPLAY ----

    for role,msg in st.session_state.chat_history:

        if role=="User":
            st.markdown(f"**You:** {msg}")
        else:
            st.markdown(f"**Bot:** {msg}")

    st.info("If issue is not solved go to Ticket System tab to create a ticket.")

# =====================================================
# TICKET TAB
# =====================================================

with tab2:

    st.subheader("🎫 Helpdesk Ticket System")

# ---------------- CREATE TICKET ----------------

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

# ---------------- DASHBOARD ----------------

    st.subheader("📊 Ticket Dashboard")

    df = pd.DataFrame(st.session_state.tickets)

    if not df.empty:

        col1,col2,col3 = st.columns(3)

        col1.metric("Open", len(df[df["Status"]=="Open"]))
        col2.metric("In Progress", len(df[df["Status"]=="In Progress"]))
        col3.metric("Resolved", len(df[df["Status"]=="Resolved"]))

# ---------------- SEARCH ----------------

    search = st.text_input("Search Ticket")

    if search and not df.empty:
        df = df[df["Issue"].str.contains(search, case=False)]

# ---------------- FILTER ----------------

    status_filter = st.selectbox(
        "Filter Tickets",
        ["All","Open","In Progress","Resolved"]
    )

    if not df.empty and status_filter!="All":
        df = df[df["Status"]==status_filter]

    st.dataframe(df)

# ---------------- UPDATE STATUS ----------------

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

# ---------------- DOWNLOAD ----------------

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