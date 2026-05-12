import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Guided MW Pipeline", page_icon="🎯", layout="wide")

DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

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


    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")

st.title("🎯 Guided MW Pipeline by Quarter")
st.markdown("Track official company-level guided capacity additions by quarter.")

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

historical_quarters = ['q1_2025', 'q2_2025', 'q3_2025', 'q4_2025']
future_quarters = ['q1_2026', 'q2_2026', 'q3_2026', 'q4_2026', 'q1_2027', 'q2_2027', 'q3_2027', 'q4_2027', 'q1_2028', 'q2_2028', 'q3_2028', 'q4_2028']
all_quarters = historical_quarters + future_quarters

quarter_labels = {
    'q1_2025': '1Q25', 'q2_2025': '2Q25', 'q3_2025': '3Q25', 'q4_2025': '4Q25',
    'q1_2026': '1Q26E', 'q2_2026': '2Q26E', 'q3_2026': '3Q26E', 'q4_2026': '4Q26E',
    'q1_2027': '1Q27E', 'q2_2027': '2Q27E', 'q3_2027': '3Q27E', 'q4_2027': '4Q27E',
    'q1_2028': '1Q28E', 'q2_2028': '2Q28E', 'q3_2028': '3Q28E', 'q4_2028': '4Q28E'
}

@st.cache_data(ttl=10)
def load_data():
    query = "SELECT id, company, " + ", ".join(all_quarters) + ", notes FROM guided_mw_pipeline ORDER BY company;"
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_data()

st.markdown("### 📝 Edit Company Guidance")
st.caption("Expand below to view or edit the official company guidance.")
with st.expander("Show Data Editor", expanded=True):
    # Configure columns for the editor
    col_config = { "id": None } # hide id
    for q in all_quarters:
        col_config[q] = st.column_config.NumberColumn(quarter_labels[q], format="%d")
        
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="guided_editor",
        hide_index=True,
        column_config=col_config
    )

    if st.button("💾 Save Guidance to Database"):
        try:
            with st.spinner("Saving directly to PostgreSQL..."):
                edited_df.to_sql("guided_mw_pipeline", engine, if_exists="replace", index=False)
                st.cache_data.clear()
            st.success("Successfully saved changes!")
            st.rerun()
        except Exception as e:
            st.error(f"Error saving data: {e}")

if not df.empty:
    st.markdown("### 📈 Visual Summary")
    
    # Calculate totals
    display_df = df.copy()
    display_df['Total Guided MW'] = display_df[all_quarters].sum(axis=1)
    
    # Sort by total for the chart
    top_companies = display_df.sort_values('Total Guided MW', ascending=False).head(10)
    
    chart_data = top_companies.set_index('company')[all_quarters].T
    chart_data.index = [quarter_labels[q] for q in chart_data.index]
    st.bar_chart(chart_data, height=500)



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
