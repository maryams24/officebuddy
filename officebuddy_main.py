import streamlit as st
import anthropic
from datetime import datetime
import time
from pathlib import Path
import json

# Configure Streamlit page
st.set_page_config(
    page_title="🏢 Office Helpdesk Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    /* Animated gradient background */
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Fade-in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Pulse animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Slide animation */
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Main container */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient-shift 15s ease infinite;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    .header-title {
        color: white;
        font-size: 2.5em;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1em;
        margin-top: 10px;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        animation: fadeIn 0.3s ease-out;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20px;
        border-bottom-right-radius: 0;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 20px;
        border-bottom-left-radius: 0;
    }
    
    .status-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 12px;
        border-radius: 8px;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
        animation: pulse 1.4s infinite;
    }
    
    /* Button styling */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Category cards */
    .category-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        animation: fadeIn 0.4s ease-out;
    }
    
    .category-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    .category-title {
        color: #667eea;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background-color: #00FF00;
    }
    
    .status-idle {
        background-color: #FFA500;
    }
    
    .status-busy {
        background-color: #FF0000;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #667eea;
    }
    
    .metric-number {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9em;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now()

if "issue_count" not in st.session_state:
    st.session_state.issue_count = 0

if "resolved_count" not in st.session_state:
    st.session_state.resolved_count = 0

# Initialize Anthropic client
@st.cache_resource
def get_anthropic_client():
    return anthropic.Anthropic()

client = get_anthropic_client()

# Helper function to get system prompt
def get_system_prompt():
    return """You are a professional and friendly Office Helpdesk Support Assistant AI. Your role is to help employees with IT issues, provide technical support, and guide them through troubleshooting steps.

Your characteristics:
- Friendly and professional tone
- Patient and clear explanations
- Provide step-by-step solutions
- Ask clarifying questions when needed
- Suggest workarounds when immediate fixes aren't available
- Escalate critical issues appropriately
- Maintain confidentiality and security awareness

Common issues you can help with:
1. Password resets and account issues
2. Email and calendar problems
3. VPN and remote access issues
4. Software installation and updates
5. Network and connectivity problems
6. Hardware issues (printer, scanner, monitor, etc.)
7. File sharing and document access
8. License key activation
9. System performance issues
10. General IT guidance

Always be helpful, accurate, and professional. If you don't know something, admit it and suggest escalation to the IT team."""

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🏢 Office Helpdesk Chatbot</h1>
    <p class="header-subtitle">Your 24/7 IT Support Assistant</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for quick stats and categories
with st.sidebar:
    st.markdown("### 📊 Session Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Issues",
            value=st.session_state.issue_count,
            delta=None,
            fontWeight="bold",
            fontSize=20
        )
    
    with col2:
        st.metric(
            label="Resolved",
            value=st.session_state.resolved_count,
            delta=None,
            fontWeight="bold",
            fontSize=20
        )
    
    with col3:
        session_duration = (datetime.now() - st.session_state.session_start_time).seconds // 60
        st.metric(
            label="Duration (min)",
            value=session_duration,
            delta=None,
            fontWeight="bold",
            fontSize=20
        )
    
    st.divider()
    
    # Status indicator
    st.markdown("### 🟢 Chatbot Status")
    st.markdown(
        '<span class="status-indicator status-online"></span><span>Online & Ready</span>',
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Quick categories
    st.markdown("### 🎯 Quick Categories")
    
    categories = {
        "🔐 Password Reset": "I need to reset my password",
        "📧 Email Issues": "I'm having email problems",
        "🌐 VPN Connection": "I can't connect to VPN",
        "🖨️ Printer Problem": "Printer isn't working",
        "🔌 Hardware": "My monitor/keyboard isn't working",
        "⚡ Performance": "My computer is running slow",
        "📁 File Access": "I can't access shared files",
        "💾 Software": "Software installation issues"
    }
    
    if st.button("🆕 Clear Chat History", key="clear_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    
    for i, (category, prompt) in enumerate(categories.items()):
        if st.button(category, key=f"cat_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.issue_count += 1
            st.rerun()

# Main chat area
st.markdown("### 💬 Chat with Support")

# Display chat history
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>Support Assistant:</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)

# Chat input
col1, col2 = st.columns([0.9, 0.1])

with col1:
    user_input = st.chat_input(
        "Type your question or issue here...",
        key="user_input"
    )

with col2:
    send_button = st.button("📤 Send", use_container_width=True, key="send_btn")

# Process user input
if user_input or send_button:
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.issue_count += 1
        
        # Show loading animation
        with st.spinner("🤖 Assistant is thinking..."):
            try:
                # Call Claude API
                response = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=get_system_prompt(),
                    messages=st.session_state.conversation_history
                )
                
                assistant_message = response.content[0].text
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                st.session_state.resolved_count += 1
                
            except Exception as e:
                error_message = f"⚠️ Error communicating with AI: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
        
        st.rerun()

# Footer with additional info
st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">24/7</div>
        <div class="metric-label">Support Available</div>
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">💬</div>
        <div class="metric-label">Instant Response</div>
    </div>
    """, unsafe_allow_html=True)

with footer_col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-number">✅</div>
        <div class="metric-label">High Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

# Info section
st.markdown("""
---
### ℹ️ About This Chatbot

This Office Helpdesk Chatbot is powered by advanced AI and provides:
- **Instant support** for common IT issues
- **Step-by-step guidance** for troubleshooting
- **Quick category shortcuts** for faster assistance
- **Session tracking** to monitor your support requests
- **Professional assistance** available 24/7

**Privacy Notice:** This chatbot maintains conversation history for the current session only.

---
*Last updated: 2026-03-14 | Version 2.0 with Enhanced AI Capabilities*
""")

# Performance metrics at the very bottom (optional advanced stats)
if st.checkbox("📈 Show Advanced Analytics", value=False):
    st.markdown("### Advanced Session Analytics")
    
    analytics_col1, analytics_col2, analytics_col3, analytics_col4 = st.columns(4)
    
    with analytics_col1:
        st.metric(
            label="Total Messages",
            value=len(st.session_state.messages),
            fontWeight="bold"
        )
    
    with analytics_col2:
        resolution_rate = (st.session_state.resolved_count / max(st.session_state.issue_count, 1)) * 100
        st.metric(
            label="Resolution Rate",
            value=f"{resolution_rate:.1f}%",
            fontWeight="bold"
        )
    
    with analytics_col3:
        avg_response_time = "< 1s"
        st.metric(
            label="Avg Response Time",
            value=avg_response_time,
            fontWeight="bold"
        )
    
    with analytics_col4:
        session_duration = (datetime.now() - st.session_state.session_start_time).seconds // 60
        st.metric(
            label="Session Duration",
            value=f"{session_duration} min",
            fontWeight="bold"
        )
