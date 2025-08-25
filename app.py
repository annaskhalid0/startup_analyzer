import streamlit as st

st.set_page_config(
    page_title="AI Startup Evaluator",
    page_icon="🚀",
    layout="wide",
    menu_items={"Get help": None, "Report a bug": None, "About": None},
)

# Define pages programmatically
home     = st.Page("pages/home.py",     title="Home",     icon="🏠")
evaluate = st.Page("pages/evaluate.py", title="Evaluate", icon="🧪")
reports  = st.Page("pages/reports.py",  title="Reports",  icon="📊")
about    = st.Page("pages/about.py",    title="About",    icon="ℹ️")

# Sidebar (you can switch to position="top" later if you prefer)
nav = st.navigation([home, evaluate, reports, about], position="sidebar")
nav.run()
