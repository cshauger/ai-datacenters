import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import uuid

st.set_page_config(page_title="Capacity Deals", page_icon="🤝", layout="wide")
st.title("🤝 Capacity Deal Announcements")
st.markdown("Track capacity reservations, hyperscaler leases, and major infrastructure deals.")

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    st.warning("DATABASE_URL environment variable is missing.")
    st.stop()

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

try:
    engine = create_engine(db_url)
except Exception as e:
    st.error(f"Error creating database engine: {e}")
    st.stop()

@st.cache_data(ttl=10)
def load_deals():
    try:
        df = pd.read_sql("SELECT * FROM capacity_deals ORDER BY announcement_date DESC NULLS LAST;", engine)
        if df.empty:
            return pd.DataFrame(columns=["id", "company", "partner_tenant", "capacity_mw", "deal_value_usd", "announcement_date", "description", "source_url"])
        return df
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame(columns=["id", "company", "partner_tenant", "capacity_mw", "deal_value_usd", "announcement_date", "description", "source_url"])

df = load_deals()

st.write("### Deal Editor")
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="deals_editor",
    column_config={
        "id": None,  # Hide ID
        "created_at": None, # Hide timestamp
        "announcement_date": st.column_config.DateColumn("Announcement Date"),
        "source_url": st.column_config.LinkColumn("Source URL"),
        "capacity_mw": st.column_config.NumberColumn("Capacity (MW)", format="%d")
    }
)

if st.button("💾 Save Deals to Database"):
    try:
        with st.spinner("Saving directly to PostgreSQL..."):
            if "id" in edited_df.columns:
                edited_df["id"] = edited_df["id"].apply(lambda x: str(uuid.uuid4()) if pd.isna(x) or str(x).strip() == "" else x)
            edited_df.to_sql("capacity_deals", engine, if_exists="replace", index=False)
            st.cache_data.clear()
        st.success("Successfully saved changes to the database!")
    except Exception as e:
        st.error(f"Error saving data: {e}")


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
