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
    'Under construction',
    'Operational/expanding',
    'Fully operational',
    'Decommissioned/abandoned'
]

# Find any other statuses in the DB not in our standard list
db_statuses = df['status'].unique().tolist()
kanban_columns = base_statuses.copy()
for s in db_statuses:
    if s not in kanban_columns:
        kanban_columns.append(s)

# Create columns for the board
cols = st.columns(len(kanban_columns))

# Render the cards grouped by company
for i, status in enumerate(kanban_columns):
    with cols[i]:
        # Count items for header
        status_df = df[df['status'] == status]
        st.markdown(f"**{status} ({len(status_df)})**")
        
        # Group by company within this status column
        grouped = status_df.groupby('company')
        for company, group in grouped:
            with st.expander(f"🏢 {company} ({len(group)})"):
                for _, row in group.iterrows():
                    mw_text = f"{int(row['estimated_capacity_mw'])} MW" if row['estimated_capacity_mw'] > 0 else "TBD MW"
                    
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #444; 
                        border-radius: 6px; 
                        padding: 8px; 
                        margin-bottom: 8px; 
                        background-color: #2e2e2e; 
                        color: #eee;
                    ">
                        <div style="font-weight: bold; font-size: 0.95em; margin-bottom: 2px;">{row['name']}</div>
                        <div style="font-size: 0.8em; color: #ccc;">📍 {row['location']}</div>
                        <div style="font-size: 0.8em; color: #4CAF50; font-weight: bold; margin-top: 2px;">⚡ {mw_text}</div>
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
