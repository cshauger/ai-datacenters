import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Intelligence Blog", page_icon="📰", layout="wide")
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
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("app.py", label="Kanban Board", icon="📋")
with col2:
    st.page_link("pages/1_Table_View.py", label="Data Directory", icon="🏢")
with col3:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col4:
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
