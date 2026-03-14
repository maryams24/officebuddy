# officebuddy_main.py
import streamlit as st
import datetime as dt
from flows import FLOWS, get_next_step
from kb_utils import upload_policies, search_kb

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
if "kb_docs" not in st.session_state:
    st.session_state["kb_docs"] = []
if "last_output" not in st.session_state:
    st.session_state["last_output"] = ""

# =========================
# Sidebar: upload policy files
st.sidebar.subheader("Upload policies/FAQs")
uploaded_files = st.sidebar.file_uploader(
    "Upload .txt or .md", type=["txt", "md"], accept_multiple_files=True
)
if uploaded_files:
    st.session_state.kb_docs = upload_policies(uploaded_files)
    st.sidebar.success(f"Loaded {len(uploaded_files)} file(s)")

# =========================
# Chat input
user_text = st.chat_input("Ask anything office-related (e.g., raise a ticket, leave request)")

def bot_reply(text):
    text_lower = text.lower().strip()
    
    # Commands
    if text_lower in ["/help", "help"]:
        return (
            "I can help with:\n"
            "- Raise a ticket: type 'raise ticket'\n"
            "- Leave request: type 'leave request'\n"
            "- Draft email: type 'draft email'\n"
            "- Policy questions: type your question after uploading policy files\n"
            "- Commands: /cancel, /clear"
        )
    if text_lower == "/cancel":
        st.session_state.active_flow = None
        st.session_state.flow_data = {}
        return "Flow cancelled."
    if text_lower == "/clear":
        st.session_state.messages = []
        st.session_state.last_output = ""
        return "Chat cleared."
    
    # Active flow
    if st.session_state.active_flow:
        flow_key = st.session_state.active_flow
        step = get_next_step(FLOWS[flow_key], st.session_state.flow_data)
        if step:
            # Save user answer
            st.session_state.flow_data[step.field] = text
            # Get next step
            step = get_next_step(FLOWS[flow_key], st.session_state.flow_data)
            if step:
                return step.prompt
            else:
                # Flow done
                st.session_state.active_flow = None
                output_text = FLOWS[flow_key].formatter(st.session_state.flow_data)
                st.session_state.last_output = output_text
                return output_text
    
    # Start flows
    if "raise ticket" in text_lower:
        st.session_state.active_flow = "ticket"
        st.session_state.flow_data = {s.field: "" for s in FLOWS["ticket"].steps}
        return get_next_step(FLOWS["ticket"], st.session_state.flow_data).prompt
    
    if "leave request" in text_lower:
        st.session_state.active_flow = "leave"
        st.session_state.flow_data = {s.field: "" for s in FLOWS["leave"].steps}
        return get_next_step(FLOWS["leave"], st.session_state.flow_data).prompt
    
    if "draft email" in text_lower:
        st.session_state.active_flow = "email"
        st.session_state.flow_data = {s.field: "" for s in FLOWS["email"].steps}
        return get_next_step(FLOWS["email"], st.session_state.flow_data).prompt
    
    # KB search
    if st.session_state.kb_docs:
        hits = search_kb(st.session_state.kb_docs, text)
        if hits:
            return "\n\n".join(hits)
    
    return "I can help with office tasks: tickets, leave, email templates, policy questions. Type /help."

# =========================
# Display chat
if user_text:
    st.session_state.messages.append({"role": "user", "text": user_text})
    reply = bot_reply(user_text)
    st.session_state.messages.append({"role": "bot", "text": reply})

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["text"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["text"])

# =========================
# Download button for last completed flow
if st.session_state.last_output.strip():
    st.download_button(
        label="Download Last Output",
        data=st.session_state.last_output,
        file_name="officebuddy_output.txt",
        mime="text/plain"
    )
