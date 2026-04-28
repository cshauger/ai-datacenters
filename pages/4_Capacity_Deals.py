import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import uuid
from collections import defaultdict

# ============================================
# AUTHENTICATION & SETUP
# ============================================
st.set_page_config(page_title="Capacity Deals", page_icon="🤝", layout="wide")

DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
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

with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")

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

if df.empty:
    st.info("No deal data available to display.")
    st.stop()

# --- Kanban View Logic ---
df['company'] = df['company'].fillna('Unknown Provider')
df['partner_tenant'] = df['partner_tenant'].fillna('Unknown Partner')
df['capacity_mw'] = df['capacity_mw'].fillna(0)

companies = sorted(df['company'].unique().tolist())
selected_company = st.selectbox("🔍 Filter to a specific Provider", ["All Providers"] + companies)

if selected_company != "All Providers":
    display_companies = [selected_company]
else:
    display_companies = companies

st.markdown('''
<style>
    div[data-testid="stExpander"] details summary p {
        font-size: 1.4em !important;
        font-weight: bold !important;
    }
</style>
''', unsafe_allow_html=True)

st.markdown("---")

for company in display_companies:
    comp_df = df[df['company'] == company]
    if comp_df.empty:
        continue
        
    with st.expander(f"🏢 {company} ({len(comp_df)} deals)", expanded=True):
        relevant_partners = sorted(comp_df['partner_tenant'].unique().tolist())
        cols = st.columns(len(relevant_partners))
        
        for i, partner in enumerate(relevant_partners):
            with cols[i]:
                partner_df = comp_df[comp_df['partner_tenant'] == partner]
                st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.85em; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 5px;'>{partner.upper()}</div>", unsafe_allow_html=True)
                
                for _, row in partner_df.iterrows():
                    val = f"💰 {row['deal_value_usd']}" if pd.notna(row['deal_value_usd']) and str(row['deal_value_usd']).strip() else ""
                    mw_text = f"{int(row['capacity_mw'])} MW" if row['capacity_mw'] > 0 else "TBD MW"
                    date_str = row['announcement_date'].strftime("%Y-%m-%d") if pd.notna(row['announcement_date']) else "Unknown Date"
                    source_link = f"<div style='font-size: 0.8em; margin-top: 6px;'><a href='{row['source_url']}' target='_blank' style='color: #4da6ff; text-decoration: none;'>🔗 Source Announcement</a></div>" if 'source_url' in row and pd.notna(row['source_url']) and str(row['source_url']).strip() else ""
                    
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
                        <div style="font-size: 0.8em; color: #bbb; line-height: 1.2; margin-bottom: 4px;">📅 {date_str}</div>
                        <div style="font-weight: bold; font-size: 1.0em; color: #4CAF50; margin-bottom: 4px;">⚡ {mw_text}</div>
                        <div style="font-size: 0.9em; font-weight: bold; margin-bottom: 6px;">{val}</div>
                        <div style="font-size: 0.85em; color: #ddd; line-height: 1.3;">{row['description']}</div>
                        {source_link}
                    </div>
                    """, unsafe_allow_html=True)

st.markdown("---")
st.write("### 📝 Raw Data Editor")
st.caption("Expand below to view or edit the raw records.")
with st.expander("Show Data Editor", expanded=False):
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="deals_editor",
        column_config={
            "id": None,
            "created_at": None,
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
            st.success("Successfully saved changes to the database! Refresh the page to see them on the board.")
        except Exception as e:
            st.error(f"Error saving data: {e}")

# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("app.py", label="Kanban", icon="📋")
    st.page_link("pages/4_Capacity_Deals.py", label="Deals", icon="🤝")
with col2:
    st.page_link("pages/1_Table_View.py", label="Directory", icon="🏢")
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col3:
    st.page_link("pages/5_Projected_MW_Additions.py", label="Property MW", icon="⚡")
    st.page_link("pages/7_Guided_MW_Pipeline.py", label="Guided MW", icon="🎯")
with col4:
    st.page_link("pages/6_Revenue_Projections.py", label="Revenue", icon="💰")
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
