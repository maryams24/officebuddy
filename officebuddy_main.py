import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import json
import csv
import io

st.set_page_config(page_title="Office Helpdesk Bot", page_icon="🛠️")

# ---------------- UI STYLE ----------------

st.markdown("""
<style>
.stApp {
background: linear-gradient(120deg,#eef2ff,#f0fdf4);
}

.ticket-card{
padding:12px;
border-radius:10px;
background:#ffffff;
border:1px solid #e5e7eb;
margin-bottom:10px;
}

</style>
""",unsafe_allow_html=True)

# ---------------- NLP TRAINING DATA ----------------

training_data={
"Access":["cannot login","password not working","account locked","login problem"],
"VPN":["vpn not connecting","vpn error","vpn disconnected"],
"WiFi":["wifi not working","internet slow","network disconnected"],
"Printer":["printer not printing","printer offline"],
"Software":["cannot install software","software issue"],
"Phishing":["suspicious email","phishing email"]
}

# ---------------- NLP CLASSIFIER ----------------

def predict_category(text):

    text=text.lower()

    best_category="General"
    best_score=0

    for category,sentences in training_data.items():

        score=0

        for sentence in sentences:

            for word in sentence.split():

                if word in text:
                    score+=1

        if score>best_score:
            best_score=score
            best_category=category

    return best_category

# ---------------- TROUBLESHOOTING ----------------

def quick_steps(cat):

    steps={
    "VPN":"🔹 Restart VPN\n🔹 Check internet\n🔹 Try hotspot",
    "WiFi":"🔹 Reconnect WiFi\n🔹 Restart laptop",
    "Access":"🔹 Check caps lock\n🔹 Reset password",
    "Printer":"🔹 Restart printer\n🔹 Clear print queue",
    "Software":"🔹 Request install access from IT",
    "Phishing":"🔹 Do not click links\n🔹 Report to IT"
    }

    return steps.get(cat,"Provide more details")

# ---------------- DATABASE ----------------

conn=sqlite3.connect("helpdesk.db",check_same_thread=False)
cur=conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets(
ticket_id TEXT,
created_at TEXT,
category TEXT,
issue TEXT,
status TEXT
)
""")

conn.commit()

# ---------------- TICKET FUNCTIONS ----------------

def create_ticket(issue):

    category=predict_category(issue)

    ticket_id="HD-"+uuid.uuid4().hex[:6].upper()

    time=datetime.now().strftime("%Y-%m-%d %H:%M")

    cur.execute(
    "INSERT INTO tickets VALUES (?,?,?,?,?)",
    (ticket_id,time,category,issue,"Open")
    )

    conn.commit()

    return ticket_id,category

def load_tickets():

    cur.execute("SELECT * FROM tickets ORDER BY created_at DESC")

    return cur.fetchall()

def update_ticket_status(ticket_id,status):

    cur.execute(
    "UPDATE tickets SET status=? WHERE ticket_id=?",
    (status,ticket_id)
    )

    conn.commit()

# ---------------- DOWNLOAD FUNCTIONS ----------------

def tickets_to_csv(tickets):

    buffer=io.StringIO()

    writer=csv.writer(buffer)

    writer.writerow(["Ticket ID","Created","Category","Issue","Status"])

    for t in tickets:
        writer.writerow(t)

    return buffer.getvalue()

def tickets_to_json(tickets):

    data=[]

    for t in tickets:

        data.append({
        "ticket_id":t[0],
        "created":t[1],
        "category":t[2],
        "issue":t[3],
        "status":t[4]
        })

    return json.dumps(data,indent=2)

# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:

    st.session_state.messages=[
    {"role":"assistant","content":"👋 **Office Helpdesk Bot**\n\nDescribe your issue.\nType **create ticket** when ready."}
    ]

if "last_issue" not in st.session_state:
    st.session_state.last_issue=None

# ---------------- HEADER ----------------

st.title("🛠️ Office Helpdesk Assistant")

# ---------------- TABS ----------------

chat_tab,ticket_tab=st.tabs(["💬 Chat","🎫 Tickets"])

# ---------------- CHAT ----------------

with chat_tab:

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input=st.chat_input("Describe your issue")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        text=user_input.lower().strip()

        if text=="create ticket":

            if st.session_state.last_issue:

                ticket_id,category=create_ticket(st.session_state.last_issue)

                response=f"""
🎫 **Ticket Created**

**Ticket ID:** {ticket_id}  
**Category:** {category}  
**Status:** Open

Check **Tickets tab** to manage tickets.
"""

            else:

                response="⚠️ Please describe the issue first."

        else:

            category=predict_category(user_input)

            steps=quick_steps(category)

            st.session_state.last_issue=user_input

            response=f"""
🔍 **Detected Issue:** {category}

💡 **Suggested Fix**
{steps}

If problem continues type **create ticket**
"""

        st.session_state.messages.append({"role":"assistant","content":response})

        st.rerun()

# ---------------- TICKETS DASHBOARD ----------------

with ticket_tab:

    st.header("🎫 Helpdesk Tickets")

    tickets=load_tickets()

# ---- STATS ----

    open_count=len([t for t in tickets if t[4]=="Open"])
    progress_count=len([t for t in tickets if t[4]=="In Progress"])
    resolved_count=len([t for t in tickets if t[4]=="Resolved"])

    col1,col2,col3=st.columns(3)

    col1.metric("🟡 Open",open_count)
    col2.metric("🔵 In Progress",progress_count)
    col3.metric("🟢 Resolved",resolved_count)

# ---- DOWNLOAD ----

    col1,col2=st.columns(2)

    with col1:

        st.download_button(
        "📥 Download CSV",
        data=tickets_to_csv(tickets),
        file_name="helpdesk_tickets.csv",
        mime="text/csv"
        )

    with col2:

        st.download_button(
        "📥 Download JSON",
        data=tickets_to_json(tickets),
        file_name="helpdesk_tickets.json",
        mime="application/json"
        )

# ---- FILTER ----

    status_filter=st.selectbox(
    "Filter Tickets",
    ["All","Open","In Progress","Resolved"]
    )

    if status_filter!="All":
        tickets=[t for t in tickets if t[4]==status_filter]

# ---- TICKET LIST ----

    for t in tickets:

        status_icon={
        "Open":"🟡",
        "In Progress":"🔵",
        "Resolved":"🟢"
        }

        icon=status_icon.get(t[4],"⚪")

        st.markdown(f"""
<div class="ticket-card">

<b>🎫 Ticket:</b> {t[0]} <br>
<b>📅 Created:</b> {t[1]} <br>
<b>📂 Category:</b> {t[2]} <br>
<b>📝 Issue:</b> {t[3]} <br>
<b>Status:</b> {icon} {t[4]}

</div>
""",unsafe_allow_html=True)

# ---- UPDATE STATUS ----

    st.subheader("🛠 Update Ticket Status")

    ticket_ids=[t[0] for t in load_tickets()]

    selected_ticket=st.selectbox("Ticket ID",ticket_ids)

    new_status=st.selectbox(
    "New Status",
    ["Open","In Progress","Resolved"]
    )

    if st.button("Update Status"):

        update_ticket_status(selected_ticket,new_status)

        st.success("Ticket status updated")

        st.rerun()