import streamlit as st
from datetime import datetime
import requests
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
    
    /* Action button */
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

# Knowledge base for quick responses
KNOWLEDGE_BASE = {
    "password": {
        "keywords": ["password", "reset", "login", "account", "forgot"],
        "response": """🔐 **Password Reset Guide**

Here's how to reset your password:

1. **Go to Login Page**: Visit the company login portal
2. **Click "Forgot Password"**: Look for this link below the login button
3. **Enter Your Email**: Type your company email address
4. **Check Your Email**: Look for a reset link (check spam folder too!)
5. **Create New Password**: Follow the link and set a new password
6. **Re-login**: Use your new password to access your account

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 number (0-9)
- At least 1 special character (!@#$%^&*)

⏱️ **Didn't receive email?**
- Wait 5 minutes for delivery
- Check spam/junk folder
- Try resetting again
- Contact IT if still having issues: support@company.com"""
    },
    
    "email": {
        "keywords": ["email", "outlook", "gmail", "mail", "inbox"],
        "response": """📧 **Email Troubleshooting**

**Problem: Can't access email**
1. Check internet connection
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try incognito mode (Ctrl+Shift+N)
4. Restart your browser
5. Try a different browser

**Problem: Email won't send**
1. Check recipient email address
2. Verify you have internet connection
3. Try waiting a few minutes
4. Sign out and sign back in
5. Check email quota hasn't been exceeded

**Problem: Missing emails**
1. Check "All Mail" and "Archive" folders
2. Look in "Spam" or "Junk" folder
3. Check email filters and rules
4. Search using sender name

**Quick Tips:**
✓ Restart Outlook/Gmail
✓ Check storage limits
✓ Verify account is synced
✓ Update browser to latest version

Need more help? Contact: support@company.com"""
    },
    
    "vpn": {
        "keywords": ["vpn", "remote", "connection", "network", "access"],
        "response": """🌐 **VPN Connection Guide**

**Step 1: Download VPN Client**
- Visit company.vpn.com
- Download the VPN application for your OS
- Install it (you may need admin privileges)

**Step 2: Open VPN Client**
- Launch the VPN application
- It's usually in your applications folder

**Step 3: Connect**
- Click "Connect" button
- Enter your company credentials
- Wait for "Connected" status

**Troubleshooting:**

❌ **"Connection Failed"**
- Check internet connection
- Restart VPN client
- Restart your computer
- Update VPN client software

❌ **"Invalid Credentials"**
- Verify username is correct
- Check Caps Lock is OFF
- Reset password if needed
- Contact IT support

❌ **"VPN Disconnects"**
- Check WiFi/network stability
- Update network drivers
- Disable firewall temporarily
- Try wired connection

**VPN Support:** support@company.com"""
    },
    
    "printer": {
        "keywords": ["printer", "print", "paper", "toner", "scanning"],
        "response": """🖨️ **Printer Troubleshooting**

**Step 1: Basic Checks**
✓ Check if printer is powered ON
✓ Check if cable is connected properly
✓ Verify printer is not in sleep mode
✓ Check for paper jams

**Step 2: Check Connection**
1. On your computer, go to: Settings → Devices → Printers
2. Look for your printer in the list
3. If not listed, click "Add a printer"

**Step 3: Clear Print Queue**
- Right-click printer → "Set as default"
- Settings → Devices → Printers → [Your Printer] → "Open queue"
- Click "Printer" menu → "Cancel all documents"

**Step 4: Reinstall Printer**
1. Remove printer from devices
2. Restart computer
3. Download latest driver from manufacturer
4. Reinstall printer with new driver

**Common Issues:**
- **Offline**: Restart printer and computer
- **Paper Jam**: Open all covers and remove jammed paper
- **No Toner**: Replace toner cartridge
- **Can't Find Network Printer**: Check WiFi connection, restart router

**Support:** IT Helpdesk - Ext. 5555"""
    },
    
    "hardware": {
        "keywords": ["hardware", "monitor", "keyboard", "mouse", "usb", "dock"],
        "response": """🔌 **Hardware Troubleshooting**

**MONITOR NOT WORKING**
1. Check monitor power cable
2. Verify monitor is turned ON
3. Check video cable is connected
4. Try a different power outlet
5. Restart computer with monitor OFF, then turn ON

**KEYBOARD/MOUSE NOT WORKING**
1. Check wireless connection (lights on?)
2. Replace batteries if wireless
3. Restart computer
4. Try USB port on different side
5. Update drivers: Settings → Device Manager

**USB DEVICES**
1. Unplug device completely
2. Wait 10 seconds
3. Plug back in
4. Try different USB port
5. Restart if needed

**DOCKING STATION ISSUES**
1. Disconnect all cables
2. Power cycle dock (off for 30 seconds)
3. Reconnect cables one by one
4. Update dock firmware if available
5. Restart computer

**HEADPHONES/SPEAKERS**
1. Check if muted (look for mute icon)
2. Adjust volume slider
3. Check sound settings in System
4. Restart audio driver
5. Test with different device

**Escalation:** If issue persists, contact IT"""
    },
    
    "performance": {
        "keywords": ["slow", "performance", "lag", "fast", "speed", "cpu"],
        "response": """⚡ **Performance Optimization**

**Why Is My Computer Slow?**

**Step 1: Check Running Programs**
1. Press Ctrl+Shift+Esc (Task Manager)
2. Look at CPU and RAM usage
3. Close unused applications
4. Restart computer

**Step 2: Free Up Storage**
- Go to Settings → Storage
- Delete temporary files
- Clear recycle bin
- Uninstall unused programs

**Step 3: Disable Startup Programs**
1. Task Manager → Startup tab
2. Right-click unnecessary programs
3. Select "Disable"
4. Restart computer

**Step 4: Check for Viruses**
- Run Windows Defender scan
- Run full antivirus scan
- Update virus definitions
- Restart computer

**Step 5: Update System**
1. Settings → Update & Security
2. Click "Check for updates"
3. Install all available updates
4. Restart if prompted

**Quick Speed Boost:**
✓ Restart computer (most effective!)
✓ Close unnecessary browser tabs
✓ Disable animations
✓ Update all drivers
✓ Check disk space (keep 10% free)

**Still Slow?** Contact IT for diagnostics"""
    },
    
    "files": {
        "keywords": ["file", "access", "share", "folder", "permissions", "document"],
        "response": """📁 **File & Document Access**

**CAN'T ACCESS SHARED FILES**

1. **Check Connection**
   - Verify you're on company network
   - Connect to VPN if remote
   - Check internet connection

2. **Verify Permissions**
   - Ask your manager for access
   - File owner may need to share it
   - Wait 15 minutes for permissions to update

3. **Map Network Drive** (Windows)
   - File Explorer → "This PC"
   - "Map network drive"
   - Enter server path (ask IT for location)
   - Enter credentials

4. **Access Shared Drive** (Mac)
   - Finder → Go → "Connect to Server"
   - Enter server address
   - Select drive and click Connect

**TROUBLE UPLOADING FILES**

✓ Check file size isn't too large
✓ Check internet connection
✓ Try different browser
✓ Clear cache and cookies
✓ Try incognito mode

**FILE PERMISSIONS ISSUES**

- Right-click file → Properties
- Go to Security tab
- Click Edit
- Add your username
- Select Full Control → Apply

**LOST FILES**

1. Check Recycle Bin (or Trash on Mac)
2. Use File Search (search all folders)
3. Contact IT for backup recovery

**Support:** IT Help - support@company.com"""
    },
    
    "software": {
        "keywords": ["software", "install", "application", "app", "license", "program"],
        "response": """💾 **Software Installation & License**

**HOW TO INSTALL SOFTWARE**

1. **Request Access**
   - Submit ticket to IT
   - Provide software name and version
   - Wait for approval

2. **Download Software**
   - Check company software store
   - Download from official vendor
   - Save to your Downloads folder

3. **Install**
   - Run installer
   - Accept license agreement
   - Follow on-screen prompts
   - Complete installation
   - Restart computer if needed

**LICENSE KEY ACTIVATION**

1. Open software
2. Go to Help → Activate or Register
3. Paste your license key
4. Follow activation steps
5. Software should now be unlocked

**LICENSE KEY NOT WORKING**

- Check key is correct (copy-paste to avoid typos)
- Verify license hasn't expired
- Check you have latest software version
- Try activating online vs offline
- Contact software vendor

**UNINSTALL SOFTWARE**

1. Go to Settings → Apps → Apps & Features
2. Find your software
3. Click it and select "Uninstall"
4. Follow uninstall wizard
5. Restart computer

**COMMON ISSUES**

❌ "Installation Failed" → Run as Administrator
❌ "Product Key Invalid" → Check with IT
❌ "Program Won't Open" → Reinstall or update
❌ "Slow Performance" → Check system requirements

**IT Help:** support@company.com"""
    },
    
    "general": {
        "keywords": ["help", "issue", "problem", "need", "support"],
        "response": """👋 **Welcome to IT Support!**

I can help you with:
- 🔐 Password resets and account issues
- 📧 Email and calendar problems
- 🌐 VPN and remote access
- 🖨️ Printer and scanner issues
- 🔌 Hardware troubleshooting
- ⚡ Computer performance optimization
- 📁 File access and sharing
- 💾 Software installation and licenses
- 🎓 General IT guidance

**How to get the best help:**
1. Be specific about your issue
2. Describe what you've already tried
3. Mention any error messages
4. Tell us your device/OS

**Quick Links:**
- IT Portal: support.company.com
- Emergency Support: Ext. 5555
- Chat Hours: 24/7 (AI) / 9-5 (Staff)

**What would you like help with today?**"""
    }
}

def get_response_from_knowledge_base(user_input):
    """Search knowledge base for relevant response"""
    user_input_lower = user_input.lower()
    
    # Check each category
    for category, data in KNOWLEDGE_BASE.items():
        for keyword in data["keywords"]:
            if keyword in user_input_lower:
                return data["response"]
    
    # Default response
    return KNOWLEDGE_BASE["general"]["response"]

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🏢 Office Helpdesk Chatbot</h1>
    <p class="header-subtitle">Your 24/7 IT Support Assistant (No API Key Needed!)</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for quick stats and categories
with st.sidebar:
    st.markdown("### 📊 Session Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Issues", value=st.session_state.issue_count)
    
    with col2:
        st.metric(label="Resolved", value=st.session_state.resolved_count)
    
    with col3:
        session_duration = (datetime.now() - st.session_state.session_start_time).seconds // 60
        st.metric(label="Duration (min)", value=session_duration)
    
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
        st.session_state.issue_count += 1
        
        # Show loading animation
        with st.spinner("🤖 Assistant is thinking..."):
            # Get response from knowledge base
            assistant_message = get_response_from_knowledge_base(user_input)
            
            # Add assistant response to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            st.session_state.resolved_count += 1
        
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
        <div class="metric-label">No API Key Needed</div>
    </div>
    """, unsafe_allow_html=True)

# Info section
st.markdown("""
---
### ℹ️ About This Chatbot

This Office Helpdesk Chatbot provides:
- **Instant support** for common IT issues
- **Step-by-step guidance** for troubleshooting
- **Quick category shortcuts** for faster assistance
- **Session tracking** to monitor your support requests
- **Professional assistance** available 24/7
- **✅ No API Keys Required** - Works offline!

**Features:**
✓ Local knowledge base
✓ No internet required
✓ No API key setup
✓ Works instantly
✓ Fully customizable

**Privacy Notice:** This chatbot maintains conversation history for the current session only and doesn't send data anywhere.

---
*Last updated: 2026-03-14 | Version 3.0 (Open Version - No API Key Required)*
""")

# Advanced analytics
if st.checkbox("📈 Show Advanced Analytics", value=False):
    st.markdown("### Advanced Session Analytics")
    
    analytics_col1, analytics_col2, analytics_col3, analytics_col4 = st.columns(4)
    
    with analytics_col1:
        st.metric(label="Total Messages", value=len(st.session_state.messages))
    
    with analytics_col2:
        resolution_rate = (st.session_state.resolved_count / max(st.session_state.issue_count, 1)) * 100
        st.metric(label="Resolution Rate", value=f"{resolution_rate:.1f}%")
    
    with analytics_col3:
        st.metric(label="Avg Response Time", value="< 0.1s")
    
    with analytics_col4:
        session_duration = (datetime.now() - st.session_state.session_start_time).seconds // 60
        st.metric(label="Session Duration", value=f"{session_duration} min")
