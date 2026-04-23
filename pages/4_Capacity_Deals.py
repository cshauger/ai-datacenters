import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from collections import defaultdict


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

st.set_page_config(page_title="Capacity Deals Kanban", page_icon="🤝", layout="wide")

# Sidebar - External Links
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
    st.info("No capacity deals found. Add deals to see them here.")
    st.stop()

# Parse deals into Kanban structure (company = provider, partner_tenant = customer)
by_company = defaultdict(list)
all_partners = set()

for _, row in df.iterrows():
    company = row['company']
    partner = row['partner_tenant']
    
    by_company[company].append({
        'partner': partner,
        'capacity_mw': row['capacity_mw'],
        'value': row['deal_value_usd'],
        'date': row['announcement_date'],
        'description': row['description'],
        'source': row['source_url']
    })
    all_partners.add(partner)

# Summary stats
st.markdown(f"**{len(by_company)} providers** × **{len(all_partners)} partners** = **{len(df)} total deals**")
st.markdown("---")

# Create Kanban board
for company in sorted(by_company.keys()):
    company_deals = by_company[company]
    
    # Calculate total capacity for this company
    total_mw = sum(d['capacity_mw'] for d in company_deals if pd.notna(d['capacity_mw']))
    
    with st.expander(f"🏢 {company} — {len(company_deals)} deals, {total_mw:,.0f} MW total", expanded=False):
        
        # Group deals by partner for this company
        partners_in_company = defaultdict(list)
        for deal in company_deals:
            partners_in_company[deal['partner']].append(deal)
        
        # Display in rows of 4 partners
        partner_list = sorted(partners_in_company.keys())
        
        for i in range(0, len(partner_list), 4):
            row_partners = partner_list[i:i+4]
            cols = st.columns(len(row_partners))
            
            for j, partner in enumerate(row_partners):
                partner_deals = partners_in_company[partner]
                
                with cols[j]:
                    st.markdown(f"### {partner}")
                    
                    for deal in partner_deals:
                        st.markdown("**Deal:**")
                        
                        if pd.notna(deal['capacity_mw']):
                            st.markdown(f"⚡ **{deal['capacity_mw']:,.0f} MW**")
                        else:
                            st.markdown("⚡ Capacity TBD")
                        
                        if pd.notna(deal['value']) and deal['value']:
                            st.markdown(f"💰 {deal['value']}")
                        
                        if pd.notna(deal['date']):
                            st.markdown(f"📅 {deal['date'].strftime('%b %d, %Y')}")
                        
                        if pd.notna(deal['description']) and deal['description']:
                            with st.expander("ℹ️ Details", expanded=False):
                                st.write(deal['description'])
                        
                        if pd.notna(deal['source']) and deal['source']:
                            st.markdown(f"[🔗 Source]({deal['source']})")
                        
                        if len(partner_deals) > 1:
                            st.markdown("---")
            
            if i + 4 < len(partner_list):
                st.markdown("---")

# Summary statistics
st.markdown("---")
st.subheader("📊 Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Deals", len(df))

with col2:
    st.metric("Providers", len(by_company))

with col3:
    st.metric("Partners", len(all_partners))

# Recent deals
st.markdown("### 🆕 Recent Deals")

recent_df = df.sort_values('announcement_date', ascending=False, na_position='last').head(5)

for _, row in recent_df.iterrows():
    st.markdown(f"**{row['company']}** → **{row['partner_tenant']}**")
    
    cols = st.columns([2, 2, 2, 1])
    
    with cols[0]:
        if pd.notna(row['capacity_mw']):
            st.write(f"⚡ {row['capacity_mw']:,.0f} MW")
        else:
            st.write("⚡ Capacity TBD")
    
    with cols[1]:
        if pd.notna(row['deal_value_usd']) and row['deal_value_usd']:
            st.write(f"💰 {row['deal_value_usd']}")
        else:
            st.write("💰 Value undisclosed")
    
    with cols[2]:
        if pd.notna(row['announcement_date']):
            st.write(f"📅 {row['announcement_date'].strftime('%B %d, %Y')}")
    
    with cols[3]:
        if pd.notna(row['source_url']) and row['source_url']:
            st.markdown(f"[🔗]({row['source_url']})")
    
    st.markdown("---")

# Navigation Links
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
