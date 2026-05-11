import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os

st.set_page_config(page_title="Hardware Tracker", page_icon="🖥️", layout="wide")

DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "Jetha2026!")

if 'authenticated' not in st.session_state:
    if 'auth_cookie' in st.context.cookies and st.context.cookies['auth_cookie'] == DASHBOARD_PASSWORD:
        st.session_state.authenticated = True
    else:
        st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 AI Datacenter Tracker")
    st.markdown("### Login Required")
    import uuid
    page_key = f"password_{str(uuid.uuid4())[:8]}"
    password_input = st.text_input("Enter password:", type="password", key=page_key)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        btn_key = f"login_{str(uuid.uuid4())[:8]}"
        if st.button("🔓 Login", use_container_width=True, key=btn_key):
            if password_input == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                try:
                    import streamlit.components.v1 as components
                    components.html(
                        f'''
                        <script>
                            document.cookie = "auth_cookie={DASHBOARD_PASSWORD}; path=/; max-age=" + 30*24*60*60;
                            window.parent.postMessage("reload", "*");
                        </script>
                        ''',
                        height=0
                    )
                except:
                    pass
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    st.stop()


    st.markdown("### 🔗 Related Tools")
    st.markdown("[GPU Pricing Tracker →](https://gpu-pricing-tracker-vaxov.ondigitalocean.app)")
    st.markdown("---")

st.title("🖥️ Datacenter Hardware Pricing")
st.markdown("Track pricing and specs for critical datacenter components (CPUs, DRAM, NAND/SSDs).")

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
def load_hardware():
    query = "SELECT id, component_category, manufacturer, product_name, capacity_or_speed, price_usd, date_recorded, notes FROM datacenter_hardware ORDER BY date_recorded DESC, component_category;"
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Could not load data: {e}")
        return pd.DataFrame()

df = load_hardware()

st.markdown("### 📝 Add / Edit Hardware Data")
with st.expander("Show Data Editor", expanded=True):
    if df.empty:
        df = pd.DataFrame(columns=["id", "component_category", "manufacturer", "product_name", "capacity_or_speed", "price_usd", "date_recorded", "notes"])
    
    col_config = {
        "id": None, # hide id
        "component_category": st.column_config.SelectboxColumn("Category", options=["CPU", "DRAM", "NAND Flash / SSD", "Networking", "Other"], required=True),
        "manufacturer": st.column_config.TextColumn("Manufacturer"),
        "product_name": st.column_config.TextColumn("Product Name"),
        "capacity_or_speed": st.column_config.TextColumn("Capacity / Speed"),
        "price_usd": st.column_config.NumberColumn("Price (USD)", format="$%.2f"),
        "date_recorded": st.column_config.DateColumn("Date"),
        "notes": st.column_config.TextColumn("Notes")
    }
        
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        key="hardware_editor",
        hide_index=True,
        column_config=col_config,
        num_rows="dynamic"
    )

    if st.button("💾 Save Hardware Data"):
        try:
            with st.spinner("Saving to database..."):
                with engine.begin() as conn:
                    conn.execute(text("DELETE FROM datacenter_hardware;"))
                    if not edited_df.empty:
                        # Drop id to let it autoincrement
                        if 'id' in edited_df.columns:
                            save_df = edited_df.drop(columns=['id'])
                        else:
                            save_df = edited_df
                        save_df.to_sql("datacenter_hardware", conn, if_exists="append", index=False)
                st.cache_data.clear()
            st.success("Successfully saved changes!")
            st.rerun()
        except Exception as e:
            st.error(f"Error saving data: {e}")

if not df.empty:
    st.markdown("---")
    st.markdown("### 📈 Price Trends")
    
    categories = df['component_category'].unique()
    selected_cat = st.selectbox("Select Category to Chart", categories)
    
    cat_df = df[df['component_category'] == selected_cat].copy()
    if not cat_df.empty and 'date_recorded' in cat_df.columns and 'price_usd' in cat_df.columns:
        cat_df['date_recorded'] = pd.to_datetime(cat_df['date_recorded'])
        # Pivot so each product is a line
        chart_data = cat_df.pivot_table(index='date_recorded', columns='product_name', values='price_usd')
        st.line_chart(chart_data)


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
