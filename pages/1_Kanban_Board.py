import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Kanban Board", page_icon="📋", layout="wide")
st.title("📋 Datacenter Kanban Board")
st.markdown("Visualize datacenters by status and drill down into specific companies.")

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

# Drill down by company
companies = sorted(df['company'].unique().tolist())
selected_company = st.selectbox("🔍 Select a Company to Drill Down", ["All Companies"] + companies)

if selected_company != "All Companies":
    df = df[df['company'] == selected_company]

st.markdown("---")

# Define standard Kanban columns (Statuses) in a logical progression
base_statuses = [
    'Planned',
    'Active/Planned',
    'Under Construction/Planned',
    'Under Construction',
    'Active/Under Construction',
    'Active/Expanding',
    'Active'
]

# Find any other statuses in the DB not in our standard list
db_statuses = df['status'].unique().tolist()
kanban_columns = base_statuses.copy()
for s in db_statuses:
    if s not in kanban_columns:
        kanban_columns.append(s)

# Create columns for the board
cols = st.columns(len(kanban_columns))

# Render the cards
for i, status in enumerate(kanban_columns):
    with cols[i]:
        # Count items for header
        status_df = df[df['status'] == status]
        st.markdown(f"**{status} ({len(status_df)})**")
        
        for _, row in status_df.iterrows():
            mw_text = f"{int(row['estimated_capacity_mw'])} MW" if row['estimated_capacity_mw'] > 0 else "TBD MW"
            
            st.markdown(f"""
            <div style="
                border: 1px solid #444; 
                border-radius: 6px; 
                padding: 12px; 
                margin-bottom: 12px; 
                background-color: #1e1e1e; 
                color: #eee;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            ">
                <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 4px;">{row['name']}</div>
                <div style="font-size: 0.9em; color: #aaa;">🏢 {row['company']}</div>
                <div style="font-size: 0.9em; color: #aaa;">📍 {row['location']}</div>
                <div style="font-size: 0.9em; color: #4CAF50; font-weight: bold; margin-top: 4px;">⚡ {mw_text}</div>
            </div>
            """, unsafe_allow_html=True)
