import streamlit as st

st.markdown("""
<style>
.hero{padding:56px 0}
.hero h1{font-weight:800;font-size:48px;line-height:1.1;margin:0}
.hero p{font-size:18px;opacity:.9;margin:8px 0 0}
.glass{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
       border-radius:20px;padding:24px}
.badge{font-size:12px;border:1px solid rgba(255,255,255,.2);
       border-radius:999px;padding:6px 10px;opacity:.85}
</style>
<div class='hero'>
  <span class='badge'>AI • Due Diligence • Investor-ready</span>
  <h1>AI-Powered Startup Evaluation</h1>
  <p>Validate ideas, spot risks, and get an action plan in minutes.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.1, 0.9])
with col1:
    st.subheader("Try it now")
    st.write("Go to **Evaluate** and paste your idea or deck summary.")
    st.page_link("pages/evaluate.py", label="→ Open Evaluate", icon="🧪")

with col2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.write("**What you get**")
    st.markdown("- Scorecard (Viability, Market, Moat, Financials)\n- Strengths & Risks\n- Next 7-day action plan\n- Downloadable report")
    st.markdown("</div>", unsafe_allow_html=True)
