import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="Sajid SmartDine - AI Restaurant Assistant",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Backend URL configuration
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except (KeyError, FileNotFoundError):
    BACKEND_URL = "https://restaurant-assistant-fyp.onrender.com"  # ← CORRECT URL

# Initialize theme in session state
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Premium Modern CSS with Dual Theme Support
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --accent-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.18);
    }
    
    * {
        font-family: 'Inter', 'Poppins', sans-serif;
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    /* Dark Theme */
    .theme-dark .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e293b 100%);
        color: #e2e8f0;
    }
    
    .theme-dark .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    
    .theme-dark .stChatMessage {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    .theme-dark .chat-user {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
    }
    
    .theme-dark .chat-bot {
        background: rgba(51, 65, 85, 0.9);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        color: #e2e8f0;
    }
    
    .theme-dark .menu-item {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.15);
        color: #e2e8f0;
    }
    
    .theme-dark .metric-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(148, 163, 184, 0.15);
    }
    
    /* Light Theme */
    .theme-light .main {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 50%, #f8f9fa 100%);
        color: #1e293b;
    }
    
    .theme-light .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(203, 213, 225, 0.5);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    }
    
    .theme-light .stChatMessage {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(203, 213, 225, 0.4);
    }
    
    .theme-light .chat-user {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        color: white;
    }
    
    .theme-light .chat-bot {
        background: rgba(248, 250, 252, 0.95);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(203, 213, 225, 0.4);
        color: #334155;
    }
    
    .theme-light .menu-item {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(203, 213, 225, 0.4);
        color: #1e293b;
    }
    
    .theme-light .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(203, 213, 225, 0.4);
    }
    
    /* Header */
    .premium-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: glow 8s linear infinite;
    }
    
    @keyframes glow {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
    }
    
    .header-content {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        position: relative;
        z-index: 1;
    }
    
    .header-logo {
        font-size: 3em;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .header-text h1 {
        margin: 0;
        font-size: 2.2em;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(to right, #fff, #e0e7ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .header-text p {
        margin: 0.5rem 0 0 0;
        font-size: 1em;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(10px);
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-size: 0.95em;
        font-weight: 600;
        position: relative;
        z-index: 1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .status-dot {
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 12px #10b981;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    /* Chat Interface */
    .stChatMessage {
        border-radius: 20px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-user {
        border-radius: 20px 20px 4px 20px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    .chat-bot {
        border-radius: 20px 20px 20px 4px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        animation: slideInLeft 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Menu Items */
    .menu-item {
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .menu-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s;
    }
    
    .menu-item:hover::before {
        left: 100%;
    }
    
    .menu-item:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.25);
    }
    
    .menu-item h4 {
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.3em;
        letter-spacing: -0.5px;
    }
    
    .menu-item p {
        opacity: 0.8;
        margin: 0.6rem 0;
        line-height: 1.7;
        font-size: 0.95em;
    }
    
    .price-tag {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.15em;
        display: inline-block;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        letter-spacing: 0.5px;
    }
    
    .menu-badges {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 1.2rem;
    }
    
    .badge {
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        font-size: 0.85em;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    .badge-available {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    
    .badge-unavailable {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.45);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.02);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stChatInput > div > input {
        border-radius: 50px;
        border: 2px solid rgba(148, 163, 184, 0.3);
        padding: 0.8rem 1.5rem;
        font-size: 0.95em;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus,
    .stChatInput > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 0 20px rgba(102, 126, 234, 0.3);
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Order Cards */
    .order-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 1.8rem;
        margin: 1.2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .order-card:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .order-item {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        padding: 1rem 1.2rem;
        margin: 0.6rem 0;
        border-radius: 12px;
        border-left: 3px solid #667eea;
        transition: all 0.2s ease;
    }
    
    .order-item:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        transform: translateX(5px);
    }
    
    /* Status Badges */
    .status-badge {
        padding: 0.6rem 1.3rem;
        border-radius: 50px;
        font-weight: 700;
        display: inline-block;
        font-size: 0.85em;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .status-pending {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
    }
    
    .status-confirmed {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
    }
    
    .status-preparing {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        color: #1e40af;
    }
    
    .status-ready {
        background: linear-gradient(135deg, #ccfbf1 0%, #99f6e4 100%);
        color: #115e59;
    }
    
    .status-delivered {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        color: #14532d;
    }
    
    .status-cancelled {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        color: #991b1b;
    }
    
    /* Metric Cards */
    .metric-card {
        border-radius: 20px;
        padding: 2.2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.25);
    }
    
    .metric-value {
        font-size: 3.2em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .metric-label {
        opacity: 0.7;
        font-size: 1.05em;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Theme Toggle */
    .theme-toggle {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 1.5em;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .theme-toggle:hover {
        transform: scale(1.1) rotate(180deg);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Icons */
    .icon {
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        transition: all 0.3s ease;
    }
    
    .icon:hover {
        transform: scale(1.1);
        filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        opacity: 0.6;
        font-size: 0.9em;
        letter-spacing: 0.5px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Apply theme class to main container
theme_class = f"theme-{st.session_state.theme}"
st.markdown(f'<div class="{theme_class}">', unsafe_allow_html=True)

def make_request(endpoint, method="GET", data=None):
    """Make HTTP request to backend API"""
    try:
        url = f"{BACKEND_URL}/{endpoint.lstrip('/')}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to backend at {BACKEND_URL}")
        st.info("Make sure the backend server is running and the URL is correct.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid response from server")
        return None

def display_menu():
    """Display the restaurant menu"""
    st.markdown("## <span class='icon'>🍽️</span> Our Menu", unsafe_allow_html=True)
    
    menu_data = make_request("menu")
    
    if menu_data and menu_data.get("success"):
        menu_items = menu_data.get("menu", [])
        
        if not menu_items:
            st.info("No menu items available at the moment.")
            return
        
        categories = {}
        for item in menu_items:
            category = item.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in categories.items():
            st.markdown(f"### {category}")
            
            cols = st.columns(3)
            
            for idx, item in enumerate(items):
                with cols[idx % 3]:
                    available_badge = f'<span class="badge badge-available">✓ Available</span>' if item.get('available') else f'<span class="badge badge-unavailable">✗ Unavailable</span>'
                    
                    st.markdown(f"""
                    <div class="menu-item">
                        <h4>{item.get('name', 'Unknown')}</h4>
                        <p>{item.get('description', 'No description available')}</p>
                        <div class="price-tag">💰 PKR {item.get('price', 0)}</div>
                        <div class="menu-badges">
                            {available_badge}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("Quick Order", key=f"order_{item.get('item_id')}_{idx}", use_container_width=True):
                        st.session_state.quick_order = item.get('name')
                        st.session_state.page = "💬 Chat & Order"
                        st.rerun()
    else:
        st.error("Failed to load menu. Please try again later.")

def display_orders():
    """Display order history"""
    st.markdown("## <span class='icon'>📋</span> Order History", unsafe_allow_html=True)
    
    orders_data = make_request("orders?limit=20")
    
    if orders_data and orders_data.get("success"):
        orders = orders_data.get("orders", [])
        
        if not orders:
            st.info("No orders found.")
            return
        
        for order in orders:
            status = order.get('status', 'Unknown')
            status_class = f"status-{status.lower()}"
            
            with st.expander(f"🎫 Order #{order.get('order_id', 'Unknown')[:20]} - PKR {order.get('total_price', 0)}", expanded=False):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"**👤 Customer:** {order.get('user', {}).get('name', 'Guest')}")
                    st.markdown(f'**📊 Status:** <span class="status-badge {status_class}">{status}</span>', unsafe_allow_html=True)
                    st.markdown(f"**💰 Total:** PKR {order.get('total_price', 0)}")
                    
                    created_at = order.get('created_at', 'Unknown')
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    st.markdown(f"**🕐 Created:** {created_at}")
                
                with col2:
                    st.markdown("**🛒 Items:**")
                    for item in order.get('items', []):
                        st.markdown(f"""
                        <div class="order-item">
                            <strong>{item.get('quantity', 1)}x {item.get('name', 'Unknown')}</strong> - PKR {item.get('total_price', 0)}
                        </div>
                        """, unsafe_allow_html=True)
                
                if order.get('original_message'):
                    st.markdown(f"**💬 Original Message:** *'{order['original_message']}'*")
                
                st.markdown("---")
                
                col_status1, col_status2 = st.columns([3, 1])
                
                with col_status1:
                    new_status = st.selectbox(
                        "Update Status:",
                        ["Pending", "Confirmed", "Preparing", "Ready", "Delivered", "Cancelled"],
                        index=["Pending", "Confirmed", "Preparing", "Ready", "Delivered", "Cancelled"].index(order.get('status', 'Pending')),
                        key=f"status_{order.get('order_id')}"
                    )
                
                with col_status2:
                    if st.button("Update", key=f"update_{order.get('order_id')}", use_container_width=True):
                        update_data = {"status": new_status}
                        result = make_request(f"orders/{order.get('order_id')}/status", "PUT", update_data)
                        
                        if result and result.get("success"):
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
                        else:
                            st.error("Failed to update status")
    else:
        st.error("Failed to load orders. Please try again later.")

def chat_interface():
    """Main chat interface for placing orders"""
    st.markdown("## <span class='icon'>💬</span> Chat with Sajid SmartDine AI", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! Welcome to Sajid SmartDine. You can order food by saying something like 'I want 2 pizzas and 1 coke' or ask me to 'show menu' to see available items."}
        ]
    
    # Handle quick order from menu - FIXED VERSION
    if "quick_order" in st.session_state and st.session_state.quick_order:
        quick_item = st.session_state.quick_order
        user_message = f"I want 1 {quick_item}"
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # Process the order with loading indicator
        with st.spinner("Processing your quick order..."):
            order_data = {"message": user_message}
            result = make_request("order", "POST", order_data)
            
            if result:
                if result.get("success"):
                    # Check if it's an order
                    if result.get("intent") == "order_food" and result.get("order"):
                        order = result["order"]
                        response = result.get("response", "Order processed successfully!")
                        
                        # Create detailed response message
                        detailed_response = f"{response}\n\n"
                        detailed_response += f"📦 **Order Details:**\n"
                        detailed_response += f"🎫 Order ID: `{order.get('order_id')}`\n"
                        detailed_response += f"💰 Total: PKR {order.get('total_price')}\n"
                        detailed_response += f"📊 Status: {order.get('status')}\n\n"
                        detailed_response += f"🛒 **Items:**\n"
                        for item in order.get('items', []):
                            detailed_response += f"  • {item['quantity']}x {item['name']} @ PKR {item['unit_price']} = PKR {item['total_price']}\n"
                        
                        # Add the detailed response to messages
                        st.session_state.messages.append({"role": "assistant", "content": detailed_response})
                    else:
                        response = result.get("response", "Thank you for your message!")
                        st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    error_msg = f"Sorry, I couldn't process that: {result.get('error', 'Unknown error')}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                error_msg = "Sorry, I'm having trouble connecting right now. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear the quick order flag and rerun
        st.session_state.quick_order = None
        st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(f'<div class="chat-user">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-user">{prompt}</div>', unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            with st.spinner("Processing your order..."):
                order_data = {"message": prompt}
                result = make_request("order", "POST", order_data)
                response = ""
                
                if result:
                    if result.get("success"):
                        if result.get("intent") == "order_food" and result.get("order"):
                            order = result["order"]
                            response = result.get("response", "Order processed successfully!")
                            
                            st.markdown(f'<div class="chat-bot">{response}</div>', unsafe_allow_html=True)
                            
                            with st.expander("📦 Order Summary", expanded=True):
                                st.markdown(f"**🎫 Order ID:** `{order.get('order_id')}`")
                                st.markdown(f"**💰 Total:** PKR {order.get('total_price')}")
                                st.markdown(f"**📊 Status:** {order.get('status')}")
                                st.markdown("**🛒 Items:**")
                                
                                for item in order.get('items', []):
                                    st.write(f"- {item['quantity']}x {item['name']} @ PKR {item['unit_price']} = PKR {item['total_price']}")
                        
                        elif result.get("intent") == "show_menu" and result.get("menu"):
                            response = result.get("response", "Here's our menu:")
                            st.markdown(f'<div class="chat-bot">{response}</div>', unsafe_allow_html=True)
                            
                            for item in result["menu"]:
                                if item.get("available"):
                                    st.write(f"• {item['name']} - PKR {item['price']}")
                                    if item.get("description"):
                                        st.caption(item["description"])
                        
                        else:
                            response = result.get("response", "Thank you for your message!")
                            st.markdown(f'<div class="chat-bot">{response}</div>', unsafe_allow_html=True)
                    else:
                        error_msg = f"Sorry, I couldn't process that: {result.get('error', 'Unknown error')}"
                        st.error(error_msg)
                        response = error_msg
                else:
                    response = "Sorry, I'm having trouble connecting right now. Please try again."
                    st.error(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})

def system_status():
    """Display system status and health"""
    st.markdown("## <span class='icon'>🔧</span> System Status", unsafe_allow_html=True)
    
    health_data = make_request("health")
    
    if health_data:
        st.success("Backend is running")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔧 Service:** {health_data.get('service', 'Unknown')}")
            st.markdown(f"**📌 Version:** {health_data.get('version', 'Unknown')}")
        
        with col2:
            st.markdown(f"**💾 Database:** {health_data.get('database', 'Unknown')}")
            timestamp = health_data.get("timestamp", "Unknown")
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                except:
                    pass
            st.markdown(f"**⏰ Last Check:** {timestamp}")
    else:
        st.error("Backend is not responding")
        st.info(f"Backend URL: {BACKEND_URL}")
    
    st.markdown("### ⚙️ Configuration")
    st.code(f"Backend URL: {BACKEND_URL}", language="text")
    
    st.markdown("### 📊 Statistics")
    
    menu_data = make_request("menu")
    menu_count = len(menu_data.get("menu", [])) if menu_data and menu_data.get("success") else 0
    
    orders_data = make_request("orders?limit=1000")
    orders_count = len(orders_data.get("orders", [])) if orders_data and orders_data.get("success") else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{menu_count}</div>
            <div class="metric-label">Menu Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{orders_count}</div>
            <div class="metric-label">Total Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_text = "Online" if health_data else "Offline"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{'✓' if health_data else '✗'}</div>
            <div class="metric-label">Backend {status_text}</div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Initialize page state
    if "page" not in st.session_state:
        st.session_state.page = "💬 Chat & Order"
    
    health_data = make_request("health")
    is_online = health_data is not None
    
    st.markdown(f"""
    <div class="premium-header">
        <div class="header-content">
            <div class="header-logo">🍽️</div>
            <div class="header-text">
                <h1>Sajid SmartDine</h1>
                <p>AI-Powered Restaurant Assistant</p>
            </div>
        </div>
        <div class="status-indicator">
            <div class="status-dot"></div>
            <span>{'Online' if is_online else 'Offline'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Navigation Menu",
        [
            "💬 Chat & Order", 
            "🍽️ View Menu", 
            "📋 Order History",
            "🔧 System Status"
        ],
        index=[
            "💬 Chat & Order", 
            "🍽️ View Menu", 
            "📋 Order History",
            "🔧 System Status"
        ].index(st.session_state.page) if st.session_state.page in [
            "💬 Chat & Order", 
            "🍽️ View Menu", 
            "📋 Order History",
            "🔧 System Status"
        ] else 0,
        label_visibility="collapsed"
    )
    
    # Update page state
    st.session_state.page = page
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Theme")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🌙 Dark", use_container_width=True):
            st.session_state.theme = "dark"
            st.rerun()
    with col2:
        if st.button("☀️ Light", use_container_width=True):
            st.session_state.theme = "light"
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")
    backend_url = st.sidebar.text_input("Backend URL:", value=BACKEND_URL)
    
    if backend_url != BACKEND_URL:
        globals()['BACKEND_URL'] = backend_url.rstrip('/')
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.clear()
        st.session_state.theme = "dark"
        st.session_state.page = "💬 Chat & Order"
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        if "messages" in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! Welcome to Sajid SmartDine. How can I help you today?"}
            ]
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Try These Examples")
    sample_queries = [
        "I want 2 chicken pizzas",
        "Show me the menu",
        "Give me a burger and fries", 
        "I need 3 samosas and 2 teas",
        "What do you have?"
    ]
    
    for query in sample_queries:
        if st.sidebar.button(f"💬 {query}", key=f"sample_{hash(query)}", use_container_width=True):
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({"role": "user", "content": query})
            
            order_data = {"message": query}
            result = make_request("order", "POST", order_data)
            
            if result and result.get("success"):
                response = result.get("response", "Thank you for your message!")
            else:
                response = "Sorry, I'm having trouble right now. Please try again."
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.page = "💬 Chat & Order"
            st.rerun()
    
    # Display selected page
    if page == "💬 Chat & Order":
        chat_interface()
    elif page == "🍽️ View Menu":
        display_menu()
    elif page == "📋 Order History":
        display_orders()
    elif page == "🔧 System Status":
        system_status()
    
    st.markdown("""
    <div class="footer">
        Powered by Sajid SmartDine AI • Built with Streamlit, Flask & Firebase<br>
        Smart Restaurant Ordering Assistant v1.0
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()