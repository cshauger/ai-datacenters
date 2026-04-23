import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os


import os

# ============================================
# AUTHENTICATION
# ============================================
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Authentication check
if not st.session_state.authenticated:
    st.set_page_config(page_title="Login - AI Datacenter Tracker", layout="centered")

# Sidebar - External Links
with st.sidebar:
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

st.set_page_config(page_title="Datacenter Intelligence", page_icon="📡", layout="wide")

# Sidebar - External Links
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")
st.title("📡 Datacenter Intelligence")
st.markdown("Automated news, permitting, and satellite imagery.")

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
def load_data():
    query = """
    SELECT a.company, a.name, a.location, a.status, a.estimated_capacity_mw, 
           i.latitude, i.longitude, i.satellite_image_url, i.recent_news, i.last_updated
    FROM ai_datacenters a
    LEFT JOIN datacenter_intelligence i ON a.id = i.datacenter_id
    ORDER BY a.company, a.name
    """
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("No data available to display. Has the intelligence worker run yet?")
    st.stop()

companies = sorted(df['company'].fillna('Unknown').unique().tolist())
selected_company = st.selectbox("🔍 Filter by Company", ["All Companies"] + companies)

if selected_company != "All Companies":
    df = df[df['company'] == selected_company]

for _, row in df.iterrows():
    with st.expander(f"{row['company']} - {row['name']} ({row['location']})"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"**Status:** {row['status']}")
            st.markdown(f"**Capacity:** {row['estimated_capacity_mw']} MW")
            st.markdown(f"**Last Updated:** {row['last_updated']}")
            st.markdown("### Recent News & Permitting")
            if pd.notna(row['recent_news']) and row['recent_news'].strip():
                st.markdown(row['recent_news'])
            else:
                st.write("No recent news found.")
                
        with col2:
            st.markdown("### Satellite Imagery")
            if pd.notna(row['satellite_image_url']):
                st.image(row['satellite_image_url'], caption=f"Lat: {row['latitude']}, Lng: {row['longitude']}", use_container_width=True)
            else:
                st.write("Satellite imagery not available (Geocoding failed or API key missing).")


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("app.py", label="Kanban Board", icon="📋")
with col2:
    st.page_link("pages/1_Table_View.py", label="Data Directory", icon="🏢")
with col3:
    st.page_link("pages/4_Capacity_Deals.py", label="Capacity Deals", icon="🤝")
with col4:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col5:
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
