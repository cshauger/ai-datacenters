import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Kanban Board", page_icon="📋", layout="wide")
st.title("📋 Datacenter Kanban Board")
st.markdown("Visualize datacenters grouped by Company and broken down by Pipeline Status.")

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

@st.cache_data(ttl=10)
def load_data():
    try:
        return pd.read_sql("SELECT * FROM ai_datacenters", engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.info("No data available to display.")
    st.stop()

# Fill missing values for cleaner display
df['status'] = df['status'].fillna('Unknown')
df['company'] = df['company'].fillna('Unknown')
df['estimated_capacity_mw'] = df['estimated_capacity_mw'].fillna(0)
df['location'] = df['location'].fillna('N/A')

# Target statuses order requested by user (plus Under construction)
target_statuses = [
    'Fully operational',
    'Operational/expanding',
    'Under construction',
    'Planned',
    'Decommissioned/abandoned'
]

# Drill down by company
companies = sorted(df['company'].unique().tolist())
selected_company = st.selectbox("🔍 Filter to a specific Company", ["All Companies"] + companies)

if selected_company != "All Companies":
    display_companies = [selected_company]
else:
    display_companies = companies

st.markdown("---")

# Render Kanban swimlanes per company
for company in display_companies:
    comp_df = df[df['company'] == company]
    if comp_df.empty:
        continue
        
    with st.expander(f"🏢 {company} ({len(comp_df)} properties)", expanded=True):
        cols = st.columns(len(target_statuses))
        
        for i, status in enumerate(target_statuses):
            with cols[i]:
                status_df = comp_df[comp_df['status'] == status]
                st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.85em; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;'>{status.upper()} ({len(status_df)})</div>", unsafe_allow_html=True)
                
                for _, row in status_df.iterrows():
                    mw_text = f"{int(row['estimated_capacity_mw'])} MW" if row['estimated_capacity_mw'] > 0 else "TBD MW"
                    
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #555; 
                        border-radius: 6px; 
                        padding: 10px; 
                        margin-bottom: 10px; 
                        background-color: #262626; 
                        color: #eee;
                        box-shadow: 1px 1px 3px rgba(0,0,0,0.3);
                    ">
                        <div style="font-weight: bold; font-size: 0.95em; margin-bottom: 4px; line-height: 1.2;">{row['name']}</div>
                        <div style="font-size: 0.8em; color: #bbb; line-height: 1.2;">📍 {row['location']}</div>
                        <div style="font-size: 0.85em; color: #4CAF50; font-weight: bold; margin-top: 6px;">⚡ {mw_text}</div>
                    </div>
                    """, unsafe_allow_html=True)


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("app.py", label="Data Editor", icon="🏢")
with col2:
    st.page_link("pages/1_Kanban_Board.py", label="Kanban Board", icon="📋")
with col3:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col4:
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
