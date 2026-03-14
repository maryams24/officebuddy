# officebuddy_main.py
import streamlit as st
import datetime as dt
from flows import FLOWS, get_next_step, start_flow
from kb_utils import upload_policies, search_kb

# =========================
# Page setup
st.set_page_config(page_title="OfficeBuddy", layout="centered")
st.title("OfficeBuddy • Office Helper Chatbot")
st.write("I help with tickets, leave requests, emails, and HR/IT policies. Type /help for guidance.")

# =========================
# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "active_flow" not in st.session_state:
    st.session_state.active_flow = None

if "flow_data" not in st.session_state:
    st.session_state.flow_data = {}

# =========================
# Upload KB files
kb_texts = upload_policies()

# =========================
# Flow helpers
def start_flow(flow_name):
    st.session_state.active_flow = flow_name
    st.session_state.flow_data = {}

def get_next_step(flow):
    for step in flow.steps:
        if step.field not in st.session_state.flow_data:
            return step
    return None

# =========================
# Chat input
user_input = st.text_input("You:", key="input_text")

if user_input:
    ts = dt.datetime.now().strftime("%H:%M")
    reply = ""

    # Commands
    if user_input.lower() in ["/help", "help"]:
        reply = ("Try:\n"
                 "- raise ticket\n"
                 "- leave request\n"
                 "- draft email\n"
                 "- ask HR/IT policy questions (after uploading files)\n"
                 "Type /cancel to stop any active task.")
    elif user_input.lower() == "/cancel":
        st.session_state.active_flow = None
        st.session_state.flow_data = {}
        reply = "Active task cancelled."

    # Active flow
    elif st.session_state.active_flow:
        flow = FLOWS[st.session_state.active_flow]
        step = get_next_step(flow)
        if step:
            st.session_state.flow_data[step.field] = user_input
            next_step = get_next_step(flow)
            if next_step:
                reply = f"{next_step.prompt} {'(required)' if next_step.required else '(optional)'}"
            else:
                # Flow complete
                data = st.session_state.flow_data
                result_lines = [f"{k}: {v}" for k, v in data.items()]
                reply = f"✅ {flow.name} completed:\n" + "\n".join(result_lines)
                st.session_state.active_flow = None
                st.session_state.flow_data = {}
    # Policy search
    elif "policy" in user_input.lower() and kb_texts:
        kb_result = search_kb(user_input, kb_texts)
        reply = kb_result or "No matching policy found."

    # Start flows
    elif "raise ticket" in user_input.lower():
        start_flow("ticket")
        first_step = get_next_step(FLOWS["ticket"])
        reply = f"Let’s raise a ticket.\n{first_step.prompt} (required)"

    elif "leave request" in user_input.lower():
        start_flow("leave")
        first_step = get_next_step(FLOWS["leave"])
        reply = f"Let’s submit a leave request.\n{first_step.prompt} (required)"

    elif "draft email" in user_input.lower() or "write email" in user_input.lower():
        start_flow("email")
        first_step = get_next_step(FLOWS["email"])
        reply = f"Let’s draft an email.\n{first_step.prompt} (required)"

    else:
        reply = "I can help with tickets, leave requests, emails, and policies. Type /help for guidance."

    # Store chat
    st.session_state.chat_history.append({"role": "user", "text": user_input, "ts": ts})
    st.session_state.chat_history.append({"role": "assistant", "text": reply, "ts": ts})

# =========================
# Display chat
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f"**You ({chat['ts']}):** {chat['text']}")
    else:
        st.markdown(f"**OfficeBuddy ({chat['ts']}):** {chat['text']}")
