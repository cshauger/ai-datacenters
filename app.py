import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

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
    # Render the Airtable-like spreadsheet editor
    st.write("### Edit Datacenters")
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",        # Allows adding and deleting rows
        use_container_width=True,
        key="datacenter_editor"
    )

    # Save changes button
    if st.button("💾 Save Changes to Database"):
        try:
            with st.spinner("Saving directly to PostgreSQL..."):
                # For simplicity, this rewrites the table with the new dataframe contents
                edited_df.to_sql("ai_datacenters", engine, if_exists="replace", index=False)
                st.cache_data.clear()
            st.success("Successfully saved changes to the database!")
        except Exception as e:
            st.error(f"Error saving data: {e}")
else:
    st.info("No data found or table doesn't exist yet.")
