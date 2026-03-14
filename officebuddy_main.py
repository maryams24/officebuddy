import streamlit as st
import datetime as dt

# =========================
# Page config
st.set_page_config(page_title="OfficeBuddy • Office Helpdesk Bot", layout="centered")

st.title("OfficeBuddy • Office Helpdesk Bot")
st.write("Hi! I can help with tickets, leave requests, email templates, and policy questions.")
st.write("Type /help for guidance.")

# =========================
# Session state init
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "active_flow" not in st.session_state:
    st.session_state["active_flow"] = None
if "flow_data" not in st.session_state:
    st.session_state["flow_data"] = {}
if "step_index" not in st.session_state:
    st.session_state["step_index"] = 0
if "kb_docs" not in st.session_state:
    st.session_state["kb_docs"] = []

# =========================
# Sidebar: upload policy files
st.sidebar.subheader("Upload policies/FAQs")
uploaded_files = st.sidebar.file_uploader(
    "Upload .txt or .md", type=["txt", "md"], accept_multiple_files=True
)
if uploaded_files:
    st.session_state.kb_docs = []
    for f in uploaded_files:
        content = f.read().decode("utf-8", errors="ignore")
        st.session_state.kb_docs.append(content)
    st.sidebar.success(f"Loaded {len(uploaded_files)} file(s)")

# =========================
# Define flows
TICKET_STEPS = [
    {"field": "Category", "prompt": "Ticket category? (IT/HR/Facilities/Payroll/Other)"},
    {"field": "Summary", "prompt": "Short summary (one line)"},
    {"field": "Business Impact", "prompt": "Business impact (who/what is blocked)"},
    {"field": "Urgency", "prompt": "Urgency (Low/Medium/High/Critical)"},
]

LEAVE_STEPS = [
    {"field": "Leave Type", "prompt": "Leave type? (PTO/Sick/Personal/Other)"},
    {"field": "Dates", "prompt": "Leave dates (e.g., 2026-03-15 to 2026-03-17)"},
    {"field": "Coverage Plan", "prompt": "Coverage plan during your leave"},
    {"field": "Manager", "prompt": "Manager name"},
]

EMAIL_STEPS = [
    {"field": "Subject", "prompt": "Email subject"},
    {"field": "Recipient", "prompt": "Recipient name/email"},
    {"field": "Context", "prompt": "Context or reason for email"},
    {"field": "Action", "prompt": "Action or approval needed"},
]

def format_flow_data(data: dict) -> str:
    return "\n".join([f"{k}: {v}" for k, v in data.items()])

# =========================
# Bot logic
def bot_reply(user_text: str) -> str:
    text = user_text.strip()
    text_lower = text.lower()

    # Commands
    if text_lower in ["/help", "help"]:
        return ("I can help with:\n"
                "- Raise a ticket: type 'raise ticket'\n"
                "- Leave request: type 'leave request'\n"
                "- Draft email: type 'draft email'\n"
                "- Policy questions: type your question after uploading policy files\n"
                "- Commands: /cancel, /clear, /download")

    if text_lower == "/cancel":
        st.session_state.active_flow = None
        st.session_state.flow_data = {}
        st.session_state.step_index = 0
        return "Flow cancelled. Start again by typing your request."

    if text_lower == "/clear":
        st.session_state.messages = []
        st.session_state.active_flow = None
        st.session_state.flow_data = {}
        st.session_state.step_index = 0
        return "Chat cleared."

    if text_lower == "/download":
        if st.session_state.active_flow is None and st.session_state.flow_data:
            ticket_text = format_flow_data(st.session_state.flow_data)
            st.download_button("Download Output", ticket_text, file_name="output.txt")
            return "Your output is ready to download."
        return "No completed ticket/email/leave request to download yet."

    # Active flow logic
    if st.session_state.active_flow:
        steps = {
            "ticket": TICKET_STEPS,
            "leave": LEAVE_STEPS,
            "email": EMAIL_STEPS
        }[st.session_state.active_flow]

        # Save user input for current step
        step_idx = st.session_state.step_index
        st.session_state.flow_data[steps[step_idx]["field"]] = text
        st.session_state.step_index += 1

        # Next step
        if st.session_state.step_index < len(steps):
            return steps[st.session_state.step_index]["prompt"]
        else:
            # Flow finished
            output = format_flow_data(st.session_state.flow_data)
            st.session_state.active_flow = None
            st.session_state.step_index = 0
            return f"All steps completed!\n\n{output}\n\nType /download to download this."

    # Start flows
    if "raise ticket" in text_lower:
        st.session_state.active_flow = "ticket"
        st.session_state.flow_data = {}
        st.session_state.step_index = 0
        return TICKET_STEPS[0]["prompt"]

    if "leave request" in text_lower:
        st.session_state.active_flow = "leave"
        st.session_state.flow_data = {}
        st.session_state.step_index = 0
        return LEAVE_STEPS[0]["prompt"]

    if "draft email" in text_lower:
        st.session_state.active_flow = "email"
        st.session_state.flow_data = {}
        st.session_state.step_index = 0
        return EMAIL_STEPS[0]["prompt"]

    # Policy KB search
    if st.session_state.kb_docs:
        results = [doc for doc in st.session_state.kb_docs if text_lower in doc.lower()]
        if results:
            return "\n\n".join(results)

    return "I can help with tickets, leave requests, email drafts, or policy questions. Type /help."

# =========================
# Display chat
user_input = st.chat_input("Ask anything office-related...")
if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    reply = bot_reply(user_input)
    st.session_state.messages.append({"role": "bot", "text": reply})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])
