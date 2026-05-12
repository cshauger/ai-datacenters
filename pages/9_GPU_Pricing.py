import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os

st.set_page_config(page_title="GPU Pricing Tracker", page_icon="📈", layout="wide")

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

try:
    df = load_data()
    
    if df.empty:
        st.warning("No pricing data yet. Worker will populate data at 5 AM PT daily.")
        st.info("First run: worker loads 399 historical records, then scrapes live pricing daily.")
    else:
        # Show summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GPU Types", len(df['gpu_type'].unique()))
        with col2:
            st.metric("Providers", len(df['provider'].unique()))
        with col3:
            st.metric("Price Points", len(df))
        
        st.divider()
        
        # Daily Mean Price Trend
        st.subheader("📊 Daily Mean Vendor Price by GPU Model")
        
        daily_means = df.groupby(['date', 'gpu_type'])['price_per_hr'].mean().reset_index()
        daily_means_pivot = daily_means.pivot(index='date', columns='gpu_type', values='price_per_hr')
        
        st.bar_chart(daily_means_pivot, use_container_width=True)
        
        with st.expander("📋 View Daily Mean Prices"):
            display_df = daily_means_pivot.reset_index()
            display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d')
            st.dataframe(
                display_df.style.format({col: "${:.2f}" for col in daily_means_pivot.columns}),
                use_container_width=True,
                hide_index=True
            )
        
        st.divider()
        
        # GPU selector
        gpu_types = sorted(df['gpu_type'].unique())
        selected_gpu = st.selectbox("Select GPU Type for Details", gpu_types)
        
        filtered_df = df[df['gpu_type'] == selected_gpu]
        
        # Current pricing
        st.subheader(f"💰 Current Pricing - {selected_gpu}")
        latest_date = df['date'].max()
        latest_df = filtered_df[filtered_df['date'] == latest_date].sort_values(by='price_per_hr')
        
        if not latest_df.empty:
            latest_df = latest_df.reset_index(drop=True)
            latest_df.index = latest_df.index + 1
            
            st.dataframe(
                latest_df[['provider', 'price_per_hr']].style.format({"price_per_hr": "${:.2f}"}),
                use_container_width=True
            )
            
            best_provider = latest_df.iloc[0]['provider']
            best_price = latest_df.iloc[0]['price_per_hr']
            st.success(f"🏆 Best Deal: **{best_provider}** at **${best_price:.2f}/hr**")
        
        st.caption(f"Last updated: {latest_date} | Live scraping at 5 AM PT daily")

except Exception as e:
    st.error(f"Error: {e}")

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
