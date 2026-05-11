import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os


import os

# ============================================
# AUTHENTICATION
# ============================================

# MUST BE FIRST! - Set page config before anything else
st.set_page_config(layout="wide")

# ============================================
# AUTHENTICATION
# ============================================
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

# Initialize session state
if 'authenticated' not in st.session_state:
    # Check if they have the cookie
    if 'auth_cookie' in st.context.cookies and st.context.cookies['auth_cookie'] == DASHBOARD_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.session_state.authenticated = False

# Authentication check
if not st.session_state.authenticated:
    st.title("🔒 AI Datacenter Tracker")
    st.markdown("### Login Required")
    
    # Use a unique key for the password input to avoid collisions across pages
    import uuid
    page_key = f"password_{str(uuid.uuid4())[:8]}"
    password_input = st.text_input("Enter password:", type="password", key=page_key)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Use a unique key for the login button
        btn_key = f"login_{str(uuid.uuid4())[:8]}"
        if st.button("🔓 Login", use_container_width=True, key=btn_key):
            if password_input == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                
                # Try to set a cookie if the component is available, otherwise rely on session state
                try:
                    import streamlit.components.v1 as components
                    # Set a cookie that expires in 30 days
                    components.html(
                        f'''
                        <script>
                            document.cookie = "auth_cookie={DASHBOARD_PASSWORD}; path=/; max-age=" + 30*24*60*60;
                            window.parent.postMessage("reload", "*");
                        </script>
                        ''',
                        height=0
                    )
                except:
                    pass
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    st.stop()

# ============================================
# AUTHENTICATED CONTENT BELOW
# ============================================

# Sidebar - External Links (only shown after auth)

    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")


    st.markdown("---")
    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")
    st.title("🔒 AI Datacenter Tracker")
    st.markdown("### Login Required")
    
    password_input = st.text_input("Enter password:", type="password", key="password")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔓 Login", use_container_width=True):
            if password_input == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    st.stop()

# ============================================
# AUTHENTICATED CONTENT BELOW
# ============================================


# Sidebar - External Links

    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")
st.title("📰 Intelligence Summary Blog")
st.markdown("An automated, reverse-chronological feed of the latest news and permitting updates discovered for your tracked AI Datacenters.")

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    st.warning("DATABASE_URL environment variable is missing.")
    st.stop()

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

@st.cache_resource
def get_engine():
    return create_engine(db_url)

engine = get_engine()

@st.cache_data(ttl=60)
def load_blog_data():
    query = """
    SELECT a.company, a.name, a.location, i.recent_news, i.last_updated
    FROM datacenter_intelligence i
    JOIN ai_datacenters a ON i.datacenter_id = a.id
    WHERE i.recent_news IS NOT NULL AND i.recent_news != ''
    ORDER BY i.last_updated DESC
    """
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_blog_data()

if df.empty:
    st.info("No updates available yet. The intelligence worker might still be running or hasn't found new data.")
    st.stop()

# Group by Date or just show reverse chronological feed
for _, row in df.iterrows():
    # Format the date nicely
    date_str = pd.to_datetime(row['last_updated']).strftime("%B %d, %Y - %H:%M UTC")
    
    with st.container():
        st.markdown(f"### {row['company']} — {row['name']}")
        st.caption(f"📍 {row['location']} &nbsp; • &nbsp; 🕒 Discovered: {date_str}")
        
        # The news is already formatted as markdown bullet links by the worker
        st.markdown(row['recent_news'])
        st.markdown("---")


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("pages/0_AI_Datacenter_Tracker.py", label="Kanban", icon="📋")
    st.page_link("pages/4_Capacity_Deals.py", label="Deals", icon="🤝")
with col2:
    st.page_link("pages/1_Table_View.py", label="Directory", icon="🏢")
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col3:
    st.page_link("pages/5_Projected_MW_Additions.py", label="Property MW", icon="⚡")
    st.page_link("pages/7_Guided_MW_Pipeline.py", label="Guided MW", icon="🎯")
with col4:
    st.page_link("pages/6_Revenue_Projections.py", label="Revenue", icon="💰")
    st.page_link("pages/8_Hardware_Tracker.py", label="Hardware", icon="🖥️")
with col5:
    st.page_link("pages/9_GPU_Pricing.py", label="GPU Pricing", icon="📈")
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
