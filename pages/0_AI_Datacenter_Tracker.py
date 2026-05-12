import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# MUST BE FIRST! - Set page config before anything else
st.set_page_config(page_title="AI Datacenter Tracker", page_icon="📋", layout="wide")

# ============================================
# AUTHENTICATION
# ============================================
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

# Initialize session state
if 'authenticated' not in st.session_state:
    try:
        if 'auth_cookie' in st.context.cookies and st.context.cookies['auth_cookie'] == DASHBOARD_PASSWORD:
            st.session_state.authenticated = True
        else:
            st.session_state.authenticated = False
    except:
        st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 AI Datacenter Tracker")
    st.markdown("### Login Required")
    
    password_input = st.text_input("Enter password:", type="password")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔓 Login", use_container_width=True):
            if password_input == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                try:
                    import streamlit.components.v1 as components
                    components.html(
                        f'''
                        <script>
                            document.cookie = "auth_cookie={DASHBOARD_PASSWORD}; path=/; max-age=2592000";
                            window.parent.location.reload();
                        </script>
                        ''',
                        height=0
                    )
                except:
                    pass
                st.success("Logging in... please wait.")
                st.stop()
            else:
                st.error("❌ Incorrect password")
    st.stop()

# ============================================
# AUTHENTICATED CONTENT BELOW
# ============================================


    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")

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

@st.cache_data(ttl=10)
def load_deals():
    try:
        return pd.read_sql("SELECT * FROM capacity_deals", engine)
    except Exception as e:
        return pd.DataFrame()

df = load_data()
deals_df = load_deals()

if df.empty:
    st.info("No datacenter data found.")
    st.stop()

# Handle missing values
df['estimated_capacity_mw'] = df['estimated_capacity_mw'].fillna(0)

# Get unique values for filters
all_companies = sorted(df['company'].dropna().unique().tolist())
all_statuses = sorted(df['status'].dropna().unique().tolist())

# Sidebar filters
st.sidebar.markdown("### Filters")
selected_companies = st.sidebar.multiselect("Companies", all_companies, default=all_companies)
selected_statuses = st.sidebar.multiselect("Status", all_statuses, default=all_statuses)

# Filter data
df = df[df['company'].isin(selected_companies) & df['status'].isin(selected_statuses)]

# Debug output
st.sidebar.markdown("---")
st.sidebar.markdown("### 🐛 Debug Info")
st.sidebar.write(f"Total datacenters: {len(df)}")
st.sidebar.write(f"Companies selected: {len(selected_companies)}")
st.sidebar.write(f"Statuses selected: {len(selected_statuses)}")

# Display logic
target_statuses = selected_statuses if selected_statuses else all_statuses
display_companies = selected_companies if selected_companies else all_companies

for company in display_companies:
    comp_df = df[df['company'] == company]
    if comp_df.empty:
        continue
        
    with st.expander(f"🏢 {company} ({len(comp_df)} properties)", expanded=True):
        if not deals_df.empty:
            comp_deals = deals_df[deals_df['company'] == company]
            if not comp_deals.empty:
                st.markdown("##### 🤝 Recent Capacity Deals")
                for _, deal in comp_deals.iterrows():
                    val = f" | 💰 {deal['deal_value_usd']}" if pd.notna(deal['deal_value_usd']) else ""
                    mw = f" | ⚡ {int(deal['capacity_mw'])} MW" if pd.notna(deal['capacity_mw']) else ""
                    st.info(f"**Partner:** {deal['partner_tenant']}{mw}{val} — *{deal['description']}*")
                st.markdown("<br>", unsafe_allow_html=True)
                
        cols = st.columns(len(target_statuses))
        
        for i, status in enumerate(target_statuses):
            with cols[i]:
                status_df = comp_df[comp_df['status'] == status]
                
                st.markdown(f"**{status}** ({len(status_df)})")
                
                for _, row in status_df.iterrows():
                    name_text = row['name'] if pd.notna(row['name']) else "Unnamed Property"
                    mw_text = f"{int(row['estimated_capacity_mw'])} MW" if row['estimated_capacity_mw'] > 0 else "TBD MW"
                    loc_text = f"{row['location']}" if pd.notna(row['location']) else "Location TBD"
                    
                    source_link = ""
                    if pd.notna(row.get('source_url')) and row['source_url']:
                        source_link = f"\n\n[🔗 Source]({row['source_url']})"
                    
                    card_text = f"**{name_text}**\n\n⚡ {mw_text}\n\n📍 {loc_text}{source_link}"
                    st.info(card_text)

# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.page_link("pages/0_AI_Datacenter_Tracker.py", label="Kanban", icon="📋")
    st.page_link("pages/4_Capacity_Deals.py", label="Deals", icon="🤝")
with col2:
    st.page_link("pages/1_Table_View.py", label="Directory", icon="🏢")
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
with col3:
    st.page_link("pages/5_Projected_MW_Additions.py", label="Property MW", icon="⚡")
    st.page_link("pages/7_Guided_MW_Pipeline.py", label="Guided MW", icon="🎯")
with col4:
    st.page_link("pages/6_Revenue_Projections.py", label="Revenue", icon="💰")
    st.page_link("pages/8_Hardware_Tracker.py", label="Hardware", icon="🖥️")
with col5:
    st.page_link("pages/9_GPU_Pricing.py", label="GPU Pricing", icon="📈")
    st.page_link("pages/3_Summary_Blog.py", label="Summary Blog", icon="📰")
