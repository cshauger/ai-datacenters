import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

# MUST BE FIRST! - Set page config before anything else
st.set_page_config(page_title="Quarterly AI Revenue Projections", page_icon="💰", layout="wide")

# ============================================
# AUTHENTICATION
# ============================================
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Authentication check
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

# Sidebar - External Links
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")

st.title("💰 Quarterly AI Revenue Projections")
st.markdown("Track quarterly AI revenue projections by company and property")

# Database connection
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

# Define quarters
historical_quarters = ['q1_2025', 'q2_2025', 'q3_2025', 'q4_2025']
future_quarters = [
    'q1_2026', 'q2_2026', 'q3_2026', 'q4_2026',
    'q1_2027', 'q2_2027', 'q3_2027', 'q4_2027',
    'q1_2028', 'q2_2028', 'q3_2028', 'q4_2028'
]

quarter_labels = {
    'q1_2025': '1Q25', 'q2_2025': '2Q25', 'q3_2025': '3Q25', 'q4_2025': '4Q25',
    'q1_2026': '1Q26E', 'q2_2026': '2Q26E', 'q3_2026': '3Q26E', 'q4_2026': '4Q26E',
    'q1_2027': '1Q27E', 'q2_2027': '2Q27E', 'q3_2027': '3Q27E', 'q4_2027': '4Q27E',
    'q1_2028': '1Q28E', 'q2_2028': '2Q28E', 'q3_2028': '3Q28E', 'q4_2028': '4Q28E'
}

@st.cache_data(ttl=10)
def load_projections():
    try:
        query = """
        SELECT 
            company,
            property_name,
            q1_2025, q2_2025, q3_2025, q4_2025,
            q1_2026, q2_2026, q3_2026, q4_2026,
            q1_2027, q2_2027, q3_2027, q4_2027,
            q1_2028, q2_2028, q3_2028, q4_2028,
            notes,
            estimated_completion_date
        FROM quarterly_revenue_projections
        ORDER BY company, property_name;
        """
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=10)
def get_companies():
    try:
        query = "SELECT DISTINCT company FROM ai_datacenters WHERE company IS NOT NULL ORDER BY company;"
        result = pd.read_sql(query, engine)
        return result['company'].tolist()
    except:
        return []

df = load_projections()
companies = get_companies()

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 By Company Summary", "🏢 By Property Detail", "➕ Add/Edit Data"])

with tab1:
    st.markdown("### Quarterly AI Revenue - Company Summary")
    
    if df.empty:
        st.info("No projection data yet. Add some in the 'Add/Edit Data' tab!")
    else:
        # Aggregate by company
        company_summary = df.groupby('company')[historical_quarters + future_quarters].sum().reset_index()
        
        # Rename columns for display
        display_df = company_summary.copy()
        display_df.columns = ['Company'] + [quarter_labels[q] for q in historical_quarters + future_quarters]
        
        # Calculate totals
        display_df['Total (Revenue)'] = display_df[[quarter_labels[q] for q in historical_quarters + future_quarters]].sum(axis=1)
        
        # Display with formatting
        st.dataframe(
            display_df.style.format({
                **{quarter_labels[q]: '{:.0f}' for q in historical_quarters + future_quarters},
                'Total (Revenue)': '{:.0f}'
            }),
            use_container_width=True,
            height=600
        )
        
        # Chart
        st.markdown("### 📈 Quarterly AI Revenue Chart")
        chart_data = company_summary.set_index('company')[historical_quarters + future_quarters].T
        chart_data.index = [quarter_labels[q] for q in chart_data.index]
        st.bar_chart(chart_data, height=400)

with tab2:
    st.markdown("### Quarterly AI Revenue - Property Detail")
    
    if df.empty:
        st.info("No projection data yet.")
    else:
        # Company filter
        selected_company = st.selectbox("Filter by Company", ["All Companies"] + sorted(df['company'].unique().tolist()))
        
        if selected_company != "All Companies":
            filtered_df = df[df['company'] == selected_company].copy()
        else:
            filtered_df = df.copy()
        
        # Display
        display_cols = ['company', 'property_name'] + historical_quarters + future_quarters + ['notes']
        display_df = filtered_df[display_cols].copy()
        
        # Rename for display
        display_df.columns = (
            ['Company', 'Property'] + 
            [quarter_labels[q] for q in historical_quarters + future_quarters] + 
            ['Notes']
        )
        
        st.dataframe(
            display_df.style.format({
                quarter_labels[q]: '{:.0f}' for q in historical_quarters + future_quarters
            }),
            use_container_width=True,
            height=600
        )

with tab3:
    st.markdown("### Add or Edit Projection Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_input = st.selectbox("Company", companies, key="add_company")
    
    with col2:
        property_input = st.text_input("Property Name (e.g., 'Finland 5', 'Vineland NJ')", key="add_property")
    
    st.markdown("#### Historical Actuals (Revenue)")
    hist_cols = st.columns(4)
    hist_values = {}
    for i, q in enumerate(historical_quarters):
        with hist_cols[i]:
            hist_values[q] = st.number_input(quarter_labels[q], min_value=0.0, step=10.0, key=f"hist_{q}")
    
    st.markdown("#### Future Estimates (Revenue)")
    
    # Split into 3 rows of 4 quarters each
    for year_offset in range(3):
        year_quarters = future_quarters[year_offset*4:(year_offset+1)*4]
        fut_cols = st.columns(4)
        for i, q in enumerate(year_quarters):
            with fut_cols[i]:
                hist_values[q] = st.number_input(quarter_labels[q], min_value=0.0, step=10.0, key=f"fut_{q}")
    
    notes_input = st.text_area("Notes", key="add_notes")
    completion_date = st.date_input("Estimated Completion Date (optional)", value=None, key="add_completion")
    
    if st.button("💾 Save Projection", type="primary"):
        if not property_input:
            st.error("Please enter a property name")
        else:
            try:
                # Build INSERT query
                cols = ['company', 'property_name'] + historical_quarters + future_quarters + ['notes', 'estimated_completion_date']
                values = [company_input, property_input] + [hist_values[q] for q in historical_quarters + future_quarters] + [notes_input, completion_date]
                
                # Use ON CONFLICT to update if exists
                placeholders = ', '.join(['%s'] * len(cols))
                update_cols = ', '.join([f"{col} = EXCLUDED.{col}" for col in cols if col not in ['company', 'property_name']])
                
                query = f"""
                INSERT INTO quarterly_revenue_projections ({', '.join(cols)})
                VALUES ({placeholders})
                ON CONFLICT (company, property_name)
                DO UPDATE SET {update_cols}, updated_at = CURRENT_TIMESTAMP;
                """
                
                with engine.connect() as conn:
                    conn.execute(query, values)
                    conn.commit()
                
                st.success(f"✅ Saved projection for {company_input} - {property_input}")
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving: {e}")
    
    # Show existing data for editing
    if not df.empty:
        st.markdown("---")
        st.markdown("#### Existing Projections")
        
        edit_company = st.selectbox("Select Company to Edit", sorted(df['company'].unique()), key="edit_company_select")
        
        company_df = df[df['company'] == edit_company]
        
        if not company_df.empty:
            edit_property = st.selectbox("Select Property", company_df['property_name'].tolist(), key="edit_property_select")
            
            selected_row = company_df[company_df['property_name'] == edit_property].iloc[0]
            
            st.json({
                "Company": selected_row['company'],
                "Property": selected_row['property_name'],
                **{quarter_labels[q]: float(selected_row[q]) for q in historical_quarters + future_quarters},
                "Notes": selected_row['notes']
            })
            
            if st.button("🗑️ Delete This Projection", key="delete_btn"):
                try:
                    query = "DELETE FROM quarterly_revenue_projections WHERE company = %s AND property_name = %s;"
                    with engine.connect() as conn:
                        conn.execute(query, (selected_row['company'], selected_row['property_name']))
                        conn.commit()
                    
                    st.success(f"✅ Deleted {selected_row['company']} - {selected_row['property_name']}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting: {e}")

st.markdown("---")
st.caption("💡 Tip: Add projections for each property with its estimated completion quarter. The summary view will aggregate by company.")


# --- Navigation Links ---
st.markdown("---")
st.markdown("### Navigation")
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.page_link("app.py", label="Kanban", icon="📋")
with col2:
    st.page_link("pages/1_Table_View.py", label="Directory", icon="🏢")
with col3:
    st.page_link("pages/5_Projected_MW_Additions.py", label="MW Additions", icon="⚡")
with col4:
    st.page_link("pages/6_Revenue_Projections.py", label="Revenue", icon="💰")
with col5:
    st.page_link("pages/4_Capacity_Deals.py", label="Deals", icon="🤝")
with col6:
    st.page_link("pages/2_Intelligence.py", label="Intelligence", icon="📡")
