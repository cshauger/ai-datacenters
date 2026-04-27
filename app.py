import streamlit as st

# Redirect to AI Datacenter Tracker
st.switch_page("pages/0_AI_Datacenter_Tracker.py")


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
