import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append('.')
import database
import auth
import agent
import memory

database.init_db()

st.set_page_config(
    page_title="Panchayat Seva Agent",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
<style>
    /* Main gradient header */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Auth card styling */
    .auth-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        max-width: 500px;
        margin: 0 auto;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .bot-message {
        background: #f0f2f6;
        color: #1a1a1a;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
    }
    
    /* Sidebar styling */
    .sidebar-profile {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* Notification styling */
    .notification-banner {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        font-weight: 600;
        padding: 10px 25px;
        transition: all 0.3s ease;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.profile = None
    st.session_state.messages = []
    st.session_state.first_message = True

def show_auth_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="auth-card">
            <div style="text-align: center;">
                <h1 style="color: #1e3c72; margin-bottom: 5px;">🏛️ Panchayat Seva Agent</h1>
                <p style="color: #666; font-size: 14px;">Your AI assistant for Kerala Government Services</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📋 Register"])
        
        with tab1:
            st.markdown("<p style='color: #666;'>Welcome back! Login to continue</p>", unsafe_allow_html=True)
            
            login_phone = st.text_input(
                "📱 Phone Number",
                placeholder="Enter 10 digit number",
                key="login_phone"
            )
            login_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                login_btn = st.button("🚀 Login", type="primary", use_container_width=True)
            
            if login_btn:
                if login_phone and login_password:
                    with st.spinner("Logging in..."):
                        result = auth.login_user(login_phone, login_password)
                    
                    if result['success']:
                        st.session_state.logged_in = True
                        st.session_state.user_id = result['user_id']
                        st.session_state.profile = result['profile']
                        st.success(f"✅ Welcome, {result['profile']['name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    st.warning("⚠️ Please fill all fields")
        
        with tab2:
            st.markdown("<p style='color: #666;'>Create your account to get started</p>", unsafe_allow_html=True)
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("**Personal Details**")
                reg_name = st.text_input("👤 Full Name", key="reg_name")
                reg_phone = st.text_input("📱 Phone Number", placeholder="10 digits", key="reg_phone")
                reg_password = st.text_input("🔒 Password", type="password", key="reg_password")
                reg_district = st.selectbox("📍 District", auth.KERALA_DISTRICTS, key="reg_district")
            
            with col_right:
                st.markdown("**Eligibility Details**")
                reg_category = st.selectbox("🏷️ Category", auth.CATEGORIES, key="reg_category")
                reg_income = st.number_input("💰 Annual Income (₹)", min_value=0, step=1000, key="reg_income")
                reg_age = st.number_input("🎂 Age", min_value=18, max_value=120, key="reg_age")
                reg_family = st.number_input("👨‍👩‍👧‍👦 Family Size", min_value=1, max_value=20, key="reg_family")
            
            reg_language = st.radio(
                "🗣️ Preferred Language",
                ["malayalam", "english"],
                horizontal=True,
                index=0,
                key="reg_language"
            )
            
            st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
            
            col_reg1, col_reg2, col_reg3 = st.columns([1, 2, 1])
            with col_reg2:
                register_btn = st.button("📝 Create Account", type="primary", use_container_width=True)
            
            if register_btn:
                if reg_name and reg_phone and reg_password:
                    data = {
                        'name': reg_name,
                        'phone': reg_phone,
                        'password': reg_password,
                        'district': reg_district,
                        'category': reg_category,
                        'income': reg_income,
                        'age': reg_age,
                        'family_size': reg_family,
                        'language': reg_language
                    }
                    
                    with st.spinner("Creating account..."):
                        result = auth.register_user(data)
                    
                    if result['success']:
                        st.success("🎉 Account created! Please login.")
                        st.rerun()
                    else:
                        for error in result['errors']:
                            st.error(f"❌ {error}")
                else:
                    st.warning("⚠️ Please fill all required fields")
        
        st.markdown("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <p style="color: #666; font-size: 13px;">
                <b>Get help with:</b><br>
                Birth/Death Certificate • Ration Card • Caste Certificate<br>
                Income Certificate • Government Schemes • FSSAI License • And more...
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_chat_ui():
    profile = st.session_state.profile
    
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-profile">
            <h3 style="color: #1e3c72; text-align: center;">👤 Profile</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="margin: 5px 0;"><b>Name:</b> {profile.get('name', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>📍 District:</b> {profile.get('district', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>🏷️ Category:</b> {profile.get('category', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>💰 Income:</b> ₹{profile.get('income', 0):,}</p>
            <p style="margin: 5px 0;"><b>👥 Family:</b> {profile.get('family_size', 0)} members</p>
            <p style="margin: 5px 0;"><b>🗣️ Language:</b> {profile.get('language', 'malayalam').title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("⚙️ Settings"):
            new_lang = st.selectbox(
                "Language",
                ["malayalam", "english"],
                index=["malayalam", "english"].index(profile.get('language', 'malayalam'))
            )
            if new_lang != profile.get('language'):
                database.update_user_profile(st.session_state.user_id, {'language': new_lang})
                st.session_state.profile['language'] = new_lang
                st.success("Language updated!")
        
        notifications = database.get_unread_notifications(st.session_state.user_id)
        if notifications:
            st.markdown("""
            <div class="notification-banner">
                <b>📢 Notifications</b><br>
                You have """ + str(len(notifications)) + """ new message(s)
            </div>
            """, unsafe_allow_html=True)
            for n in notifications:
                with st.expander(f"📢 {n['scheme_name']}"):
                    st.write(n.get('message_ml') or n.get('message_en', ''))
                    if st.button("✓ Mark as read", key=f"read_{n['id']}"):
                        database.mark_notification_read(n['id'])
                        st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        col_log1, col_log2 = st.columns(2)
        with col_log1:
            st.button("🚪 Logout", use_container_width=True)
        with col_log2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.markdown("""
        <div style="position: fixed; bottom: 20px; text-align: center; color: #999; font-size: 11px;">
            Panchayat Seva Agent v1.0<br>
            Powered by AI Kyro
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Panchayat Seva Agent</h1>
        <p>Your AI assistant for Kerala Government Services</p>
    </div>
    """, unsafe_allow_html=True)
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="text-align: right; margin: 15px 0;">
                    <div class="user-message">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: left; margin: 15px 0;">
                    <div class="bot-message">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    prompt = st.chat_input("💬 Type your question in Malayalam or English...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("🤔 Thinking... / ചിന്തിക്കുന്നു..."):
            try:
                is_first = st.session_state.first_message
                response = agent.simple_process_message(
                    st.session_state.user_id,
                    prompt,
                    is_first
                )
                st.session_state.first_message = False
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"⚠️ Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        st.rerun()

if st.session_state.logged_in:
    show_chat_ui()
else:
    show_auth_screen()
