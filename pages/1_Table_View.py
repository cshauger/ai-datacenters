import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import uuid


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

st.set_page_config(page_title="AI Datacenters Tracker", page_icon="🏢", layout="wide")

# Sidebar - External Links
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")
st.title("🏢 AI Datacenters Tracker")
st.markdown("Airtable-style interface connected to the DigitalOcean Managed Database.")

# Fetch the database URL that DigitalOcean automatically injects
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    st.warning("DATABASE_URL environment variable is missing. Please set it in the App Platform settings.")
    st.stop()

# SQLAlchemy requires the connection string to start with postgresql://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(db_url)
except Exception as e:
    st.error(f"Error creating database engine: {e}")
    st.stop()

# Load data from the database
@st.cache_data(ttl=10)
def load_data():
    try:
        return pd.read_sql("SELECT * FROM ai_datacenters ORDER BY company, name;", engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Render a read-only dataframe
    st.write("### Datacenters Directory")
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "id": None,  # Hides the ID column from the UI
            "source_url": st.column_config.LinkColumn("Source URL"),
        }
    )
else:
    st.info("No data found or table doesn't exist yet.")


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")

# External link to GPU Pricing Tracker
st.markdown("🎯 **Related Tools:**")
st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("pages/0_AI_Datacenter_Tracker.py", label="AI Datacenter Tracker", icon="📋")
with col2:
    st.page_link("pages/1_Table_View.py", label="Data Directory", icon="🏢")
with col3:
    st.page_link("pages/4_Capacity_Deals.py", label="Capacity Deals", icon="🤝")
with col4:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col5:
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
