import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import uuid

st.set_page_config(page_title="AI Datacenters Tracker", page_icon="🏢", layout="wide")
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
        }
    )
else:
    st.info("No data found or table doesn't exist yet.")


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("app.py", label="Kanban Board", icon="📋")
with col2:
    st.page_link("pages/1_Table_View.py", label="Data Directory", icon="🏢")
with col3:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col4:
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
